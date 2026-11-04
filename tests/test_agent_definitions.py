"""The Claude Code subagents and skills the orchestrator relies on are well-formed and listed in CLAUDE.md."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AGENTS = sorted((ROOT / ".claude" / "agents").glob("*.md"))
SKILLS = sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md"))
KNOWN_TOOLS = {"Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch"}


def frontmatter(path: Path) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    assert match, f"{path.name}: thiếu frontmatter"
    return {k.strip(): v.strip() for k, v in (line.split(":", 1) for line in match.group(1).splitlines() if ":" in line)}


@pytest.mark.parametrize("path", AGENTS, ids=lambda p: p.stem)
def test_agent_definition_is_well_formed(path):
    meta = frontmatter(path)
    assert meta["name"] == path.stem
    assert len(meta["description"]) > 60
    if "tools" in meta:
        tools = {t.strip() for t in meta["tools"].split(",")}
        assert tools <= KNOWN_TOOLS, tools - KNOWN_TOOLS
    assert "vedit" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", SKILLS, ids=lambda p: p.parent.name)
def test_skill_definition_is_well_formed(path):
    meta = frontmatter(path)
    assert meta["name"] == path.parent.name and len(meta["description"]) > 60


def test_claude_md_lists_every_agent_and_skill():
    claude_md = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    for path in AGENTS:
        assert f"`{path.stem}`" in claude_md, f"CLAUDE.md chưa nhắc agent {path.stem}"
    for path in SKILLS:
        assert f"`/{path.parent.name}`" in claude_md, f"CLAUDE.md chưa nhắc lệnh tắt /{path.parent.name}"


def test_content_creator_is_wired_into_the_workflow():
    assert (ROOT / ".claude" / "agents" / "video-content-creator.md").exists()
    assert "video-content-creator" in (ROOT / ".claude" / "skills" / "noi-dung" / "SKILL.md").read_text(encoding="utf-8")
    assert "noi-dung" in (ROOT / ".claude" / "skills" / "lam-video" / "SKILL.md").read_text(encoding="utf-8")
