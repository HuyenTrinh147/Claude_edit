# vedit — ghi chú cho Claude Code

Hệ thống 3 agent dựng video ngắn (Python + ffmpeg). Người dùng nói tiếng Việt; giao diện, prompt, kho kiến thức
viết tiếng Việt, mã nguồn & comment tiếng Anh.

## Làm việc với người dùng trong workspace này

Trong Claude Code, bạn là người điều phối: 3 agent chạy dưới dạng subagent (`.claude/agents/`), nên không cần
ANTHROPIC_API_KEY. Các bước không cần AI (`vedit fetch / analyze / validate / render / kb / projects`) chạy bằng CLI.

- Đầu phiên, nếu `command -v vedit` không thấy lệnh: `bash scripts/setup.sh` (tạo .venv, cài, đưa `vedit` ra PATH).
- Lệnh tắt cho người dùng (`.claude/skills/`): `/lam-video` (trọn quy trình), `/kich-ban` (Agent 2),
  `/sua-video` (Agent 3), `/nghien-cuu` (Agent 1). Người dùng nói tự nhiên ("dựng video này cho TikTok...") thì
  làm theo đúng quy trình của skill tương ứng.
- Video vào: `vedit fetch "<link>"` → `inbox/`. Mạng của môi trường có thể chặn Drive/YouTube/TikTok; khi đó nêu
  tên miền bị chặn và hai cách: thêm vào Allowed domains trong cài đặt môi trường, hoặc tải video lên GitHub vào
  `inbox/` của nhánh hiện tại rồi `git pull`.
- Kết quả ra: gửi `final.mp4`, `final.jpg`, `script.md` bằng SendUserFile. Kịch bản lên Google Drive bằng công cụ
  Google Drive đang kết nối (Google Doc từ `script.md`); video quá lớn để tải qua kết nối đó.
- Workspace là tạm thời: `projects/` không được commit; ghi chú mới trong `knowledge/` thì commit + push.

## Mã nguồn

- `vedit/edl.py` — schema `EditPlan` (pydantic), hợp đồng giữa Agent 2 và Agent 3. Clip start/end = giây nguồn;
  texts/captions/audio = giây timeline.
- `vedit/render.py` — EditPlan → một filter graph ffmpeg (concat/xfade, fit cover/contain/blur, zoompan, ASS qua
  libass cho chữ & phụ đề, amix + sidechaincompress + loudnorm).
- `vedit/media.py` — ffprobe, dò cảnh/khoảng lặng, trích khung hình, faster-whisper (tuỳ chọn).
- `vedit/agents/` — phiên bản chạy bằng Claude API (cần key) của 3 agent: `base.py` (tool runner streaming,
  web_search/web_fetch, caching, fallbacks), `tools.py`, `researcher.py`, `scriptwriter.py`, `editor.py`.
- `vedit/fetch.py` — tải video từ Drive/YouTube/TikTok/link; `vedit/knowledge.py` — kho
  `knowledge/<category>/<slug>.md`; `vedit/gdrive.py` — Drive qua OAuth (scope drive.file).

Lệnh: `pip install -e ".[dev]"`, `pytest` (cần ffmpeg; không gọi API thật), `vedit -h`.
Không commit `projects/`, `inbox/` (video nặng) hay `.env`.
