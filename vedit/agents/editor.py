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


def _frames(video: Path, times: list[float], out_dir: Path, width: int = 360) -> list[dict]:
    duration = probe(video).duration
    blocks: list[dict] = []
    for t in times[:12]:
        if not 0 <= t < duration:
            blocks.append({"type": "text", "text": f"t={t}s nằm ngoài video (dài {duration:.2f}s)"})
            continue
        frame = extract_frame(video, t, out_dir / f"{video.stem}_{t:07.2f}.jpg", width=width)
        blocks += [{"type": "text", "text": f"{video.name} @ {t:.2f}s"}, image_block(frame)]
    return blocks


SYSTEM = """Bạn là Agent 3 — Biên tập viên dựng & xuất video trong hệ thống "vedit".

Bạn làm việc trên EditPlan (JSON) của một dự án; bộ render ffmpeg sẽ dựng chính xác theo EditPlan đó.
Mục tiêu: xuất video hoàn chỉnh, đúng kịch bản, đẹp, không lỗi.

Quy trình gợi ý:
1. get_edit_plan để đọc kế hoạch hiện tại. Nếu người dùng có yêu cầu chỉnh sửa, sửa kế hoạch rồi save_edit_plan
   (gửi TOÀN BỘ kế hoạch; công cụ kiểm tra với media thật và báo lỗi cụ thể để bạn sửa).
2. render_preview — trả về khung hình mẫu của bản xem trước. Kiểm tra kỹ: chữ có bị cắt/tràn khung, đè lên mặt
   chủ thể hay nằm trong vùng giao diện app che (12% trên, 22% dưới với video dọc) không; crop có mất chủ thể không;
   cảnh có đúng nội dung kịch bản không; caption có khớp thời điểm. Dùng inspect_render để xem thêm mốc khác,
   view_frames để xem video nguồn khi cần chọn lại điểm cắt / focus_x.
3. Sửa và render_preview lại cho tới khi đạt (thường 1-3 vòng; đừng sửa vụn vặt vô hạn).
4. render_final để xuất bản chính thức.

Ghi nhớ: Clip.start/end tính theo giây NGUỒN; texts/captions/audio theo giây TIMELINE. Khi đổi độ dài/thứ tự clip,
phải dời mốc texts/captions tương ứng. Kho kiến thức (kb_search) có các kỹ thuật dựng và công thức ffmpeg.

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
    def inspect_render(times: list[float], which: str = "preview") -> list:
        """Xem khung hình của video đã render tại các mốc giây trên timeline.

        Args:
            times: Tối đa 12 mốc thời gian (giây).
            which: 'preview' hoặc 'final'.
        """
        result = state.get(which)
        if result is None:
            raise ToolError(f"Chưa có bản {which} — gọi render_{which} trước.")
        return _frames(result.output, times, qa_dir)

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
    parts = [f"Dự án: {project.slug}", "",
             f"Yêu cầu của người dùng: {instructions}" if instructions else
             "Yêu cầu: dựng đúng theo EditPlan hiện có, kiểm tra chất lượng, sửa lỗi nếu thấy, rồi xuất bản chính thức.",
             "", "## EditPlan hiện tại", plan.summary()]
    if script:
        parts += ["", f"## Kịch bản ({script.title})", f"Hook: {script.hook}",
                  *[f"- {s.start:.1f}–{s.end:.1f}s [{s.purpose}] {s.visual} | chữ: {s.on_screen_text} | {s.edit_notes}"
                    for s in script.scenes]]
    if not export:
        parts += ["", "Chỉ cần làm tới bản preview đạt yêu cầu; KHÔNG gọi render_final."]

    tools = [*plan_tools(project), probe_media, *frame_tools(project), *list_assets_tool(settings),
             *knowledge_tools(kb, writable=False), render_preview, inspect_render]
    if export:
        tools.append(render_final)
    run = run_agent(settings, label="Agent3·Edit", system=SYSTEM, prompt="\n".join(parts), tools=tools,
                    effort=settings.effort_edit, max_iterations=40, quiet=quiet)
    if export and state["final"] is None:
        print("[Agent3·Edit] agent chưa xuất bản chính thức — tự render theo edit_plan.json đã lưu", flush=True)
        state["final"] = render_project(settings, project, quiet=quiet)
    return run
