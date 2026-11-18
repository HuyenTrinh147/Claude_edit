---
title: Tự chỉnh màu và độ nét theo nội dung (vedit grade)
category: techniques
tags: [màu, độ nét, đồ ăn, look, grade, editor]
updated: 2026-11-18
sources:
  - vedit/autograde.py
---
# Tự chỉnh màu và độ nét theo nội dung

Biên tập (Agent 3) chạy bước này trước khi render bản xem trước, mọi video:

`vedit grade <dự án | plan.json> --content food|nguoi|phong-canh|mac-dinh [--source file@giây ...] [--apply]`

- Đo vài khung hình (độ sáng, dải sáng tối, độ rực, độ ấm, độ nét) rồi đề xuất các trường của `look`:
  `saturation`, `contrast`, `brightness`, `warmth`, `sharpen`. `--apply` ghi vào plan, bản cũ lưu `*.pre-grade.json`.
- Đồ ăn: đẩy ấm, tăng độ rực tối đa ×1,32, tương phản nhẹ, làm nét ~0,4. Có người: nhẹ tay hơn (rực ≤ ×1,10) để da không cam.
- Đây là ước lượng theo số đo, KHÔNG phải cam kết đẹp: luôn xem lại khung hình trước / sau (`vedit frame`) và chỉnh tay nếu
  da người ám cam, đồ ăn bị sặc, vùng sáng cháy, clip HDR đã tone-map khác nhau.
- Khi dùng `grade`, `look.preset` về `none` để không chồng màu hai lần.
- Chạy trên intro dựng ngoài EditPlan thì ghi `look` vào `intro_plan_v2.json` (bước tạo nền 4 khung không đổi).
