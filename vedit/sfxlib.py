"""Sound-effect library: real SFX packs (a folder, a .zip, loose files or a Google Drive link) imported into
``assets/sfx/<pack>/``, analysed (length, loudness, where the hit is) and indexed so agents can search them by
name or category and line the hit up with a frame.

Audio files stay out of git (packs are large and usually not ours to redistribute); each pack's ``index.json``
records where it came from so it can be imported again in a fresh workspace.
"""

from __future__ import annotations

import array
import datetime as dt
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

from .knowledge import slugify, strip_accents
from .media import MediaError, loudness, probe, require_ffmpeg

AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".aac", ".ogg", ".oga", ".flac", ".aif", ".aiff", ".opus", ".wma"}
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
ANALYSIS_RATE = 8000  # Hz, mono — plenty to find a transient

# category -> keywords matched (accent-free, lower case) against folder + file names; first match wins
CATEGORIES: dict[str, tuple[str, ...]] = {
    "whoosh": ("whoosh", "woosh", "swoosh", "swish", "swipe", "swoop", "transition", "chuyen canh", "vut", "luot"),
    "impact": ("impact", "punch", "boom", "bass drop", "drop", "thud", "slam", "hit", "kick", "explosion", "explode",
               "dap", "no ", "dam", "bang", "cinematic"),
    "riser": ("riser", "rise", "uplifter", "build up", "buildup", "tension", "suspense", "cang thang"),
    "pop": ("pop", "bubble", "bloop", "boop", "plop", "blop", "bup"),
    "click": ("click", "tick", "tap", "mouse", "button", "keyboard", "typing", "type", "go phim", "bam"),
    "ding": ("ding", "bell", "chime", "notification", "noti", "chuong", "success", "correct", "ting"),
    "magic": ("magic", "sparkle", "shine", "twinkle", "glitter", "fairy", "lap lanh", "shimmer"),
    "glitch": ("glitch", "static", "digital", "distort", "error", "noise"),
    "camera": ("camera", "shutter", "photo", "chup", "flash"),
    "cash": ("cash", "coin", "money", "register", "kaching", "ka ching", "tien"),
    "fail": ("wrong", "fail", "buzzer", "sai", "trombone", "sad"),
    "funny": ("funny", "cartoon", "boing", "spring", "laugh", "cuoi", "meme", "bruh", "vine", "huh", "troll", "hai"),
    "crowd": ("applause", "clap", "vo tay", "cheer", "crowd", "wow", "omg"),
    "game": ("game", "8bit", "8 bit", "arcade", "level", "jump", "power up", "powerup", "retro", "mario"),
    "scratch": ("scratch", "rewind", "record", "tua"),
}


class SfxError(RuntimeError):
    pass


@dataclass
class Sound:
    name: str          # original file name without extension
    file: str          # path inside the pack folder
    category: str
    duration: float
    peak_db: float | None
    mean_db: float | None
    onset: float       # first moment above -20 dB of the loudest window (s)
    hit: float         # loudest 10 ms window (s) — put this on the frame the sound belongs to

    def path(self, pack_dir: Path) -> Path:
        return pack_dir / self.file


# ---- analysis ---------------------------------------------------------------------------------------

def guess_category(rel_path: str) -> str:
    text = " " + re.sub(r"[^a-z0-9]+", " ", strip_accents(rel_path).lower()) + " "
    for category, words in CATEGORIES.items():
        if any(f" {w} " in text or (len(w) > 4 and w in text) for w in words):
            return category
    return "other"


def envelope(path: Path) -> list[float]:
    """RMS per 10 ms of a mono 8 kHz decode."""
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-vn", "-ac", "1",
                           "-ar", str(ANALYSIS_RATE), "-f", "s16le", "-"], capture_output=True)
    samples = array.array("h")
    samples.frombytes(proc.stdout[: len(proc.stdout) // 2 * 2])
    hop = ANALYSIS_RATE // 100
    out = []
    for i in range(0, len(samples), hop):
        chunk = samples[i:i + hop]
        out.append((sum(s * s for s in chunk) / max(len(chunk), 1)) ** 0.5 / 32768)
    return out


def analyse(path: Path, rel: str) -> Sound:
    info = probe(path)
    env = envelope(path)
    loud = loudness(path)
    if env and max(env) > 0:
        top = max(range(len(env)), key=env.__getitem__)
        onset = next(i for i, v in enumerate(env) if v >= env[top] * 0.1)
        hit, onset_s = top / 100, onset / 100
    else:
        hit = onset_s = 0.0
    return Sound(name=Path(rel).stem, file=rel, category=guess_category(rel), duration=round(info.duration, 3),
                 peak_db=loud.get("peak_db"), mean_db=loud.get("mean_db"), onset=round(onset_s, 2), hit=round(hit, 2))


# ---- import -----------------------------------------------------------------------------------------

def _zip_name(info: zipfile.ZipInfo) -> str:
    """Zips made on Windows/macOS without the UTF-8 flag store names as raw bytes Python reads as cp437."""
    if info.flag_bits & 0x800:
        return info.filename
    try:
        return info.filename.encode("cp437").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return info.filename


def _extract_zip(path: Path, dest: Path) -> None:
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            name = _zip_name(info)
            if info.is_dir() or name.startswith("__MACOSX/") or "/." in "/" + name:
                continue
            target = (dest / name).resolve()
            if dest.resolve() not in target.parents:  # no path traversal out of the temp dir
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)


def _download_drive(url: str, dest: Path) -> None:
    try:
        import gdown  # type: ignore
    except ImportError:
        raise SfxError("cần gdown để tải thư mục Google Drive: pip install gdown") from None
    try:
        if "/folders/" in url:
            got = gdown.download_folder(url, output=str(dest), quiet=True, use_cookies=False, remaining_ok=True)
        else:
            got = gdown.download(url, output=str(dest) + "/", quiet=True, use_cookies=False, fuzzy=True)
    except Exception as exc:  # gdown raises many kinds of errors, incl. network ones
        raise SfxError(f"không tải được từ Google Drive ({exc}). Nếu mạng chặn drive.google.com / "
                       "drive.usercontent.google.com, thêm hai tên miền đó vào Allowed domains của môi trường "
                       "hoặc tải file .zip thẳng vào chat.") from None
    if not got:
        raise SfxError("Google Drive không trả về file nào (thư mục trống, riêng tư, hoặc mạng bị chặn)")


def _collect(root: Path) -> list[Path]:
    files = []
    for f in sorted(root.rglob("*")):
        if not f.is_file() or f.name.startswith("."):
            continue
        ext = f.suffix.lower()
        if ext == ".zip":
            inner = f.with_name(f.stem + "_unzipped")
            _extract_zip(f, inner)
            files += _collect(inner)
        elif ext in AUDIO_EXTS or ext in VIDEO_EXTS:
            files.append(f)
    return files


def _safe_rel(rel: Path) -> str:
    parts = [slugify(p, 60) for p in rel.parent.parts] + [slugify(rel.stem, 80)]
    return "/".join(p for p in parts if p)


def import_pack(sources: list[str], sfx_dir: Path, name: str | None = None, log=print) -> tuple[Path, list[Sound]]:
    """Copy every audio file (and the sound of every video file) from `sources` into sfx_dir/<pack>/ and write
    the pack's index.json. Re-importing a pack replaces it."""
    require_ffmpeg()
    with tempfile.TemporaryDirectory(prefix="vedit-sfx-") as tmp:
        staging = Path(tmp)
        for i, source in enumerate(sources):
            slot = staging / f"src{i}"
            slot.mkdir()
            if re.match(r"https?://", source):
                if "drive.google.com" not in source and "docs.google.com" not in source:
                    raise SfxError("chỉ hỗ trợ link Google Drive; nguồn khác hãy tải về rồi đưa đường dẫn")
                _download_drive(source, slot)
                continue
            path = Path(source).expanduser()
            if not path.exists():
                raise SfxError(f"không thấy {path}")
            if path.is_dir():
                shutil.copytree(path, slot / path.name)
            elif path.suffix.lower() == ".zip":
                _extract_zip(path, slot / path.stem)
            else:
                shutil.copy2(path, slot / path.name)
        files: list[tuple[Path, Path]] = []   # (file, path relative to its source, minus wrapper folders)
        wrappers: list[str] = []
        for slot in sorted(staging.glob("src*")):
            found = _collect(slot)
            rels = [f.relative_to(slot) for f in found]
            while rels and all(len(r.parts) > 1 for r in rels) and len({r.parts[0] for r in rels}) == 1:
                wrappers.append(rels[0].parts[0])          # e.g. zip name, then the pack's own top folder
                rels = [Path(*r.parts[1:]) for r in rels]
            files += list(zip(found, rels))
        if not files:
            raise SfxError("không có file âm thanh / video nào trong nguồn")
        default = wrappers[-1] if wrappers and len(sources) == 1 else (
            "drive" if re.match(r"https?://", sources[0]) else Path(sources[0]).stem)
        pack = slugify(name or default, 40)
        pack_dir = sfx_dir / pack
        if pack_dir.exists():
            shutil.rmtree(pack_dir)
        pack_dir.mkdir(parents=True)
        sounds, used = [], set()
        for f, rel in files:
            base = _safe_rel(rel) or "sfx"
            key, n = base, 2
            while key in used:
                key, n = f"{base}-{n}", n + 1
            used.add(key)
            ext = f.suffix.lower()
            target = pack_dir / (key + (".wav" if ext in VIDEO_EXTS else ext))
            target.parent.mkdir(parents=True, exist_ok=True)
            if ext in VIDEO_EXTS:
                proc = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(f), "-vn",
                                       "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(target)],
                                      capture_output=True)
                if proc.returncode or not target.exists():
                    log(f"  - bỏ qua {rel} (không có tiếng)")
                    continue
            else:
                shutil.copy2(f, target)
            try:
                sound = analyse(target, str(target.relative_to(pack_dir)))
            except MediaError:
                target.unlink(missing_ok=True)
                log(f"  - bỏ qua {rel} (không đọc được)")
                continue
            sound.name = rel.stem
            sounds.append(sound)
    index = {"pack": pack, "source": sources, "imported": dt.datetime.now().isoformat(timespec="seconds"),
             "count": len(sounds), "sounds": [asdict(s) for s in sounds]}
    (pack_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    return pack_dir, sounds


# ---- library ----------------------------------------------------------------------------------------

def library(sfx_dir: Path) -> list[tuple[Path, Sound]]:
    """Every indexed sound whose file is present: (pack folder, sound)."""
    out = []
    for index in sorted(Path(sfx_dir).glob("*/index.json")):
        data = json.loads(index.read_text(encoding="utf-8"))
        for raw in data.get("sounds", []):
            sound = Sound(**raw)
            if sound.path(index.parent).exists():
                out.append((index.parent, sound))
    return out


def missing_packs(sfx_dir: Path) -> list[tuple[str, list[str]]]:
    """Packs whose index exists but whose audio is gone (fresh workspace): (pack, sources to re-import)."""
    out = []
    for index in sorted(Path(sfx_dir).glob("*/index.json")):
        data = json.loads(index.read_text(encoding="utf-8"))
        files = [index.parent / s["file"] for s in data.get("sounds", [])]
        if files and not any(f.exists() for f in files):
            out.append((data.get("pack", index.parent.name), data.get("source", [])))
    return out


def search(sfx_dir: Path, query: str = "", category: str | None = None, limit: int = 40) -> list[tuple[Path, Sound]]:
    terms = [t for t in re.findall(r"[a-z0-9]+", strip_accents(query).lower()) if t]
    scored = []
    for pack_dir, sound in library(sfx_dir):
        if category and sound.category != category:
            continue
        hay = strip_accents(f"{sound.name} {sound.file} {sound.category}").lower()
        score = sum(hay.count(t) for t in terms) if terms else 1
        if score:
            scored.append((score, sound.duration, pack_dir, sound))
    scored.sort(key=lambda s: (-s[0], s[1]))
    return [(p, s) for _, _, p, s in scored[:limit]]


def describe(pack_dir: Path, sound: Sound) -> str:
    peak = f"peak {sound.peak_db:.1f} dB" if sound.peak_db is not None else ""
    return (f"{sound.path(pack_dir)}  [{sound.category}]  {sound.duration:.2f}s  đỉnh tiếng @{sound.hit:.2f}s  {peak}"
            f"  — {sound.name}")
