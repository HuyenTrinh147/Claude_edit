"""Game toolkit: object tracking, world mapping, HUD items, chiptune SFX, pitch and freeze frames."""

import argparse
import importlib.util
import json
import re
import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError

from conftest import ffmpeg, needs_ffmpeg
from vedit.ass import FontBook, build_ass
from vedit.edl import EditPlan, ValueKey, validate_against_media
from vedit.hud import Counter, envelope, format_value, hud_events, value_at
from vedit.media import probe
from vedit.render import SFX, build_command, render
from vedit.track import Track, TrackPoint, smooth, track_path
from vedit.world import World, camera_at

needs_cv2 = pytest.mark.skipif(importlib.util.find_spec("cv2") is None, reason="opencv not installed")

ALL_HUD = [
    {"type": "visor", "start": 0, "end": 1.5, "text": "LEVEL 1 · CÀ PHÁO"},
    {"type": "reticle", "start": 0, "end": 1.5, "text": "CHILI", "lock_at": 0.5},
    {"type": "panel", "start": 0, "end": 1.5, "items": ["Rửa cà", "Pha nước muối"], "checks": [0.4, None]},
    {"type": "meter", "start": 0, "end": 1.5, "keys": [{"t": 0, "v": 0}, {"t": 1, "v": 0.8}], "zone": [0.7, 0.85],
     "style": "needle", "orientation": "vertical"},
    {"type": "counter", "start": 0, "end": 1.5, "keys": [{"t": 0, "v": 259200}, {"t": 1.2, "v": 0}],
     "format": "timer", "text": "FERMENTING"},
    {"type": "popup", "start": 0.3, "end": 1.2, "text": "PERFECT!", "sub": "+50"},
    {"type": "slots", "start": 0, "end": 1.5, "count": 3, "items": ["TỎI", "ỚT"], "icons": ["drop", None],
     "times": [0.6, 0.9]},
    {"type": "card", "start": 0.5, "end": 1.5, "stars": 2, "items": ["Độ giòn: 100%"]},
    {"type": "prompt", "start": 0, "end": 1.5, "button": "A", "text": "HOLD TO SEAL", "hold": [0.2, 0.8]},
    {"type": "icon", "start": 0, "end": 1.5, "icon": "coin", "spin": True},
]


def color_plan(**extra) -> EditPlan:
    data = {"canvas": {"width": 540, "height": 960, "fps": 30},
            "clips": [{"source": "color:#203040", "duration": 1.5}]}
    data.update(extra)
    return EditPlan.model_validate(data)


# ---- schema --------------------------------------------------------------------------------------

def test_hud_schema_accepts_every_type_and_rejects_bad_items():
    plan = color_plan(hud=ALL_HUD)
    assert [h.type for h in plan.hud] == [h["type"] for h in ALL_HUD]
    with pytest.raises(ValidationError, match="does not match any of the expected tags"):
        color_plan(hud=[{"type": "hologram", "start": 0, "end": 1}])
    with pytest.raises(ValidationError, match="checks"):
        color_plan(hud=[{"type": "panel", "start": 0, "end": 1, "items": ["a"], "checks": [0.1, 0.2]}])
    with pytest.raises(ValidationError, match="zone"):
        color_plan(hud=[{"type": "meter", "start": 0, "end": 1, "keys": [{"t": 0, "v": 0}], "zone": [0.9, 0.2]}])
    with pytest.raises(ValidationError, match="ô"):
        color_plan(hud=[{"type": "slots", "start": 0, "end": 1, "count": 1, "times": [0.2, 0.4]}])
    assert color_plan(hud=[{"type": "popup", "start": 0, "end": 1, "text": "x"}]).hud[0].exit == "pop"


def test_freeze_extends_clip_and_pitch_field():
    plan = EditPlan.model_validate({"clips": [{"source": "a.mp4", "start": 1, "end": 3, "speed": 2, "freeze": 0.5}],
                                    "audio": [{"path": "sfx:coin", "role": "sfx", "pitch": 7}]})
    assert plan.clips[0].timeline_duration == pytest.approx(1.5)
    assert plan.duration == pytest.approx(1.5)
    assert plan.audio[0].pitch == 7


# ---- values, easing --------------------------------------------------------------------------------

def test_value_keys_and_counter_formats():
    keys = [ValueKey(t=0, v=0), ValueKey(t=1, v=100, ease="linear"), ValueKey(t=2, v=0, ease="hold")]
    assert value_at(keys, -1) == 0
    assert value_at(keys, 0.25) == pytest.approx(25)
    assert value_at(keys, 1.5) == pytest.approx(100)  # hold: jumps only at the key
    assert value_at(keys, 2.5) == 0
    c = Counter(type="counter", start=0, end=1, keys=[ValueKey(t=0, v=0)], format="timer")
    assert format_value(c, 259200) == "72:00:00"
    assert format_value(c, 59.6) == "00:01:00"
    c.format, c.prefix = "int", "+"
    assert format_value(c, 1250.4) == "+1,250"
    c.format, c.prefix = "combo", ""
    assert format_value(c, 3) == "×3"


def test_enter_exit_envelopes():
    plan = color_plan(hud=[{"type": "icon", "start": 0, "end": 1, "icon": "star", "enter": "pop", "exit": "fade"},
                           {"type": "icon", "start": 0, "end": 1, "icon": "star", "enter": "stamp", "exit": "pop"}])
    pop, stamp = plan.hud
    assert envelope(pop, 0, 960).scale == pytest.approx(0, abs=1e-6)
    assert max(envelope(pop, t / 100, 960).scale for t in range(30)) > 1.05   # overshoot
    assert envelope(pop, 0.5, 960).scale == 1 and envelope(pop, 0.5, 960).alpha == 1
    assert envelope(pop, 0.99, 960).alpha < 0.1
    assert envelope(stamp, 0, 960).scale > 2 and envelope(stamp, 0, 960).rot < 0
    assert envelope(stamp, 0.99, 960).scale < 0.5


# ---- world mapping ----------------------------------------------------------------------------------

class FakeInfo:
    def __init__(self, w, h):
        self.width, self.height = w, h


def test_world_maps_source_points_through_fit_zoom_and_camera(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"")
    plan = EditPlan.model_validate({
        "canvas": {"width": 1080, "height": 1920, "fps": 30},
        "clips": [{"source": str(video), "start": 0, "end": 2, "zoom": "in", "zoom_amount": 0.1},
                  {"source": str(video), "start": 0, "end": 2, "fit": "contain"}],
        "motion": [{"type": "punch", "start": 3.0, "duration": 0.5, "amount": 0.1}]})
    world = World(plan, tmp_path, 30, lambda p: FakeInfo(640, 360))
    a, b = world.spans
    # cover: landscape 640x360 into 1080x1920 -> scale 5.333, centre crop
    x, y, ws, hs = world.fit(a, 0.5, 0.5)
    assert (x, y) == pytest.approx((540, 960)) and ws == pytest.approx(3413.33, abs=0.1)
    x, _, _, _ = world.fit(a, 0.55, 0.5)
    assert x == pytest.approx(540 + 0.05 * ws)
    # contain: letterboxed, full width
    x, y, ws, hs = world.fit(b, 0.0, 0.0)
    assert (x, ws) == pytest.approx((0, 1080)) and y == pytest.approx((1920 - 607.5) / 2)
    # Ken Burns zoom-in pushes points away from the centre by the current zoom
    last = a.frames - 1
    sx, _, z = world.to_screen(last, 640, 960, a)
    assert z == pytest.approx(1 + 0.1 * last / a.frames)
    assert sx == pytest.approx(540 + 100 * z)
    # timeline punch peaks at 20% of its window
    k = round(3.0 * 30) + round(0.2 * 15)
    assert camera_at(plan, k, 30)[0] == pytest.approx(1.1, abs=1e-3)
    assert world.span_at(round(2.5 * 30)) is b
    assert world.span_at(10_000) is None


def test_world_box_follows_track_and_hides_off_source(tmp_path):
    video, other = tmp_path / "v.mp4", tmp_path / "w.mp4"
    video.write_bytes(b"")
    other.write_bytes(b"")
    Track("cup", str(video), [TrackPoint(0, 0.2, 0.5, 0.1, 0.1), TrackPoint(2, 0.8, 0.5, 0.1, 0.1)]).save(
        track_path(tmp_path, "cup"))
    plan = EditPlan.model_validate({
        "canvas": {"width": 1000, "height": 1000, "fps": 20},
        "clips": [{"source": str(video), "start": 0, "end": 2}, {"source": str(other), "start": 0, "end": 1},
                  {"source": "color:#000000", "duration": 1}],
        "hud": [{"type": "icon", "start": 0, "end": 4, "icon": "star", "anchor": {"track": "cup", "point": "top"}}]})
    world = World(plan, tmp_path, 20, lambda p: FakeInfo(1000, 1000))
    anchor = plan.hud[0].anchor
    x, y, w, h = world.box(anchor, 20)        # t = 1s -> halfway along the track
    assert (x, y, w, h) == pytest.approx((500, 450, 100, 100))
    assert world.box(anchor, 50) is None      # another video on screen
    assert world.box(anchor, 70) is None      # colour card
    info = type("I", (), {"is_image": False, "duration": 5, "has_audio": False, "width": 1000, "height": 1000})
    problems = validate_against_media(plan, tmp_path, lambda p: info())
    assert any("không chiếu video của track 'cup'" in p for p in problems)
    plan2 = plan.model_copy(update={"hud": [plan.hud[0].model_copy(update={"anchor": anchor.model_copy(
        update={"track": "nope"})})]})
    assert any("chưa có track 'nope'" in p for p in validate_against_media(plan2, tmp_path, lambda p: info()))


# ---- HUD events -------------------------------------------------------------------------------------

def test_static_hud_parts_merge_into_single_events():
    plan = color_plan(hud=[{"type": "icon", "start": 0.5, "end": 1.0, "icon": "check", "enter": "none",
                            "exit": "none"}])
    lines = hud_events(plan, World(plan, None, 30), FontBook(), "DejaVu Sans")
    assert lines and len(lines) <= 3
    for line in lines:   # edges sit halfway between frames: 15 -> 14.5/30 s, 30 -> 29.5/30 s
        assert ",0:00:00.48,0:00:00.98," in line


def test_every_hud_type_produces_events():
    plan = color_plan(hud=ALL_HUD)
    ass = build_ass(plan, "DejaVu Sans", Path("assets/fonts"), fps=30)
    layers = {int(m.group(1)) for m in re.finditer(r"^Dialogue: (\d+),", ass, re.M)}
    for idx in range(len(ALL_HUD)):   # every item drew something on its own layer band
        assert any(20 + idx * 6 <= layer < 26 + idx * 6 for layer in layers), ALL_HUD[idx]["type"]
    assert "72:00:00"[:2] in ass and "PERFECT!" in ass and "HOLD TO SEAL" in ass


def test_smoothing_keeps_endpoints_and_removes_jitter():
    pts = [TrackPoint(i / 30, 0.5 + (0.02 if i % 2 else -0.02), 0.5, 0.1, 0.1) for i in range(30)]
    out = smooth(pts, 0.8)
    spread = max(p.x for p in out[5:-5]) - min(p.x for p in out[5:-5])
    assert spread < 0.02 and len(out) == len(pts)


# ---- tracking (OpenCV) ------------------------------------------------------------------------------

@needs_ffmpeg
@needs_cv2
def test_track_follows_moving_square_and_stops_at_cut(tmp_path, settings):
    from vedit.cli import cmd_track
    from vedit.project import Project
    from vedit.track import track_object

    video = tmp_path / "square.mp4"
    # a textured 48 px patch sliding right for 2 s, then a cut to another shot (plain squares have nothing
    # for any correlation tracker to hold on to, real objects do)
    ffmpeg("-f", "lavfi", "-i", "color=c=0x202830:s=320x240:r=25:d=2",
           "-f", "lavfi", "-i", "testsrc=s=48x48:r=25:d=2",
           "-f", "lavfi", "-i", "testsrc2=s=320x240:r=25:d=1",
           "-filter_complex", "[0][1]overlay=x='20+100*t':y=96:shortest=1[a];[a][2]concat=n=2:v=1[v]",
           "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video))
    track = track_object(video, name="sq", at=0.0, box=(20 / 320, 96 / 240, 48 / 320, 48 / 240), until=2.8)
    assert track.points[0].t == pytest.approx(0.0)
    for t in (0.5, 1.0, 1.5):
        p = track.at(t)
        assert p.x == pytest.approx((20 + 100 * t + 24) / 320, abs=0.015)
        assert p.y == pytest.approx(120 / 240, abs=0.015)
    assert track.end < 2.05 and track.stopped == ["cuối"]   # did not track into the second shot

    project = Project.create(settings, video, "sq")
    args = argparse.Namespace(project=project.slug, name="sq", at=0.5, box="0.22,0.40,0.15,0.20", until=1.5,
                              back=0.0, source=None, smooth=0.5)
    cmd_track(args, settings)
    saved = Track.load(track_path(project.dir, "sq"))
    assert saved.start == pytest.approx(0.0) and saved.end == pytest.approx(1.48, abs=0.05)
    assert (project.analysis_dir / "tracks" / "sq_sheet.jpg").exists()


# ---- audio --------------------------------------------------------------------------------------------

@needs_ffmpeg
def test_every_builtin_sfx_renders(tmp_path):
    for name, graph in SFX.items():
        out = tmp_path / f"{name}.wav"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-filter_complex",
                        f"{graph},asetrate=48000*1.5,aresample=48000[a]", "-map", "[a]", str(out)], check=True)
        assert probe(out).duration > 0.02, name


# ---- full render --------------------------------------------------------------------------------------

@needs_ffmpeg
def test_render_with_hud_freeze_and_game_sfx(media, tmp_path):
    plan = EditPlan.model_validate({
        "sources": {"main": str(media["land"])},
        "canvas": {"width": 540, "height": 960, "fps": 30},
        "clips": [{"source": "main", "start": 0.5, "end": 1.5, "freeze": 0.5}],
        "hud": ALL_HUD,
        "audio": [{"path": "sfx:levelup", "role": "sfx", "start": 0.2, "volume": 0.6, "pitch": 2},
                  {"path": "sfx:slash", "role": "sfx", "start": 0.8, "volume": 0.6}],
    })
    cmd = build_command(plan, tmp_path / "x.mp4", base_dir=tmp_path, work_dir=tmp_path / "w", font="DejaVu Sans")
    graph = cmd[cmd.index("-filter_complex") + 1]
    assert "tpad=stop_mode=clone:stop_duration=1.5" in graph
    assert "asetrate=53878" in graph   # +2 semitones
    result = render(plan, tmp_path / "out.mp4", base_dir=tmp_path, font="DejaVu Sans",
                    fonts_dir=Path("assets/fonts"), work_dir=tmp_path / "work")
    assert result.duration == pytest.approx(1.5, abs=0.05)
    ass = (tmp_path / "work" / "overlays.ass").read_text(encoding="utf-8")
    assert ass.count("Dialogue:") > 50
    snapshot = json.loads((tmp_path / "out.plan.json").read_text(encoding="utf-8"))
    assert len(snapshot["hud"]) == len(ALL_HUD)


# ---- slash + sprites cut from the video ---------------------------------------------------------------

def test_make_sprite_pixelates_quantizes_and_chamfers():
    from PIL import Image

    from vedit.edl import Sprite
    from vedit.hud import make_sprite

    image = Image.new("RGB", (200, 100), (230, 40, 30))
    image.paste((30, 60, 220), (100, 0, 200, 100))   # right half blue
    art = make_sprite(image, Sprite(t=0, box=(0, 0, 1, 1), pixels=8, colors=4))
    assert (art.w, art.h) == (8, 4)
    assert len(art.runs) == 2                       # two flat colours survive quantisation
    cells = {(r, c) for runs in art.runs.values() for r, c0, c1 in runs for c in range(c0, c1)}
    assert (0, 0) not in cells and (3, 7) not in cells   # chamfered corners
    assert (1, 1) in cells and len(cells) == 8 * 4 - 4


@needs_ffmpeg
def test_slash_and_video_sprites_draw(media, tmp_path):
    plan = EditPlan.model_validate({
        "sources": {"main": str(media["land"])},
        "canvas": {"width": 540, "height": 960, "fps": 30},
        "clips": [{"source": "main", "start": 0, "end": 1.5}],
        "hud": [
            {"type": "slash", "start": 0.2, "end": 0.5, "x": 0.5, "y": 0.5},
            {"type": "slots", "start": 0, "end": 1.5, "count": 2, "items": ["MUỐI"], "times": [0.6],
             "sprites": [{"t": 1.0, "box": [0.1, 0.1, 0.3, 0.3], "pixels": 10, "colors": 6}]},
            {"type": "card", "start": 0.8, "end": 1.5, "sprite": {"t": 4.5, "box": [0, 0, 1, 1]}},
            {"type": "icon", "start": 0, "end": 1.5, "sprite": {"t": 2.5, "box": [0.2, 0.2, 0.5, 0.5]}, "spin": True},
        ]})
    assert validate_against_media(plan, tmp_path, probe) == []
    ass = build_ass(plan, "DejaVu Sans", Path("assets/fonts"), fps=30, base_dir=tmp_path, probe=probe)
    slash = [ln for ln in ass.splitlines() if ln.startswith(("Dialogue: 20,", "Dialogue: 21,", "Dialogue: 22,",
                                                             "Dialogue: 23,"))]
    assert len(slash) > 10                           # streak, afterimage and particles over ~9 frames
    colours = set(re.findall(r"\\1c(&H[0-9A-F]{6}&)", ass))
    assert len(colours) > 12                         # pixel-art palettes from three different frames
    bad = plan.model_copy(update={"hud": [plan.hud[2].model_copy(update={"sprite": plan.hud[2].sprite.model_copy(
        update={"t": 99.0})})]})
    assert any("vượt quá độ dài nguồn" in p for p in validate_against_media(bad, tmp_path, probe))
    with pytest.raises(ValidationError, match="đúng một"):
        color_plan(hud=[{"type": "icon", "start": 0, "end": 1}])
