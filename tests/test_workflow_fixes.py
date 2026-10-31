"""Approval-gate workflow and the round-1 fixes from Agent 1's research."""

import json
import unicodedata
from pathlib import Path

import pytest

from vedit.agents.scriptwriter import Concept, ConceptSet, concepts_markdown
from vedit.ass import build_ass, check_fonts
from vedit.edl import EditPlan
from vedit.media import MediaInfo, contact_sheet, probe
from vedit.pipeline import choose_concept
from vedit.project import Project
from vedit.render import render

FONTS = Path(__file__).resolve().parents[1] / "assets" / "fonts"


def concept(name: str) -> dict:
    return {"name": name, "idea": "ý tưởng", "style": "silent vlog", "hook": "hũ thành phẩm",
            "beats": ["20.5-21.6s hook", "0.4-2.0s rót nước"], "pacing": "chậm, có cảnh thở",
            "typography": "Mali, kem", "signature_moves": ["speed ramp", "freeze frame"], "audio": "tiếng gốc",
            "color": "warm", "duration": 15, "why": "hợp ASMR"}


def test_text_is_normalised_to_nfc():
    nfd = unicodedata.normalize("NFD", "Muối hũ cà pháo")
    plan = EditPlan.model_validate({
        "clips": [{"source": "color:#000000", "duration": 1}],
        "texts": [{"text": nfd, "start": 0, "end": 1}],
        "graphics": [{"type": "callout", "start": 0, "end": 1, "text": nfd}],
    })
    assert plan.texts[0].text == plan.graphics[0].text == unicodedata.normalize("NFC", nfd)


def test_check_fonts_reports_unknown_family_and_missing_glyphs():
    plan = EditPlan.model_validate({
        "clips": [{"source": "color:#000000", "duration": 1}],
        "texts": [{"text": "Ngon 🥒", "start": 0, "end": 1, "font": "Mali"},
                  {"text": "x", "start": 0, "end": 1, "font": "Không Có Font Này"},
                  {"text": "Ổn định ỆỮỢẪ", "start": 0, "end": 1, "font": "Be Vietnam Pro"}],
    })
    problems = check_fonts(plan, "Be Vietnam Pro", FONTS)
    assert len(problems) == 2
    assert "thiếu ký tự '🥒'" in problems[0] and "không có font 'Không Có Font Này'" in problems[1]


def test_text_box_and_caption_wrapping():
    plan = EditPlan.model_validate({
        "clips": [{"source": "color:#000000", "duration": 2}],
        "texts": [{"text": "Hộp nền", "start": 0, "end": 1, "box": True, "box_color": "#112233", "box_opacity": 0.5}],
        "captions": {"style": "karaoke", "segments": [{"start": 0, "end": 2, "text": "một câu khá dài " * 5}]},
    })
    ass = build_ass(plan, "Be Vietnam Pro", FONTS)
    style = next(line for line in ass.splitlines() if line.startswith("Style: T0,"))
    assert ",3," in style and "&H80332211" in style  # BorderStyle 3 box in the box colour
    caps = [line for line in ass.splitlines() if ",Cap," in line]
    assert caps and all(r"{\q0}" in line or r"{\q0\\" in line for line in caps)


def test_silent_timeline_renders_with_loudnorm_on(tmp_path):
    plan = EditPlan.model_validate({"canvas": {"width": 180, "height": 320},
                                    "clips": [{"source": "color:#204060", "duration": 1}],
                                    "export": {"encoder_preset": "ultrafast", "normalize_audio": True}})
    result = render(plan, tmp_path / "silent.mp4", base_dir=tmp_path)
    assert probe(result.output).duration == pytest.approx(1.0, abs=0.05)


def test_render_keeps_history_and_plan_snapshot(tmp_path):
    plan = EditPlan.model_validate({"canvas": {"width": 180, "height": 320},
                                    "clips": [{"source": "color:#204060", "duration": 0.5}],
                                    "export": {"encoder_preset": "ultrafast", "normalize_audio": False}})
    out = tmp_path / "renders" / "final.mp4"
    render(plan, out, base_dir=tmp_path)
    render(plan, out, base_dir=tmp_path)
    history = sorted(p.name for p in (out.parent / "history").iterdir())
    assert any(n.endswith(".mp4") for n in history) and any(n.endswith(".plan.json") for n in history)
    assert json.loads(out.with_suffix(".plan.json").read_text(encoding="utf-8"))["clips"][0]["duration"] == 0.5
    assert not list(out.parent.glob(".final.rendering*"))


def test_hdr_detection():
    base = dict(path="x", duration=1, width=1, height=1, fps=30, has_video=True, has_audio=False, is_image=False,
                video_codec="hevc", audio_codec=None, size_bytes=1)
    assert MediaInfo(**base, color_transfer="arib-std-b67").is_hdr
    assert not MediaInfo(**base, color_transfer="bt709").is_hdr


def test_contact_sheet(media, tmp_path):
    out, times = contact_sheet(media["land"], tmp_path / "sheet.jpg", start=1, end=3, count=6, cols=3, width=160)
    assert out.exists() and len(times) == 6 and 1 < times[0] < times[-1] < 3
    assert probe(out).width == 160 * 3 + 4 * 2


def test_concept_gate_records_choice(media, settings):
    project = Project.create(settings, media["land"], "gate")
    assert project.memory_path.exists()
    cs = ConceptSet.model_validate({"understanding": "video muối cà", "concepts": [concept("A"), concept("Game AR")]})
    project.script_dir.mkdir(parents=True, exist_ok=True)
    (project.script_dir / "concepts.json").write_text(cs.model_dump_json(), encoding="utf-8")
    md = concepts_markdown(cs, project)
    assert "## 2. Game AR" in md and "**Chiêu chữ ký:** speed ramp · freeze frame" in md
    chosen, notes = choose_concept(project, 2, "thêm điểm XP")
    assert isinstance(chosen, Concept) and chosen.name == "Game AR" and notes == "thêm điểm XP"
    assert "chọn hướng 2 — Game AR; ghi chú: thêm điểm XP" in project.memory_path.read_text(encoding="utf-8")
    with pytest.raises(SystemExit):
        choose_concept(project, 5)
