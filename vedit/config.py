"""Settings loaded from environment variables (and a local .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


def _path(name: str, default: Path | None = None) -> Path | None:
    value = _env(name)
    return Path(value).expanduser() if value else default


def _effort(name: str, default: str) -> str:
    value = (_env(name, default) or default).lower()
    if value not in EFFORT_LEVELS:
        raise ValueError(f"{name}={value!r} không hợp lệ, chọn một trong {EFFORT_LEVELS}")
    return value


@dataclass
class Settings:
    root: Path
    model: str
    effort_research: str
    effort_script: str
    effort_edit: str
    max_tokens: int
    use_fallbacks: bool
    lang: str
    knowledge_dir: Path
    projects_dir: Path
    assets_dir: Path
    font: str
    whisper_model: str
    github_token: str | None
    gdrive_oauth_client: Path | None
    gdrive_service_account: Path | None
    gdrive_token: Path
    gdrive_parent_id: str | None
    gdrive_root_name: str

    @property
    def fonts_dir(self) -> Path:
        return self.assets_dir / "fonts"

    @property
    def music_dir(self) -> Path:
        return self.assets_dir / "music"


def load_settings(root: Path | None = None) -> Settings:
    root = Path(root or _env("VEDIT_HOME") or Path.cwd()).resolve()
    load_dotenv(root / ".env", override=False)

    return Settings(
        root=root,
        model=_env("VEDIT_MODEL", "claude-opus-5-5"),
        effort_research=_effort("VEDIT_EFFORT_RESEARCH", "medium"),
        effort_script=_effort("VEDIT_EFFORT_SCRIPT", "high"),
        effort_edit=_effort("VEDIT_EFFORT_EDIT", "medium"),
        max_tokens=int(_env("VEDIT_MAX_TOKENS", "64000")),
        use_fallbacks=_env("VEDIT_FALLBACKS", "1") not in ("0", "false", "no"),
        lang=_env("VEDIT_LANG", "vi"),
        knowledge_dir=_path("VEDIT_KNOWLEDGE_DIR", root / "knowledge"),
        projects_dir=_path("VEDIT_PROJECTS_DIR", root / "projects"),
        assets_dir=_path("VEDIT_ASSETS_DIR", root / "assets"),
        font=_env("VEDIT_FONT", "Inter"),
        whisper_model=_env("VEDIT_WHISPER_MODEL", "small"),
        github_token=_env("GITHUB_TOKEN"),
        gdrive_oauth_client=_path("GOOGLE_OAUTH_CLIENT_FILE"),
        gdrive_service_account=_path("GOOGLE_SERVICE_ACCOUNT_FILE"),
        gdrive_token=_path("GOOGLE_TOKEN_FILE", Path.home() / ".config" / "vedit" / "gdrive_token.json"),
        gdrive_parent_id=_env("GOOGLE_DRIVE_PARENT_ID"),
        gdrive_root_name=_env("GOOGLE_DRIVE_ROOT_NAME", "vedit"),
    )
