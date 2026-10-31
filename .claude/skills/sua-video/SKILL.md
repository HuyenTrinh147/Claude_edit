---
name: sua-video
description: Agent 3 — dựng, chỉnh sửa và xuất video của một dự án vedit theo yêu cầu bằng lời (vd "chữ to hơn, bỏ cảnh 3, thêm zoom"), có agent phản biện soi lỗi trước khi giao. Dùng khi người dùng muốn render, sửa hoặc xuất lại video.
argument-hint: [slug dự án] [yêu cầu chỉnh sửa]
---

Yêu cầu: $ARGUMENTS

Trao đổi bằng tiếng Việt.

1. Nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh`.
2. Xác định dự án: slug trong yêu cầu; nếu không có, `vedit projects` và lấy dự án mới nhất có `edit_plan.json`
   (hỏi lại nếu có nhiều dự án và không rõ ý).
3. Ghi yêu cầu nguyên văn: `vedit note <slug> "<yêu cầu>" --kind "yêu cầu sửa"`. Nếu yêu cầu là lời chê bản trước, cập
   nhật luôn `profile/gu-nguoi-dung.md`.
4. Nếu yêu cầu đổi hẳn phong cách / ý tưởng (không phải chỉnh chi tiết) → quay về cổng duyệt của skill `lam-video`
   (bước 4–5): đề xuất hướng mới cho người dùng chọn trước khi dựng.
5. Agent tool `subagent_type: video-editor`: dự án `<slug>`, yêu cầu nguyên văn, dựng bản preview và tự kiểm tra.
6. Thay đổi lớn → `video-critic` soi bản preview; CẦN SỬA thì giao lại `video-editor` (tối đa 2 vòng).
7. `video-editor` xuất bản chính thức (`vedit render <slug>`; bản cũ vào `renders/history/`).
8. Gửi `projects/<slug>/renders/final.mp4` và `final.jpg` bằng SendUserFile, tóm tắt những gì đã thay đổi, hỏi cảm nhận;
   ghi phản hồi vào `project.md` và hồ sơ gu như bước 11 của `lam-video`.
