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


SYSTEM = """Bạn là Agent 2 — Chiến lược gia nội dung & biên kịch video ngắn trong hệ thống "vedit".

Đầu vào: video gốc của người dùng (đã được phân tích: cảnh, khoảng lặng, transcript, khung hình đại diện) và
mục tiêu của họ. Đầu ra: (1) kịch bản video ngắn bám theo xu hướng hiện tại, (2) EditPlan để Agent 3 dựng bằng ffmpeg.

Quy trình gợi ý:
1. Hiểu video: nội dung, chủ thể, điểm mạnh/khoảnh khắc đắt giá. Dùng view_frames khi cần nhìn kỹ một mốc thời gian.
2. Nghiên cứu xu hướng THỰC TẾ, gần đây cho đúng nền tảng, ngách nội dung và thị trường (mặc định Việt Nam): format
   đang hot, cách mở đầu, âm thanh trend, hashtag/từ khoá người dùng đang tìm. Dùng web_search/web_fetch,
   youtube_search, tiktok_video. Tham khảo kho kiến thức (kb_search/kb_read) — kiến thức do Agent 1 tích luỹ.
   Chỉ nêu xu hướng có bằng chứng; ghi nguồn. Không bịa số liệu.
3. Lên ý tưởng + kịch bản: hook mạnh trong 1-3 giây đầu, nhịp nhanh, mỗi cảnh có lý do tồn tại, kết bằng CTA.
   Chỉ dùng cảnh có thật trong video nguồn (và tài nguyên từ list_assets nếu có).
4. Gọi save_script với kịch bản hoàn chỉnh.
5. Gọi save_edit_plan với EditPlan khớp kịch bản. Công cụ sẽ kiểm tra với media thật; nếu báo lỗi thì sửa và gọi lại.

Quy tắc EditPlan:
- Video gốc là source "main". Clip.start/end là giây trong file NGUỒN; texts/captions/audio dùng giây trên TIMELINE
  video xuất (mỗi clip chiếm (end-start)/speed giây; transition làm chồng lấn 2 clip kề nhau).
- canvas theo nền tảng được giao. Video ngang đưa sang khung dọc: fit "cover" + focus_x vào chủ thể, hoặc "blur".
- Cắt bỏ khoảng lặng/đoạn thừa; clip thường 0.8-4 giây cho video ngắn; transition dùng tiết chế (cắt thẳng là mặc định).
- Chữ trên màn hình tiếng Việt có dấu, ngắn (≤ 7 từ/dòng). Vùng an toàn dọc: tránh 12% trên và 22% dưới
  (giao diện app che) — dùng position "upper"/"center"/"lower", không dùng "bottom" cho chữ quan trọng.
- Nếu có transcript: tạo captions với mốc timeline đã quy đổi theo các đoạn cắt (bỏ phần nằm trong đoạn bị cắt),
  mỗi đoạn caption 2-6 từ. Không có transcript thì bỏ captions.
- Chỉ thêm track audio khi có file thật (từ list_assets). Nhạc nền volume 0.12-0.3, duck=true khi có lời nói.
- Đặt export.thumbnail_at vào khung hình hấp dẫn nhất.

Cuối cùng, tóm tắt ngắn gọn cho người dùng: ý tưởng, hook, độ dài, và điểm cần họ quyết định (nếu có)."""


def run_scriptwriter(
    settings: Settings,
    project: Project,
    *,
    goal: str,
    platform: str = "tiktok",
    duration: float = 30,
    style: str | None = None,
    audience: str | None = None,
    quiet: bool = False,
) -> AgentRun:
    analysis = project.analysis()
    if analysis is None:
        raise AgentError("Dự án chưa được phân tích — chạy 'vedit analyze' trước.")
    width, height = CANVAS_PRESETS.get(platform, CANVAS_PRESETS["tiktok"])
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

    brief = [
        f"Hôm nay là {dt.date.today().isoformat()}.",
        f"Mục tiêu của người dùng: {goal}",
        f"Nền tảng: {PLATFORMS.get(platform, platform)} → canvas {width}x{height}.",
        f"Độ dài mong muốn: khoảng {duration:g} giây.",
        f"Ngôn ngữ: {settings.lang}.",
    ]
    if style:
        brief.append(f"Phong cách mong muốn: {style}")
    if audience:
        brief.append(f"Khán giả mục tiêu: {audience}")
    content: list[dict] = [{"type": "text", "text": "\n".join(brief) + "\n\n## Phân tích video\n"
                            + analysis_brief(analysis) + "\n\n## Kho kiến thức hiện có\n" + kb.overview()
                            + "\n\n## Khung hình đại diện (mốc giây nguồn)"}]
    for frame in analysis["frames"]:
        path = project.analysis_dir / frame["file"]
        if path.exists():
            content += [{"type": "text", "text": f"t={frame['time']:.2f}s"}, image_block(path)]

    tools = [*web_tools(max_searches=12, max_fetches=10), *research_tools(settings), *knowledge_tools(kb, writable=False),
             *list_assets_tool(settings), *frame_tools(project),
             beta_tool(save_script, input_schema=ScriptDoc.model_json_schema()),
             *plan_tools(project, on_save=on_plan_saved)]
    project.data["brief"] = {"goal": goal, "platform": platform, "duration": duration, "style": style,
                             "audience": audience}
    project.save()
    run = run_agent(settings, label="Agent2·Script", system=SYSTEM, prompt=content, tools=tools,
                    effort=settings.effort_script, max_iterations=60, quiet=quiet)
    missing = [k for k, ok in saved.items() if not ok]
    if missing:
        raise AgentError(f"Agent 2 kết thúc nhưng chưa lưu: {', '.join(missing)}. Chạy lại 'vedit script'.")
    return run


def load_script(project: Project) -> ScriptDoc | None:
    path = project.script_dir / "script.json"
    return ScriptDoc.model_validate(json.loads(path.read_text(encoding="utf-8"))) if path.exists() else None

