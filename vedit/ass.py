"""ASS (libass) layer: animated text, captions and vector motion graphics, burned in by ffmpeg's
subtitles filter. All coordinates are canvas pixels (PlayRes = canvas size).

Font sizes are normalised: libass sizes a font by its line metrics, which differ wildly between fonts
(Mali's lines are ~2.1 em tall, Inter's ~1.2 em), so the same \\fs looks tiny in one font and huge in
another. Every `size` in an EditPlan means "em ≈ 0.8 × size px", whatever the font.
"""

from __future__ import annotations

import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .edl import CaptionSegment, Captions, EditPlan, Graphic, TextOverlay

EM_PER_SIZE = 0.8


# ---- primitives -------------------------------------------------------------------------------

def ass_color(hex_color: str, alpha: float = 1.0) -> str:
    """#RRGGBB + opacity -> &HAABBGGRR (style colour; ASS alpha 00 = opaque)."""
    r, g, b = hex_color[1:3], hex_color[3:5], hex_color[5:7]
    return f"&H{round((1 - alpha) * 255):02X}{b}{g}{r}".upper()


def bgr(hex_color: str) -> str:
    """#RRGGBB -> &HBBGGRR& for inline \\1c/\\3c tags."""
    return f"&H{hex_color[5:7]}{hex_color[3:5]}{hex_color[1:3]}&".upper()


def alpha_tag(opacity: float) -> str:
    return f"&H{round((1 - opacity) * 255):02X}&"


def ass_time(t: float) -> str:
    cs = int(round(max(t, 0.0) * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_text(text: str) -> str:
    text = text.replace("\\n", "\n").replace("\\", "＼").replace("{", "(").replace("}", ")")
    return text.replace("\r", "").replace("\n", r"\N")


def _f(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")


def ms(seconds: float) -> int:
    return int(round(seconds * 1000))


# ---- vector paths (ASS drawing commands) --------------------------------------------------------

def rect_path(x0: float, y0: float, x1: float, y1: float) -> str:
    return f"m {_f(x0)} {_f(y0)} l {_f(x1)} {_f(y0)} {_f(x1)} {_f(y1)} {_f(x0)} {_f(y1)}"


def round_rect_path(w: float, h: float, r: float) -> str:
    r = max(0.0, min(r, w / 2, h / 2))
    k = r * 0.4477  # control-point inset approximating a quarter circle
    return (f"m {_f(r)} 0 l {_f(w - r)} 0 b {_f(w - k)} 0 {_f(w)} {_f(k)} {_f(w)} {_f(r)} "
            f"l {_f(w)} {_f(h - r)} b {_f(w)} {_f(h - k)} {_f(w - k)} {_f(h)} {_f(w - r)} {_f(h)} "
            f"l {_f(r)} {_f(h)} b {_f(k)} {_f(h)} 0 {_f(h - k)} 0 {_f(h - r)} "
            f"l 0 {_f(r)} b 0 {_f(k)} {_f(k)} 0 {_f(r)} 0")


def circle_path(r: float) -> str:
    k, c, d = r * 0.5523, r, 2 * r
    return (f"m {_f(d)} {_f(c)} b {_f(d)} {_f(c + k)} {_f(c + k)} {_f(d)} {_f(c)} {_f(d)} "
            f"b {_f(c - k)} {_f(d)} 0 {_f(c + k)} 0 {_f(c)} b 0 {_f(c - k)} {_f(c - k)} 0 {_f(c)} 0 "
            f"b {_f(c + k)} 0 {_f(d)} {_f(c - k)} {_f(d)} {_f(c)}")


def star_path(r: float) -> str:
    """Four-point sparkle with concave sides."""
    c, k = r, r * 0.16
    return (f"m {_f(c)} 0 b {_f(c + k)} {_f(c - k)} {_f(c + k)} {_f(c - k)} {_f(2 * c)} {_f(c)} "
            f"b {_f(c + k)} {_f(c + k)} {_f(c + k)} {_f(c + k)} {_f(c)} {_f(2 * c)} "
            f"b {_f(c - k)} {_f(c + k)} {_f(c - k)} {_f(c + k)} 0 {_f(c)} "
            f"b {_f(c - k)} {_f(c - k)} {_f(c - k)} {_f(c - k)} {_f(c)} 0")


def line_path(x0: float, y0: float, x1: float, y1: float, thickness: float) -> str:
    """A straight stroke as a thin quad, in absolute coordinates (use with \\an7\\pos(0,0))."""
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length * thickness / 2, dx / length * thickness / 2
    return (f"m {_f(x0 + nx)} {_f(y0 + ny)} l {_f(x1 + nx)} {_f(y1 + ny)} "
            f"{_f(x1 - nx)} {_f(y1 - ny)} {_f(x0 - nx)} {_f(y0 - ny)}")


def drawing(tags: str, path: str) -> str:
    return f"{{{tags}\\p1}}{path}{{\\p0}}"


# ---- fonts ------------------------------------------------------------------------------------

@dataclass(frozen=True)
class FontFace:
    path: str
    family: str      # name a plan may use: typographic family (name ID 16) or legacy family (ID 1)
    ass_name: str    # the name libass matches on (legacy family, ID 1), e.g. "Be Vietnam Pro ExtraBold"
    weight: int
    upem: int
    line_units: int  # libass sizes fonts GDI-style by usWinAscent + usWinDescent


def _read_face(path: Path) -> list[FontFace]:
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return []
    try:
        font = TTFont(str(path), lazy=True, fontNumber=0)
        os2, names, hhea = font["OS/2"], font["name"], font["hhea"]
        line = os2.usWinAscent + os2.usWinDescent or (hhea.ascent - hhea.descent)
        legacy = names.getDebugName(1)
        families = {n for n in (names.getDebugName(16), legacy) if n}
        return [FontFace(str(path), fam, legacy or fam, os2.usWeightClass, font["head"].unitsPerEm, line or 1)
                for fam in families]
    except Exception:
        return []


class FontBook:
    """Finds the font file libass will use for a family/weight and measures text with it."""

    def __init__(self, fonts_dir: Path | None = None):
        self.local: list[FontFace] = []
        self._faces: dict[tuple[str, bool], FontFace | None] = {}
        self._pil_fonts: dict[tuple[str, float], object] = {}
        self._cmaps: dict[str, set[int]] = {}
        if fonts_dir and Path(fonts_dir).is_dir():
            for path in sorted(Path(fonts_dir).iterdir()):
                if path.suffix.lower() in (".ttf", ".otf"):
                    self.local += _read_face(path)

    def face(self, family: str, bold: bool) -> FontFace | None:
        key = (family.lower(), bold)
        if key not in self._faces:
            self._faces[key] = self._find(family, bold)
        return self._faces[key]

    def _find(self, family: str, bold: bool) -> FontFace | None:
        candidates = [f for f in self.local if f.family.lower() == family.lower()]
        if not candidates and shutil.which("fc-match"):
            query = f"{family}:weight={200 if bold else 80}"
            out = subprocess.run(["fc-match", "-f", "%{file}", query], capture_output=True, text=True).stdout
            if out:  # system font: libass asks fontconfig for the family itself, so keep the requested name
                candidates = [FontFace(f.path, family, family, f.weight, f.upem, f.line_units)
                              for f in _read_face(Path(out))[:1]]
        if not candidates:
            return None
        if bold:  # fontconfig resolves a bold request to the nearest weight, heavier on a tie
            return min(candidates, key=lambda f: (abs(f.weight - 700), -f.weight))
        return min(candidates, key=lambda f: (abs(f.weight - 400), f.weight))

    def resolves(self, family: str) -> bool:
        """True when libass will find this family (bundled in fonts_dir or installed), instead of silently
        substituting another font."""
        if any(f.family.lower() == family.lower() for f in self.local):
            return True
        if not shutil.which("fc-match"):
            return True  # cannot tell
        out = subprocess.run(["fc-match", "-f", "%{family}", family], capture_output=True, text=True).stdout
        return family.lower() in (name.strip().lower() for name in out.split(","))

    def missing_chars(self, text: str, family: str, bold: bool) -> set[str]:
        face = self.face(family, bold)
        if face is None:
            return set()
        if face.path not in self._cmaps:
            try:
                from fontTools.ttLib import TTFont
                self._cmaps[face.path] = set(TTFont(face.path, lazy=True, fontNumber=0).getBestCmap() or {})
            except Exception:
                self._cmaps[face.path] = set()
        cmap = self._cmaps[face.path]
        return {c for c in text if not c.isspace() and cmap and ord(c) not in cmap}

    def name(self, family: str, bold: bool) -> str:
        """Font name to put in ASS so libass picks the face we measured."""
        face = self.face(family, bold)
        return face.ass_name if face else family

    def fs(self, family: str, bold: bool, size: float) -> float:
        """ASS \\fs that renders this family with em ≈ EM_PER_SIZE × size."""
        face = self.face(family, bold)
        em = size * EM_PER_SIZE
        return em * face.line_units / face.upem if face else em * 1.25

    def _pil(self, path: str, em: float):
        if (path, em) not in self._pil_fonts:
            from PIL import ImageFont
            self._pil_fonts[(path, em)] = ImageFont.truetype(path, size=em)
        return self._pil_fonts[(path, em)]

    def width(self, text: str, family: str, bold: bool, size: float) -> float:
        face = self.face(family, bold)
        em = size * EM_PER_SIZE
        if face:
            try:
                return float(self._pil(face.path, round(em * 4) / 4).getlength(text))
            except Exception:
                pass
        return len(text) * em * 0.56

    def block(self, text: str, family: str, bold: bool, size: float) -> tuple[float, float, int]:
        """(width, height, line count) of a possibly multi-line text block."""
        lines = text.replace("\\n", "\n").split("\n")
        line_h = self.fs(family, bold, size)
        return max(self.width(ln, family, bold, size) for ln in lines), line_h * len(lines), len(lines)


# ---- layout helpers ---------------------------------------------------------------------------

_POSITIONS = {  # position -> (alignment numpad, vertical margin as fraction of height)
    "top": (8, 0.08),
    "upper": (8, 0.20),
    "center": (5, 0.0),
    "lower": (2, 0.24),
    "bottom": (2, 0.09),
}


def anchor(position: str, width: int, height: int) -> tuple[int, int, int, int]:
    align, margin_frac = _POSITIONS[position]
    margin = int(height * margin_frac)
    x = width // 2
    y = {8: margin, 5: height // 2, 2: height - margin}[align]
    return align, margin, x, y


def style_line(name: str, *, font: str, size: float, primary: str, secondary: str, outline_color: str,
               back: str, bold: bool, border_style: int, outline: float, shadow: float, align: int,
               margin_lr: int, margin_v: int) -> str:
    return (f"Style: {name},{font},{_f(size)},{primary},{secondary},{outline_color},{back},{-1 if bold else 0},"
            f"0,0,0,100,100,0,0,{border_style},{outline:g},{shadow:g},{align},{margin_lr},{margin_lr},{margin_v},1")


def _ev(layer: int, start: float, end: float, style: str, text: str) -> str:
    return f"Dialogue: {layer},{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{text}"


POP = r"\fscx0\fscy0\t({a},{b},\fscx112\fscy112)\t({b},{c},\fscx100\fscy100)"


def pop(delay: int = 0, length: int = 260) -> str:
    return POP.format(a=delay, b=delay + int(length * 0.6), c=delay + length)


# ---- text overlays ----------------------------------------------------------------------------

def _entry_tags(anim: str, cx: float, cy: float, bbox: tuple[float, float, float, float], W: int, H: int) -> tuple[str, bool]:
    """Override tags for an entry animation. Returns (tags, uses_move)."""
    x0, y0, x1, y1 = bbox
    if anim == "fade":
        return r"\fad(220,180)", False
    if anim == "pop":
        return r"\fad(80,150)\fscx70\fscy70\t(0,140,\fscx108\fscy108)\t(140,240,\fscx100\fscy100)", False
    if anim == "bounce":
        return (r"\fad(60,150)\fscx30\fscy30\t(0,160,\fscx118\fscy118)\t(160,260,\fscx92\fscy92)"
                r"\t(260,340,\fscx103\fscy103)\t(340,400,\fscx100\fscy100)"), False
    if anim == "slide_up":
        return rf"\move({_f(cx)},{_f(cy + H * 0.045)},{_f(cx)},{_f(cy)},0,260)\fad(160,150)", True
    if anim == "slide_left":
        return rf"\move({_f(cx + W * 0.6)},{_f(cy)},{_f(cx)},{_f(cy)},0,300)\fad(0,150)", True
    if anim == "blur_in":
        return r"\fad(0,150)\blur14\t(0,320,\blur0)", False
    if anim == "wipe":
        return (rf"\fad(0,150)\clip({_f(x0)},{_f(y0)},{_f(x0 + 1)},{_f(y1)})"
                rf"\t(0,420,\clip({_f(x0)},{_f(y0)},{_f(x1)},{_f(y1)}))"), False
    return r"\fad(0,120)", False  # none, typewriter, word_pop (handled per character / word)


def _staggered(text: str, anim: str) -> str:
    """Typewriter (per character) or word_pop (per word) reveal using inline alpha tags."""
    out, k = [], 0
    if anim == "typewriter":
        visible = [c for c in text if c not in " \n"]
        step = max(25, min(60, 900 // max(len(visible), 1)))
        for ch in text:
            if ch in " \n":
                out.append(r"\N" if ch == "\n" else " ")
                continue
            t = k * step
            out.append(rf"{{\alpha&HFF&\t({t},{t + 1},\alpha&H00&)}}{ass_text(ch)}")
            k += 1
        return "".join(out)
    for li, line in enumerate(text.split("\n")):
        if li:
            out.append(r"\N")
        for wi, word in enumerate(line.split(" ")):
            if wi:
                out.append(" ")
            t = k * 140
            out.append(rf"{{\alpha&HFF&\fscy40\t({t},{t + 160},\alpha&H00&\fscy100)}}{ass_text(word)}")
            k += 1
    return "".join(out)


def text_events(texts: list[TextOverlay], W: int, H: int, default_font: str, fonts: FontBook) -> tuple[list[str], list[str]]:
    styles, events = [], []
    for i, t in enumerate(texts):
        family = t.font or default_font
        raw = t.text.replace("\\n", "\n")
        size = float(t.size)
        tw, th, _ = fonts.block(raw, family, t.bold, size)
        if tw > W * 0.88:  # auto-fit instead of letting long lines run off the frame
            size *= W * 0.88 / tw
            tw, th, _ = fonts.block(raw, family, t.bold, size)
        fs = fonts.fs(family, t.bold, size)
        cx = t.x * W if t.x is not None else W / 2
        if t.y is not None:
            cy = t.y * H
        else:
            align, margin, _, _ = anchor(t.position, W, H)
            cy = {8: margin + th / 2, 5: H / 2, 2: H - margin - th / 2}[align]

        has_shape = t.shape != "none"
        pad_x, pad_y = (0.55 if t.shape == "banner" else 0.42) * fs, 0.18 * fs
        sw, sh = tw + 2 * pad_x, th + 2 * pad_y
        bbox = (cx - sw / 2, cy - sh / 2, cx + sw / 2, cy + sh / 2)
        tags, moves = _entry_tags(t.animation, cx, cy, bbox, W, H)
        place = "" if moves else rf"\pos({_f(cx)},{_f(cy)})"
        rot = t.rotation if t.rotation else (-2.0 if t.shape == "banner" else 0.0)
        rot_tag = rf"\frz{rot:g}" if rot else ""

        if has_shape:
            shape_anim = {"typewriter": "pop", "word_pop": "pop", "blur_in": "fade"}.get(t.animation, t.animation)
            shape_tags, _ = _entry_tags(shape_anim, cx, cy, bbox, W, H)
            radius = sh / 2 if t.shape == "pill" and raw.count("\n") == 0 else (0.35 * fs if t.shape == "pill" else 6)
            fill = rf"\1c{bgr(t.shape_color)}\1a{alpha_tag(t.shape_opacity)}"
            events.append(_ev(5, t.start, t.end, "G", drawing(
                rf"\an5{place}{rot_tag}\bord0\shad3\4c&H000000&\4a&HB4&{fill}{shape_tags}",
                round_rect_path(sw, sh, radius))))

        outline, shadow = (0, 0) if has_shape else (t.outline, 2)
        border_style, outline_color = 1, ass_color(t.outline_color)
        if t.box and not has_shape:  # libass BorderStyle 3: an opaque box per line, coloured by OutlineColour
            border_style, outline_color = 3, ass_color(t.box_color, t.box_opacity)
            outline, shadow = max(fs * 0.22, 6), 0
        styles.append(style_line(
            f"T{i}", font=fonts.name(family, t.bold), size=fs, primary=ass_color(t.color), secondary=ass_color(t.color),
            outline_color=outline_color, back=ass_color("#000000", 0.55), bold=t.bold, border_style=border_style,
            outline=outline, shadow=shadow, align=5, margin_lr=int(W * 0.05), margin_v=0))
        body = _staggered(raw, t.animation) if t.animation in ("typewriter", "word_pop") else ass_text(raw)
        events.append(_ev(6, t.start, t.end, f"T{i}", rf"{{\an5{place}{rot_tag}{tags}}}{body}"))
    return styles, events


# ---- captions ---------------------------------------------------------------------------------

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


def caption_events(caps: Captions, W: int, H: int, default_font: str, fonts: FontBook) -> tuple[list[str], list[str]]:
    align, margin_v, _, _ = anchor(caps.position, W, H)
    family = caps.font or default_font
    bold = caps.style != "clean"
    fs = fonts.fs(family, bold, caps.size)
    base = dict(font=fonts.name(family, bold), size=fs, primary=ass_color(caps.color), secondary=ass_color(caps.color),
                back=ass_color("#000000", 0.4), align=align, margin_lr=int(W * 0.08), margin_v=margin_v)
    if caps.style == "boxed":
        style = style_line("Cap", outline_color=ass_color("#000000", 0.55), bold=True, border_style=3,
                           outline=max(fs * 0.2, 6), shadow=0, **base)
    elif caps.style == "clean":
        style = style_line("Cap", outline_color=ass_color("#000000"), bold=False, border_style=1,
                           outline=3, shadow=1, **base)
    else:  # bold_pop / karaoke
        style = style_line("Cap", outline_color=ass_color("#000000"), bold=True, border_style=1,
                           outline=max(fs * 0.08, 4), shadow=2, **base)

    hl = ass_color(caps.highlight_color)
    events = []
    for seg in caps.segments:
        text = seg.text.upper() if caps.uppercase else seg.text
        if caps.style != "karaoke":
            anim = (r"{\q0\fad(60,60)\fscx85\fscy85\t(0,120,\fscx100\fscy100)}" if caps.style == "bold_pop"
                    else r"{\q0\fad(80,80)}")
            events.append(_ev(1, seg.start, seg.end, "Cap", anim + ass_text(text)))
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
                w = ass_text(w)
                parts.append(rf"{{\c{hl}\fscx110\fscy110}}{w}{{\r}}" if j == k else w)
            events.append(_ev(1, start, end, "Cap", r"{\q0}" + " ".join(parts)))
    return [style], events


# ---- motion graphics --------------------------------------------------------------------------

OUT = r"\fad(0,180)"


def _label(text: str, cx: float, cy: float, g: Graphic, fonts: FontBook, default_font: str,
           start: float, end: float, delay: int) -> tuple[list[str], float, float]:
    """Pill + text centred at (cx, cy) popping in after `delay` ms. Returns events and pill size."""
    family = g.font or default_font
    tw, th, n = fonts.block(text, family, True, g.size)
    fs = fonts.fs(family, True, g.size)
    w, h = tw + 0.9 * fs, th + 0.42 * fs
    anim = pop(delay, 300) + OUT
    pill = drawing(rf"\an5\pos({_f(cx)},{_f(cy)})\bord0\shad4\4c&H000000&\4a&HA0&\1c{bgr(g.color)}{anim}",
                   round_rect_path(w, h, h / 2 if n == 1 else 0.35 * fs))
    label = (rf"{{\an5\pos({_f(cx)},{_f(cy)})\fn{fonts.name(family, True)}\fs{_f(fs)}\b1\bord0\shad0\1c{bgr(g.text_color)}{anim}}}"
             + ass_text(text))
    return [_ev(3, start, end, "G", pill), _ev(4, start, end, "G", label)], w, h


def _callout(g: Graphic, W: int, H: int, fonts: FontBook, font: str) -> list[str]:
    tx, ty = g.x * W, g.y * H
    family = g.font or font
    tw, th, _ = fonts.block(g.text, family, True, g.size)
    fs = fonts.fs(family, True, g.size)
    pw, ph = tw + 0.9 * fs, th + 0.42 * fs
    lx = g.label_x * W if g.label_x is not None else tx
    ly = g.label_y * H if g.label_y is not None else (ty - 0.13 * H if ty > 0.32 * H else ty + 0.13 * H)
    lx = min(max(lx, pw / 2 + 0.04 * W), W - pw / 2 - 0.04 * W)
    ly = min(max(ly, 0.12 * H + ph / 2), 0.78 * H - ph / 2)

    events = []
    dark = bgr("#141414")
    events.append(_ev(2, g.start, g.end, "G", drawing(
        rf"\an5\pos({_f(tx)},{_f(ty)})\1c{bgr(g.accent_color)}\bord3\3c&HFFFFFF&\shad0{pop(0, 220)}{OUT}",
        circle_path(11))))
    events.append(_ev(2, g.start, min(g.start + 0.9, g.end), "G", drawing(
        rf"\an5\pos({_f(tx)},{_f(ty)})\1a&HFF&\bord3\3c{bgr(g.accent_color)}\shad0\fscx60\fscy60"
        r"\t(0,700,\fscx260\fscy260\3a&HFF&)", circle_path(14))))
    dx, dy = tx - lx, ty - ly
    if abs(dx) > pw / 2 or abs(dy) > ph / 2:  # line from the pill edge to the target
        scale = min(pw / 2 / abs(dx) if dx else math.inf, ph / 2 / abs(dy) if dy else math.inf)
        ex, ey = lx + dx * scale, ly + dy * scale
        x0, y0, x1, y1 = min(tx, ex) - 6, min(ty, ey) - 6, max(tx, ex) + 6, max(ty, ey) + 6
        grow = (rf"\clip({_f(tx - 3)},{_f(ty - 3)},{_f(tx + 3)},{_f(ty + 3)})"
                rf"\t(100,380,\clip({_f(x0)},{_f(y0)},{_f(x1)},{_f(y1)}))")
        events.append(_ev(2, g.start, g.end, "G", drawing(
            rf"\an7\pos(0,0)\1c{bgr(g.accent_color)}\bord1.5\3c{dark}\shad0{grow}{OUT}",
            line_path(tx, ty, ex, ey, 6))))
    label_events, _, _ = _label(g.text, lx, ly, g, fonts, font, g.start, g.end, delay=300)
    return events + label_events


def _badge(g: Graphic, W: int, H: int, fonts: FontBook, font: str) -> list[str]:
    family = g.font or font
    r = g.size * 0.85
    cx, cy = g.x * W, g.y * H
    events = []
    if g.label:
        tw, th, _ = fonts.block(g.label, family, True, g.size * 0.9)
        fs = fonts.fs(family, True, g.size * 0.9)
        pw, ph = tw + 0.9 * fs + r * 0.6, max(th + 0.42 * fs, r * 1.3)
        cx = min(cx, W - 0.04 * W - pw - r * 0.4)
        left = cx + r * 0.4
        lx = left + pw / 2
        reveal = (rf"\clip({_f(cx)},{_f(cy - ph)},{_f(cx + 1)},{_f(cy + ph)})"
                  rf"\t(180,480,\clip({_f(cx)},{_f(cy - ph)},{_f(left + pw + 8)},{_f(cy + ph)}))")
        events.append(_ev(2, g.start, g.end, "G", drawing(
            rf"\an5\pos({_f(lx)},{_f(cy)})\bord0\shad4\4c&H000000&\4a&HA0&\1c{bgr(g.color)}{reveal}{OUT}",
            round_rect_path(pw, ph, ph / 2))))
        events.append(_ev(3, g.start, g.end, "G",
                          rf"{{\an5\pos({_f(lx + r * 0.3)},{_f(cy)})\fn{fonts.name(family, True)}\fs{_f(fs)}\b1\bord0\shad0"
                          rf"\1c{bgr(g.text_color)}{reveal}{OUT}}}" + ass_text(g.label)))
    spin = (r"\frz-35\fscx0\fscy0\t(0,200,\frz8\fscx116\fscy116)\t(200,320,\frz0\fscx100\fscy100)" + OUT)
    events.append(_ev(4, g.start, g.end, "G", drawing(
        rf"\an5\pos({_f(cx)},{_f(cy)})\1c{bgr(g.accent_color)}\bord5\3c{bgr(g.color)}\shad3\4a&HA0&{spin}",
        circle_path(r))))
    fs = fonts.fs(family, True, g.size * 0.95)
    events.append(_ev(5, g.start, g.end, "G",
                      rf"{{\an5\pos({_f(cx)},{_f(cy)})\fn{fonts.name(family, True)}\fs{_f(fs)}\b1\bord0\shad0\1c{bgr(g.color)}{spin}}}"
                      + ass_text(g.text)))
    return events


def _progress(g: Graphic, W: int, H: int) -> list[str]:
    y0 = min(max(g.y * H, 0.0), H - g.thickness)
    y1 = y0 + g.thickness
    dur = ms(g.end - g.start)
    track = drawing(r"\an7\pos(0,0)\bord0\shad0\1c&HFFFFFF&\1a&HA0&", rect_path(0, y0, W, y1))
    fill = drawing(rf"\an7\pos(0,0)\bord0\shad0\1c{bgr(g.accent_color)}\clip(0,{_f(y0)},0,{_f(y1)})"
                   rf"\t(0,{dur},\clip(0,{_f(y0)},{W},{_f(y1)}))", rect_path(0, y0, W, y1))
    return [_ev(7, g.start, g.end, "G", track), _ev(8, g.start, g.end, "G", fill)]


def _highlight(g: Graphic, W: int, H: int) -> list[str]:
    R = g.radius * W
    pulses = "".join(rf"\t({450 + k * 1000},{950 + k * 1000},\fscx107\fscy107)\t({950 + k * 1000},{1450 + k * 1000},"
                     r"\fscx100\fscy100)" for k in range(max(0, int((g.end - g.start - 0.45) / 1.0))))
    tags = (rf"\an5\pos({_f(g.x * W)},{_f(g.y * H)})\1a&HFF&\bord7\3c{bgr(g.color)}\shad0\blur0.8"
            rf"\fscx160\fscy160\3a&HFF&\t(0,260,\fscx100\fscy100\3a&H00&){pulses}{OUT}")
    return [_ev(2, g.start, g.end, "G", drawing(tags, circle_path(R)))]


def _sparkles(g: Graphic, W: int, H: int) -> list[str]:
    cx, cy, R = g.x * W, g.y * H, g.radius * W
    events = []
    for i in range(g.count):
        ang = i * 2.39996  # golden angle spreads stars evenly
        rr = R * math.sqrt((i + 0.5) / g.count)
        px, py = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
        size = g.size * (0.35 + 0.3 * ((i * 37) % 10) / 10)
        t = g.start + (i * 0.137) % 0.6
        while t < g.end:
            end = min(t + 0.75, g.end)
            tags = (rf"\an5\pos({_f(px)},{_f(py)})\1c{bgr(g.color)}\bord2\3c{bgr(g.color)}\3a&H70&\blur2.5\shad0"
                    r"\fscx0\fscy0\frz0\t(0,260,\fscx100\fscy100\frz45)\t(260,700,\fscx0\fscy0\frz110)")
            events.append(_ev(6, t, end, "G", drawing(tags, star_path(size))))
            t += 1.05
    return events


def _flash(g: Graphic, W: int, H: int) -> list[str]:
    tags = rf"\an7\pos(0,0)\bord0\shad0\1c{bgr(g.color)}\alpha&H30&\t(0,{ms(g.end - g.start)},\alpha&HFF&)"
    return [_ev(9, g.start, g.end, "G", drawing(tags, rect_path(0, 0, W, H)))]


def graphic_events(graphics: list[Graphic], W: int, H: int, font: str, fonts: FontBook) -> list[str]:
    events: list[str] = []
    for g in graphics:
        if g.type == "callout":
            events += _callout(g, W, H, fonts, font)
        elif g.type == "badge":
            events += _badge(g, W, H, fonts, font)
        elif g.type == "progress_bar":
            events += _progress(g, W, H)
        elif g.type == "highlight":
            events += _highlight(g, W, H)
        elif g.type == "sparkles":
            events += _sparkles(g, W, H)
        elif g.type == "flash":
            events += _flash(g, W, H)
    return events


def check_fonts(plan: EditPlan, font: str, fonts_dir: Path | None = None) -> list[str]:
    """Problems a render would hide: unknown font families (libass silently swaps in another font) and
    characters the font lacks (emoji, symbols), which libass draws from a fallback font."""
    fonts = FontBook(fonts_dir)
    uses: list[tuple[str, str, bool, str]] = [
        (f"text #{i}", t.font or font, t.bold, t.text) for i, t in enumerate(plan.texts)]
    if plan.captions:
        uses += [(f"caption #{i}", plan.captions.font or font, plan.captions.style != "clean", s.text)
                 for i, s in enumerate(plan.captions.segments)]
    uses += [(f"graphic #{i}", g.font or font, True, g.text + g.label)
             for i, g in enumerate(plan.graphics) if g.text or g.label]
    if plan.hud:
        from .hud import HUD_FONT, REWARD_FONT, hud_texts

        hud_font = HUD_FONT if fonts.resolves(HUD_FONT) else font
        for i, item in enumerate(plan.hud):
            text = "".join(hud_texts(item))
            if not text:
                continue
            uses.append((f"hud #{i} ({item.type})", item.font or hud_font, True, text))
            if item.type in ("popup", "card") and not item.font and fonts.resolves(REWARD_FONT):
                uses.append((f"hud #{i} ({item.type})", REWARD_FONT, True, text))
    problems, unknown = [], set()
    for where, family, bold, text in uses:
        if family in unknown:
            continue
        if not fonts.resolves(family):
            unknown.add(family)
            problems.append(f"{where}: không có font '{family}' — libass sẽ âm thầm thay font khác "
                            f"(xem assets/fonts/README.md)")
            continue
        missing = fonts.missing_chars(text.replace("\\n", ""), family, bold)
        if missing:
            problems.append(f"{where}: font '{family}' thiếu ký tự {''.join(sorted(missing))!r} "
                            "(emoji/ký hiệu sẽ bị vẽ bằng font khác, đơn sắc) — bỏ đi hoặc đổi font")
    return problems


def build_ass(plan: EditPlan, font: str, fonts_dir: Path | None = None, *, fps: int | None = None,
              base_dir: Path | None = None, probe=None) -> str:
    """The overlay script. HUD items are evaluated per frame at `fps` (the render's frame rate); anchored ones
    need `base_dir` (where analysis/tracks/ lives) and `probe` (source video sizes)."""
    W, H = plan.canvas.width, plan.canvas.height
    fonts = FontBook(fonts_dir)
    styles = [style_line("G", font=font, size=60, primary=ass_color("#FFFFFF"), secondary=ass_color("#FFFFFF"),
                         outline_color=ass_color("#000000"), back=ass_color("#000000", 0.5), bold=True,
                         border_style=1, outline=0, shadow=0, align=5, margin_lr=0, margin_v=0)]
    events: list[str] = []
    text_styles, text_evs = text_events(plan.texts, W, H, font, fonts)
    styles += text_styles
    events += text_evs
    if plan.captions and plan.captions.segments:
        cap_styles, cap_evs = caption_events(plan.captions, W, H, font, fonts)
        styles += cap_styles
        events += cap_evs
    events += graphic_events(plan.graphics, W, H, font, fonts)
    if plan.hud:
        from .hud import hud_events
        from .world import World

        world = World(plan, base_dir, fps or plan.canvas.fps, probe)
        events += hud_events(plan, world, fonts, font)
    return "\n".join([
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2",
        "ScaledBorderAndShadow: yes", "YCbCr Matrix: TV.709", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding",
        *styles, "",
        "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        *events, "",
    ])
