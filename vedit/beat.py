"""Music analysis for picking a background track: tempo, first beat, the most energetic window, loudness.

No AI and no extra dependencies (numpy + ffmpeg). The tempo estimate is the autocorrelation peak of an onset-strength
envelope, folded into 70-180 BPM; it is a good guess, not ground truth, so `confidence` says how clear the peak was.
"""

from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .media import MediaError, loudness, probe

AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus"}
SR = 11025
HOP = 256  # envelope frame = 23 ms


@dataclass
class MusicInfo:
    path: str
    duration: float
    bpm: float
    confidence: float          # 0..1, how dominant the tempo peak is (< 0.3: treat the BPM as a guess)
    first_beat: float          # seconds of the first beat on the estimated grid
    best_window_start: float   # start of the most energetic window (for cutting a hook-length excerpt)
    window: float
    mean_db: float | None      # mean volume (dB) — compare with the voice level before choosing the music volume
    peak_db: float | None

    def to_dict(self) -> dict:
        return asdict(self)


def _decode(path: Path) -> np.ndarray:
    proc = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                          capture_output=True)
    if proc.returncode != 0:
        raise MediaError(f"Không đọc được âm thanh {path}: {proc.stderr.decode(errors='replace')[-300:]}")
    return np.frombuffer(proc.stdout, dtype="<f4")


def _onset_envelope(x: np.ndarray) -> np.ndarray:
    """Positive spectral flux on a 1024-point STFT, hop 256."""
    n_fft = 1024
    if len(x) < n_fft * 2:
        return np.zeros(0)
    win = np.hanning(n_fft)
    idx = np.arange(0, len(x) - n_fft, HOP)
    frames = np.stack([x[i:i + n_fft] * win for i in idx])
    mag = np.log1p(10 * np.abs(np.fft.rfft(frames, axis=1)))
    flux = np.maximum(np.diff(mag, axis=0), 0).sum(axis=1)
    flux = np.concatenate([[0.0], flux])
    return flux - np.convolve(flux, np.ones(21) / 21, mode="same")   # remove the slow trend


def estimate_tempo(env: np.ndarray, lo: float = 70, hi: float = 180) -> tuple[float, float, float]:
    """(bpm, confidence, first_beat_s) from an onset envelope."""
    rate = SR / HOP
    if len(env) < rate * 4:
        return 0.0, 0.0, 0.0
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    lags = np.arange(len(ac))
    lag_lo, lag_hi = int(rate * 60 / hi), int(rate * 60 / lo)
    seg = ac[lag_lo:lag_hi + 1]
    if seg.max() <= 0:
        return 0.0, 0.0, 0.0
    # sharpen: a true tempo also has energy at 2x its period
    score = seg.copy()
    for k, lag in enumerate(range(lag_lo, lag_hi + 1)):
        if 2 * lag < len(ac):
            score[k] += 0.5 * ac[2 * lag]
    best = int(np.argmax(score))
    lag = lag_lo + best
    # parabolic refinement of the peak position
    if 0 < lag < len(ac) - 1:
        a, b, c = ac[lag - 1], ac[lag], ac[lag + 1]
        denom = a - 2 * b + c
        if denom != 0:
            lag = lag + 0.5 * (a - c) / denom
    bpm = 60.0 * rate / lag
    confidence = float(np.clip((seg.max() - np.median(seg)) / (ac[0] + 1e-9) * 4, 0, 1))
    # first beat: the phase (offset within one fractional period) with the most onset energy; the STFT frame time is the
    # window START, the flux peak lands when the onset is mid-window, so add half a window back
    period = lag
    phases = np.arange(0, period, 0.5)
    frames = np.arange(len(env), dtype=float)
    energy = []
    for ph in phases:
        pos = np.arange(ph, len(env) - 1, period)
        energy.append(float(np.interp(pos, frames, env).sum()))
    first = float(phases[int(np.argmax(energy))]) + (512 / HOP)
    return float(bpm), confidence, (first / rate) % (60.0 / bpm)


def best_window(x: np.ndarray, window: float) -> float:
    """Start (s) of the window with the highest mean RMS; falls back to 0 for short tracks."""
    hop = SR // 2
    rms = np.sqrt(np.array([np.mean(x[i:i + hop] ** 2) for i in range(0, max(len(x) - hop, 1), hop)]))
    w = max(int(window / 0.5), 1)
    if len(rms) <= w:
        return 0.0
    sums = np.convolve(rms, np.ones(w), mode="valid")
    return float(np.argmax(sums)) * 0.5


def analyze_music(path: str | Path, window: float = 20.0) -> MusicInfo:
    path = Path(path)
    info = probe(path)
    x = _decode(path)
    bpm, conf, first = estimate_tempo(_onset_envelope(x))
    try:
        loud = loudness(path)
    except MediaError:
        loud = {}
    return MusicInfo(path=str(path), duration=round(info.duration, 2), bpm=round(bpm, 1), confidence=round(conf, 2),
                     first_beat=round(first, 3), best_window_start=round(best_window(x, window), 1), window=window,
                     mean_db=loud.get("mean_db"), peak_db=loud.get("peak_db"))


def list_music(directory: Path) -> list[Path]:
    return sorted(p for p in Path(directory).rglob("*") if p.suffix.lower() in AUDIO_EXTS and p.is_file())
