"""Command line: `vedit <command>`. Run `vedit -h` for help."""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sys
from pathlib import Path

from .config import load_settings

PLATFORM_CHOICES = ["tiktok", "reels", "shorts", "youtube", "square"]


def _project_or_new(settings, ref: str, name: str | None):
    from .project import Project, ProjectError

    path = Path(ref).expanduser()
    if path.is_file():
        return Project.create(settings, path, name)
    try:
        return Project.open(settings, ref)
    except ProjectError:
        raise SystemExit(f"'{ref}' không phải file video hay dự án có sẵn (xem: vedit projects)") from None


def cmd_research(args, settings) -> None:
    from .agents.researcher import run_research

    run = run_research(settings, args.topic, depth=args.depth, focus=args.focus)
    print("\n" + run.text)
    print(f"\nKho kiến thức: {settings.knowledge_dir / 'INDEX.md'}")


def cmd_fetch(args, settings) -> None:
    from .fetch import fetch_video
    from .media import probe

    path = fetch_video(args.source, settings.inbox_dir)
    info = probe(path)
    print(f"✓ {path}\n  {info.width}x{info.height} {info.orientation}, {info.duration:.1f}s, "
          f"{info.size_bytes / 1e6:.1f} MB, âm thanh: {'có' if info.has_audio else 'không'}")


def cmd_analyze(args, settings) -> None:
    from .pipeline import analyze

    project = _project_or_new(settings, args.video, args.name)
    analysis = analyze(settings, project, transcript=args.transcript, max_frames=args.max_frames, force=True)
    print(f"\nDự án: {project.slug}\n  {len(analysis['scenes'])} cảnh, {len(analysis['silences'])} khoảng lặng, "
          f"transcript: {'có' if analysis['transcript'] else 'không'}\n  {project.analysis_dir / 'analysis.json'}")


def cmd_concepts(args, settings) -> None:
    from .agents.scriptwriter import run_concepts
    from .pipeline import analyze

    project = _project_or_new(settings, args.target, args.name)
    print(f"■ Dự án: {project.dir}")
    analyze(settings, project, transcript=args.transcript)
    concepts = run_concepts(settings, project, goal=args.goal, platform=args.platform, duration=args.duration,
                            style=args.style, audience=args.audience, idea=args.idea)
    print("\n" + (project.script_dir / "concepts.md").read_text(encoding="utf-8"))
    print(f"Bước tiếp: vedit script {project.slug} --goal \"...\" --concept <1-{len(concepts.concepts)}> [--notes '...']")


def cmd_script(args, settings) -> None:
    from .agents.scriptwriter import run_scriptwriter
    from .pipeline import analyze, choose_concept

    project = _project_or_new(settings, args.target, args.name)
    print(f"■ Dự án: {project.dir}")
    analyze(settings, project, transcript=args.transcript)
    chosen, notes = choose_concept(project, args.concept, args.notes)
    run = run_scriptwriter(settings, project, goal=args.goal, platform=args.platform, duration=args.duration,
                           style=args.style, audience=args.audience, concept=chosen, notes=notes)
    print("\n" + run.text)
    print(f"\nKịch bản: {project.script_dir / 'script.md'}\nEditPlan: {project.plan_path}")
    if args.drive:
        from .gdrive import sync_project

        print(f"Google Drive: {sync_project(settings, project, renders=False)['url']}")
    print(f"\nBước tiếp: vedit edit {project.slug}")


def cmd_edit(args, settings) -> None:
    from .agents.editor import run_editor
    from .project import Project

    project = Project.open(settings, args.project)
    run = run_editor(settings, project, args.instructions, export=not args.no_export)
    print("\n" + run.text)
    if args.drive:
        from .gdrive import sync_project

        print(f"Google Drive: {sync_project(settings, project)['url']}")


def _load_plan(settings, target_ref: str):
    """Plan + base dir + renders dir from a project name or an edit_plan.json path; exits on invalid plans."""
    from pydantic import ValidationError

    from .agents.tools import format_validation_error
    from .edl import EditPlan, validate_against_media
    from .media import probe
    from .project import Project

    target = Path(target_ref).expanduser()
    if target.suffix == ".json" and target.is_file():
        plan_path, base_dir, renders = target, target.parent, target.parent / "renders"
    else:
        project = Project.open(settings, target_ref)
        plan_path, base_dir, renders = project.plan_path, project.dir, project.renders_dir
    try:
        plan = EditPlan.load(plan_path)
    except ValidationError as e:
        raise SystemExit(f"{plan_path} không hợp lệ:\n" + format_validation_error(e)) from None
    from .ass import check_fonts

    problems = validate_against_media(plan, base_dir, probe) + check_fonts(plan, settings.font, settings.fonts_dir)
    if problems:
        raise SystemExit(f"{plan_path} có lỗi:\n- " + "\n- ".join(problems))
    return plan, base_dir, renders


def cmd_frame(args, settings) -> None:
    """Grab one frame (optionally with a coordinate grid) from a project's source or render, or any video."""
    from .media import extract_frame
    from .project import Project

    target = Path(args.target).expanduser()
    if target.is_file():
        video, out_dir = target, settings.root / "inbox" / "frames"
    else:
        project = Project.open(settings, args.target)
        video = project.input_path if args.source == "source" else project.renders_dir / (
            "preview.mp4" if args.source == "preview" else "final.mp4")
        out_dir = project.analysis_dir / "frames"
    if not video.exists():
        raise SystemExit(f"Không có {video} — render trước đã")
    for t in args.times:
        out = Path(args.out) if args.out and len(args.times) == 1 else \
            out_dir / f"{args.source}_{t:07.2f}{'_grid' if args.grid else ''}.jpg"
        print(extract_frame(video, t, out, width=args.width, grid=args.grid))


def cmd_sheet(args, settings) -> None:
    from .media import contact_sheet
    from .project import Project

    target = Path(args.target).expanduser()
    if target.is_file():
        video, out_dir = target, settings.root / "inbox" / "frames"
    else:
        project = Project.open(settings, args.target)
        video = project.input_path if args.source == "source" else project.renders_dir / (
            "preview.mp4" if args.source == "preview" else "final.mp4")
        out_dir = project.analysis_dir / "frames"
    if not video.exists():
        raise SystemExit(f"Không có {video} — render trước đã")
    span = f"{args.start:06.2f}-{args.end:06.2f}" if args.end is not None else f"{args.start:06.2f}-het"
    out = Path(args.out) if args.out else out_dir / f"sheet_{args.source}_{span}.jpg"
    path, times = contact_sheet(video, out, start=args.start, end=args.end, count=args.count, cols=args.cols,
                                width=args.width)
    print(f"{path}\n  mốc: {', '.join(f'{t:.2f}' for t in times)}")


def cmd_track(args, settings) -> None:
    """Track an object in a project's source video so HUD graphics can follow it."""
    from .project import Project
    from .track import Track, describe, track_object, track_path, track_sheet

    project = Project.open(settings, args.project)
    tracks_dir = project.analysis_dir / "tracks"
    if not args.name:
        files = sorted(tracks_dir.glob("*.json")) if tracks_dir.is_dir() else []
        print("\n".join(describe(Track.load(f)) for f in files) or "Chưa có track nào")
        return
    out = track_path(project.dir, args.name)
    if args.at is None or args.box is None:
        if not out.exists():
            raise SystemExit("Cần --at và --box để tạo track mới")
        track = Track.load(out)
    else:
        try:
            box = tuple(float(v) for v in args.box.split(","))
        except ValueError:
            box = ()
        if len(box) != 4:
            raise SystemExit("--box phải là x,y,w,h (tỉ lệ 0..1), vd 0.30,0.30,0.45,0.40")
        video = Path(args.source).expanduser() if args.source else project.input_path
        track = track_object(video, name=args.name, at=args.at, box=box, until=args.until, back=args.back,
                             smoothing=args.smooth)
        track.save(out)
    sheet = track_sheet(track, Path(track.source), tracks_dir / f"{args.name}_sheet.jpg")
    print(f"✓ {describe(track)}\n  {out}\n  kiểm tra bằng mắt: {sheet}")


def cmd_sfx(args, settings) -> None:
    """Real sound-effect packs: import, list, search."""
    from .sfxlib import SfxError, describe, import_pack, library, missing_packs, search

    sfx_dir = settings.assets_dir / "sfx"
    try:
        if args.sfx_cmd == "add":
            print(f"• Nhập {len(args.source)} nguồn...")
            pack_dir, sounds = import_pack(args.source, sfx_dir, args.name)
            cats: dict[str, int] = {}
            for s in sounds:
                cats[s.category] = cats.get(s.category, 0) + 1
            print(f"✓ Bộ '{pack_dir.name}': {len(sounds)} âm thanh → {pack_dir}\n  "
                  + ", ".join(f"{k} {v}" for k, v in sorted(cats.items(), key=lambda kv: -kv[1])))
            return
        for pack, src in missing_packs(sfx_dir):
            print(f"! Bộ '{pack}' có chỉ mục nhưng chưa có file (workspace mới) — nhập lại: "
                  f"vedit sfx add {' '.join(src)} --name {pack}")
        hits = search(sfx_dir, " ".join(args.query), args.category, args.limit) if (args.query or args.category) \
            else library(sfx_dir)[: args.limit]
        if not hits:
            print("Chưa có SFX nào khớp. Nhập bộ SFX: vedit sfx add <thư mục | file.zip | link Drive> --name <tên>")
            return
        for pack_dir, sound in hits:
            print(describe(pack_dir, sound))
    except SfxError as e:
        raise SystemExit(f"✗ {e}") from None


def cmd_note(args, settings) -> None:
    from .project import Project

    project = Project.open(settings, args.project)
    project.note(" ".join(args.text), args.kind)
    print(f"✓ Đã ghi vào {project.memory_path}")


def cmd_validate(args, settings) -> None:
    """Validate a project's concepts.json, script.json and edit_plan.json (whichever exist; regenerating the
    readable .md files), or a bare edit_plan.json path."""
    from pydantic import ValidationError

    from .agents.scriptwriter import ConceptSet, ScriptDoc, concepts_markdown, script_markdown
    from .agents.tools import format_validation_error
    from .project import Project, ProjectError

    target = Path(args.target).expanduser()
    if target.suffix == ".json" and target.is_file():
        plan, _, _ = _load_plan(settings, args.target)
        print(plan.summary() + "\n✓ EditPlan hợp lệ")
        return
    try:
        project = Project.open(settings, args.target)
    except ProjectError as e:
        raise SystemExit(str(e)) from None

    checked = 0
    for name, model, render_md in (("concepts", ConceptSet, concepts_markdown), ("script", ScriptDoc, script_markdown)):
        path = project.script_dir / f"{name}.json"
        if not path.exists():
            continue
        try:
            doc = model.model_validate_json(path.read_text(encoding="utf-8"))
        except ValidationError as e:
            raise SystemExit(f"{path} không hợp lệ:\n" + format_validation_error(e)) from None
        (project.script_dir / f"{name}.md").write_text(render_md(doc, project), encoding="utf-8")
        print(f"✓ {name}.json hợp lệ — đã tạo lại {project.script_dir / f'{name}.md'}")
        checked += 1
    if project.plan_path.exists():
        plan, _, _ = _load_plan(settings, str(project.dir))
        print(plan.summary() + "\n✓ EditPlan hợp lệ")
        checked += 1
    if not checked:
        raise SystemExit(f"Dự án {project.slug} chưa có concepts.json, script.json hay edit_plan.json")


def cmd_schema(args, settings) -> None:
    import json

    from .agents.scriptwriter import ConceptSet, ScriptDoc
    from .edl import EditPlan

    model = {"script": ScriptDoc, "concepts": ConceptSet}.get(args.which, EditPlan)
    print(json.dumps(model.model_json_schema(), ensure_ascii=False, indent=1))


def cmd_render(args, settings) -> None:
    from .agents.editor import Progress
    from .render import render

    plan, base_dir, renders = _load_plan(settings, args.target)
    print(plan.summary())
    output = Path(args.out) if args.out else renders / ("preview.mp4" if args.preview else plan.export.filename)
    progress = Progress("preview" if args.preview else "render")
    result = render(plan, output, base_dir=base_dir, preview=args.preview, font=settings.font,
                    fonts_dir=settings.fonts_dir, work_dir=renders / ".work", on_progress=progress)
    progress.finish()
    print(f"✓ {result.output} ({result.duration:.2f}s, {result.elapsed:.0f}s render)"
          + (f"\n  âm thanh: true peak {result.true_peak:.1f} dBTP" if result.true_peak is not None else "")
          + (f"\n  thumbnail: {result.thumbnail}" if result.thumbnail else ""))


def cmd_make(args, settings) -> None:
    from .pipeline import make_video

    project = make_video(settings, Path(args.video), goal=args.goal, platform=args.platform, duration=args.duration,
                         style=args.style, audience=args.audience, name=args.name, transcript=args.transcript,
                         research_topic=args.research, drive=args.drive, export=not args.no_export,
                         idea=args.idea, concept=args.concept, notes=args.notes)
    print(f"\n✓ Xong. Thư mục dự án: {project.dir}")


def cmd_kb(args, settings) -> None:
    from .knowledge import CATEGORIES, KnowledgeBase

    kb = KnowledgeBase(settings.knowledge_dir)
    if args.kb_cmd == "search":
        for note, score, snippet in kb.search(" ".join(args.query), limit=args.limit):
            print(f"[{note.ref}] {note.title} ({score})\n   {snippet}\n")
    elif args.kb_cmd == "show":
        note = kb.get(args.ref)
        print(note.path.read_text(encoding="utf-8") if note else f"Không có ghi chú '{args.ref}'")
    elif args.kb_cmd == "index":
        print(kb.write_index())
    else:
        notes = kb.notes(args.category)
        for cat in CATEGORIES:
            group = [n for n in notes if n.category == cat]
            if group:
                print(f"\n{cat} ({len(group)})")
                for n in group:
                    print(f"  {n.ref:<55} {n.title}")
        print(f"\nTổng: {len(notes)} ghi chú — {settings.knowledge_dir}")


def cmd_drive(args, settings) -> None:
    from .gdrive import setup_project_folders, sync_project
    from .project import Project

    project = Project.open(settings, args.project)
    if args.drive_cmd == "setup":
        info = setup_project_folders(settings, project)
        print(f"✓ Thư mục Drive: {info['url']}")
    else:
        result = sync_project(settings, project, renders=not args.no_renders, source=args.source)
        print(f"✓ Đã tải {len(result['files'])} file lên {result['url']}")


def cmd_projects(args, settings) -> None:
    from .project import Project

    projects = Project.list_all(settings)
    if not projects:
        print(f"Chưa có dự án nào trong {settings.projects_dir}")
    for p in projects:
        flags = [name for name, ok in (("phân tích", p.analysis() is not None),
                                       ("kịch bản", (p.script_dir / "script.md").exists()),
                                       ("plan", p.plan_path.exists()),
                                       ("đã xuất", any(p.renders_dir.glob("*.mp4"))),
                                       ("drive", "drive" in p.data)) if ok]
        print(f"{p.slug:<45} {Path(p.data['input']).name:<30} {', '.join(flags)}")


def cmd_doctor(args, settings) -> None:
    def row(ok: bool, label: str, hint: str = "") -> None:
        print(f"  {'✓' if ok else '✗'} {label}" + (f" — {hint}" if hint and not ok else ""))

    print("vedit doctor")
    row(bool(shutil.which("ffmpeg")) and bool(shutil.which("ffprobe")), "ffmpeg / ffprobe",
        "cài ffmpeg: https://ffmpeg.org/download.html")
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
    row(has_key, "ANTHROPIC_API_KEY", "đặt trong .env (bắt buộc cho 3 agent; 'vedit render' không cần)")
    row(importlib.util.find_spec("faster_whisper") is not None, "faster-whisper (phụ đề tự động)",
        "tuỳ chọn: pip install 'vedit[transcribe]'")
    row(importlib.util.find_spec("cv2") is not None, "OpenCV (vedit track — HUD bám vật)",
        "tuỳ chọn: pip install 'vedit[track]'")
    row(importlib.util.find_spec("googleapiclient") is not None, "google-api-python-client (Drive)",
        "tuỳ chọn: pip install 'vedit[gdrive]'")
    row(bool(settings.gdrive_oauth_client or settings.gdrive_service_account), "Cấu hình Google Drive",
        "tuỳ chọn: GOOGLE_OAUTH_CLIENT_FILE trong .env")
    row(bool(settings.github_token), "GITHUB_TOKEN", "tuỳ chọn: tăng giới hạn GitHub API cho Agent 1")
    if shutil.which("fc-list"):
        import subprocess

        fonts = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True).stdout
        local = list(settings.fonts_dir.glob("*.[ot]tf")) if settings.fonts_dir.exists() else []
        row(settings.font.lower() in fonts.lower() or bool(local), f"Font '{settings.font}'",
            f"không thấy font; thêm file .ttf vào {settings.fonts_dir} hoặc đổi VEDIT_FONT")
    print(f"\n  model: {settings.model} | effort: research={settings.effort_research} "
          f"script={settings.effort_script} edit={settings.effort_edit}")
    print(f"  knowledge: {settings.knowledge_dir}\n  projects: {settings.projects_dir}\n  assets: {settings.assets_dir}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vedit", description="Hệ thống 3 agent dựng, chỉnh sửa và lên kịch bản video ngắn.")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("research", help="Agent 1: nghiên cứu kỹ thuật edit (GitHub, web, YouTube, TikTok) → kho kiến thức")
    r.add_argument("topic", help='Chủ đề, ví dụ "kỹ thuật cắt nhịp nhanh cho video TikTok"')
    r.add_argument("--depth", choices=["quick", "standard", "deep"], default="standard")
    r.add_argument("--focus", nargs="+", choices=["web", "github", "youtube", "tiktok"], help="Ưu tiên nguồn")
    r.set_defaults(func=cmd_research)

    def brief_args(sp, video_required=True):
        sp.add_argument("--goal", required=True, help="Mục tiêu / ý tưởng video (vd: 'review quán cafe, thu hút giới trẻ')")
        sp.add_argument("--platform", choices=PLATFORM_CHOICES, default="tiktok")
        sp.add_argument("--duration", type=float, default=30, help="Độ dài mong muốn (giây)")
        sp.add_argument("--style", help="Phong cách (vd: 'năng động, hài hước, vlog')")
        sp.add_argument("--audience", help="Khán giả mục tiêu")
        sp.add_argument("--name", help="Tên dự án")
        sp.add_argument("--transcript", type=Path, help="File phụ đề .srt/.vtt có sẵn (thay cho nhận dạng giọng nói)")
        sp.add_argument("--drive", action="store_true", help="Tạo thư mục Google Drive và tải kết quả lên")

    f = sub.add_parser("fetch", help="Tải video vào inbox/ từ link Google Drive, YouTube, TikTok... hoặc link trực tiếp")
    f.add_argument("source", help="URL hoặc đường dẫn file")
    f.set_defaults(func=cmd_fetch)

    a = sub.add_parser("analyze", help="Phân tích video (cảnh, khoảng lặng, transcript, khung hình) — không dùng AI")
    a.add_argument("video")
    a.add_argument("--name")
    a.add_argument("--transcript", type=Path)
    a.add_argument("--max-frames", type=int, default=16)
    a.set_defaults(func=cmd_analyze)

    c = sub.add_parser("concepts", help="Agent 2 (bước 1): đề xuất 2-3 hướng dựng khác nhau để bạn chọn")
    c.add_argument("target", help="File video hoặc tên dự án đã có")
    brief_args(c)
    c.add_argument("--idea", help="Ý tưởng riêng của bạn (vd 'làm như game AR') — một hướng sẽ phát triển đúng ý này")
    c.set_defaults(func=cmd_concepts)

    s = sub.add_parser("script", help="Agent 2 (bước 2): kịch bản + EditPlan theo hướng dựng bạn đã chọn")
    s.add_argument("target", help="File video hoặc tên dự án đã có")
    brief_args(s)
    s.add_argument("--concept", type=int, help="Số thứ tự hướng dựng đã chọn trong script/concepts.md")
    s.add_argument("--notes", help="Ghi chú thêm cho hướng đã chọn")
    s.set_defaults(func=cmd_script)

    e = sub.add_parser("edit", help="Agent 3: chỉnh EditPlan theo yêu cầu, render, tự kiểm tra và xuất video")
    e.add_argument("project")
    e.add_argument("-i", "--instructions", help='Yêu cầu chỉnh sửa, vd "chữ to hơn, bỏ cảnh thứ 3, thêm zoom ở hook"')
    e.add_argument("--no-export", action="store_true", help="Chỉ làm tới bản preview")
    e.add_argument("--drive", action="store_true", help="Tải video xuất lên Google Drive")
    e.set_defaults(func=cmd_edit)

    rd = sub.add_parser("render", help="Render trực tiếp từ EditPlan (không dùng AI)")
    rd.add_argument("target", help="Tên dự án hoặc file edit_plan.json")
    rd.add_argument("--preview", action="store_true", help="Nửa độ phân giải, nhanh")
    rd.add_argument("--out", help="File xuất (mặc định renders/<export.filename>)")
    rd.set_defaults(func=cmd_render)

    fr = sub.add_parser("frame", help="Trích khung hình (có lưới toạ độ 0-1 để đặt chữ/đồ hoạ chính xác)")
    fr.add_argument("target", help="Tên dự án hoặc file video")
    fr.add_argument("times", nargs="+", type=float, help="Mốc giây (nguồn với --source source, timeline với preview/final)")
    fr.add_argument("--source", choices=["source", "preview", "final"], default="source")
    fr.add_argument("--grid", action="store_true", help="Vẽ lưới 10%% kèm nhãn toạ độ")
    fr.add_argument("--width", type=int, default=540)
    fr.add_argument("--out")
    fr.set_defaults(func=cmd_frame)

    v = sub.add_parser("validate", help="Kiểm tra EditPlan (schema + đối chiếu file media)")
    v.add_argument("target", help="Tên dự án hoặc file edit_plan.json")
    v.set_defaults(func=cmd_validate)

    sc = sub.add_parser("schema", help="In JSON schema của EditPlan hoặc kịch bản")
    sc.add_argument("which", choices=["plan", "script", "concepts"], nargs="?", default="plan")
    sc.set_defaults(func=cmd_schema)

    m = sub.add_parser("make", help="Chạy cả quy trình: phân tích → Agent 2 → Agent 3 (→ Drive)")
    m.add_argument("video")
    brief_args(m)
    m.add_argument("--research", metavar="TOPIC", help="Cho Agent 1 nghiên cứu nhanh chủ đề này trước")
    m.add_argument("--no-export", action="store_true", help="Dừng ở bản preview")
    m.add_argument("--idea", help="Ý tưởng riêng của bạn, đưa vào bước đề xuất hướng dựng")
    m.add_argument("--concept", type=int, help="Chọn sẵn hướng dựng (bỏ qua câu hỏi)")
    m.add_argument("--notes", help="Ghi chú cho hướng đã chọn")
    m.set_defaults(func=cmd_make)

    sh = sub.add_parser("sheet", help="Ảnh ghép nhiều khung hình có mốc giây (xem cả video / quanh một điểm cắt)")
    sh.add_argument("target", help="Tên dự án hoặc file video")
    sh.add_argument("--source", choices=["source", "preview", "final"], default="preview")
    sh.add_argument("--start", type=float, default=0.0)
    sh.add_argument("--end", type=float)
    sh.add_argument("--count", type=int, default=12)
    sh.add_argument("--cols", type=int, default=4)
    sh.add_argument("--width", type=int, default=360)
    sh.add_argument("--out")
    sh.set_defaults(func=cmd_sheet)

    tk = sub.add_parser("track", help="Bám theo một vật trong video nguồn để HUD / đồ hoạ dính vào vật (OpenCV)")
    tk.add_argument("project")
    tk.add_argument("name", nargs="?", help="Tên track, vd 'hu', 'ot' (bỏ trống = liệt kê track đã có)")
    tk.add_argument("--at", type=float, help="Mốc giây NGUỒN nơi khoanh vật (xem `vedit frame <dự án> <giây> --grid`)")
    tk.add_argument("--box", help="Hộp quanh vật tại --at: x,y,w,h theo tỉ lệ khung nguồn (góc trên-trái + rộng, cao)")
    tk.add_argument("--until", type=float, help="Bám tới giây nguồn này (mặc định hết video)")
    tk.add_argument("--back", type=float, help="Bám ngược về giây nguồn này")
    tk.add_argument("--source", help="File video khác video của dự án")
    tk.add_argument("--smooth", type=float, default=0.5, help="Làm mượt 0..1 (mặc định 0.5)")
    tk.set_defaults(func=cmd_track)

    sx = sub.add_parser("sfx", help="Thư viện SFX thật (bộ âm thanh tải về / tải lên): nhập, liệt kê, tìm")
    sxsub = sx.add_subparsers(dest="sfx_cmd", required=True)
    sxa = sxsub.add_parser("add", help="Nhập bộ SFX từ thư mục, file .zip, file âm thanh/video hoặc link Google Drive")
    sxa.add_argument("source", nargs="+")
    sxa.add_argument("--name", help="Tên bộ (mặc định theo tên thư mục / file)")
    sxl = sxsub.add_parser("list", help="Liệt kê / tìm: vedit sfx list whoosh  |  vedit sfx list --category impact")
    sxl.add_argument("query", nargs="*")
    sxl.add_argument("--category", help="whoosh, impact, riser, pop, click, ding, magic, glitch, camera, cash, fail, "
                                        "funny, crowd, game, scratch, other")
    sxl.add_argument("--limit", type=int, default=40)
    sx.set_defaults(func=cmd_sfx)

    nt = sub.add_parser("note", help="Ghi quyết định / phản hồi vào nhật ký dự án (project.md)")
    nt.add_argument("project")
    nt.add_argument("text", nargs="+")
    nt.add_argument("--kind", default="ghi chú", help="vd: phản hồi, quyết định, chọn hướng")
    nt.set_defaults(func=cmd_note)

    k = sub.add_parser("kb", help="Xem / tìm trong kho kiến thức")
    ksub = k.add_subparsers(dest="kb_cmd")
    kl = ksub.add_parser("list")
    kl.add_argument("--category")
    ks = ksub.add_parser("search")
    ks.add_argument("query", nargs="+")
    ks.add_argument("--limit", type=int, default=8)
    kshow = ksub.add_parser("show")
    kshow.add_argument("ref", help="category/slug")
    ksub.add_parser("index", help="Tạo lại knowledge/INDEX.md")
    k.set_defaults(func=cmd_kb, category=None)

    d = sub.add_parser("drive", help="Google Drive: tạo thư mục dự án / đồng bộ kết quả")
    dsub = d.add_subparsers(dest="drive_cmd", required=True)
    ds = dsub.add_parser("setup")
    ds.add_argument("project")
    dy = dsub.add_parser("sync")
    dy.add_argument("project")
    dy.add_argument("--source", action="store_true", help="Tải cả video gốc")
    dy.add_argument("--no-renders", action="store_true")
    d.set_defaults(func=cmd_drive)

    sub.add_parser("projects", help="Liệt kê dự án").set_defaults(func=cmd_projects)
    sub.add_parser("doctor", help="Kiểm tra môi trường").set_defaults(func=cmd_doctor)
    return p


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    settings = load_settings()
    from .agents.base import AgentError
    from .fetch import FetchError
    from .gdrive import DriveError
    from .media import MediaError
    from .project import ProjectError
    from .render import RenderError

    try:
        args.func(args, settings)
    except (AgentError, DriveError, FetchError, MediaError, ProjectError, RenderError) as e:
        print(f"\n✗ {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n✗ Đã huỷ", file=sys.stderr)
        return 130
    return 0
