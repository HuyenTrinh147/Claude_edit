"""Game HUD for "the video is a VR game" edits: reticles locking onto real objects, quest panels, meters,
counters, reward pop-ups, inventory slots, result cards, controller prompts, icons and a VR visor frame.

Every item is evaluated per output frame in Python (anchor position from a track, eased enter / exit, value
keys) and written as static ASS events; consecutive identical frames are merged, so static parts cost one
event. Event edges sit halfway between frames, so centisecond rounding never shows the wrong frame.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .ass import FontBook, alpha_tag, ass_text, ass_time, bgr
from .edl import Card, Counter, EditPlan, Icon, Meter, Panel, Popup, Prompt, Reticle, Slots, ValueKey, Visor
from .world import World

HUD_FONT = "Chakra Petch"   # techy HUD labels (bundled, Vietnamese OK)
REWARD_FONT = "Bungee"      # chunky reward text (bundled, Vietnamese OK)
DARK = "#07121C"
BASE_LAYER = 20


# ---- easing ---------------------------------------------------------------------------------------

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def ease_out(p: float) -> float:
    return 1 - (1 - clamp(p)) ** 3


def ease_in(p: float) -> float:
    return clamp(p) ** 3


def ease_inout(p: float) -> float:
    p = clamp(p)
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


def back_out(p: float, k: float = 1.9) -> float:
    p = clamp(p) - 1
    return 1 + (k + 1) * p ** 3 + k * p ** 2


def value_at(keys: list[ValueKey], t: float) -> float:
    keys = sorted(keys, key=lambda kk: kk.t)
    if t <= keys[0].t:
        return keys[0].v
    for a, b in zip(keys, keys[1:]):
        if t < b.t:
            p = (t - a.t) / (b.t - a.t) if b.t > a.t else 1.0
            e = {"linear": p, "in": ease_in(p), "out": ease_out(p), "inout": ease_inout(p), "hold": 0.0}[b.ease]
            return a.v + (b.v - a.v) * e
    return keys[-1].v


ENTER_TIME = {"pop": 0.3, "slide": 0.3, "stamp": 0.24, "fade": 0.2, "none": 0.0}
EXIT_TIME = {"pop": 0.2, "slide": 0.25, "stamp": 0.2, "fade": 0.22, "none": 0.0}


@dataclass
class Env:
    scale: float = 1.0
    alpha: float = 1.0
    dy: float = 0.0     # px
    rot: float = 0.0    # degrees, counter-clockwise


def envelope(item, t: float, H: int) -> Env:
    env = Env()
    age, left = t - item.start, item.end - t
    d_in, d_out = ENTER_TIME[item.enter], EXIT_TIME[item.exit]
    if d_in and age < d_in:
        p = age / d_in
        if item.enter == "pop":
            env.scale, env.alpha = max(back_out(p), 0.0), clamp(p * 3)
        elif item.enter == "slide":
            env.dy, env.alpha = 0.035 * H * (1 - ease_out(p)), ease_out(p)
        elif item.enter == "stamp":
            env.scale = 2.1 - 1.1 * (p / 0.72) ** 2 if p < 0.72 else 1 - 0.07 * math.sin(math.pi * (p - 0.72) / 0.28)
            env.rot, env.alpha = -9 * (1 - ease_out(p)), clamp(p * 4)
        else:
            env.alpha = p
    if d_out and left < d_out:
        q = clamp(left / d_out)
        if item.exit in ("pop", "stamp"):
            env.scale *= 0.2 + 0.8 * ease_out(q)
            env.alpha *= clamp(q * 1.6)
        elif item.exit == "slide":
            env.dy -= 0.03 * H * (1 - q)
            env.alpha *= q
        else:
            env.alpha *= q
    return env


# ---- shapes (local coordinates, origin = item centre) ------------------------------------------------

Path = list  # list of ("m"|"l"|"b", [(x, y), ...])


def rect(x0, y0, x1, y1) -> Path:
    return [("m", [(x0, y0)]), ("l", [(x1, y0), (x1, y1), (x0, y1)])]


def round_rect(x0, y0, x1, y1, r) -> Path:
    r = max(0.0, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    k = r * 0.4477
    return [("m", [(x0 + r, y0)]), ("l", [(x1 - r, y0)]), ("b", [(x1 - k, y0), (x1, y0 + k), (x1, y0 + r)]),
            ("l", [(x1, y1 - r)]), ("b", [(x1, y1 - k), (x1 - k, y1), (x1 - r, y1)]),
            ("l", [(x0 + r, y1)]), ("b", [(x0 + k, y1), (x0, y1 - k), (x0, y1 - r)]),
            ("l", [(x0, y0 + r)]), ("b", [(x0, y0 + k), (x0 + k, y0), (x0 + r, y0)])]


def circle(cx, cy, r) -> Path:
    k = r * 0.5523
    return [("m", [(cx + r, cy)]), ("b", [(cx + r, cy + k), (cx + k, cy + r), (cx, cy + r)]),
            ("b", [(cx - k, cy + r), (cx - r, cy + k), (cx - r, cy)]),
            ("b", [(cx - r, cy - k), (cx - k, cy - r), (cx, cy - r)]),
            ("b", [(cx + k, cy - r), (cx + r, cy - k), (cx + r, cy)])]


def polygon(points) -> Path:
    return [("m", [points[0]]), ("l", list(points[1:]))]


def stroke(points, width) -> Path:
    """Thick polyline as one quad per segment (joins overlap, fine for neon strokes)."""
    out: Path = []
    w = width / 2
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        length = math.hypot(x1 - x0, y1 - y0) or 1.0
        nx, ny = -(y1 - y0) / length * w, (x1 - x0) / length * w
        ex, ey = (x1 - x0) / length * w * 0.5, (y1 - y0) / length * w * 0.5  # extend a bit to close joins
        out += polygon([(x0 + nx - ex, y0 + ny - ey), (x1 + nx + ex, y1 + ny + ey),
                        (x1 - nx + ex, y1 - ny + ey), (x0 - nx - ex, y0 - ny - ey)])
    return out


def arc(cx, cy, r, width, a0, a1, steps=48) -> Path:
    """Ring segment from angle a0 to a1 (degrees, 0 = up, clockwise)."""
    if a1 - a0 < 0.5:
        return []
    n = max(2, int(steps * (a1 - a0) / 360) + 1)
    outer, inner = [], []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        sx, sy = math.sin(a), -math.cos(a)
        outer.append((cx + (r + width / 2) * sx, cy + (r + width / 2) * sy))
        inner.append((cx + (r - width / 2) * sx, cy + (r - width / 2) * sy))
    return polygon(outer + inner[::-1])


def star5(cx, cy, R, ratio=0.45) -> Path:
    pts = []
    for i in range(10):
        a = math.radians(i * 36)
        r = R if i % 2 == 0 else R * ratio
        pts.append((cx + r * math.sin(a), cy - r * math.cos(a)))
    return polygon(pts)


def triangle(cx, cy, size, direction="right") -> Path:
    s = size
    pts = {"right": [(cx - s * 0.5, cy - s * 0.6), (cx + s * 0.6, cy), (cx - s * 0.5, cy + s * 0.6)],
           "down": [(cx - s * 0.6, cy - s * 0.5), (cx + s * 0.6, cy - s * 0.5), (cx, cy + s * 0.6)],
           "up": [(cx - s * 0.6, cy + s * 0.5), (cx + s * 0.6, cy + s * 0.5), (cx, cy - s * 0.6)]}[direction]
    return polygon(pts)


def bracket_corners(w, h, arm, width, ox=0.0, oy=0.0) -> Path:
    """Four L-shaped corner brackets around a w x h box centred on (ox, oy)."""
    x0, y0, x1, y1 = ox - w / 2, oy - h / 2, ox + w / 2, oy + h / 2
    out: Path = []
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        out += stroke([(cx + sx * arm, cy), (cx, cy), (cx, cy + sy * arm)], width)
    return out


def icon_path(name: str, size: float) -> list[tuple[Path, str]]:
    """Icon drawn in a box of `size` px centred on the origin -> [(path, role)] with role 'fill' | 'detail'."""
    u = size / 100
    if name == "star":
        return [(star5(0, 4 * u, 52 * u, 0.46), "fill")]
    if name == "check":
        return [(stroke([(-34 * u, 0), (-10 * u, 26 * u), (36 * u, -26 * u)], 17 * u), "fill")]
    if name == "lock":
        return [(arc(0, -8 * u, 24 * u, 11 * u, -90, 90), "fill"),
                (polygon([(-30 * u, -8 * u), (-30 * u, -8 * u - 1), (-30 * u + 1, -8 * u)]), "fill"),
                (round_rect(-36 * u, -6 * u, 36 * u, 46 * u, 9 * u), "fill"),
                (round_rect(-5 * u, 8 * u, 5 * u, 30 * u, 4 * u), "detail")]
    if name == "coin":
        return [(circle(0, 0, 46 * u), "fill"), (arc(0, 0, 33 * u, 6 * u, 0, 360), "detail"),
                (round_rect(-6 * u, -20 * u, 6 * u, 20 * u, 3 * u), "detail")]
    if name == "heart":
        return [([("m", [(0, 44 * u)]), ("b", [(-30 * u, 22 * u), (-50 * u, 4 * u), (-50 * u, -16 * u)]),
                  ("b", [(-50 * u, -38 * u), (-24 * u, -50 * u), (0, -26 * u)]),
                  ("b", [(24 * u, -50 * u), (50 * u, -38 * u), (50 * u, -16 * u)]),
                  ("b", [(50 * u, 4 * u), (30 * u, 22 * u), (0, 44 * u)])], "fill")]
    if name == "hand":
        parts = [round_rect(-30 * u, -6 * u, 28 * u, 46 * u, 15 * u)]
        for x, top in ((-26, -40), (-11, -48), (4, -46), (18, -36)):
            parts.append(round_rect(x * u, top * u, (x + 12) * u, 4 * u, 6 * u))
        parts.append(polygon([(-30 * u, 4 * u), (-50 * u, -12 * u), (-42 * u, -20 * u), (-22 * u, -4 * u)]))
        return [(p, "fill") for p in parts]
    if name == "clock":
        return [(circle(0, 0, 46 * u), "fill"), (circle(0, 0, 36 * u), "detail_bg"),
                (stroke([(0, 0), (0, -26 * u)], 7 * u), "fill"), (stroke([(0, 0), (18 * u, 6 * u)], 7 * u), "fill")]
    if name == "drop":
        return [([("m", [(0, -50 * u)]), ("b", [(16 * u, -24 * u), (38 * u, 0), (38 * u, 18 * u)]),
                  ("b", [(38 * u, 40 * u), (20 * u, 50 * u), (0, 50 * u)]),
                  ("b", [(-20 * u, 50 * u), (-38 * u, 40 * u), (-38 * u, 18 * u)]),
                  ("b", [(-38 * u, 0), (-16 * u, -24 * u), (0, -50 * u)])], "fill")]
    if name == "bolt":
        return [(polygon([(10 * u, -52 * u), (-30 * u, 8 * u), (-4 * u, 8 * u), (-12 * u, 52 * u),
                          (32 * u, -10 * u), (6 * u, -10 * u)]), "fill")]
    if name == "flame":
        return [([("m", [(0, -52 * u)]), ("b", [(10 * u, -24 * u), (40 * u, -10 * u), (40 * u, 16 * u)]),
                  ("b", [(40 * u, 40 * u), (22 * u, 52 * u), (0, 52 * u)]),
                  ("b", [(-22 * u, 52 * u), (-40 * u, 40 * u), (-40 * u, 16 * u)]),
                  ("b", [(-40 * u, -2 * u), (-24 * u, -12 * u), (-16 * u, -30 * u)]),
                  ("b", [(-8 * u, -16 * u), (-4 * u, -28 * u), (0, -52 * u)])], "fill"),
                ([("m", [(0, 6 * u)]), ("b", [(10 * u, 18 * u), (20 * u, 26 * u), (20 * u, 36 * u)]),
                  ("b", [(20 * u, 46 * u), (10 * u, 50 * u), (0, 50 * u)]),
                  ("b", [(-10 * u, 50 * u), (-20 * u, 46 * u), (-20 * u, 36 * u)]),
                  ("b", [(-20 * u, 26 * u), (-10 * u, 18 * u), (0, 6 * u)])], "detail")]
    return [(circle(0, 0, 40 * u), "fill")]


# ---- pen: applies an item's transform and writes ASS ------------------------------------------------

def _n(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".") if abs(x) >= 0.05 else "0"


@dataclass
class Pen:
    cx: float
    cy: float
    env: Env
    fonts: FontBook
    font: str
    layer: int
    parts: list[tuple[str, int, str]] = field(default_factory=list)

    reward_font: str = ""
    bbox: list[float] | None = None   # canvas-px extent of what was drawn (for keeping items on screen)

    def _grow(self, slot: str, x0: float, y0: float, x1: float, y1: float) -> None:
        if slot.startswith(("fly", "trail", "flash", "glow")) or slot.endswith("~"):
            return
        if self.bbox is None:
            self.bbox = [x0, y0, x1, y1]
        else:
            b = self.bbox
            b[0], b[1], b[2], b[3] = min(b[0], x0), min(b[1], y0), max(b[2], x1), max(b[3], y1)

    @property
    def origin(self) -> tuple[float, float]:
        return self.cx, self.cy + self.env.dy

    def xy(self, lx: float, ly: float) -> tuple[float, float]:
        s, rot = self.env.scale, math.radians(self.env.rot)
        x, y = lx * s, ly * s
        if rot:
            x, y = x * math.cos(rot) + y * math.sin(rot), -x * math.sin(rot) + y * math.cos(rot)
        ox, oy = self.origin
        return ox + x, oy + y

    def local(self, x: float, y: float) -> tuple[float, float]:
        """Canvas px -> this item's local coordinates (ignoring rotation)."""
        ox, oy = self.origin
        s = max(self.env.scale, 1e-3)
        return (x - ox) / s, (y - oy) / s

    def _alpha(self, opacity: float) -> str:
        return alpha_tag(clamp(opacity * self.env.alpha))

    def shape(self, slot: str, sub: int, path: Path, *, fill: str | None, opacity: float = 1.0,
              border: float = 0.0, border_color: str | None = None, border_opacity: float | None = None,
              blur: float = 0.0, shadow: float = 0.0) -> None:
        if not path or self.env.alpha <= 0.004 or self.env.scale <= 0.02:
            return
        cmds = []
        xs, ys = [], []
        for op, pts in path:
            moved = [self.xy(x, y) for x, y in pts]
            xs += [q[0] for q in moved]
            ys += [q[1] for q in moved]
            cmds.append(op + " " + " ".join(f"{_n(px)} {_n(py)}" for px, py in moved))
        self._grow(slot, min(xs) - border, min(ys) - border, max(xs) + border, max(ys) + border)
        tags = [r"\an7\pos(0,0)", rf"\bord{_n(border * self.env.scale)}" if border else r"\bord0",
                rf"\shad{_n(shadow)}" if shadow else r"\shad0"]
        if fill:
            tags.append(rf"\1c{bgr(fill)}\1a{self._alpha(opacity)}")
        else:
            tags.append(r"\1a&HFF&")
        if border:
            tags.append(rf"\3c{bgr(border_color or fill or '#FFFFFF')}"
                        rf"\3a{self._alpha(opacity if border_opacity is None else border_opacity)}")
        if shadow:
            tags.append(rf"\4c&H000000&\4a{self._alpha(0.45)}")
        if blur:
            tags.append(rf"\blur{_n(blur)}")
        self.parts.append((slot, self.layer + sub, "{" + "".join(tags) + r"\p1}" + " ".join(cmds) + r"{\p0}"))

    def glow_shape(self, slot: str, sub: int, path: Path, color: str, opacity: float = 1.0, glow: float = 0.55) -> None:
        """Neon: a blurred halo under a crisp fill."""
        self.shape(slot + "~", max(sub - 1, 0), path, fill=color, opacity=opacity * glow, border=3,
                   border_color=color, border_opacity=opacity * glow * 0.6, blur=6)
        self.shape(slot, sub, path, fill=color, opacity=opacity)

    def text(self, slot: str, sub: int, lx: float, ly: float, text: str, *, size: float, color: str,
             font: str | None = None, align: int = 5, opacity: float = 1.0, outline: float = 0.0,
             outline_color: str = DARK, shadow: tuple[float, float] | None = None, shadow_color: str = "#000000",
             rot: float = 0.0, spacing: float = 0.0, scale: float = 1.0, blur: float = 0.0,
             halo: bool = True) -> None:
        """Text at local (lx, ly). Without an outline, HUD text gets a soft dark halo so it reads on bright
        backgrounds (libass blurs only the border when there is one)."""
        s = self.env.scale * scale
        if not text or self.env.alpha <= 0.004 or s <= 0.02:
            return
        family = font or self.font
        face = self.fonts.face(family, True)
        bold = face.weight >= 600 if face else True
        x, y = self.xy(lx, ly)
        fs = self.fonts.fs(family, bold, size) * s
        tags = [rf"\an{align}\pos({_n(x)},{_n(y)})", rf"\fn{self.fonts.name(family, bold)}", rf"\fs{_n(fs)}",
                rf"\b{1 if bold else 0}", rf"\1c{bgr(color)}\1a{self._alpha(opacity)}"]
        if outline:
            tags.append(rf"\bord{_n(outline * s)}\3c{bgr(outline_color)}\3a{self._alpha(opacity)}")
        elif halo:
            tags.append(rf"\bord{_n(max(fs * 0.09, 2.5))}\3c{bgr(DARK)}\3a{self._alpha(opacity * 0.55)}")
            blur = max(blur, fs * 0.07, 2.0)
        else:
            tags.append(r"\bord0")
        if shadow:
            tags.append(rf"\xshad{_n(shadow[0] * s)}\yshad{_n(shadow[1] * s)}\4c{bgr(shadow_color)}"
                        rf"\4a{self._alpha(opacity)}")
        else:
            tags.append(r"\shad0")
        if spacing:
            tags.append(rf"\fsp{_n(spacing * s)}")
        total_rot = self.env.rot + rot
        if total_rot:
            ox, oy = self.origin
            tags.append(rf"\org({_n(ox)},{_n(oy)})\frz{total_rot:.2f}")
        if blur:
            tags.append(rf"\blur{_n(blur)}")
        tw = self.fonts.width(text, family, bold, size) * s + len(text) * spacing * s
        x0 = {1: x, 4: x, 7: x, 3: x - tw, 6: x - tw, 9: x - tw}.get(align, x - tw / 2)
        y0 = {7: y, 8: y, 9: y, 1: y - fs, 2: y - fs, 3: y - fs}.get(align, y - fs / 2)
        self._grow(slot, x0, y0, x0 + tw, y0 + fs)
        self.parts.append((slot, self.layer + sub, "{" + "".join(tags) + "}" + ass_text(text)))

    def width(self, text: str, size: float, font: str | None = None) -> float:
        family = font or self.font
        face = self.fonts.face(family, True)
        return self.fonts.width(text, family, face.weight >= 600 if face else True, size)


# ---- components -------------------------------------------------------------------------------------

def _reticle(item: Reticle, pen: Pen, t: float, box, W: int, H: int) -> None:
    bw, bh = (box[2] * (1 + 2 * item.pad), box[3] * (1 + 2 * item.pad)) if box else (item.w * W, item.h * H)
    lock = item.lock_at if item.lock_at is not None else item.start + 0.4
    scan = clamp((t - item.start) / max(lock - item.start, 0.05))
    locked = t >= lock
    since = t - lock
    grow = 1 + 0.16 * (1 - ease_out(scan)) if not locked else 1 + 0.012 * math.sin(2 * math.pi * 1.4 * since)
    flash = clamp(1 - since / 0.18) if locked else 0.0
    color = item.accent_color if locked else item.color
    w, h = bw * grow, bh * grow
    # keep the brackets on screen: clip the box to the safe area and re-centre
    m = 0.035 * W
    cx, cy = pen.origin
    x0, x1 = max(cx - w / 2, m), min(cx + w / 2, W - m)
    y0, y1 = max(cy - h / 2, m), min(cy + h / 2, H - m)
    if x1 - x0 < 40 or y1 - y0 < 40:
        return
    ox, oy, w, h = (x0 + x1) / 2 - cx, (y0 + y1) / 2 - cy, x1 - x0, y1 - y0
    arm = max(min(w, h) * 0.2, 18)
    lw = max(4.0, item.size * 0.1)
    spin = 0.0 if locked else 30 * (1 - ease_out(scan))
    saved = pen.env.rot
    pen.env.rot = saved + spin
    pen.glow_shape("corners", 2, bracket_corners(w, h, arm, lw, ox, oy), color)
    pen.env.rot = saved
    if flash > 0:
        pen.shape("flash", 4, bracket_corners(w, h, arm, lw * 2.2, ox, oy), fill="#FFFFFF", opacity=flash, blur=4)
    c = max(min(w, h) * 0.05, 9)
    pen.shape("cross", 2, stroke([(ox - c, oy), (ox + c, oy)], 3) + stroke([(ox, oy - c), (ox, oy + c)], 3),
              fill=color, opacity=0.85)
    if not locked:  # scan line sweeping the box
        phase = ((t - item.start) / 0.6) % 1
        y = oy - h / 2 + h * phase
        pen.shape("scan", 1, rect(ox - w / 2 + lw, y - 1.5, ox + w / 2 - lw, y + 1.5), fill=item.color, opacity=0.55,
                  blur=2)
    label = item.text
    sub = item.sub or ("LOCKED" if locked else "SCANNING…")
    lx, top = ox - w / 2, oy - h / 2 - lw * 1.5
    if label:
        size = item.size * 0.62
        tw = pen.width(label, size)
        th = size * 1.15
        if cy + top - th < m:  # no room above: put the tab inside the top edge
            top = oy - h / 2 + lw * 2 + th
        pen.shape("tab", 3, round_rect(lx, top - th, lx + tw + size * 0.8, top, 4), fill=color, opacity=0.92)
        pen.text("label", 4, lx + size * 0.4, top - th / 2, label, size=size, color=DARK, align=4, halo=False)
    sub_y = oy + h / 2 + lw * 1.5 + item.size * 0.3
    if cy + sub_y > H - m:
        sub_y = oy + h / 2 - lw * 2 - item.size * 0.3
    pen.text("sub", 4, lx, sub_y, sub, size=item.size * 0.46, color=color, align=4, spacing=2,
             opacity=0.95 if locked or int(t * 4) % 2 else 0.55)


def _panel(item: Panel, pen: Pen, t: float, W: int) -> None:
    sz = item.size
    pw = item.width * W
    row, title_h, pad = sz * 1.5, sz * 1.65, sz * 0.5
    ph = title_h + row * len(item.items) + pad
    x0, y0, x1, y1 = -pw / 2, -ph / 2, pw / 2, ph / 2
    pen.shape("bg", 0, round_rect(x0, y0, x1, y1, sz * 0.25), fill=DARK, opacity=0.62, border=2.5,
              border_color=item.color, border_opacity=0.9, shadow=0)
    notch = sz * 0.5
    pen.glow_shape("notch1", 2, polygon([(x0, y0 + notch), (x0, y0), (x0 + notch, y0), (x0 + notch * 0.6, y0 + 6),
                                         (x0 + 6, y0 + 6), (x0 + 6, y0 + notch * 0.6)]), item.color)
    pen.glow_shape("notch2", 2, polygon([(x1, y1 - notch), (x1, y1), (x1 - notch, y1), (x1 - notch * 0.6, y1 - 6),
                                         (x1 - 6, y1 - 6), (x1 - 6, y1 - notch * 0.6)]), item.color)
    pen.text("title", 3, x0 + pad, y0 + title_h / 2, item.text, size=sz * 0.82, color=item.color, align=4, spacing=1.5)
    pen.shape("rule", 1, rect(x0 + pad, y0 + title_h - 2, x1 - pad, y0 + title_h), fill=item.color, opacity=0.5)
    current = next((i for i in range(len(item.items))
                    if i >= len(item.checks) or item.checks[i] is None or t < item.checks[i]), None)
    for i, line in enumerate(item.items):
        cy = y0 + title_h + row * (i + 0.5) + pad * 0.3
        box = sz * 0.68
        bx = x0 + pad + box / 2
        tick = item.checks[i] if i < len(item.checks) else None
        done = tick is not None and t >= tick
        since = t - tick if done else -1.0
        bump = 1 + 0.45 * clamp(1 - since / 0.22) if done else 1.0
        b = box * bump
        if done:
            pen.shape(f"box{i}", 1, round_rect(bx - b / 2, cy - b / 2, bx + b / 2, cy + b / 2, 5),
                      fill=item.accent_color)
            pen.shape(f"tick{i}", 2, stroke([(bx - b * 0.28, cy), (bx - b * 0.08, cy + b * 0.22),
                                              (bx + b * 0.3, cy - b * 0.24)], max(b * 0.13, 4)), fill=DARK)
            if since < 0.35:
                sweep = ease_out(since / 0.35)
                pen.shape(f"rowflash{i}", 0, rect(x0 + 4, cy - row / 2 + 4, x0 + 4 + (pw - 8) * sweep, cy + row / 2 - 4),
                          fill=item.accent_color, opacity=0.35 * (1 - sweep))
        else:
            pen.shape(f"box{i}", 1, round_rect(bx - b / 2, cy - b / 2, bx + b / 2, cy + b / 2, 5), fill=None,
                      border=2.5, border_color=item.color, border_opacity=0.9)
        if i == current and int(t * 3) % 2 == 0:
            pen.shape(f"cur{i}", 2, triangle(x0 + pad * 0.45, cy, sz * 0.22), fill=item.color)
        pen.text(f"item{i}", 3, bx + box / 2 + sz * 0.4, cy, line, size=sz * 0.78,
                 color=item.accent_color if done else item.text_color, align=4, opacity=0.8 if done else 1.0)


def _meter(item: Meter, pen: Pen, t: float, W: int, H: int) -> None:
    v = clamp(value_at(item.keys, t))
    T = item.thickness
    horiz = item.orientation == "horizontal"
    L = item.length * (W if horiz else H)

    def at(u: float, w: float) -> tuple[float, float]:
        return (-L / 2 + u * L, w) if horiz else (w, L / 2 - u * L)

    def band(u0: float, u1: float, w0: float, w1: float) -> Path:
        (ax, ay), (bx, by) = at(u0, w0), at(u1, w1)
        return rect(min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))

    pen.shape("bg", 0, band(0, 1, -T / 2, T / 2), fill=DARK, opacity=0.6, border=2.5, border_color=item.color)
    inside = item.zone is not None and item.zone[0] <= v <= item.zone[1]
    if item.zone:
        lo, hi = item.zone
        pen.shape("zone", 1, band(lo, hi, -T / 2, T / 2), fill=item.accent_color, opacity=0.8 if inside else 0.38,
                  blur=0 if not inside else 1)
        for u in (lo, hi):
            pen.shape(f"zedge{u}", 3, band(u - 0.002, u + 0.002, -T * 0.85, T * 0.85), fill=item.accent_color, opacity=0.95)
    for k in range(1, 10):
        pen.shape(f"tick{k}", 1, band(k / 10 - 0.0015, k / 10 + 0.0015, T / 2 + 3, T / 2 + 3 + T * (0.45 if k == 5 else 0.25)),
                  fill=item.color, opacity=0.55)
    if item.style == "fill":
        if v > 0.003:
            pen.shape("fill", 2, band(0, v, -T / 2 + 3, T / 2 - 3), fill=item.accent_color if inside else item.color,
                      opacity=0.88)
            pen.glow_shape("edge", 3, band(max(v - 0.004, 0), v, -T / 2 - 2, T / 2 + 2), "#FFFFFF")
    else:
        pen.glow_shape("needle", 3, band(v - 0.003, v + 0.003, -T * 0.95, T * 0.95), "#FFFFFF")
        px, py = at(v, -T * 0.95 - 10)
        pen.shape("pointer", 3, triangle(px, py, T * 0.45, "down" if horiz else "right"), fill="#FFFFFF")
    if horiz:
        label_at, value_at_ = (-L / 2, -T / 2 - item.size * 0.55, 4), (L / 2, -T / 2 - item.size * 0.55, 6)
    else:
        label_at, value_at_ = (0, -L / 2 - item.size * 1.25, 5), (0, -L / 2 - item.size * 0.5, 5)
    if item.text:
        pen.text("label", 3, label_at[0], label_at[1], item.text, size=item.size * 0.62, color=item.color,
                 align=label_at[2], spacing=1.5)
    if item.show_value:
        pen.text("value", 3, value_at_[0], value_at_[1], f"{round(v * 100)}%", size=item.size * 0.66,
                 color=item.accent_color if inside else item.text_color, align=value_at_[2])


def format_value(item: Counter, v: float) -> str:
    if item.format == "timer":
        s = max(int(round(v)), 0)
        body = f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"
    elif item.format == "combo":
        body = f"×{round(v)}"
    elif item.format == "percent":
        body = f"{round(v)}%"
    else:
        body = f"{round(v):,}"
    return f"{item.prefix}{body}{item.suffix}"


def _counter(item: Counter, pen: Pen, t: float) -> None:
    v = value_at(item.keys, t)
    text = format_value(item, v)
    sz = item.size
    bump = 1.0
    for key in sorted(item.keys, key=lambda kk: kk.t)[1:]:
        if 0 <= t - key.t < 0.2:
            bump = 1 + 0.22 * (1 - (t - key.t) / 0.2)
    digit_w = max(pen.width(d, sz) for d in "0123456789")
    widths = [digit_w if ch.isdigit() else pen.width(ch, sz) for ch in text]
    widest = max((format_value(item, k.v) for k in item.keys), key=len)
    full = max(sum(digit_w if ch.isdigit() else pen.width(ch, sz) for ch in widest), sum(widths))
    label_h, num_h, gap = (sz * 0.48, sz * 0.95, sz * 0.14) if item.text else (0.0, sz * 0.95, 0.0)
    total_h = label_h + gap + num_h
    if item.box:
        label_w = pen.width(item.text, sz * 0.5) + 2 * len(item.text) if item.text else 0
        bw, bh = max(full, label_w) + sz * 0.9, total_h + sz * 0.5
        pen.shape("bg", 0, round_rect(-bw / 2, -bh / 2, bw / 2, bh / 2, sz * 0.22), fill=DARK, opacity=0.6, border=2.5,
                  border_color=item.color, border_opacity=0.85)
    if item.text:
        pen.text("label", 3, 0, -total_h / 2 + label_h / 2, item.text, size=sz * 0.5, color=item.color, spacing=2)
    x = -sum(widths) / 2
    cy = total_h / 2 - num_h / 2
    for i, (ch, w) in enumerate(zip(text, widths)):
        pen.text(f"ch{i}", 3, x + w / 2, cy, ch, size=sz, color=item.text_color, outline=sz * 0.05, scale=bump)
        x += w


def _popup(item: Popup, pen: Pen, t: float, H: int) -> None:
    age, dur = t - item.start, item.end - item.start
    pen.env.dy -= item.rise * H * ease_out(age / max(dur, 0.01))
    sz = item.size
    if item.burst and age < 0.45:
        p = age / 0.45
        r0, r1 = sz * (0.5 + 1.4 * ease_out(p)), sz * (0.9 + 2.2 * ease_out(p))
        rays: Path = []
        for i in range(12):
            a = math.radians(i * 30 + 8)
            sx, sy = math.sin(a), -math.cos(a)
            wdt = sz * 0.07 * (1 - p)
            nx, ny = -sy * wdt, sx * wdt
            rays += polygon([(sx * r0 + nx, sy * r0 + ny), (sx * r1, sy * r1), (sx * r0 - nx, sy * r0 - ny)])
        pen.shape("rays", 0, rays, fill=item.accent_color, opacity=0.9 * (1 - p))
        pen.shape("ring", 0, arc(0, 0, sz * (0.6 + 1.8 * ease_out(p)), sz * 0.08 * (1 - p) + 1, 0, 360),
                  fill="#FFFFFF", opacity=0.8 * (1 - p))
    pen.text("text", 3, 0, 0, item.text, size=sz, color=item.accent_color, font=item.font or pen.reward_font,
             outline=sz * 0.085, outline_color="#1A0F2E", shadow=(sz * 0.05, sz * 0.07), shadow_color=item.shadow_color,
             rot=item.tilt)
    if item.sub:
        sub_alpha = clamp((age - 0.12) / 0.15)
        pen.text("sub", 3, 0, sz * 0.82, item.sub, size=sz * 0.42, color=item.text_color, font=item.font or pen.reward_font,
                 outline=sz * 0.05, outline_color="#1A0F2E", rot=item.tilt, opacity=sub_alpha)


def _bezier(p0, p1, p2, u):
    return ((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u ** 2 * p2[0],
            (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u ** 2 * p2[1])


def _chip(pen: Pen, slot: str, sub: int, x: float, y: float, r: float, item: Slots, i: int, scale: float = 1.0) -> None:
    r *= scale
    pen.shape(slot + "c", sub, circle(x, y, r), fill=item.accent_color, border=3, border_color=DARK)
    icon = item.icons[i] if i < len(item.icons) else None
    if icon:
        for n, (path, role) in enumerate(icon_path(icon, r * 1.2)):
            moved = [(op, [(px + x, py + y) for px, py in pts]) for op, pts in path]
            pen.shape(f"{slot}i{n}", sub + 1, moved, fill=DARK if role == "fill" else item.accent_color)
    elif i < len(item.items):
        pen.text(slot + "t", sub + 1, x, y, item.items[i][:4], size=r * 0.95, color=DARK)


def _slots(item: Slots, pen: Pen, t: float, world: World, k: int) -> None:
    S, gap = item.slot_size, item.slot_size * 0.18
    total = item.count * S + (item.count - 1) * gap
    centers = [(-total / 2 + S / 2 + i * (S + gap), 0.0) for i in range(item.count)]
    filled = 0
    for i, (sx, sy) in enumerate(centers):
        arrive = item.times[i] if i < len(item.times) else None
        landed = arrive is not None and t >= arrive
        filled += landed
        since = t - arrive if landed else -1.0
        hot = clamp(1 - since / 0.3) if landed else 0.0
        pen.shape(f"slot{i}", 0, round_rect(sx - S / 2, sy - S / 2, sx + S / 2, sy + S / 2, S * 0.18), fill=DARK,
                  opacity=0.6, border=2.5 + 2 * hot, border_color=item.accent_color if hot > 0 else item.color)
        if hot > 0:
            pen.shape(f"slotflash{i}", 1, round_rect(sx - S / 2, sy - S / 2, sx + S / 2, sy + S / 2, S * 0.18),
                      fill=item.accent_color, opacity=0.45 * hot)
        if landed:
            _chip(pen, f"chip{i}", 2, sx, sy, S * 0.36, item, i, scale=1 + 0.3 * hot)
            if i < len(item.items):
                pen.text(f"name{i}", 3, sx, sy + S / 2 + item.size * 0.5, item.items[i], size=item.size * 0.6,
                         color=item.text_color, opacity=clamp(since / 0.2))
        elif arrive is not None and arrive - item.fly <= t < arrive:
            u = ease_inout((t - (arrive - item.fly)) / item.fly)
            src = item.sources[i] if i < len(item.sources) else None
            box = world.box(src, k) if src else None
            gx, gy = (box[0], box[1]) if box else (item.from_x * world.W, item.from_y * world.H)
            # flight path in local coordinates (undo the item's own placement)
            p0 = pen.local(gx, gy)
            p2 = (sx, sy)
            p1 = ((p0[0] + p2[0]) / 2, min(p0[1], p2[1]) - 0.16 * world.H)
            x, y = _bezier(p0, p1, p2, u)
            for j, lagu in enumerate((0.08, 0.16, 0.24)):
                tx, ty = _bezier(p0, p1, p2, max(u - lagu, 0))
                pen.shape(f"trail{i}_{j}", 1, circle(tx, ty, S * (0.16 - j * 0.04)), fill=item.accent_color,
                          opacity=0.5 - j * 0.14)
            _chip(pen, f"fly{i}", 4, x, y, S * 0.36, item, i, scale=0.75 + 0.25 * u)


def _card(item: Card, pen: Pen, t: float, W: int) -> None:
    sz = item.size
    cw = item.width * W
    title_h, star_r = sz * 1.9, sz * 0.95
    rows = len(item.items)
    ch = title_h + star_r * 3.2 + rows * sz * 1.2 + sz * 0.8
    x0, y0, x1, y1 = -cw / 2, -ch / 2, cw / 2, ch / 2
    pen.shape("glow", 0, round_rect(x0, y0, x1, y1, sz * 0.4), fill=item.color, opacity=0.35, blur=14)
    pen.shape("bg", 1, round_rect(x0, y0, x1, y1, sz * 0.4), fill=DARK, opacity=0.88, border=3, border_color=item.color)
    pen.shape("titlebar", 1, round_rect(x0 + 10, y0 + 10, x1 - 10, y0 + title_h, sz * 0.3), fill=item.color, opacity=0.95)
    pen.text("title", 3, 0, y0 + 10 + (title_h - 10) / 2, item.text, size=sz * 1.0, color=DARK,
             font=item.font or pen.reward_font)
    sy = y0 + title_h + star_r * 1.6
    for i in range(3):
        sx = (i - 1) * star_r * 2.5
        lift = -star_r * 0.28 if i == 1 else 0.0
        big = 1.15 if i == 1 else 1.0
        at = item.start + item.star_delay + i * item.star_gap
        earned = i < item.stars and t >= at
        if earned:
            p = (t - at) / 0.2
            s = 2.3 - 1.3 * ease_in(p) if p < 1 else 1 + 0.08 * math.sin(math.pi * clamp((p - 1) * 0.2 / 0.15))
            pen.shape(f"star{i}", 2, star5(sx, sy + lift, star_r * big * s), fill=item.accent_color, border=4,
                      border_color="#1A0F2E", opacity=clamp(p * 3))
            if t - at < 0.4:
                q = (t - at) / 0.4
                pen.shape(f"starring{i}", 3, arc(sx, sy + lift, star_r * big * (1 + 1.2 * ease_out(q)), 6 * (1 - q) + 1,
                                                 0, 360), fill="#FFFFFF", opacity=1 - q)
        else:
            pen.shape(f"star{i}", 2, star5(sx, sy + lift, star_r * big), fill="#FFFFFF", opacity=0.12, border=3,
                      border_color=item.color, border_opacity=0.6)
    last = item.start + item.star_delay + max(item.stars - 1, 0) * item.star_gap + 0.25
    for i, line in enumerate(item.items):
        appear = clamp((t - last - i * 0.12) / 0.2)
        pen.text(f"line{i}", 3, 0, sy + star_r * 1.65 + sz * 1.2 * (i + 0.5), line, size=sz * 0.62,
                 color=item.text_color, opacity=appear)


def _prompt(item: Prompt, pen: Pen, t: float) -> None:
    sz = item.size
    R = sz * 0.68
    holding = item.hold is not None and t >= item.hold[0]
    p = clamp((t - item.hold[0]) / max(item.hold[1] - item.hold[0], 0.05)) if holding else 0.0
    done = holding and p >= 1
    since_done = t - item.hold[1] if done else -1.0
    blink = 0.55 + 0.45 * (0.5 + 0.5 * math.cos(2 * math.pi * 2.2 * (t - item.start))) if item.blink and not holding else 1.0
    fill = item.accent_color if done and since_done < 0.25 else DARK
    pen.shape("btn", 1, circle(0, 0, R), fill=fill, opacity=0.8, border=3, border_color=item.color)
    pen.text("key", 3, 0, 0, item.button, size=sz * (0.62 if len(item.button) == 1 else 0.44), color=item.color)
    if holding:
        pen.shape("ringbg", 1, arc(0, 0, R + 9, 7, 0, 360), fill="#FFFFFF", opacity=0.18)
        pen.glow_shape("ring", 2, arc(0, 0, R + 9, 7, 0, 360 * p), item.accent_color)
    if item.text:
        tw = pen.width(item.text, sz * 0.6)
        x0 = R + sz * 0.35
        pen.shape("pill", 0, round_rect(x0, -sz * 0.45, x0 + tw + sz * 0.7, sz * 0.45, sz * 0.45), fill=DARK,
                  opacity=0.55 * blink, border=2, border_color=item.color, border_opacity=0.8 * blink)
        pen.text("label", 3, x0 + sz * 0.35, 0, item.text, size=sz * 0.6, color=item.text_color, align=4,
                 opacity=blink, spacing=1)


def _icon(item: Icon, pen: Pen, t: float) -> None:
    age = t - item.start
    saved = (pen.env.rot, pen.env.dy)
    sx = 1.0
    if item.spin:
        if item.icon == "coin":
            sx = max(abs(math.cos(2 * math.pi * 0.9 * age)), 0.08)
        elif item.icon == "star":
            pen.env.rot += 12 * math.sin(2 * math.pi * 1.1 * age)
        else:
            pen.env.dy += item.size * 0.08 * math.sin(2 * math.pi * 1.3 * age)
    size = item.size * 1.6
    for n, (path, role) in enumerate(icon_path(item.icon, size)):
        path = [(op, [(x * sx, y) for x, y in pts]) for op, pts in path]
        if role == "fill":
            pen.shape(f"p{n}", 1, path, fill=item.accent_color, border=max(size * 0.045, 3), border_color=DARK)
        elif role == "detail_bg":
            pen.shape(f"p{n}", 2, path, fill=DARK, opacity=0.85)
        else:
            pen.shape(f"p{n}", 2, path, fill=DARK, opacity=0.55)
    pen.env.rot, pen.env.dy = saved


def _visor(item: Visor, pen: Pen, t: float, W: int, H: int) -> None:
    age = t - item.start
    boot = ease_out(age / 0.45)
    m = item.margin * W
    out = (1 - boot) * 0.05 * W
    arm, lw = 0.075 * W, 5.0
    # corners in local coords: the visor item is centred on the frame
    for name, (cx, cy, sx, sy) in {"tl": (-W / 2 + m - out, -H / 2 + m - out, 1, 1),
                                   "tr": (W / 2 - m + out, -H / 2 + m - out, -1, 1),
                                   "bl": (-W / 2 + m - out, H / 2 - m + out, 1, -1),
                                   "br": (W / 2 - m + out, H / 2 - m + out, -1, -1)}.items():
        pen.glow_shape(name, 2, stroke([(cx + sx * arm, cy), (cx, cy), (cx, cy + sy * arm)], lw), item.color)
    top = -H / 2 + m + item.size * 0.55
    sz = item.size * 0.7
    tw = pen.width(item.text, sz) + 3 * len(item.text)
    band_h = m + item.size * 1.9
    pen.shape("band", 0, rect(-W / 2, -H / 2 - 40, W / 2, -H / 2 + band_h), fill="#000000", opacity=0.3 * boot,
              blur=28)
    pen.text("title", 3, 0, top, item.text, size=sz, color=item.color, spacing=3, opacity=boot)
    gap = tw / 2 + sz * 0.8
    for side in (-1, 1):
        x_in, x_out = side * gap, side * (W / 2 - m - arm - sz * 0.6)
        if abs(x_out) > abs(x_in):
            pen.shape(f"rule{side}", 1, stroke([(x_in, top), (x_out, top)], 2), fill=item.color, opacity=0.55 * boot)
            pen.shape(f"rulecap{side}", 1, rect(x_out - 3, top - 7, x_out + 3, top + 7), fill=item.color,
                      opacity=0.8 * boot)
    small = item.size * 0.52
    row2 = top + sz * 1.25
    if item.rec:
        on = int(age * 2) % 2 == 0
        x = W / 2 - m - small * 0.4
        pen.text("rec", 3, x, row2, "REC", size=small, color=item.text_color, align=6, spacing=1.5, opacity=boot)
        pen.shape("recdot", 2, circle(x - pen.width("REC", small) - small * 0.9, row2, small * 0.28),
                  fill="#FF3B3B", opacity=boot if on else 0.15)
    if item.clock:
        s = int(age)
        pen.text("clock", 3, -W / 2 + m + small * 0.4, row2, f"T+{s // 60:02d}:{s % 60:02d}", size=small,
                 color=item.text_color, align=4, spacing=1.5, opacity=boot)
    bottom = H / 2 - m - 6
    pen.shape("btm", 1, stroke([(-0.12 * W, bottom), (0.12 * W, bottom)], 2), fill=item.color, opacity=0.5 * boot)
    for i in (-1, 0, 1):
        pen.shape(f"btmdot{i}", 1, circle(i * 0.035 * W, bottom - 14, 3.5), fill=item.color, opacity=0.7 * boot)
    if item.scanlines:
        lines: Path = []
        for y in range(0, H, 6):
            lines += rect(-W / 2, y - H / 2, W / 2, y - H / 2 + 2)
        pen.shape("scanlines", 0, lines, fill="#000000", opacity=0.12)
    sweep = (age % 3.2) / 3.2
    pen.shape("sweep", 0, rect(-W / 2, -H / 2 + H * sweep - 40, W / 2, -H / 2 + H * sweep), fill=item.color,
              opacity=0.05, blur=10)


# ---- driver -------------------------------------------------------------------------------------------

def _flusher(runs: dict, lines: list[str], edge):
    def flush(slot: str) -> None:
        first, last, lay, text = runs.pop(slot)
        lines.append(f"Dialogue: {lay},{edge(first)},{edge(last + 1)},G,,0,0,0,,{text}")
    return flush


def _keep_inside(bbox: list[float], W: int, H: int, margin: float = 0.03) -> tuple[float, float]:
    """Shift that brings a drawn extent inside the safe frame (centred when bigger than the frame)."""
    m = margin * W
    shift = []
    for lo, hi, size in ((bbox[0], bbox[2], W), (bbox[1], bbox[3], H)):
        if hi - lo > size - 2 * m:
            shift.append(size / 2 - (lo + hi) / 2)
        elif lo < m:
            shift.append(m - lo)
        elif hi > size - m:
            shift.append(size - m - hi)
        else:
            shift.append(0.0)
    return shift[0], shift[1]


def hud_events(plan: EditPlan, world: World, fonts: FontBook, default_font: str) -> list[str]:
    """ASS Dialogue lines for every HUD item, one static event per run of identical frames."""
    if not plan.hud:
        return []
    W, H, fps = world.W, world.H, world.fps
    hud_font = HUD_FONT if fonts.resolves(HUD_FONT) else default_font
    reward_font = REWARD_FONT if fonts.resolves(REWARD_FONT) else hud_font
    lines: list[str] = []

    def edge(k: int) -> str:
        return ass_time(max((k - 0.5) / fps, 0.0))

    def draw(item, pen: Pen, t: float, box, k: int) -> None:
        if item.type == "reticle":
            _reticle(item, pen, t, box, W, H)
        elif item.type == "panel":
            _panel(item, pen, t, W)
        elif item.type == "meter":
            _meter(item, pen, t, W, H)
        elif item.type == "counter":
            _counter(item, pen, t)
        elif item.type == "popup":
            _popup(item, pen, t, H)
        elif item.type == "slots":
            _slots(item, pen, t, world, k)
        elif item.type == "card":
            _card(item, pen, t, W)
        elif item.type == "prompt":
            _prompt(item, pen, t)
        elif item.type == "icon":
            _icon(item, pen, t)
        elif item.type == "visor":
            _visor(item, pen, t, W, H)

    for idx, item in enumerate(plan.hud):
        layer = BASE_LAYER + idx * 6
        k0 = max(math.ceil(item.start * fps - 1e-9), 0)
        k1 = min(math.ceil(item.end * fps - 1e-9), world.total)   # exclusive
        runs: dict[str, list] = {}   # slot -> [first_frame, last_frame, layer, text]
        lag_pos: tuple[float, float] | None = None
        flush = _flusher(runs, lines, edge)

        for k in range(k0, k1):
            t = k / fps
            box = None
            if item.anchor is not None:
                box = world.box(item.anchor, k)
                if box is None:
                    for slot in list(runs):
                        flush(slot)
                    lag_pos = None
                    continue
                target = (box[0], box[1])
                if item.anchor.lag and lag_pos is not None:
                    a = 1 - item.anchor.lag
                    lag_pos = (lag_pos[0] + a * (target[0] - lag_pos[0]), lag_pos[1] + a * (target[1] - lag_pos[1]))
                else:
                    lag_pos = target
                cx, cy = lag_pos
            elif item.type == "visor":
                cx, cy = W / 2, H / 2
            else:
                cx, cy = item.x * W, item.y * H
            pen = Pen(cx, cy, envelope(item, t, H), fonts, item.font or hud_font, layer, reward_font=reward_font)
            draw(item, pen, t, box, k)
            if item.anchor is not None and item.type not in ("reticle", "visor") and pen.bbox:
                shift = _keep_inside(pen.bbox, W, H)   # world-anchored UI must not slide off screen
                if shift != (0.0, 0.0):
                    pen = Pen(cx + shift[0], cy + shift[1], envelope(item, t, H), fonts, item.font or hud_font,
                              layer, reward_font=reward_font)
                    draw(item, pen, t, box, k)
            seen = set()
            for slot, lay, text in pen.parts:
                seen.add(slot)
                run = runs.get(slot)
                if run and run[3] == text and run[2] == lay and run[1] == k - 1:
                    run[1] = k
                else:
                    if run:
                        flush(slot)
                    runs[slot] = [k, k, lay, text]
            for slot in [s for s in runs if s not in seen]:
                flush(slot)
        for slot in list(runs):
            flush(slot)
    return lines


def hud_texts(item) -> list[str]:
    """Visible strings of a HUD item (for font / glyph checks)."""
    texts = [getattr(item, name, "") or "" for name in ("text", "sub", "prefix", "suffix", "button")]
    texts += list(getattr(item, "items", []) or [])
    if isinstance(item, Counter):
        texts += [format_value(item, k.v) for k in item.keys]
    return [t for t in texts if t]
