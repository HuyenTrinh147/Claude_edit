"""Client-side tools shared by the agents. Each factory closes over its context and returns
@beta_tool functions for the SDK tool runner. Raising ToolError sends Claude an error result
it can recover from."""

from __future__ import annotations

import json
from pathlib import Path

from anthropic import beta_tool
from anthropic.lib.tools import ToolError
from pydantic import ValidationError

from ..config import Settings
from ..ass import check_fonts
from ..edl import EditPlan, validate_against_media
from ..knowledge import CATEGORIES, KnowledgeBase
from ..media import MediaError, extract_frame, image_block, probe
from ..project import Project
from ..sources import github, tiktok, youtube

AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def _json(data) -> str:
    return json.dumps(data, ensure_ascii=False, indent=1)


def format_validation_error(err: ValidationError) -> str:
    lines = []
    for e in err.errors()[:25]:
        loc = ".".join(str(p) for p in e["loc"]) or "(gốc)"
        lines.append(f"- {loc}: {e['msg']}")
    return "\n".join(lines)


# ---- knowledge base -------------------------------------------------------------------

def knowledge_tools(kb: KnowledgeBase, *, writable: bool) -> list:
    @beta_tool
    def kb_search(query: str, category: str | None = None, limit: int = 6) -> str:
        """Tìm trong kho kiến thức dựng video nội bộ (do Agent 1 thu thập). Trả về danh sách ghi chú khớp nhất.

        Args:
            query: Từ khoá tìm kiếm (tiếng Việt hoặc tiếng Anh).
            category: Lọc theo nhóm: techniques, scripting, trends, platforms, audio, tools, ffmpeg.
            limit: Số kết quả tối đa.
        """
        hits = kb.search(query, limit=limit, category=category)
        if not hits:
            return "Không có ghi chú nào khớp."
        return "\n\n".join(f"[{n.ref}] {n.title} (điểm {s}, cập nhật {n.updated})\n  …{snip}…" for n, s, snip in hits)

    @beta_tool
    def kb_read(ref: str) -> str:
        """Đọc toàn văn một ghi chú trong kho kiến thức.

        Args:
            ref: Mã ghi chú dạng 'category/slug' (lấy từ kb_search).
        """
        note = kb.get(ref)
        if note is None:
            raise ToolError(f"Không có ghi chú '{ref}'. Dùng kb_search để lấy đúng mã.")
        return f"# {note.title}\nNguồn: {', '.join(note.sources) or '(không có)'}\n\n{note.body}"

    tools = [kb_search, kb_read]
    if writable:
        @beta_tool
        def kb_save(title: str, category: str, content: str, tags: list[str], sources: list[str]) -> str:
            """Lưu (hoặc ghi đè nếu trùng tiêu đề) một ghi chú kiến thức dạng Markdown vào kho.

            Args:
                title: Tiêu đề ngắn, cụ thể (tiếng Việt).
                category: Một trong: techniques, scripting, trends, platforms, audio, tools, ffmpeg.
                content: Nội dung Markdown: tóm tắt, các bước áp dụng, ví dụ / lệnh cụ thể, lưu ý.
                tags: 3-8 từ khoá để tìm lại.
                sources: Các URL nguồn đã thực sự đọc (bắt buộc ít nhất 1).
            """
            if category not in CATEGORIES:
                raise ToolError(f"category không hợp lệ. Chọn: {', '.join(CATEGORIES)}")
            if not sources:
                raise ToolError("Cần ít nhất một URL nguồn đã đọc.")
            note = kb.save(title, category, content, tags, sources)
            print(f"    📝 đã lưu {note.ref}", flush=True)
            return f"Đã lưu {note.ref}"

        tools.append(kb_save)
    return tools


# ---- GitHub / YouTube / TikTok ------------------------------------------------------------

def research_tools(settings: Settings) -> list:
    @beta_tool
    def github_search_repos(query: str, limit: int = 8, sort: str = "stars") -> str:
        """Tìm repository trên GitHub (công cụ, thư viện, script dựng video tự động...).

        Args:
            query: Cú pháp tìm kiếm GitHub, ví dụ 'auto editor silence cut language:python' hoặc 'topic:video-editing'.
            limit: Số kết quả (tối đa 30).
            sort: 'stars', 'updated' hoặc 'best-match'.
        """
        try:
            sort_key = None if sort == "best-match" else sort
            return _json(github.search_repositories(query, limit, sort_key, settings.github_token))
        except github.GitHubError as e:
            raise ToolError(str(e)) from e

    @beta_tool
    def github_readme(repo: str, max_chars: int = 12000) -> str:
        """Đọc README của một repository GitHub.

        Args:
            repo: 'owner/name' hoặc URL github.com.
            max_chars: Giới hạn độ dài trả về.
        """
        try:
            return github.get_readme(repo, max_chars, settings.github_token)
        except github.GitHubError as e:
            raise ToolError(str(e)) from e

    @beta_tool
    def youtube_search(query: str, limit: int = 8) -> str:
        """Tìm video YouTube (tutorial edit, phân tích trend...). Trả về tiêu đề, kênh, lượt xem, thời lượng, URL.

        Args:
            query: Từ khoá tìm kiếm.
            limit: Số kết quả (tối đa 20).
        """
        try:
            return _json(youtube.search(query, limit))
        except Exception as e:
            raise ToolError(f"YouTube không truy cập được ({str(e)[:200]}). Thử web_search thay thế.") from e

    @beta_tool
    def youtube_video(url: str, transcript: bool = True) -> str:
        """Lấy mô tả, chương, tags và transcript (phụ đề) của một video YouTube để học nội dung.

        Args:
            url: URL video YouTube.
            transcript: Có lấy phụ đề (vi/en) hay không.
        """
        try:
            return _json(youtube.video_info(url, transcript=transcript))
        except Exception as e:
            raise ToolError(f"Không đọc được video ({str(e)[:200]}). Thử web_fetch trang video.") from e

    @beta_tool
    def tiktok_video(url: str) -> str:
        """Lấy thông tin một video TikTok: mô tả, hashtag, nhạc, lượt xem/thích/chia sẻ.

        Args:
            url: URL video TikTok (https://www.tiktok.com/@user/video/...).
        """
        try:
            return _json(tiktok.video_info(url))
        except Exception as e:
            raise ToolError(f"TikTok chặn truy cập ({str(e)[:200]}). Dùng web_search / web_fetch thay thế.") from e

    return [github_search_repos, github_readme, youtube_search, youtube_video, tiktok_video]


# ---- assets & frames ------------------------------------------------------------------------

def list_assets_tool(settings: Settings) -> list:
    @beta_tool
    def list_assets() -> str:
        """Liệt kê tài nguyên có sẵn trong thư mục assets/: nhạc nền, SFX, ảnh/logo (đường dẫn tuyệt đối + độ dài)."""
        items = []
        root = settings.assets_dir
        if root.exists():
            for f in sorted(root.rglob("*")):
                ext = f.suffix.lower()
                if ext in AUDIO_EXTS:
                    try:
                        items.append({"type": "audio", "path": str(f.resolve()), "duration": probe(f).duration})
                    except MediaError:
                        continue
                elif ext in IMAGE_EXTS:
                    items.append({"type": "image", "path": str(f.resolve())})
        if not items:
            return ("assets/ đang trống — không có nhạc/ảnh. Nếu cần nhạc, ghi hướng dẫn chọn nhạc trong kịch bản "
                    "(music_direction) thay vì thêm track audio.")
        return _json(items)

    @beta_tool
    def search_sfx(query: str = "", category: str | None = None, limit: int = 20) -> str:
        """Tìm âm thanh hiệu ứng THẬT trong thư viện SFX (bộ người dùng đã nhập bằng `vedit sfx add`). Mỗi kết quả có
        đường dẫn (dùng làm audio.path), loại, độ dài và mốc đỉnh tiếng `hit`: đặt audio.start = mốc khung hình - hit
        để đỉnh tiếng rơi đúng khung. Không có kết quả thì dùng SFX tổng hợp 'sfx:<tên>'.

        Args:
            query: Từ khoá theo tên file (vd 'whoosh', 'ding', 'cash', 'vỗ tay').
            category: whoosh, impact, riser, pop, click, ding, magic, glitch, camera, cash, fail, funny, crowd, game,
                scratch, other.
            limit: Số kết quả tối đa.
        """
        from ..sfxlib import describe, search

        hits = search(settings.assets_dir / "sfx", query, category, limit)
        return "\n".join(describe(p, s) for p, s in hits) or "Không có SFX thật nào khớp (thư viện trống hoặc sai từ khoá)."

    return [list_assets, search_sfx]


def frame_tools(project: Project) -> list:
    @beta_tool
    def view_frames(times: list[float], source: str = "main", grid: bool = False) -> list:
        """Xem khung hình của video nguồn tại các mốc thời gian (giây) để quyết định điểm cắt, khung crop, chữ.

        Args:
            times: Tối đa 12 mốc thời gian, tính theo giây trong file nguồn.
            source: 'main' (video đầu vào) hoặc đường dẫn file media khác.
            grid: Vẽ lưới 10% có nhãn toạ độ 0-1 để đọc vị trí x/y cho callout, highlight, chữ.
        """
        path = project.input_path if source == "main" else Path(source).expanduser()
        if not path.exists():
            raise ToolError(f"Không tìm thấy {path}")
        duration = probe(path).duration
        blocks: list = []
        for t in times[:12]:
            if not 0 <= t < duration:
                blocks.append({"type": "text", "text": f"t={t}s nằm ngoài video (dài {duration:.2f}s)"})
                continue
            name = f"view_{path.stem}_{t:07.2f}{'_grid' if grid else ''}.jpg"
            frame = extract_frame(path, t, project.analysis_dir / "frames" / name, grid=grid)
            blocks += [{"type": "text", "text": f"t={t:.2f}s"}, image_block(frame)]
        return blocks

    @beta_tool
    def track_object(name: str, at: float, box: list[float], until: float | None = None,
                     back: float | None = None) -> list:
        """Bám theo một vật trong video nguồn (OpenCV) để HUD / đồ hoạ dính vào vật thật (anchor.track = name).
        Tự dừng ở điểm cắt cảnh. Trả về tóm tắt + ảnh kiểm tra có vẽ hộp bám — hãy xem ảnh trước khi dùng track.

        Args:
            name: Tên track ngắn, không dấu, vd 'hu', 'ot', 'tay'.
            at: Mốc giây NGUỒN nơi khoanh vật (đo bằng view_frames với grid=true).
            box: [x, y, w, h] theo tỉ lệ khung nguồn 0..1 (góc trên-trái + rộng, cao) bao sát vật tại `at`.
            until: Bám tới giây nguồn này (mặc định hết video).
            back: Bám ngược về giây nguồn này.
        """
        from ..track import TrackError, describe, track_path, track_sheet
        from ..track import track_object as run_track

        if len(box) != 4:
            raise ToolError("box phải có 4 số [x, y, w, h] trong 0..1")
        try:
            track = run_track(project.input_path, name=name, at=at, box=tuple(box), until=until, back=back)
        except TrackError as e:
            raise ToolError(str(e)) from None
        track.save(track_path(project.dir, name))
        sheet = track_sheet(track, project.input_path, project.analysis_dir / "tracks" / f"{name}_sheet.jpg")
        return [{"type": "text", "text": describe(track)}, image_block(sheet)]

    return [view_frames, track_object]


# ---- edit plan ------------------------------------------------------------------------------

def plan_tools(project: Project, *, on_save=None, font: str | None = None, fonts_dir: Path | None = None) -> list:
    """`font` (the default font) turns on font checks: unknown families and missing characters are errors."""
    def check(plan_data: dict) -> EditPlan:
        plan_data.setdefault("sources", {})
        plan_data["sources"].setdefault("main", str(project.input_path))
        try:
            plan = EditPlan.model_validate(plan_data)
        except ValidationError as e:
            raise ToolError("EditPlan không hợp lệ, sửa rồi gọi lại:\n" + format_validation_error(e)) from e
        problems = validate_against_media(plan, project.dir, probe)
        if font:
            problems += check_fonts(plan, font, fonts_dir)
        if problems:
            raise ToolError("EditPlan không khớp với media thực tế, sửa rồi gọi lại:\n- " + "\n- ".join(problems))
        return plan

    def save_edit_plan(**plan) -> str:
        """Lưu EditPlan (kế hoạch dựng) cho dự án sau khi kiểm tra hợp lệ với file media thật.
        Nếu lỗi, công cụ trả về danh sách lỗi cụ thể — sửa và gọi lại. Gửi TOÀN BỘ kế hoạch mỗi lần gọi."""
        edit_plan = check(plan)
        edit_plan.save(project.plan_path)
        if on_save:
            on_save(edit_plan)
        return f"Đã lưu {project.plan_path.name}.\n{edit_plan.summary()}"

    @beta_tool
    def get_edit_plan() -> str:
        """Đọc EditPlan hiện tại của dự án (JSON) kèm tóm tắt timeline."""
        if not project.plan_path.exists():
            raise ToolError("Dự án chưa có edit_plan.json")
        plan = EditPlan.load(project.plan_path)
        return f"{plan.summary()}\n\nJSON:\n{plan.model_dump_json(indent=1, exclude_none=True)}"

    return [beta_tool(save_edit_plan, input_schema=EditPlan.model_json_schema()), get_edit_plan]
