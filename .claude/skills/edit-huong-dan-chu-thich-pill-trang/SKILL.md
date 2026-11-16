---
name: edit-huong-dan-chu-thich-pill-trang
description: Công thức video "N kiểu / N bước" ~90 s quay màn hình điện thoại — mỗi bước một chú thích trắng bo tròn chữ đen đặt giữa phần xem trước và dòng thời gian, mỗi chú thích 3–6 s, ba khối kỹ thuật ~25–30 s, thẻ tiêu đề đầu, kết 3 s im lặng. Học từ video mẫu 3 kiểu chuyển cảnh. Dùng khi dạy nhiều kỹ thuật dựng bằng quay màn hình điện thoại.
argument-hint: <số kỹ thuật> <chủ đề>
---

**Chỉ là một tuỳ chọn**: dùng sau khi người dùng đã chọn hướng dựng; chỉ học cấu trúc. Video mẫu là bản dịch phủ chữ lên video nguồn của người khác — **chỉ dùng video quay màn hình của chính người dùng**, không dịch / đăng lại video của người khác.

## Khi nào dùng
Dạy 2–4 kỹ thuật, mỗi kỹ thuật 5–8 thao tác ngắn, quay màn hình điện thoại (khung gần vuông 0.7).

## Số đo thật (ref-mim-6, một video, 91.7 s, nguồn 576×828)
- 13 cảnh: thẻ tiêu đề 0–3.8 s ("3 kiểu chuyển cảnh nhất định phải biết." trên nền đen); các cảnh 1.4–22 s theo từng kỹ
  thuật (kỹ thuật 1 ≈ 5–28 s, kỹ thuật 2 ≈ 28–58 s, kỹ thuật 3 ≈ 58–88 s); khoảng im lặng cuối 88.8–91.7 s.
- Chú thích: nền trắng bo tròn, chữ đen thường (câu đủ ý, có dấu chấm), **một thao tác một câu** ("Đưa video sau vào Ảnh
  trong ảnh.", "Ở đầu video, kéo Độ hòa trộn về 0.", "Tăng Độ hòa trộn lên 100."), cỡ chữ ≈ 7 % chiều ngang, tâm y≈0.50
  (khe giữa phần xem trước và dòng thời gian); câu mở khối cũng đánh số ("3. Chuyển cảnh mặt nạ."), mỗi câu hiện 3–6 s.
- Nội dung chữ **khớp thao tác đang diễn ra** trên màn hình trong chính giây đó.

## Các bước
1. Liệt kê N kỹ thuật, mỗi kỹ thuật chia thành các thao tác (một thao tác = một câu ≤ 12 tiếng).
2. Thẻ đầu 3–4 s: `style: "chu-thich-pill-trang"` với câu "N kiểu … nhất định phải biết." trên cảnh đầu hoặc nền đen.
3. Mỗi thao tác: `style: "chu-thich-pill-trang"`, `start` = lúc thao tác bắt đầu, hiện ≥ ký tự / 15 + 0.5 s (≥ 2.5 s thực tế);
   câu mở mỗi kỹ thuật đánh số "k. Tên kỹ thuật.".
4. Giữ `y` ≈ 0.5 nhưng **dời lên / xuống** nếu che đúng chỗ ngón tay / nút đang bấm (xem khung bằng `--grid`).
5. Âm thanh: giọng người dẫn hoặc nhạc nhẹ `volume ≤ 0.15`; mẫu gần như không có nhạc lớn.
6. Kết 3 s im lặng + thanh tìm kênh. `vedit textcheck <slug>` rồi `/soat-chu`.

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
