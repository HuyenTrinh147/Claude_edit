import shutil
import subprocess
from pathlib import Path

import pytest

from vedit.config import load_settings

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


@pytest.fixture(scope="session")
def media(tmp_path_factory) -> dict[str, Path]:
    """Small synthetic media files: a 3-shot landscape video with a silent gap, a portrait
    video without audio, a music file, a logo and a subtitle file."""
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg not installed")
    d = tmp_path_factory.mktemp("media")
    ffmpeg("-f", "lavfi", "-i", "testsrc2=s=640x360:r=25:d=2", "-f", "lavfi", "-i", "smptebars=s=640x360:r=25:d=2",
           "-f", "lavfi", "-i", "mandelbrot=s=640x360:r=25", "-f", "lavfi", "-i", "sine=f=300:d=6",
           "-filter_complex", "[2:v]trim=duration=2,setpts=PTS-STARTPTS[m];[0:v][1:v][m]concat=n=3:v=1[v];"
           "[3:a]volume='if(between(t,2.5,3.7),0,1)':eval=frame[a]",
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(d / "land.mp4"))
    ffmpeg("-f", "lavfi", "-i", "smptebars=s=360x640:r=25:d=2", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           str(d / "port.mp4"))
    ffmpeg("-f", "lavfi", "-i", "sine=f=220:d=1.5", "-c:a", "libmp3lame", str(d / "music.mp3"))
    ffmpeg("-f", "lavfi", "-i", "color=c=red:s=64x64:d=1", "-frames:v", "1", str(d / "logo.png"))
    (d / "subs.srt").write_text(
        "1\n00:00:00,200 --> 00:00:01,800\nXin chào các bạn\n\n2\n00:00:04,000 --> 00:00:05,500\nĐồ uống rất ngon\n",
        encoding="utf-8")
    return {p.stem if p.suffix != ".srt" else "srt": p for p in d.iterdir()}


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("VEDIT_KNOWLEDGE_DIR", "VEDIT_PROJECTS_DIR", "VEDIT_ASSETS_DIR"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("VEDIT_FONT", "DejaVu Sans")
    return load_settings(tmp_path)
