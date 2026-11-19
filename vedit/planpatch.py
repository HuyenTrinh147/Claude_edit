"""Bridge between the Studio timeline page and edit_plan.json.

`timeline(plan)` flattens an EditPlan into what a timeline UI draws (clip positions on the timeline, text / audio / graphic /
motion blocks). `apply_edits(plan, edits)` applies the user's edits one at a time, each validated against the EditPlan schema,
so a bad value is reported and skipped instead of corrupting the plan.

An edit is ``{"id", "op": "set"|"delete", "path": "texts[3].text", "value": ..., "label": "..."}``.

``{"op": "move", "path": "clips[9]", "after": 8}`` reorders clips: clip number 9 (as numbered in the plan the user saw) goes
right after clip 8 (``after`` = -1 puts it first). Numbers always mean the ORIGINAL positions, so several moves and the
set / delete edits in one batch never shift each other; moves run last, in the order given.
"""

from __future__ import annotations

import copy
import re
from typing import Any

from pydantic import ValidationError

from .edl import EditPlan

ROOTS = {"clips", "texts", "audio", "graphics", "motion", "look", "canvas", "export"}
_TOKEN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)|\[(\d+)\]")


def parse_path(path: str) -> list[str | int]:
    pos, out = 0, []
    while pos < len(path):
        if path[pos] == ".":
            pos += 1
            continue
        m = _TOKEN.match(path, pos)
        if not m:
            raise ValueError(f"đường dẫn không hợp lệ: {path!r}")
        out.append(m.group(1) if m.group(1) is not None else int(m.group(2)))
        pos = m.end()
    if not out or out[0] not in ROOTS:
        raise ValueError(f"chỉ sửa được: {', '.join(sorted(ROOTS))} (nhận {path!r})")
    return out


def _walk(obj: Any, keys: list[str | int]) -> Any:
    for k in keys:
        obj = obj[k]
    return obj


def set_path(plan: dict, path: str, value: Any) -> None:
    keys = parse_path(path)
    parent = _walk(plan, keys[:-1])
    last = keys[-1]
    if isinstance(last, int):
        if not 0 <= last < len(parent):
            raise IndexError(f"{path}: không có phần tử số {last}")
        parent[last] = value
    else:
        if not isinstance(parent, dict):
            raise ValueError(f"{path}: không phải đối tượng")
        parent[last] = value


def delete_path(plan: dict, path: str) -> None:
    keys = parse_path(path)
    parent = _walk(plan, keys[:-1])
    last = keys[-1]
    if isinstance(last, int):
        del parent[last]
    else:
        parent.pop(last, None)


def append_path(plan: dict, path: str, value: Any) -> None:
    keys = parse_path(path)
    target = _walk(plan, keys)
    if not isinstance(target, list):
        raise ValueError(f"{path}: không phải danh sách để thêm vào")
    target.append(value)


def move_clip(plan: dict, ids: list, path: str, after: int) -> None:
    """Move the clip that was originally at `path` (clips[N]) to right after the clip that was originally `after`.
    `ids` mirrors plan["clips"] with each clip's original index (None for appended clips)."""
    keys = parse_path(path)
    if len(keys) != 2 or keys[0] != "clips" or not isinstance(keys[1], int):
        raise ValueError(f"chỉ dời được clip (clips[N]), nhận {path!r}")
    src = keys[1]
    if src not in ids:
        raise ValueError(f"{path}: clip này đã bị xoá hoặc không có")
    if after != -1 and after not in ids:
        raise ValueError(f"không dời được ra sau clip {after}: clip đó đã bị xoá hoặc không có")
    if after == src:
        raise ValueError("không thể dời clip ra sau chính nó")
    pos = ids.index(src)
    clip = plan["clips"].pop(pos)
    ids.pop(pos)
    dest = 0 if after == -1 else ids.index(after) + 1
    plan["clips"].insert(dest, clip)
    ids.insert(dest, src)


def apply_edits(plan: dict, edits: list[dict]) -> tuple[dict, list[dict], list[dict]]:
    """Returns (new plan dict, applied edits, rejected edits with a `reason`). Order: sets, appends, deletes
    (highest index first, so earlier deletes never shift later ones), then clip moves (by original index)."""
    current = copy.deepcopy(plan)
    applied, rejected = [], []
    ids: list = list(range(len(current.get("clips", []))))
    moves = [e for e in edits if e.get("op") == "move"]
    edits = [e for e in edits if e.get("op") != "move"]
    sets = [e for e in edits if e.get("op", "set") in ("set", "append")]
    sets.sort(key=lambda e: e.get("op") == "append")
    deletes = sorted((e for e in edits if e.get("op") == "delete"),
                     key=lambda e: [k for k in parse_path(e["path"]) if isinstance(k, int)] or [0], reverse=True)
    for e in sets + deletes:
        trial = copy.deepcopy(current)
        try:
            op = e.get("op", "set")
            if op == "delete":
                delete_path(trial, e["path"])
            elif op == "append":
                append_path(trial, e["path"], e.get("value"))
            else:
                set_path(trial, e["path"], e.get("value"))
            EditPlan.model_validate(trial)
            _track_clips(e, ids)
        except (ValueError, KeyError, IndexError, TypeError, ValidationError) as err:
            reason = "; ".join(x["msg"] for x in err.errors()[:2]) if isinstance(err, ValidationError) else str(err)
            rejected.append({**e, "reason": reason})
            continue
        current = trial
        applied.append(e)
    for e in moves:
        trial, trial_ids = copy.deepcopy(current), list(ids)
        try:
            move_clip(trial, trial_ids, e["path"], int(e.get("after", -1)))
            EditPlan.model_validate(trial)
        except (ValueError, KeyError, IndexError, TypeError, ValidationError) as err:
            reason = "; ".join(x["msg"] for x in err.errors()[:2]) if isinstance(err, ValidationError) else str(err)
            rejected.append({**e, "reason": reason})
            continue
        current, ids = trial, trial_ids
        applied.append(e)
    return current, applied, rejected


def _track_clips(e: dict, ids: list) -> None:
    """Keep `ids` (original clip numbers) in step with deletes / appends on plan["clips"]."""
    keys = parse_path(e["path"])
    if keys[0] != "clips":
        return
    op = e.get("op", "set")
    if op == "delete" and len(keys) == 2 and isinstance(keys[1], int) and 0 <= keys[1] < len(ids):
        ids.pop(keys[1])
    elif op == "append" and len(keys) == 1:
        ids.append(None)


def _sfx_len(name: str) -> float:
    return 0.8 if name in ("complete", "levelup", "rise", "combo") else 0.45


def timeline(plan: EditPlan) -> dict:
    """What the timeline UI draws. Times are timeline seconds."""
    offsets = plan.clip_offsets()
    clips = []
    for i, c in enumerate(plan.clips):
        clips.append({"i": i, "source": c.source, "ss": round(c.start, 3), "se": round(c.end or 0, 3), "speed": c.speed,
                      "tl": round(offsets[i], 3), "dur": round(c.timeline_duration, 3), "freeze": c.freeze,
                      "mute": c.mute, "volume": c.volume, "fit": c.fit, "zoom": c.zoom, "zoom_amount": c.zoom_amount,
                      "scale": c.scale, "focus_x": c.focus_x, "focus_y": c.focus_y,
                      "transition": ({"type": c.transition.type, "duration": c.transition.duration} if c.transition else None),
                      "note": c.note})
    total = plan.duration
    texts = [{"i": i, "text": t.text, "start": t.start, "end": t.end, "style": t.style, "font": t.font, "size": t.size,
              "color": t.color, "x": t.x, "y": t.y, "rotation": t.rotation, "animation": t.animation,
              "bold": t.bold, "outline": t.outline, "outline_color": t.outline_color, "shadow": t.shadow,
              "shadow_color": t.shadow_color, "shape": t.shape, "shape_color": t.shape_color}
             for i, t in enumerate(plan.texts)]
    audio = []
    for i, a in enumerate(plan.audio):
        name = a.builtin or a.path.rsplit("/", 1)[-1]
        dur = a.duration or (total - a.start if a.role == "music" else _sfx_len(a.builtin or ""))
        audio.append({"i": i, "role": a.role, "name": name, "start": a.start, "dur": round(dur, 3), "volume": a.volume,
                      "pitch": a.pitch, "fade_in": a.fade_in, "fade_out": a.fade_out})
    graphics = [{"i": i, "type": g.type, "start": g.start, "end": g.end, "color": getattr(g, "color", None)}
                for i, g in enumerate(plan.graphics)]
    motion = [{"i": i, "type": m.type, "start": m.start, "duration": m.duration, "amount": m.amount} for i, m in enumerate(plan.motion)]
    return {"duration": round(total, 3), "fps": plan.canvas.fps, "title": plan.title, "clips": clips, "texts": texts,
            "audio": audio, "graphics": graphics, "motion": motion}
