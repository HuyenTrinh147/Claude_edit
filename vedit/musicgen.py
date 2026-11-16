"""Procedural music beds: a short, loopable background track made from code (no files, no licences).

Styles (``CATALOG`` has the mood / BPM / when-to-use of each):
- ``pastel`` = cheerful music-box / kalimba arpeggios over a I–vi–IV–V loop with a soft bass, a warm pad and a light
  shaker; the last two bars resolve into a bell arpeggio and a held chord, so the bed can end on a "level clear".
- ``beat`` = the same bright tones on a clear drum groove (kick on 1 and the "and" of 3, clap on 2 and 4, 8th hats)
  with a bouncing bass: for cutting on the beat (~122 BPM).
- ``lofi`` = slow, swung, soft: warm pad, sparse plucks, gentle kick / rim and a vinyl crackle (~80 BPM), made to sit
  under a voice-over.
Deterministic for a given (duration, bpm, seed). Written as 48 kHz 16-bit stereo WAV; use it as an EditPlan
``audio`` track with ``role: "music"``.
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SR = 48000
STYLES = ("pastel", "beat", "lofi")
# (target BPM when `bpm` is not given, mood, when to use) — the actual BPM is nudged so the bed is a whole number of bars
CATALOG = {
    "pastel": (104, "vui, ngọt, hộp nhạc / kalimba", "video đồ ăn, mèo, game pastel, nhạc thưa dưới giọng"),
    "beat": (122, "sôi nổi, có nhịp trống rõ", "cắt theo beat 1–1,5 s, video mẹo / công thức, sản phẩm, showcase"),
    "lofi": (80, "chậm, ấm, êm", "dưới giọng đọc, vlog, kể chuyện, ASMR nhẹ, cảnh thư giãn"),
}

# chord -> (bass MIDI note, intervals); melody and pad are built from the same tones
CHORDS = {"C": (36, (0, 4, 7)), "Am": (33, (0, 3, 7)), "F": (29, (0, 4, 7)), "G": (31, (0, 4, 7))}
LOOP = ("C", "Am", "F", "G")
# eighth-note patterns: indexes into the chord's tones over two octaves (0-5), None = rest
PATTERNS = (
    (2, None, 4, 3, 2, 3, 4, None),
    (0, 2, 3, 2, 4, 3, 2, None),
    (3, 4, 5, 4, 3, 2, 1, 2),
    (1, 3, 4, 3, 2, None, 3, 4),
)


def _hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def _pluck(freq: float, dur: float, bright: float = 1.0) -> np.ndarray:
    """Music-box / kalimba tone: a fundamental plus fast-dying inharmonic partials and a tiny click."""
    t = np.arange(int(dur * SR)) / SR
    y = (np.sin(2 * np.pi * freq * t) * np.exp(-t * 4.2)
         + 0.32 * bright * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t * 8.5)
         + 0.16 * bright * np.sin(2 * np.pi * freq * 4.1 * t) * np.exp(-t * 17.0))
    attack = np.minimum(t / 0.003, 1.0)
    return (y * attack).astype(np.float32)


def _bass(freq: float, dur: float) -> np.ndarray:
    t = np.arange(int(dur * SR)) / SR
    y = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t)
    env = np.minimum(t / 0.01, 1.0) * np.exp(-t * 3.2) * np.minimum((dur - t) / 0.05, 1.0).clip(0, 1)
    return (y * env).astype(np.float32)


def _pad(freqs: list[float], dur: float) -> np.ndarray:
    t = np.arange(int(dur * SR)) / SR
    y = np.zeros_like(t)
    for f in freqs:
        for detune in (-0.25, 0.25):
            y += np.sin(2 * np.pi * (f + detune) * t) + 0.22 * np.sin(2 * np.pi * 2 * (f + detune) * t)
    env = np.sin(np.minimum(t / 0.4, 1.0) * np.pi / 2) ** 2 * np.minimum((dur - t) / 0.5, 1.0).clip(0, 1)
    return (y * env / (2 * len(freqs))).astype(np.float32)


def _place(bus: np.ndarray, sound: np.ndarray, start: float, gain: float, pan: float) -> None:
    """Add `sound` into a (2, n) bus at `start` seconds, constant-power panned (-1 left .. 1 right)."""
    i = int(round(start * SR))
    if i >= bus.shape[1] or i + len(sound) <= 0:
        return
    if i < 0:   # humanised timing can land a hair before the start: trim instead of wrapping around
        sound, i = sound[-i:], 0
    j = min(i + len(sound), bus.shape[1])
    seg = sound[: j - i] * gain
    angle = (pan + 1) * np.pi / 4
    bus[0, i:j] += seg * np.cos(angle)
    bus[1, i:j] += seg * np.sin(angle)


def _reverb(x: np.ndarray, seconds: float = 0.9, wet: float = 0.24, seed: int = 11) -> np.ndarray:
    """Cheap room: convolve with exponentially decaying, softened noise (FFT)."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((2, n)) * np.exp(-t / 0.2)
    for ch in range(2):  # soften the highs so it sounds like a warm room, not a hiss
        ir[ch] = np.convolve(ir[ch], np.ones(8) / 8, mode="same")
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    size = 1 << int(np.ceil(np.log2(x.shape[1] + n)))
    out = np.empty_like(x)
    for ch in range(2):
        out[ch] = np.fft.irfft(np.fft.rfft(x[ch], size) * np.fft.rfft(ir[ch], size), size)[: x.shape[1]]
    return x * (1 - wet * 0.5) + out * wet


def _kick(dur: float = 0.32, soft: bool = False) -> np.ndarray:
    t = np.arange(int(dur * SR)) / SR
    freq = 48 + 90 * np.exp(-t * 28)                       # pitch drop 138 -> 48 Hz
    y = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * (11 if soft else 8))
    y += 0.25 * np.sin(2 * np.pi * 60 * t) * np.exp(-t * 14)
    return (y * np.minimum(t / 0.002, 1.0) * (0.7 if soft else 1.0)).astype(np.float32)


def _noise_burst(rng: np.random.Generator, dur: float, decay: float, hp: bool = True) -> np.ndarray:
    n = rng.standard_normal(int(dur * SR)).astype(np.float32)
    if hp:
        n = np.diff(n, prepend=0.0)                          # one-pole high-pass: brighter, tick-like
    return n * np.exp(-np.arange(len(n)) / SR * decay).astype(np.float32)


def _clap(rng: np.random.Generator, soft: bool = False) -> np.ndarray:
    parts = [_noise_burst(rng, 0.18, 26 if soft else 20) * g for g in (0.7, 0.5, 1.0)]
    out = np.zeros(int(0.2 * SR), np.float32)
    for k, part in enumerate(parts):                         # three quick bursts = a hand clap
        i = int(k * 0.011 * SR)
        out[i:i + len(part)] += part[: len(out) - i]
    return out * (0.35 if soft else 0.5)


def _render_groove(duration: float, style: str, bpm: float | None, seed: int) -> np.ndarray:
    target = CATALOG[style][0]
    bars = max(2, round(duration / (240.0 / target)))
    bpm = bpm or 240.0 * bars / duration
    beat = 60.0 / bpm
    bar_s = 4 * beat
    lofi = style == "lofi"
    n = int(duration * SR)
    rng = np.random.default_rng(seed)
    lead = np.zeros((2, n), np.float32)
    rhythm = np.zeros((2, n), np.float32)
    swing = 0.16 * beat if lofi else 0.0                      # push the off-beat 8ths late

    for b in range(int(np.ceil(duration / bar_s))):
        t0 = b * bar_s
        if t0 >= duration - 0.05:
            break
        chord = "C" if b >= bars - 1 else ("G" if b == bars - 2 else LOOP[b % 4])
        root, intervals = CHORDS[chord]
        tones = [root + 24 + iv for iv in intervals]
        tones6 = tones + [m + 12 for m in tones]
        outro = b == bars - 1
        pad = _pad([_hz(root + 12 + iv) for iv in intervals] + ([_hz(root + 12 + 10)] if lofi else []),
                   min(bar_s + 0.3, duration - t0))
        _place(lead, pad, t0, 0.24 if lofi else 0.1, 0.0)
        # bass: whole-note-ish and soft in lofi, bouncing 1 / "and"-of-2 / 4 in beat
        for pos, g in (((0, 0.4), (2, 0.28)) if lofi else ((0, 0.5), (1.5, 0.38), (3, 0.34))):
            _place(rhythm, _bass(_hz(root + 12), beat * (1.7 if lofi else 0.9)), t0 + pos * beat, g, 0.0)
        # drums
        kick_pos = (0, 2.5) if lofi else (0, 2, 2.5)
        for pos in kick_pos:
            _place(rhythm, _kick(soft=lofi), t0 + pos * beat, 0.5 if lofi else 0.78, 0.0)
        for pos in (1, 3):
            when = t0 + pos * beat + (swing * 0.5 if lofi else 0.0)
            _place(rhythm, _clap(rng, soft=lofi), when, 0.5, 0.05)
        for k in range(8):                                    # 8th-note hats, off-beats louder
            when = t0 + k * beat / 2 + (swing if (lofi and k % 2) else 0.0)
            _place(rhythm, _noise_burst(rng, 0.05, 90), when, 0.07 if k % 2 else 0.04, float(rng.uniform(-0.4, 0.4)))
        if outro:
            for k, m in enumerate((84, 88, 91, 96)):
                _place(lead, _pluck(_hz(m), 2.4, 1.2), t0 + k * beat / 2, 0.4 - 0.04 * k, (-0.3, 0.3)[k % 2])
            for k, m in enumerate((72, 76, 79)):
                _place(lead, _pluck(_hz(m), 2.6, 0.9), t0 + 2 * beat + 0.04 * k, 0.26, (-0.2, 0.0, 0.2)[k])
        else:
            pattern = PATTERNS[(b + (1 if b >= bars - 2 else 0)) % len(PATTERNS)]
            for slot, idx in enumerate(pattern):
                if idx is None or (lofi and slot % 2):        # lofi plays every other slot: space for the voice
                    continue
                when = t0 + slot * beat / 2 + float(rng.normal(0, 0.012 if lofi else 0.004))
                gain = (0.2 if lofi else 0.3) * (1.0 if slot % 2 == 0 else 0.75) * float(rng.uniform(0.9, 1.08))
                _place(lead, _pluck(_hz(tones6[idx] - (12 if lofi else 0)), 1.8, 0.45 if lofi else 1.0), when, gain,
                       (-0.35, 0.35)[slot % 2])
    if lofi:                                                  # vinyl crackle: sparse ticks + a faint hiss
        hiss = (rng.standard_normal(n) * 0.004).astype(np.float32)
        for t in rng.uniform(0, duration - 0.05, int(duration * 6)):
            _place(rhythm, _noise_burst(rng, 0.012, 400) * float(rng.uniform(0.05, 0.14)), float(t), 1.0, float(rng.uniform(-1, 1)))
        rhythm += hiss
    mix = _reverb(lead, wet=0.3 if lofi else 0.2) + rhythm
    fade_in, fade_out = int(0.005 * SR), int(min(0.4, duration / 4) * SR)
    mix[:, :fade_in] *= np.linspace(0, 1, fade_in)
    mix[:, -fade_out:] *= np.linspace(1, 0, fade_out)
    peak = float(np.abs(mix).max()) or 1.0
    return (mix / peak * 0.5).astype(np.float32)


def render_bed(duration: float, style: str = "pastel", bpm: float | None = None, seed: int = 7) -> np.ndarray:
    """The bed as a float32 array of shape (2, n), peak-normalised to -6 dBFS."""
    if style not in STYLES:
        raise ValueError(f"style phải là một trong {STYLES}")
    if style != "pastel":
        return _render_groove(duration, style, bpm, seed)
    bars = max(2, round(duration / 2.3))
    bpm = bpm or 240.0 * bars / duration         # 4 beats per bar; default: the bed is exactly `bars` bars long
    beat = 60.0 / bpm
    bar_s = 4 * beat
    n = int(duration * SR)
    rng = np.random.default_rng(seed)
    lead = np.zeros((2, n), np.float32)           # melody + pad: goes through the reverb
    rhythm = np.zeros((2, n), np.float32)         # bass + shaker: stays dry and tight

    n_bars = int(np.ceil(duration / bar_s))
    for b in range(n_bars):
        t0 = b * bar_s
        if t0 >= duration - 0.05:   # float rounding can add an empty bar after the end
            break
        chord = "C" if b >= bars - 1 else ("G" if b == bars - 2 else LOOP[b % 4])
        root, intervals = CHORDS[chord]
        tones = [root + 24 + iv for iv in intervals]
        tones6 = tones + [m + 12 for m in tones]
        outro = b == bars - 1
        # pad: the whole bar, a little lower and softer
        _place(lead, _pad([_hz(root + 12 + iv) for iv in intervals], min(bar_s + 0.3, duration - t0)), t0, 0.16, 0.0)
        # bass on beats 1 and 3
        for beat_i in (0, 2):
            _place(rhythm, _bass(_hz(root + 12), beat * 1.6), t0 + beat_i * beat, 0.42 if beat_i == 0 else 0.3, 0.0)
        if outro:  # bell arpeggio into a held, ringing chord
            for k, m in enumerate((84, 88, 91, 96)):
                _place(lead, _pluck(_hz(m), 2.4, 1.2), t0 + k * beat / 2, 0.42 - 0.04 * k, (-0.3, 0.3)[k % 2])
            for k, m in enumerate((72, 76, 79)):
                _place(lead, _pluck(_hz(m), 2.6, 0.9), t0 + 2 * beat + 0.04 * k, 0.26, (-0.2, 0.0, 0.2)[k])
        else:
            pattern = PATTERNS[(b + (1 if b >= bars - 2 else 0)) % len(PATTERNS)]
            for slot, idx in enumerate(pattern):
                if idx is None:
                    continue
                accent = 1.0 if slot % 2 == 0 else 0.72
                when = t0 + slot * beat / 2 + float(rng.normal(0, 0.006))
                gain = 0.36 * accent * float(rng.uniform(0.88, 1.08))
                _place(lead, _pluck(_hz(tones6[idx]), 1.6), when, gain, (-0.35, 0.35)[slot % 2])
        # light shaker on every 16th, louder on the off-beats
        for s in range(16):
            tt = t0 + s * beat / 4
            if tt >= duration:
                break
            ticks = rng.standard_normal(int(0.03 * SR)).astype(np.float32)
            ticks = np.diff(ticks, prepend=0.0) * np.exp(-np.arange(len(ticks)) / SR * 150)
            _place(rhythm, ticks, tt, (0.05 if s % 4 == 2 else 0.022), float(rng.uniform(-0.5, 0.5)))

    mix = _reverb(lead) + rhythm
    fade_in, fade_out = int(0.005 * SR), int(min(0.4, duration / 4) * SR)
    mix[:, :fade_in] *= np.linspace(0, 1, fade_in)
    mix[:, -fade_out:] *= np.linspace(1, 0, fade_out)
    peak = float(np.abs(mix).max()) or 1.0
    return (mix / peak * 0.5).astype(np.float32)


def write_wav(path: Path, audio: np.ndarray) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(audio.T, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(pcm.tobytes())
    return path


def make_bed(path: Path, duration: float, style: str = "pastel", bpm: float | None = None, seed: int = 7) -> Path:
    return write_wav(path, render_bed(duration, style, bpm, seed))
