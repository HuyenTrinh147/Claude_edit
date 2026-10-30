---
title: Kích thước và vùng an toàn cho video dọc
category: platforms
tags: [9:16, safe zone, tiktok, reels, shorts, kích thước]
updated: 2026-10-30
sources:
  - (ghi chú khởi tạo từ kiến thức nền — chạy Agent 1 để kiểm chứng & cập nhật)
---
# Kích thước và vùng an toàn cho video dọc

> (ghi chú khởi tạo từ kiến thức nền — chạy Agent 1 để kiểm chứng & cập nhật)

## Thông số chuẩn
- Khung 9:16, **1080x1920**, 30 fps (60 fps cho nội dung chuyển động nhanh). H.264 + AAC, `-movflags +faststart`.
- TikTok / Reels / Shorts đều dùng 9:16. Bài vuông 1:1 (1080x1080), dọc 4:5 (1080x1350) cho feed Instagram/Facebook.

## Vùng an toàn (giao diện app che phủ)
- **Trên ~12%**: thanh tab, nút tìm kiếm, nhãn "Live/Following".
- **Dưới ~20-25%**: tên tài khoản, caption, nhạc, thanh tiến trình.
- **Cạnh phải ~12-15%**: nút thích / bình luận / chia sẻ.
- Chữ quan trọng đặt ở khoảng 15%–75% chiều cao, lệch trái/giữa. Trong vedit: dùng `position` = `upper` / `center` / `lower`; tránh `bottom` cho chữ quan trọng.

## Đưa video ngang sang dọc
- `fit: cover` + `focus_x` (0..1) để giữ chủ thể khi crop — kiểm tra bằng view_frames.
- `fit: blur` khi cần giữ toàn bộ khung ngang (nền mờ phía sau).
