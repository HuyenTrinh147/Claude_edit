"""A project = one input video and everything the agents produce for it.

projects/<slug>/
  project.json        metadata (input path, brief, Google Drive ids)
  project.md          memory: chosen concept, decisions, the user's feedback verbatim, version history
  analysis/           analysis.json + keyframes (frames/)
  script/             script.md, script.json (Agent 2)
  edit_plan.json      EditPlan (Agent 2 writes, Agent 3 edits/renders)
  renders/            preview.mp4, final videos + thumbnails (Agent 3)
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field
from pathlib import Path

from .config import Settings
from .knowledge import slugify


class ProjectError(RuntimeError):
    pass


@dataclass
class Project:
    dir: Path
    data: dict = field(default_factory=dict)

    @property
    def slug(self) -> str:
        return self.dir.name

    @property
    def input_path(self) -> Path:
        return Path(self.data["input"])

    @property
    def analysis_dir(self) -> Path:
        return self.dir / "analysis"

    @property
    def script_dir(self) -> Path:
        return self.dir / "script"

    @property
    def renders_dir(self) -> Path:
        return self.dir / "renders"

    @property
    def plan_path(self) -> Path:
        return self.dir / "edit_plan.json"

    @property
    def memory_path(self) -> Path:
        return self.dir / "project.md"

    def note(self, text: str, kind: str = "ghi chú") -> None:
        """Append a timestamped line to project.md — agents read it first so feedback is never lost."""
        if not self.memory_path.exists():
            self.memory_path.write_text(
                f"# Dự án {self.slug}\n\nVideo nguồn: `{Path(self.data['input']).name}`\n\n## Nhật ký\n\n",
                encoding="utf-8")
        with open(self.memory_path, "a", encoding="utf-8") as f:
            f.write(f"- {dt.datetime.now():%Y-%m-%d %H:%M} · **{kind}**: {text.strip()}\n")

    def analysis(self) -> dict | None:
        path = self.analysis_dir / "analysis.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def save(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "project.json").write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def create(cls, settings: Settings, video: Path, name: str | None = None) -> "Project":
        video = Path(video).expanduser().resolve()
        if not video.exists():
            raise ProjectError(f"Không tìm thấy video: {video}")
        slug = f"{dt.date.today():%Y%m%d}-{slugify(name or video.stem, 40)}"
        target, n = settings.projects_dir / slug, 2
        while (target / "project.json").exists():
            existing = json.loads((target / "project.json").read_text(encoding="utf-8"))
            if existing.get("input") == str(video):
                return cls(dir=target, data=existing)  # same video again -> reuse the project
            target, n = settings.projects_dir / f"{slug}-{n}", n + 1
        project = cls(dir=target, data={"name": name or video.stem, "input": str(video),
                                        "created": dt.datetime.now().isoformat(timespec="seconds")})
        project.save()
        project.note("tạo dự án", "hệ thống")
        return project

    @classmethod
    def open(cls, settings: Settings, ref: str | Path) -> "Project":
        candidates = [Path(ref).expanduser(), settings.projects_dir / str(ref)]
        if not any((c / "project.json").exists() for c in candidates):
            candidates += sorted(settings.projects_dir.glob(f"*{ref}*"))
        for c in candidates:
            if (c / "project.json").exists():
                return cls(dir=c.resolve(), data=json.loads((c / "project.json").read_text(encoding="utf-8")))
        raise ProjectError(f"Không tìm thấy dự án '{ref}' trong {settings.projects_dir}")

    @staticmethod
    def list_all(settings: Settings) -> list["Project"]:
        return [Project(dir=p.parent, data=json.loads(p.read_text(encoding="utf-8")))
                for p in sorted(settings.projects_dir.glob("*/project.json"))]
