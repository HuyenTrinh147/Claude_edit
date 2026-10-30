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
) -> Project:
    from .agents.editor import run_editor
    from .agents.researcher import run_research
    from .agents.scriptwriter import run_scriptwriter

    project = Project.create(settings, video, name)
    print(f"■ Dự án: {project.dir}")
    analyze(settings, project, transcript=transcript)

    if research_topic:
        print("\n■ Agent 1 — nghiên cứu")
        run_research(settings, research_topic, depth="quick")

    print("\n■ Agent 2 — xu hướng & kịch bản")
    run_scriptwriter(settings, project, goal=goal, platform=platform, duration=duration, style=style,
                     audience=audience)
    print(f"  → {project.script_dir / 'script.md'}")

    print("\n■ Agent 3 — dựng & xuất video")
    run_editor(settings, project, export=export)

    if drive:
        from .gdrive import sync_project
        print("\n■ Google Drive")
        result = sync_project(settings, project, renders=export)
        print(f"  → {result['url']}")
    return project
