"""Render an EditPlan to a video file with a single ffmpeg filter graph.

Text overlays and captions are rendered through an ASS subtitle file (libass), which handles
Vietnamese diacritics, outlines, boxes and simple animations far better than drawtext.
"""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .edl import CaptionSegment, Captions, EditPlan, TextOverlay
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


# ---- ASS subtitles -------------------------------------------------------------------

def _ass_color(hex_color: str, alpha: float = 1.0) -> str:
    """#RRGGBB + opacity -> &HAABBGGRR (ASS alpha: 00 = opaque)."""
    r, g, b = hex_color[1:3], hex_color[3:5], hex_color[5:7]
    aa = round((1 - alpha) * 255)
    return f"&H{aa:02X}{b}{g}{r}".upper()


def _ass_time(t: float) -> str:
    t = max(t, 0.0)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _ass_text(text: str) -> str:
    text = text.replace("\\n", "\n").replace("\\", "＼").replace("{", "(").replace("}", ")")
    return text.replace("\r", "").replace("\n", r"\N")


_POSITIONS = {  # position -> (alignment numpad, vertical margin as fraction of height)
    "top": (8, 0.08),
    "upper": (8, 0.20),
    "center": (5, 0.0),
    "lower": (2, 0.24),
    "bottom": (2, 0.09),
}


def _anchor(position: str, width: int, height: int) -> tuple[int, int, int, int]:
    align, margin_frac = _POSITIONS[position]
    margin = int(height * margin_frac)
    x = width // 2
    y = {8: margin, 5: height // 2, 2: height - margin}[align]
    return align, margin, x, y


def _style_line(name: str, *, font: str, size: int, primary: str, secondary: str, outline_color: str,
                back: str, bold: bool, border_style: int, outline: float, shadow: float, align: int,
                margin_lr: int, margin_v: int) -> str:
    return (f"Style: {name},{font},{size},{primary},{secondary},{outline_color},{back},{-1 if bold else 0},0,0,0,"
            f"100,100,0,0,{border_style},{outline:g},{shadow:g},{align},{margin_lr},{margin_lr},{margin_v},1")


def _text_events(texts: list[TextOverlay], width: int, height: int, font: str) -> tuple[list[str], list[str]]:
    styles, events = [], []
    margin_lr = int(width * 0.07)
    for i, t in enumerate(texts):
        align, margin_v, x, y = _anchor(t.position, width, height)
        if t.box:
            outline_color, border_style, outline = _ass_color(t.box_color, t.box_opacity), 3, max(t.size * 0.22, 6)
        else:
            outline_color, border_style, outline = _ass_color(t.outline_color), 1, t.outline
        styles.append(_style_line(
            f"T{i}", font=t.font or font, size=t.size, primary=_ass_color(t.color), secondary=_ass_color(t.color),
            outline_color=outline_color, back=_ass_color("#000000", 0.5), bold=t.bold, border_style=border_style,
            outline=outline, shadow=0 if t.box else 2, align=align, margin_lr=margin_lr, margin_v=margin_v,
        ))
        anim = {
            "none": "",
            "fade": r"{\fad(200,200)}",
            "pop": r"{\fad(80,150)\fscx70\fscy70\t(0,140,\fscx108\fscy108)\t(140,240,\fscx100\fscy100)}",
            "slide_up": rf"{{\an{align}\move({x},{y + int(height * 0.04)},{x},{y},0,220)\fad(150,150)}}",
        }[t.animation]
        events.append(f"Dialogue: 1,{_ass_time(t.start)},{_ass_time(t.end)},T{i},,0,0,0,,{anim}{_ass_text(t.text)}")
    return styles, events


def _estimate_words(seg: CaptionSegment) -> list[tuple[str, float, float]]:
    if seg.words:
        return [(w.text, w.start, w.end) for w in seg.words]
    words = seg.text.split()
    total_chars = sum(len(w) for w in words) or 1
    out, cursor, span = [], seg.start, seg.end - seg.start
    for w in words:
        dur = span * len(w) / total_chars
        out.append((w, cursor, cursor + dur))
        cursor += dur
    return out


def _caption_events(caps: Captions, width: int, height: int, font: str) -> tuple[list[str], list[str]]:
    align, margin_v, _, _ = _anchor(caps.position, width, height)
    margin_lr = int(width * 0.08)
    base = dict(font=caps.font or font, size=caps.size, primary=_ass_color(caps.color),
                secondary=_ass_color(caps.color), back=_ass_color("#000000", 0.4), align=align,
                margin_lr=margin_lr, margin_v=margin_v)
    if caps.style == "boxed":
        style = _style_line("Cap", outline_color=_ass_color("#000000", 0.55), bold=True, border_style=3,
                            outline=max(caps.size * 0.2, 6), shadow=0, **base)
    elif caps.style == "clean":
        style = _style_line("Cap", outline_color=_ass_color("#000000"), bold=False, border_style=1,
                            outline=3, shadow=1, **base)
    else:  # bold_pop / karaoke
        style = _style_line("Cap", outline_color=_ass_color("#000000"), bold=True, border_style=1,
                            outline=max(caps.size * 0.08, 4), shadow=2, **base)

    hl = _ass_color(caps.highlight_color)
    events = []
    for seg in caps.segments:
        text = seg.text.upper() if caps.uppercase else seg.text
        if caps.style != "karaoke":
            anim = (r"{\fad(60,60)\fscx85\fscy85\t(0,120,\fscx100\fscy100)}" if caps.style == "bold_pop"
                    else r"{\fad(80,80)}")
            events.append(f"Dialogue: 0,{_ass_time(seg.start)},{_ass_time(seg.end)},Cap,,0,0,0,,{anim}{_ass_text(text)}")
            continue
        words = _estimate_words(seg)
        if caps.uppercase:
            words = [(w.upper(), s, e) for w, s, e in words]
        for k, (_, w_start, _) in enumerate(words):
            start = seg.start if k == 0 else w_start
            end = words[k + 1][1] if k + 1 < len(words) else seg.end
            if end <= start:
                continue
            parts = []
            for j, (w, _, _) in enumerate(words):
                w = _ass_text(w)
                parts.append(rf"{{\c{hl}\fscx110\fscy110}}{w}{{\r}}" if j == k else w)
            events.append(f"Dialogue: 0,{_ass_time(start)},{_ass_time(end)},Cap,,0,0,0,,{' '.join(parts)}")
    return [style], events


def build_ass(plan: EditPlan, font: str) -> str:
    width, height = plan.canvas.width, plan.canvas.height
    styles, events = _text_events(plan.texts, width, height, font)
    if plan.captions and plan.captions.segments:
        cap_styles, cap_events = _caption_events(plan.captions, width, height, font)
        styles += cap_styles
        events += cap_events
    return "\n".join([
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding",
        *styles,
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        *events,
        "",
    ])


# ---- ffmpeg graph ----------------------------------------------------------------------

AUDIO_FMT = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
SAMPLE_RATE = 48000


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

    # 3) image overlays
    for k, img in enumerate(plan.images):
        idx = add_input("-loop", "1", "-t", _num(total + 1), "-i", str(plan.resolve(img.path, base_dir)))
        end = img.end if img.end is not None else total
        graph.append(f"[{idx}:v]scale={_even(img.width * W)}:-2,format=rgba,"
                     f"colorchannelmixer=aa={img.opacity:g}[img{k}]")
        graph.append(f"[{cur_v}][img{k}]overlay=x='{img.x:g}*W-w/2':y='{img.y:g}*H-h/2':"
                     f"enable='between(t,{_num(img.start)},{_num(end)})':eof_action=pass[vi{k}]")
        cur_v = f"vi{k}"

    # 4) texts + captions via ASS
    if plan.texts or (plan.captions and plan.captions.segments):
        work_dir.mkdir(parents=True, exist_ok=True)
        (work_dir / "overlays.ass").write_text(build_ass(plan, font), encoding="utf-8")
        opts = "subtitles=overlays.ass"
        if fonts_dir and fonts_dir.is_dir() and SAFE_FILTER_PATH.match(str(fonts_dir.resolve())):
            opts += f":fontsdir={fonts_dir.resolve()}"
        graph.append(f"[{cur_v}]{opts}[vsub]")
        cur_v = "vsub"
    graph.append(f"[{cur_v}]format=yuv420p[vout]")

    # 5) audio: voice bus (clips + voiceover + sfx), music bus (ducked), loudness
    voice_tracks, music_tracks = [], []
    for k, track in enumerate(plan.audio):
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
