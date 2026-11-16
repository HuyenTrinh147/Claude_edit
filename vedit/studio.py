"""Studio: a local dashboard over `projects/` — where each project is in the agent loop, the approval gates, and a
ready-made prompt to paste into Claude Code for the next step.

Nothing here calls an AI. State is inferred from the files and from `project.md` (the same notes the agents read), so
the page and the agents never disagree. Writes are limited to `project.md` notes (the gate buttons). The server binds
to 127.0.0.1 only.
"""

from __future__ import annotations

import json
import mimetypes
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .config import Settings
from .beat import AUDIO_EXTS
from .project import Project

UI_FILE = Path(__file__).with_name("studio_ui.html")
NOTE_RE = re.compile(r"^- (\d{4}-\d\d-\d\d \d\d:\d\d) · \*\*(.+?)\*\*: (.*)$")
APPROVE_PREFIX = "Duyệt bản xuất"
CHOSEN_PREFIX = "Chọn hướng"

# (key, label, who) — the loop shown on the page, in order
STEPS = (
    ("giao", "Giao việc", "Điều phối"),
    ("source", "Xem source", "vedit analyze"),
    ("nhac", "Chọn nhạc", "Agent 5"),
    ("noidung", "Nội dung", "Agent 4"),
    ("kichban", "Kịch bản", "Agent 2"),
    ("cong1", "Cổng 1", "bạn chọn hướng"),
    ("soatchu", "Soát chữ", "Agent 6"),
    ("dung", "Dựng", "Agent 3"),
    ("phanbien", "Phản biện", "video-critic"),
    ("cong2", "Cổng 2", "bạn duyệt bản"),
    ("ghiso", "Ghi sổ", "vedit note"),
)
GATES = ("cong1", "cong2")


def parse_notes(project: Project) -> list[dict]:
    path = project.memory_path
    if not path.exists():
        return []
    notes = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = NOTE_RE.match(line)
        if m:
            notes.append({"time": m.group(1), "kind": m.group(2), "text": m.group(3)})
    return notes


def _is_user(note: dict) -> bool:
    return note["kind"].strip().lower() in ("người dùng", "user")


def _load_concepts(project: Project) -> list[dict]:
    path = project.script_dir / "concepts.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    items = data.get("concepts", []) if isinstance(data, dict) else data
    return [{"index": i + 1, "name": str(c.get("name", f"Hướng {i + 1}")),
             "idea": str(c.get("idea", "")), "style": str(c.get("style", ""))}
            for i, c in enumerate(items) if isinstance(c, dict)]


def _final_video(project: Project) -> Path | None:
    finals = sorted(project.renders_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime) if project.renders_dir.exists() else []
    finals = [p for p in finals if p.stem != "preview"]
    return finals[-1] if finals else None


def _plan_has_music(project: Project) -> bool:
    try:
        plan = json.loads(project.plan_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return any(isinstance(a, dict) and a.get("role", "music") == "music" and not str(a.get("path", "")).startswith("sfx:")
               for a in plan.get("audio", []))


def _textcheck(project: Project) -> dict | None:
    """The last `vedit textcheck` report if it is newer than the plan: {"errors": n, "warnings": n}."""
    path = project.script_dir / "textcheck.json"
    if not path.exists() or not project.plan_path.exists() or path.stat().st_mtime < project.plan_path.stat().st_mtime:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {"errors": int(data.get("errors", 0)), "warnings": int(data.get("warnings", 0))}
    except (OSError, ValueError, TypeError):
        return None


def project_state(project: Project, music_files: int = 0) -> dict:
    """Where the project is in the loop: step statuses, the open gate, the prompt to paste for the next step.

    `music_files` = how many tracks sit in assets/music: the music step only blocks the loop when there is something to pick."""
    notes = parse_notes(project)
    slug = project.slug
    concepts = _load_concepts(project)
    final = _final_video(project)
    has_plan = project.plan_path.exists()
    chosen = has_plan or any(_is_user(n) and (n["text"].startswith(CHOSEN_PREFIX) or
                                               ("chọn" in n["text"].lower() and "hướng" in n["text"].lower()))
                             for n in notes)
    critic = any("phản biện" in n["kind"].lower() or "critic" in n["kind"].lower()
                 or "critic" in n["text"].lower() or "phản biện" in n["text"].lower() for n in notes)
    approved = any(_is_user(n) and n["text"].startswith(APPROVE_PREFIX) for n in notes)

    tc = _textcheck(project)
    done = {
        "giao": True,
        # a plan / concepts / render can only exist after the source was looked at (some projects have no analysis.json)
        "source": project.analysis() is not None or has_plan or bool(concepts) or final is not None,
        "nhac": (project.dir / "audio" / "music.md").exists() or _plan_has_music(project)
                or any("agent 5" in n["kind"].lower() or "chọn nhạc" in n["kind"].lower() for n in notes),
        "noidung": (project.dir / "content" / "post.md").exists(),
        "kichban": has_plan or bool(concepts),
        "cong1": chosen,
        "soatchu": tc is not None and tc["errors"] == 0,
        "dung": final is not None,
        "phanbien": final is not None and critic,
        "cong2": approved,
        "ghiso": bool(notes),
    }
    # (prompt, what is open) for the first unfinished required step
    prompts = {
        "source": ("Phân tích video của dự án {slug}: chạy `vedit analyze` rồi xem sheet các khung hình, tóm tắt cho tôi "
                   "video quay gì, tiếng gốc thế nào.", "Xem source"),
        "kichban": ("/kich-ban bước 1 cho dự án {slug}: đề xuất 2–3 hướng dựng khác hẳn nhau vào script/concepts.md, "
                    "ghi giả định về nền tảng và độ dài. Chưa viết EditPlan.", "Agent 2 đề xuất hướng"),
        "nhac": ("/chon-nhac cho dự án {slug}: Agent 5 chọn nhạc nền từ assets/music (vedit bpm), ghi audio/music.md "
                 "gồm bài chọn, BPM, điểm vào, âm lượng và lưới beat.", "Agent 5 chọn nhạc"),
        "cong1": ("", "Bạn chọn hướng dựng"),
        "soatchu": ("/soat-chu dự án {slug}: Agent 6 chạy vedit textcheck và đọc chính tả, đối chiếu lời; còn LỖI thì "
                    "sửa trong EditPlan rồi soát lại (tối đa 2 vòng).",
                    "Sửa lỗi chữ" + (f" ({tc['errors']} lỗi)" if tc and tc["errors"] else "") if tc else "Agent 6 soát chữ"),
        "dung": ("/sua-video dựng dự án {slug} từ edit_plan.json: render bản xem trước, kiểm tra mọi điểm cắt, "
                 "rồi xuất renders/final.mp4.", "Agent 3 dựng"),
        "phanbien": ("Cho video-critic soi renders/final.mp4 của dự án {slug} theo hướng đã chọn trong project.md "
                     "và gu người dùng; CẦN SỬA thì video-editor sửa (tối đa 2 vòng).", "Phản biện soi bản xuất"),
        "cong2": ("", "Bạn duyệt bản xuất"),
    }
    if chosen and not has_plan:
        prompts["kichban"] = ("/kich-ban bước 2 cho dự án {slug}: viết script/script.md và edit_plan.json theo hướng đã "
                              "chọn trong project.md (đọc cả profile/gu-nguoi-dung.md). Chưa render.", "Agent 2 viết kịch bản")
        done["kichban"] = False

    # the music step blocks only before the plan exists and only when there is music to pick from;
    # the text check blocks between the plan and the render
    blockers = ["source"] + (["nhac"] if music_files and not has_plan else []) + ["kichban", "cong1"] \
        + (["soatchu"] if has_plan and final is None else []) + ["dung", "phanbien", "cong2"]
    current = next((k for k in blockers if not done[k]), None)
    # the optional content step never blocks; every other status derives from `current`
    steps = []
    for key, label, who in STEPS:
        if done[key]:
            status = "done"
        elif key == current:
            status = "waiting" if key in GATES else "active"
        elif key == "soatchu" and tc is not None:
            status = "warn"                     # a fresh report with errors: visible even when it does not block
        elif key in ("noidung", "nhac"):
            status = "optional"
        elif key == "soatchu" and final is not None:
            status = "skipped"
        else:
            status = "todo"
        step = {"key": key, "label": label, "who": who, "status": status, "gate": key in GATES}
        if key == "soatchu" and tc is not None:
            step["badge"] = f"{tc['errors']} lỗi" if tc["errors"] else "sạch"
        steps.append(step)

    prompt, headline = ("", "Xong — đã giao")
    if current:
        template, headline = prompts[current]
        prompt = template.format(slug=slug)

    thumb = None
    if final is not None:
        jpg = final.with_suffix(".jpg")
        thumb = f"/media/{slug}/renders/{jpg.name}" if jpg.exists() else None
    return {
        "slug": slug,
        "name": project.data.get("name", slug),
        "created": project.data.get("created", ""),
        "steps": steps,
        "current": current,
        "headline": headline,
        "prompt": prompt,
        "concepts": concepts if current == "cong1" else [],
        "final": f"/media/{slug}/renders/{final.name}" if final else None,
        "thumb": thumb,
        "notes": notes[-8:][::-1],
        "waiting": current in GATES,
        "finished": current is None,
    }


def overview(settings: Settings) -> dict:
    music = sum(1 for _ in settings.music_dir.rglob("*") if _.suffix.lower() in AUDIO_EXTS) if settings.music_dir.exists() else 0
    projects = [project_state(p, music) for p in Project.list_all(settings)]
    profile = settings.root / "profile" / "gu-nguoi-dung.md"
    rules = sum(1 for ln in profile.read_text(encoding="utf-8").splitlines() if ln.lstrip().startswith(("- ", "* "))) \
        if profile.exists() else 0
    kb = sum(1 for _ in settings.knowledge_dir.glob("*/*.md")) if settings.knowledge_dir.exists() else 0
    return {
        "projects": projects,
        "stats": {
            "projects": len(projects),
            "waiting": sum(p["waiting"] for p in projects),
            "finished": sum(p["finished"] for p in projects),
            "rules": rules,
            "kb": kb,
            "music": music,
        },
    }


def add_gate_note(settings: Settings, slug: str, gate: str, text: str = "", concept: int | None = None) -> str:
    """Record a gate decision in project.md. Returns the prompt to paste into Claude Code next."""
    project = Project.open(settings, slug)
    state = project_state(project)
    text = " ".join(text.split())[:600]
    if gate == "cong1":
        picked = next((c for c in state["concepts"] if c["index"] == concept), None)
        if picked is None:
            raise ValueError("Hướng không tồn tại")
        project.note(f"{CHOSEN_PREFIX} {picked['index']}: {picked['name']}" + (f" — {text}" if text else ""), "Người dùng")
        return (f"/kich-ban bước 2 cho dự án {project.slug}: viết script/script.md và edit_plan.json theo hướng "
                f"{picked['index']} «{picked['name']}» (đã ghi trong project.md). Chưa render.")
    if gate == "cong2-ok":
        project.note(f"{APPROVE_PREFIX}." + (f" {text}" if text else ""), "Người dùng")
        return ""
    if gate == "cong2-fix":
        if not text:
            raise ValueError("Hãy ghi rõ cần sửa gì")
        project.note(f"Cần sửa: {text}", "Người dùng")
        return f"/sua-video dự án {project.slug}: {text}. Sửa edit_plan.json, render lại, phản biện soi rồi báo tôi."
    raise ValueError("Cổng không hợp lệ")


def _safe_media(settings: Settings, rel: str) -> Path | None:
    parts = Path(unquote(rel)).parts
    if len(parts) < 3 or parts[1] not in ("renders", "analysis") or ".." in parts:
        return None
    path = (settings.projects_dir / Path(*parts)).resolve()
    if settings.projects_dir.resolve() not in path.parents or not path.is_file():
        return None
    return path


def make_handler(settings: Settings):
    class Handler(BaseHTTPRequestHandler):
        server_version = "vedit-studio"

        def log_message(self, *args):  # quiet
            pass

        def _send(self, code: int, body: bytes, ctype: str, extra: dict | None = None) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, data) -> None:
            self._send(code, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            path = urlparse(self.path).path
            if path in ("/", "/index.html"):
                self._send(200, UI_FILE.read_bytes(), "text/html; charset=utf-8")
            elif path == "/api/overview":
                self._json(200, overview(settings))
            elif path.startswith("/media/"):
                self._media(path[len("/media/"):])
            else:
                self._json(404, {"error": "not found"})

        def _media(self, rel: str) -> None:
            file = _safe_media(settings, rel)
            if file is None:
                return self._json(404, {"error": "not found"})
            data = file.read_bytes()
            ctype = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
            rng = self.headers.get("Range")
            m = re.match(r"bytes=(\d*)-(\d*)", rng or "")
            if m and (m.group(1) or m.group(2)):
                size = len(data)
                start = int(m.group(1)) if m.group(1) else max(size - int(m.group(2)), 0)
                end = min(int(m.group(2)), size - 1) if m.group(1) and m.group(2) else size - 1
                if start > end:
                    return self._send(416, b"", ctype, {"Content-Range": f"bytes */{size}"})
                return self._send(206, data[start:end + 1], ctype,
                                  {"Content-Range": f"bytes {start}-{end}/{size}", "Accept-Ranges": "bytes"})
            self._send(200, data, ctype, {"Accept-Ranges": "bytes"})

        def do_POST(self):
            if urlparse(self.path).path != "/api/gate":
                return self._json(404, {"error": "not found"})
            # a page on another origin must not be able to write notes through the user's browser
            host = (self.headers.get("Host") or "").split(":")[0]
            origin = self.headers.get("Origin")
            if host not in ("127.0.0.1", "localhost") or (origin and urlparse(origin).hostname not in ("127.0.0.1", "localhost")):
                return self._json(403, {"error": "forbidden"})
            if self.headers.get("X-Studio") != "1":
                return self._json(403, {"error": "forbidden"})
            try:
                length = min(int(self.headers.get("Content-Length") or 0), 20000)
                body = json.loads(self.rfile.read(length) or b"{}")
                prompt = add_gate_note(settings, str(body.get("slug", "")), str(body.get("gate", "")),
                                       str(body.get("text", "")), body.get("concept"))
            except (ValueError, KeyError, TypeError) as e:
                return self._json(400, {"error": str(e)})
            except Exception as e:  # unknown project etc.
                return self._json(400, {"error": str(e)})
            self._json(200, {"ok": True, "prompt": prompt, "overview": overview(settings)})

    return Handler


def serve(settings: Settings, port: int = 8765, open_browser: bool = False) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(settings))
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"Studio đang chạy: {url}  (Ctrl+C để dừng)")
    if open_browser:
        threading.Timer(0.5, lambda: __import__("webbrowser").open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng Studio")
    finally:
        server.server_close()
