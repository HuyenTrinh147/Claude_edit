---
title: Thư viện nhạc nền của vedit: pastel, beat, lofi + chỉ mục library.json
category: audio
tags: [nhạc nền, bpm, beat, lofi, pastel, library.json, vedit music, vedit bpm]
updated: 2026-11-16
sources:
  - vedit/musicgen.py
  - vedit/beat.py
  - kiểm bằng tests/test_beat_textcheck.py
---
# Thư viện nhạc nền của vedit: pastel, beat, lofi + chỉ mục library.json

Nhạc nền có hai nguồn: (1) nhạc tạo bằng code (không file, không bản quyền) và (2) file nhạc của người dùng trong
`assets/music/` (chỉ dùng nhạc có quyền sử dụng; file không commit, chỉ commit chỉ mục).

## Nhạc tạo bằng code — `vedit music <dự án> --duration <giây> --style <tên> [--seed N]`
`vedit music --list` in lại bảng này. Bài luôn dài đúng một số nguyên ô nhịp, xác định theo seed.

| Kiểu | BPM đích | Không khí | Dùng khi |
|---|---|---|---|
| `pastel` | ~104 | vui, hộp nhạc / kalimba | đồ ăn, mèo, game pastel, nhạc thưa dưới giọng |
| `beat` | ~122 | sôi nổi, trống rõ (kick 1 + "và" của 3, clap 2–4, hat 8) | cắt theo beat 1–1,5 s, mẹo / công thức, showcase |
| `lofi` | ~80 | chậm, ấm, swing, vinyl | dưới giọng đọc, vlog, kể chuyện, cảnh thư giãn |

Đã kiểm: 20 s → pastel 108 BPM, beat 120, lofi 84 (khớp số ô nhịp; `vedit bpm` đo lại đúng ±3).

## Nhạc của người dùng — `vedit bpm`
- `vedit bpm [file|thư mục]`: độ dài, BPM, độ chắc, nhịp đầu, đoạn sôi nhất, mean dB (ước lượng bằng tự tương quan của
  đường bao onset, chấm theo bội số chu kỳ để khỏi nhầm tỉ lệ 3:2 với nhạc lệch phách). Độ chắc < 0.3 = đoán.
- `vedit bpm --index`: ghi `assets/music/library.json` (BPM, nhịp đầu, đoạn sôi nổi, dB + `mood`, `tags`, `note` điền
  tay; chạy lại giữ nguyên phần điền tay).

## Chọn nhạc theo nhịp cắt
Độ dài cảnh = số nguyên nhịp: 120 BPM → 0.5 s/nhịp → cảnh 1.0 / 1.5 s; 84 BPM → 0.71 s → 1.43 s; đặt điểm cắt trên
`nhịp đầu + k × 60/BPM`, lệch ≤ 0.08 s. Có giọng đọc: nhạc `volume` 0.15–0.25 và `duck: true`; không giọng, cắt theo beat:
0.3–0.4. Agent: `video-music-picker` (skill `chon-nhac`).
