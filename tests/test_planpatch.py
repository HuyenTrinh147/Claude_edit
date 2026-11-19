"""Studio timeline bridge: EditPlan -> timeline data, and validated edits back into the plan."""
import pytest

from vedit.edl import EditPlan
from vedit.planpatch import apply_edits, parse_path, timeline


def base_plan():
    return {"sources": {"a": "a.mp4"}, "clips": [
        {"source": "a", "start": 0, "end": 4}, {"source": "a", "start": 4, "end": 8, "speed": 2, "transition": {"type": "fade", "duration": 0.5}}],
        "texts": [{"text": "một", "start": 0.5, "end": 2.5, "y": 0.3}, {"text": "hai", "start": 3, "end": 5, "y": 0.4}],
        "audio": [{"path": "sfx:pop", "role": "sfx", "start": 1.0, "volume": 0.5}, {"path": "sfx:ding", "role": "sfx", "start": 3.0}]}


def test_timeline_matches_the_plan_geometry():
    plan = EditPlan.model_validate(base_plan())
    tl = timeline(plan)
    assert tl["duration"] == pytest.approx(plan.duration) and [c["i"] for c in tl["clips"]] == [0, 1]
    assert tl["clips"][1]["tl"] == pytest.approx(4 - 0.5)            # the fade overlaps the previous clip by its duration
    assert tl["clips"][1]["dur"] == pytest.approx(2.0)               # 4 s of source at x2
    assert tl["texts"][0]["text"] == "một" and tl["audio"][0]["name"] == "pop" and tl["audio"][0]["dur"] > 0


def test_parse_path_and_roots():
    assert parse_path("texts[3].text") == ["texts", 3, "text"]
    with pytest.raises(ValueError):
        parse_path("sources.a")


def test_apply_edits_sets_validates_and_rejects():
    plan = base_plan()
    edits = [{"path": "texts[0].text", "value": "MỘT"}, {"path": "clips[1].speed", "value": 99},
             {"path": "audio[0].volume", "value": 0.2}, {"path": "texts[9].text", "value": "x"}, {"path": "sources.a", "value": "b.mp4"}]
    new, applied, rejected = apply_edits(plan, edits)
    assert [e["path"] for e in applied] == ["texts[0].text", "audio[0].volume"]
    assert {e["path"] for e in rejected} == {"clips[1].speed", "texts[9].text", "sources.a"}
    assert new["texts"][0]["text"] == "MỘT" and new["audio"][0]["volume"] == 0.2 and plan["texts"][0]["text"] == "một"   # input untouched
    EditPlan.model_validate(new)


def test_deletes_run_last_and_highest_index_first():
    new, applied, rejected = apply_edits(base_plan(), [
        {"op": "delete", "path": "texts[0]"}, {"op": "delete", "path": "texts[1]"}, {"path": "texts[1].text", "value": "HAI"}])
    assert not rejected and new["texts"] == [] and len(applied) == 3


def test_append_adds_a_new_block_after_the_sets():
    new, applied, rejected = apply_edits(base_plan(), [
        {"op": "append", "path": "texts", "value": {"text": "mới", "start": 6, "end": 7.5, "y": 0.5}},
        {"path": "texts[2].text", "value": "không có (chưa thêm)"}])
    assert [e["path"] for e in applied] == ["texts[2].text", "texts"] or len(new["texts"]) == 3
    assert new["texts"][-1]["text"] in ("mới",)  # the append is applied; the set on the not-yet-existing item was rejected first
    assert any(e["path"] == "texts[2].text" for e in rejected)
    assert apply_edits(base_plan(), [{"op": "append", "path": "clips", "value": {"nope": 1}}])[2]   # invalid element rejected


def plan4():
    p = base_plan()
    p["clips"] = [{"source": "a", "start": i, "end": i + 1} for i in range(4)]
    return p


def test_move_clips_use_original_numbers_and_run_last():
    new, applied, rejected = apply_edits(plan4(), [
        {"op": "move", "path": "clips[1]", "after": 3}, {"op": "move", "path": "clips[2]", "after": 3},
        {"path": "clips[1].end", "value": 1.5}])
    assert not rejected and len(applied) == 3
    assert [c["start"] for c in new["clips"]] == [0, 3, 2, 1] and new["clips"][3]["end"] == 1.5   # set used original number 1


def test_move_to_front_and_rejects_bad_targets():
    new, applied, rejected = apply_edits(plan4(), [
        {"op": "move", "path": "clips[3]", "after": -1}, {"op": "move", "path": "clips[9]", "after": 0},
        {"op": "move", "path": "clips[1]", "after": 1}, {"op": "move", "path": "texts[0]", "after": 0}])
    assert [c["start"] for c in new["clips"]] == [3, 0, 1, 2]
    assert len(applied) == 1 and len(rejected) == 3


def test_move_skips_deleted_clips():
    new, applied, rejected = apply_edits(plan4(), [
        {"op": "delete", "path": "clips[2]"}, {"op": "move", "path": "clips[0]", "after": 3}, {"op": "move", "path": "clips[1]", "after": 2}])
    assert [c["start"] for c in new["clips"]] == [1, 3, 0] and len(rejected) == 1
