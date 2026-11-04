---
name: noi-dung
description: Agent 4 — Content Creator: nghĩ ý tưởng nội dung, viết hook, lời thoại, chữ trên màn hình, caption, hashtag, CTA, series và lịch đăng cho video ngắn / bài đăng, có cổng chất lượng chống văn AI. Dùng khi người dùng muốn ý tưởng nội dung, caption, lời thoại hoặc gói đăng bài; khác /kich-ban (hướng dựng + EditPlan).
argument-hint: [slug dự án hoặc chủ đề] [mục tiêu, nền tảng, giọng...]
---

Yêu cầu nội dung: $ARGUMENTS

Trao đổi bằng tiếng Việt.

1. Nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh`.
2. Xác định bối cảnh: slug dự án trong yêu cầu (hoặc `vedit projects`, lấy dự án mới nhất đã có video xuất) → nội dung
   gắn với video đó (Agent 4 đọc `script/`, transcript, hồ sơ gu). Không có dự án → nội dung độc lập.
3. Dự án có sẵn: ghi yêu cầu nguyên văn `vedit note <slug> "<yêu cầu>" --kind "yêu cầu"`.
4. Agent tool `subagent_type: video-content-creator`: truyền slug (nếu có), yêu cầu nguyên văn, nền tảng, ngôn ngữ, giọng
   kênh. Người dùng chưa nói nền tảng → mặc định TikTok.
5. Gửi kết quả bằng SendUserFile: `projects/<slug>/content/post.md` (kèm `ideas.md`, `calendar.md` nếu có) hoặc thư mục
   `projects/_content/...`. Tóm tắt 3–5 điểm: góc / hook đề xuất, caption hay nhất, hashtag, ý tưởng series.
6. Người dùng khen / chê → ghi nguyên văn `vedit note <slug> "..." --kind "phản hồi"`, cập nhật `profile/gu-nguoi-dung.md`
   (thích / không thích / bài học), commit + push file hồ sơ.
7. Google Drive (khi người dùng muốn): như bước 12 của skill `lam-video` (thư mục `vedit/<slug>`, Google Doc từ `post.md`).
