---
name: edit-huong-dan-chu-buoc-in-hoa
description: Công thức video hướng dẫn làm mẫu chữ / intro ~60 s — mở bằng kết quả 4 s, quay màn hình điện thoại với chú thích bước chữ HOA đậm trắng viền đen (từ khoá vàng) ở vùng dưới, sau đó tổng hợp các biến thể kết quả cắt nhanh ~1 s, kết quả lại, 3 s im lặng. Học từ video mẫu hướng dẫn intro tiếng Indonesia. Dùng khi dạy template chữ, intro hoặc hiệu ứng có nhiều biến thể.
argument-hint: <tên mẫu / intro> <số biến thể>
---

**Chỉ là một tuỳ chọn**: dùng sau khi người dùng đã chọn hướng dựng; chỉ học cấu trúc, không chép hình hay chữ của video mẫu.

## Khi nào dùng
Dạy một mẫu chữ / intro / hiệu ứng có thể ra nhiều biến thể; muốn người xem thấy "ra được nhiều kiểu" ở cuối.

## Số đo thật (ref-mim-7, một video, 61.8 s, nguồn 576×1024, giọng + chữ tiếng Indonesia)
- 16 cảnh: kết quả 0–4.1 s (một cảnh); hướng dẫn 4.1–33.2 s (cảnh 2.7 / 4.0 / 22.4 s); sau 33.2 s các cảnh ngắn
  0.8–2.1 s (đặc biệt 39.4–52.1 s: 9 cảnh ~1 s, mỗi cảnh một biến thể kết quả); kết quả cuối 57.8–58.9 s; im lặng
  58.9–61.8 s với khung tìm kênh. Có nhạc nền (ước lượng ~89 BPM, độ chắc 0.55).
- Chú thích bước: chữ HOA đậm (kiểu Montserrat Black) trắng viền đen dày, **từ khoá đổi màu vàng**, tối đa 2 dòng × 3 tiếng,
  tâm y≈0.78 (ngay trên thanh công cụ của app, cách đáy ≥ 0.12); thẻ tiêu đề nhỏ hơn ở y≈0.70 lúc đầu ("MEMBUAT INTRO PERKENALAN").
- Mỗi bước một động từ: "PERTAMA SIAPKAN SATU", "PINDAHKAN KE OVERLAY", "BACKGROUND DAN KLIK", "DAN PILIH KERTAS",
  "FRAME DI DEPAN" → trong tiếng Việt: "ĐẦU TIÊN CHUẨN BỊ", "CHUYỂN LÊN OVERLAY", "NỀN VÀ BẤM".

## Các bước
1. **Mở bằng kết quả đẹp nhất** 3–4 s (một cảnh), không chữ giải thích.
2. **Phần hướng dẫn**: mỗi bước một chú thích `style: "buoc-in-hoa-trang-den"` (2 `texts` chồng nhau: cả dòng trắng + từ khoá
   vàng #FFD93D phủ lên đúng vị trí); chọn từ khoá = từ chỉ nút / công cụ cần bấm.
3. **Tổng hợp biến thể** (nếu có): 6–9 cảnh × ~1.0 s, mỗi cảnh một biến thể; cắt đều theo nhịp nhạc
   (`vedit bpm`, xem `/edit-nhip-cat-deu`), không chữ.
4. **Kết quả cuối** 1–2 s rồi 3 s im lặng + thanh tìm kênh.
5. `vedit textcheck <slug>`: chú thích 2 dòng 14 ký tự cần ≥ 1.5 s; nhịp 1 s của phần tổng hợp thì **không có chữ**.

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
