---
title: Speed ramp, freeze frame, keyframe zoom và split screen
category: techniques
tags: [speed ramp, slow motion, velocity, freeze frame, keyframe, easing, zoompan, ken burns, punch-in, shake, parallax, split screen]
updated: 2026-10-31
sources:
  - https://www.capcut.com/tools/speed-ramp
  - https://filmora.wondershare.com/video-editing/how-to-slow-mo-in-capcut.html
  - https://shotkit.com/velocity-capcut/
  - https://morphic.com/ai-glossary/Speed-Ramping
  - https://fstoppers.com/education/beginners-guide-speed-ramping-74536
  - https://blog.frame.io/2024/01/17/insider-tips-speed-ramping-in-final-cut-pro
  - https://lists.ffmpeg.org/pipermail/ffmpeg-user/2019-September/045470.html
  - https://ffmpeg.org/pipermail/ffmpeg-user/2017-June/036310.html
  - https://creatomate.com/blog/how-to-speed-up-or-slow-down-video-playback-using-ffmpeg
  - https://www.kapwing.com/resources/how-to-do-the-record-scratch-yep-thats-me-meme/
  - https://www.flexclip.com/learn/character-introduction-freeze-effect-premiere-pro.html
  - https://FlexClip.com/learn/freeze-frame-video.html
  - https://lists.ffmpeg.org/pipermail/ffmpeg-trac/2016-December/037787.html
  - https://ffmpeg.org/pipermail/ffmpeg-trac/2025-March/072904.html
  - https://lists.ffmpeg.org/pipermail/ffmpeg-devel/2020-February/257073.html
  - https://github.com/scriptituk/xfade-easing/blob/main/README.md
  - https://github.com/mifi/editly/blob/master/README.md
  - https://github.com/FFmpeg/FFmpeg/blob/release/6.1/doc/filters.texi
  - https://github.com/BrokenSource/DepthFlow/blob/main/readme.md
  - https://www.capcut.com/el-gr/resource/capcut-3d-zoom
  - https://macmyths.com/how-to-do-the-3d-photo-effect-on-tiktok/
---
# Speed ramp, freeze frame, keyframe zoom và split screen

Các kỹ thuật "thao tác thời gian và khung hình" — thứ làm video trông *được dựng* chứ không chỉ *được cắt*. Mọi
lệnh dưới đây đã chạy thử trên ffmpeg 6.1.1 với `inbox/video-01.mov` (720x1280, 30 fps) ngày 2026-10-31.

## 1. Speed ramp (đổi tốc độ mượt trong một clip)

**Preset CapCut** (Speed → Curve): Montage, Hero, Bullet, Jump Cut, Flash In, Flash Out; tự vẽ đường cong 5 điểm.
Bullet = nhanh → *đập* chậm → bật lại nhanh; Hero = giữ đoạn slow-mo ở giữa.

**Thông số hay dùng**: 100% → 10–20% (chậm 5–10 lần) trong 0,5–1 s, giữ chậm 1–2 s, rồi trả về (quy ước, chỉnh
theo nhạc). Điểm khoá càng gần nhau thì tăng/giảm tốc càng gắt.
- Tốc độ tối thiểu không giật = fps timeline / fps quay: 24/60 = 40%; 30/120 = 25%. Footage điện thoại 30 fps
  chậm xuống 25% sẽ lặp frame → cần nội suy (optical flow) hoặc chấp nhận "giật có chủ ý".
- Velocity edit: ramp đặt ở drop/bass/clap; một ramp đúng chỗ hơn năm ramp tuỳ tiện; thêm motion blur/rung/chớp.

**ffmpeg — một biểu thức `setpts` duy nhất (đã thử)**: gọi f = 1/tốc độ (hệ số kéo dãn). Ramp tuyến tính f: 1→F
trên [a,b] (giây nguồn), giữ F đến c, trả F→1 trên [c,d]. Thời gian ra = tích phân f:
```
k1=(F-1)/(b-a); Ib=(b-a)(1+F)/2; Ic=Ib+F(c-b); k2=(F-1)/(d-c); Id=Ic+(d-c)(F+1)/2
setpts='( if(lt(T,a), T,
         if(lt(T,b), a+(T-a)+k1/2*(T-a)^2,
         if(lt(T,c), a+Ib+F*(T-b),
         if(lt(T,d), a+Ic+F*(T-c)-k2/2*(T-c)^2,
                     a+Id+(T-d))))) )/TB', framerate=fps=30
```
Ví dụ đã chạy: a=0.4, b=0.8, c=1.4, d=1.8, F=4 trên đoạn cà rơi 12.95–15.15 s → 2,2 s nguồn thành 5,23 s.
- Sau `setpts` phải chuẩn lại fps: `fps=30` (lặp frame, nhanh), `framerate=fps=30` (trộn frame, nhanh: 0,8 s),
  `minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir` (nội suy chuyển động, đẹp nhất nhưng **~20 lần
  chậm hơn**: 16 s cho 2,2 s ở 360p).
- Lỗi thường gặp: nhân PTS với hệ số đổi theo thời gian (`lerp(2,8,T/5)*PTS`) bị báo giật; chia nhiều đoạn
  `trim`+`setpts` thì tiếng lệch ~1 s nếu không đổi `atempo` tương ứng → dùng ánh xạ tích phân như trên.
- **Âm thanh**: (a) tắt tiếng đoạn ramp và đặt SFX/tiếng gốc tốc độ thường đúng khoảnh khắc va chạm (hay nhất
  cho ASMR); (b) `atempo` theo từng bậc; (c) `asetrate=48000*0.5,aresample=48000` cho tiếng trầm "slow-mo" kiểu điện ảnh.

## 2. Freeze frame (dừng hình)

Dùng cho: giới thiệu nhân vật / "Yep, that's me" (dừng hình + tiếng record scratch), nhấn khoảnh khắc đắt (money
shot), đặt chữ/đồ hoạ lên hình đứng yên. Tiếng đi kèm: record scratch, máy ảnh "tách", whoosh, hoặc **cắt tiếng
đột ngột** (im lặng). Biến thể: làm mờ nền + viền chủ thể (cần mask), zoom chậm trong lúc dừng.

ffmpeg (đã thử) — dừng frame thứ 18 của clip trong 36 frame (1,2 s), chớp trắng 2 frame, giảm bão hoà khi dừng:
```
[0:v]fps=30,loop=loop=36:size=1:start=18,setpts=N/30/TB,
hue=s='if(between(t,0.6,1.8),0.35,1)',
drawbox=c=white@0.85:t=fill:enable='between(t,0.6,0.667)'[v]
```
Tiếng: chèn khoảng `anullsrc` 1,2 s giữa hai nửa `atrim` rồi `concat`, đặt SFX "tách" ở mốc 0.6 s.

## 3. Keyframe zoom / pan có easing

- Ken Burns: editly mặc định `zoomAmount` 0.1 (10%), hướng in/out/left/right. Punch-in: 5–15% (vật), 10–20%
  (mặt người, đổi "góc máy" giả).
- **Easing**: chuyển động tuyến tính trông máy móc. Công thức easing của xfade-easing dùng được cho mọi filter có
  biểu thức (zoompan, overlay, rotate, drawtext): lưu tiến độ chuẩn hoá vào `st(0,…)`, ease, rồi nội suy.
```
# zoom 1.0 → 1.3 từ giây 1 đến 2 (cubic in-out), tâm zoom ở (px,py) = (0.45, 0.62)
zoompan=z='st(0,clip((in_time-1)/1,0,1));
           st(0,if(lt(ld(0),0.5),4*ld(0)^3,1-4*(1-ld(0))^3));
           1+0.3*ld(0)'
       :x='clip(0.45*iw-iw/zoom/2,0,iw-iw/zoom)'
       :y='clip(0.62*ih-ih/zoom/2,0,ih-ih/zoom)':d=1:s=1080x1920:fps=30
```
- **Lỗi rung của zoompan** (ticket #4298, vẫn mở 3/2025): toạ độ bị làm tròn theo pixel nên zoom chậm bị "lắc".
  Phóng 2x trước zoompan giảm được nhưng không hết, và chậm/tốn RAM: `scale=iw*2:ih*2,zoompan=…`. Ưu tiên phóng 2x
  cho Ken Burns chậm; punch nhanh ít lộ.

## 4. Rung máy (shake)

- Rung va chạm: biên độ giảm dần trong 0,2–0,4 s, trùng onset tiếng động (vedit đã có `motion: shake`).
- Rung "cầm tay" liên tục cho cảnh chân máy quá tĩnh (đề xuất, chưa có nguồn số liệu): biên độ rất nhỏ
  (0,2–0,5% khung), tần số thấp; thêm xoay nhẹ bằng `rotate=a='0.004*sin(2*PI*1.3*t)'` sau khi phóng 3–4% để
  không lộ mép.

## 5. Parallax / ảnh 3D (2.5D)

CapCut "3D Zoom" là chuyển động 2.5D: tiền cảnh và hậu cảnh di chuyển khác tốc độ dựa trên bản đồ độ sâu.
Hay hỏng ở tóc, tay, vật mảnh, **bề mặt phản chiếu/trong suốt** (hũ thuỷ tinh là ứng viên kém). Mã nguồn mở:
DepthFlow (shader GLSL ray-marching, ước lượng độ sâu bằng model ngoài, tạo loop liền mạch; cần GPU để nhanh).
Trong ffmpeg thuần có thể dùng `displace` với bản đồ độ sâu — phức tạp, xếp loại **khó**.

## 6. Split screen / PiP

Trước–sau, so sánh, hai góc cùng lúc. Khung dọc 1080x1920 chia đôi:
```
[0:v]scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960[top];
[1:v]scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960[bot];
[top][bot]vstack=inputs=2,drawbox=y=958:w=iw:h=4:c=white:t=fill[v]
```
Lưới nhiều ô: `xstack`. PiP: `[1:v]scale=360:-2[p];[0:v][p]overlay=x=W-w-40:y=220`. Cho panel trượt vào:
`overlay=x='-w+w*min(t/0.3,1)'` (thêm easing như mục 3).

## Áp dụng vào vedit

| Kỹ thuật | Hiện có | Thiếu → đề xuất |
|---|---|---|
| Speed | `Clip.speed` hằng số 0.25–4 (atempo theo) | `Clip.speed_ramp` (preset hero/bullet/montage hoặc danh sách điểm) → biểu thức setpts tích phân + `framerate`; tuỳ chọn `minterpolate`; tiếng: tắt/giữ tốc độ thường |
| Freeze | Không | `Clip.freeze: {at, duration, flash, desaturate}` → `loop` + `drawbox` + `hue`; SFX "shutter" |
| Ken Burns | `zoom: in/out` tuyến tính, tâm giữa | thêm `focus_x/y`, easing, hướng pan; phóng 2x trước zoompan cho zoom chậm |
| Punch/shake | `motion` ở tâm khung | thêm `x,y` tâm punch, rotation shake, motion blur (xem ghi chú chuyển cảnh) |
| Split/PiP | Không (1 lớp video) | `Clip.layout` split_v/split_h/pip với nguồn thứ hai |
| Parallax | Không | để sau (cần depth model) |

Với video cà pháo: ramp "hero" ở khoảnh khắc gừng sợi rơi (9.16–10.56 s nguồn) hoặc quả cà chạm nước; freeze 0,8 s
ở frame hũ thành phẩm đẹp nhất kèm "tách" + chữ viết tay.

_Ghi chú nguồn: trang ngoài GitHub đọc qua trích đoạn tìm kiếm; tài liệu filter đọc trực tiếp từ mirror GitHub
FFmpeg 6.1; các lệnh được Agent 1 chạy thử._
