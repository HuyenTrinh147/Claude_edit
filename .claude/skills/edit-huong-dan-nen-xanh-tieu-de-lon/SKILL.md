---
name: edit-huong-dan-nen-xanh-tieu-de-lon
description: Công thức video hướng dẫn hiệu ứng ~60 s — kết quả mở đầu 7 s, rồi màn hình dựng nhỏ nằm giữa nền xanh trang trí với tên hiệu ứng thật to bên dưới (chữ script cam + chữ lớn vàng), mỗi hiệu ứng một khối 16–35 s, kết 3 s im lặng. Học từ video mẫu hướng dẫn hiệu ứng Flicker / Frame Click. Dùng khi dạy một hoặc hai hiệu ứng dựng trên màn hình máy tính.
argument-hint: <tên hiệu ứng> [tên hiệu ứng thứ hai]
---

**Chỉ là một tuỳ chọn**: dùng sau khi người dùng đã chọn hướng dựng; chỉ học cấu trúc, không chép hình / nhạc / tên kênh của video mẫu.

## Khi nào dùng
Dạy một hiệu ứng cụ thể bằng quay màn hình máy tính (khung ngang), muốn người xem nhớ **tên hiệu ứng** và thấy kết quả trước.

## Số đo thật (ref-mim-5, một video, 62.7 s, nguồn 576×1024)
- 5 cảnh dài: kết quả 0–2.0 s và 2.0–7.5 s (hai cảnh kết quả); hiệu ứng 1: 7.5–42.3 s (34.8 s, một cảnh liền); hiệu ứng 2: 42.3–58.6 s
  (16.3 s); đuôi 58.6–62.7 s trong đó 59.7–62.7 s im lặng với khung tìm kênh. Có nhạc (ước lượng ~99 BPM, độ chắc 0.77).
- Bố cục dọc: nền xanh đậm trang trí kín khung; màn hình dựng ngang chiếm dải y≈0.27–0.60 (toàn bề ngang, nhỏ); khối tiêu
  đề y≈0.60–0.76: chữ script cam ("Hiệu ứng") y≈0.63 + chữ lớn vàng→trắng ("FLICKER") y≈0.70; watermark kênh góc dưới
  phải. Tiêu đề **đứng nguyên cả khối hiệu ứng** rồi đổi sang tên hiệu ứng kế tiếp ("FRAME CLICK" + chữ script
  "Transition").
- Cảnh kết quả (0–7.5 s) nằm trên nửa trên, tiêu đề đã hiện dưới nền đen: người xem biết đang xem gì ngay từ khung đầu.

## Các bước
1. **Mở bằng kết quả** 5–8 s (1–2 cảnh), tiêu đề hiện ngay từ khung đầu: `style: "chu-script-cam-nho"` (nhãn) +
   `style: "tieu-gradient-lon-vang"` (tên hiệu ứng, ≤ 12 ký tự HOA).
2. **Khối hướng dẫn** 15–35 s mỗi hiệu ứng: video quay màn hình giữ nguyên tốc độ thật (thao tác cần xem kịp); nền
   `color:#0B2A6F` hoặc ảnh nền xanh của người dùng; tiêu đề đứng yên; chỉ cắt khi đổi sang hiệu ứng khác (không cắt
   giữa thao tác).
3. Hiệu ứng thứ hai: đổi **cả khối tiêu đề** cùng lúc với cú cắt, âm "whoosh" ngắn ở chỗ đổi.
4. **Kết 3 s**: im lặng, thanh tìm kênh (xem khung chung bên dưới); dùng tên kênh của người dùng.
5. `vedit textcheck <slug>`, xem `vedit frame --grid`: tiêu đề không chạm màn hình dựng (cách ≥ 0.03 khung).

## Khung chung của họ video hướng dẫn quay màn hình (4 mẫu ref-mim-5…8)
Kết quả trước (2–7 s) → các bước thao tác (mỗi bước một chú thích) → có thể kết quả lần nữa → **3 s cuối im lặng** với
khung tìm kênh (`khung-tim-am-thanh` kiểu thanh tìm kiếm + tên kênh của bạn). Ghi chú đầy đủ và số đo cả 4 mẫu:
`vedit kb show techniques/bon-mau-video-huong-dan-quay-man-hinh-capcut-ref-mim-5-den-8`.

## Giới hạn hiện tại của vedit (nói rõ với người dùng trước khi chọn hướng này)
EditPlan chưa có **video-trong-khung** (đặt một clip quay màn hình vào một hình chữ nhật trên nền khác) và chưa có **cắt
vùng tuỳ ý / zoom vào một góc** của video quay màn hình: `fit` chỉ cover / contain / blur, `zoom` luôn lấy tâm khung,
`focus_x` / `focus_y` chỉ dịch được khi nguồn rộng hơn khung. Hướng này vì vậy chỉ dựng đầy đủ khi (a) video quay màn hình
của người dùng đã đúng bố cục cần (chỉ thêm chữ, âm thanh, cắt), hoặc (b) làm tính năng `rect` / `crop` cho clip trước
(Agent 2 ghi vào `new_features`, người điều phối hỏi người dùng).
