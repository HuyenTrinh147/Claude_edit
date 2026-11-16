---
name: edit-mau-am-thanh-danh-so
description: Công thức video "N mẫu âm thanh / N mẹo" ~25 s — hook tiêu đề có sao lấp lánh + nút lưu, mỗi mục 1–1,5 s với nhãn số thứ tự tượng thanh, khung tìm âm thanh dưới hình, cắt đúng tiếng thật, kết 4 s im lặng bằng khung tìm kênh. Học từ video mẫu 10 mẫu âm thanh làm video nấu ăn. Dùng khi làm video liệt kê âm thanh, mẹo, công cụ hoặc món theo số thứ tự.
argument-hint: <số mục> <chủ đề> [nền tảng]
---

**Chỉ là một tuỳ chọn**: dùng sau khi người dùng đã chọn hướng dựng và hướng đó hợp với chiêu này; không ép vào mọi video.
Chỉ học cấu trúc và nhịp, không chép hình, âm thanh, logo, tên kênh hay watermark của video mẫu.

## Khi nào dùng
Video liệt kê N thứ ngắn, mỗi thứ có một khoảnh khắc nhìn thấy + nghe thấy rõ (âm thanh nấu ăn, mẹo vặt, công cụ,
món ăn, đồ dùng). Cần có mỗi mục một cảnh quay ≥ 1 s có hành động rõ.

## Số đo thật (video mẫu ref-mim-4, quan sát 2026-11, chỉ một video)
- Tổng 25.4 s, dọc 9:16, 16 cảnh. Hook 3.0 s = 3 cảnh ~1 s cùng một tiêu đề; 12 cảnh mục dài 1.0–1.8 s (một mục 4.0 s
  là ngoại lệ); khung kết 4.0 s (21.4–25.4 s) im lặng hoàn toàn.
- Chữ: tiêu đề trắng viền đen dày + sao hồng / xanh lấp lánh ở y≈0.28; nhãn số vàng viền tối ở y≈0.12–0.27 ("1. Xắt
  xắt xắt", "2. Xịt xịt" — số + tượng thanh); khung tìm âm thanh tối màu ở y≈0.6–0.7 hiện kèm mỗi mục (từ khoá tiếng Anh
  + tên âm thanh); "lưu ngay nhé" nhỏ trắng dưới biểu tượng dấu trang (vàng khi "đã lưu").
- Có một khoảng lặng 0.64 s giữa video (≈ 11.4 s) để tách hai nửa. Mẫu đánh số nhảy cóc và có mục 11 dù tiêu đề nói 10
  → **của bạn thì đếm cho đúng với tiêu đề**.

## Các bước
1. **Chọn N mục** (6–11). Mỗi mục: một cảnh quay có hành động + một tiếng thật ở đúng khung hình hành động. Thiếu tiếng
   thật thì dùng SFX trong thư viện (`vedit sfx list <từ khoá>`); không thì SFX tổng hợp (`sfx:` trong `audio`).
2. **Hook 3 s** (3 cảnh × ~1 s, cùng tiêu đề): `texts` với `style: "tieu-de-trang-vien-den"` (≤ 2 dòng, ≤ 4 tiếng mỗi
   dòng) + 4–6 `graphics` sparkles quanh chữ (hồng #F58FB0, xanh #A9C7F5). Cảnh thứ 2–3: biểu tượng dấu trang
   (`images` hoặc `graphics`) + `style: "phu-de-nho-trang"` "lưu ngay nhé"; đổi trắng → vàng khi "bấm".
3. **Mỗi mục 1.0–1.5 s** (đừng đều tăm tắp: xen 1–2 mục 1.8–2.5 s): cắt cứng. Nhãn `style: "nhan-so-vang"` "k. tượng
   thanh" bật ngay khung cắt (`pop`); tượng thanh viết lặp theo tiếng ("Xắt xắt xắt", "Xịt xịt") — mỗi tiếng một chữ.
4. **Khung tìm âm thanh** `style: "khung-tim-am-thanh"` vào trễ ~0.25–0.3 s sau nhãn (mỗi lần chỉ một thứ mới), 2 dòng:
   từ khoá + tên âm thanh. Đặt dưới giữa khung (y 0.6–0.7), không che hành động chính; thử bằng `vedit frame --grid`.
5. **Âm thanh**: tiếng thật (hoặc SFX) rơi đúng khung hình hành động; không nhạc nền, hoặc nhạc rất thấp (≤ 0.12,
   `duck: true`). Chỉ chèn 0.5–0.6 s lặng một lần ở giữa để tách hai nửa.
6. **Kết 3–4 s**: nền tối + chữ mời xem tiếp (`style: "tieu-de-anton-pill-kem"` hoặc `phu-de-nho-trang`): "Tìm @<kênh
   của bạn> để xem thêm"; im lặng. Dùng tên kênh của người dùng, không dùng logo / giao diện của nền tảng.
7. `vedit textcheck <slug>` (thời gian đọc nhãn ≥ ký tự / 15 + 0.5 s; nhãn 1.2 s chỉ ≤ 10 ký tự) rồi `/soat-chu`.

## Lỗi hay gặp
Nhãn không kịp đọc (mục 1.0 s mà nhãn dài); khung tìm âm thanh che hành động; tiếng không khớp khung hình; đánh số
sai; bắt chước logo / tên người khác; quên kết im lặng nên kết bị cụt.

Ghi chú đầy đủ: `vedit kb show techniques/video-mau-am-thanh-lam-video-nau-an-danh-so-tuong-thanh-khun`.
Form chữ: `vedit styles` (ảnh mẫu `assets/styles/gallery.jpg`).
