import json

import pytest

from vedit.media import MediaError, analyze_video, detect_scenes, detect_silences, load_srt, probe


def test_probe(media):
    info = probe(media["land"])
    assert (info.width, info.height, info.orientation) == (640, 360, "landscape")
    assert info.duration == pytest.approx(6, abs=0.1)
    assert info.has_audio and not info.is_image
    port = probe(media["port"])
    assert port.orientation == "portrait" and not port.has_audio
    assert probe(media["logo"]).is_image
    with pytest.raises(MediaError):
        probe(media["land"].parent / "nope.mp4")


def test_scenes_and_silences(media):
    scenes = detect_scenes(media["land"])
    assert len(scenes) == 3
    assert scenes[1][0] == pytest.approx(2, abs=0.1)
    silences = detect_silences(media["land"], min_silence=0.5)
    assert len(silences) == 1
    assert silences[0][0] == pytest.approx(2.5, abs=0.15)


def test_load_srt(media):
    segs = load_srt(media["srt"])
    assert segs == [{"start": 0.2, "end": 1.8, "text": "Xin chào các bạn"},
                    {"start": 4.0, "end": 5.5, "text": "Đồ uống rất ngon"}]


def test_analyze_video(media, tmp_path):
    analysis = analyze_video(media["land"], tmp_path, transcript_file=media["srt"], log=lambda *_: None)
    saved = json.loads((tmp_path / "analysis.json").read_text(encoding="utf-8"))
    assert saved["media"]["duration"] == analysis["media"]["duration"]
    assert len(saved["scenes"]) == 3
    assert saved["transcript"][0]["text"] == "Xin chào các bạn"
    assert len(saved["frames"]) >= 3
    assert all((tmp_path / f["file"]).exists() for f in saved["frames"])
