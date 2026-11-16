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
