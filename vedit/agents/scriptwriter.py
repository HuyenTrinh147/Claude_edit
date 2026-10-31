"""Agent 2 — Trend & script strategist: analyses the user's video, researches current trends and
keywords, writes a short-video script and an EditPlan for Agent 3."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from anthropic import beta_tool
from anthropic.lib.tools import ToolError
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..config import Settings
from ..edl import CANVAS_PRESETS
from ..knowledge import KnowledgeBase
from ..media import image_block
from ..project import Project
from .base import AgentError, AgentRun, run_agent, web_tools
from .tools import format_validation_error, frame_tools, knowledge_tools, list_assets_tool, plan_tools, research_tools

PLATFORMS = {
    "tiktok": "TikTok (9:16, 1080x1920)",
    "reels": "Instagram/Facebook Reels (9:16, 1080x1920)",
    "shorts": "YouTube Shorts (9:16, 1080x1920, tối đa 3 phút)",
    "youtube": "YouTube ngang (16:9, 1920x1080)",
    "square": "Bài đăng vuông (1:1, 1080x1080)",
}


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TrendInsight(_Model):
    trend: str = Field(description="Tên xu hướng / format / âm thanh / chủ đề đang hot")
    evidence: str = Field(description="Bằng chứng: nguồn, link, số liệu đã thấy (ghi rõ nếu chỉ là nhận định)")
    how_to_apply: str = Field(description="Áp dụng cụ thể vào video này như thế nào")


class ScriptScene(_Model):
    start: float = Field(ge=0, description="Bắt đầu trên timeline video xuất (giây)")
    end: float = Field(gt=0, description="Kết thúc trên timeline video xuất (giây)")
    purpose: str = Field(description="Vai trò: hook, vấn đề, nội dung chính, twist, CTA...")
    visual: str = Field(description="Hình ảnh: cảnh nào trong video nguồn (mốc giây nguồn), góc máy, hiệu ứng")
    voiceover: str = Field("", description="Lời thoại / giọng đọc (nếu có)")
    on_screen_text: str = Field("", description="Chữ trên màn hình")
    edit_notes: str = Field("", description="Ghi chú dựng: nhịp cắt, transition, zoom, SFX")


class ScriptDoc(_Model):
    title: str = Field(description="Tiêu đề chọn dùng")
    title_options: list[str] = Field(min_length=2, description="3-5 phương án tiêu đề")
    hook: str = Field(description="Hook chọn dùng cho 1-3 giây đầu")
    hook_options: list[str] = Field(min_length=2, description="3-5 phương án hook")
    concept: str = Field(description="Ý tưởng / góc tiếp cận chính và lý do chọn")
    target_audience: str
    platform: str
    duration_target: float = Field(gt=0)
    trend_insights: list[TrendInsight] = Field(min_length=1)
    keywords: list[str] = Field(min_length=3, description="Từ khoá SEO / tìm kiếm trong app")
    hashtags: list[str] = Field(min_length=3)
    post_caption: str = Field(description="Caption đăng kèm video")
    scenes: list[ScriptScene] = Field(min_length=1)
    music_direction: str = Field(description="Hướng chọn nhạc/âm thanh (thể loại, BPM, trend sound nếu có)")
    cta: str
    posting_tips: list[str] = Field(default_factory=list, description="Giờ đăng, cách tương tác, series...")
    sources: list[str] = Field(default_factory=list, description="URL tham khảo đã đọc")


class Concept(_Model):
    name: str = Field(description="Tên ngắn của hướng dựng")
    idea: str = Field(description="Ý tưởng 1-2 câu: video này là gì, người xem cảm thấy gì")
    style: str = Field(description="Phong cách tham chiếu (silent vlog/ASMR, velocity, Hormozi, cinematic, game HUD/AR...)")
    hook: str = Field(description="0-2 giây đầu: hình, chữ, âm thanh")
    beats: list[str] = Field(min_length=2, description="Chuỗi beat kèm mốc giây NGUỒN, vd '20.5-21.6s hũ thành phẩm (hook)'")
    pacing: str = Field(description="Nhịp: độ dài cảnh, chỗ dồn, chỗ thở, speed ramp / dừng hình")
    typography: str = Field(description="Font (từ thư viện assets/fonts), màu, kiểu chữ, lượng chữ")
    signature_moves: list[str] = Field(min_length=2, max_length=6, description="3-5 chiêu chữ ký của phong cách")
    audio: str = Field(description="Tiếng gốc / nhạc / SFX (ghi ngân sách SFX)")
    color: str = Field(description="Màu / look")
    duration: float = Field(gt=0, description="Độ dài dự kiến (giây)")
    why: str = Field(description="Vì sao hợp mục tiêu và gu người dùng")
    risks: str = Field("", description="Rủi ro / điều người dùng cần quyết")
    new_features: list[str] = Field(default_factory=list, description="Tính năng vedit còn thiếu mà hướng này cần")


class ConceptSet(_Model):
    understanding: str = Field(description="Agent hiểu video thế nào: nội dung, khoảnh khắc mạnh, âm thanh, điểm yếu")
    questions: list[str] = Field(default_factory=list, max_length=3, description="Câu hỏi còn mở cho người dùng")
    concepts: list[Concept] = Field(min_length=2, max_length=3, description="2-3 hướng dựng KHÁC HẲN nhau")


def concepts_markdown(cs: ConceptSet, project: Project) -> str:
    lines = [f"# Hướng dựng đề xuất — {project.slug}", "", "## Agent hiểu video thế nào", "", cs.understanding, ""]
    for k, c in enumerate(cs.concepts, start=1):
        lines += [
            f"## {k}. {c.name}", "", f"**Ý tưởng:** {c.idea}", "",
            f"- **Phong cách:** {c.style}", f"- **Hook (0–2s):** {c.hook}", f"- **Nhịp:** {c.pacing}",
            f"- **Chữ:** {c.typography}", f"- **Âm thanh:** {c.audio}", f"- **Màu:** {c.color}",
            f"- **Độ dài:** ~{c.duration:g}s", "", "**Chuỗi beat:**", *[f"{i}. {b}" for i, b in enumerate(c.beats, 1)], "",
            "**Chiêu chữ ký:** " + " · ".join(c.signature_moves), "", f"**Vì sao hợp:** {c.why}",
        ]
        if c.risks:
            lines.append(f"**Cần lưu ý:** {c.risks}")
        if c.new_features:
            lines.append("**Cần thêm tính năng:** " + "; ".join(c.new_features))
        lines.append("")
    if cs.questions:
        lines += ["## Câu hỏi cho bạn", "", *[f"- {q}" for q in cs.questions], ""]
    return "\n".join(lines)


def load_concepts(project: Project) -> ConceptSet | None:
    path = project.script_dir / "concepts.json"
    return ConceptSet.model_validate_json(path.read_text(encoding="utf-8")) if path.exists() else None


def _context_block(settings: Settings, project: Project) -> str:
    """User taste profile + project memory: read before proposing or building anything."""
    parts = []
    if settings.profile_path.exists():
        parts.append("## Gu & phản hồi của người dùng (profile/gu-nguoi-dung.md)\n"
                     + settings.profile_path.read_text(encoding="utf-8"))
    if project.memory_path.exists():
        parts.append("## Nhật ký dự án (project.md)\n" + project.memory_path.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def _rules(kb: KnowledgeBase) -> str:
    note = kb.get("techniques/tu-duy-dung-sang-tao-cho-video-ngan")
    return note.body if note else ""


def _cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|") or "—"


def script_markdown(doc: ScriptDoc, project: Project) -> str:
    lines = [
        f"# {doc.title}", "",
        f"**Nền tảng:** {doc.platform} · **Thời lượng:** ~{doc.duration_target:g}s · **Khán giả:** {doc.target_audience}",
        f"**Video nguồn:** `{project.input_path.name}` · **Dự án:** `{project.slug}`", "",
        "## Ý tưởng", "", doc.concept, "",
        "## Hook (1-3 giây đầu)", "", f"**Chọn:** {doc.hook}", "",
        *[f"- {h}" for h in doc.hook_options], "",
        "## Phương án tiêu đề", "", *[f"- {t}" for t in doc.title_options], "",
        "## Insight xu hướng", "", "| Xu hướng | Bằng chứng | Áp dụng |", "|---|---|---|",
        *[f"| {_cell(t.trend)} | {_cell(t.evidence)} | {_cell(t.how_to_apply)} |" for t in doc.trend_insights], "",
        "## Kịch bản chi tiết", "",
        "| Thời gian | Mục đích | Hình ảnh | Lời thoại | Chữ trên màn hình | Ghi chú dựng |", "|---|---|---|---|---|---|",
        *[f"| {s.start:.1f}–{s.end:.1f}s | {_cell(s.purpose)} | {_cell(s.visual)} | {_cell(s.voiceover)} | "
          f"{_cell(s.on_screen_text)} | {_cell(s.edit_notes)} |" for s in doc.scenes], "",
        "## Nhạc & âm thanh", "", doc.music_direction, "",
        "## CTA", "", doc.cta, "",
        "## Caption đăng bài", "", doc.post_caption, "", " ".join(doc.hashtags), "",
        "## Từ khoá", "", ", ".join(doc.keywords), "",
    ]
    if doc.posting_tips:
        lines += ["## Mẹo đăng", "", *[f"- {t}" for t in doc.posting_tips], ""]
    if doc.sources:
        lines += ["## Nguồn tham khảo", "", *[f"- {s}" for s in doc.sources], ""]
    lines += [f"_Tạo bởi vedit Agent 2 — {dt.datetime.now():%Y-%m-%d %H:%M}_", ""]
    return "\n".join(lines)


def analysis_brief(analysis: dict, max_transcript_chars: int = 30000) -> str:
    m = analysis["media"]
    lines = [
        f"File: {Path(analysis['source']).name} — {m['width']}x{m['height']} ({m['orientation']}), {m['fps']}fps, "
        f"{m['duration']:.2f}s, âm thanh: {'có' if m['has_audio'] else 'không'}"
        + (f", mean {analysis['loudness'].get('mean_db')} dB" if analysis.get("loudness") else ""),
        "",
        f"Cảnh (scene detection, {len(analysis['scenes'])} cảnh, mốc giây NGUỒN):",
        *[f"  #{i} {s['start']:.2f}–{s['end']:.2f}s ({s['duration']:.1f}s)" for i, s in enumerate(analysis["scenes"][:120])],
    ]
    if analysis["silences"]:
        lines += ["", "Khoảng lặng (có thể cắt bỏ):",
                  *[f"  {s['start']:.2f}–{s['end']:.2f}s" for s in analysis["silences"][:80]]]
    transcript = analysis.get("transcript")
    lines.append("")
    if transcript:
        text = "\n".join(f"  [{seg['start']:.2f}–{seg['end']:.2f}] {seg['text']}" for seg in transcript)
        if len(text) > max_transcript_chars:
            text = text[:max_transcript_chars] + "\n  [... transcript bị cắt bớt]"
        lines += [f"Transcript ({analysis.get('transcript_source')}, mốc giây NGUỒN):", text]
    elif m["has_audio"]:
        lines.append("Transcript: (không có — chưa cài faster-whisper và không có file .srt). Dựa vào hình ảnh; "
                     "nếu cần phụ đề, để trống captions và ghi chú trong kịch bản.")
    else:
        lines.append("Transcript: video không có tiếng.")
    return "\n".join(lines)


SYSTEM_CONCEPTS = """Bạn là Agent 2 — Chiến lược gia nội dung & biên kịch video ngắn trong hệ thống "vedit".

Nhiệm vụ lúc này: ĐỀ XUẤT HƯỚNG DỰNG để người dùng chọn — chưa viết kịch bản, chưa viết EditPlan.

1. Hiểu video thật kỹ: nội dung, khoảnh khắc mạnh (mốc giây nguồn), âm thanh, điểm yếu. Dùng view_frames khi cần.
2. Đọc gu & phản hồi cũ của người dùng (trong tin nhắn) — tránh lặp lại thứ họ đã chê.
3. Tìm hiểu xu hướng THỰC TẾ, gần đây (web_search, kho kiến thức kb_search/kb_read). Chỉ nêu điều có bằng chứng.
4. Gọi save_concepts với 2-3 hướng dựng KHÁC HẲN nhau về phong cách và cấu trúc (không phải 3 biến thể của một ý):
   thường 1 hướng an toàn bám mục tiêu, 1-2 hướng táo bạo. Nếu người dùng đã nêu ý tưởng riêng, ít nhất một hướng
   phải phát triển đúng ý tưởng đó. Mỗi hướng dùng 3-5 chiêu chữ ký của phong cách đó, chỉ dùng cảnh có thật,
   ghi rõ tính năng vedit còn thiếu nếu hướng đó cần (đối chiếu kb 'techniques/ban-do-nang-luc-dung-vedit-da-co-va-con-thieu').
5. Kết thúc bằng 2-4 câu tóm tắt — người điều phối sẽ đưa các hướng cho người dùng chọn."""


SYSTEM = """Bạn là Agent 2 — Chiến lược gia nội dung & biên kịch video ngắn trong hệ thống "vedit".

Người dùng ĐÃ CHỌN một hướng dựng (trong tin nhắn, kèm ghi chú của họ). Nhiệm vụ: biến hướng đó thành (1) kịch bản
chi tiết và (2) EditPlan để Agent 3 dựng bằng ffmpeg — trung thành với hướng đã duyệt, không tự đổi phong cách.

Quy trình gợi ý:
1. Đọc lại hướng đã duyệt, gu người dùng và nhật ký dự án (trong tin nhắn). Xem khung hình khi cần chọn điểm cắt.
2. Bổ sung nghiên cứu nếu cần (hashtag, từ khoá, âm thanh trend) — chỉ nêu điều có bằng chứng, ghi nguồn.
3. Gọi save_script với kịch bản hoàn chỉnh, rồi save_edit_plan với EditPlan khớp kịch bản (công cụ kiểm tra với media
   thật và font; báo lỗi thì sửa và gọi lại).

Kỹ thuật EditPlan:
- Video gốc là source "main". Clip.start/end là giây NGUỒN; texts/captions/graphics/motion/audio là giây TIMELINE
  (mỗi clip chiếm (end-start)/speed giây; transition làm 2 clip kề nhau chồng lấn).
- canvas theo nền tảng. Video ngang sang khung dọc: fit "cover" + focus_x vào chủ thể, hoặc "blur".
- Có transcript: captions với mốc đã quy đổi theo đoạn cắt. Âm thanh: file thật (list_assets) hoặc 'sfx:<tên>'.
- Đo vị trí x/y cho chữ & đồ hoạ bằng view_frames(grid=true). Đặt export.thumbnail_at vào khung hình đẹp nhất.
- Bảng công cụ (tra cứu, không bắt buộc): kb_read('techniques/bo-cong-cu-do-hoa-hieu-ung-cua-vedit').

Luật dựng — luật cứng phải tuân thủ, phần sáng tạo là nguyên tắc:
{rules}

Cuối cùng, tóm tắt ngắn: hướng đã dựng theo, hook, độ dài, và điều người dùng nên xem kỹ."""


def _brief(settings: Settings, project: Project, analysis: dict, kb: KnowledgeBase, *, goal: str, platform: str,
           duration: float, style: str | None, audience: str | None, extra: list[str]) -> list[dict]:
    width, height = CANVAS_PRESETS.get(platform, CANVAS_PRESETS["tiktok"])
    lines = [
        f"Hôm nay là {dt.date.today().isoformat()}.",
        f"Mục tiêu của người dùng: {goal}",
        f"Nền tảng: {PLATFORMS.get(platform, platform)} → canvas {width}x{height}.",
        f"Độ dài mong muốn: khoảng {duration:g} giây.",
        f"Ngôn ngữ: {settings.lang}.",
    ]
    if style:
        lines.append(f"Phong cách mong muốn: {style}")
    if audience:
        lines.append(f"Khán giả mục tiêu: {audience}")
    lines += extra
    text = ("\n".join(lines) + "\n\n" + _context_block(settings, project) + "\n\n## Phân tích video\n"
            + analysis_brief(analysis) + "\n\n## Kho kiến thức hiện có\n" + kb.overview()
            + "\n\n## Khung hình đại diện (mốc giây nguồn)")
    content: list[dict] = [{"type": "text", "text": text}]
    for frame in analysis["frames"]:
        path = project.analysis_dir / frame["file"]
        if path.exists():
            content += [{"type": "text", "text": f"t={frame['time']:.2f}s"}, image_block(path)]
    return content


def run_concepts(
    settings: Settings,
    project: Project,
    *,
    goal: str,
    platform: str = "tiktok",
    duration: float = 30,
    style: str | None = None,
    audience: str | None = None,
    idea: str | None = None,
    quiet: bool = False,
) -> ConceptSet:
    """Phase 1: propose 2-3 contrasting concepts for the user to choose from (no script, no EditPlan yet)."""
    analysis = project.analysis()
    if analysis is None:
        raise AgentError("Dự án chưa được phân tích — chạy 'vedit analyze' trước.")
    kb = KnowledgeBase(settings.knowledge_dir)
    saved: dict[str, ConceptSet] = {}

    def save_concepts(**data) -> str:
        """Lưu 2-3 hướng dựng đề xuất (concepts.json + concepts.md) để người dùng chọn."""
        try:
            cs = ConceptSet.model_validate(data)
        except ValidationError as e:
            raise ToolError("Hướng dựng chưa hợp lệ, sửa rồi gọi lại:\n" + format_validation_error(e)) from e
        project.script_dir.mkdir(parents=True, exist_ok=True)
        (project.script_dir / "concepts.json").write_text(cs.model_dump_json(indent=2), encoding="utf-8")
        (project.script_dir / "concepts.md").write_text(concepts_markdown(cs, project), encoding="utf-8")
        saved["concepts"] = cs
        return f"Đã lưu {len(cs.concepts)} hướng dựng vào script/concepts.md."

    extra = [f"Ý tưởng riêng của người dùng (phải có một hướng phát triển đúng ý này): {idea}"] if idea else []
    content = _brief(settings, project, analysis, kb, goal=goal, platform=platform, duration=duration, style=style,
                     audience=audience, extra=extra)
    tools = [*web_tools(max_searches=8, max_fetches=6), *knowledge_tools(kb, writable=False), *frame_tools(project),
             *list_assets_tool(settings), beta_tool(save_concepts, input_schema=ConceptSet.model_json_schema())]
    project.data["brief"] = {"goal": goal, "platform": platform, "duration": duration, "style": style,
                             "audience": audience, "idea": idea}
    project.save()
    run_agent(settings, label="Agent2·Concepts", system=SYSTEM_CONCEPTS, prompt=content, tools=tools,
              effort=settings.effort_script, max_iterations=40, quiet=quiet)
    if "concepts" not in saved:
        raise AgentError("Agent 2 kết thúc nhưng chưa lưu hướng dựng. Chạy lại 'vedit concepts'.")
    project.note(f"đề xuất {len(saved['concepts'].concepts)} hướng dựng: "
                 + " | ".join(c.name for c in saved["concepts"].concepts), "Agent 2")
    return saved["concepts"]


def run_scriptwriter(
    settings: Settings,
    project: Project,
    *,
    goal: str,
    platform: str = "tiktok",
    duration: float = 30,
    style: str | None = None,
    audience: str | None = None,
    concept: Concept | None = None,
    notes: str | None = None,
    quiet: bool = False,
) -> AgentRun:
    """Phase 2: script + EditPlan for the concept the user approved."""
    analysis = project.analysis()
    if analysis is None:
        raise AgentError("Dự án chưa được phân tích — chạy 'vedit analyze' trước.")
    kb = KnowledgeBase(settings.knowledge_dir)
    saved: dict[str, bool] = {"script": False, "plan": False}

    def save_script(**data) -> str:
        """Lưu kịch bản hoàn chỉnh (script.json + script.md dễ đọc) vào dự án. Gửi toàn bộ kịch bản mỗi lần gọi."""
        try:
            script = ScriptDoc.model_validate(data)
        except ValidationError as e:
            raise ToolError("Kịch bản chưa hợp lệ, sửa rồi gọi lại:\n" + format_validation_error(e)) from e
        project.script_dir.mkdir(parents=True, exist_ok=True)
        (project.script_dir / "script.json").write_text(script.model_dump_json(indent=2), encoding="utf-8")
        (project.script_dir / "script.md").write_text(script_markdown(script, project), encoding="utf-8")
        saved["script"] = True
        return f"Đã lưu script.md ({len(script.scenes)} cảnh). Tiếp theo: save_edit_plan."

    def on_plan_saved(_plan) -> None:
        saved["plan"] = True

    extra = []
    if concept:
        extra.append("## Hướng dựng người dùng ĐÃ DUYỆT\n" + concept.model_dump_json(indent=1))
    if notes:
        extra.append(f"Ghi chú thêm của người dùng: {notes}")
    content = _brief(settings, project, analysis, kb, goal=goal, platform=platform, duration=duration, style=style,
                     audience=audience, extra=extra)

    tools = [*web_tools(max_searches=12, max_fetches=10), *research_tools(settings), *knowledge_tools(kb, writable=False),
             *list_assets_tool(settings), *frame_tools(project),
             beta_tool(save_script, input_schema=ScriptDoc.model_json_schema()),
             *plan_tools(project, on_save=on_plan_saved, font=settings.font, fonts_dir=settings.fonts_dir)]
    project.data["brief"] = {"goal": goal, "platform": platform, "duration": duration, "style": style,
                             "audience": audience}
    project.save()
    run = run_agent(settings, label="Agent2·Script", system=SYSTEM.format(rules=_rules(kb)), prompt=content, tools=tools,
                    effort=settings.effort_script, max_iterations=60, quiet=quiet)
    missing = [k for k, ok in saved.items() if not ok]
    if missing:
        raise AgentError(f"Agent 2 kết thúc nhưng chưa lưu: {', '.join(missing)}. Chạy lại 'vedit script'.")
    return run


def load_script(project: Project) -> ScriptDoc | None:
    path = project.script_dir / "script.json"
    return ScriptDoc.model_validate(json.loads(path.read_text(encoding="utf-8"))) if path.exists() else None

