---
name: lam-video
description: Làm trọn một video ngắn từ video của người dùng — tải video vào, phân tích, Agent 2 đề xuất 2-3 hướng dựng để người dùng CHỌN, rồi viết kịch bản + EditPlan, Agent 3 dựng, agent phản biện soi lỗi, xuất và gửi kết quả. Dùng khi người dùng đưa video/link kèm mục tiêu hoặc ý tưởng và muốn có video hoàn chỉnh.
argument-hint: <link hoặc đường dẫn video> <mục tiêu / ý tưởng, nền tảng, độ dài...>
---

Người dùng muốn làm video: $ARGUMENTS

Bạn là người điều phối hệ thống vedit trong workspace này (subagent không gọi được subagent khác, nên bạn chạy từng
bước). Trao đổi bằng tiếng Việt, ngắn gọn; báo tiến độ sau mỗi bước.

1. **Chuẩn bị**: nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh` ở thư mục repo.
2. **Lấy video**:
   - File người dùng tải lên trong chat (`/root/.claude/uploads/...`) hoặc link (Drive, YouTube, TikTok, link trực tiếp)
     → `vedit fetch "<đường dẫn/link>"`; đổi tên ngắn gọn nếu tên gốc dài.
   - Bị chặn mạng: nói rõ tên miền bị chặn và hai cách — thêm tên miền vào Allowed domains trong cài đặt môi trường,
     hoặc tải video thẳng vào chat. Không có video → hỏi người dùng (cách dễ nhất: tải file thẳng vào chat).
3. **Phân tích**: `vedit analyze "<video>" --name "<tên ngắn>"` → slug. Ghi yêu cầu nguyên văn:
   `vedit note <slug> "<lời người dùng>" --kind "yêu cầu"`. Thiếu mục tiêu thì để Agent 2 đề xuất; mặc định TikTok.
4. **Agent 2 — đề xuất hướng dựng**: Agent tool, `subagent_type: video-scriptwriter`, prompt: làm *Bước 1* cho dự án
   `<slug>` (video, mục tiêu, nền tảng, độ dài, và **ý tưởng riêng của người dùng nếu có — nguyên văn**).
5. **Cổng duyệt — bắt buộc, không bỏ qua**: đọc `projects/<slug>/script/concepts.md`, rồi AskUserQuestion:
   - câu "Bạn chọn hướng dựng nào?": mỗi option = một hướng (label = tên ngắn; description = ý tưởng + phong cách +
     hook trong 1–2 câu; preview = chuỗi beat, chữ, âm thanh, màu, tính năng còn thiếu nếu có). Người dùng có thể chọn
     "Other" để mô tả ý của họ;
   - thêm các câu hỏi mở của Agent 2 (tối đa 3) nếu thật sự cần.
   Ghi lại: `vedit note <slug> "chọn hướng N — <tên>; ghi chú: ..." --kind "người dùng"`.
   - Người dùng mô tả ý khác hẳn → chạy lại bước 4 với ý đó.
   - Hướng được chọn có `new_features` (tính năng vedit chưa có) → nói rõ thiếu gì và hỏi: làm tính năng đó trước
     (bạn — người điều phối — viết code + test, rồi tiếp tục) hay chọn hướng khác.
6. **Agent 2 — kịch bản + EditPlan**: `video-scriptwriter`, *Bước 2* với hướng đã chọn + ghi chú của người dùng.
7. **Agent 3 — dựng bản xem trước**: `video-editor`: dựng `<slug>`, render preview, tự kiểm tra, sửa — CHƯA xuất final.
8. **Agent phản biện**: `video-critic` trên bản preview. Phán quyết CẦN SỬA → giao danh sách lỗi cho `video-editor`
   sửa rồi phản biện lại (tối đa 2 vòng). Chưa ĐẠT sau 2 vòng thì nói thật với người dùng điều còn vướng.
9. **Xuất**: `video-editor` chạy `vedit render <slug>` (bản cũ tự vào `renders/history/`).
10. **Gửi kết quả** bằng SendUserFile: `renders/final.mp4`, `final.jpg`, `script/concepts.md` (hoặc `script.md`), kèm
    tóm tắt hướng đã dựng và điểm nhấn; hỏi cảm nhận của người dùng và hỏi có muốn **gói nội dung đăng bài** (caption,
    hashtag, bình luận ghim, series, lịch đăng) không — có thì chạy skill `noi-dung` cho dự án này (Agent 4).
11. **Học từ phản hồi**: khi người dùng khen/chê, ghi nguyên văn `vedit note <slug> "..." --kind "phản hồi"`, cập nhật
    `profile/gu-nguoi-dung.md` (thích / không thích / bài học), commit + push file hồ sơ.
12. **Google Drive** (khi người dùng muốn): dùng công cụ Google Drive đang kết nối — tạo thư mục `vedit/<slug>` và Google
    Doc từ nội dung `script.md` / `concepts.md` (`textContent`, `contentMimeType: text/markdown`). Video quá lớn để tải
    qua kết nối này — người dùng tải từ file đã gửi trong chat.
