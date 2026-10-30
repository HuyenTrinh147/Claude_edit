---
name: lam-video
description: Làm trọn một video ngắn từ video của người dùng — tải video vào, phân tích, Agent 2 viết kịch bản theo trend, Agent 3 dựng và xuất, gửi kết quả (và lưu kịch bản lên Google Drive nếu muốn). Dùng khi người dùng đưa video/link kèm mục tiêu và muốn có video hoàn chỉnh.
argument-hint: <link hoặc đường dẫn video> <mục tiêu, nền tảng, độ dài, phong cách...>
---

Người dùng muốn làm video: $ARGUMENTS

Bạn là người điều phối hệ thống vedit trong workspace này. Trao đổi bằng tiếng Việt, ngắn gọn; báo tiến độ sau mỗi bước.

1. **Chuẩn bị**: nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh` ở thư mục repo.
2. **Lấy video**:
   - Link (Google Drive, YouTube, TikTok, link trực tiếp) → `vedit fetch "<link>"`. Nếu báo bị chặn mạng, nói rõ tên
     miền bị chặn và hai cách: thêm tên miền vào Allowed domains trong cài đặt môi trường, hoặc tải video lên
     GitHub vào thư mục `inbox/` của nhánh hiện tại rồi báo lại (khi đó chạy `git pull` và lấy file trong `inbox/`).
   - Đường dẫn file trong workspace → dùng luôn. Không có video → hỏi người dùng.
3. **Làm rõ yêu cầu** chỉ khi thiếu mục tiêu. Mặc định: TikTok, khoảng 30 giây, tiếng Việt.
4. **Phân tích**: `vedit analyze "<video>" --name "<tên ngắn>"` → ghi lại slug dự án.
5. **Agent 2** — gọi Agent tool với `subagent_type: video-scriptwriter`, prompt gồm: slug, đường dẫn video, mục tiêu,
   nền tảng, độ dài, phong cách/khán giả nếu có, và dặn: phân tích đã chạy, viết `script/script.json` +
   `edit_plan.json`, chạy `vedit validate <slug>` tới khi hợp lệ, không cần làm bước Google Drive.
   Sau đó tóm tắt cho người dùng: ý tưởng, hook, các cảnh chính, hashtag.
6. **Agent 3** — gọi Agent tool với `subagent_type: video-editor`: dự án `<slug>`, dựng theo EditPlan, preview, tự
   kiểm tra khung hình, sửa lỗi, rồi `vedit render <slug>` xuất bản chính thức.
7. **Gửi kết quả** bằng SendUserFile: `projects/<slug>/renders/final.mp4`, `final.jpg`, `script/script.md`.
8. **Google Drive** (khi người dùng muốn, hoặc hỏi một câu nếu chưa rõ): dùng công cụ Google Drive đang kết nối —
   tìm/tạo thư mục `vedit` ở My Drive, tạo thư mục con tên slug, tạo Google Doc từ nội dung `script.md`
   (`textContent`, `contentMimeType: text/markdown`) và file `edit_plan.json` (`disableConversionToGoogleType: true`).
   Video không tải lên Drive qua kết nối này được (quá lớn) — người dùng tải video từ file đã gửi trong chat.
9. Kết thúc: đường dẫn kết quả, link Drive (nếu có), và gợi ý chỉnh sửa tiếp bằng `/sua-video <slug> <yêu cầu>`.
