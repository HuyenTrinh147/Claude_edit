"""Bring a video into the workspace inbox/ from a Google Drive share link, a YouTube / TikTok /
Facebook / Instagram URL, or a direct download link."""

from __future__ import annotations

import re
import shutil
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .knowledge import slugify

PLATFORM_HOSTS = ("youtube.com", "youtu.be", "tiktok.com", "facebook.com", "fb.watch", "instagram.com",
                  "vimeo.com", "x.com", "twitter.com")


class FetchError(RuntimeError):
    pass


def drive_file_id(url: str) -> str | None:
    """File id from the usual Google Drive share-link shapes."""
    if "drive.google.com" not in url and "docs.google.com" not in url and "drive.usercontent.google.com" not in url:
        return None
    match = re.search(r"/file/d/([\w-]{10,})", url) or re.search(r"[?&]id=([\w-]{10,})", url)
    return match.group(1) if match else None


def classify(url: str) -> str:
    if drive_file_id(url):
        return "drive"
    host = urllib.parse.urlparse(url).netloc.lower()
    if any(host == h or host.endswith("." + h) for h in PLATFORM_HOSTS):
        return "platform"
    if url.startswith(("http://", "https://")):
        return "http"
    return "local"


def _network_hint(url: str, err: Exception) -> FetchError:
    host = urllib.parse.urlparse(url).netloc
    return FetchError(
        f"Không tải được từ {host} ({err}). Nếu đang chạy trong Claude Code trên web, có thể chính sách mạng của "
        f"môi trường đang chặn {host}: thêm tên miền này vào Allowed domains trong cài đặt môi trường.")


def _filename_from_headers(headers, fallback: str) -> str:
    disposition = headers.get("Content-Disposition", "")
    match = re.search(r"filename\*=UTF-8''([^;]+)", disposition) or re.search(r'filename="?([^";]+)"?', disposition)
    return urllib.parse.unquote(match.group(1)) if match else fallback


def _download(url: str, inbox: Path, fallback_name: str) -> Path:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 vedit"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            if "text/html" in resp.headers.get("Content-Type", ""):
                raise FetchError("Link trả về trang web chứ không phải file video — với Google Drive, hãy chia sẻ "
                                 "file ở chế độ 'Bất kỳ ai có đường liên kết'.")
            name = _filename_from_headers(resp.headers, fallback_name)
            stem, suffix = Path(name).stem, Path(name).suffix or ".mp4"
            target = inbox / f"{slugify(stem, 60)}{suffix.lower()}"
            with open(target, "wb") as out:
                shutil.copyfileobj(resp, out, length=1024 * 1024)
    except FetchError:
        raise
    except (urllib.error.URLError, OSError) as e:
        raise _network_hint(url, e) from e
    return target


def fetch_video(source: str, inbox: Path) -> Path:
    """Download (or copy) a video into inbox/ and return its path."""
    inbox.mkdir(parents=True, exist_ok=True)
    kind = classify(source)
    if kind == "local":
        path = Path(source).expanduser()
        if not path.is_file():
            raise FetchError(f"Không tìm thấy file {path}")
        target = inbox / path.name
        if path.resolve() != target.resolve():
            shutil.copy2(path, target)
        return target
    if kind == "drive":
        file_id = drive_file_id(source)
        url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
        return _download(url, inbox, f"drive-{file_id}.mp4")
    if kind == "http":
        return _download(source, inbox, Path(urllib.parse.urlparse(source).path).name or "video.mp4")

    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError

    opts = {
        "quiet": True, "no_warnings": True, "noplaylist": True,
        "format": "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/bv*+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": str(inbox / "%(uploader).30B-%(id)s.%(ext)s"),
        "restrictfilenames": True,
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(source, download=True)
            return Path(ydl.prepare_filename(info)).with_suffix(".mp4")
    except DownloadError as e:
        raise _network_hint(source, e) from e
