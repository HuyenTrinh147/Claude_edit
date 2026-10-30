"""Render an EditPlan to a video file with a single ffmpeg filter graph.

Text, captions and motion graphics are drawn by libass from an ASS file built in `vedit.ass`;
colour looks, punch/shake camera moves and synthesised sound effects are plain ffmpeg filters.
"""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .ass import ass_color as _ass_color  # noqa: F401  (re-exported for callers/tests)
from .ass import ass_text as _ass_text  # noqa: F401
from .ass import ass_time as _ass_time  # noqa: F401
from .ass import build_ass
from .edl import EditPlan
from .media import extract_frame, probe, require_ffmpeg

SAFE_FILTER_PATH = re.compile(r"^[\w./\-]+$")


class RenderError(RuntimeError):
    pass


@dataclass
class RenderResult:
    output: Path
    duration: float
    preview: bool
    thumbnail: Path | None
    command: list[str]
    elapsed: float


def _even(x: float) -> int:
    return max(2, int(round(x / 2)) * 2)


def _num(x: float) -> str:
    return f"{x:.3f}".rstrip("0").rstrip(".") or "0"


def _atempo_chain(speed: float) -> list[str]:
    parts = []
    while speed > 2.0:
        parts.append("atempo=2.0")
        speed /= 2.0
    while speed < 0.5:
        parts.append("atempo=0.5")
        speed /= 0.5
    if abs(speed - 1.0) > 1e-6:
        parts.append(f"atempo={speed:.5f}")
    return parts


# ---- ffmpeg graph ----------------------------------------------------------------------

AUDIO_FMT = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
SAMPLE_RATE = 48000

LOOKS = {
    "warm_food": "eq=contrast=1.06:saturation=1.22:gamma=1.02,"
                 "colorbalance=rs=0.05:gs=0.01:bs=-0.06:rm=0.04:bm=-0.04:rh=0.02:bh=-0.02,unsharp=5:5:0.35",
    "bright_clean": "eq=brightness=0.035:contrast=1.05:saturation=1.08,unsharp=5:5:0.3",
    "film": "curves=preset=vintage,eq=saturation=0.92:contrast=1.04",
    "moody": "eq=contrast=1.12:saturation=0.82:brightness=-0.03,colorbalance=rs=-0.03:bs=0.05:rh=0.03",
    "vivid": "eq=saturation=1.38:contrast=1.08,unsharp=5:5:0.3",
    "bw": "hue=s=0,eq=contrast=1.12",
}

# Synthesised sound effects (no files needed): short, clean, and mixed on the voice bus.
SFX = {
    "pop": "aevalsrc='0.8*sin(2*PI*(260+900*exp(-t*38))*t)*exp(-t*26)':s=48000:d=0.2",
    "click": "aevalsrc='0.7*sin(2*PI*2400*t)*exp(-t*140)+0.3*sin(2*PI*1200*t)*exp(-t*90)':s=48000:d=0.06",
    "ding": "aevalsrc='0.45*(sin(2*PI*1568*t)+0.5*sin(2*PI*3136*t)+0.2*sin(2*PI*4704*t))*exp(-t*4.5)':s=48000:d=1.3",
    "sparkle": "aevalsrc='0.22*(sin(2*PI*2637*t)*exp(-t*11)+gte(t,0.08)*sin(2*PI*3520*(t-0.08))*exp(-(t-0.08)*11)"
               "+gte(t,0.16)*sin(2*PI*4186*(t-0.16))*exp(-(t-0.16)*11)"
               "+gte(t,0.24)*sin(2*PI*5274*(t-0.24))*exp(-(t-0.24)*12))':s=48000:d=0.9",
    "whoosh": "anoisesrc=d=0.6:c=pink:r=48000:a=0.5,bandpass=f=1400:width_type=h:w=1800,"
              "afade=t=in:d=0.35:curve=exp,afade=t=out:st=0.35:d=0.25",
    "thud": "aevalsrc='0.9*sin(2*PI*(55+90*exp(-t*22))*t)*exp(-t*11)':s=48000:d=0.4",
    "rise": "aevalsrc='0.3*sin(2*PI*(300*t+700*t*t))*min(t/0.9,1)*exp(-max(t-0.9,0)*20)':s=48000:d=1.0",
}


def look_filters(plan: EditPlan) -> list[str]:
    look = plan.look
    filters = [LOOKS[look.preset]] if look.preset in LOOKS else []
    if look.vignette > 0:
        filters.append(f"vignette=angle={0.25 + 0.65 * look.vignette:.3f}")
    if look.grain > 0:
        filters.append(f"noise=c0s={int(4 + 16 * look.grain)}:c0f=t+u")
    return filters


def motion_filter(plan: EditPlan, fps: int, W: int, H: int) -> str | None:
    """One zoompan over the whole timeline: punch = fast zoom-in that eases back out, shake = decaying jitter."""
    if not plan.motion:
        return None
    z, x, y = ["1"], ["iw/2-(iw/zoom/2)"], ["ih/2-(ih/zoom/2)"]
    for m in plan.motion:
        a, d = round(m.start * fps), max(2, round(m.duration * fps))
        win, p = f"between(on,{a},{a + d})", f"((on-{a})/{d})"
        if m.type == "punch":
            env = f"if(lt({p},0.2),sin(PI/2*{p}/0.2),cos(PI/2*({p}-0.2)/0.8))"
            z.append(f"{m.amount:g}*if({win},{env},0)")
        else:
            decay = f"(1-{p})"
            z.append(f"{2.2 * m.amount:g}*if({win},{decay},0)")
            x.append(f"{m.amount:g}*iw*if({win},sin((on-{a})*2.4)*{decay},0)")
            y.append(f"{m.amount:g}*ih*if({win},cos((on-{a})*3.1)*{decay},0)")
    return (f"zoompan=z='{'+'.join(z)}':x='{'+'.join(x)}':y='{'+'.join(y)}'"
            f":d=1:s={W}x{H}:fps={fps}")


def frame_layout(plan: EditPlan, fps: int) -> tuple[list[int], list[int], int]:
    """Lay the timeline out in whole frames: frames per clip, frames each clip overlaps the previous one
    (transition length, 0 for a hard cut) and total frames. Clip boundaries are rounded from the plan's
    exact offsets rather than summed from rounded lengths, so video, audio and text never drift apart by
    more than half a frame, however many clips there are."""
    frames: list[int] = []
    overlaps: list[int] = []
    prev_end = 0
    for clip, offset in zip(plan.clips, plan.clip_offsets()):
        start = round(offset * fps) if clip.transition else prev_end
        end = max(start + 1, round((offset + clip.timeline_duration) * fps))
        overlap = 0
        if clip.transition and frames:
            overlap = min(max(prev_end - start, 1), frames[-1] - 1, end - start - 1)
            start = prev_end - overlap
        frames.append(end - start)
        overlaps.append(overlap)
        prev_end = end
    return frames, overlaps, prev_end


def build_command(
    plan: EditPlan,
    output: Path,
    *,
    base_dir: Path,
    work_dir: Path,
    preview: bool = False,
    font: str = "Inter",
    fonts_dir: Path | None = None,
) -> list[str]:
    """Build the ffmpeg argv. Writes the ASS subtitle file into work_dir when needed."""
    canvas = plan.canvas
    scale = 0.5 if preview else 1.0
    W, H = _even(canvas.width * scale), _even(canvas.height * scale)
    fps = min(canvas.fps, 30) if preview else canvas.fps
    clip_frames, overlaps, total_frames = frame_layout(plan, fps)
    total = total_frames / fps

    def secs(n_frames: int) -> str:
        return f"{n_frames / fps:.6f}"

    def samples(n_frames: int) -> int:
        return round(n_frames * SAMPLE_RATE / fps)

    inputs: list[str] = []
    n_inputs = 0
    graph: list[str] = []

    def add_input(*args: str) -> int:
        nonlocal n_inputs
        inputs.extend(args)
        n_inputs += 1
        return n_inputs - 1

    # 1) per-clip video + audio chains -> [v{i}] [a{i}]
    for i, clip in enumerate(plan.clips):
        n = clip_frames[i]
        has_audio = False
        if clip.is_color:
            color = clip.source.split(":", 1)[1].lstrip("#")
            idx = add_input("-f", "lavfi", "-i", f"color=c=0x{color}:s={W}x{H}:r={fps}:d={_num(clip.source_duration)}")
        else:
            path = plan.resolve(clip.source, base_dir)
            info = probe(path)
            if info.is_image:
                idx = add_input("-loop", "1", "-framerate", str(fps), "-t", _num(clip.source_duration), "-i", str(path))
            else:
                idx = add_input("-ss", _num(clip.start), "-t", _num(clip.source_duration), "-i", str(path))
                has_audio = info.has_audio and not clip.mute and clip.volume > 0

        pre = f"[{idx}:v]setpts=(PTS-STARTPTS)/{clip.speed:g},fps={fps}"
        if clip.fit == "blur":
            bw, bh = _even(W / 4), _even(H / 4)
            graph.append(f"{pre},split=2[c{i}a][c{i}b]")
            graph.append(f"[c{i}a]scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh},"
                         f"boxblur=10:2,scale={W}:{H},eq=brightness=-0.06[c{i}bg]")
            graph.append(f"[c{i}b]scale={W}:{H}:force_original_aspect_ratio=decrease:force_divisible_by=2[c{i}fg]")
            graph.append(f"[c{i}bg][c{i}fg]overlay=(W-w)/2:(H-h)/2[c{i}]")
        elif clip.fit == "contain":
            bg = canvas.background.lstrip("#")
            graph.append(f"{pre},scale={W}:{H}:force_original_aspect_ratio=decrease:force_divisible_by=2,"
                         f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x{bg}[c{i}]")
        else:
            graph.append(f"{pre},scale={W}:{H}:force_original_aspect_ratio=increase,"
                         f"crop={W}:{H}:(iw-{W})*{clip.focus_x:g}:(ih-{H})*{clip.focus_y:g}[c{i}]")

        post = []
        if clip.zoom != "none":
            a = clip.zoom_amount
            z = f"1+{a:g}*on/{n}" if clip.zoom == "in" else f"1+{a:g}-{a:g}*on/{n}"
            post.append(f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={fps}")
        post += ["setsar=1", "format=yuv420p", "tpad=stop_mode=clone:stop_duration=1",
                 f"trim=end_frame={n}", "setpts=PTS-STARTPTS", f"settb=1/{fps}"]
        graph.append(f"[c{i}]{','.join(post)}[v{i}]")

        if has_audio:
            achain = ["asetpts=PTS-STARTPTS", *_atempo_chain(clip.speed), f"volume={clip.volume:g}", AUDIO_FMT,
                      "apad", f"atrim=end_sample={samples(n)}", "asetpts=PTS-STARTPTS"]
            graph.append(f"[{idx}:a]{','.join(achain)}[a{i}]")
        else:
            graph.append(f"anullsrc=r={SAMPLE_RATE}:cl=stereo,atrim=end_sample={samples(n)},{AUDIO_FMT}[a{i}]")

    # 2) join: concat runs of hard cuts, xfade/acrossfade at transitions
    groups: list[list[int]] = [[0]]
    for i in range(1, len(plan.clips)):
        if plan.clips[i].transition:
            groups.append([i])
        else:
            groups[-1].append(i)

    def concat(idxs: list[int], tag: str) -> tuple[str, str]:
        if len(idxs) == 1:
            return f"v{idxs[0]}", f"a{idxs[0]}"
        pads = "".join(f"[v{k}][a{k}]" for k in idxs)
        graph.append(f"{pads}concat=n={len(idxs)}:v=1:a=1[gc{tag}][ga{tag}]")
        graph.append(f"[gc{tag}]settb=1/{fps}[gv{tag}]")
        return f"gv{tag}", f"ga{tag}"

    cur_v, cur_a = concat(groups[0], "0")
    cur_len = sum(clip_frames[k] for k in groups[0])
    for g, idxs in enumerate(groups[1:], start=1):
        gv, ga = concat(idxs, str(g))
        tr = plan.clips[idxs[0]].transition
        assert tr is not None
        overlap = overlaps[idxs[0]]
        offset = cur_len - overlap
        graph.append(f"[{cur_v}][{gv}]xfade=transition={tr.type}:duration={secs(overlap)}:"
                     f"offset={secs(offset)}[xv{g}]")
        graph.append(f"[{cur_a}][{ga}]acrossfade=ns={samples(overlap)}:c1=tri:c2=tri[xa{g}]")
        cur_v, cur_a = f"xv{g}", f"xa{g}"
        cur_len = offset + sum(clip_frames[k] for k in idxs)

    # 3) colour look + camera motion on the joined timeline
    post = look_filters(plan)
    move = motion_filter(plan, fps, W, H)
    if move:
        post.append(move)
    if post:
        graph.append(f"[{cur_v}]{','.join(post)}[vlook]")
        cur_v = "vlook"

    # 4) image overlays
    for k, img in enumerate(plan.images):
        idx = add_input("-loop", "1", "-t", _num(total + 1), "-i", str(plan.resolve(img.path, base_dir)))
        end = img.end if img.end is not None else total
        graph.append(f"[{idx}:v]scale={_even(img.width * W)}:-2,format=rgba,"
                     f"colorchannelmixer=aa={img.opacity:g}[img{k}]")
        graph.append(f"[{cur_v}][img{k}]overlay=x='{img.x:g}*W-w/2':y='{img.y:g}*H-h/2':"
                     f"enable='between(t,{_num(img.start)},{_num(end)})':eof_action=pass[vi{k}]")
        cur_v = f"vi{k}"

    # 5) texts, captions and motion graphics via ASS
    if plan.texts or plan.graphics or (plan.captions and plan.captions.segments):
        work_dir.mkdir(parents=True, exist_ok=True)
        (work_dir / "overlays.ass").write_text(build_ass(plan, font, fonts_dir), encoding="utf-8")
        opts = "subtitles=overlays.ass"
        if fonts_dir and fonts_dir.is_dir() and SAFE_FILTER_PATH.match(str(fonts_dir.resolve())):
            opts += f":fontsdir={fonts_dir.resolve()}"
        graph.append(f"[{cur_v}]{opts}[vsub]")
        cur_v = "vsub"
    graph.append(f"[{cur_v}]format=yuv420p[vout]")

    # 6) audio: voice bus (clips + voiceover + sfx), music bus (ducked), loudness
    voice_tracks, music_tracks = [], []
    for k, track in enumerate(plan.audio):
        if track.builtin is not None:
            chain = [SFX[track.builtin], AUDIO_FMT, f"volume={track.volume:g}"]
            if track.start > 0:
                chain.append(f"adelay=delays={int(track.start * 1000)}:all=1")
            graph.append(f"{','.join(chain)}[t{k}]")
            voice_tracks.append(k)
            continue
        dur = track.duration or max(total - track.start, 0.1)
        args = ["-stream_loop", "-1"] if track.loop and track.role == "music" else []
        idx = add_input(*args, "-ss", _num(track.source_start), "-i", str(plan.resolve(track.path, base_dir)))
        chain = [f"atrim=duration={_num(dur)}", "asetpts=PTS-STARTPTS", AUDIO_FMT, f"volume={track.volume:g}"]
        if track.fade_in > 0:
            chain.append(f"afade=t=in:st=0:d={_num(min(track.fade_in, dur))}")
        if track.fade_out > 0:
            chain.append(f"afade=t=out:st={_num(max(dur - track.fade_out, 0))}:d={_num(min(track.fade_out, dur))}")
        if track.start > 0:
            chain.append(f"adelay=delays={int(track.start * 1000)}:all=1")
        graph.append(f"[{idx}:a]{','.join(chain)}[t{k}]")
        (music_tracks if track.role == "music" else voice_tracks).append(k)

    voice = cur_a
    if voice_tracks:
        pads = f"[{cur_a}]" + "".join(f"[t{k}]" for k in voice_tracks)
        graph.append(f"{pads}amix=inputs={len(voice_tracks) + 1}:duration=first:dropout_transition=0:normalize=0[voice]")
        voice = "voice"
    mixed = voice
    if music_tracks:
        if len(music_tracks) > 1:
            pads = "".join(f"[t{k}]" for k in music_tracks)
            graph.append(f"{pads}amix=inputs={len(music_tracks)}:duration=longest:dropout_transition=0:normalize=0[music]")
            music = "music"
        else:
            music = f"t{music_tracks[0]}"
        if any(plan.audio[k].duck for k in music_tracks):
            graph.append(f"[{voice}]asplit=2[voicemain][voicesc]")
            graph.append(f"[{music}][voicesc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[musicd]")
            voice, music = "voicemain", "musicd"
        graph.append(f"[{voice}][{music}]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mixed]")
        mixed = "mixed"
    final_audio = []
    if plan.export.normalize_audio:
        final_audio += ["loudnorm=I=-14:TP=-1.5:LRA=11", AUDIO_FMT]
    final_audio += [f"atrim=end_sample={samples(total_frames)}"]
    graph.append(f"[{mixed}]{','.join(final_audio)}[aout]")

    ex = plan.export
    crf = 30 if preview else ex.crf
    preset = "veryfast" if preview else ex.encoder_preset
    return [
        "ffmpeg", "-hide_banner", "-y", "-nostats", "-progress", "pipe:1",
        *inputs,
        "-filter_complex", ";\n".join(graph),
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", "-r", str(fps),
        "-c:a", "aac", "-b:a", "128k" if preview else ex.audio_bitrate, "-ar", "48000",
        "-movflags", "+faststart", "-frames:v", str(total_frames),
        str(output.resolve()),
    ]


def render(
    plan: EditPlan,
    output: Path,
    *,
    base_dir: Path,
    preview: bool = False,
    font: str = "Inter",
    fonts_dir: Path | None = None,
    work_dir: Path | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> RenderResult:
    require_ffmpeg()
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    work_dir = (work_dir or output.parent / ".work").resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    cmd = build_command(plan, output, base_dir=Path(base_dir).resolve(), work_dir=work_dir, preview=preview,
                        font=font, fonts_dir=fonts_dir)
    (work_dir / ("preview_cmd.txt" if preview else "render_cmd.txt")).write_text(
        "\n".join(cmd), encoding="utf-8")

    total = plan.duration
    started = time.time()
    stderr_path = work_dir / "ffmpeg.log"
    with open(stderr_path, "w", encoding="utf-8") as err:
        proc = subprocess.Popen(cmd, cwd=work_dir, stdout=subprocess.PIPE, stderr=err, text=True)
        assert proc.stdout is not None
        for line in proc.stdout:
            if line.startswith("out_time_us=") and on_progress:
                try:
                    on_progress(min(int(line.split("=", 1)[1]) / 1e6 / total, 1.0))
                except ValueError:
                    pass
        proc.wait()
    if proc.returncode != 0:
        tail = "\n".join(stderr_path.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-30:])
        raise RenderError(f"ffmpeg lỗi (mã {proc.returncode}). Log: {stderr_path}\n{tail}")

    thumbnail = None
    if not preview:
        t = plan.export.thumbnail_at if plan.export.thumbnail_at is not None else min(1.0, total / 2)
        thumbnail = extract_frame(output, min(t, max(total - 0.1, 0)), output.with_suffix(".jpg"),
                                  width=plan.canvas.width)
    return RenderResult(output=output, duration=probe(output).duration, preview=preview, thumbnail=thumbnail,
                        command=cmd, elapsed=time.time() - started)
