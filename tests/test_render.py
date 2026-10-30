import re

import pytest

from vedit.edl import EditPlan
from vedit.media import probe
from vedit.render import _ass_color, _ass_text, _ass_time, build_ass, build_command, render


def test_ass_helpers():
    assert _ass_color("#FF8800") == "&H000088FF"
    assert _ass_color("#000000", 0.6) == "&H66000000"
    assert _ass_time(3723.456) == "1:02:03.46"
    assert _ass_text("Dòng 1\nDòng {2}") == r"Dòng 1\NDòng (2)"


def test_build_ass_karaoke_and_overlays():
    p = EditPlan.model_validate({
        "clips": [{"source": "color:#000000", "duration": 4}],
        "texts": [{"text": "Hook mạnh", "start": 0, "end": 2, "position": "upper", "animation": "slide_up"}],
        "captions": {"style": "karaoke", "segments": [{"start": 1, "end": 2, "text": "một hai ba"}]},
    })
    ass = build_ass(p, "Inter")
    assert "PlayResX: 1080" in ass and "PlayResY: 1920" in ass
    assert "Style: T0,Inter,80" in ass and "Style: Cap,Inter" in ass
    assert r"\move(" in ass and "Hook mạnh" in ass
    karaoke = [line for line in ass.splitlines() if line.startswith("Dialogue: 0")]
    assert len(karaoke) == 3  # one event per word, current word highlighted
    assert all(r"\c&H0000E6FF" in line for line in karaoke)


def _full_plan(media) -> EditPlan:
    return EditPlan.model_validate({
        "sources": {"main": str(media["land"]), "port": str(media["port"])},
        "canvas": {"width": 360, "height": 640, "fps": 25},
        "clips": [
            {"source": "color:#1A1A2E", "duration": 0.8},
            {"source": "main", "start": 0.2, "end": 1.8, "fit": "blur", "transition": {"type": "fade", "duration": 0.3}},
            {"source": "main", "start": 2.2, "end": 3.4, "speed": 1.5, "zoom": "in", "focus_x": 0.3},
            {"source": "port", "start": 0, "end": 1.2, "fit": "contain", "transition": {"type": "slideleft",
                                                                                    "duration": 0.3}},
            {"source": str(media["logo"]), "duration": 0.6},
        ],
        "texts": [{"text": "Bí quyết dựng video", "start": 0, "end": 1.5, "size": 40, "box": True}],
        "captions": {"style": "bold_pop", "segments": [{"start": 1.0, "end": 2.0, "text": "xin chào"}]},
        "images": [{"path": str(media["logo"]), "x": 0.85, "y": 0.1, "width": 0.15}],
        "audio": [{"path": str(media["music"]), "volume": 0.3, "loop": True}],
        "export": {"filename": "out.mp4", "encoder_preset": "ultrafast", "thumbnail_at": 1.0},
    })


def test_build_command_graph(media, tmp_path):
    p = _full_plan(media)
    cmd = build_command(p, tmp_path / "o.mp4", base_dir=tmp_path, work_dir=tmp_path / "w")
    graph = cmd[cmd.index("-filter_complex") + 1]
    assert graph.count("xfade=") == 2 and graph.count("acrossfade=") == 2
    assert "zoompan=" in graph and "boxblur=" in graph and "sidechaincompress" in graph
    assert "subtitles=overlays.ass" in graph and (tmp_path / "w" / "overlays.ass").exists()
    assert re.search(r"atempo=1\.5", graph)
    output_t = len(cmd) - 1 - cmd[::-1].index("-t")  # the output -t, after all the input options
    assert float(cmd[output_t + 1]) == pytest.approx(p.duration)


def test_render_end_to_end(media, tmp_path):
    p = _full_plan(media)
    progress = []
    result = render(p, tmp_path / "out.mp4", base_dir=tmp_path, font="DejaVu Sans", on_progress=progress.append)
    info = probe(result.output)
    assert (info.width, info.height) == (360, 640)
    assert info.has_audio
    assert info.duration == pytest.approx(p.duration, abs=0.1)
    assert result.thumbnail and result.thumbnail.exists()
    assert progress and progress[-1] <= 1.0


def test_render_preview_is_half_size(media, tmp_path):
    p = EditPlan.model_validate({"sources": {"main": str(media["land"])}, "canvas": {"width": 360, "height": 640},
                                 "clips": [{"source": "main", "start": 0, "end": 1}]})
    result = render(p, tmp_path / "prev.mp4", base_dir=tmp_path, preview=True)
    info = probe(result.output)
    assert (info.width, info.height) == (180, 320)
    assert result.thumbnail is None
