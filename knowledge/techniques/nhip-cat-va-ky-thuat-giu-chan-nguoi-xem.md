---
title: Nhịp cắt và kỹ thuật giữ chân người xem
category: techniques
tags: [jump cut, zoom, b-roll, nhịp, transition, phụ đề]
updated: 2026-10-30
sources:
  - (ghi chú khởi tạo từ kiến thức nền — chạy Agent 1 để kiểm chứng & cập nhật)
---
# Nhịp cắt và kỹ thuật giữ chân người xem

> (ghi chú khởi tạo từ kiến thức nền — chạy Agent 1 để kiểm chứng & cập nhật)

- **Jump cut**: cắt bỏ hơi thở, "ờ", khoảng lặng > 0.3s trong đoạn nói. Dùng silencedetect để tìm.
- **Punch-in zoom**: phóng 10-20% ở câu nhấn mạnh (vedit: `zoom: in`, `zoom_amount: 0.12-0.2`) — tạo cảm giác đổi góc máy khi chỉ có 1 cảnh quay.
- **B-roll** minh hoạ đè lên lời nói; **J-cut / L-cut**: âm thanh cảnh sau vào trước hình (hoặc ngược lại) cho chuyển cảnh mượt.
- **Chuyển cảnh**: mặc định cắt thẳng; dùng `fade`/`slide`/`zoomin` 0.2-0.4s chỉ khi đổi ý lớn.
- **Phụ đề luôn bật**: phần lớn người xem tắt tiếng; kiểu karaoke (tô màu từ đang đọc) tăng chú ý.
- **Nhịp theo nhạc**: đặt điểm cắt trùng phách (beat) của nhạc nền.
