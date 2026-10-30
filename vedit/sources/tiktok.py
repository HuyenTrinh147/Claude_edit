"""TikTok video metadata via yt-dlp. TikTok has no public search/trend API, so trend discovery
goes through web search (e.g. TikTok Creative Center pages); this module reads specific videos."""

from __future__ import annotations

import re

from yt_dlp import YoutubeDL


def hashtags(text: str) -> list[str]:
    return sorted(set(re.findall(r"#[\wÀ-ỹ]+", text or "")))


def video_info(url: str) -> dict:
    with YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False) or {}
    description = info.get("description") or info.get("title") or ""
    return {
        "author": info.get("uploader") or info.get("creator"),
        "description": description[:1500],
        "hashtags": hashtags(description),
        "music": {"track": info.get("track"), "artist": info.get("artist")},
        "duration": info.get("duration"),
        "views": info.get("view_count"),
        "likes": info.get("like_count"),
        "comments": info.get("comment_count"),
        "shares": info.get("repost_count"),
        "upload_date": info.get("upload_date"),
        "url": info.get("webpage_url") or url,
    }
