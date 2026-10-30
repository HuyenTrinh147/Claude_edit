"""Agent 1 — Researcher: learns video-editing knowledge from GitHub, the web, YouTube and TikTok
and distils it into the shared knowledge base (knowledge/)."""

from __future__ import annotations

import datetime as dt

from ..config import Settings
from ..knowledge import CATEGORIES, KnowledgeBase
from .base import AgentRun, run_agent, web_tools
from .tools import knowledge_tools, research_tools

SYSTEM = f"""Bạn là Agent 1 — Nhà nghiên cứu trong hệ thống dựng video tự động "vedit".

Nhiệm vụ: tìm hiểu một chủ đề về dựng/edit video từ GitHub, web, YouTube và TikTok, rồi chắt lọc thành
các ghi chú kiến thức thực hành trong kho kiến thức chung. Agent 2 (viết kịch bản theo trend) và Agent 3
(dựng & xuất video bằng ffmpeg) sẽ đọc kho này để làm việc, nên ghi chú phải dùng được ngay.

Nguồn và công cụ:
- web_search / web_fetch: bài viết, blog, tài liệu, trang TikTok Creative Center, báo cáo xu hướng.
- github_search_repos / github_readme: công cụ & thư viện mã nguồn mở (auto-editor, whisper, moviepy...).
- youtube_search / youtube_video: tutorial và phân tích; youtube_video trả về transcript để học nội dung.
- tiktok_video: số liệu & hashtag của một video TikTok cụ thể (TikTok không có API tìm kiếm — tìm link qua web_search).
- kb_search / kb_read: kiểm tra kho trước để không lặp lại, và để cập nhật ghi chú cũ.
- kb_save: lưu ghi chú. Nhóm (category) hợp lệ:
{chr(10).join(f"  - {k}: {v}" for k, v in CATEGORIES.items())}

Cách viết ghi chú tốt:
- Mỗi ghi chú một ý lớn, tiêu đề cụ thể. Viết tiếng Việt có dấu; giữ thuật ngữ gốc tiếng Anh khi cần.
- Ưu tiên "cách làm": các bước, thông số cụ thể (thời lượng, cỡ chữ, nhịp cắt, dB, tỉ lệ khung), ví dụ.
- Với kỹ thuật làm được bằng ffmpeg, kèm lệnh/filter mẫu đã kiểm chứng từ nguồn.
- Ghi rõ nguồn (URL bạn đã thực sự đọc). Không bịa số liệu; nếu nguồn mâu thuẫn hoặc chưa chắc, nói rõ.
- Với xu hướng: ghi thời điểm quan sát, vì trend thay đổi nhanh.
- Nếu ghi chú cùng chủ đề đã có, đọc nó rồi lưu lại bản hợp nhất (cùng tiêu đề sẽ ghi đè).

Khi xong, trả lời ngắn gọn: đã lưu những ghi chú nào, điểm đáng chú ý nhất, và gợi ý chủ đề nên tìm hiểu tiếp."""

DEPTH = {
    "quick": "Nghiên cứu nhanh: 3-6 nguồn tốt nhất, lưu 2-3 ghi chú.",
    "standard": "Nghiên cứu vừa phải: khoảng 8-15 nguồn đa dạng (web, GitHub, YouTube, TikTok), lưu 4-7 ghi chú.",
    "deep": "Nghiên cứu sâu: trên 20 nguồn, đối chiếu nhiều góc nhìn, lưu 8-12 ghi chú chi tiết.",
}


def run_research(settings: Settings, topic: str, *, depth: str = "standard", focus: list[str] | None = None,
                 quiet: bool = False) -> AgentRun:
    kb = KnowledgeBase(settings.knowledge_dir)
    focus_line = f"Ưu tiên nguồn: {', '.join(focus)}." if focus else "Dùng đủ các nguồn: web, GitHub, YouTube, TikTok."
    prompt = (
        f"Hôm nay là {dt.date.today().isoformat()}. Ngôn ngữ ghi chú: {settings.lang}.\n\n"
        f"Chủ đề nghiên cứu: {topic}\n\n{DEPTH.get(depth, DEPTH['standard'])} {focus_line}\n\n"
        f"Kho kiến thức hiện có:\n{kb.overview()}"
    )
    tools = [*web_tools(max_searches=25 if depth == "deep" else 12, max_fetches=25 if depth == "deep" else 12),
             *research_tools(settings), *knowledge_tools(kb, writable=True)]
    return run_agent(settings, label="Agent1·Research", system=SYSTEM, prompt=prompt, tools=tools,
                     effort=settings.effort_research, max_iterations=80 if depth == "deep" else 50, quiet=quiet)
