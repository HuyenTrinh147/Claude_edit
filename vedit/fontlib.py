"""Font tooling for the font agent: Vietnamese coverage check, install from a folder / zip / URL, specimen sheet.

No AI. A font is usable for Vietnamese video text only when it has every precomposed Vietnamese letter (a font that lacks
a few of them silently falls back to another font for those glyphs, which looks broken). `check` reports exactly which
are missing. `add` copies static fonts into ``assets/fonts`` and cuts variable fonts into static Regular / Bold files,
because libass picks the wrong weight from a variable font.
"""

from __future__ import annotations

import io
import re
import shutil
import tempfile
import unicodedata
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from fontTools.ttLib import TTFont

FONT_EXTS = {".ttf", ".otf"}
# every precomposed Vietnamese letter (lower + upper), plus the two letters that only exist in Vietnamese orthography
_BASES = "aăâeêioôơuưyAĂÂEÊIOÔƠUƯY"
_MARKS = ("̀", "́", "̃", "̉", "̣")
VIET_CHARS = sorted({unicodedata.normalize("NFC", b + m) for b in _BASES for m in _MARKS} | set("đĐăĂâÂêÊôÔơƠưƯ"))
PANGRAM = "Tôi yêu Việt Nam: ăn bánh mì, uống cà phê sữa đá ở phố cổ Hà Nội"


@dataclass
class FontReport:
    path: str
    family: str
    style: str
    variable: bool
    missing: list[str] = field(default_factory=list)
    license: str = ""

    @property
    def vietnamese_ok(self) -> bool:
        return not self.missing

    @property
    def coverage(self) -> float:
        return 1 - len(self.missing) / len(VIET_CHARS)


def _name(font: TTFont, ids: tuple[int, ...]) -> str:
    for i in ids:
        rec = font["name"].getName(i, 3, 1, 0x409) or font["name"].getName(i, 1, 0, 0)
        if rec is not None:
            try:
                return rec.toUnicode().strip()
            except UnicodeDecodeError:
                continue
    return ""


def check(path: Path) -> FontReport:
    font = TTFont(str(path), lazy=True)
    cmap = font.getBestCmap() or {}
    missing = [c for c in VIET_CHARS if ord(c) not in cmap]
    lic = _name(font, (14,)) or _name(font, (13,))
    return FontReport(path=str(path), family=_name(font, (16, 1)), style=_name(font, (17, 2)), variable="fvar" in font,
                      missing=missing, license=re.sub(r"\s+", " ", lic)[:160])


def list_fonts(fonts_dir: Path) -> list[FontReport]:
    return [check(p) for p in sorted(Path(fonts_dir).glob("*")) if p.suffix.lower() in FONT_EXTS]


def _static_instances(path: Path, out_dir: Path) -> list[Path]:
    """Variable font -> static Regular (400) and Bold (700), renamed so libass can address them."""
    from fontTools.varLib import instancer

    made = []
    for weight, style in ((400, "Regular"), (700, "Bold")):
        font = TTFont(str(path))
        axes = {a.axisTag: a for a in font["fvar"].axes}
        loc = {"wght": min(max(weight, axes["wght"].minValue), axes["wght"].maxValue)} if "wght" in axes else {}
        for tag, a in axes.items():
            if tag != "wght":
                loc[tag] = a.defaultValue
        inst = instancer.instantiateVariableFont(font, loc)
        family = _name(inst, (16, 1)) or path.stem
        family = re.sub(r"\s+(Thin|Light|Regular|Medium|SemiBold|Bold|ExtraBold|Black)$", "", family)
        for rec in inst["name"].names:
            if rec.nameID in (1, 16, 21, 25):
                rec.string = family
            elif rec.nameID in (2, 17, 22):
                rec.string = style
            elif rec.nameID == 4:
                rec.string = f"{family} {style}"
            elif rec.nameID == 6:
                rec.string = f"{family}-{style}".replace(" ", "")
        inst["OS/2"].usWeightClass = weight
        target = out_dir / f"{family.replace(' ', '')}-{style}.ttf"
        inst.save(str(target))
        made.append(target)
    return made


def _collect(source: str, work: Path) -> list[Path]:
    """Font files (and licence files) from a folder, a .zip, a .ttf/.otf file or an http(s) URL of one of those."""
    if re.match(r"^https?://", source):
        name = source.split("?")[0].rstrip("/").split("/")[-1] or "download"
        target = work / name
        req = urllib.request.Request(source, headers={"User-Agent": "vedit-fonts"})
        with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310 - the user chose this URL
            target.write_bytes(r.read())
        source = str(target)
    p = Path(source).expanduser()
    if p.is_dir():
        return [f for f in p.rglob("*") if f.is_file()]
    if p.suffix.lower() == ".zip":
        with zipfile.ZipFile(p) as z:
            z.extractall(work / "unz")   # zipfile refuses absolute / parent paths on extract
        return [f for f in (work / "unz").rglob("*") if f.is_file()]
    if p.suffix.lower() in FONT_EXTS:
        return [p]
    raise ValueError(f"Không nhận ra nguồn font: {source} (cần thư mục, .zip, .ttf/.otf hoặc URL của chúng)")


def add(source: str, fonts_dir: Path, *, require_vietnamese: bool = True) -> list[tuple[FontReport, Path | None, str]]:
    """Install fonts from `source` into `fonts_dir`. Returns (report, installed path or None, reason) per font file."""
    fonts_dir = Path(fonts_dir)
    fonts_dir.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        files = _collect(source, Path(tmp))
        fonts = [f for f in files if f.suffix.lower() in FONT_EXTS]
        licences = [f for f in files if re.search(r"(OFL|LICEN[CS]E)", f.name, re.I) and f.suffix.lower() in (".txt", "")]
        if not fonts:
            raise ValueError("Không thấy file .ttf / .otf trong nguồn này")
        for f in fonts:
            rep = check(f)
            if require_vietnamese and not rep.vietnamese_ok:
                results.append((rep, None, f"thiếu {len(rep.missing)} ký tự tiếng Việt (ví dụ {''.join(rep.missing[:6])})"))
                continue
            if rep.variable:
                made = _static_instances(f, fonts_dir)
                results.append((rep, made[0], "font biến thiên: đã cắt bản Regular 400 và Bold 700"))
            else:
                target = fonts_dir / f.name
                shutil.copyfile(f, target)
                results.append((rep, target, "đã chép"))
        if licences and any(p for _, p, _ in results):
            fam = next((r.family for r, p, _ in results if p), "font").replace(" ", "")
            shutil.copyfile(licences[0], fonts_dir / f"LICENSE-{fam}.txt")
    return results


def specimen(families: list[str], fonts_dir: Path, out: Path, *, text: str = PANGRAM, bg: str = "#FFF4D6",
             color: str = "#3B2A6B", size: int = 54) -> Path:
    """One labelled row per family on the given background / text colour: a quick way to compare fonts for a vibe."""
    from PIL import Image, ImageDraw, ImageFont

    fonts_dir = Path(fonts_dir)
    by_family: dict[str, Path] = {}
    for rep in list_fonts(fonts_dir):
        by_family.setdefault(rep.family.lower(), Path(rep.path))
    label_font = ImageFont.truetype(str(next(iter(by_family.values()))), 20)
    rows = []
    for fam in families:
        path = by_family.get(fam.lower())
        if path is None:
            raise ValueError(f"Chưa có font '{fam}' trong {fonts_dir} (vedit fonts list)")
        rows.append((fam, ImageFont.truetype(str(path), size)))
    width, row_h = 1400, size * 2 + 20
    img = Image.new("RGB", (width, row_h * len(rows) + 20), bg)
    d = ImageDraw.Draw(img)
    for i, (fam, f) in enumerate(rows):
        y = 10 + i * row_h
        d.text((20, y), fam, fill=color, font=label_font)
        d.text((20, y + 28), text, fill=color, font=f)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=90)
    return out
