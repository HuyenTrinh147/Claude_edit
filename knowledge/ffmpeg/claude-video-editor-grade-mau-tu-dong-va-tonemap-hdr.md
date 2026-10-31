---
title: claude-video-editor: Grade màu tự động và tonemap HDR
category: ffmpeg
tags: [claude-video-editor, grade, màu, signalstats, auto grade, hdr, hlg, tonemap, zscale, iphone, asc cdl]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/helpers/grade.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/helpers/render.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/short-form-video/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/generate-footage/SKILL.md
---
# claude-video-editor: Grade màu tự động và tonemap HDR

## 1. Tư duy grade (video-use)

"Your job is to **reason about the image**, not apply a preset. Look at a frame, decide what's wrong, adjust one
thing, look again." Mô hình **ASC CDL** từng kênh: `out = (in * slope + offset) ** power`, rồi saturation tổng —
`slope` ≈ vùng sáng, `offset` ≈ vùng tối, `power` ≈ trung tính. Luật: grade **từng đoạn lúc trích** (không grade sau
concat để khỏi mã hoá 2 lần); "Never go aggressive without testing skin tones." Mặc định khi người dùng chưa yêu cầu:
không grade.

## 2. Preset (chuỗi filter nguyên văn trong `grade.py`)

```text
subtle         eq=contrast=1.03:saturation=0.98
neutral_punch  eq=contrast=1.06:brightness=0.0:saturation=1.0,curves=master='0/0 0.25/0.23 0.75/0.77 1/1'
warm_cinematic eq=contrast=1.12:brightness=-0.02:saturation=0.88,
               colorbalance=rs=0.02:gs=0.0:bs=-0.03:rm=0.04:gm=0.01:bm=-0.02:rh=0.08:gh=0.02:bh=-0.05,
               curves=master='0/0 0.25/0.22 0.75/0.78 1/1'
```

`warm_cinematic` (teal/cam nhẹ, giảm bão hoà, đường cong kiểu phim) được đánh dấu **opt-in** — "too aggressive for
standard launch content". `neutral_punch` = chỉ thêm tương phản + S-curve nhẹ, không lệch màu.

## 3. Auto-grade theo từng clip (giới hạn ±8%)

Mục tiêu "make it look clean without looking graded" — không LUT sáng tạo, không teal/orange.

1. Lấy mẫu ~10 khung trong đoạn: `fps=<n/dur>,signalstats,metadata=print:file=…` (fps kẹp 0.5–10).
2. Đọc `YAVG`, `YMIN`, `YMAX`, `SATAVG`; **chia cho (2^YBITDEPTH − 1)** để đúng cả nguồn 10-bit.
3. Quy tắc (giá trị 0..1):
   - Tương phản: dải `YMAX−YMIN` < 0.65 → contrast nội suy 1.08 (dải 0.50) … 1.03 (dải 0.65); còn lại 1.03.
   - Gamma: `YAVG` < 0.42 → gamma 1.10 (0.30) … 1.02 (0.42); `YAVG` > 0.60 → 0.97.
   - Bão hoà: `SATAVG` < 0.18 → 1.04; > 0.38 → 0.96; còn lại 0.98.
   - Kẹp cứng: contrast 0.94–1.08, gamma 0.94–1.10, saturation 0.94–1.06; bỏ tham số lệch < 0.005.
4. Kết quả dạng `eq=contrast=1.050:gamma=1.040:saturation=0.980`, chèn vào chuỗi `-vf` của đoạn đó.

## 4. HDR (iPhone HLG / PQ) → SDR

iPhone mặc định quay HLG HDR (Rec.2020). Nếu chỉ hạ 10-bit → 8-bit mà không tonemap, file vẫn mang metadata HLG/PQ;
trình phát/mạng xã hội hiểu theo HDR → **"oversaturated / blown out"** (QuickTime trên máy có thể che lỗi này).
Phát hiện: `ffprobe -show_entries stream=color_transfer` ∈ {`smpte2084` (PQ), `arib-std-b67` (HLG)}. Chuỗi xử lý đặt
**trước** scale/grade:

```bash
zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p
```

Đã chạy thử 2026-10-31 với ffmpeg 6.1.1 của môi trường vedit (có `--enable-libzimg`): nguồn HLG tổng hợp
(`yuv420p10le`, `arib-std-b67`) → đầu ra `yuv420p`, `color_transfer=bt709`.

## 5. Grade cho mặt người & ảnh tĩnh

- Short-form (talking head): CSS `contrast(1.08) saturate(1.08) brightness(0.97)` + Ken Burns 1.00→1.025 + vignette
  hai bên. Xấp xỉ ffmpeg (nhận định): `eq=contrast=1.08:saturation=1.08,colorchannelmixer=rr=0.97:gg=0.97:bb=0.97`.
- Ảnh tĩnh từ nhiều nguồn (generate-footage): **vignette tối thống nhất** làm các ảnh khác nguồn trông cùng một bộ và
  giúp phụ đề dễ đọc; khoá **một** style mô tả cho mọi ảnh.

## Áp dụng vào vedit

**Đã có**: `look.preset` (`warm_food`, `bright_clean`, `film`, `moody`, `vivid`, `bw`) + `vignette` + `grain`, áp
**một lần cho cả timeline** sau khi nối clip (một filter graph nên không mã hoá lại).

**Còn thiếu**: không nhận diện/tonemap HDR (rủi ro lớn với video iPhone người dùng gửi); không hiệu chỉnh riêng từng
clip khi các cảnh lệch sáng/màu; không có preset "sạch, không lộ grade"; không đặt `look` riêng cho từng clip.

**Đề xuất (ưu tiên)**:
1. **Tonemap HDR tự động** trong chuỗi per-clip của `render.py`: `probe()` đọc thêm `color_transfer`; nếu PQ/HLG thì
   chèn chuỗi mục 4 ngay sau `setpts/fps`. `vedit analyze` ghi cờ `hdr: true` để agent biết. Dễ.
2. **`look.auto: true`** (hoặc `Clip.auto_grade`): đo signalstats trên đoạn [start,end] của từng clip lúc render và
   chèn `eq` giới hạn ±8% như mục 3 — cân màu giữa các cảnh trước khi áp preset sáng tạo. Vừa.
3. Thêm preset `clean` (= `eq=contrast=1.03:saturation=0.98`) và `neutral_punch` (chuỗi nguyên văn mục 2) làm lựa
   chọn an toàn cho talking head; preset `talking_head` theo mục 5. Dễ.
4. Cho phép `Clip.look` ghi đè preset từng clip (cảnh b-roll lạnh, cảnh thành phẩm ấm). Vừa.
5. Prompt Agent 3: soi khung trước/sau grade ở cảnh có da người; chỉnh một thứ mỗi lần. Dễ.
