---
name: sua-video
description: Agent 3 — dựng, chỉnh sửa và xuất video của một dự án vedit theo yêu cầu bằng lời (vd "chữ to hơn, bỏ cảnh 3, thêm zoom"). Dùng khi người dùng muốn render, sửa hoặc xuất lại video.
argument-hint: [slug dự án] [yêu cầu chỉnh sửa]
---

Yêu cầu: $ARGUMENTS

Trao đổi bằng tiếng Việt.

1. Nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh`.
2. Xác định dự án: dùng slug trong yêu cầu; nếu không có, chạy `vedit projects` và lấy dự án mới nhất có
   `edit_plan.json` (hỏi lại nếu có nhiều dự án và không rõ ý).
3. Gọi Agent tool với `subagent_type: video-editor`: dự án `<slug>`, yêu cầu chỉnh sửa nguyên văn của người dùng
   (hoặc "dựng đúng theo EditPlan" nếu không có yêu cầu), kiểm tra bằng preview rồi `vedit render <slug>`.
4. Gửi `projects/<slug>/renders/final.mp4` và `final.jpg` bằng SendUserFile, tóm tắt những gì đã thay đổi.
