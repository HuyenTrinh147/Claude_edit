"""End-to-end flow: video in -> analysis -> (Agent 1) -> Agent 2 script + plan -> Agent 3 render -> Drive."""

from __future__ import annotations

from pathlib import Path

from .config import Settings
from .media import analyze_video
from .project import Project


def analyze(settings: Settings, project: Project, *, transcript: Path | None = None, max_frames: int = 16,
            force: bool = False) -> dict:
    existing = project.analysis()
    if existing and not force and not transcript:
        print(f"• Dùng lại phân tích có sẵn ({project.analysis_dir / 'analysis.json'})")
        return existing
    print(f"• Phân tích video → {project.analysis_dir}")
    return analyze_video(project.input_path, project.analysis_dir, transcript_file=transcript,
                         whisper_model=settings.whisper_model, language=settings.lang, max_frames=max_frames)


def choose_concept(project: Project, concept: int | None = None, notes: str | None = None):
    """The approval gate: show the proposed concepts and let the user pick one (and add notes) before anything is
    built. Non-interactive runs must pass `concept`."""
    import sys

    from .agents.scriptwriter import load_concepts

    concepts = load_concepts(project)
    if concepts is None:
        raise SystemExit("Chưa có hướng dựng — chạy 'vedit concepts' trước.")
    if concept is None:
        print("\n" + (project.script_dir / "concepts.md").read_text(encoding="utf-8"))
        if not sys.stdin.isatty():
            raise SystemExit(f"Đọc {project.script_dir / 'concepts.md'} rồi chạy lại với --concept <số> [--notes '...'].")
        answer = input(f"Chọn hướng dựng 1-{len(concepts.concepts)} (có thể thêm ghi chú sau dấu ':'): ").strip()
        head, _, tail = answer.partition(":")
        concept, notes = int(head), (tail.strip() or notes)
    if not 1 <= concept <= len(concepts.concepts):
        raise SystemExit(f"Chọn 1-{len(concepts.concepts)}")
    chosen = concepts.concepts[concept - 1]
    project.note(f"chọn hướng {concept} — {chosen.name}" + (f"; ghi chú: {notes}" if notes else ""), "người dùng")
    return chosen, notes


def make_video(
    settings: Settings,
    video: Path,
    *,
    goal: str,
    platform: str = "tiktok",
    duration: float = 30,
    style: str | None = None,
    audience: str | None = None,
    name: str | None = None,
    transcript: Path | None = None,
    research_topic: str | None = None,
    drive: bool = False,
    export: bool = True,
    idea: str | None = None,
    concept: int | None = None,
    notes: str | None = None,
) -> Project:
    from .agents.editor import run_editor
    from .agents.researcher import run_research
    from .agents.scriptwriter import load_concepts, run_concepts, run_scriptwriter

    project = Project.create(settings, video, name)
    print(f"■ Dự án: {project.dir}")
    analyze(settings, project, transcript=transcript)

    if research_topic:
        print("\n■ Agent 1 — nghiên cứu")
        run_research(settings, research_topic, depth="quick")

    if load_concepts(project) is None or idea:
        print("\n■ Agent 2 — đề xuất hướng dựng")
        run_concepts(settings, project, goal=goal, platform=platform, duration=duration, style=style,
                     audience=audience, idea=idea)
    chosen, notes = choose_concept(project, concept, notes)

    print("\n■ Agent 2 — kịch bản & EditPlan theo hướng đã chọn")
    run_scriptwriter(settings, project, goal=goal, platform=platform, duration=duration, style=style,
                     audience=audience, concept=chosen, notes=notes)
    print(f"  → {project.script_dir / 'script.md'}")

    print("\n■ Agent 3 — dựng & xuất video")
    run_editor(settings, project, export=export)

    if drive:
        from .gdrive import sync_project
        print("\n■ Google Drive")
        result = sync_project(settings, project, renders=export)
        print(f"  → {result['url']}")
    return project
