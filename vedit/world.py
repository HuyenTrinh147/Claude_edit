"""Where things are on screen: maps a point in a source video (e.g. a tracked object) to canvas pixels at any
timeline frame, reproducing the renderer's geometry — frame-quantized clip layout, fit (cover / contain / blur),
Ken Burns zoom and the timeline punch / shake camera. Used to stick HUD graphics to real objects."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from .edl import Anchor, Clip, EditPlan, frame_layout

# camera-move envelopes, shared by the ffmpeg expression (render.motion_filter) and the Python mirror below
PUNCH_ATTACK = 0.2       # fraction of a punch spent zooming in
SHAKE_ZOOM = 2.2         # shake zooms in by this × amount so the jitter never shows the frame edge
SHAKE_FREQ_X, SHAKE_FREQ_Y = 2.4, 3.1  # radians per frame


def motion_window(start: float, duration: float, fps: int) -> tuple[int, int]:
    return round(start * fps), max(2, round(duration * fps))


def camera_at(plan: EditPlan, k: int, fps: int) -> tuple[float, float, float]:
    """Timeline camera at frame k: (zoom, dx, dy) with dx/dy as fractions of the frame size."""
    z, dx, dy = 1.0, 0.0, 0.0
    for m in plan.motion:
        a, d = motion_window(m.start, m.duration, fps)
        if not a <= k <= a + d:
            continue
        p = (k - a) / d
        if m.type == "punch":
            env = math.sin(math.pi / 2 * p / PUNCH_ATTACK) if p < PUNCH_ATTACK else \
                math.cos(math.pi / 2 * (p - PUNCH_ATTACK) / (1 - PUNCH_ATTACK))
            z += m.amount * env
        else:
            decay = 1 - p
            z += SHAKE_ZOOM * m.amount * decay
            dx += m.amount * math.sin((k - a) * SHAKE_FREQ_X) * decay
            dy += m.amount * math.cos((k - a) * SHAKE_FREQ_Y) * decay
    return z, dx, dy


@dataclass
class Span:
    index: int
    clip: Clip
    first: int          # first timeline frame
    frames: int
    overlap: int        # frames shared with the previous clip (transition)
    path: Path | None   # resolved media file (None for colour cards)
    src_w: int = 0
    src_h: int = 0


class World:
    def __init__(self, plan: EditPlan, base_dir: Path | None, fps: int, probe=None):
        self.plan, self.fps = plan, fps
        self.W, self.H = plan.canvas.width, plan.canvas.height
        self.base_dir = Path(base_dir) if base_dir else None
        frames, overlaps, self.total = frame_layout(plan, fps)
        self.spans: list[Span] = []
        first = 0
        for i, clip in enumerate(plan.clips):
            if i:
                first = self.spans[-1].first + frames[i - 1] - overlaps[i]
            path = None
            w = h = 0
            if not clip.is_color and self.base_dir is not None:
                path = plan.resolve(clip.source, self.base_dir).resolve()
                if probe is not None and path.exists():
                    info = probe(path)
                    w, h = info.width, info.height
            self.spans.append(Span(i, clip, first, frames[i], overlaps[i], path, w, h))
        self._tracks: dict[str, object] = {}

    # ---- clips ------------------------------------------------------------------------------------

    def span_at(self, k: int) -> Span | None:
        """The clip on screen at timeline frame k (the incoming clip from halfway through a transition)."""
        current = None
        for span in self.spans:
            if span.first + span.overlap / 2 <= k:
                current = span
            else:
                break
        if current is None or k >= current.first + current.frames:
            return None
        return current

    def source_time(self, span: Span, k: int) -> float:
        """Source seconds shown at timeline frame k (held during a freeze)."""
        j = k - span.first
        held = min(j / self.fps * span.clip.speed, span.clip.source_duration - 1e-3)
        return span.clip.start + max(held, 0.0)

    # ---- geometry ---------------------------------------------------------------------------------

    def fit(self, span: Span, sx: float, sy: float) -> tuple[float, float, float, float]:
        """Source fractions -> canvas px after fit, plus the px size of one source width / height."""
        W, H, c = self.W, self.H, span.clip
        if not span.src_w or not span.src_h:
            return sx * W, sy * H, W, H
        if c.fit == "cover":
            s = max(W / span.src_w, H / span.src_h)
            ws, hs = span.src_w * s, span.src_h * s
            return sx * ws - (ws - W) * c.focus_x, sy * hs - (hs - H) * c.focus_y, ws, hs
        s = min(W / span.src_w, H / span.src_h)
        ws, hs = span.src_w * s, span.src_h * s
        return (W - ws) / 2 + sx * ws, (H - hs) / 2 + sy * hs, ws, hs

    def clip_zoom(self, span: Span, k: int) -> float:
        c = span.clip
        if c.zoom == "none":
            return 1.0
        j, n = k - span.first, span.frames
        return 1 + c.zoom_amount * j / n if c.zoom == "in" else 1 + c.zoom_amount - c.zoom_amount * j / n

    def to_screen(self, k: int, x: float, y: float, span: Span | None = None) -> tuple[float, float, float]:
        """Canvas px of a point in the (fitted) clip image at frame k, through Ken Burns + timeline camera.
        Returns (x, y, total zoom)."""
        W, H = self.W, self.H
        z1 = self.clip_zoom(span, k) if span else 1.0
        x, y = (x - W / 2) * z1 + W / 2, (y - H / 2) * z1 + H / 2
        z2, dx, dy = camera_at(self.plan, k, self.fps)
        x, y = (x - W / 2 - dx * W) * z2 + W / 2, (y - H / 2 - dy * H) * z2 + H / 2
        return x, y, z1 * z2

    # ---- tracks -----------------------------------------------------------------------------------

    def track(self, name: str):
        from .track import Track, track_path

        if name not in self._tracks:
            path = track_path(self.base_dir, name) if self.base_dir else None
            self._tracks[name] = Track.load(path) if path and path.exists() else None
        return self._tracks[name]

    def box(self, anchor: Anchor, k: int) -> tuple[float, float, float, float] | None:
        """Tracked box at frame k in canvas px: (x, y, w, h) of the anchor point and box size, or None when the
        tracked video is not on screen."""
        track = self.track(anchor.track)
        span = self.span_at(k)
        if track is None or span is None or span.path is None:
            return None
        if track.source and Path(track.source).resolve() != span.path:
            return None
        p = track.at(self.source_time(span, k))
        ox, oy = _POINTS[anchor.point]
        sx, sy = p.x + ox * p.w / 2, p.y + oy * p.h / 2
        fx, fy, ws, hs = self.fit(span, sx, sy)
        x, y, z = self.to_screen(k, fx, fy, span)
        return x + anchor.dx * self.W, y + anchor.dy * self.H, p.w * ws * z, p.h * hs * z

    def point(self, k: int, x: float, y: float) -> tuple[float, float]:
        """A source-free canvas point (fractions) — screen-space HUD does not move with the camera."""
        return x * self.W, y * self.H


_POINTS = {
    "center": (0, 0), "top": (0, -1), "bottom": (0, 1), "left": (-1, 0), "right": (1, 0),
    "top_left": (-1, -1), "top_right": (1, -1), "bottom_left": (-1, 1), "bottom_right": (1, 1),
}


def check_anchor(plan: EditPlan, base_dir: Path, anchor: Anchor, start: float, end: float, where: str,
                 probe=None) -> list[str]:
    """Problems with a HUD anchor: missing track file, or the item shows while the tracked video is off
    screen / outside the tracked range (the graphic would vanish or freeze)."""
    from .track import Track, track_path

    path = track_path(base_dir, anchor.track)
    if not path.exists():
        return [f"{where}: chưa có track '{anchor.track}' ({path}) — tạo bằng `vedit track <dự án> {anchor.track} "
                f"--at <giây nguồn> --box x,y,w,h`"]
    track = Track.load(path)
    world = World(plan, base_dir, plan.canvas.fps, probe)
    k0, k1 = round(start * world.fps), min(round(end * world.fps), world.total) - 1
    off, outside = 0, []
    for k in range(k0, k1 + 1):
        span = world.span_at(k)
        if span is None or span.path is None or (track.source and Path(track.source).resolve() != span.path):
            off += 1
            continue
        s = world.source_time(span, k)
        if s < track.start - 0.1 or s > track.end + 0.1:
            outside.append(s)
    problems = []
    tolerance = 0.15 * world.fps  # a few frames at a cut are fine
    if off > tolerance:
        problems.append(f"{where}: {off / world.fps:.2f}s trong [{start:.2f}, {end:.2f}] không chiếu video của track "
                        f"'{anchor.track}' — đồ hoạ sẽ ẩn lúc đó")
    if len(outside) > tolerance:
        problems.append(f"{where}: track '{anchor.track}' chỉ có {track.start:.2f}–{track.end:.2f}s nguồn nhưng cần "
                        f"{min(outside):.2f}–{max(outside):.2f}s — đồ hoạ sẽ đứng yên; track thêm bằng --until/--back")
    return problems
