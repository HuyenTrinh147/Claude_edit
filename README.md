# vedit — hệ thống 3 agent dựng, chỉnh sửa & lên kịch bản video ngắn

`vedit` biến một video thô của bạn thành video ngắn (TikTok / Reels / Shorts / YouTube) hoàn chỉnh,
bằng 3 agent dùng Claude + ffmpeg:

| Agent | Lệnh | Làm gì |
|---|---|---|
| **Agent 1 — Nghiên cứu** | `vedit research` | Tìm hiểu kỹ thuật edit trên **GitHub, web, YouTube, TikTok**, chắt lọc thành ghi chú trong kho kiến thức `knowledge/` |
| **Agent 2 — Trend & kịch bản** | `vedit script` | Phân tích video bạn đưa vào, nghiên cứu **trend, từ khoá, hashtag** hiện tại, viết **kịch bản** + **EditPlan** (kế hoạch dựng); tuỳ chọn tạo **thư mục Google Drive** |
| **Agent 3 — Dựng & xuất** | `vedit edit` | Dựng theo EditPlan, render bản xem trước, **tự xem lại khung hình để sửa lỗi**, rồi **xuất video** + thumbnail |
| **Agent phản biện** | (trong Claude Code) | Soi lỗi bản xem trước — đối chiếu hướng đã duyệt, gu của bạn và luật dựng — trước khi giao video |

**Quy trình**: phân tích video → Agent 2 **đề xuất 2–3 hướng dựng khác hẳn nhau** → **bạn chọn** (hoặc đưa ý tưởng riêng,
ví dụ "làm như game AR") → kịch bản + EditPlan → Agent 3 dựng → agent phản biện soi lỗi → xuất. Mọi lời khen/chê của bạn
được ghi vào nhật ký dự án và **hồ sơ gu** (`profile/gu-nguoi-dung.md`) để các video sau đúng ý hơn.

```mermaid
flowchart LR
    V[Video của bạn] --> AN[analyze<br/>cảnh · khoảng lặng · transcript · khung hình]
    A1[Agent 1<br/>GitHub · Web · YouTube · TikTok] --> KB[(knowledge/<br/>kho kiến thức)]
    AN --> A2[Agent 2<br/>trend · từ khoá · kịch bản]
    KB --> A2
    A2 --> S[script.md + edit_plan.json]
    S --> A3[Agent 3<br/>preview → tự kiểm tra → sửa]
    KB --> A3
    A3 --> R[ffmpeg render<br/>final.mp4 + thumbnail]
    S -. --drive .-> GD[(Google Drive)]
    R -. --drive .-> GD
```

> **Cách dễ nhất:** mở repo trong Claude Code và gõ `/lam-video <link video> <mục tiêu>` — xem mục
> [Dùng ngay trong Claude Code](#dùng-ngay-trong-claude-code-không-cần-cài-không-cần-api-key). Phần cài đặt dưới
> đây dành cho chạy trên máy của bạn bằng Claude API.

## Cài đặt

Cần **Python 3.10+** và **ffmpeg** (có libass — bản phổ thông đều có). Hoặc chạy `bash scripts/setup.sh`.

```bash
# macOS: brew install ffmpeg      Ubuntu: sudo apt install ffmpeg      Windows: winget install ffmpeg
git clone https://github.com/HuyenTrinh147/Claude_edit.git && cd Claude_edit
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[gdrive,transcribe]"                  # bỏ extra nào không cần
cp .env.example .env                                   # rồi điền ANTHROPIC_API_KEY
vedit doctor                                           # kiểm tra môi trường
```

- `transcribe` cài **faster-whisper** để tự nhận dạng lời nói → phụ đề karaoke, cắt khoảng lặng theo lời. Không cài
  thì có thể đưa file `.srt` sẵn có qua `--transcript`.
- `gdrive` cài thư viện Google để tạo thư mục / tải file lên Drive.

## Dùng nhanh

```bash
# 1 lệnh: phân tích → Agent 2 viết kịch bản theo trend → Agent 3 dựng & xuất (→ Drive)
vedit make ~/Videos/quan-cafe.mp4 \
  --goal "Review quán cà phê 20k ở quận 1, thu hút sinh viên đến quán" \
  --platform tiktok --duration 30 --style "năng động, hài hước" --drive
```

Kết quả nằm trong `projects/<ngày>-<tên>/`:

```
projects/20261030-quan-cafe/
├── project.json          # thông tin dự án, link Google Drive
├── analysis/             # analysis.json + khung hình đại diện
├── script/script.md      # kịch bản dễ đọc: hook, insight trend, bảng cảnh, caption, hashtag
├── script/script.json
├── edit_plan.json        # kế hoạch dựng (Agent 3 render từ file này)
└── renders/final.mp4     # video xuất + final.jpg (thumbnail), preview.mp4
```

### Từng bước (khi muốn kiểm soát)

```bash
vedit research "kỹ thuật cắt nhịp nhanh và phụ đề karaoke cho TikTok" --depth standard   # Agent 1
vedit kb list                       # xem kho kiến thức  (vedit kb search hook / vedit kb show <ref>)

vedit script ~/Videos/quan-cafe.mp4 --goal "..." --platform reels --duration 45          # Agent 2
#   → đọc & sửa tay projects/<dự án>/script/script.md hoặc edit_plan.json nếu muốn

vedit edit 20261030-quan-cafe                                                            # Agent 3
vedit edit quan-cafe -i "chữ hook to hơn, bỏ cảnh thứ 3, thêm zoom chậm ở cảnh cuối"      # chỉnh bằng lời

vedit render quan-cafe --preview    # render lại không cần AI (nhanh, nửa độ phân giải)
vedit validate quan-cafe            # kiểm tra edit_plan.json sau khi sửa tay
vedit drive sync quan-cafe          # tải kịch bản + video lên Google Drive
vedit projects                      # danh sách dự án & trạng thái
vedit fetch "<link Drive/YouTube/TikTok>"   # tải video vào inbox/
vedit concepts quan-cafe --goal "..." --idea "làm như game AR"   # Agent 2: đề xuất hướng dựng
vedit script quan-cafe --goal "..." --concept 2 --notes "..."    # kịch bản theo hướng đã chọn
vedit sheet quan-cafe --source preview      # ảnh ghép nhiều khung hình có mốc giây
vedit note quan-cafe "chữ hơi nhỏ" --kind "phản hồi"            # ghi phản hồi vào nhật ký dự án
```

## Chi tiết 3 agent

### Agent 1 — Nghiên cứu (`vedit research "<chủ đề>"`)
- Công cụ: `web_search`/`web_fetch` (chạy phía server của Anthropic), tìm repo + đọc README GitHub, tìm video +
  đọc transcript YouTube, đọc số liệu/hashtag video TikTok (qua `yt-dlp`), đọc/ghi kho kiến thức.
- Ghi chú lưu ở `knowledge/<nhóm>/<slug>.md` (có nguồn, tags, ngày cập nhật) + mục lục `knowledge/INDEX.md`.
  Nhóm: `techniques`, `scripting`, `trends`, `platforms`, `audio`, `tools`, `ffmpeg`.
- `--depth quick|standard|deep` quyết định số nguồn; `--focus github youtube` để ưu tiên nguồn.
- Kho có sẵn 7 ghi chú khởi tạo (hook, cấu trúc kịch bản, vùng an toàn, nhịp cắt, âm thanh, công thức ffmpeg,
  repo hữu ích) — chạy Agent 1 để kiểm chứng và mở rộng.

### Agent 2 — Trend & kịch bản (`vedit script <video|dự án> --goal "..."`)
1. **Phân tích video** (không dùng AI, `vedit analyze`): thông số, dò cảnh, khoảng lặng, transcript, khung hình đại diện.
2. Claude **xem khung hình**, đọc transcript, **nghiên cứu xu hướng thật** gần đây (web, YouTube, TikTok, kho kiến
   thức), chọn ý tưởng → viết kịch bản: phương án tiêu đề & hook, insight trend có dẫn nguồn, bảng cảnh (thời gian,
   hình ảnh, lời thoại, chữ trên màn hình, ghi chú dựng), nhạc, CTA, caption, hashtag, từ khoá, mẹo đăng.
3. Viết **EditPlan** khớp kịch bản. EditPlan được kiểm tra với file thật (điểm cắt có vượt độ dài không, file có
   tồn tại không...) — sai thì Claude tự sửa.
4. `--drive`: tạo `vedit/<dự án>/{01_Nguon, 02_Kich_ban, 03_Video_xuat}` trên Google Drive và tải `script.md`
   (thành Google Docs), `script.json`, `edit_plan.json` lên.

### Agent 3 — Dựng & xuất (`vedit edit <dự án> [-i "yêu cầu"]`)
- Đọc EditPlan, áp dụng yêu cầu chỉnh sửa bằng lời (nếu có), **render preview** rồi **nhìn các khung hình mẫu**
  để kiểm tra: chữ bị cắt/đè mặt/nằm dưới giao diện app, crop mất chủ thể, sai cảnh, lệch phụ đề... → sửa → render lại.
- `render_final`: xuất H.264/AAC, loudness -14 LUFS, `faststart`, kèm thumbnail. Nếu agent quên xuất, hệ thống tự
  render từ EditPlan đã lưu.

## EditPlan — "ngôn ngữ chung" giữa Agent 2 và Agent 3

Một file JSON mô tả toàn bộ video. Ví dụ rút gọn (`vedit schema plan` in đầy đủ schema):

```json
{
  "title": "Quán cà phê 20k",
  "sources": {"main": "/Users/ban/Videos/quan-cafe.mp4"},
  "canvas": {"width": 1080, "height": 1920, "fps": 30},
  "clips": [
    {"source": "main", "start": 12.4, "end": 14.9, "fit": "cover", "focus_x": 0.4, "zoom": "in", "note": "hook"},
    {"source": "main", "start": 31.0, "end": 34.2, "fit": "blur"},
    {"source": "main", "start": 50.5, "end": 55.0, "speed": 1.5, "transition": {"type": "fade", "duration": 0.3}},
    {"source": "color:#111111", "duration": 1.5, "note": "thẻ CTA"}
  ],
  "texts": [{"text": "Chỉ 20k mà như này?", "start": 0, "end": 2.4, "position": "upper", "size": 96, "animation": "pop"}],
  "captions": {"style": "karaoke", "segments": [{"start": 0.2, "end": 1.9, "text": "Xin chào các bạn"}]},
  "images": [{"path": "assets/logo.png", "x": 0.88, "y": 0.06, "width": 0.14, "opacity": 0.9}],
  "audio": [{"path": "assets/music/lofi.mp3", "role": "music", "volume": 0.2, "duck": true}],
  "export": {"filename": "final.mp4", "crf": 20, "thumbnail_at": 1.0}
}
```

- `clips` nối tiếp nhau; `start/end` là **giây trong file nguồn**. `texts`, `captions`, `images`, `audio` dùng
  **giây trên timeline** của video xuất.
- `fit`: `cover` (cắt đầy khung, chỉnh `focus_x/focus_y`), `contain` (viền màu), `blur` (nền mờ — hợp khi đưa video
  ngang sang dọc). `zoom`: `in`/`out` (Ken Burns). `speed` 0.25–4. `transition`: `fade`, `slideleft`, `zoomin`,
  `circleopen`... (chuyển cảnh từ clip trước).
- Chữ & phụ đề render bằng **libass**: tiếng Việt có dấu, viền, hộp nền, hiệu ứng `pop` / `fade` / `slide_up`;
  phụ đề `clean`, `boxed`, `bold_pop`, `karaoke` (tô màu từ đang đọc).
- Âm thanh: nhạc nền tự **giảm âm lượng khi có lời nói** (`duck`), fade in/out, lặp; voiceover/SFX đặt theo mốc.
- **Lớp sáng tạo** (chi tiết: `knowledge/techniques/bo-cong-cu-do-hoa-hieu-ung-cua-vedit.md`):
  - chữ động `bounce`, `typewriter`, `word_pop`, `slide_left`, `blur_in`, `wipe`… trên nền sticker `pill` / `banner`,
    đặt tự do bằng `x`, `y`, `rotation`; font tiếng Việt kèm sẵn: Be Vietnam Pro, Mali, Pacifico;
  - `graphics`: `callout` (nhãn + đường chỉ vào vật), `badge` (số bước), `progress_bar`, `highlight`, `sparkles`, `flash`;
  - `motion`: `punch` (zoom giật) và `shake` (rung) khớp tiếng va chạm / beat;
  - `look`: tông màu `warm_food`, `bright_clean`, `film`, `moody`, `vivid`, `bw` + vignette, hạt film;
  - âm thanh hiệu ứng tổng hợp không cần file: `sfx:pop|click|ding|sparkle|whoosh|thud|rise`.
- `vedit frame <dự án> <giây> --grid` trích khung hình có lưới toạ độ 0–1 để đặt đồ hoạ đúng vị trí vật.

## Google Drive

Agent 2 chỉ cần **tạo thư mục và tải file** nên dùng quyền hẹp `drive.file` (chỉ thấy file do vedit tạo).

1. Vào [Google Cloud Console](https://console.cloud.google.com/) → tạo project → **APIs & Services → Enable APIs** → bật **Google Drive API**.
2. **OAuth consent screen**: chọn External, thêm email của bạn vào *Test users*.
3. **Credentials → Create credentials → OAuth client ID → Desktop app** → tải file JSON về `secrets/client_secret.json`.
4. Trong `.env`: `GOOGLE_OAUTH_CLIENT_FILE=./secrets/client_secret.json`.
5. Chạy `vedit drive setup <dự án>` lần đầu → trình duyệt mở để đăng nhập; token được lưu lại cho các lần sau.

(Service account cũng được hỗ trợ — xem `.env.example` — nhưng service account không có dung lượng riêng, nên phải
dùng thư mục trong Shared Drive.)

## Dùng ngay trong Claude Code (không cần cài, không cần API key)

Mở repo này trong Claude Code (web, app hoặc CLI) rồi chat. Claude điều phối 3 subagent trong `.claude/agents/`
(`video-researcher`, `video-scriptwriter`, `video-editor`) bằng công cụ web/Bash có sẵn của Claude Code, nên
**không cần ANTHROPIC_API_KEY riêng**. Lần đầu mỗi phiên, Claude tự chạy `bash scripts/setup.sh` để cài `vedit`.

| Gõ trong chat | Việc |
|---|---|
| `/lam-video <link video> <mục tiêu>` | Trọn quy trình: tải video → kịch bản theo trend → dựng → gửi `final.mp4` + thumbnail + kịch bản |
| `/kich-ban <link video> <mục tiêu>` | Agent 2: chỉ ý tưởng + kịch bản (+ lưu Google Doc lên Drive) |
| `/sua-video <dự án> <yêu cầu>` | Agent 3: sửa bằng lời ("chữ to hơn, bỏ cảnh 3") và xuất lại |
| `/nghien-cuu <chủ đề>` | Agent 1: nghiên cứu & lưu vào kho kiến thức |

Hoặc nói tự nhiên: *"dựng video này thành TikTok 30s review quán cà phê, lưu kịch bản lên Drive"*.

**Đưa video vào** (`vedit fetch` lưu vào `inbox/`):
- **Dễ nhất: tải file video thẳng vào khung chat** của Claude Code rồi nói mục tiêu.
- Link Google Drive (chia sẻ "Bất kỳ ai có đường liên kết"), YouTube, TikTok hoặc link tải trực tiếp. Trên Claude Code
  web, mạng của môi trường có thể chặn các trang này → vào cài đặt môi trường (menu môi trường ở thanh tiêu đề →
  Edit → Network access) thêm `drive.google.com`, `drive.usercontent.google.com` (và `youtube.com`, `tiktok.com`
  nếu cần) vào Allowed domains, hoặc chọn mức truy cập rộng hơn.
- Hoặc tải video lên GitHub vào thư mục `inbox/` của nhánh đang dùng (GitHub web giới hạn 25 MB/file) rồi báo Claude.

**Nhận kết quả**: video, thumbnail, kịch bản được gửi thẳng trong chat; kịch bản lưu lên Google Drive thành Google Doc
qua kết nối Drive của Claude. Workspace trên web là tạm thời — tải video về máy sau khi xong.

**Cài sẵn cho mỗi phiên mới** (tuỳ chọn): thêm `cd Claude_edit && bash scripts/setup.sh` vào Setup script trong
cài đặt môi trường.

## Cấu hình & chi phí

- Mặc định model `claude-opus-5-5`, adaptive thinking; mức `effort` riêng từng agent (`VEDIT_EFFORT_*` trong `.env`):
  research `medium`, script `high`, edit `medium`. Hạ xuống `low` để tiết kiệm, nâng `high`/`xhigh` khi cần chất lượng.
- Prompt caching được bật cho cả system prompt và hội thoại; cuối mỗi lần chạy agent in số token đã dùng.
- `VEDIT_FALLBACKS=1`: nếu bộ lọc an toàn từ chối một lượt, API tự chạy lại lượt đó trên model dự phòng (đặt `0` để tắt).
- Web search/fetch tính phí theo lượt dùng; mỗi agent có giới hạn `max_uses`.

## Giới hạn cần biết

- **TikTok không có API tìm kiếm công khai**: Agent tìm link qua web search rồi đọc từng video bằng `yt-dlp`;
  TikTok/YouTube đôi khi chặn truy cập tự động — agent sẽ tự chuyển sang web search/web fetch.
- Claude **không nghe được âm thanh**: lời nói chỉ được hiểu qua transcript (faster-whisper hoặc file `.srt`).
- Emoji hiển thị dạng nét đơn sắc (libass không vẽ emoji màu).
- Nhạc trend trong app thường không được phép chèn sẵn vào file — Agent 2 ghi hướng dẫn chọn sound trong kịch bản.

## Phát triển

```bash
pip install -e ".[dev]"
pytest            # 30+ test: schema, ffmpeg render thật trên video tổng hợp, phân tích media,
                  # kho kiến thức, vòng lặp agent với API giả lập (không tốn phí)
```

Mã nguồn: `vedit/edl.py` (schema EditPlan) · `vedit/render.py` (ffmpeg + ASS) · `vedit/media.py` (phân tích) ·
`vedit/agents/` (3 agent + công cụ) · `vedit/knowledge.py` · `vedit/gdrive.py` · `vedit/cli.py`.
