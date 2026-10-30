import pytest

from vedit.knowledge import KnowledgeBase, slugify, strip_accents


def test_slugify_vietnamese():
    assert slugify("Công thức Hook 3 giây đầu!") == "cong-thuc-hook-3-giay-dau"
    assert strip_accents("Đường đi") == "Duong di"


def test_save_search_get(tmp_path):
    kb = KnowledgeBase(tmp_path)
    kb.save("Cắt khoảng lặng tự động", "ffmpeg", "Dùng silencedetect để tìm khoảng lặng.", ["silence", "jump cut"],
            ["https://ffmpeg.org"])
    kb.save("Hook mở đầu", "scripting", "Câu hỏi gây tò mò trong 3 giây đầu.", ["hook"], ["https://example.com"])

    hits = kb.search("khoang lang")  # accent-insensitive
    assert hits[0][0].ref == "ffmpeg/cat-khoang-lang-tu-dong"
    note = kb.get("cat-khoang-lang-tu-dong")
    assert note and note.tags == ["silence", "jump cut"] and note.sources == ["https://ffmpeg.org"]
    assert note.body.startswith("# Cắt khoảng lặng tự động")
    assert kb.get("scripting/hook-mo-dau").title == "Hook mở đầu"
    index = (tmp_path / "INDEX.md").read_text(encoding="utf-8")
    assert "ffmpeg/cat-khoang-lang-tu-dong.md" in index
    assert "scripting/hook-mo-dau" in kb.overview()


def test_save_overwrites_same_title(tmp_path):
    kb = KnowledgeBase(tmp_path)
    kb.save("Ghi chú", "trends", "v1", [], ["a"])
    kb.save("Ghi chú", "trends", "v2", [], ["b"])
    notes = kb.notes()
    assert len(notes) == 1 and "v2" in notes[0].body


def test_invalid_category(tmp_path):
    with pytest.raises(ValueError):
        KnowledgeBase(tmp_path).save("x", "random", "y")
