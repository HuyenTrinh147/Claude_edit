---
name: edit-huong-dan-nguoi-dan-nen-mo
description: Công thức video hướng dẫn có người dẫn ~50 s — người dẫn nói thẳng 3 s kèm tiêu đề vàng trong ngoặc kép, rồi quay màn hình điện thoại đặt giữa khung trên nền chính cảnh người dẫn làm tối và mờ, phụ đề viết tay nghiêng nhẹ ở dưới, kết bằng người dẫn có viền sticker trắng cảm ơn + 3 s im lặng. Học từ video mẫu của kênh @editwithmim. Dùng khi người dùng có cảnh tự quay mặt nói và muốn dạy một tính năng dựng.
argument-hint: <tên tính năng> [có tự quay người dẫn không]
---

**Chỉ là một tuỳ chọn**: dùng sau khi người dùng đã chọn hướng dựng; người dẫn phải là **chính người dùng** (hoặc người đã đồng ý), không dùng hình người khác; chỉ học cấu trúc.

## Khi nào dùng
Người dùng tự quay một đoạn nói với camera (mở và kết) + một đoạn quay màn hình thao tác; muốn video thân thiện, có gương mặt.

## Số đo thật (ref-mim-8, watermark @editwithmim, một video, 50.9 s, nguồn 576×1024)
- 6 cảnh: người dẫn + quay màn hình 0–25.6 s (một cảnh dài, người dẫn nói ~3 s đầu rồi màn hình điện thoại vào); tiếp tục
  hướng dẫn tới 41.2 s; kết 41.2–50.9 s: người dẫn cảm ơn 41.2–48.0 s (3 cảnh 1.6–2.3 s) rồi 48.0–50.9 s im lặng với khung tìm kênh.
- **Mở (0–3 s)**: người dẫn nhìn camera, tay chỉ lên; tiêu đề vàng đậm viền đen 2 dòng ở y≈0.20–0.32: Cách làm /
  "Text hiện sau đầu" (tên tính năng trong ngoặc kép). Có vòng tròn nét đứt trắng quanh mặt khi nhấn mạnh.
- **Hướng dẫn**: màn hình điện thoại (khung dọc) đặt giữa, rộng ≈ 0.45–0.5 khung, y≈0.12–0.58, nằm trên **chính cảnh người
  dẫn đã làm tối và mờ**; tiêu đề vàng vẫn lộ lờ mờ hai mép (nằm dưới lớp tối). Phụ đề lời nói nghiêng ≈ −4°, trắng
  viết tay, 2 dòng, y≈0.80, mỗi câu 2–3.5 s ("Nhấn vào video." / "rồi đột 'Lớp phụ' song song với 'Lớp chính'.").
- **Kết**: người dẫn có **viền sticker trắng dày** quanh người, sao lấp lánh, mũi tên + chữ viết tay "Cảm ơn bạn đã dừng lại ở
  đây!" nghiêng, tim đỏ rải góc; cảnh cuối vẫy tay; rồi im lặng 3 s + thanh tìm kênh.

## Các bước
1. Người dùng quay **3–5 s nói mở** và **5–8 s nói kết** (tay chỉ / vẫy tay), 9:16.
2. Mở: `style: "tieu-de-vang-trich-dan"` (tên tính năng trong ngoặc kép) cùng `punch` 0.04 ở khung đầu.
3. Hướng dẫn: nền = cảnh người dẫn làm tối (`look` tối + clip `fit: "blur"`) và quay màn hình đặt giữa (xem giới hạn);
   phụ đề `style: "chu-thich-nghieng-viet-tay"` đồng bộ lời nói, mỗi câu ≥ ký tự / 15 + 0.5 s.
4. Kết: cảnh người dẫn + chữ viết tay cảm ơn (`style: "tieu-de-trang-vien-den"`, `rotation` −5), sparkles + tim bằng
   `graphics`; viền sticker trắng quanh người cần tách nền (chưa có — dùng `images` PNG đã tách sẵn nếu người dùng cung cấp).
5. 3 s im lặng + thanh tìm kênh. Giọng người dẫn là giọng thật của người dùng hoặc giọng AI do người dùng chọn.

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
