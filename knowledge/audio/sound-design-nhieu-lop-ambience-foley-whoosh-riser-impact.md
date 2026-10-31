---
title: Sound design nhiều lớp: ambience, foley, whoosh, riser, impact
category: audio
tags: [sound design, sfx, ambience, room tone, foley, whoosh, riser, impact, asmr, aevalsrc, eq]
updated: 2026-10-31
sources:
  - https://krotos.studio/blog/what-is-sound-design-in-video-editing
  - https://krotos.studio/blog/post-production-sound-design
  - https://sfxengine.com/blog/sound-design-tips-for-video-editors
  - https://pixflow.net/blog/sound-effects-layering/
  - https://northwestmediasystems.com/blog/sound-design-for-video-editors-fundamentals/
  - https://www.markstudios.com/blog/sound-design-music-selection-for-video-2026
  - https://toneproduction.net/sound-design-for-video-post-production-techniques/
  - https://filmora.wondershare.com/vlog-tips/make-asmr-cooking-video.html
  - https://www.maono.com/blogs/news/why-food-asmr-is-so-addictive-the-mics-that-make-it-work
  - https://sparki.io/blog/how-to-edit-food-asmr-videos
  - https://audioedit.io/blog/how-to-make-asmr-audio
  - https://asmrregistry.com/guides/how-to-create-asmr-food-content/
  - https://www.freelancer.in/projects/sound-design/youtube-cooking-asmr-editing
  - https://favikon.com/blog/who-is-bayashi
  - https://www.kapwing.com/resources/how-to-do-the-record-scratch-yep-thats-me-meme/
  - https://github.com/FFmpeg/FFmpeg/blob/release/6.1/doc/filters.texi
---
# Sound design nhiều lớp: ambience, foley, whoosh, riser, impact

Âm thanh làm nửa cảm giác "có tay nghề". Cấu trúc chuẩn: **ambience (nền) → foley (động tác) → SFX nhấn (whoosh,
riser, impact) → nhạc**, mỗi lớp một track/stem riêng, gán nhãn rõ.

## 1. Các lớp và thông số
| Lớp | Vai trò | Thông số / quy tắc |
|---|---|---|
| Ambience / room tone | lấp "lỗ im" giữa các cú cắt | thu ≥30 s room tone mỗi buổi quay; dưới lời thoại ở ~−45 đến −50 dB; nghe thấy rõ là đã quá to; ép xuống khi có lời |
| Foley | tiếng động tác trên hình (bước chân, vải, dao, thìa) | không có phòng foley thì dùng thư viện SFX tốt |
| Whoosh | che cú cắt, chuyển cảnh | transient trùng **đỉnh chuyển động** — lệch vài chục ms là lộ |
| Riser | dồn nén | thường 1–2 s cao độ tăng, **kết thúc đúng** điểm nhấn |
| Impact / hit | điểm rơi | sub trầm (độ nặng) + transient sắc (lực) + đuôi vang/ambience (thật), nén nhẹ cả bus |
| Nhạc | cảm xúc, nhịp | xem `audio/am-thanh-cho-video-ngan` |

Công thức riser "điện ảnh": sweep thiết kế + đoạn đảo ngược (reverse) để tạo chờ đợi + lớp texture + impact sạch;
cắt phần build khớp điểm dựng, có fade.

**Kiềm chế**: người mới thêm whoosh cho mọi chuyển cảnh và riser cho mọi khoảnh khắc căng — sound design giỏi phần
lớn là bớt.

## 2. Tiếng cho các khoảnh khắc đặc biệt
- Dừng hình / "Yep, that's me": record scratch (kéo dài hết hình dừng), máy ảnh "tách", whoosh, hoặc cắt im bặt.
- Chữ/sticker bật ra: pop/click rất nhỏ; khoảnh khắc "wow": ding/sparkle.
- Hài: dọn nhạc trước punchline, không nhét tiếng vào khoảng dừng.

## 3. ASMR / đồ ăn
- **Sound-first**: tiếng thật (xèo, giòn, dao, thìa) là track chính; tách và làm rõ từng vi chi tiết, chỉ thêm foley
  nhẹ khi cần. Bayashi nổi tiếng nhờ đồng bộ các tiếng thành một nhịp (đánh giá thứ cấp).
- Thu: mic cách nguồn ~3–8 inch (7–20 cm); tránh clip ở tiếng to nhanh (xèo, va chạm) — méo thì không cứu được.
- EQ: tăng nhẹ high-mid ~3–5 kHz cho độ giòn, cắt nhẹ dải trầm để bỏ ù phòng; giảm ồn vừa phải (profile từ đoạn im)
  — giảm mạnh làm hỏng tiếng. Giữ âm lượng đều; ASMR phần nhiều là "trừ đi" lỗi.
- Nhạc: không có, hoặc thấp hơn trigger 4–6 dB.

## 4. Công thức ffmpeg (đã chạy thử 2026-10-31, mức đỉnh đo bằng volumedetect)
```
# Riser 1,5 s: nhiễu trắng + sine quét lên, tăng dần, kết thúc gọn (đỉnh −4,7 dB)
aevalsrc='0.35*(2*random(0)-1)*pow(t/1.5,3)+0.25*sin(2*PI*(200*t+300*t*t))*pow(t/1.5,2)':s=48000:d=1.5,
highpass=f=300,afade=t=out:st=1.47:d=0.03

# Impact 1,2 s: sub quét xuống + nhiễu chát + vang ngắn (đỉnh −7,3 dB)
aevalsrc='0.9*sin(2*PI*(45*t+60*(1-exp(-t*18))/18))*exp(-t*6)+0.5*(2*random(0)-1)*exp(-t*40)':s=48000:d=1.2,
lowpass=f=4000,aecho=0.8:0.5:60|120:0.35|0.2,afade=t=out:st=0.9:d=0.3

# Máy ảnh "tách-tách" 0,25 s (hai xung nhiễu cách 70 ms)
aevalsrc='0.8*(2*random(0)-1)*(exp(-t*90)+gte(t,0.07)*exp(-(t-0.07)*70))':s=48000:d=0.25,
bandpass=f=3500:width_type=h:w=3000

# Whoosh stereo 0,5 s lia trái → phải (mỗi kênh một biểu thức, ngăn bằng |)
aevalsrc='(2*random(0)-1)*sin(PI*t/0.5)^2*(1-t/0.5)|(2*random(1)-1)*sin(PI*t/0.5)^2*(t/0.5)':s=48000:d=0.5:c=stereo,
bandpass=f=1200:width_type=o:w=2

# Làm rõ tiếng ASMR một clip (EQ + giảm ồn nhẹ)
highpass=f=80,equalizer=f=4000:t=q:w=1.2:g=3,afftdn=nr=10:nf=-42
```
Phổ tần đã kiểm tra: riser tăng dần, impact tắt dần có vệt vang, shutter hai xung, whoosh dải giữa phồng rồi xẹp.
Tổng hợp chỉ là bản nháp — thư viện SFX thu thật (CC0) vẫn hay hơn.

## Áp dụng vào vedit
- Hiện có: 7 SFX tổng hợp (`sfx:pop/click/ding/sparkle/whoosh/thud/rise`), đặt theo giây, chỉnh `volume`; `AudioTrack`
  nhận **file âm thanh bất kỳ** với `role: "sfx"` → có thể dùng ngay thư viện SFX thật nếu đặt trong `assets/sfx/`.
  SFX đi vào bus giọng nên cũng ép nhạc khi `duck`.
- Thiếu → đề xuất: (1) thêm SFX tổng hợp `riser`, `impact`, `shutter`, `whoosh_lr/rl` (stereo), `record_scratch`
  (công thức trên); (2) tham số `pan` (−1..1) cho track; (3) `role: "ambience"` lặp room tone dưới toàn video, tự
  ép khi có tiếng trigger; (4) `Clip.audio_fx`: `asmr_clarity` (EQ + giảm ồn nhẹ), `highpass`, `presence_db`;
  (5) `vedit analyze` xuất onset tiếng động để đặt SFX/punch đúng transient (Agent 3 đang đo tay).
- Với video cà pháo: thay chuỗi `pop` 0.15 lặp lại bằng: room tone liền mạch + tiếng thật được làm rõ; chỉ 2–3 SFX có
  chủ đích (shutter khi dừng hình thành phẩm, whoosh lia khi sang phần cà, ding nhỏ ở kết).

_Ghi chú nguồn: trang ngoài GitHub đọc qua trích đoạn tìm kiếm; công thức aevalsrc do Agent 1 viết và chạy thử._
