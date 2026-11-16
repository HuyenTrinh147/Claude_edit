"""Hard-rule checks for the on-screen text of an EditPlan (texts + captions): the part of "Soát chữ" that needs no
judgement. Spelling, tone and fact-checking stay with the `video-text-checker` agent, which reads this report first.

Rules come from the project's content gate: reading time >= chars/15 + 0.5 s, <= 2 lines, <= 8 syllables per line,
text centres inside the canvas safe area, NFC Vietnamese, no clashing overlays.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field

from .edl import EditPlan

MAX_LINES = 2
MAX_WORDS_PER_LINE = 8
CHARS_PER_SECOND = 15
BASE_SECONDS = 0.5
POSITION_Y = {"top": 0.12, "upper": 0.3, "center": 0.5, "lower": 0.72, "bottom": 0.88}
VIET_DIACRITICS = re.compile(r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]", re.I)


@dataclass
class Finding:
    level: str            # "error" | "warn"
    rule: str
    where: str            # e.g. "texts[3] 2.70-5.34 s"
    text: str
    message: str


@dataclass
class TextReport:
    findings: list[Finding] = field(default_factory=list)
    checked: int = 0

    @property
    def errors(self) -> int:
        return sum(f.level == "error" for f in self.findings)

    @property
    def warnings(self) -> int:
        return sum(f.level == "warn" for f in self.findings)

    def to_dict(self) -> dict:
        return {"checked": self.checked, "errors": self.errors, "warnings": self.warnings,
                "findings": [asdict(f) for f in self.findings]}

    def to_markdown(self) -> str:
        lines = ["# Soát chữ (luật cứng)", "",
                 f"Đã kiểm {self.checked} dòng chữ · {self.errors} lỗi · {self.warnings} cảnh báo", ""]
        if not self.findings:
            lines.append("Không phát hiện vi phạm luật cứng. Chính tả, giọng điệu và dữ kiện vẫn cần người / agent đọc.")
        for f in self.findings:
            lines.append(f"- **{'LỖI' if f.level == 'error' else 'cảnh báo'}** `{f.rule}` · {f.where} · “{f.text}” — {f.message}")
        return "\n".join(lines) + "\n"


def _syllables(line: str) -> int:
    return len([w for w in re.split(r"\s+", line.strip()) if re.search(r"\w", w)])


def check_plan(plan: EditPlan) -> TextReport:
    report = TextReport()
    total = plan.duration
    x0, y0, x1, y1 = plan.canvas.safe_area

    def add(level, rule, where, text, message):
        report.findings.append(Finding(level, rule, where, text.replace("\n", " / "), message))

    items = [(f"texts[{i}] {t.start:.2f}-{t.end:.2f} s", t.text, t.start, t.end, t.x, t.y if t.y is not None else POSITION_Y[t.position], t.size)
             for i, t in enumerate(plan.texts)]
    if plan.captions:
        items += [(f"captions[{i}] {c.start:.2f}-{c.end:.2f} s", c.text, c.start, c.end, None, POSITION_Y[plan.captions.position], plan.captions.size)
                  for i, c in enumerate(plan.captions.segments)]
    report.checked = len(items)

    for where, text, start, end, x, y, size in items:
        lines = [ln for ln in text.split("\n") if ln.strip()]
        flat = " ".join(lines)
        if unicodedata.normalize("NFC", text) != text:
            add("error", "nfc", where, text, "Dấu tiếng Việt chưa ở dạng dựng sẵn (NFC): dễ hiện lỗi font.")
        if "�" in text or "  " in text.strip():
            add("warn", "ky-tu-la", where, text, "Có ký tự lỗi hoặc hai khoảng trắng liền nhau.")
        need = len(flat) / CHARS_PER_SECOND + BASE_SECONDS
        if end - start < need - 1e-6:
            add("error", "thoi-gian-doc", where, text,
                f"Hiện {end - start:.2f} s, cần ≥ {need:.2f} s ({len(flat)} ký tự / {CHARS_PER_SECOND} + {BASE_SECONDS}).")
        if len(lines) > MAX_LINES:
            add("error", "so-dong", where, text, f"{len(lines)} dòng, tối đa {MAX_LINES}.")
        for ln in lines:
            if _syllables(ln) > MAX_WORDS_PER_LINE:
                add("warn", "dong-dai", where, text, f"Một dòng có {_syllables(ln)} tiếng, nên ≤ {MAX_WORDS_PER_LINE}.")
                break
        if end > total + 0.05:
            add("warn", "qua-het-video", where, text, f"Kết thúc {end:.2f} s sau khi video hết ({total:.2f} s).")
        if y is not None and not (y0 <= y <= y1):
            add("error", "vung-an-toan", where, text,
                f"Tâm dọc y={y:.2f} nằm ngoài vùng an toàn [{y0:.2f}, {y1:.2f}] (bị nút/chú thích che).")
        if x is not None and not (x0 <= x <= x1):
            add("error", "vung-an-toan", where, text, f"Tâm ngang x={x:.2f} nằm ngoài vùng an toàn [{x0:.2f}, {x1:.2f}].")
        letters = re.sub(r"[^A-Za-zÀ-ỹĐđ]", "", flat)
        if len(flat) >= 12 and letters and not VIET_DIACRITICS.search(flat) and not flat.isupper():
            add("warn", "thieu-dau", where, text, "Câu dài không có dấu tiếng Việt nào — có thể đã mất dấu.")

    # two overlays at nearly the same height and time read as a clash
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            (wi, ti, si, ei, _xi, yi, _zi), (wj, _tj, sj, ej, _xj, yj, _zj) = items[i], items[j]
            overlap = min(ei, ej) - max(si, sj)
            if overlap > 0.15 and abs(yi - yj) < 0.06:
                add("warn", "chong-chu", f"{wi} & {wj}", ti, f"Hai chữ chồng nhau {overlap:.2f} s ở cùng độ cao.")
    return report
