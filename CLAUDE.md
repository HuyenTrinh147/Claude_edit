# vedit — ghi chú cho Claude Code

Hệ thống 3 agent dựng video ngắn (Python + ffmpeg). Người dùng nói tiếng Việt; giao diện, prompt, kho kiến thức
viết tiếng Việt, mã nguồn & comment tiếng Anh.

## Làm việc với người dùng trong workspace này

Trong Claude Code, bạn là người điều phối: 4 agent chạy dưới dạng subagent (`.claude/agents/`) nên không cần
ANTHROPIC_API_KEY — `video-researcher` (Agent 1), `video-scriptwriter` (Agent 2), `video-editor` (Agent 3),
`video-critic` (phản biện). Subagent không gọi được subagent khác: bạn chạy từng bước. Việc không cần AI
(`vedit fetch / analyze / sheet / frame / track / validate / render / note / kb / projects`) chạy bằng CLI.

- Đầu phiên, nếu `command -v vedit` không thấy lệnh: `bash scripts/setup.sh` (tạo .venv, cài, đưa `vedit` ra PATH).
- Lệnh tắt (`.claude/skills/`): `/lam-video` (trọn quy trình), `/kich-ban` (Agent 2), `/sua-video` (Agent 3),
  `/nghien-cuu` (Agent 1). Người dùng nói tự nhiên thì làm đúng quy trình của skill tương ứng.
- **Không bao giờ dựng khi người dùng chưa chọn hướng dựng**: Agent 2 đề xuất 2–3 hướng khác hẳn nhau
  (`script/concepts.md`), bạn hỏi bằng AskUserQuestion, ghi lựa chọn bằng `vedit note`. Ý tưởng riêng của người dùng
  (ví dụ "làm dưới dạng game AR") luôn được phát triển thành ít nhất một hướng.
- **Agent phản biện duyệt trước khi giao**: `video-critic` soi bản preview; CẦN SỬA thì `video-editor` sửa (≤ 2 vòng).
- **Nhớ gu người dùng**: mọi lời khen/chê ghi nguyên văn vào `projects/<slug>/project.md` (`vedit note`) và bài học vào
  `profile/gu-nguoi-dung.md` (commit + push). Agent đọc cả hai trước khi làm.
- Luật dựng chung: `knowledge/techniques/tu-duy-dung-sang-tao-cho-video-ngan.md` (luật cứng + tự do sáng tạo).
- Video vào: người dùng tải file thẳng trong chat (xuất hiện ở `/root/.claude/uploads/...`) hoặc gửi link;
  `vedit fetch "<đường dẫn/link>"` → `inbox/`. Mạng của môi trường có thể chặn Drive/YouTube/TikTok; khi đó nêu tên
  miền bị chặn và cách mở (Allowed domains trong cài đặt môi trường) hoặc nhờ tải file thẳng vào chat.
- Kết quả ra: gửi `final.mp4`, `final.jpg`, `script.md`/`concepts.md` bằng SendUserFile. Kịch bản lên Google Drive bằng
  công cụ Google Drive đang kết nối; video quá lớn để tải qua kết nối đó. Bản xuất cũ nằm trong `renders/history/`.
- Workspace là tạm thời: `projects/` không được commit; `knowledge/`, `profile/` thì commit + push.

## Mã nguồn

- `vedit/edl.py` — schema `EditPlan` (pydantic), hợp đồng giữa Agent 2 và Agent 3. Clip start/end = giây nguồn;
  texts/captions/audio = giây timeline.
- `vedit/render.py` — EditPlan → một filter graph ffmpeg (timeline theo khung hình nguyên, concat/xfade, fit
  cover/contain/blur, freeze bằng tpad, look màu, zoom/punch/shake bằng `perspective` (mượt dưới pixel), SFX tổng hợp
  bằng aevalsrc (+ 8-bit, pitch bằng asetrate), amix + sidechaincompress + loudnorm).
- `vedit/ass.py` — lớp libass: chữ động + nền sticker, phụ đề, đồ hoạ vector (callout, badge, progress bar, highlight,
  sparkles, flash); `FontBook` chuẩn hoá cỡ chữ theo metric win của font và đổi tên family sang tên libass nhận.
- `vedit/media.py` — ffprobe, dò cảnh/khoảng lặng, trích khung hình, faster-whisper (tuỳ chọn).
- `vedit/track.py` — bám vật bằng OpenCV CSRT (extra `track`), tự dừng ở điểm cắt cảnh → `analysis/tracks/<tên>.json`.
- `vedit/world.py` — quy đổi toạ độ nguồn (track) → pixel khung ở từng frame, theo đúng hình học của render (layout
  theo frame, fit, Ken Burns, punch/shake — hằng số envelope dùng chung với `render.motion_filter`).
- `vedit/hud.py` — HUD game (visor, reticle, panel, meter, counter, popup, slots, card, prompt, icon): tính từng frame
  bằng Python rồi ghi event ASS tĩnh, gộp các frame giống nhau; mép event nằm giữa hai frame.
- `vedit/agents/` — phiên bản chạy bằng Claude API (cần key): `base.py` (tool runner streaming, web_search/web_fetch,
  caching, fallbacks), `tools.py`, `researcher.py`, `scriptwriter.py` (`run_concepts` → cổng duyệt `pipeline.choose_concept`
  → `run_scriptwriter`), `editor.py`.
- `vedit/fetch.py` — tải video từ Drive/YouTube/TikTok/link; `vedit/knowledge.py` — kho
  `knowledge/<category>/<slug>.md`; `vedit/gdrive.py` — Drive qua OAuth (scope drive.file).

Lệnh: `pip install -e ".[dev]"`, `pytest` (cần ffmpeg; không gọi API thật), `vedit -h`.
Không commit `projects/`, `inbox/` (video nặng) hay `.env`.
