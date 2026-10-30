import pytest

from vedit.config import load_settings
from vedit.fetch import FetchError, classify, drive_file_id, fetch_video


@pytest.mark.parametrize("url, expected", [
    ("https://drive.google.com/file/d/1AbC_dEf-GhIjKlMn/view?usp=sharing", "1AbC_dEf-GhIjKlMn"),
    ("https://drive.google.com/open?id=1AbC_dEf-GhIjKlMn", "1AbC_dEf-GhIjKlMn"),
    ("https://drive.google.com/uc?export=download&id=1AbC_dEf-GhIjKlMn", "1AbC_dEf-GhIjKlMn"),
    ("https://example.com/file/d/1AbC_dEf-GhIjKlMn", None),
])
def test_drive_file_id(url, expected):
    assert drive_file_id(url) == expected


@pytest.mark.parametrize("source, kind", [
    ("https://drive.google.com/file/d/1AbC_dEf-GhIjKlMn/view", "drive"),
    ("https://www.tiktok.com/@user/video/7300000000000000000", "platform"),
    ("https://youtu.be/dQw4w9WgXcQ", "platform"),
    ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "platform"),
    ("https://cdn.example.com/clip.mp4", "http"),
    ("~/Videos/a.mp4", "local"),
])
def test_classify(source, kind):
    assert classify(source) == kind


def test_fetch_local_copies_into_inbox(media, tmp_path):
    path = fetch_video(str(media["land"]), tmp_path / "inbox")
    assert path == tmp_path / "inbox" / "land.mp4" and path.stat().st_size == media["land"].stat().st_size
    with pytest.raises(FetchError):
        fetch_video(str(tmp_path / "missing.mp4"), tmp_path / "inbox")


def test_default_root_finds_workspace_from_subdirectory(tmp_path, monkeypatch):
    monkeypatch.delenv("VEDIT_HOME", raising=False)
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "projects" / "x").mkdir(parents=True)
    monkeypatch.chdir(tmp_path / "projects" / "x")
    settings = load_settings()
    assert settings.root == tmp_path.resolve() and settings.inbox_dir == tmp_path.resolve() / "inbox"
