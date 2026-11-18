from PIL import Image

from vedit import autograde
from vedit.edl import Look
from vedit.render import look_filters


def test_flat_dull_frame_gets_boost_within_caps():
    dull = autograde.FrameStats(0.30, 0.30, 0.20, 0.02, 0.01)
    s = autograde.suggest(dull, "food").look
    assert 1.0 < s["saturation"] <= 1.32
    assert s["brightness"] > 0 and s["warmth"] > 0 and s["sharpen"] > 0.4
    Look(**s)  # valid against the schema


def test_people_graded_gentler_than_food():
    st = autograde.FrameStats(0.5, 0.6, 0.2, 0.05, 0.03)
    assert autograde.suggest(st, "nguoi").look["saturation"] < autograde.suggest(st, "food").look["saturation"]


def test_frame_stats_grey_image_has_no_saturation():
    st = autograde.frame_stats(Image.new("RGB", (64, 64), (128, 128, 128)))
    assert st.saturation < 0.01 and abs(st.warmth) < 0.01


def test_look_fields_reach_filter_graph():
    f = ",".join(look_filters(type("P", (), {"look": Look(saturation=1.2, warmth=0.2, sharpen=0.4)})()))
    assert "saturation=1.200" in f and "colorbalance" in f and "unsharp" in f
