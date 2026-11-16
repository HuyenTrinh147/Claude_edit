---
title: Video mẫu âm thanh làm video nấu ăn: đánh số tượng thanh + khung tìm âm thanh (ref-mim-4)
category: techniques
tags: [mẫu âm thanh, đánh số, tượng thanh, khung tìm âm thanh, foley, nấu ăn, hook, ref-mim-4]
updated: 2026-11-16
sources:
  - video mẫu ref-mim-4 do người dùng gửi (2026-11), phân tích bằng vedit analyze + vedit bpm
---
# Video mẫu âm thanh làm video nấu ăn: đánh số tượng thanh + khung tìm âm thanh (ref-mim-4)

Một video mẫu (25.4 s, dọc 576×1024 gốc, 9:16) giới thiệu mẫu âm thanh cho video nấu ăn. Chỉ quan sát cấu trúc; hình,
âm thanh, logo, watermark của tác giả không dùng lại. Chưa phải cả kênh: **một video**.

## Cấu trúc đo được
| Đoạn | Giây | Cảnh | Nội dung |
|---|---|---|---|
| Hook | 0–3.0 | 3 cảnh ~1 s | tiêu đề "10 mẫu âm thanh làm video nấu ăn" (trắng viền đen, sao lấp lánh hồng/xanh), cảnh 2–3: dấu trang trắng → vàng + con trỏ bấm, "lưu ngay nhé" |
| Mục 1…11 | 3.0–21.4 | 12 cảnh, 1.0–1.8 s (một cảnh 4.0 s) | nhãn vàng "k. tượng thanh" ở trên + khung tìm âm thanh tối ở dưới; cắt đúng khung hành động |
| Khoảng lặng | ~11.4 | 0.64 s | tách hai nửa |
| Kết | 21.4–25.4 | 4.0 s im lặng | nền đen + khung tìm kênh |

- ASL của 12 cảnh mục ≈ 1.5 s (trung vị 1.23 s); hook 3 cảnh ~1.0 s. Ước lượng BPM 127 (độ chắc 0.57, âm thanh chủ yếu
  tiếng bếp nên chỉ là gợi ý), cảnh cắt ở nhịp ~0.47 s.
- Chữ: tiêu đề ở y≈0.28 (2 dòng); nhãn số y≈0.12–0.27; khung tìm âm thanh y≈0.6–0.7; phụ đề nhỏ dưới biểu tượng.
- Khung tìm âm thanh hiện kèm mỗi mục với từ khoá tiếng Anh (chopping, spray, cut fruit, open canned food, egg, whisk).
- Lỗi của chính video mẫu: tiêu đề nói 10 mẫu nhưng đánh số tới 11 và nhảy số — video của mình phải đếm đúng.

## Vì sao chạy
Mỗi 1–1.5 s có một hình + một tiếng + một nhãn mới: người xem được thưởng liên tục; nhãn tượng thanh viết lặp theo tiếng
nghe được nên "đọc ra tiếng". Nút lưu ở hook + khung tìm kênh ở cuối là hai chỗ chốt hành động.

## Áp dụng
Skill `edit-mau-am-thanh-danh-so`; form chữ `tieu-de-trang-vien-den`, `nhan-so-vang`, `khung-tim-am-thanh`,
`phu-de-nho-trang` (xem `typography/thu-vien-form-chu-cua-vedit-preset-texts-style`).
