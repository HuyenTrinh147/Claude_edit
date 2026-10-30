"""YouTube search, metadata and transcripts through yt-dlp (no API key needed)."""

from __future__ import annotations

import json
import re
import urllib.request

from yt_dlp import YoutubeDL

_OPTS = {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True}


def search(query: str, limit: int = 8) -> list[dict]:
    with YoutubeDL({**_OPTS, "extract_flat": "in_playlist"}) as ydl:
        info = ydl.extract_info(f"ytsearch{min(limit, 20)}:{query}", download=False)
    results = []
    for e in (info or {}).get("entries", []) or []:
        if not e:
            continue
        results.append({
            "title": e.get("title"),
            "channel": e.get("channel") or e.get("uploader"),
            "views": e.get("view_count"),
            "duration": e.get("duration"),
            "url": e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}",
        })
    return results


def _pick_caption(info: dict, langs: tuple[str, ...]) -> tuple[str, str] | None:
    for key in ("subtitles", "automatic_captions"):
        tracks = info.get(key) or {}
        for lang in langs:
            for code, formats in tracks.items():
                if code == lang or code.startswith(f"{lang}-"):
                    by_ext = {f.get("ext"): f.get("url") for f in formats}
                    for ext in ("json3", "vtt"):
                        if by_ext.get(ext):
                            return ext, by_ext[ext]
    return None


def _caption_text(ext: str, url: str) -> str:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
        raw = r.read().decode("utf-8", "replace")
    if ext == "json3":
        events = json.loads(raw).get("events", [])
        lines = []
        for ev in events:
            text = "".join(s.get("utf8", "") for s in ev.get("segs", []) or []).strip()
            if text:
                lines.append(f"[{ev.get('tStartMs', 0) / 1000:.0f}s] {text}")
        return "\n".join(lines)
    lines: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or "-->" in line or line.isdigit() or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line and (not lines or lines[-1] != line):  # auto-captions repeat the previous line
            lines.append(line)
    return "\n".join(lines)


def video_info(url: str, transcript: bool = True, langs: tuple[str, ...] = ("vi", "en"),
               max_chars: int = 15000) -> dict:
    with YoutubeDL(_OPTS) as ydl:
        info = ydl.extract_info(url, download=False) or {}
    result = {
        "title": info.get("title"),
        "channel": info.get("channel") or info.get("uploader"),
        "upload_date": info.get("upload_date"),
        "duration": info.get("duration"),
        "views": info.get("view_count"),
        "likes": info.get("like_count"),
        "tags": (info.get("tags") or [])[:20],
        "chapters": [{"start": c.get("start_time"), "title": c.get("title")} for c in info.get("chapters") or []],
        "description": (info.get("description") or "")[:3000],
        "url": info.get("webpage_url") or url,
    }
    if transcript:
        picked = _pick_caption(info, langs)
        if picked:
            text = _caption_text(*picked)
            result["transcript"] = text[:max_chars] + ("\n[... cắt bớt]" if len(text) > max_chars else "")
        else:
            result["transcript"] = None
    return result
