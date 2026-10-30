"""Media helpers built on ffmpeg/ffprobe: probing, scene & silence detection,
frame extraction and optional speech-to-text."""

from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


class MediaError(RuntimeError):
    pass


def require_ffmpeg() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise MediaError(f"Không tìm thấy '{tool}'. Cài ffmpeg: https://ffmpeg.org/download.html")


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-25:])
        raise MediaError(f"Lệnh thất bại ({proc.returncode}): {' '.join(cmd[:6])} ...\n{tail}")
    return proc


@dataclass(frozen=True)
class MediaInfo:
    path: str
    duration: float
    width: int
    height: int
    fps: float
    has_video: bool
    has_audio: bool
    is_image: bool
    video_codec: str | None
    audio_codec: str | None
    size_bytes: int

    @property
    def orientation(self) -> str:
        if not self.has_video:
            return "audio"
        if self.width == self.height:
            return "square"
        return "portrait" if self.height > self.width else "landscape"

    def to_dict(self) -> dict:
        return {**asdict(self), "orientation": self.orientation}


def _parse_rate(rate: str | None) -> float:
    if not rate or rate in ("0/0", "0"):
        return 0.0
    if "/" in rate:
        num, den = rate.split("/")
        return float(num) / float(den) if float(den) else 0.0
    return float(rate)


def _rotation(stream: dict) -> int:
    for side in stream.get("side_data_list", []) or []:
        if "rotation" in side:
            return int(float(side["rotation"]))
    return int(float(stream.get("tags", {}).get("rotate", 0) or 0))


@lru_cache(maxsize=256)
def _probe_cached(path: str, mtime: float) -> MediaInfo:
    proc = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path])
    data = json.loads(proc.stdout or "{}")
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"
                  and not s.get("disposition", {}).get("attached_pic")), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    is_image = Path(path).suffix.lower() in IMAGE_EXTS
    width = height = 0
    fps = 0.0
    if video:
        width, height = int(video.get("width", 0)), int(video.get("height", 0))
        if abs(_rotation(video)) in (90, 270):
            width, height = height, width
        fps = _parse_rate(video.get("avg_frame_rate")) or _parse_rate(video.get("r_frame_rate"))
    duration = float(data.get("format", {}).get("duration", 0) or 0)
    if not duration and video:
        duration = float(video.get("duration", 0) or 0)
    return MediaInfo(
        path=path,
        duration=0.0 if is_image else round(duration, 3),
        width=width,
        height=height,
        fps=round(fps, 3),
        has_video=video is not None,
        has_audio=audio is not None,
        is_image=is_image,
        video_codec=video.get("codec_name") if video else None,
        audio_codec=audio.get("codec_name") if audio else None,
        size_bytes=int(data.get("format", {}).get("size", 0) or 0),
    )


def probe(path: str | Path) -> MediaInfo:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise MediaError(f"Không tìm thấy file: {p}")
    return _probe_cached(str(p), p.stat().st_mtime)


def detect_scenes(path: Path, threshold: float = 0.15, min_scene: float = 0.8) -> list[tuple[float, float]]:
    """Shot boundaries via ffmpeg's scene score. Returns (start, end) pairs covering the video.
    0.15 catches soft phone-camera cuts that 0.3 misses, without firing on ordinary hand motion."""
    info = probe(path)
    proc = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-an",
        "-vf", f"scale=320:-2,select='gt(scene,{threshold})',showinfo", "-f", "null", "-",
    ], check=False)
    cuts = [float(m) for m in re.findall(r"pts_time:([0-9.]+)", proc.stderr)]
    bounds = [0.0]
    for t in cuts:
        if t - bounds[-1] >= min_scene and info.duration - t >= min_scene:
            bounds.append(round(t, 3))
    bounds.append(info.duration)
    return list(zip(bounds, bounds[1:]))


def detect_silences(path: Path, noise_db: float = -35, min_silence: float = 0.6) -> list[tuple[float, float]]:
    info = probe(path)
    if not info.has_audio:
        return []
    proc = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn",
        "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}", "-f", "null", "-",
    ], check=False)
    starts = [float(x) for x in re.findall(r"silence_start: (-?[0-9.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", proc.stderr)]
    if len(ends) < len(starts):
        ends.append(info.duration)
    return [(round(max(s, 0.0), 3), round(e, 3)) for s, e in zip(starts, ends)]


def loudness(path: Path) -> dict:
    """Mean / peak volume in dB (ffmpeg volumedetect)."""
    if not probe(path).has_audio:
        return {}
    proc = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn",
                "-af", "volumedetect", "-f", "null", "-"], check=False)
    mean = re.search(r"mean_volume: (-?[0-9.]+) dB", proc.stderr)
    peak = re.search(r"max_volume: (-?[0-9.]+) dB", proc.stderr)
    return {"mean_db": float(mean.group(1)) if mean else None, "peak_db": float(peak.group(1)) if peak else None}


# 10% grid with 0.1..0.9 labels: lets an agent read positions (EditPlan x/y fractions) off a frame
GRID_FILTER = ",".join(
    ["drawgrid=w=iw/10:h=ih/10:t=1:c=white@0.55"]
    + [f"drawtext=text='{k / 10:.1f}':x=w*{k / 10:.1f}+3:y=3:fontsize=h/45:fontcolor=yellow:box=1:boxcolor=black@0.6"
       for k in range(1, 10)]
    + [f"drawtext=text='{k / 10:.1f}':x=3:y=h*{k / 10:.1f}+3:fontsize=h/45:fontcolor=cyan:box=1:boxcolor=black@0.6"
       for k in range(1, 10)]
)


def extract_frame(path: Path, t: float, out: Path, width: int = 512, grid: bool = False) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = f"scale={width}:-2" + ("," + GRID_FILTER if grid else "")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{max(t, 0):.3f}", "-i", str(path),
         "-frames:v", "1", "-vf", vf, "-q:v", "4", str(out)])
    if not out.exists():
        raise MediaError(f"Không trích được khung hình tại {t:.2f}s (có thể vượt quá độ dài video)")
    return out


def image_block(path: Path) -> dict:
    """An image content block for the Claude API."""
    media_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
    return {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}}


# ---- transcripts -------------------------------------------------------------

def _srt_time(value: str) -> float:
    h, m, rest = value.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


def load_srt(path: Path) -> list[dict]:
    """Parse .srt/.vtt into [{start, end, text}]."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    segments = []
    pattern = re.compile(
        r"(\d{1,2}:\d{2}:\d{2}[.,]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[.,]\d{1,3})[^\n]*\n(.*?)(?:\n\s*\n|\Z)", re.S
    )
    for start, end, body in pattern.findall(text):
        clean = re.sub(r"<[^>]+>", "", body).strip().replace("\n", " ")
        if clean:
            segments.append({"start": round(_srt_time(start), 3), "end": round(_srt_time(end), 3), "text": clean})
    return segments


def transcribe(path: Path, model_size: str = "small", language: str | None = "vi") -> list[dict] | None:
    """Speech-to-text with word timestamps using faster-whisper (optional dependency).
    Returns None when faster-whisper is not installed."""
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        return None
    if not probe(path).has_audio:
        return []
    model = WhisperModel(model_size, device="auto", compute_type="auto")
    segments, _ = model.transcribe(str(path), language=language, word_timestamps=True, vad_filter=True)
    result = []
    for seg in segments:
        words = [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
                 for w in (seg.words or []) if w.word.strip()]
        result.append({"start": round(seg.start, 3), "end": round(seg.end, 3), "text": seg.text.strip(),
                       "words": words})
    return result


# ---- full analysis -------------------------------------------------------------

def analyze_video(
    path: Path,
    out_dir: Path,
    *,
    transcript_file: Path | None = None,
    whisper_model: str = "small",
    language: str | None = "vi",
    max_frames: int = 16,
    log=print,
) -> dict:
    """Probe + scenes + silences + keyframes + transcript. Writes analysis.json and frames/ into out_dir."""
    require_ffmpeg()
    path = Path(path).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    info = probe(path)
    if not info.has_video:
        raise MediaError(f"{path.name} không có luồng video")
    log(f"  • {path.name}: {info.width}x{info.height} {info.fps}fps, {info.duration:.1f}s")

    log("  • Dò cảnh (scene detection)...")
    scenes = detect_scenes(path)
    log(f"    {len(scenes)} cảnh")

    log("  • Dò khoảng lặng...")
    silences = detect_silences(path)

    # keyframes: middle of each scene, evenly subsampled down to max_frames
    picks = scenes
    if len(scenes) > max_frames:
        step = len(scenes) / max_frames
        picks = [scenes[int(i * step)] for i in range(max_frames)]
    if len(picks) < min(6, max_frames):  # long single shots: sample evenly instead
        n = min(6, max_frames)
        picks = [(info.duration * i / n, info.duration * (i + 1) / n) for i in range(n)]
    frames_dir = out_dir / "frames"
    frames = []
    for s, e in picks:
        t = round((s + e) / 2, 2)
        frame = extract_frame(path, t, frames_dir / f"t{t:07.2f}.jpg")
        frames.append({"time": t, "file": str(frame.relative_to(out_dir))})
    log(f"  • Trích {len(frames)} khung hình đại diện")

    transcript: list[dict] | None = None
    transcript_source = None
    if transcript_file:
        transcript = load_srt(transcript_file)
        transcript_source = str(transcript_file)
    elif info.has_audio:
        log("  • Chuyển giọng nói thành chữ (faster-whisper)...")
        transcript = transcribe(path, whisper_model, language)
        transcript_source = f"faster-whisper:{whisper_model}" if transcript is not None else None
        if transcript is None:
            log("    (bỏ qua — chưa cài faster-whisper: pip install 'vedit[transcribe]')")

    analysis = {
        "source": str(path),
        "media": info.to_dict(),
        "loudness": loudness(path),
        "scenes": [{"start": round(s, 3), "end": round(e, 3), "duration": round(e - s, 3)} for s, e in scenes],
        "silences": [{"start": s, "end": e, "duration": round(e - s, 3)} for s, e in silences],
        "frames": frames,
        "transcript_source": transcript_source,
        "transcript": transcript,
    }
    (out_dir / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    return analysis
