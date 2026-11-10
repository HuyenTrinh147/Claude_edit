---
name: edit-toc-do-cong-chu-u
description: Speed ramp cong chậm-nhanh-chậm (đường chữ U/vòm) trong mỗi cảnh ~1.2 s, học từ video quán cà phê mẫu. Dùng khi muốn cảnh lia máy/đi xuyên không gian mượt, có cảm giác điện ảnh trên nhạc có nhịp.
argument-hint: <clip nguồn> <giây vào> <giây ra>
---

**Chỉ là một tuỳ chọn**: dùng sau khi người dùng đã chọn hướng dựng và hướng đó hợp với chiêu này; không ép vào mọi video. Nếu không hợp, bỏ qua.

## Khi nào dùng
Cảnh có chuyển động máy liên tục (đi xuyên quán, lia, vuốt) dài 1–1.5 s sau khi dựng. Không dùng cho cảnh người nói.

## Quan sát
v1 hiển thị đồ thị tốc độ CapCut trên mỗi cảnh: dạng U (chậm vào-nhanh giữa-chậm ra), vòm (nhanh rồi chậm) và hai gợn. Hệ số cụ thể KHÔNG đo được; số dưới là đề xuất xấp xỉ.

## Cách làm trong vedit (chưa có speed_curve, chỉ `Clip.speed` hằng số)
Tách 1 cảnh thành 3 clip liên tiếp cùng `source`, nối bằng cắt cứng (không transition):
- U: speed 0.6 (30% đầu) / 1.8 (40% giữa) / 0.6 (30% cuối).
- Vòm (nhanh vào, chậm ra): 1.8 / 1.0 / 0.5.
Ví dụ cảnh 1.2 s đầu ra, nguồn từ 12.0: clip A start 12.00 end 12.22 speed 0.6 (0.36 s); clip B 12.22-12.98 speed 1.8 (0.42 s); clip C 12.98-13.12 speed 0.6 (0.24 s)... tính lại để tổng = độ dài cảnh trên timeline. Thêm `motion: punch` nhẹ (amount nhỏ) ở đầu đoạn nhanh nếu muốn nhấn; `look.preset: warm_food` cho cảnh quán.

## Lỗi hay gặp
Speed < 0.5 từ clip 30 fps -> giật (không nội suy khung); đổi tốc độ đột ngột -> thấy bậc; âm gốc bị méo -> `mute: true` và dùng nhạc.
Đề xuất cho dev: thêm trường `speed_curve` vào Clip (render bằng một biểu thức setpts, xem `vedit kb show techniques/speed-ramp-freeze-frame-keyframe-zoom-va-split-screen`).

Nguồn: ref-mim-1..3 (mẫu 3 video, chưa phải cả kênh; quan sát 2026-11). Chi tiết số đo: `vedit kb show techniques/so-do-nhip-cat-toc-do-am-thanh-3-video-mau-ref-mim`.
