"""Object tracking: follow a box drawn around something in a source video (a jar, a chili, a hand) so HUD
graphics can stick to it. Uses OpenCV's CSRT tracker (optional extra: ``pip install -e ".[track]"``).

Track files live in ``projects/<slug>/analysis/tracks/<name>.json``; coordinates are fractions of the
*source* frame (after rotation), so they stay valid whatever crop / zoom / speed the edit applies.
"""

from __future__ import annotations

import bisect
import json
import math
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .media import MediaError, probe, require_ffmpeg

HDR_TO_SDR = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
              "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
TRACK_WIDTH = 480  # px; CSRT is slow, and the box does not need more precision than this


class TrackError(RuntimeError):
    pass


@dataclass
class TrackPoint:
    t: float          # source seconds
    x: float          # box centre, fraction of source width
    y: float          # box centre, fraction of source height
    w: float          # box size, fractions of source width / height
    h: float
    ok: bool = True   # False = tracker lost the object; the box is held / interpolated

    def as_list(self) -> list:
        return [round(self.t, 4), round(self.x, 5), round(self.y, 5), round(self.w, 5), round(self.h, 5),
                1 if self.ok else 0]


@dataclass
class Track:
    name: str
    source: str
    points: list[TrackPoint] = field(default_factory=list)
    fps: float = 30.0
    stopped: list[str] = field(default_factory=list)   # ends cut short by a scene cut ("đầu" / "cuối")

    @property
    def start(self) -> float:
        return self.points[0].t

    @property
    def end(self) -> float:
        return self.points[-1].t

    @property
    def lost(self) -> float:
        return sum(not p.ok for p in self.points) / max(len(self.points), 1)

    def at(self, t: float) -> TrackPoint:
        """Box at source time t: linear between samples, held outside the tracked range."""
        pts = self.points
        if t <= pts[0].t:
            return pts[0]
        if t >= pts[-1].t:
            return pts[-1]
        i = bisect.bisect_right([p.t for p in pts], t)
        a, b = pts[i - 1], pts[i]
        u = (t - a.t) / (b.t - a.t) if b.t > a.t else 0.0
        mix = lambda p, q: p + (q - p) * u  # noqa: E731
        return TrackPoint(t, mix(a.x, b.x), mix(a.y, b.y), mix(a.w, b.w), mix(a.h, b.h), a.ok and b.ok)

    # ---- persistence -------------------------------------------------------------------------

    def to_json(self) -> str:
        return json.dumps({"name": self.name, "source": self.source, "fps": self.fps,
                           "fields": ["t", "x", "y", "w", "h", "ok"],
                           "points": [p.as_list() for p in self.points]}, ensure_ascii=False)

    def save(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> "Track":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        points = [TrackPoint(p[0], p[1], p[2], p[3], p[4], bool(p[5]) if len(p) > 5 else True)
                  for p in data["points"]]
        if not points:
            raise TrackError(f"track {path} trống")
        return cls(data.get("name", Path(path).stem), data.get("source", ""), points, data.get("fps", 30.0))


def track_path(base_dir: Path, name: str) -> Path:
    return Path(base_dir) / "analysis" / "tracks" / f"{name}.json"


# ---- tracking -----------------------------------------------------------------------------------

def _frames(path: Path, start: float, end: float, width: int, height: int, hdr: bool):
    """Yield (source_time, BGR ndarray) for every source frame in [start, end], scaled to width x height."""
    import numpy as np

    vf = (HDR_TO_SDR + "," if hdr else "") + f"scale={width}:{height},format=bgr24"
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", str(path),
           "-t", f"{max(end - start, 0.04):.3f}", "-vf", vf, "-fps_mode", "passthrough",
           "-f", "rawvideo", "-"]
    fps = probe(path).fps or 30.0
    first = math.ceil(start * fps - 1e-6) / fps  # accurate seek starts at the first frame at/after `start`
    size = width * height * 3
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdout is not None
    k = 0
    try:
        while True:
            buf = proc.stdout.read(size)
            if len(buf) < size:
                break
            yield first + k / fps, np.frombuffer(buf, np.uint8).reshape(height, width, 3)
            k += 1
    finally:
        proc.stdout.close()
        proc.wait()
    if proc.returncode not in (0, None) and k == 0:
        raise TrackError(f"ffmpeg không đọc được {path}: {proc.stderr.read().decode(errors='replace')[-400:]}")


def _new_tracker():
    try:
        import cv2
    except ImportError:
        raise TrackError('chưa cài OpenCV — chạy: pip install -e ".[track]"') from None
    params = cv2.TrackerCSRT_Params()
    params.use_segmentation = True
    return cv2.TrackerCSRT_create(params)


CUT_MAD, CUT_CORR = 30.0, 0.75  # measured on real footage: cuts score MAD 28-74 or histogram corr < 0.75


def _signature(frame):
    import cv2

    small = cv2.resize(frame, (160, max(round(frame.shape[0] * 160 / frame.shape[1]), 2)))
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [16, 8], [0, 180, 0, 256])
    cv2.normalize(hist, hist)
    return hist, cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype("float32")


def is_cut(a, b) -> bool:
    """True when two consecutive frames belong to different shots (a cut): tracking across it is meaningless."""
    import cv2
    import numpy as np

    (ha, ga), (hb, gb) = a, b
    return float(np.mean(np.abs(ga - gb))) > CUT_MAD or cv2.compareHist(ha, hb, cv2.HISTCMP_CORREL) < CUT_CORR


def _run(frames: list, box_px: tuple[int, int, int, int]) -> list[tuple[tuple[float, float, float, float], bool]]:
    """Track through `frames`; stops early at a cut (the result is then shorter than `frames`)."""
    tracker = _new_tracker()
    tracker.init(frames[0], box_px)
    out = [(tuple(float(v) for v in box_px), True)]
    last = out[0][0]
    sig = _signature(frames[0])
    for frame in frames[1:]:
        nxt = _signature(frame)
        if is_cut(sig, nxt):
            break
        sig = nxt
        ok, box = tracker.update(frame)
        if ok and box[2] > 2 and box[3] > 2:
            last = tuple(float(v) for v in box)
            out.append((last, True))
        else:
            out.append((last, False))
    return out


def smooth(points: list[TrackPoint], strength: float = 0.5) -> list[TrackPoint]:
    """Zero-phase smoothing (forward + backward exponential pass): removes tracker jitter without the lag a
    one-way filter adds. strength 0 = raw, 1 = very smooth."""
    if strength <= 0 or len(points) < 3:
        return points
    alpha = 1.0 - 0.85 * min(strength, 1.0)

    def ema(values: list[float]) -> list[float]:
        out, acc = [], values[0]
        for v in values:
            acc += alpha * (v - acc)
            out.append(acc)
        return out

    cols = list(zip(*[(p.x, p.y, p.w, p.h) for p in points]))
    smoothed = []
    for col in cols:
        fwd = ema(list(col))
        bwd = ema(fwd[::-1])[::-1]
        smoothed.append(bwd)
    return [TrackPoint(p.t, x, y, w, h, p.ok) for p, x, y, w, h in zip(points, *smoothed)]


def track_object(video: Path, *, name: str, at: float, box: tuple[float, float, float, float],
                 until: float | None = None, back: float | None = None, smoothing: float = 0.5,
                 on_progress=None) -> Track:
    """Track the object inside ``box`` (x, y, w, h as fractions of the source frame; x, y = top-left corner)
    seen at source time ``at``, forward to ``until`` and backward to ``back`` (source seconds)."""
    require_ffmpeg()
    video = Path(video)
    info = probe(video)
    if not info.has_video or info.is_image:
        raise TrackError(f"{video.name} không phải video")
    bx, by, bw, bh = box
    if not (0 <= bx < 1 and 0 <= by < 1 and 0 < bw <= 1 and 0 < bh <= 1 and bx + bw <= 1.001 and by + bh <= 1.001):
        raise TrackError("box phải là x,y,w,h theo tỉ lệ khung nguồn (0..1), vd 0.30,0.30,0.45,0.40")
    end = min(until if until is not None else info.duration, info.duration)
    begin = max(back if back is not None else at, 0.0)
    if not begin <= at <= end:
        raise TrackError(f"--at {at}s phải nằm trong [{begin}, {end}]")
    width = min(TRACK_WIDTH, info.width) // 2 * 2
    height = round(info.height * width / info.width) // 2 * 2
    box_px = (int(bx * width), int(by * height), max(int(bw * width), 4), max(int(bh * height), 4))

    try:
        frames = list(_frames(video, begin, end + 0.5 / (info.fps or 30), width, height, info.is_hdr))
    except MediaError as exc:
        raise TrackError(str(exc)) from None
    if not frames:
        raise TrackError("không đọc được khung hình nào trong đoạn này")
    times = [t for t, _ in frames]
    k0 = min(range(len(times)), key=lambda k: abs(times[k] - at))
    imgs = [f for _, f in frames]
    forward = _run(imgs[k0:], box_px)
    if on_progress:
        on_progress(0.5 if k0 else 1.0)
    backward = _run(imgs[: k0 + 1][::-1], box_px)[::-1] if k0 else []
    first = k0 - (len(backward) - 1) if backward else k0
    results = backward[:-1] + forward if backward else forward
    times = times[first:first + len(results)]

    points = []
    for t, ((x, y, w, h), ok) in zip(times, results):
        points.append(TrackPoint(t, (x + w / 2) / width, (y + h / 2) / height, w / width, h / height, ok))
    points = smooth(points, smoothing)
    track = Track(name=name, source=str(video), points=points, fps=info.fps or 30.0)
    track.stopped = [label for label, hit in (("đầu", back is not None and track.start > begin + 0.05),
                                              ("cuối", track.end < end - 0.05)) if hit]
    return track


def describe(track: Track) -> str:
    first, last = track.points[0], track.points[-1]
    travel = math.hypot(last.x - first.x, last.y - first.y)
    lost = f", mất dấu {track.lost:.0%} khung" if track.lost else ""
    cut = f"; dừng ở điểm cắt cảnh ({', '.join(track.stopped)})" if track.stopped else ""
    return (f"track '{track.name}': {track.start:.2f}–{track.end:.2f}s nguồn, {len(track.points)} khung, "
            f"tâm ({first.x:.2f},{first.y:.2f}) → ({last.x:.2f},{last.y:.2f}), dịch {travel:.2f} khung{lost}{cut}")


def track_sheet(track: Track, video: Path, out: Path, *, count: int = 8, cols: int = 4, width: int = 300) -> Path:
    """Contact sheet of the tracked range with the box drawn on each tile (green = tracked, red = lost),
    so an agent can check the track before sticking graphics to it."""
    from PIL import Image, ImageDraw

    from .media import extract_frame

    out = Path(out)
    tmp = out.parent / f".{out.stem}_tiles"
    span = track.end - track.start
    times = [track.start + span * (k + 0.5) / count for k in range(count)] if span > 0 else [track.start]
    tiles = []
    for k, t in enumerate(times):
        tile = Image.open(extract_frame(Path(video), t, tmp / f"{k:02d}.jpg", width=width)).convert("RGB")
        p = track.at(t)
        tw, th = tile.size
        draw = ImageDraw.Draw(tile)
        x0, y0 = (p.x - p.w / 2) * tw, (p.y - p.h / 2) * th
        x1, y1 = (p.x + p.w / 2) * tw, (p.y + p.h / 2) * th
        color = (60, 230, 120) if p.ok else (255, 70, 70)
        draw.rectangle([x0, y0, x1, y1], outline=color, width=3)
        draw.ellipse([p.x * tw - 4, p.y * th - 4, p.x * tw + 4, p.y * th + 4], fill=color)
        draw.rectangle([0, 0, 92, 20], fill=(0, 0, 0))
        draw.text((5, 4), f"{t:.2f}s{'' if p.ok else ' LOST'}", fill=(255, 230, 0))
        tiles.append(tile)
    tw, th = tiles[0].size
    rows = -(-len(tiles) // cols)
    sheet = Image.new("RGB", (tw * cols + 4 * (cols - 1), th * rows + 4 * (rows - 1)), (20, 20, 20))
    for k, tile in enumerate(tiles):
        sheet.paste(tile, ((k % cols) * (tw + 4), (k // cols) * (th + 4)))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    return out
