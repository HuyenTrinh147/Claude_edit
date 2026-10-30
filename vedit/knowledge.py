"""Knowledge base: markdown notes written by Agent 1 and read by Agents 2 and 3.

Layout: knowledge/<category>/<slug>.md with a small front-matter header, plus an
auto-generated knowledge/INDEX.md for browsing.
"""

from __future__ import annotations

import datetime as dt
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

CATEGORIES: dict[str, str] = {
    "techniques": "Kỹ thuật dựng: nhịp cắt, chuyển cảnh, J/L-cut, zoom, màu, hiệu ứng",
    "scripting": "Kịch bản: hook, cấu trúc, storytelling, CTA, viết lời thoại",
    "trends": "Xu hướng & format đang hot trên TikTok / Reels / Shorts",
    "platforms": "Đặc thù nền tảng: kích thước, độ dài, vùng an toàn, thuật toán phân phối",
    "audio": "Âm thanh: nhạc nền, giọng đọc, SFX, loudness",
    "tools": "Công cụ, thư viện, repo GitHub hữu ích cho dựng video tự động",
    "ffmpeg": "Công thức ffmpeg / tự động hoá dựng video",
}


def strip_accents(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def slugify(text: str, max_len: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", strip_accents(text).lower()).strip("-")
    return slug[:max_len].rstrip("-") or "note"


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", strip_accents(text).lower()) if len(t) >= 2]


@dataclass
class Note:
    path: Path
    title: str
    category: str
    tags: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    updated: str = ""
    body: str = ""

    @property
    def slug(self) -> str:
        return self.path.stem

    @property
    def ref(self) -> str:
        return f"{self.category}/{self.slug}"


def _parse(path: Path) -> Note:
    raw = path.read_text(encoding="utf-8")
    meta: dict[str, object] = {"sources": []}
    body = raw
    if raw.startswith("---\n"):
        end = raw.find("\n---", 4)
        if end != -1:
            header, body = raw[4:end], raw[end + 4:].lstrip("\n")
            current = None
            for line in header.splitlines():
                if line.startswith("  - ") and current == "sources":
                    meta["sources"].append(line[4:].strip())  # type: ignore[union-attr]
                elif ":" in line:
                    key, value = line.split(":", 1)
                    current = key.strip()
                    if current != "sources":
                        meta[current] = value.strip()
    tags = [t.strip() for t in str(meta.get("tags", "")).strip("[]").split(",") if t.strip()]
    return Note(path=path, title=str(meta.get("title", path.stem)), category=str(meta.get("category", path.parent.name)),
                tags=tags, sources=list(meta["sources"]), updated=str(meta.get("updated", "")),  # type: ignore[arg-type]
                body=body)


class KnowledgeBase:
    def __init__(self, root: Path):
        self.root = Path(root)

    def notes(self, category: str | None = None) -> list[Note]:
        if not self.root.exists():
            return []
        pattern = f"{category}/*.md" if category else "*/*.md"
        return sorted((_parse(p) for p in self.root.glob(pattern)), key=lambda n: (n.category, n.title))

    def get(self, ref: str) -> Note | None:
        ref = ref.strip().removesuffix(".md")
        if "/" in ref:
            path = self.root / f"{ref}.md"
            return _parse(path) if path.exists() else None
        matches = list(self.root.glob(f"*/{ref}.md"))
        return _parse(matches[0]) if matches else None

    def save(self, title: str, category: str, content: str, tags: list[str] | None = None,
             sources: list[str] | None = None) -> Note:
        if category not in CATEGORIES:
            raise ValueError(f"category phải là một trong: {', '.join(CATEGORIES)}")
        path = self.root / category / f"{slugify(title)}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        tags = [t.strip() for t in (tags or []) if t.strip()]
        sources = [s.strip() for s in (sources or []) if s.strip()]
        header = ["---", f"title: {title.strip()}", f"category: {category}", f"tags: [{', '.join(tags)}]",
                  f"updated: {dt.date.today().isoformat()}", "sources:"] + [f"  - {s}" for s in sources] + ["---", ""]
        body = content.strip()
        if not body.startswith("#"):
            body = f"# {title.strip()}\n\n{body}"
        path.write_text("\n".join(header) + body + "\n", encoding="utf-8")
        self.write_index()
        return _parse(path)

    def search(self, query: str, limit: int = 8, category: str | None = None) -> list[tuple[Note, float, str]]:
        terms = set(_tokens(query))
        if not terms:
            return []
        results = []
        for note in self.notes(category):
            title_t, tag_t = set(_tokens(note.title)), set(_tokens(" ".join(note.tags)))
            body_tokens = _tokens(note.body)
            body_counts: dict[str, int] = {}
            for tok in body_tokens:
                if tok in terms:
                    body_counts[tok] = body_counts.get(tok, 0) + 1
            score = 3 * len(terms & title_t) + 2 * len(terms & tag_t) + sum(min(c, 5) for c in body_counts.values()) * 0.5
            score += 1.5 * len(body_counts)  # reward covering more distinct terms
            if score > 0:
                results.append((note, round(score, 2), self._snippet(note.body, terms)))
        results.sort(key=lambda r: -r[1])
        if results:  # drop weak matches (e.g. a lone stripped-accent collision) far below the best hit
            cutoff = results[0][1] * 0.2
            results = [r for r in results if r[1] >= cutoff]
        return results[:limit]

    @staticmethod
    def _snippet(body: str, terms: set[str], width: int = 240) -> str:
        plain = strip_accents(body).lower()
        positions = [plain.find(t) for t in terms if plain.find(t) >= 0]
        start = max(min(positions) - 60, 0) if positions else 0
        return re.sub(r"\s+", " ", body[start:start + width]).strip()

    def write_index(self) -> Path:
        lines = ["# Kho kiến thức dựng video", "", "_Tự động tạo bởi vedit — đừng sửa tay._", ""]
        for category, desc in CATEGORIES.items():
            notes = self.notes(category)
            if not notes:
                continue
            lines += [f"## {category} — {desc}", ""]
            lines += [f"- [{n.title}]({category}/{n.path.name})" + (f" — _{', '.join(n.tags)}_" if n.tags else "")
                      for n in notes]
            lines.append("")
        index = self.root / "INDEX.md"
        self.root.mkdir(parents=True, exist_ok=True)
        index.write_text("\n".join(lines), encoding="utf-8")
        return index

    def overview(self) -> str:
        """Compact list of all notes, to put into an agent prompt."""
        notes = self.notes()
        if not notes:
            return "(kho kiến thức đang trống)"
        return "\n".join(f"- {n.ref}: {n.title}" + (f" [{', '.join(n.tags[:5])}]" if n.tags else "") for n in notes)
