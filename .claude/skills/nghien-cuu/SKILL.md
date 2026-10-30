---
name: nghien-cuu
description: Agent 1 — nghiên cứu một chủ đề dựng/edit video (kỹ thuật, trend, công cụ GitHub, tutorial YouTube, TikTok) và lưu ghi chú vào kho kiến thức knowledge/. Dùng khi người dùng muốn tìm hiểu, học hoặc cập nhật kiến thức về edit video.
argument-hint: <chủ đề> [nhanh|sâu]
---

Chủ đề nghiên cứu: $ARGUMENTS

Trao đổi bằng tiếng Việt.

1. Nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh`.
2. Gọi Agent tool với `subagent_type: video-researcher`, truyền chủ đề và độ sâu (mặc định vừa phải: 8-15 nguồn,
   4-7 ghi chú; "nhanh": 3-6 nguồn; "sâu": trên 20 nguồn).
3. Tóm tắt cho người dùng: ghi chú đã thêm/cập nhật (đường dẫn), 3-5 điểm đáng chú ý nhất, chủ đề nên tìm hiểu tiếp.
4. Workspace là tạm thời: commit thay đổi trong `knowledge/` ("Cập nhật kho kiến thức: <chủ đề>") và push lên nhánh
   hiện tại để giữ lại cho các phiên sau.
