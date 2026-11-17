"""vedit bpm (tempo estimate on a synthetic click track) and vedit textcheck (hard text rules)."""
import wave

import numpy as np
import pytest

from vedit.beat import analyze_music, list_music
from vedit.edl import EditPlan
from vedit.textcheck import check_plan


def click_track(path, bpm=120.0, seconds=16.0, offset=0.25, sr=22050):
    n = int(seconds * sr)
    x = np.zeros(n)
    period = 60.0 / bpm
    t = offset
    burst = np.sin(2 * np.pi * 1500 * np.arange(int(0.03 * sr)) / sr) * np.exp(-np.arange(int(0.03 * sr)) / (0.008 * sr))
    while t < seconds - 0.05:
        i = int(t * sr)
        x[i:i + len(burst)] += burst
        t += period
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((np.clip(x, -1, 1) * 30000).astype("<i2").tobytes())


@pytest.mark.parametrize("bpm", [100.0, 128.0])
def test_bpm_and_first_beat_on_click_track(tmp_path, bpm):
    path = tmp_path / "clicks.wav"
    click_track(path, bpm=bpm, offset=0.25)
    info = analyze_music(path)
    assert info.bpm == pytest.approx(bpm, abs=3)
    period = 60.0 / bpm
    assert abs(((info.first_beat - 0.25 + period / 2) % period) - period / 2) < 0.06   # beat grid phase
    assert info.duration == pytest.approx(16.0, abs=0.2) and info.confidence > 0.3


def test_list_music_filters_audio(tmp_path):
    (tmp_path / "a.mp3").write_bytes(b"x")
    (tmp_path / "notes.txt").write_text("x")
    assert [p.name for p in list_music(tmp_path)] == ["a.mp3"]


def plan(texts, **canvas):
    base = {"sources": {"a": "a.mp4"}, "clips": [{"source": "a", "start": 0, "end": 10}],
            "canvas": {"safe_area": [0.05, 0.1, 0.85, 0.8], **canvas}, "texts": texts}
    return EditPlan.model_validate(base)


def rules(report):
    return sorted({(f.rule, f.level) for f in report.findings})


def test_clean_text_passes():
    r = check_plan(plan([{"text": "1/6 THÁI", "start": 1, "end": 2.5, "y": 0.3}]))
    assert r.checked == 1 and not r.findings


def test_too_short_reading_time_is_error():
    r = check_plan(plan([{"text": "Canh chua cá nấu sáu bước", "start": 1, "end": 2, "y": 0.3}]))
    assert ("thoi-gian-doc", "error") in rules(r)


def test_safe_area_and_lines_and_syllables():
    r = check_plan(plan([
        {"text": "UNBOX!", "start": 0, "end": 2, "y": 0.05},
        {"text": "một\nhai\nba", "start": 3, "end": 6, "y": 0.4},
        {"text": "một hai ba bốn năm sáu bảy tám chín mười", "start": 6, "end": 9, "y": 0.4},
    ]))
    got = rules(r)
    assert ("vung-an-toan", "error") in got and ("so-dong", "error") in got and ("dong-dai", "warn") in got


def test_overlap_and_missing_diacritics_warn():
    r = check_plan(plan([
        {"text": "mot cau dai khong dau", "start": 0, "end": 3, "y": 0.3},
        {"text": "CHONG", "start": 1, "end": 3, "y": 0.31},
    ]))
    got = rules(r)
    assert ("chong-chu", "warn") in got and ("thieu-dau", "warn") in got
    assert r.errors == 0


# ---- music styles + library index -------------------------------------------------------------------------

@pytest.mark.parametrize("style,bpm", [("pastel", 108.0), ("beat", 120.0), ("lofi", 84.0)])
def test_music_styles_are_deterministic_and_have_the_expected_tempo(tmp_path, style, bpm):
    from vedit.musicgen import make_bed, render_bed

    a, b = render_bed(20.0, style, seed=5), render_bed(20.0, style, seed=5)
    assert a.shape == (2, 20 * 48000) and np.array_equal(a, b) and not np.array_equal(a, render_bed(20.0, style, seed=6))
    path = make_bed(tmp_path / f"{style}.wav", 20.0, style, seed=5)
    assert analyze_music(path).bpm == pytest.approx(bpm, abs=3)      # the bed is a whole number of bars at this BPM


def test_music_catalog_covers_every_style():
    from vedit.musicgen import CATALOG, STYLES

    assert set(CATALOG) == set(STYLES)


def test_library_index_keeps_hand_written_tags(tmp_path):
    import json

    from vedit.beat import write_library_index

    row = {"path": str(tmp_path / "a.mp3"), "duration": 30.0, "bpm": 100.0, "confidence": 0.6, "first_beat": 0.1,
           "best_window_start": 2.0, "mean_db": -20.0, "peak_db": -1.0}
    index = tmp_path / "library.json"
    write_library_index(index, [row], tmp_path)
    data = json.loads(index.read_text(encoding="utf-8"))
    data["tracks"][0].update(mood="vui", tags=["food"], note="hợp hook")
    index.write_text(json.dumps(data), encoding="utf-8")
    write_library_index(index, [{**row, "bpm": 101.0}], tmp_path)   # re-run after the analysis changed
    track = json.loads(index.read_text(encoding="utf-8"))["tracks"][0]
    assert (track["file"], track["bpm"], track["mood"], track["tags"], track["note"]) == ("a.mp3", 101.0, "vui", ["food"], "hợp hook")


# ---- text style library -----------------------------------------------------------------------------------

def test_every_text_style_is_a_valid_overlay_with_installed_fonts():
    from pathlib import Path

    from vedit.ass import check_fonts
    from vedit.textstyles import STYLES

    texts = [{"text": s.sample, "start": 0, "end": 3, "style": s.name} for s in STYLES.values()]
    p = plan(texts)
    assert [t.style for t in p.texts] == list(STYLES) and all(t.font for t in p.texts)
    assert check_fonts(p, "Inter", Path("assets/fonts")) == []


def test_explicit_fields_win_over_the_style_and_unknown_style_is_rejected():
    from pydantic import ValidationError

    p = plan([{"text": "1. Xắt", "start": 0, "end": 3, "style": "nhan-so-vang", "size": 60, "color": "#FF0000"}])
    t = p.texts[0]
    assert (t.size, t.color, t.font) == (60, "#FF0000", "Baloo 2")
    with pytest.raises(ValidationError):
        plan([{"text": "x", "start": 0, "end": 3, "style": "khong-co"}])


def test_vlog_styles_have_no_background_plate_and_shadow_reaches_the_ass_style():
    from pathlib import Path

    from vedit.ass import build_ass
    from vedit.textstyles import STYLES

    vlog = [s for s in STYLES.values() if s.name.startswith("vlog-")]
    assert len(vlog) >= 8
    for s in vlog:   # the user finds text plates "quê": the vlog set must rely on outline + shadow only
        assert s.fields.get("shape", "none") == "none" and not s.fields.get("box") and s.fields["outline"] >= 4
    p = plan([{"text": "BÁNH MÌ QUE", "start": 0, "end": 3, "style": "vlog-tu-khoa-bong-bay"}])
    ass = build_ass(p, "Inter", Path("assets/fonts"), fps=30)
    style = next(line for line in ass.splitlines() if line.startswith("Style: T0,"))
    assert "Cherry Bomb One" in style and "&H001E34E0" in style        # opaque shadow colour #E0341E as BGR
    assert style.split(",")[17] == "9"                                   # shadow depth
