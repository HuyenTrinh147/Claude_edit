---
name: edit-nen-mo-phong-to
description: Khung dọc có ảnh chính hẹp (~60% bề ngang) và nền là chính cảnh đó phóng to và làm mờ, học từ video quán cà phê mẫu. Dùng khi footage không phủ khung 9:16 hoặc muốn cảnh "điện ảnh nhẹ" thay vì cắt crop mất bố cục.
argument-hint: <clip> [mức mờ]
---

**Chỉ là một tuỳ chọn**: dùng sau khi người dùng đã chọn hướng dựng và hướng đó hợp với chiêu này; không ép vào mọi video. Nếu không hợp, bỏ qua.

## Khi nào dùng
Footage ngang hoặc gần vuông mà không muốn crop mất chi tiết; cảnh quán, nội thất, đồ ăn.

## Số đo thật
v1: vùng hình sắc nét chiếm khoảng x 0.20–0.80 (60% bề ngang), hai bên nền mờ phóng to cùng cảnh; kết hợp màu ấm vàng/cam tối (đèn vàng) trong cả 8 cảnh.

## Cách làm trong vedit
- `clips[i].fit: "blur"` (nền mờ phía sau) -> đã tạo nền mờ + ảnh giữa. Ảnh giữa trong vedit có thể rộng hơn 60% (tuỳ tỉ lệ nguồn); chưa có tham số thu nhỏ ảnh chính (đề xuất `fit_scale`).
- `look: {preset: "warm_food", vignette: 0.2}` hoặc `moody` cho cảnh tối. Kiểm tra bằng `vedit frame` mốc 1–2 s.
- Giữ cùng một kiểu fit cho cả video; đừng xen cover/blur ngẫu nhiên.

## Lỗi hay gặp
Nguồn đã dọc 9:16 -> fit blur vô nghĩa (không có viền); mờ quá mạnh làm màu nền ám; chữ chèn đè ranh giới ảnh/nền.

Nguồn: ref-mim-1..3 (mẫu 3 video, chưa phải cả kênh; quan sát 2026-11). Chi tiết số đo: `vedit kb show techniques/so-do-nhip-cat-toc-do-am-thanh-3-video-mau-ref-mim`.
