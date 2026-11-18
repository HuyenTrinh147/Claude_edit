"""Automatic colour / sharpness grading suggestions for the editor.

Measures a handful of frames (mean luma, tonal spread, saturation, warmth, sharpness) and suggests the plan's `look`
values for a kind of content (food gets warmer, more saturated, slightly crisper). It is a heuristic with hard caps,
not magic: the editor still checks the result by eye (skin tones, over-saturation, HDR clips).
"""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

CONTENT_KINDS = ("food", "nguoi", "phong-canh", "mac-dinh")


@dataclass
class FrameStats:
    luma: float          # mean luma 0..1
    spread: float        # p95 - p5 of luma (tonal range) 0..1
    saturation: float    # mean HSV saturation 0..1
    warmth: float        # mean (R - B) / 255, -1..1
    sharpness: float     # mean absolute Laplacian response, 0..~0.3 (higher = crisper)


@dataclass
class Suggestion:
    look: dict
    notes: list[str] = field(default_factory=list)


def frame_stats(img: Image.Image) -> FrameStats:
    im = img.convert("RGB")
    im.thumbnail((640, 640))
    a = np.asarray(im, dtype=np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0.0)
    gray = luma
    lap = np.abs(4 * gray[1:-1, 1:-1] - gray[:-2, 1:-1] - gray[2:, 1:-1] - gray[1:-1, :-2] - gray[1:-1, 2:])
    p5, p95 = np.percentile(luma, [5, 95])
    return FrameStats(float(luma.mean()), float(p95 - p5), float(sat.mean()), float((r - b).mean()), float(lap.mean()))


def average(stats: list[FrameStats]) -> FrameStats:
    n = max(1, len(stats))
    return FrameStats(*(sum(getattr(s, f) for s in stats) / n for f in ("luma", "spread", "saturation", "warmth", "sharpness")))


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# per-content targets: (target saturation, max saturation factor, warmth push, base contrast, sharpen)
_TARGETS = {
    "food": dict(sat=0.46, sat_max=1.32, warmth=0.30, contrast=1.07, sharpen=0.42),
    "nguoi": dict(sat=0.34, sat_max=1.10, warmth=0.12, contrast=1.04, sharpen=0.25),
    "phong-canh": dict(sat=0.42, sat_max=1.22, warmth=0.08, contrast=1.06, sharpen=0.40),
    "mac-dinh": dict(sat=0.38, sat_max=1.15, warmth=0.10, contrast=1.04, sharpen=0.30),
}


def suggest(stats: FrameStats, content: str = "food") -> Suggestion:
    """Look values (edl.Look fields) for `content`, derived from the measured `stats`."""
    t = _TARGETS.get(content, _TARGETS["mac-dinh"])
    notes = []
    sat = _clamp(t["sat"] / max(stats.saturation, 0.05), 1.0, t["sat_max"])
    notes.append(f"Độ rực trung bình {stats.saturation:.2f} → nhân {sat:.2f}" + (" (đã chạm trần để khỏi quá sặc)" if sat >= t["sat_max"] - 1e-6 else ""))
    contrast = t["contrast"] + (0.06 if stats.spread < 0.45 else 0.0) - (0.04 if stats.spread > 0.8 else 0.0)
    notes.append(f"Dải sáng tối {stats.spread:.2f} → tương phản {contrast:.2f}")
    brightness = 0.0
    if stats.luma < 0.36:
        brightness = _clamp((0.42 - stats.luma) * 0.5, 0.0, 0.08)
        notes.append(f"Hơi tối (độ sáng {stats.luma:.2f}) → tăng sáng {brightness:+.2f}")
    elif stats.luma > 0.64:
        brightness = -_clamp((stats.luma - 0.58) * 0.5, 0.0, 0.06)
        notes.append(f"Hơi cháy sáng (độ sáng {stats.luma:.2f}) → giảm sáng {brightness:+.2f}")
    warmth = t["warmth"] if stats.warmth < 0.12 else t["warmth"] * 0.5
    notes.append(f"Độ ấm {stats.warmth:+.2f} → đẩy ấm {warmth:.2f}")
    sharpen = _clamp(t["sharpen"] + (0.15 if stats.sharpness < 0.02 else 0.0) - (0.15 if stats.sharpness > 0.08 else 0.0), 0.1, 0.7)
    notes.append(f"Độ nét đo được {stats.sharpness:.3f} → làm nét {sharpen:.2f}")
    look = {"preset": "none", "saturation": round(sat, 3), "contrast": round(contrast, 3), "brightness": round(brightness, 3),
            "warmth": round(warmth, 3), "sharpen": round(sharpen, 3)}
    return Suggestion(look, notes)


def sample_frames(source: Path, times: list[float], out_dir: Path) -> list[Path]:
    out = []
    for i, t in enumerate(times):
        p = out_dir / f"{source.stem}_{i}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0.0, t):.2f}", "-i", str(source), "-frames:v", "1",
                        "-vf", "scale=640:-2", str(p)], check=False)
        if p.exists():
            out.append(p)
    return out


def measure(sources: list[tuple[Path, float]], per_source: int = 1) -> FrameStats:
    """Average stats over frames taken at (file, second) pairs."""
    stats = []
    with tempfile.TemporaryDirectory() as tmp:
        for src, t in sources:
            for f in sample_frames(src, [t + 0.4 * k for k in range(per_source)], Path(tmp)):
                with Image.open(f) as im:
                    stats.append(frame_stats(im))
    if not stats:
        raise ValueError("Không lấy được khung hình nào để đo")
    return average(stats)
