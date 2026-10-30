from pathlib import Path

import pytest
from pydantic import ValidationError

from vedit.edl import EditPlan, validate_against_media
from vedit.media import MediaInfo


def plan(**overrides) -> EditPlan:
    data = {
        "clips": [
            {"source": "main", "start": 0, "end": 4},
            {"source": "main", "start": 10, "end": 12, "speed": 2, "transition": {"type": "fade", "duration": 0.5}},
            {"source": "color:#112233", "duration": 1.5},
        ],
    }
    data.update(overrides)
    return EditPlan.model_validate(data)


def test_timeline_with_speed_and_transition():
    p = plan()
    # clip1 lasts 2s/2 = 1s and overlaps clip0 by 0.5s
    assert p.clip_offsets() == [0.0, 3.5, 4.5]
    assert p.duration == pytest.approx(6.0)


@pytest.mark.parametrize("bad, message", [
    ({"clips": [{"source": "main", "start": 3, "end": 2}]}, "end"),
    ({"clips": [{"source": "main", "start": 0}]}, "end"),
    ({"clips": [{"source": "main", "end": 2, "transition": {"type": "fade"}}]}, "clip đầu tiên"),
    ({"clips": [{"source": "main", "end": 2}, {"source": "main", "end": 0.3, "transition": {"duration": 0.5}}]},
     "transition"),
    ({"clips": [{"source": "main", "end": 2}], "canvas": {"width": 1081}}, "chẵn"),
    ({"clips": [{"source": "main", "end": 2}], "texts": [{"text": "x", "start": 2, "end": 1}]}, "end"),
    ({"clips": [{"source": "main", "end": 2, "fit": "stretch"}]}, "fit"),
    ({"clips": [{"source": "main", "end": 2}], "unknown_field": 1}, "unknown_field"),
])
def test_validation_errors(bad, message):
    with pytest.raises(ValidationError, match=message):
        EditPlan.model_validate(bad)


def test_resolve_and_roundtrip(tmp_path: Path):
    p = plan(sources={"main": "input/video.mp4", "abs": "/data/x.mp4"})
    assert p.resolve("main", tmp_path) == tmp_path / "input/video.mp4"
    assert p.resolve("abs", tmp_path) == Path("/data/x.mp4")
    assert p.resolve("other.mov", tmp_path) == tmp_path / "other.mov"
    p.save(tmp_path / "plan.json")
    assert EditPlan.load(tmp_path / "plan.json") == p


def test_validate_against_media(tmp_path: Path):
    (tmp_path / "v.mp4").write_bytes(b"")

    def fake_probe(path):
        return MediaInfo(str(path), 10.0, 640, 360, 25, True, True, False, "h264", "aac", 1)

    p = EditPlan.model_validate({
        "sources": {"main": "v.mp4"},
        "clips": [{"source": "main", "start": 5, "end": 12}, {"source": "missing.mp4", "end": 1},
                  {"source": "color:red", "duration": 1}],
        "texts": [{"text": "late", "start": 100, "end": 101}],
    })
    problems = validate_against_media(p, tmp_path, fake_probe)
    assert any("vượt quá độ dài nguồn" in x for x in problems)
    assert any("không tìm thấy" in x for x in problems)
    assert any("color:#RRGGBB" in x for x in problems)
    assert any("text #0" in x for x in problems)
