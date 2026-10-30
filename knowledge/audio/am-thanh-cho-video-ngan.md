---
title: Âm thanh cho video ngắn
category: audio
tags: [âm thanh, nhạc nền, loudness, ducking, sfx, bản quyền]
updated: 2026-10-30
sources:
  - (ghi chú khởi tạo từ kiến thức nền — chạy Agent 1 để kiểm chứng & cập nhật)
---
# Âm thanh cho video ngắn

> (ghi chú khởi tạo từ kiến thức nền — chạy Agent 1 để kiểm chứng & cập nhật)

- **Loudness**: xuất ở khoảng -14 LUFS (vedit bật `normalize_audio` mặc định), true peak ≤ -1.5 dBTP.
- **Nhạc nền dưới giọng nói**: volume 0.12-0.3 (≈ -18 đến -10 dB) và bật ducking để nhạc tự nhỏ khi có lời.
- **Âm thanh trend**: tăng khả năng được đề xuất, nhưng tài khoản doanh nghiệp thường chỉ được dùng thư viện nhạc
  thương mại của nền tảng — kiểm tra bản quyền trước khi chèn nhạc vào file xuất; có thể xuất không nhạc rồi
  chọn sound trend ngay trong app.
- **SFX**: whoosh khi chuyển cảnh, "pop" khi chữ xuất hiện, "ding" khi nêu con số — nhỏ, ngắn, không lạm dụng.
- Giọng nói rõ hơn nhạc: lời thoại luôn ưu tiên; cắt tiếng ồn nền và khoảng lặng.
