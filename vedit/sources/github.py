"""Minimal GitHub REST client (stdlib only)."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"


class GitHubError(RuntimeError):
    pass


def _request(path: str, token: str | None, accept: str = "application/vnd.github+json") -> bytes:
    req = urllib.request.Request(f"{API}{path}", headers={
        "Accept": accept,
        "User-Agent": "vedit-research-agent",
        "X-GitHub-Api-Version": "2022-11-28",
        **({"Authorization": f"Bearer {token}"} if token else {}),
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        if e.code == 403 and "rate limit" in detail.lower():
            raise GitHubError("GitHub rate limit — đặt GITHUB_TOKEN trong .env để tăng giới hạn") from e
        raise GitHubError(f"GitHub {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise GitHubError(f"Không kết nối được GitHub: {e.reason}") from e


def search_repositories(query: str, limit: int = 8, sort: str | None = "stars", token: str | None = None) -> list[dict]:
    """sort: 'stars', 'updated', 'forks' or None for GitHub's best match."""
    params: dict = {"q": query, "per_page": min(limit, 30)}
    if sort:
        params.update(sort=sort, order="desc")
    data = json.loads(_request(f"/search/repositories?{urllib.parse.urlencode(params)}", token))
    return [{
        "repo": item["full_name"],
        "description": (item.get("description") or "")[:300],
        "stars": item.get("stargazers_count", 0),
        "language": item.get("language"),
        "topics": item.get("topics", [])[:8],
        "updated": (item.get("pushed_at") or "")[:10],
        "url": item["html_url"],
    } for item in data.get("items", [])[:limit]]


def get_readme(repo: str, max_chars: int = 12000, token: str | None = None) -> str:
    repo = repo.strip().removeprefix("https://github.com/").strip("/")
    text = _request(f"/repos/{repo}/readme", token, accept="application/vnd.github.raw").decode("utf-8", "replace")
    if len(text) > max_chars:
        text = text[:max_chars] + f"\n\n[... cắt bớt, README dài {len(text)} ký tự]"
    return text
