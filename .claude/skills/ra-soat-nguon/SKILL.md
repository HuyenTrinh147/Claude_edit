---
name: ra-soat-nguon
description: Agent 7 — Cameramen: rà soát toàn bộ clip / ảnh nguồn của một dự án (nội dung, độ nét, rung, mặt người dùng hay người lạ, tiếng gốc), tải nguồn mới từ Google Drive, tạo bản 1080p và bản cắt cận từ file 4K, ghi footage.md và chỉ ra thiếu cảnh gì. Dùng khi có nguồn mới, trước khi viết kịch bản, hoặc khi người dùng hỏi mình đang có cảnh gì.
argument-hint: [slug dự án] [điều cần chuẩn bị, ví dụ "cắt cận nhân bánh"]
---

Yêu cầu: $ARGUMENTS

Trao đổi bằng tiếng Việt.

1. Nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh`.
2. Xác định dự án (slug hoặc dự án mới nhất). Đọc `projects/<slug>/director.json` nếu có (nguồn người dùng đã chọn, thư mục Drive).
3. Agent tool `subagent_type: video-cameraman`: truyền slug, yêu cầu nguyên văn, ý tưởng của người dùng.
4. Gửi `projects/<slug>/footage.md` và `cameramen.md` bằng SendUserFile (nếu có); tóm tắt: số nguồn, cờ lộ mặt / mờ / rung, còn thiếu gì cần quay thêm.
5. Cập nhật bảng tiến độ trên trang Studio (`studio/<slug>`: `members.video-cameraman`, `pipeline.camera`) khi người dùng đang dùng trang đó.
