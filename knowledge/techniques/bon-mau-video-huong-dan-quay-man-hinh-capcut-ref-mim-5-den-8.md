---
title: Bốn mẫu video hướng dẫn quay màn hình CapCut (ref-mim-5 đến 8)
category: techniques
tags: [hướng dẫn, quay màn hình, capcut, ref-mim-5, ref-mim-6, ref-mim-7, ref-mim-8, chú thích, bố cục]
updated: 2026-11-16
sources:
  - bốn video mẫu do người dùng gửi (2026-11), phân tích bằng vedit analyze / sheet / frame --grid / bpm
---
# Bốn mẫu video hướng dẫn quay màn hình CapCut (ref-mim-5 đến 8)

Bốn video mẫu cùng một họ: **hướng dẫn dựng bằng quay màn hình** (50–92 s, nguồn dọc 576×828–1024, có giọng / nhạc nhẹ).
Chỉ quan sát cấu trúc; hình, chữ, nhạc, watermark của tác giả không dùng lại. Chỉ **bốn video**, chưa phải cả kênh. Video
ref-mim-8 mang watermark @editwithmim; ba video kia thuộc các tác giả khác nhau.

## Bảng so sánh
| | ref-mim-5 hiệu ứng Flicker | ref-mim-6 3 kiểu chuyển cảnh | ref-mim-7 intro giới thiệu | ref-mim-8 text hiện sau đầu |
|---|---|---|---|---|
| Dài | 62.7 s | 91.7 s (nguồn 576×828) | 61.8 s | 50.9 s |
| Cảnh | 5 (rất dài) | 13 | 16 | 6 |
| Mở | kết quả 7.5 s | thẻ tiêu đề 3.8 s | kết quả 4.1 s | người dẫn nói 3 s |
| Bố cục | nền xanh + màn hình ngang nhỏ y 0.27–0.60 + tiêu đề lớn y 0.60–0.76 | màn hình điện thoại đủ khung + pill trắng y 0.50 | màn hình điện thoại đủ khung + chữ HOA y 0.78 | màn hình điện thoại giữa (rộng ~0.48) trên nền người dẫn tối mờ + phụ đề nghiêng y 0.80 |
| Chữ | script cam + chữ lớn vàng, đổi theo hiệu ứng | chú thích trắng đen, 1 thao tác / câu, đánh số | HOA trắng viền đen, từ khoá vàng, 1 động từ / bước | phụ đề viết tay nghiêng −4°, tiêu đề vàng ngoặc kép |
| Phần cuối | 3 s im lặng + thanh tìm kênh | 3 s im lặng + thanh tìm kênh | kết quả lại + 3 s im lặng | cảm ơn viền sticker + 3 s im lặng |
| Âm thanh | nhạc ~99 BPM (độ chắc 0.77) | gần như giọng / UI | nhạc ~89 BPM (0.55) | giọng người dẫn (BPM ước lượng không chắc) |

## Điểm chung (đúng ở cả 4 video)
1. **Kết quả hoặc người dẫn ở khung đầu** (≤ 7.5 s), không để người xem đoán sẽ học gì.
2. **Một thao tác ↔ một dòng chữ** cùng giây; chữ hiện ≥ 2.5 s, dòng ngắn.
3. **Đoạn kết 3.0 s im lặng** có thanh tìm kênh (3/4 video có biểu tượng nền tảng; ta dùng tên kênh của người dùng).
4. Cắt rất ít trong khối thao tác (thao tác phải xem kịp): ASL 3.9–14 s ở ref-mim-5/6/8; chỉ phần "biến thể kết quả" mới
   cắt ~1 s (ref-mim-7, 39.4–52.1 s).
5. Âm thanh nhỏ hơn video giải trí (mean −15.7 … −21.6 dB): tiếng giọng quan trọng hơn nhạc.

## Cho vedit
Skill: `edit-huong-dan-nen-xanh-tieu-de-lon`, `edit-huong-dan-chu-thich-pill-trang`, `edit-huong-dan-chu-buoc-in-hoa`,
`edit-huong-dan-nguoi-dan-nen-mo`. Form chữ mới: `chu-thich-pill-trang`, `buoc-in-hoa-trang-den`,
`tieu-gradient-lon-vang`, `chu-script-cam-nho`, `chu-thich-nghieng-viet-tay`, `tieu-de-vang-trich-dan`.
**Tính năng còn thiếu** (cả họ này cần): video-trong-khung (đặt clip quay màn hình vào hình chữ nhật trên nền khác),
cắt / zoom vùng tuỳ ý của clip, tách nền người để có viền sticker. Nếu không có, người dùng phải đưa video quay màn hình
đã đúng bố cục.
