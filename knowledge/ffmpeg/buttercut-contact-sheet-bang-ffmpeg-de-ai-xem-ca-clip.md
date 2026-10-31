---
title: buttercut: Contact sheet bằng ffmpeg để AI xem cả clip
category: ffmpeg
tags: [contact sheet, ffmpeg, tile, drawtext, khung hình, vision, buttercut, vfr]
updated: 2026-10-31
sources:
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/contact_sheet.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/contact_sheet_job.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/rotation_metadata.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/platform.rb
  - https://github.com/barefootford/buttercut/blob/main/skills/contact-sheet/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/roughcut_agent_prompt.md
  - https://github.com/barefootford/buttercut/blob/main/spec/buttercut/contact_sheet_spec.rb
  - https://github.com/barefootford/buttercut/blob/main/spec/buttercut/contact_sheet_benchmark_spec.rb
  - https://github.com/barefootford/buttercut/blob/main/CHANGELOG.md
---
# buttercut: Contact sheet bằng ffmpeg để AI xem cả clip

**Contact sheet** = một ảnh JPEG lưới N khung hình rải đều trong clip (hoặc một đoạn), mỗi ô in sẵn mốc thời gian.
AI đọc **một ảnh** là thấy được bối cảnh, hành động, ai trong khung và chỗ hình thay đổi, rồi mới quyết định
cần xem kỹ đoạn nào. ButterCut 0.7.0 thay "visual transcript" (LLM mô tả từng khung) bằng contact sheet thuần
ffmpeg; theo CHANGELOG: "analysis runtime drops from roughly 1× footage length to a small fraction of it".

## Thông số ButterCut (đọc từ `contact_sheet.rb`)

| Tham số | Giá trị |
|---|---|
| Clip > 10s, ngang | 16 khung, lưới 4x4 |
| Clip ≤ 10s, ngang | 8 khung, lưới 4x2 (SKILL.md ghi "4 frames 2x2" nhưng code là 8; tin code) |
| Clip dọc | lưới vuông để cả tấm cũng dọc: ≤ 10s → 3x3 (9 khung), > 10s → 4x4 |
| Bề rộng cả tấm | `GRID_WIDTH = 2500` px; padding 4, margin 4; ô rộng `(2500 − 8 − (cols−1)·4)/cols` = 620 px (4 cột) |
| Mốc lấy mẫu | điểm giữa mỗi khoảng: `t_i = start + (i + 0.5) · (end − start) / N` |
| Nhãn | `HH:MM:SS` (giây nguyên, làm tròn xuống), góc dưới trái; `fontsize = ô/17` (≈36), lề `ô/40`, hộp `black@0.65`, viền hộp `ô/60` |
| Font | `Arimo-Regular.ttf` đóng gói kèm repo (bản Windows không có fontconfig) |
| JPEG | `-fps_mode vfr -pix_fmt yuvj420p -q:v 3` |
| Clip > 10 phút | thêm 1 sheet cho mỗi 10 phút: `<clip>_00-10-00_to_00-20-00.jpg` |
| Zoom | `ruby lib/buttercut/contact_sheet.rb <video> 02:00 02:30 --library ...` khi cần chốt điểm cắt |

## Hai chiến lược trích khung

1. **seek-and-grab** (mặc định): mỗi mốc là một input riêng, tua thẳng tới mốc, lấy đúng 1 khung → chi phí tỉ lệ
   với số khung, không phụ thuộc độ dài clip.
2. **single-pass**: giải mã cả đoạn một lần, `fps=N/range` lấy mẫu đều, `drawtext ... enable='eq(n\,i)'` in mốc
   cho từng ô. Chỉ dùng khi clip "nặng" (pix_fmt chứa `422`/`444`, phần cứng Apple không giải mã) **và** đoạn
   ≤ 30s, vì 16 lần khởi tạo bộ giải mã nặng tốn hơn giải mã một lượt.

Luật chọn: clip **VFR** (`avg_frame_rate / r_frame_rate < 0.95`: quay màn hình, action cam, clip AI) luôn
seek-and-grab vì `fps` giả định frame rate cố định. Codec all-intra (prores, dnxhd, dnxhr, mjpeg, v210, rawvideo,
ffv1, huffyuv, cfhd) tua gần như miễn phí. Thử `-hwaccel videotoolbox` (mac) / `d3d11va` (Windows) trước, lỗi thì
chạy lại bằng phần mềm. Xoay: đọc `tags.rotate` (chiều kim đồng hồ) hoặc `side_data_list[].rotation` của
displaymatrix (ngược chiều, đổi dấu), dùng `-noautorotate` rồi tự `transpose=1` (90°), `transpose=1,transpose=1`
(180°), `transpose=2` (270°).

## Lệnh mẫu (cấu trúc của ButterCut, 4 khung cho dễ đọc)

```bash
ffmpeg -hide_banner -loglevel error -nostdin -y \
  -ss 1.000 -t 0.1 -i in.mov  -ss 3.000 -t 0.1 -i in.mov \
  -ss 5.000 -t 0.1 -i in.mov  -ss 7.000 -t 0.1 -i in.mov \
  -filter_complex "\
[0:v]select=eq(n\,0),scale=620:-2,setsar=1,setpts=PTS-STARTPTS,drawtext=fontfile=F.ttf:text='1.0s':x=16:y=h-th-16:fontsize=36:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=10[v0];\
[1:v]select=eq(n\,0),scale=620:-2,setsar=1,setpts=PTS-STARTPTS,drawtext=fontfile=F.ttf:text='3.0s':x=16:y=h-th-16:fontsize=36:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=10[v1];\
[2:v]select=eq(n\,0),scale=620:-2,setsar=1,setpts=PTS-STARTPTS,drawtext=fontfile=F.ttf:text='5.0s':x=16:y=h-th-16:fontsize=36:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=10[v2];\
[3:v]select=eq(n\,0),scale=620:-2,setsar=1,setpts=PTS-STARTPTS,drawtext=fontfile=F.ttf:text='7.0s':x=16:y=h-th-16:fontsize=36:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=10[v3];\
[v0][v1][v2][v3]concat=n=4:v=1[c];[c]tile=2x2:padding=4:margin=4:color=black" \
  -frames:v 1 -update 1 -fps_mode vfr -pix_fmt yuvj420p -q:v 3 sheet.jpg
```

Biến thể single-pass (clip nặng, đoạn ngắn):
`-ss START -to END -i in.mov -an -sn -vf "fps=N/RANGE,scale=620:-2:flags=lanczos,setsar=1,drawtext=...:enable='eq(n\,0)',...,tile=4x4:padding=4:margin=4:color=black" -frames:v 1 ...`

## Script đã chạy thử cho vedit (ffmpeg 6.1.1, Linux, không hwaccel)

Khác ButterCut ở 2 điểm có chủ đích: **giữ accurate seek** (bỏ `-noaccurate_seek`) và **nhãn giây thập phân**
(`12.4s`) vì video ngắn cần độ chính xác ~0.1s; để ffmpeg tự xoay theo metadata nên không cần `transpose`.

```bash
#!/usr/bin/env bash
# contact_sheet.sh <video> <out.jpg> [start] [end] [cols] [frames] [grid_width]
set -euo pipefail
VIDEO="$1"; OUT="$2"; START="${3:-0}"; END="${4:-}"
COLS="${5:-4}"; N="${6:-16}"; GRID_W="${7:-2500}"
FONT="assets/fonts/BeVietnamPro-SemiBold.ttf"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO"); END="${END:-$DUR}"
ROWS=$(( (N + COLS - 1) / COLS )); TW=$(( (GRID_W - 8 - (COLS - 1) * 4) / COLS ))
FS=$(( TW / 17 )); PAD=$(( TW / 40 )); BW=$(( TW / 60 > 1 ? TW / 60 : 1 ))
inputs=(); chains=(); labels=""
for ((i=0; i<N; i++)); do
  t=$(awk -v s="$START" -v e="$END" -v i="$i" -v n="$N" 'BEGIN{printf "%.3f", s+(i+0.5)*(e-s)/n}')
  lab=$(awk -v t="$t" 'BEGIN{printf "%.1fs", t}')
  inputs+=(-ss "$t" -t 0.1 -i "$VIDEO")
  chains+=("[$i:v]select=eq(n\,0),scale=${TW}:-2,setsar=1,setpts=PTS-STARTPTS,drawtext=fontfile=${FONT}:text='${lab}':x=${PAD}:y=h-th-${PAD}:fontsize=${FS}:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=${BW}[v$i]")
  labels+="[v$i]"
done
graph="$(IFS=';'; echo "${chains[*]}");${labels}concat=n=${N}:v=1[c];[c]tile=${COLS}x${ROWS}:padding=4:margin=4:color=black"
ffmpeg -hide_banner -loglevel error -nostdin -y "${inputs[@]}" -filter_complex "$graph" \
  -frames:v 1 -update 1 -fps_mode vfr -pix_fmt yuvj420p -q:v 3 "$OUT"
```

Kết quả với `inbox/video-01.mov` (HEVC 720x1280, 25.6s): toàn clip 16 khung 4x4 → 2500x4428 px, ~986 KB, 4.4s;
zoom 12–18s 9 khung 3x3 rộng 1500 → 1498x2650 px, 1.1s. Nhìn tấm toàn clip thấy ngay mạch: hũ rỗng → nước →
gia vị → khuấy → ớt → tỏi gừng → **bồn rửa (≈12s, cảnh lạc)** → thả cà → đóng nắp → giơ hũ → dọn chai.

## Lưu ý thực tế

- `-noaccurate_seek` (ButterCut dùng để nhanh) trả về **keyframe gần nhất phía trước**, không đúng mốc: file iPhone
  HEVC ở trên có keyframe mỗi 1.0s (đo bằng `ffprobe -skip_frame nokey -show_entries frame=pts_time`) nên khung
  có thể lệch tới ~1s so với nhãn. ButterCut chấp nhận vì chỉ cần chính xác ~1s; vedit thì không nên.
- Ảnh lớn bị thu nhỏ khi model đọc: tấm 2500x4428 được hiển thị 1129x2000 trong phiên này, mỗi ô dọc chỉ còn
  ~280 px. Với clip dọc nên dùng 3x3 hoặc nhiều tấm nhỏ, và dùng sheet zoom cho chi tiết.
- Nhãn phải là mốc **thật** của khung (giây nguồn) để agent dùng thẳng làm điểm cắt.
- Cần ffmpeg có `drawtext` (libfreetype); bản Homebrew mặc định có thể thiếu, ButterCut cài bản ghim có checksum.

## Áp dụng vào vedit

**Đã có**: `vedit analyze` trích tối đa 16 khung rời (giữa mỗi cảnh, rộng 512px) vào `analysis/frames/`;
`vedit frame <slug> <giây> --grid` cho lưới toạ độ 0..1 để đặt đồ hoạ.

**Còn thiếu**: ảnh tổng quan một tấm có mốc giờ; cách "zoom" một khoảng thời gian bằng một ảnh; agent phải mở
nhiều ảnh rời và không thấy được thứ tự liền mạch.

**Đề xuất theo ưu tiên**:
1. `vedit analyze` sinh thêm `analysis/contact_sheet.jpg` (toàn clip; clip dọc ≤ 30s: 3x3 hoặc 4x3; clip dài:
   4x4 + tấm theo từng cảnh) với nhãn giây 1 chữ số thập phân, accurate seek. Dễ: port script trên sang Python
   trong `media.py` (`extract_contact_sheet(path, start, end, cols, n)`).
2. Lệnh `vedit sheet <slug> <start> <end> [--cols 3 --n 9]` để Agent 2/3 zoom vào đoạn cần chốt điểm cắt hoặc tìm
   khoảnh khắc đẹp nhất cho hook (ví dụ 9 khung trong 3s = mỗi khung cách 0.33s). Dễ.
3. Cập nhật prompt Agent 2: đọc contact sheet trước, frames rời sau; ghi mốc thấy được vào `note` của clip. Dễ.
4. Tuỳ chọn `--grid` cho sheet để vừa xem diễn biến vừa đọc toạ độ. Vừa (lưới vẽ trên từng ô).
