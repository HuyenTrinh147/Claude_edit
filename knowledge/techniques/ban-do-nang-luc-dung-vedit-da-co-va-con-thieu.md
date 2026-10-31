---
title: Bản đồ năng lực dựng: vedit đã có và còn thiếu
category: techniques
tags: [vedit, năng lực, khoảng trống, roadmap, ưu tiên, editplan, ffmpeg, libass, đề xuất tính năng]
updated: 2026-10-31
sources:
  - https://github.com/scriptituk/xfade-easing/blob/main/README.md
  - https://github.com/francozanardi/pycaps/blob/main/docs/EFFECTS_AND_ANIMATIONS.md
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/short-form-video/SKILL.md
  - https://github.com/mifi/editly/blob/master/README.md
  - https://github.com/FFmpeg/FFmpeg/blob/release/6.1/doc/filters.texi
  - https://github.com/libass/libass/blob/master/Changelog
  - https://github.com/BrokenSource/DepthFlow/blob/main/readme.md
  - https://github.com/PeterL1n/RobustVideoMatting/blob/master/README.md
  - https://github.com/danielgatis/rembg/blob/main/README.md
  - https://ffmpeg.org/pipermail/ffmpeg-trac/2025-March/072904.html
  - https://tubefilter.com/2024/03/04/mrbeast-editing-style-number-of-cuts-per-video/
  - https://blog.youtube/culture-and-trends/whats-all-the-noise-about-silent-vlogs/
---
# Bản đồ năng lực dựng: vedit đã có và còn thiếu

Tổng hợp từ các ghi chú kỹ thuật ngày 2026-10-31, đối chiếu `vedit schema plan`, `vedit/render.py`, `vedit/ass.py` và
thử nghiệm ffmpeg 6.1.1 trên `inbox/video-01.mov`. Ký hiệu độ khó: **S** = vài chục dòng, không đổi kiến trúc;
**M** = thêm trường schema + nhánh filter graph + test; **L** = cần model ML/GPU hoặc đổi kiến trúc render.

## 1. Vì sao bản cà pháo bị chê "thiếu sáng tạo" (phân tích của Agent 1)
1. **Lệch ngôn ngữ**: huy hiệu bước, callout pill, progress bar, chuỗi `pop` là ngôn ngữ video explainer; nội dung là
   ASMR/silent vlog bếp (chính kịch bản đã ghi "Reali-TEA: chữ ít, không sticker").
2. **Nhịp đều**: 9 clip 1,4–2,8 s, toàn cắt cứng — không có đoạn dồn, không có cảnh thở, không có khoảnh khắc slow-mo.
3. **Thiếu thao tác thời gian**: speed ramp, dừng hình, time-lapse — bộ chiêu chính của video đồ ăn — vedit chưa có.
4. **Âm thanh "công thức"**: `pop` 0.15 lặp 6 lần; không room tone, không làm rõ tiếng thật, cú cắt có bước nhảy biên độ
   (4/8 điểm, gấp 1,9–3,8 lần mức lân cận).
5. **Đổi góc máy (12,9 s) bằng cắt cứng**, không có chuyển cảnh có chủ đích; màu toàn cục trong khi độ sáng từng clip
   chênh Y 97–118.

## 2. Ma trận năng lực
| Nhóm | Kỹ thuật | Trạng thái | Cách làm tạm ngay hôm nay |
|---|---|---|---|
| Cắt | Jump cut, smash cut, cut on action | Có (thủ công) | — |
| Cắt | Cắt theo onset/beat | **Chưa** (Agent 3 đo tay) | đo onset bằng ffmpeg/numpy như ghi chú nấu ăn mục 6 |
| Cắt | J/L-cut | **Chưa** | — |
| Cắt | Micro-fade âm thanh ở biên clip | **Chưa** | — |
| Thời gian | Tốc độ hằng số 0.25–4x | Có | ramp bậc thang: tách 1 cảnh thành 3–4 clip 1.0/0.6/0.4/1.0 |
| Thời gian | Speed ramp mượt, slow-mo nội suy | **Chưa** | như trên |
| Thời gian | Dừng hình | **Chưa** | trích frame PNG bằng ffmpeg → clip ảnh `duration` 0.6–1 s + `flash` + SFX |
| Thời gian | Time-lapse >4x, tua ngược | **Chưa** (speed tối đa 4) | — |
| Máy | Punch, shake | Có (tâm khung, không blur) | — |
| Máy | Ken Burns | Một phần (tuyến tính, tâm giữa, zoompan có thể rung) | `focus_x/y` chỉ dời khung cắt, không dời tâm zoom |
| Máy | Keyframe zoom/pan có easing | **Chưa** | — |
| Chuyển cảnh | xfade | Một phần: 22/58 kiểu, tuyến tính | `smoothleft` 0,2 s + whoosh + punch ≈ whip |
| Chuyển cảnh | Whip, zoom-through, light leak, glitch | **Chưa** | `fadewhite` 0,15 s ≈ chớp sáng |
| Lớp hình | Split screen, PiP, B-roll đè | **Chưa** (1 lớp video) | — |
| Chữ | 10 kiểu vào, pill/banner, xoay | Có | — |
| Chữ | Kiểu ra, easing trượt, lật 3D, stamp | **Chưa** | — |
| Phụ đề | clean/boxed/bold_pop/karaoke | Một phần | — |
| Phụ đề | Chia cụm 1–3 từ, hộp nền từ, nhấn từ khoá, emoji màu | **Chưa** | emoji: dựng PNG bằng Pillow → `images` (tĩnh) |
| Đồ hoạ | callout, badge, progress, highlight, sparkles, flash | Có | — |
| Đồ hoạ | Mũi tên, gạch chân/vòng tròn vẽ dần, bộ đếm, lower third, doodle | **Chưa** | lower third/timestamp: `texts` + `shape` |
| Đồ hoạ | Sticker PNG có animation | Một phần (tĩnh) | — |
| Màu | Look toàn cục + vignette + grain | Có | — |
| Màu | Chỉnh từng clip, tự cân, LUT + cường độ, vibrance/HSL | **Chưa** | — |
| Âm thanh | Volume/mute clip, duck nhạc, loudnorm 1 lượt, 7 SFX tổng hợp, SFX từ file | Có | room tone: trích đoạn yên từ nguồn → `audio` role `music` + `loop`, volume thấp (thử duck bật/tắt) |
| Âm thanh | Pan stereo, EQ/giảm ồn từng clip, chế độ loudness ASMR, chỉnh độ sâu duck | **Chưa** | — |
| Phân tích | cảnh, khoảng lặng, transcript, khung hình | Có | — |
| Phân tích | onset/beat, cú cắt ẩn/flash frame, thống kê màu từng clip, kiểm tra loop, phân tích video tham chiếu | **Chưa** | — |
| QA | schema + đối chiếu file | Có | — |
| QA | ASL, cắt cứng liên tiếp, transition lặp, khoảng "chết", tốc độ đọc chữ, punch lệch onset | **Chưa** | Agent 3 tự kiểm bằng `vedit frame` |

## 3. Đề xuất tính năng theo ưu tiên (vấn đề → giải pháp → độ khó)

### P0 — làm trước (mở khoá sáng tạo nhiều nhất / rẻ nhất)
1. **Micro-fade ở mọi biên clip** — cú cắt có tiếng "tách" → thêm `afade=t=in:d=0.02,afade=t=out:st=dur-0.02:d=0.02`
   vào chuỗi âm thanh mỗi clip trong `render.py` (video-use dùng 30 ms). **S**.
2. **Onset (+ beat) trong `vedit analyze`** — Agent 3 phải đo tiếng bằng tay → spectral flux trên PCM 16 kHz (numpy:
   cửa sổ 512, bước 10 ms, ngưỡng median+4·MAD, lọc dải 1–6 kHz cho tiếng nhỏ) xuất `onsets: [{t, strength}]`; beat
   nhạc bằng librosa/aubio (tuỳ chọn). Cần thêm phụ thuộc numpy. Nguyên mẫu đã khớp mốc đo tay ±40 ms. **M**.
3. **Speed ramp + dừng hình** — thiếu bộ chiêu cốt lõi của đồ ăn/velocity → `Clip.speed_ramp` (preset hero/bullet/
   montage hoặc điểm `{at, speed}`) bằng một biểu thức `setpts` tích phân + `framerate` (tuỳ chọn `minterpolate`,
   chậm ~20x); `Clip.freeze {at, duration, flash, desaturate}` bằng `loop` + `drawbox` + `hue`. Đã thử cả hai. **M**.
4. **Chuyển cảnh v2** — chỉ có xfade tuyến tính → mở thêm 36 kiểu xfade; thêm `whip_*` (slide + `dblur` bậc),
   `zoom_through` (zoompan easing + `split/tmix/overlay`), `light_leak` (`gradients`+`gblur`+`blend=screen`),
   `glitch` (`rgbashift`+`noise`+`geq`), tham số `easing` (biểu thức custom, cần `-filter_complex_threads 1`).
   Đã thử; **tránh `tmix` có `enable=`** (ra hình xanh lá ở 6.1). **M**.
5. **Preset phụ đề viral** — karaoke hiện chỉ đổi màu + 110% → `captions.chunk` (words/chars), preset `hype`/
   `explosive`/`word_box`/`hormozi` (pop 0.8→1.0 trong 0,12 s vượt 5%, hộp nền từ đang đọc, IN HOA), `emphasis` từ khoá
   (màu/cỡ/SFX). Toàn bộ libass. **S–M**.

### P1 — nâng chất lượng nghề
6. **Motion v2** — punch/Ken Burns chỉ ở tâm, tuyến tính → `motion` có `x,y` tâm, `keyframes [{t, scale, x, y, ease}]`,
   motion blur tuỳ chọn, `rotate` shake; phóng 2x trước zoompan cho zoom chậm (lỗi rung #4298 vẫn mở 3/2025). **M**.
7. **Màu v2** — look toàn cục làm lộ chênh sáng giữa clip → `Clip.color {exposure, temperature, saturation}` +
   `auto_match` (đo `signalstats`, kéo về clip chuẩn), `look.lut` + `look.intensity` (`lut3d` + `blend` opacity —
   đã đo đúng 70%), preset `food_natural` (vibrance + selectivecolor, giữ trắng trung tính). **M**.
8. **Âm thanh v2** — `Clip.audio_lead/tail` (J/L-cut), `role: "ambience"`, `AudioTrack.pan`, `Clip.audio_fx`
   (`asmr_clarity` = highpass 80 + EQ 4 kHz +3 dB + afftdn nhẹ), `export.loudness_mode` (`social`: loudnorm 2 lượt;
   `asmr`: gain + alimiter ≈ −22 LUFS giữ LRA — đã đo), `duck_amount_db`; SFX tổng hợp mới `riser/impact/shutter/
   whoosh_lr` (công thức đã thử) + thư mục `assets/sfx` CC0. **S–M**.
9. **Đồ hoạ v2** — thiếu ngôn ngữ "vẽ tay/vlog" → kiểu ra (pop_out/slide_out/wipe_out), trượt có easing (nhiều event
   `\move` nối tiếp), `arrow`, `underline`, `circle_draw` (16–24 cung hiện dần), `counter`, `lower_third`, `timestamp`,
   `letterbox`, doodle sticker, chuyển động "idle" cho vật ở lâu. **S–M** mỗi món.
10. **Emoji màu & sticker động** — libass vẽ emoji đơn sắc (đã thử) → Pillow `NotoColorEmoji` cỡ 109 +
    `embedded_color=True` → PNG; `images.animation` (pop/bounce/slide/wiggle) bằng `scale`/`overlay` biểu thức. **M**.

### P2 — mở rộng
11. **Nhiều lớp video** (split screen, PiP, B-roll đè lên tiếng clip chính) — `Clip.layout` hoặc mảng `overlays`
    video; `vstack/xstack/overlay`. **M–L**.
12. **QA sáng tạo trong `vedit validate`** — cảnh báo: >5 cắt cứng liên tiếp (video năng lượng cao), 2 transition
    liền nhau cùng kiểu, không có sự kiện thị giác > N s (theo hồ sơ nhịp), chữ đọc >4 từ/s, punch/SFX lệch onset
    >2 frame, chữ ngoài vùng an toàn. **S–M**.
13. **Phân tích nâng cao** — cú cắt ẩn/flash frame (`scdet` từng frame — đã thử: 3 cú cắt ẩn 6,40 / 9,17 / 18,17 s mà
    detect_scenes bỏ sót đều nằm trong top-14 điểm `scdet`, lẫn với đỉnh do chuyển động → lọc thêm "đỉnh đơn frame"), thống kê màu từng cảnh, gợi ý cặp match cut/loop (SSIM), phân tích video tham chiếu (ASL, cường độ chuyển
    động, loudness, màu) để Agent 2 "bắt chước vibe". **M**.
14. **Hiệu ứng cần tách chủ thể** — chữ sau chủ thể, reveal theo vật, callout bám vật: rembg (ảnh, CPU) /
    RobustVideoMatting (video người, nhanh trên GPU) / tracker OpenCV. **L**.
15. **Parallax 3D** — DepthFlow (depth model + shader, cần GPU) hoặc `displace` với depth map. Hũ thuỷ tinh/vật phản
    chiếu là ca khó. **L**.
16. **Time-lapse >4x + tua ngược** — nới giới hạn `speed`, trộn frame bằng `tmix` (không dùng `enable=`), `reverse`/
    `areverse` cho clip ngắn. **S**.

## 4. Đổi cách làm của Agent 2/3 (không cần code)
- **Chọn phong cách trước** (silent vlog / Tasty / Bayashi / velocity / Hormozi), ghi vào `notes`, rồi chỉ dùng ngôn ngữ
  hình–chữ–tiếng của phong cách đó. Mỗi video chọn 3–5 "chiêu chữ ký", không rải mọi hiệu ứng.
- Đặt độ dài clip có biến thiên; ít nhất một đoạn dồn và một cảnh thở; cú cắt đặt trên onset (−2 frame).
- Mốc đổi phần/đổi góc máy dùng chuyển cảnh có chủ đích (khác kiểu với lần trước); còn lại cắt cứng.
- SFX: ít, mỗi cái có lý do; ASMR ưu tiên làm rõ tiếng thật + room tone.
- Dùng ngay các cách làm tạm ở bảng mục 2 (ramp bậc thang, dừng hình bằng clip ảnh, room tone qua track music).

## Áp dụng vào vedit
Ghi chú này là đầu vào cho lộ trình mã nguồn. Thứ tự đề xuất triển khai: P0-1 → P0-2 → P0-3 → P0-4 → P0-5, mỗi bước
kèm test render (pytest dùng ffmpeg thật, video tổng hợp `testsrc2`) và cập nhật `bo-cong-cu-do-hoa-hieu-ung-cua-vedit`.
Chi tiết kỹ thuật từng mục nằm ở: `nhip-cat-va-ky-thuat-giu-chan-nguoi-xem`, `ky-thuat-cat-jump-cut-j-l-cut-match-cut-
cat-theo-beat`, `speed-ramp-freeze-frame-keyframe-zoom-va-split-screen`, `chuyen-canh-sang-tao-whip-pan-zoom-light-leak-
glitch`, `phu-de-viral-tung-tu-highlight-emoji`, `kinetic-typography-callout-lower-third-va-sticker`, `mau-sac-grading-
theo-the-loai-va-dong-bo-giua-cac-canh`, `dung-video-nau-an-asmr-va-satisfying`, `audio/am-thanh-cho-video-ngan`,
`audio/sound-design-nhieu-lop-ambience-foley-whoosh-riser-impact`.
- Xem thêm: `tools/video-use-tong-quan-kien-truc-va-so-sanh-voi-vedit`, `tools/claude-video-editor-tong-quan-repo-va-so-sanh-voi-vedit`, `scripting/video-use-pha-khuon-sang-tao-bang-scamper-va-dao-gia-dinh`.

_Ghi chú nguồn: đối chiếu trực tiếp mã nguồn vedit và tài liệu GitHub; số đo, công thức do Agent 1 chạy thử ngày
2026-10-31; phần chẩn đoán mục 1 là nhận định, không phải dữ liệu người xem._
