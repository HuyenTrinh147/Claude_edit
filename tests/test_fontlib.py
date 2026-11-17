"""vedit fonts: Vietnamese coverage check, install from folder / zip, specimen."""
import shutil
import zipfile
from pathlib import Path

import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from vedit import fontlib

FONTS = Path("assets/fonts")


def tiny_font(path: Path, chars: str, family="Tiny Test") -> Path:
    """A valid TTF with empty glyphs for exactly `chars` (enough for cmap-based coverage checks)."""
    names = [".notdef"] + [f"g{ord(c):04x}" for c in chars]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap({ord(c): f"g{ord(c):04x}" for c in chars})
    pen = TTGlyphPen(None)
    fb.setupGlyf({n: pen.glyph() for n in names})
    fb.setupHorizontalMetrics({n: (500, 0) for n in names})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({"familyName": family, "styleName": "Regular"})
    fb.setupOS2(sTypoAscender=800, usWinAscent=800, usWinDescent=200)
    fb.setupPost()
    fb.save(str(path))
    return path


def test_vietnamese_char_set_is_complete():
    assert len(fontlib.VIET_CHARS) >= 130 and "ệ" in fontlib.VIET_CHARS and "Ữ" in fontlib.VIET_CHARS and "đ" in fontlib.VIET_CHARS


def test_installed_fonts_cover_vietnamese():
    assert fontlib.check(FONTS / "BeVietnamPro-SemiBold.ttf").vietnamese_ok
    assert all(r.vietnamese_ok for r in fontlib.list_fonts(FONTS))   # the library only ever holds Vietnamese-ready fonts


def test_check_reports_missing_letters(tmp_path):
    rep = fontlib.check(tiny_font(tmp_path / "ascii.ttf", "abcdefghijklmnopqrstuvwxyz"))
    assert not rep.vietnamese_ok and "ệ" in rep.missing and rep.coverage < 0.5


def test_add_installs_good_fonts_and_rejects_incomplete_ones(tmp_path):
    src = tmp_path / "pack"
    src.mkdir()
    shutil.copyfile(FONTS / "Baloo2-ExtraBold.ttf", src / "Baloo2-ExtraBold.ttf")
    tiny_font(src / "ascii.ttf", "abc")
    (src / "OFL.txt").write_text("SIL OPEN FONT LICENSE", encoding="utf-8")
    dest = tmp_path / "fonts"
    out = fontlib.add(str(src), dest)
    done = {rep.family: path for rep, path, _ in out}
    assert done["Baloo 2"] is not None and (dest / "Baloo2-ExtraBold.ttf").exists()
    assert done["Tiny Test"] is None and not (dest / "ascii.ttf").exists()
    assert list(dest.glob("LICENSE-*.txt"))                       # the licence travels with the font
    assert fontlib.add(str(src), dest, require_vietnamese=False)[1][1] is not None   # --allow-missing installs it anyway


def test_add_from_zip(tmp_path):
    z = tmp_path / "pack.zip"
    with zipfile.ZipFile(z, "w") as f:
        f.write(FONTS / "Mali-Bold.ttf", "fonts/Mali-Bold.ttf")
    out = fontlib.add(str(z), tmp_path / "fonts")
    assert out[0][1] is not None and out[0][1].name == "Mali-Bold.ttf"


def test_add_rejects_unknown_source(tmp_path):
    with pytest.raises(ValueError):
        fontlib.add(str(tmp_path / "nothing.txt"), tmp_path / "fonts")


def test_specimen_renders_every_requested_family(tmp_path):
    out = fontlib.specimen(["Baloo 2", "Pacifico"], FONTS, tmp_path / "s.jpg", bg="#FFD9E8", color="#4E3A68")
    from PIL import Image

    assert Image.open(out).size[1] > 200
    with pytest.raises(ValueError):
        fontlib.specimen(["Không Có Font Này"], FONTS, tmp_path / "x.jpg")
