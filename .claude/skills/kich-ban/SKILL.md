---
name: kich-ban
description: Agent 2 — từ video của người dùng, đề xuất 2-3 hướng dựng để người dùng chọn, rồi viết kịch bản video ngắn kèm EditPlan theo hướng đã chọn; có thể lưu lên Google Drive. Dùng khi người dùng muốn ý tưởng, hướng dựng hoặc kịch bản, chưa cần dựng.
argument-hint: <link hoặc đường dẫn video> <mục tiêu / ý tưởng, nền tảng, độ dài...>
---

Người dùng muốn kịch bản cho: $ARGUMENTS

Trao đổi bằng tiếng Việt.

1. Nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh`.
2. Lấy video như skill `lam-video` (file tải lên trong chat hoặc link → `vedit fetch "<đường dẫn/link>"`; bị chặn mạng
   thì nói tên miền bị chặn và cách mở, hoặc nhờ tải thẳng vào chat).
3. `vedit analyze "<video>" --name "<tên ngắn>"` → slug; `vedit note <slug> "<lời người dùng>" --kind "yêu cầu"`.
4. Agent tool `subagent_type: video-scriptwriter`, *Bước 1* (đề xuất hướng dựng; truyền nguyên văn ý tưởng riêng của
   người dùng nếu có).
5. Cổng duyệt như bước 5 của skill `lam-video` (AskUserQuestion với các hướng trong `script/concepts.md`; ghi lựa chọn
   bằng `vedit note`).
6. `video-scriptwriter`, *Bước 2* với hướng đã chọn + ghi chú.
7. Gửi `projects/<slug>/script/script.md` (và `concepts.md`) bằng SendUserFile; tóm tắt hook, nhịp, chiêu chữ ký,
   hashtag.
8. Người dùng muốn lưu Drive: công cụ Google Drive đang kết nối — thư mục `vedit/<slug>`, Google Doc từ `script.md`.
9. Gợi ý bước tiếp: `/sua-video <slug>` để dựng & xuất video theo kịch bản này.
