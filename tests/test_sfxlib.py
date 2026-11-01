"""Real SFX packs: import from zip / folder / video, categories, hit detection, search, fresh-workspace hint."""

import json
import zipfile

import pytest

from conftest import ffmpeg, needs_ffmpeg
from vedit.sfxlib import SfxError, guess_category, import_pack, library, missing_packs, search


def test_category_guess_uses_folder_and_file_names():
    assert guess_category("Whoosh/whoosh 01.wav") == "whoosh"
    assert guess_category("Âm thanh/Tiếng vỗ tay.mp3") == "crowd"
    assert guess_category("Hiệu ứng/Chuông báo.wav") == "ding"
    assert guess_category("Cinematic Boom.wav") == "impact"
    assert guess_category("random_take_7.wav") == "other"


@needs_ffmpeg
def test_import_zip_with_folders_videos_and_vietnamese_names(tmp_path):
    src = tmp_path / "BASIC SFX"
    (src / "Whoosh").mkdir(parents=True)
    (src / "Vui").mkdir()
    ffmpeg("-f", "lavfi", "-i", "anoisesrc=d=0.8:c=pink:a=0.4,afade=t=in:d=0.5:curve=exp,afade=t=out:st=0.5:d=0.3",
           str(src / "Whoosh" / "Whoosh 01.wav"))
    ffmpeg("-f", "lavfi", "-i", "sine=f=880:d=0.6", str(src / "Vui" / "Tiếng chuông ding.mp3"))
    ffmpeg("-f", "lavfi", "-i", "color=c=black:s=64x64:d=1", "-f", "lavfi", "-i", "sine=f=110:d=1", "-shortest",
           str(src / "Vui" / "boom impact.mp4"))
    ffmpeg("-f", "lavfi", "-i", "color=c=black:s=64x64:d=1", str(src / "Vui" / "silent clip.mp4"))
    archive = tmp_path / "pack.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for f in src.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(tmp_path))
    sfx_dir = tmp_path / "assets" / "sfx"
    pack_dir, sounds = import_pack([str(archive)], sfx_dir, log=lambda *_: None)
    assert pack_dir.name == "basic-sfx"                     # named after the pack's own folder
    by_name = {s.name: s for s in sounds}
    assert set(by_name) == {"Whoosh 01", "Tiếng chuông ding", "boom impact"}   # silent video skipped
    assert by_name["Whoosh 01"].category == "whoosh" and 0.35 < by_name["Whoosh 01"].hit < 0.65
    assert by_name["boom impact"].file.endswith(".wav")      # sound pulled out of the video
    assert (pack_dir / by_name["Tiếng chuông ding"].file).exists()
    index = json.loads((pack_dir / "index.json").read_text(encoding="utf-8"))
    assert index["count"] == 3 and index["source"] == [str(archive)]
    assert [s.name for _, s in search(sfx_dir, "chuông")] == ["Tiếng chuông ding"]
    assert [s.name for _, s in search(sfx_dir, category="whoosh")] == ["Whoosh 01"]
    # fresh workspace: index committed, audio gone -> tell how to re-import
    for _, s in library(sfx_dir):
        (pack_dir / s.file).unlink()
    assert missing_packs(sfx_dir) == [("basic-sfx", [str(archive)])]
    assert library(sfx_dir) == []


@needs_ffmpeg
def test_import_rejects_empty_and_non_drive_links(tmp_path):
    (tmp_path / "empty").mkdir()
    with pytest.raises(SfxError, match="không có file"):
        import_pack([str(tmp_path / "empty")], tmp_path / "sfx")
    with pytest.raises(SfxError, match="Google Drive"):
        import_pack(["https://example.com/pack.zip"], tmp_path / "sfx")
