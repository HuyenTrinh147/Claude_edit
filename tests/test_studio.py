"""Studio dashboard: step inference from project files + notes, gate notes, and the HTTP safety rules."""
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from vedit import studio
from vedit.config import load_settings
from vedit.project import Project


@pytest.fixture
def settings(tmp_path, monkeypatch):
    monkeypatch.setenv("VEDIT_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("VEDIT_KNOWLEDGE_DIR", str(tmp_path / "knowledge"))
    s = load_settings()
    s.projects_dir.mkdir(parents=True, exist_ok=True)
    return s


def make_project(settings, tmp_path) -> Project:
    video = tmp_path / "v.mp4"
    video.write_bytes(b"x")
    return Project.create(settings, video, "demo")


def steps(state):
    return {s["key"]: s["status"] for s in state["steps"]}


def test_new_project_waits_for_source(settings, tmp_path):
    st = studio.project_state(make_project(settings, tmp_path))
    assert st["current"] == "source" and steps(st)["source"] == "active"
    assert "vedit analyze" in st["prompt"]


def test_concepts_open_gate_one_then_choice_moves_on(settings, tmp_path):
    p = make_project(settings, tmp_path)
    (p.analysis_dir).mkdir(parents=True)
    (p.analysis_dir / "analysis.json").write_text("{}", encoding="utf-8")
    p.script_dir.mkdir()
    (p.script_dir / "concepts.json").write_text(json.dumps({"concepts": [
        {"name": "A", "idea": "ý A"}, {"name": "B", "idea": "ý B"}]}), encoding="utf-8")
    st = studio.project_state(p)
    assert st["current"] == "cong1" and st["waiting"] and [c["name"] for c in st["concepts"]] == ["A", "B"]

    prompt = studio.add_gate_note(settings, p.slug, "cong1", "giữ nhạc nhẹ", 2)
    assert "«B»" in prompt and "/kich-ban" in prompt
    st = studio.project_state(p)
    assert steps(st)["cong1"] == "done" and st["current"] == "kichban"   # chosen, plan not written yet
    assert "bước 2" in st["prompt"]


def test_gate_two_approve_and_fix(settings, tmp_path):
    p = make_project(settings, tmp_path)
    p.plan_path.write_text("{}", encoding="utf-8")
    p.renders_dir.mkdir()
    (p.renders_dir / "final.mp4").write_bytes(b"x")
    p.note("critic ĐẠT", "Agent 3")
    st = studio.project_state(p)
    assert st["current"] == "cong2" and st["waiting"]

    with pytest.raises(ValueError):
        studio.add_gate_note(settings, p.slug, "cong2-fix", "")            # a fix needs words
    assert "/sua-video" in studio.add_gate_note(settings, p.slug, "cong2-fix", "chữ to hơn")
    assert studio.project_state(p)["current"] == "cong2"                      # still open after a fix request
    studio.add_gate_note(settings, p.slug, "cong2-ok")
    st = studio.project_state(p)
    assert st["finished"] and st["prompt"] == ""
    assert "Duyệt bản xuất" in p.memory_path.read_text(encoding="utf-8")


def test_unknown_gate_and_concept_rejected(settings, tmp_path):
    p = make_project(settings, tmp_path)
    with pytest.raises(ValueError):
        studio.add_gate_note(settings, p.slug, "nope")
    with pytest.raises(ValueError):
        studio.add_gate_note(settings, p.slug, "cong1", "", 9)


def test_http_rules(settings, tmp_path):
    p = make_project(settings, tmp_path)
    p.renders_dir.mkdir()
    (p.renders_dir / "final.jpg").write_bytes(b"jpg")
    (settings.projects_dir / "secret.txt").write_text("s", encoding="utf-8")
    server = ThreadingHTTPServer(("127.0.0.1", 0), studio.make_handler(settings))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"

    def call(path, data=None, headers=None):
        req = urllib.request.Request(base + path, data=data, headers=headers or {})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, b""
    try:
        assert call("/")[0] == 200
        assert json.loads(call("/api/overview")[1])["stats"]["projects"] == 1
        assert call(f"/media/{p.slug}/renders/final.jpg") == (200, b"jpg")
        assert call(f"/media/{p.slug}/renders/../../secret.txt")[0] == 404   # no path escape
        assert call("/media/secret.txt")[0] == 404
        body = json.dumps({"slug": p.slug, "gate": "cong2-ok"}).encode()
        assert call("/api/gate", body)[0] == 403                              # no X-Studio header
        assert call("/api/gate", body, {"X-Studio": "1", "Origin": "https://evil.example"})[0] == 403
        assert call("/api/gate", body, {"X-Studio": "1"})[0] == 200
    finally:
        server.shutdown()
        server.server_close()


def test_text_check_blocks_before_render_and_music_only_with_files(settings, tmp_path):
    import os
    import time

    p = make_project(settings, tmp_path)
    p.analysis_dir.mkdir(parents=True)
    (p.analysis_dir / "analysis.json").write_text("{}", encoding="utf-8")
    # no music files: the music step is optional and never blocks; with files it comes right after the source step
    assert studio.project_state(p)["current"] == "kichban"
    assert studio.project_state(p, music_files=3)["current"] == "nhac"
    p.note("chọn nhạc: demo 120 BPM", "Agent 5")
    assert studio.project_state(p, music_files=3)["current"] == "kichban"

    p.plan_path.write_text("{}", encoding="utf-8")
    st = studio.project_state(p)
    assert st["current"] == "soatchu" and "/soat-chu" in st["prompt"]        # plan written, text not checked yet

    report = p.script_dir / "textcheck.json"
    p.script_dir.mkdir(exist_ok=True)
    report.write_text(json.dumps({"errors": 2, "warnings": 0}), encoding="utf-8")
    st = studio.project_state(p)
    assert st["current"] == "soatchu" and "2 lỗi" in st["headline"]
    assert {s["key"]: s.get("badge") for s in st["steps"]}["soatchu"] == "2 lỗi"

    report.write_text(json.dumps({"errors": 0, "warnings": 1}), encoding="utf-8")
    assert studio.project_state(p)["current"] == "dung"
    os.utime(p.plan_path, (time.time() + 10, time.time() + 10))                # plan edited after the check: stale
    assert studio.project_state(p)["current"] == "soatchu"


def test_room_lists_sources_agents_skills_and_director_roundtrip(settings, tmp_path, monkeypatch):
    import subprocess

    root = tmp_path / "repo"
    (root / ".claude" / "agents").mkdir(parents=True)
    (root / ".claude" / "skills" / "edit-demo").mkdir(parents=True)
    (root / ".claude" / "agents" / "video-x.md").write_text("---\nname: video-x\ndescription: agent thử nghiệm\ntools: Bash\n---\nvedit\n", encoding="utf-8")
    (root / ".claude" / "skills" / "edit-demo" / "SKILL.md").write_text("---\nname: edit-demo\ndescription: skill thử\nargument-hint: <x>\n---\n", encoding="utf-8")
    settings.root = root
    p = make_project(settings, tmp_path)
    (p.dir / "assets").mkdir()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=s=160x284:d=1:r=10", "-pix_fmt", "yuv420p",
                    str(p.dir / "assets" / "a.mp4")], check=True)
    (p.dir / "footage.md").write_text("| a.mp4 | 1 s | cận nhân bánh |\n", encoding="utf-8")

    r = studio.room(settings, p.slug)
    assert [c["file"] for c in r["clips"]] == ["a.mp4"] and r["clips"][0]["desc"] == "cận nhân bánh"
    assert (p.dir / "analysis" / "thumbs" / "a.jpg").exists() and r["clips"][0]["thumb"].endswith("/a.jpg")
    assert [a["name"] for a in r["agents"]] == ["video-x"] and r["skills"][0]["group"].startswith("Công thức")

    body = {"clips": [{"file": "a.mp4", "note": "dùng 0–1 s"}], "idea": "mở 4 khung", "avoid": "nền chữ",
            "agents": ["video-x", "khong-co"], "skills": ["edit-demo"], "announce": True}
    out = studio.save_director(settings, p.slug, body)
    assert out["director"]["agents"] == ["video-x"]                       # unknown names are dropped
    assert "director.json" in out["prompt"] and "1) a.mp4 (dùng 0–1 s)" in out["prompt"] and "«mở 4 khung»" in out["prompt"]
    assert studio.load_director(p)["clips"][0]["note"] == "dùng 0–1 s"
    assert "Chỉ đạo (director.json)" in p.memory_path.read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        studio.save_director(settings, p.slug, {"clips": [{"file": "../../etc/passwd"}]})   # only the project's own sources
