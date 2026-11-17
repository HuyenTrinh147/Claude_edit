---
name: tim-font
description: Agent 8 — Font chữ: nhận nguồn font người dùng đưa (link, zip, thư mục Drive) hoặc tự tìm font tiếng Việt miễn phí, kiểm đủ dấu và giấy phép bằng `vedit fonts`, chọn bộ font hợp vibe và màu của video, xuất ảnh so sánh. Dùng khi người dùng muốn thêm / đổi font, hoặc chê font cơ bản.
argument-hint: [slug dự án] [vibe, màu, nguồn font nếu có]
---

Yêu cầu: $ARGUMENTS

Trao đổi bằng tiếng Việt.

1. Nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh`.
2. Xác định dự án và nguồn font người dùng đưa (link, file trong chat `/root/.claude/uploads/...`, thư mục Drive). Ghi yêu cầu nguyên văn
   `vedit note <slug> "<yêu cầu>" --kind "yêu cầu"`.
3. Agent tool `subagent_type: video-font-picker`: truyền slug, yêu cầu, vibe / màu người dùng nói, nguồn font.
4. Gửi `projects/<slug>/fonts/specimen.jpg` và `fonts.md` bằng SendUserFile; tóm tắt bộ font chọn (tên họ, vai trò, màu), giấy phép, điều cần người dùng xác nhận.
5. Người dùng đồng ý → bạn thêm preset vào `vedit/textstyles.py` theo thông số đề xuất (kèm test), tạo lại `assets/styles/gallery.jpg`, commit + push.
6. Cập nhật trang Studio (`studio/<slug>`: `members.video-font-picker`, và `fonts/<slug>` với `fonts.json`) nếu người dùng đang dùng trang đó.
