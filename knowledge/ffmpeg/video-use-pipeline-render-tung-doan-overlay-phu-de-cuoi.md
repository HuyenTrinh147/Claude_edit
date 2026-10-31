---
title: video-use: Pipeline render từng đoạn, overlay, phụ đề cuối
category: ffmpeg
tags: [video-use, ffmpeg, render, concat, overlay, setpts, hdr, tonemap, zscale, fps, xoay, loudnorm]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/helpers/render.py
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/tests/test_render_fps.py
  - https://github.com/browser-use/video-use/blob/main/tests/test_render_orientation.py
---
# video-use: Pipeline render từng đoạn, overlay, phụ đề cuối

`helpers/render.py` (801 dòng) render một EDL qua 4 giai đoạn. Ghi chú này ghi lại lệnh ffmpeg của từng giai
đoạn và các xử lý cho trường hợp khó (HDR, xoay, fps).

## Giai đoạn 1 — trích từng đoạn (grade + fade đã nướng sẵn)
```bash
ffmpeg -y -ss {start:.3f} -i SRC -t {dur:.3f} \
  -vf "[TONEMAP_CHAIN,]scale=1920:-2[,GRADE]" \
  -af "afade=t=in:st=0:d=0.03,afade=t=out:st={dur-0.03:.3f}:d=0.03" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -r {RATE} \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart clips_graded/seg_00_C0103.mp4
```
- **Scale:** nguồn dọc dùng `scale=-2:1920`, nguồn ngang dùng `scale=1920:-2`. Không crop, giữ hướng gốc.
- **Ba mức chất lượng:**

  | Chế độ | Preset | CRF | Cạnh dài | Thư mục |
  |---|---|---|---|---|
  | final (mặc định) | fast | 20 | 1920 | `clips_graded/` |
  | `--preview` | medium | 22 | 1920 ("evaluable for QC") | `clips_preview/` |
  | `--draft` | ultrafast | 28 | 1280 (chỉ để kiểm điểm cắt) | `clips_draft/` |

- **Một fps cho mọi đoạn:** bắt buộc, vì concat `-c copy` đòi các đoạn cùng frame rate. Lấy `--fps` nếu có. Nếu
  không, lấy `avg_frame_rate` của nguồn đầu tiên (tốt hơn cho VFR), dự phòng `r_frame_rate`, cuối cùng là 24.
  `parse_fps` chuẩn hoá về phân số chính xác (`29.97` → `2997/100`, `30000/1001` giữ nguyên), giới hạn tử/mẫu
  trong int32 vì AVRational.
- **Xoay:** chỉ tin side data `rotation` (display matrix), vì đó là thứ ffmpeg dùng để tự xoay. Tag `rotate`
  thuần bị bỏ qua. Góc ±90/270 thì hoán đổi rộng và cao trước khi xét video dọc hay ngang (có test cho cả 2
  chiều).

## HDR → SDR (iPhone mặc định quay HLG)
Lý do theo code: nguồn HDR mà chỉ hạ bit-depth (10 → 8 bit) thì file vẫn mang metadata HLG/PQ. Trình phát và
bước re-encode của mạng xã hội sẽ hiển thị **chói, quá bão hoà**. QuickTime trên macOS có thể che mất lỗi này.
```bash
# phát hiện: color_transfer ∈ {smpte2084 (PQ/HDR10), arib-std-b67 (HLG)}
ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of default=nw=1:nk=1 in.mov
# chuỗi tone-map, đặt ĐẦU chuỗi -vf
zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p
```
Đã thử ngày 2026-10-31 trên ffmpeg 6.1 (có `zscale`) với clip HLG 10-bit tổng hợp. Kết quả ra `yuv420p`,
`color_transfer=bt709`.

## Giai đoạn 2 — nối không re-encode
```bash
# _concat.txt:  file '/abs/clips_graded/seg_00_C0103.mp4'  (mỗi đoạn 1 dòng)
ffmpeg -y -f concat -safe 0 -i _concat.txt -c copy -movflags +faststart base.mp4
```

## Giai đoạn 3 — overlay (dời PTS) rồi phụ đề sau cùng
```bash
ffmpeg -y -i base.mp4 -i slot_1/render.mp4 -filter_complex \
"[1:v]setpts=PTS-STARTPTS+0.0/TB[a1];\
[0:v][a1]overlay=enable='between(t,0.000,5.000)'[v1];\
[v1]subtitles='/abs/master.srt':force_style='FontName=Helvetica,FontSize=18,Bold=1,...,MarginV=90'[outv]" \
-map "[outv]" -map 0:a -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -c:a copy -movflags +faststart out.mp4
```
- **Rule 4:** `setpts=PTS-STARTPTS+T/TB` đưa khung 0 của animation về đúng `T`. Thiếu bước này thì cửa sổ
  overlay hiện **giữa chừng** animation.
- **Rule 1:** `subtitles` luôn là filter cuối. Đặt sớm hơn thì overlay che phụ đề và không báo lỗi gì.
- **Đường dẫn phụ đề** trong filter phải escape `:` → `\:` và `'` → `\'`. Thiếu file SRT thì dừng hẳn, không lặng
  lẽ xuất video không có phụ đề.
- Âm thanh lấy từ `0:a` (`-c:a copy`): overlay **không có tiếng**.
- **Alpha:** `render.py` không ép decoder `-c:v libvpx-vp9` cho input WebM. Đã thử ngày 2026-10-31 trên ffmpeg
  6.1 với WebM VP9 màu `red@0.3` phủ lên nền trắng:
  - decoder mặc định đọc ra `yuv420p` và **bỏ alpha** → pixel ra `253,0,0`, đỏ đặc;
  - đặt `-c:v libvpx-vp9` trước `-i` thì đọc ra `yuva420p` → pixel ra `253,178,178`, đúng màu pha trộn.

  Vậy overlay WebM trong suốt qua `render.py` sẽ bị phủ kín.

## Giai đoạn 4 — loudnorm 2 lượt (video copy)
```bash
# lượt 1: đo (JSON in ra stderr)
ffmpeg -i pre.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -vn -f null -
# lượt 2: áp số đo
ffmpeg -i pre.mp4 -c:v copy -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=..:measured_TP=..:measured_LRA=..:measured_thresh=..:offset=..:linear=true" \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart final.mp4
```
- `--draft` chỉ chạy 1 lượt. Lỗi khi đo thì lùi về 1 lượt.
- Không có overlay hay phụ đề thì bước 3 chỉ `-c copy`.

## Nhận xét khi so với vedit
- Hard Rule 2 ("per-segment extract → lossless concat, not single-pass filtergraph... Otherwise you
  double-encode") đúng **trong kiến trúc của video-use**. Nhưng ngay pipeline này cũng encode video **2 lần** khi
  có overlay hoặc phụ đề (CRF 20, rồi CRF 18).
- Lợi ích thật của việc tách đoạn: cache từng đoạn, grade riêng từng đoạn, và cắt lại chỉ tốn concat.
- vedit dựng mọi thứ trong **một** graph và encode **một** lần. Về chất lượng thì tốt hơn, **không nên** chép Rule
  2 một cách máy móc.

## Áp dụng vào vedit
**Đã có:**
- Một graph, timeline theo số khung nguyên.
- Thứ tự lớp: look → motion → ảnh overlay → ASS (chữ, phụ đề, đồ hoạ). Vậy là đúng Rule 1.
- `probe` đã hoán đổi kích thước theo side data rotation hoặc tag `rotate`.
- Chế độ preview (nửa độ phân giải, `veryfast`, CRF 30).

**Còn thiếu:**
- Fade âm ở chỗ cắt thẳng.
- Tone-map HDR.
- Overlay một **clip video** (animation dựng sẵn, PiP) dời PTS.
- Loudnorm 2 lượt.

**Đề xuất (ưu tiên giảm dần):**
1. **Fade 30 ms ở cắt thẳng** — độ khó thấp. Trong `build_command`, nhánh `has_audio`, thêm vào **cuối**
   `achain` (sau `atrim` và `asetpts`):
   ```python
   FADE = 0.03
   dur = n / fps
   nxt = plan.clips[i + 1] if i + 1 < len(plan.clips) else None
   if clip.transition is None:
       achain.append(f"afade=t=in:st=0:d={FADE}")
   if nxt is None or nxt.transition is None:   # acrossfade already smooths transitions
       achain.append(f"afade=t=out:st={max(dur - FADE, 0):.4f}:d={FADE}")
   ```
2. **Tone-map HDR** — độ khó thấp. Thêm `color_transfer` vào `MediaInfo`. Khi giá trị thuộc
   `{smpte2084, arib-std-b67}` thì nối `TONEMAP_CHAIN` ngay sau `setpts..,fps=` trong chuỗi `pre` của clip, trước
   scale/crop. Thêm một test với clip HLG tổng hợp (lệnh tạo: `testsrc2` → `format=yuv420p10le`,
   `-color_trc arib-std-b67`, libx265).
3. **Overlay clip video** — độ khó trung bình. Thêm mục `overlays` vào schema: `path, start, duration, x, y,
   width, opacity`. Graph dùng `setpts=PTS-STARTPTS+T/TB` + `overlay=enable='between(t,T,T+D)'`. Với WebM có
   alpha thì thêm `-c:v libvpx-vp9` trước `-i`. Mục này mở đường cho PiP, split-screen và animation dựng bằng
   code.
4. **Loudnorm 2 lượt** — độ khó trung bình. Render một lần với âm thanh chưa chuẩn hoá, đo, rồi chạy lượt 2
   trên audio với `-c:v copy`. Chi tiết và số đo thực tế ở
   `audio/video-use-am-thanh-fade-30ms-sfx-dung-khung-loudnorm-2-luot`.
5. **Chế độ `--draft`** — độ khó thấp. 720p, `ultrafast`, CRF 28, chỉ để kiểm điểm cắt.
