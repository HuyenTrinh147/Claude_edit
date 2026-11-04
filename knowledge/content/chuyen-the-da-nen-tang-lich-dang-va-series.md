---
title: Chuyển thể đa nền tảng, lịch đăng và series
category: content
tags: [đa nền tảng, giới hạn ký tự, lịch đăng, series, video thành bài đăng, transcript, agent-4]
updated: 2026-11-04
sources:
  - https://github.com/tvcnet/social-toolkit/blob/HEAD/README.md
  - https://github.com/tvcnet/social-toolkit/blob/HEAD/assets/js/tst-config.js
  - https://github.com/tvcnet/social-toolkit/blob/HEAD/assets/js/tst-content.js
  - https://github.com/tvcnet/social-toolkit/blob/HEAD/assets/js/tst-schedule.js
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/agents/graph.py
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/plugins/base.py
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/plugins/linkedin_plugin.py
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/plugins/reddit_plugin.py
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/core/prompts/platforms/linkedin.yaml
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/core/prompts/platforms/reddit.yaml
  - https://github.com/bikram73/SocialSpark_AI/blob/HEAD/README.md
  - https://github.com/bikram73/SocialSpark_AI/blob/HEAD/server.ts
  - https://github.com/bikram73/SocialSpark_AI/blob/HEAD/docs/BUG_FIXES.md
  - https://github.com/bikram73/SocialSpark_AI/blob/HEAD/src/components/CalendarPreviewModal.tsx
  - https://github.com/tubaarif-dev/content-craft/blob/HEAD/README.md
  - https://github.com/tubaarif-dev/content-craft/blob/HEAD/server/services/generatePosts.js
  - https://github.com/tubaarif-dev/content-craft/blob/HEAD/server/controller/uploadController.js
  - https://github.com/tubaarif-dev/content-craft/blob/HEAD/server/services/speechService.js
  - https://github.com/Xsolai/postforge-ai/blob/HEAD/src/lib/data.ts
  - https://github.com/Xsolai/postforge-ai/blob/HEAD/README.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/workspace/scripts/check-copy/rules/formats/shared.mjs
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/workspace/scripts/check-copy/rules/formats/ad.mjs
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/skills/tweet-copy/SKILL.md
---
# Chuyển thể đa nền tảng, lịch đăng và series

Tóm tắt: các repo chuyển thể mạnh ở **giới hạn ký tự + giọng từng nền tảng + hậu xử lý bằng mã**, làm lịch ở mức **bảng tuần
7 ngày + xuất CSV**, và hầu như **không** có series thật (mồi – đáp – mở rộng) hay dữ liệu về giờ đăng. Đọc thêm
`cong-chat-luong-chong-van-ai-va-bang-tieng-viet` (hợp đồng định dạng) và `khung-viet-hook-kich-ban-caption-hashtag-va-ugc`.

**Lưu ý độ tin cậy**: mọi con số giới hạn dưới đây là **con số ghi trong repo** (không kiểm với tài liệu chính thức của
nền tảng). Giới hạn đổi theo thời gian; Agent 4 phải tra lại bằng WebSearch trước khi coi là hợp đồng cứng. Ví dụ tính đến
2026-11-04, kết quả tìm kiếm về giới hạn caption TikTok **mâu thuẫn**: social-toolkit ghi 2.200; vài trang bên thứ ba nói 4.000
nếu gõ trực tiếp trong app và vẫn 2.200 qua công cụ lên lịch; không có nguồn chính thức nào đã được xác minh ở đây.

## 1. Bảng giới hạn và giọng theo nền tảng (đã có trong repo)

social-toolkit (`assets/js/tst-config.js:9-18, 37-46`; README mục Supported Platforms) — giới hạn ký tự + phong cách:

| Nền tảng | Giới hạn ghi trong repo | Giọng / phong cách ghi trong repo |
|---|---|---|
| X | 280 | Ngắn, theo hook, CTA gọn |
| Instagram | 2.200 | Kể chuyện, nhiều emoji, khối hashtag |
| Facebook | 63.206 | Chuyện trò, hướng cộng đồng |
| Threads | 500 | Chân thật, đời thường, hợp quan điểm mạnh |
| Bluesky | 300 | Chuyện trò, am hiểu công nghệ |
| LinkedIn | 3.000 | Dài, chuyên nghiệp, ngôi thứ nhất có thẩm quyền |
| Reddit | 10.000 | Cộng đồng trước, minh bạch, tránh giọng công ty |
| Mastodon | 500 | Cộng đồng, am hiểu công nghệ, chống thương mại hoá |
| TikTok | 2.200 *(chỉ có trong README; **không có** trong bảng đăng ký của mã — lệch giữa tài liệu và mã)* | Nhanh, hiểu Gen-Z, hashtag xu hướng |

Chi tiết cấp nền tảng khác:
- **X** (hedgehog `shared.mjs:71-93`): URL luôn tính 23 ký tự; emoji và ký tự CJK tính 2; đếm theo độ dài chuỗi thô sẽ cho "đạt" ở
  279 mà nền tảng vẫn từ chối. Mẫu để viết hàm đếm riêng cho TikTok / Facebook nếu có quy tắc khác. Link trong thân bài làm giảm tiếp
  cận theo lập luận của repo → đặt trong reply (`tweet.mjs:65-75`; **chưa kiểm chứng ngoài repo**; social-toolkit lặp lại lập
  luận "thuật toán thích nội dung gốc, link để ở bình luận đầu" ở phần trợ giúp, cùng mức tin cậy).
- **Meta quảng cáo** (`ad.mjs:22-26`): nội dung chính 2.200 (hiển thị 125 trước "xem thêm"), headline 40 (hiển thị ~27 trên mobile),
  mô tả 30.
- **LinkedIn** (omniwrite `linkedin.yaml:8-16, 40`): 150–280 từ; đoạn 1–3 dòng; hashtag 0 hoặc 3–5 ở cuối; kết bằng một câu hỏi
  thật hoặc CTA; emoji 0–3. Bình luận đầu: 50–120 từ.
- **Reddit** (`reddit.yaml`): thân ≤ 600 từ; có TL;DR; không hashtag; plugin `reddit_plugin.py:32`: `max_words = 800`; LinkedIn
  plugin `max_words = 300` (`linkedin_plugin.py:33`); blog 1.000 (`plugins/base.py:26`).
- **YouTube / Shorts / Pinterest** (SocialSpark `server.ts` phần PLATFORM RELEVANCE): YouTube = tiêu đề hook + ý tưởng Shorts + khái niệm
  thumbnail + mô tả; Pinterest = tìm kiếm được, hướng dẫn từng bước / checklist; Instagram = reel, carousel, mẹo đáng lưu;
  Facebook = câu hỏi cộng đồng.

**Không repo nào cover nền tảng Việt Nam** (Zalo, Facebook Reels VN, TikTok Shop...) hay có quy tắc tiếng Việt cho từng nền tảng.

## 2. Quy trình chuyển thể

Mẫu chung của các repo (sửa cho video ngắn):

1. **Một brief gốc, một góc gốc** (omniwrite chạy `strategy` một lần rồi phát tín hiệu cho mọi nền tảng). Sự kiện / con số chỉ khai báo ở một nơi (`facts.md`).
2. **Giọng riêng cho từng nền tảng trước khi viết** (`tone_per_platform` trong `strategy.yaml`): Reddit ≠ LinkedIn ≠ blog.
3. **Viết song song** từng nền tảng (omniwrite `graph.py:66-119`, dùng `asyncio.gather`); nội dung phụ thuộc (bình luận ghim) chạy sau bài chính (`:113-115`).
4. **Biên tập chéo nền tảng một lượt**: cùng sự kiện, cùng giọng thương hiệu, sửa giọng sai nền tảng trước sở thích văn phong (`editor.yaml:16-21`).
5. **Kiểm bằng mã theo định dạng**: ký tự, hashtag, link, CTA, tuyên bố cấm (xem file cổng).
6. **Reroll theo giới hạn** (social-toolkit `tst-content.js:47-63`): khi bài vượt giới hạn của nền tảng mới, sửa bản có sẵn để
   vừa — không sinh lại từ đầu.
7. **Hậu xử lý xác định** (`postProcess`, `tst-content.js:70-88`): bỏ Markdown trên nền tảng không hiển thị Markdown (TikTok, Instagram, Facebook...
   chỉ giữ ở Reddit / Mastodon), bỏ link nếu không cho phép, đổi `<br>` và chuỗi `\n` chữ thành xuống dòng thật, gộp ≥ 3 dòng trống
   thành 2.

Khác biệt giọng *(suy luận từ các bảng trên, áp cho video ngắn tiếng Việt)*:

| Nền tảng | Hook ở đâu | Độ dài chữ | Hashtag | Giọng |
|---|---|---|---|---|
| TikTok | 1–2 giây đầu của video + dòng đầu caption | ngắn; caption phụ trợ cho video | 3–6, ngách + series | khẩu ngữ, kể bằng hình |
| Reels | cùng TikTok; caption mạnh hơn cho người lướt trang cá nhân | trung bình | 3–8 *(cần đo)* | chỉn chu hơn một chút |
| Shorts | tiêu đề là hook thứ hai (phải tìm kiếm được) | tiêu đề ngắn + mô tả | ít, trong mô tả | thông tin hơn |
| Facebook | dòng đầu bài + ảnh bìa | dài hơn được, nhưng vẫn cắt "xem thêm" | 0–3 | trò chuyện, cộng đồng |
| Thread / X | dòng đầu của bài đầu | ≤ 280 / bài | ≤ 1 | sắc, một ý một bài |

Tuyệt đối đừng **đệm cho đủ giới hạn** (social-toolkit đặt khoảng "mục tiêu 240–280" cho X ở `tst-config.js:38`), và đừng bắt LLM
tự đếm ký tự — đếm bằng mã.

## 3. Lịch đăng và series

### 3.1 Những gì các repo thực sự có

- **SocialSpark**: lịch 7 ngày. Mỗi bài có 9 trường: `day, platform, contentType, idea, time, cta, caption, hashtags, engagementTip`
  (`server.ts` phần `responseSchema`), cộng `strategy` (2–3 câu), 4 trụ cột nội dung (`pillars`), 3 mẹo (`tips`). Luật: đúng 7 ngày theo thứ tự Thứ Hai → Chủ Nhật, ≥ 5/7 bài bám chủ đề thương hiệu, **tạo lại một bài riêng** mà không sinh lại cả tuần
  (`server.ts:649-`). Hậu xử lý xác định để đảm bảo đủ ngày, đủ trường (`docs/BUG_FIXES.md` mục 2).
  Giao diện có chế độ Thẻ / Lịch / Kanban (cột "đầu tuần – giữa tuần – cuối tuần") và xuất Markdown / PDF / clipboard.
  Giờ đăng là **chuỗi do LLM sinh** ("09:00 AM", "01:30 PM"…), "Peak Hours" trong giao diện là dữ liệu mẫu cố định
  (`CalendarPreviewModal.tsx:50, 122`) — **không có nguồn đo**.
- **social-toolkit**: mỗi mục lịch = `{AI, nền tảng, bài, ngày, giờ}`, xuất CSV (`tst-schedule.js:40-52`); lưu `localStorage`, xoá cache là mất
  (README). Chưa thoát công thức CSV (ô bắt đầu bằng `=`, `+`, `-`, `@` có thể bị Excel hiểu là công thức — nhắc khi xuất lịch cho người dùng).
- **PostForge** (mô phỏng, `src/lib/data.ts:9-22, 38-43`): hàng đợi có `status` ∈ {Ready, Needs edit, Scheduled, Draft}, `scheduled`, danh sách
  `platforms`, `score` 0–100; bài theo nền tảng có `characters` / `limit`; `topics[{title, pillar, audience, goal}]`.
  README nói rõ mọi dữ liệu là mô phỏng — giữ lại **mô hình dữ liệu**, bỏ mọi con số (điểm chất lượng, xu hướng tương tác) vì không đo thật.
  Dữ liệu mẫu còn ghi giới hạn LinkedIn 300 và Facebook 632, lệch với 3.000 và 63.206 của social-toolkit — ví dụ cho việc đừng tin giới hạn trong dữ liệu giả.
- **Hedgehog** cố ý **không** lập lịch / đăng ("what comes out is a file that exited 0", `tweet-copy/SKILL.md` mục Scope), thread nằm ngoài phạm vi
  ("nếu ý cần bài thứ hai thì cắt xuống còn một ý").
- **Không repo nào** có series đúng nghĩa (mồi → đáp → mở rộng, cliffhanger giữa các phần, tái dùng tư liệu quay).

### 3.2 Khung lịch + series cho Agent 4 (đề xuất, ghép từ các mảnh trên; phần series là suy luận)

`calendar.md` mỗi dòng: `Ngày | Giờ (giả định) | Nền tảng | Trụ cột | Loại bài | Hook (ý) | Mục tiêu | CTA | Trạng thái | Phụ thuộc`.
- Trạng thái theo PostForge: `Nháp → Cần sửa → Sẵn sàng → Đã lên lịch`.
- Ít nhất 70 % bài bám 3–4 **trụ cột** (SocialSpark ≥ 5/7) — ngưỡng của repo là luật prompt, không phải bằng chứng hiệu quả; coi là khởi điểm.
- Mỗi tuần cân bằng **mục tiêu** (xem / lưu / chia sẻ / follow / bán), đừng đặt 7 bài cùng mục tiêu.
- **Series** (ví dụ "LEVEL 2 mở khoá sau 3 ngày"): phần 1 có "mồi" (câu hỏi mở hoặc kết quả chưa lộ) → phần 2 "đáp" (trả lời câu hỏi
  của bình luận) → phần 3 "mở rộng" (biến thể, thất bại, hậu trường). Bình luận ghim của phần N chính là hook của phần N+1.
  Tái dùng tư liệu: cùng một buổi quay → 1 video chính + 1 video "hậu trường" + 1 video trả lời bình luận.
- **Giờ đăng**: không repo nào cung cấp dữ liệu. Ghi `giả định` và đề xuất đo bằng analytics của kênh người dùng (xem lại sau 2 tuần).
  Không viết "giờ vàng" như sự thật.

## 4. Video → bài đăng (content-craft, ví dụ gần nhất với vedit)

Luồng của `tubaarif-dev/content-craft`: tải video / audio lên → **cắt ≤ 1 phút** (`uploadController.js:20-39`) → ffmpeg tách audio PCM → chuyển mono
16 kHz (`speechService.js:9-22`) → Google Speech-to-Text → prompt tạo N bài × nền tảng × ngôn ngữ × số từ (`generatePosts.js:63-107`) → trả
danh sách bài; còn blog và newsletter theo README. Lỗi đã thấy ở repo (chi tiết trong file lỗi & rủi ro): cấu hình STT cố định `en-US`
dù README nói 26 ngôn ngữ (`speechService.js:28-33`); so sánh `startTime >= endTime` trên chuỗi (`uploadController.js:20`); tách "bài" theo dòng
(`generatePosts.js:121-124`).

Điều đáng lấy cho vedit (vì vedit đã có transcript trong `analysis/analysis.json`, `faster-whisper` tuỳ chọn, mốc giây nguồn):
1. **Bài đăng bắt nguồn từ transcript, không từ trí nhớ mô hình**: ràng buộc "không đưa ý ngoài transcript, không ngày giờ trừ khi được cho"
   (`generatePosts.js:100, 103`). Mỗi tuyên bố / trích dẫn trong bài ghi kèm mốc giây nguồn để kiểm.
2. **Đa dạng cấu trúc** giữa các phiên bản của cùng một video (`:86` "tránh lặp mẫu câu giữa các bài") — rất hợp để tạo 3 phương án caption khác hẳn nhau.
3. **Một video → nhiều sản phẩm chữ**: caption TikTok, caption Reels, tiêu đề + mô tả Shorts, thread X / chuỗi bài Facebook, carousel
   (mỗi slide một ý, ≤ 6–8 từ), bài viết dài (blog / newsletter). Mỗi sản phẩm qua hợp đồng định dạng riêng.
4. **Lượt trích "câu đắt"**: chọn 3–5 câu của người nói đáng làm hook / pull-quote (đánh dấu `giây`), thay vì để AI viết lại bằng giọng AI.
5. **Chọn ngôn ngữ STT đúng**: nếu nói tiếng Việt thì transcript phải là tiếng Việt (bài học từ lỗi `en-US` của repo); kiểm với `vedit analyze`.

## 5. Điều nên tránh khi chuyển thể

- Chép cùng một đoạn lên mọi nền tảng. SocialSpark README tự nhận: caption Instagram nhiều đoạn phải cắt tay khi sang tweet 280 ký tự đơn lẻ.
- Hashtag chung chung cho mọi nền tảng.
- Tin "giờ vàng" do mô hình sinh. Tin điểm "chất lượng" 0–100 không có công thức.
- Để mô hình tự chia bài thành nhiều tin / nhiều dòng rồi tách bằng xuống dòng.
- Đăng tự động khi chưa có người duyệt: không repo nào (kể cả các repo có nút "đăng trực tiếp" như social-toolkit cho X, LinkedIn, Bluesky qua URL soạn sẵn) ép
  duyệt, nhưng đây là điểm rủi ro lớn nhất cho thương hiệu.

## Áp dụng vào vedit

**Đã có**: Agent 4 bước 6 (gói đăng bài, 3 phương án caption, 3–6 hashtag, CTA, bình luận ghim, giờ gợi ý "nêu cơ sở"), bước 7 (series
4–8 ý tiếp theo gắn phần một, lịch 1–2 tuần, tái dùng tư liệu), tham chiếu `vedit kb search "<nền tảng>"` trong `platforms`. Kho `platforms/` mới có
`kich-thuoc-va-vung-an-toan-cho-video-doc`, **chưa có ghi chú giới hạn ký tự / giọng từng nền tảng**.

**Thiếu / đề xuất theo ưu tiên**:
1. **Tạo `platforms/gioi-han-ky-tu-va-giong-theo-nen-tang.md`** (Agent 1 làm, có nguồn chính thức): TikTok, Reels, Shorts, Facebook, Threads, X, Zalo...
   kèm ngày kiểm, vì các con số trong repo mâu thuẫn và có thể lỗi thời. Agent 4 chỉ dùng số từ ghi chú này.
2. **Định dạng cho `vedit content check`**: `tiktok-caption`, `reels-caption`, `shorts-title`, `facebook-post`, `x-post` theo mẫu `ad.mjs` / `tweet.mjs` (hạn cứng = error,
   hạn hiển thị = warning), có hàm đếm ký tự riêng (NFC, emoji, URL).
3. **Hậu xử lý xác định** `postProcess` cho từng nền tảng (bỏ Markdown, chuẩn hoá xuống dòng, gộp dòng trống, NFC) — tránh chữ `**` rác
   trong caption TikTok.
4. **Luồng video → bài đăng**: Agent 4 đọc `analysis/analysis.json` (transcript), tạo bảng `Mốc giây | Câu của người nói | Dùng làm` rồi mới viết;
   mọi trích dẫn có mốc giây. Ghi vào checklist Agent 4 (đã có ý "transcript trong analysis.json" nhưng chưa có luật bám transcript).
5. **`calendar.md` chuẩn hoá cột** như mục 3.2, trạng thái 4 mức, trường `Phụ thuộc` cho series; xuất CSV có thoát ký tự công thức.
6. **Series**: nghiên cứu thêm (Agent 1 làm) vì các repo không dạy; nguồn nên tìm: hướng dẫn series trên TikTok / Reels của nhà sáng tạo, phân tích
   video series có sẵn bằng `vedit fetch` + `vedit analyze`.
7. Không cam kết giờ đăng hay số liệu tiếp cận: giữ luật "nêu cơ sở, không chắc thì nói không chắc".
