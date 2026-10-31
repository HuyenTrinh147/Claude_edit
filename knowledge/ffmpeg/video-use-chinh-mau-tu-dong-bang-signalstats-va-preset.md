---
title: video-use: Chỉnh màu tự động bằng signalstats và preset
category: ffmpeg
tags: [video-use, màu, color grade, signalstats, eq, colorbalance, curves, asc cdl, auto grade, ffmpeg]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/helpers/grade.py
  - https://github.com/browser-use/video-use/blob/main/helpers/render.py
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
---
# video-use: Chỉnh màu tự động bằng signalstats và preset

## Tư duy
"Your job is to **reason about the image**, not apply a preset. Look at a frame (via `timeline_view`), decide
what's wrong, adjust one thing, look again."

Mô hình trong đầu là **ASC CDL**. Mỗi kênh: `out = (in * slope + offset) ** power`, sau đó chỉnh saturation
chung. Trong đó:
- `slope` tác động vùng sáng;
- `offset` tác động vùng tối;
- `power` tác động trung tính.

Hai quy tắc cứng:
- Grade **từng đoạn lúc trích** (không grade sau concat, vì sẽ encode thêm một lần).
- "Never go aggressive without testing skin tones."

## Preset (nguyên văn filter)
| Tên | Filter | Ghi chú |
|---|---|---|
| `subtle` | `eq=contrast=1.03:saturation=0.98` | Sàn an toàn, gần như không thấy |
| `neutral_punch` | `eq=contrast=1.06:brightness=0.0:saturation=1.0,curves=master='0/0 0.25/0.23 0.75/0.77 1/1'` | Tăng tương phản + S-curve nhẹ, không lệch màu |
| `warm_cinematic` | `eq=contrast=1.12:brightness=-0.02:saturation=0.88,colorbalance=rs=0.02:gs=0.0:bs=-0.03:rm=0.04:gm=0.01:bm=-0.02:rh=0.08:gh=0.02:bh=-0.05,curves=master='0/0 0.25/0.22 0.75/0.78 1/1'` | Chỉ dùng khi chủ động chọn: +12% tương phản, đen sâu, −12% bão hoà, bóng ấm + sáng lạnh. Code ghi chú "too aggressive for standard launch content" |
| `none` | (copy) | Mặc định khi người dùng không yêu cầu |

Muốn look khác (chân dung, thiên nhiên, sản phẩm, MV...) thì "invent your own chain" và truyền vào bằng
`grade.py --filter '<raw ffmpeg>'`, hoặc ghi chuỗi filter vào trường `grade` của EDL.

## Auto-grade theo từng đoạn (`"grade": "auto"`)
Mục tiêu: "make it look clean without looking graded". Không LUT, không teal/orange, không curve kiểu phim. Mọi
điều chỉnh bị chặn trong khoảng ±8%.

**1. Lấy mẫu khoảng 10 khung trong đoạn.** Tốc độ lấy mẫu `fps = clamp(10 / thời lượng, 0.5, 10)`:
```bash
ffmpeg -ss S -i in.mp4 -t D -vf "fps=F,signalstats,metadata=print:file=stats.txt" -f null -
```
**2. Đọc thống kê** `lavfi.signalstats.YAVG / YMIN / YMAX / SATAVG / YBITDEPTH`, chia cho `2^bit − 1` để đưa về
0..1:
- `y_mean = mean(YAVG)`
- `y_range = mean(YMAX) − mean(YMIN)`
- `sat_mean = mean(SATAVG)`

**3. Luật quyết định:**
- **contrast:** nếu `y_range < 0.65` thì `1.08 − 0.05·t` với `t = clamp((y_range − 0.50) / 0.15)`; ngược lại `1.03`.
  Không bao giờ giảm tương phản.
- **gamma:** nếu `y_mean < 0.42` thì `1.10 − 0.08·t` với `t = clamp((y_mean − 0.30) / 0.12)` (nâng khi tối); nếu
  `y_mean > 0.60` thì `0.97`; còn lại `1.0`.
- **saturation:** mặc định `0.98`. Nếu `sat_mean < 0.18` thì `1.04`; nếu `> 0.38` thì `0.96`.
- **Kẹp biên:** contrast [0.94, 1.08], gamma [0.94, 1.10], sat [0.94, 1.06]. Hệ số nào lệch khỏi 1 không quá
  0.005 thì bỏ.

**4. Xuất** `eq=contrast=..:gamma=..:saturation=..`. Xem trước kết quả bằng `python helpers/grade.py --analyze in.mp4`.

**Thử trên footage của vedit** (2026-10-31, tôi tự viết lại luật trên, chạy với `inbox/video-01.mov`, iPhone HEVC
8-bit bt709):
| Đoạn nguồn | y_mean | y_range | sat_mean | Filter ra |
|---|---|---|---|---|
| 0.45–2.05 | 0.393 | 0.874 | 0.030 | `eq=contrast=1.030:gamma=1.038:saturation=1.040` |
| 5.00–6.40 | 0.445 | 0.872 | 0.036 | `eq=contrast=1.030:saturation=1.040` |
| 9.16–10.56 | 0.398 | 0.869 | 0.045 | `eq=contrast=1.030:gamma=1.035:saturation=1.040` |

**Nhận xét:**
- Luật nâng gamma chỉ ở các đoạn tối hơn. Đó là đúng loại "đều màu giữa các cảnh" mà một look chung không làm
  được.
- `SATAVG` của signalstats đo khoảng cách chroma. Với 8-bit, giá trị tối đa khoảng 181, chứ không phải 255. Vì vậy
  footage điện thoại bình thường cho `sat_mean` 0.03–0.06 và **luôn** rơi vào nhánh "< 0.18 → +4%". Khi port nên
  hiệu chỉnh lại ngưỡng này trên footage thật.

## Áp dụng vào vedit
**Đã có:**
- `look.preset` gồm `warm_food`, `bright_clean`, `film`, `moody`, `vivid`, `bw`, kèm `vignette` và `grain`.
- Look được áp trên **cả timeline** sau khi nối.

**Còn thiếu:**
- Không có bước sửa lỗi kỹ thuật theo dữ liệu của **từng clip** (phơi sáng, độ phẳng) trước khi tạo look.
- Không có preset trung tính kiểu `subtle` hay `neutral_punch`.
- Không có lối thoát `filter` tự do để tự chế look.
- Không có quy trình "nhìn → sửa một thứ → nhìn lại".
- Không kiểm tra tông da.

**Đề xuất (ưu tiên giảm dần):**
1. **`look.auto_correct: true`** — độ khó thấp. Mỗi clip chạy luật trên (port từ `grade.py`, ghi chú MIT
   "Copyright (c) 2026 Browser Use") khi phân tích hoặc khi render. Chèn `eq=...` vào chuỗi clip **trước** khi
   nối, rồi mới áp look sáng tạo. Nên cache kết quả trong `analysis.json`, mỗi khoảng clip một mục.
2. **Thêm preset `subtle` và `neutral_punch`** — độ khó thấp. Thêm `look.filter` (chuỗi ffmpeg thô, validate chỉ
   cho các filter màu như `eq`, `curves`, `colorbalance`, `hue`, `colortemperature`, `lut3d`) để Agent 3 tự chế
   look khi thể loại cần.
3. **Agent 3 kiểm tra màu** — độ khó thấp. So khung của 2–3 clip khác nhau trong cùng một ảnh để xem độ đồng
   đều. Video có người thì kiểm riêng tông da trước khi dùng look mạnh như `vivid` hay `warm_food`.
