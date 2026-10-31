---
title: Chuyển cảnh sáng tạo: whip pan, zoom, light leak, glitch
category: techniques
tags: [transition, chuyển cảnh, whip pan, zoom transition, light leak, glitch, flash, easing, xfade, motion blur]
updated: 2026-10-31
sources:
  - https://nofilmschool.com/how-to-do-a-whip-pan
  - https://flexclip.com/learn/whip-pan-transition.html
  - https://photofocus.com/software/tutorials-software/easy-whip-swish-pan-in-after-effects/
  - https://www.miracamp.com/learn/premiere-pro/whip-transition
  - https://forum.shotcut.org/t/motion-blur-pan-transition-whip-pan-tutorial-part-one-now-completed/20760
  - https://www.premiumbeat.com/blog/create-seamless-transitons-whip-pan/
  - https://aejuice.com/blog/how-to-create-a-smooth-zoom-blur-transition-in-after-effects/
  - https://www.premiumbeat.com/blog/zoom-in-premiere-pro/
  - https://forum.shotcut.org/t/smooth-blur-in-transition/12443
  - https://tutvid.com/premiere-pro/create-light-leak-transition-premiere-pro/
  - https://invideo.io/blog/light-leaks/
  - https://theschoolofphotography.com/tutorials/light-leak-overlay
  - https://blog.nobledesktop.com/learn/premiere-pro/rgb-transition-effect
  - https://www.premiumbeat.com/blog/glitch-effect-tutorial-after-effects/
  - https://www.graduateschool.edu/learn/premiere-pro/rgb-glitch-video-premiere
  - https://github.com/scriptituk/xfade-easing/blob/main/README.md
  - https://github.com/gl-transitions/gl-transitions/blob/master/README.md
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/MOTION_PHILOSOPHY.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/short-form-video/SKILL.md
  - https://github.com/FFmpeg/FFmpeg/blob/release/6.1/doc/filters.texi
---
# Chuyển cảnh sáng tạo: whip pan, zoom, light leak, glitch

Mặc định vẫn là **cắt cứng**; chuyển cảnh là dấu câu, dùng ở chỗ đổi phần/đổi ý/khoảnh khắc năng lượng. Hai
nguyên tắc từ các playbook: (1) **xoay vòng kiểu chuyển cảnh** — không hai cú liên tiếp cùng một kiểu; (2)
**có easing** — xfade của ffmpeg chạy tiến độ tuyến tính nên "bắt đầu và dừng đột ngột, thiếu sức sống"
(xfade-easing). Tiếng whoosh/impact phải trùng **đỉnh** chuyển động (lệch vài chục ms là thấy).

Mọi công thức dưới đã chạy thử trên ffmpeg 6.1.1 (2026-10-31), test ở 360x640 — với 1080x1920 nhân bán kính blur ×3.

## 1. Whip pan (lia nhanh có nhoè)
- Thông số tham khảo: lớp blur 8 frame ở 24 fps (20 frame ở 60 fps); whip 10 frame với keyframe ±5 frame quanh
  điểm cắt; blur 0 → cực đại ở điểm cắt → 0, hướng ngang. Hai cảnh nên lia **cùng hướng, cùng tốc độ**.
- ffmpeg (đã thử) — trượt 0,2 s + nhoè hướng ngang mạnh nhất ở giữa:
```
[a][b]xfade=transition=slideleft:duration=0.2:offset=1.4,
dblur=angle=0:radius=25:enable='between(t,1.4,1.6)',
dblur=angle=0:radius=40:enable='between(t,1.4667,1.5334)'[v]
```
- Biến thể "vertical whip" (claude-video-editor): cảnh ra trượt lên −150 px + blur 30 px trong 0,33 s (ease-in),
  cảnh vào từ +150 px blur 30 → 0 trong 1,0 s (ease-out), vận tốc khớp tại điểm cắt.
- "Light-streak whip": một vệt sáng mờ quét ngang khung trong 0,3–0,4 s, bắn đúng điểm cắt.

## 2. Zoom transition (zoom xuyên cảnh)
- Scale 100% → ~150% (đừng quá 150% với footage độ phân giải thấp) ở cuối cảnh A với ease-in, cảnh B bắt đầu ở
  mức phóng tương ứng rồi về 100% với ease-out; chồng ~8 frame; motion blur ở đỉnh.
- ffmpeg (đã thử) — zoom cubic vào đến điểm cắt t=1.0 rồi nhả, có nhoè chuyển động quanh đỉnh:
```
[j]zoompan=z='1+0.5*if(between(in_time,0.75,1.0),pow((in_time-0.75)/0.25,3),
                    if(between(in_time,1.0,1.3),pow(1-(in_time-1.0)/0.3,3),0))'
   :x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,
 split[z1][z2];[z2]tmix=frames=3[zb];[z1][zb]overlay=enable='between(t,0.85,1.15)'[v]
```
- **Bẫy đã gặp**: `tmix=…:enable='between(…)'` (timeline) cho **hình xanh lá** ở ffmpeg 6.1. Dùng `split → tmix →
  overlay=enable=…` như trên, hoặc `tblend=all_mode=average:enable=…` (trộn 2 frame) — cả hai đã kiểm tra đúng màu.
- xfade có sẵn `zoomin` nhưng đơn giản, không easing.

## 3. Light leak / film burn
- Đặt lớp leak lên trên, blend **Screen** (đen biến mất, sáng cộng vào); Add cho rực hơn; opacity ~70%; dissolve
  3–4 frame ở hai đầu nếu leak không bắt đầu/kết thúc bằng đen. Đỉnh sáng đặt **đúng điểm cắt** để che cú cắt.
- ffmpeg (đã thử) — tự sinh leak ấm bằng `gradients`, làm mờ, fade về đen, blend screen:
```
gradients=s=1080x1920:r=30:d=3:type=radial:c0=0xFF7A1A:c1=0xFFD27F:c2=0x000000:nb_colors=3
  :x0=120:y0=360:x1=990:y1=1800:speed=0.08,format=gbrp,gblur=sigma=120,
fade=t=in:st=1.1:d=0.25:color=black,fade=t=out:st=1.45:d=0.45:color=black[leak];
[base]format=gbrp[b];[b][leak]blend=all_mode=screen:shortest=1,format=yuv420p[v]
```
- Nhanh hơn mà nhìn như nhau (đã so khung hình): sinh leak ở 270x480, `gblur=sigma=30`, rồi `scale=1080:1920` trước
  `fade` — 3 s ở 1080p giảm từ 5,7 s xuống 4,0 s render.
- Hợp với: vlog ấm, đồ ăn, hoài niệm. Không hợp: tech sạch.

## 4. Glitch / RGB split
- Tách kênh màu lệch nhau vài khung, thêm nhiễu và lệch dòng; dùng tiết chế, đúng điểm nhấn.
- ffmpeg (đã thử) — 6 frame glitch:
```
rgbashift=rh=-14:bh=14:enable='between(n,12,15)',
rgbashift=rh=8:gv=-6:bh=-8:enable='between(n,16,17)',
noise=alls=45:allf=t:enable='between(n,12,17)',
geq=lum='lum(X+if(lt(mod(floor(Y/24)+N,5),1),18,0),Y)':cb='cb(X,Y)':cr='cr(X,Y)':enable='between(n,13,15)'
```
(nhân số pixel lệch ×3 ở 1080p). Hợp: tech, game, velocity; không hợp ASMR thư giãn.

## 5. Flash, mask/shape, kiểu xfade còn bỏ ngỏ
- Flash trắng 2–3 frame ở đổi phần lớn ("flash-through-white"); vedit đã có `graphics: flash`.
- Reveal theo hình: xfade có `circleopen/circleclose/circlecrop/rectcrop/radial/diag*/vertopen/horzopen`.
  Reveal theo **vật** (người/vật che khung) cần mask (rembg, RobustVideoMatting) — khó.
- ffmpeg 6.1 có 58 kiểu xfade (0–57) + `custom`; nhóm `cover*`/`reveal*`/`*wind`/`*slice`/`squeeze*` hợp video ngắn.
- Easing cho xfade trên ffmpeg thường: `transition=custom:expr='st(0,<easing P>);<biểu thức chuyển cảnh dùng ld(0)>'`
  — bắt buộc `-filter_complex_threads 1` (st/ld không an toàn đa luồng) → render chậm hơn. Repo xfade-easing có sẵn
  biểu thức cho các xfade gốc + nhiều GL Transitions đã port.

## Áp dụng vào vedit

- Hiện có: `Clip.transition` 22/58 kiểu xfade, tuyến tính; `graphics: flash`; `motion: punch/shake` (không blur).
- Đề xuất (xếp theo giá trị): (1) mở thêm kiểu xfade `cover*/reveal*/squeeze*/hlwind/vuslice/zoomin`;
  (2) kiểu mới tự dựng: `whip_left/right/up/down` (slide + dblur bậc), `zoom_through` (zoompan easing + blur theo
  cách split/overlay), `light_leak` (gradients + screen), `glitch` (rgbashift + noise + geq), `flash_white`;
  (3) tham số `easing` (cubic/quint/back) qua biểu thức custom; (4) `vedit validate` cảnh báo khi 2 transition
  liên tiếp cùng kiểu hoặc >5 cắt cứng liên tiếp ở video năng lượng cao.
- Agent 2 hiện tại có thể: dùng `smoothleft`/`slideup` 0,2–0,3 s + `sfx:whoosh` + `motion: punch` ngay sau cắt
  để giả whip/zoom; `fadewhite` 0,15 s + `sfx:sparkle` giả light leak sáng.
- Xem thêm: `techniques/claude-video-editor-chon-chuyen-canh-theo-y-nghia`, `techniques/claude-video-editor-luat-chuyen-dong-va-ngon-ngu-hinh-anh`.

_Ghi chú nguồn: trang ngoài GitHub đọc qua trích đoạn tìm kiếm; README xfade-easing/gl-transitions và tài liệu
filter FFmpeg đọc trực tiếp; công thức do Agent 1 chạy thử._
