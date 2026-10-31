"""Agent 3 — Editor: turns the EditPlan into a finished video. It can revise the plan from
natural-language instructions, render a preview, look at the result, fix problems and export."""

from __future__ import annotations

import sys
from pathlib import Path

from anthropic import beta_tool
from anthropic.lib.tools import ToolError

from ..config import Settings
from ..edl import EditPlan
from ..knowledge import KnowledgeBase
from ..media import MediaError, extract_frame, image_block, probe
from ..media import contact_sheet as sheet
from ..project import Project
from ..render import RenderError, RenderResult, render
from .base import AgentError, AgentRun, run_agent
from .scriptwriter import load_script
from .tools import frame_tools, knowledge_tools, list_assets_tool, plan_tools


class Progress:
    """Single-line percentage display for an ffmpeg render."""

    def __init__(self, label: str):
        self.label = label
        self.last = -1

    def __call__(self, fraction: float) -> None:
        pct = int(fraction * 100)
        if pct != self.last:
            self.last = pct
            sys.stdout.write(f"\r    {self.label} {pct:3d}%")
            sys.stdout.flush()

    def finish(self) -> None:
        if self.last >= 0:
            sys.stdout.write(f"\r    {self.label} 100%\n")
            sys.stdout.flush()


def render_project(settings: Settings, project: Project, *, preview: bool = False,
                   plan: EditPlan | None = None, quiet: bool = False) -> RenderResult:
    plan = plan or EditPlan.load(project.plan_path)
    output = project.renders_dir / ("preview.mp4" if preview else plan.export.filename)
    progress = None if quiet else Progress("preview" if preview else "render")
    try:
        return render(plan, output, base_dir=project.dir, preview=preview, font=settings.font,
                      fonts_dir=settings.fonts_dir, work_dir=project.renders_dir / ".work", on_progress=progress)
    finally:
        if progress:
            progress.finish()


def sample_times(plan: EditPlan, max_clips: int = 6, max_texts: int = 4) -> list[float]:
    offsets = plan.clip_offsets()
    times = [off + clip.timeline_duration / 2 for clip, off in zip(plan.clips, offsets)]
    if len(times) > max_clips:
        step = len(times) / max_clips
        times = [times[int(i * step)] for i in range(max_clips)]
    times += [(t.start + min(t.end, plan.duration)) / 2 for t in plan.texts[:max_texts]]
    return sorted({round(min(t, plan.duration - 0.05), 2) for t in times if t >= 0})


def _frames(video: Path, times: list[float], out_dir: Path, width: int = 360, grid: bool = False) -> list[dict]:
    duration = probe(video).duration
    blocks: list[dict] = []
    for t in times[:12]:
        if not 0 <= t < duration:
            blocks.append({"type": "text", "text": f"t={t}s nằm ngoài video (dài {duration:.2f}s)"})
            continue
        frame = extract_frame(video, t, out_dir / f"{video.stem}_{t:07.2f}{'_g' if grid else ''}.jpg", width=width,
                              grid=grid)
        blocks += [{"type": "text", "text": f"{video.name} @ {t:.2f}s"}, image_block(frame)]
    return blocks


SYSTEM = """Bạn là Agent 3 — Biên tập viên dựng & xuất video trong hệ thống "vedit".

Bạn làm việc trên EditPlan (JSON) của một dự án; bộ render ffmpeg dựng chính xác theo EditPlan đó. EditPlan đi theo
một hướng dựng người dùng đã duyệt — giữ đúng tinh thần đó, không tự đổi phong cách.

Quy trình gợi ý:
1. get_edit_plan; đọc gu người dùng và nhật ký dự án (trong tin nhắn). Có yêu cầu chỉnh sửa thì sửa kế hoạch rồi
   save_edit_plan (gửi TOÀN BỘ kế hoạch; công cụ kiểm tra media thật, font, ký tự và báo lỗi cụ thể).
2. render_preview, rồi contact_sheet + inspect_render ở mọi điểm cắt và lúc mỗi chữ/đồ hoạ xuất hiện: chữ bị cắt/tràn,
   che chủ thể hoặc tay đang thao tác, nằm ngoài vùng an toàn; crop mất chủ thể; đúng cảnh; nhịp; payoff đáp đúng khung.
3. Sửa và render_preview lại (1-3 vòng; đừng sửa vụn vặt vô hạn). 4. render_final.

Kỹ thuật: Clip.start/end là giây NGUỒN; texts/captions/graphics/motion/audio là giây TIMELINE — đổi độ dài/thứ tự clip
thì dời các mốc đó. Đo vị trí bằng view_frames(grid=true) / inspect_render(grid=true). Bảng công cụ (tra cứu, không bắt
buộc): kb_read('techniques/bo-cong-cu-do-hoa-hieu-ung-cua-vedit'); HUD game bám vật:
kb_read('techniques/giao-dien-game-hud-bam-vat-cho-video') — track lệch thì gọi lại track_object với hộp sát hơn.

Luật dựng — luật cứng phải tuân thủ, phần sáng tạo là nguyên tắc:
{rules}

Kết thúc bằng tóm tắt ngắn: đã chỉnh gì, file xuất ở đâu, độ dài, và gợi ý cải thiện (nếu có)."""


def run_editor(settings: Settings, project: Project, instructions: str | None = None, *, export: bool = True,
               quiet: bool = False) -> AgentRun:
    if not project.plan_path.exists():
        raise AgentError("Dự án chưa có edit_plan.json — chạy Agent 2 ('vedit script') trước.")
    kb = KnowledgeBase(settings.knowledge_dir)
    qa_dir = project.renders_dir / ".work" / "qa"
    state: dict[str, RenderResult | None] = {"preview": None, "final": None}

    @beta_tool
    def probe_media(path: str) -> str:
        """Thông tin kỹ thuật của một file media: độ dài, kích thước, fps, có âm thanh không.

        Args:
            path: Đường dẫn file (tuyệt đối hoặc tương đối với thư mục dự án).
        """
        p = Path(path).expanduser()
        p = p if p.is_absolute() else project.dir / p
        try:
            return str(probe(p).to_dict())
        except MediaError as e:
            raise ToolError(str(e)) from e

    @beta_tool
    def render_preview() -> list:
        """Render bản xem trước (nửa độ phân giải, nhanh) từ edit_plan.json đã lưu và trả về các khung hình mẫu
        (giữa mỗi clip và lúc mỗi chữ xuất hiện) để kiểm tra chất lượng."""
        plan = EditPlan.load(project.plan_path)
        try:
            result = render_project(settings, project, preview=True, plan=plan, quiet=quiet)
        except (RenderError, MediaError) as e:
            raise ToolError(f"Render thất bại:\n{str(e)[-2500:]}") from e
        state["preview"] = result
        header = {"type": "text", "text": f"Preview: {result.output.name}, {result.duration:.2f}s "
                                          f"(kế hoạch {plan.duration:.2f}s), render {result.elapsed:.0f}s."}
        return [header, *_frames(result.output, sample_times(plan), qa_dir)]

    @beta_tool
    def inspect_render(times: list[float], which: str = "preview", grid: bool = False) -> list:
        """Xem khung hình của video đã render tại các mốc giây trên timeline.

        Args:
            times: Tối đa 12 mốc thời gian (giây).
            which: 'preview' hoặc 'final'.
            grid: Vẽ lưới toạ độ 0-1 để chỉnh vị trí chữ/đồ hoạ.
        """
        result = state.get(which)
        if result is None:
            raise ToolError(f"Chưa có bản {which} — gọi render_{which} trước.")
        return _frames(result.output, times, qa_dir, grid=grid)

    @beta_tool
    def contact_sheet(which: str = "preview", start: float = 0.0, end: float | None = None, count: int = 12) -> list:
        """Một ảnh ghép nhiều khung hình (có ghi mốc giây) của bản render — xem nhịp và bố cục cả video một lần,
        hoặc phóng to quanh một điểm cắt bằng start/end.

        Args:
            which: 'preview' hoặc 'final'.
            start: Giây bắt đầu trên timeline.
            end: Giây kết thúc (bỏ trống = hết video).
            count: Số khung hình (4-24).
        """
        result = state.get(which)
        if result is None:
            raise ToolError(f"Chưa có bản {which} — gọi render_{which} trước.")
        out = qa_dir / f"sheet_{which}_{start:06.2f}.jpg"
        try:
            path, _ = sheet(result.output, out, start=start, end=end, count=max(4, min(count, 24)))
        except MediaError as e:
            raise ToolError(str(e)) from e
        return [{"type": "text", "text": f"{which} {start:.2f}-{end if end is not None else 'hết'}s"}, image_block(path)]

    @beta_tool
    def render_final() -> str:
        """Xuất video chính thức (độ phân giải đầy đủ, chất lượng theo export của EditPlan) + ảnh thumbnail."""
        try:
            result = render_project(settings, project, preview=False, quiet=quiet)
        except (RenderError, MediaError) as e:
            raise ToolError(f"Render thất bại:\n{str(e)[-2500:]}") from e
        state["final"] = result
        info = probe(result.output)
        return (f"Đã xuất {result.output} — {info.width}x{info.height}, {info.duration:.2f}s, "
                f"{info.size_bytes / 1e6:.1f} MB, thumbnail: {result.thumbnail}")

    plan = EditPlan.load(project.plan_path)
    script = load_script(project)
    from .scriptwriter import _context_block, _rules

    parts = [f"Dự án: {project.slug}", "", _context_block(settings, project), "",
             f"Yêu cầu của người dùng: {instructions}" if instructions else
             "Yêu cầu: dựng đúng theo EditPlan hiện có, kiểm tra chất lượng, sửa lỗi nếu thấy, rồi xuất bản chính thức.",
             "", "## EditPlan hiện tại", plan.summary()]
    if script:
        parts += ["", f"## Kịch bản ({script.title})", f"Hook: {script.hook}",
                  *[f"- {s.start:.1f}–{s.end:.1f}s [{s.purpose}] {s.visual} | chữ: {s.on_screen_text} | {s.edit_notes}"
                    for s in script.scenes]]
    if not export:
        parts += ["", "Chỉ cần làm tới bản preview đạt yêu cầu; KHÔNG gọi render_final."]

    tools = [*plan_tools(project, font=settings.font, fonts_dir=settings.fonts_dir), probe_media, *frame_tools(project), *list_assets_tool(settings),
             *knowledge_tools(kb, writable=False), render_preview, inspect_render, contact_sheet]
    if export:
        tools.append(render_final)
    if instructions:
        project.note(instructions, "yêu cầu sửa")
    run = run_agent(settings, label="Agent3·Edit", system=SYSTEM.format(rules=_rules(kb)), prompt="\n".join(parts), tools=tools,
                    effort=settings.effort_edit, max_iterations=40, quiet=quiet)
    if export and state["final"] is None:
        print("[Agent3·Edit] agent chưa xuất bản chính thức — tự render theo edit_plan.json đã lưu", flush=True)
        state["final"] = render_project(settings, project, quiet=quiet)
    return run
