---
name: kich-ban
description: Agent 2 — từ video của người dùng, nghiên cứu trend/từ khoá/hashtag và viết kịch bản video ngắn kèm EditPlan, có thể lưu kịch bản lên Google Drive. Dùng khi người dùng chỉ muốn ý tưởng/kịch bản, chưa cần dựng.
argument-hint: <link hoặc đường dẫn video> <mục tiêu, nền tảng, độ dài...>
---

Người dùng muốn kịch bản cho: $ARGUMENTS

Trao đổi bằng tiếng Việt.

1. Nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh`.
2. Lấy video như skill `lam-video` (file tải lên trong chat hoặc link → `vedit fetch "<đường dẫn/link>"`; bị chặn mạng thì hướng dẫn thêm Allowed domains
   hoặc tải lên `inbox/` trên GitHub rồi `git pull`). Thiếu mục tiêu thì hỏi; mặc định TikTok ~30 giây.
3. `vedit analyze "<video>" --name "<tên ngắn>"` → slug.
4. Gọi Agent tool với `subagent_type: video-scriptwriter` (slug, video, mục tiêu, nền tảng, độ dài, phong cách),
   dặn chạy `vedit validate <slug>` tới khi hợp lệ.
5. Gửi `projects/<slug>/script/script.md` bằng SendUserFile và tóm tắt: ý tưởng, hook, insight trend, hashtag.
6. Nếu người dùng muốn lưu lên Google Drive: dùng công cụ Google Drive đang kết nối, tạo thư mục `vedit/<slug>`
   và Google Doc từ nội dung `script.md` (`textContent`, `contentMimeType: text/markdown`).
7. Gợi ý bước tiếp: `/sua-video <slug>` để dựng & xuất video theo kịch bản này.
