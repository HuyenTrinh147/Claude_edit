---
name: edit-nhan-ban-vat-theo-nhip
description: Hiệu ứng vật nhân bản/xuất hiện thêm mỗi nhịp (1 chai -> 3 -> 5) trên cùng một cảnh quay tĩnh, kèm đổi cỡ cảnh jump-cut. Dùng cho video sản phẩm, đồ uống, mẹo dựng cần điểm nhấn gây tò mò.
argument-hint: <vật> <số lần nhân bản>
---

**Chỉ là một tuỳ chọn**: dùng sau khi người dùng đã chọn hướng dựng và hướng đó hợp với chiêu này; không ép vào mọi video. Nếu không hợp, bỏ qua.

## Khi nào dùng
Có clip quay vật trên nền cố định (bệ cửa sổ, mặt bàn), muốn tạo cảm giác "vật hiện ra từng cái".

## Số đo thật
v2: 1 chai (4.4 s) -> 3 chai (5.2 s) -> 5 chai (6.0 s), sau đó 2 chai cận (8.4 s) -> 5 chai (10.0 s); khoảng giữa ~0.8–1.0 s. v3: vật A rồi A+B, đổi cỡ cảnh toàn/cận ở 4.5 / 5.3 / 6.2 / 7.0 / 7.8 s. Nhoè chuyển động ở 6.8 và 9.2 s.

## Cách làm trong vedit
1. Quay (hoặc nhờ người dùng quay) các take cố định tay: take 1 vật, take 2 hai vật, take 3 năm vật... cùng khung — vedit không tự nhân bản được.
2. Dựng: mỗi take 0.8–1.0 s, cắt cứng đúng nhịp; chỗ đổi cỡ cảnh dùng `transition hblur 0.12–0.2`.
3. Điểm nhấn mỗi lần "pop": `motion: {type: "punch", amount: nhỏ, duration: 0.15}` tại thời điểm vật mới xuất hiện + SFX `pop` (tổng hợp) cùng thời điểm.
4. Nếu tự tạo từ ảnh: cắt vật ra PNG trong suốt rồi `image_overlays` (x,y,width), thêm vật ở mỗi nhịp; hoặc dùng `vedit track` để gắn vật bám theo.

## Lỗi hay gặp
Khung hình khác nhau giữa các take -> nhảy; ánh sáng thay đổi giữa take; nhân bản mà không có nhịp -> mất hiệu ứng "đếm".
Thiếu trong vedit: tách nền/mask tự động; đề xuất ưu tiên thấp.

Nguồn: ref-mim-1..3 (mẫu 3 video, chưa phải cả kênh; quan sát 2026-11). Chi tiết số đo: `vedit kb show techniques/so-do-nhip-cat-toc-do-am-thanh-3-video-mau-ref-mim`.
