import json
import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError

from vedit.ass import FontBook, build_ass, circle_path, round_rect_path
from vedit.edl import EditPlan
from vedit.media import probe
from vedit.render import build_command, motion_filter, render

FONTS = Path(__file__).resolve().parents[1] / "assets" / "fonts"


def creative_plan(**extra) -> dict:
    data = {
        "canvas": {"width": 360, "height": 640, "fps": 25},
        "clips": [{"source": "color:#335544", "duration": 2.0}],
        "look": {"preset": "warm_food", "vignette": 0.4, "grain": 0.3},
        "texts": [
            {"text": "Hook mạnh", "start": 0, "end": 1.5, "y": 0.2, "font": "Mali", "shape": "pill", "animation": "bounce"},
            {"text": "gõ từng chữ", "start": 0.2, "end": 1.8, "animation": "typewriter"},
            {"text": "bật từng từ", "start": 0.4, "end": 1.8, "position": "lower", "animation": "word_pop"},
            {"text": "băng rôn", "start": 0.6, "end": 1.9, "y": 0.7, "shape": "banner", "animation": "wipe"},
        ],
        "graphics": [
            {"type": "callout", "start": 0.1, "end": 1.9, "x": 0.4, "y": 0.6, "text": "ớt tươi"},
            {"type": "badge", "start": 0.2, "end": 1.9, "x": 0.15, "y": 0.15, "text": "1", "label": "Pha nước"},
            {"type": "progress_bar", "start": 0, "end": 2.0},
            {"type": "highlight", "start": 0.5, "end": 1.9, "x": 0.5, "y": 0.5},
            {"type": "sparkles", "start": 0.0, "end": 1.9, "x": 0.5, "y": 0.4, "count": 5},
            {"type": "flash", "start": 1.0, "end": 1.2},
        ],
        "motion": [{"type": "punch", "start": 0.2}, {"type": "shake", "start": 1.1, "amount": 0.01}],
        "audio": [{"path": f"sfx:{name}", "role": "sfx", "start": 0.1 * i, "volume": 0.3}
                  for i, name in enumerate(["pop", "click", "ding", "sparkle", "whoosh", "thud", "rise"])],
        "export": {"encoder_preset": "ultrafast", "normalize_audio": False},
    }
    data.update(extra)
    return data


def test_font_sizes_are_normalised_across_fonts():
    fonts = FontBook(FONTS)
    # Mali's win metrics are ~2.1 em tall vs ~1.5 em for Be Vietnam Pro: the same `size` must still
    # give text of similar width, and Be Vietnam Pro must resolve to the face name libass matches on
    widths = {f: fonts.width("Muối hũ cà pháo", f, True, 100) for f in ("Be Vietnam Pro", "Mali")}
    assert abs(widths["Mali"] - widths["Be Vietnam Pro"]) / widths["Mali"] < 0.15
    assert fonts.fs("Mali", True, 100) > fonts.fs("Be Vietnam Pro", True, 100) * 1.3
    assert fonts.name("Be Vietnam Pro", True) == "Be Vietnam Pro ExtraBold"
    assert fonts.name("Be Vietnam Pro", False) == "Be Vietnam Pro SemiBold"


def test_paths_are_closed_shapes():
    assert round_rect_path(100, 40, 20).startswith("m 20 0 l 80 0 b")
    assert circle_path(10).count(" b ") == 4 and circle_path(10).startswith("m 20 10 b")


def test_build_ass_has_every_graphic_and_animation():
    plan = EditPlan.model_validate(creative_plan())
    ass = build_ass(plan, "Inter", FONTS)
    dialogue = [line for line in ass.splitlines() if line.startswith("Dialogue")]
    assert any(r"\p1" in d for d in dialogue)                        # vector drawings
    assert ass.count(r"\t(0,1,\alpha&H00&)") == 1                     # typewriter: first character
    assert ass.count(r"\fscy40") == 3                                 # word_pop: one per word
    assert r"\clip(0," in ass and r"\t(0,2000,\clip(0," in ass       # progress bar grows over 2s
    assert "Style: T0,Mali," in ass                                   # pill text uses the requested font
    assert r"\frz-2" in ass                                           # banners tilt by default
    assert sum(r"\alpha&H30&" in d for d in dialogue) == 1            # one flash


def test_motion_filter_expressions():
    plan = EditPlan.model_validate(creative_plan())
    expr = motion_filter(plan, 25, 360, 640)
    assert expr.startswith("zoompan=z='1+0.08*if(between(on,5,13)") and "sin((on-28)*2.4)" in expr
    assert motion_filter(EditPlan.model_validate(creative_plan(motion=[])), 25, 360, 640) is None


def test_graph_contains_look_motion_and_sfx(tmp_path):
    plan = EditPlan.model_validate(creative_plan())
    cmd = build_command(plan, tmp_path / "o.mp4", base_dir=tmp_path, work_dir=tmp_path / "w", fonts_dir=FONTS)
    graph = cmd[cmd.index("-filter_complex") + 1]
    assert "colorbalance=" in graph and "vignette=" in graph and "noise=" in graph and "zoompan=z='1+" in graph
    assert graph.count("aevalsrc=") == 6 and "anoisesrc=" in graph
    assert f"fontsdir={FONTS}" in graph


@pytest.mark.parametrize("bad, message", [
    ({"graphics": [{"type": "callout", "start": 0, "end": 1}]}, "cần 'text'"),
    ({"graphics": [{"type": "flash", "start": 1, "end": 0.5}]}, "end phải lớn hơn start"),
    ({"audio": [{"path": "sfx:boom"}]}, "không có"),
    ({"texts": [{"text": "x", "start": 0, "end": 1, "animation": "spin"}]}, "animation"),
])
def test_creative_validation(bad, message):
    with pytest.raises(ValidationError, match=message):
        EditPlan.model_validate(creative_plan(**bad))


def test_render_creative_plan(tmp_path):
    plan = EditPlan.model_validate(creative_plan())
    result = render(plan, tmp_path / "fx.mp4", base_dir=tmp_path, font="Inter", fonts_dir=FONTS)
    info = probe(result.output)
    assert (info.width, info.height) == (360, 640) and info.has_audio
    assert info.duration == pytest.approx(2.0, abs=0.05)
    # the synthesised sound effects are actually audible
    out = subprocess.run(["ffmpeg", "-i", str(result.output), "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    peak = float(out.split("max_volume: ")[1].split(" dB")[0])
    assert peak > -30
    assert json.loads(json.dumps(plan.model_dump()))["graphics"][0]["type"] == "callout"
