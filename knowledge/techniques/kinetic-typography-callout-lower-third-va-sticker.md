---
title: Kinetic typography, callout, lower third và sticker
category: techniques
tags: [kinetic typography, chữ động, easing, libass, callout, mũi tên, lower third, sticker, meme, text behind subject, progress bar]
updated: 2026-10-31
sources:
  - https://www.tella.com/motion/kinetic-typography.md
  - https://hera.video/blog/kinetic-typography-video-generator-guide
  - https://www.influencers-time.com/boost-short-form-video-retention-with-kinetic-typography-tips/
  - https://www.grid.uns.ac.rs/symposium/download/2024/89.pdf
  - https://my-test.valpo.edu/kinetic-typography-after-effects-template-14746
  - https://blog.frame.io/2017/12/04/create-lower-thirds-titles-that-dont-suck/
  - https://www.epidemicsound.com/blog/lower-thirds/
  - https://riverside.com/blog/lower-thirds
  - https://www.kapwing.com/resources/how-to-do-the-record-scratch-yep-thats-me-meme/
  - https://www.capcut.com/resource/how-to-put-text-behind-a-person-in-capcut
  - https://www.flexclip.com/learn/text-behind-person-effect.html
  - https://www.capcut.com/template-detail/textbehindsubject/7507937836256070973
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/short-form-video/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/MOTION_PHILOSOPHY.md
  - https://github.com/danielgatis/rembg/blob/main/README.md
  - https://github.com/PeterL1n/RobustVideoMatting/blob/master/README.md
  - https://github.com/francozanardi/pycaps/blob/main/docs/EFFECTS_AND_ANIMATIONS.md
---
# Kinetic typography, callout, lower third và sticker

Chữ động "có tay nghề" khác chữ động mặc định ở 3 điểm: **chỉ một từ là ngôi sao**, **chuyển động mang nghĩa**
(gấp → đập/phóng; êm → trượt có easing), và **thời điểm** (chữ đáp đúng beat/tiếng, không sớm hơn thứ nó nói tới).

## 1. Nguyên tắc
- Chọn "hero word" rồi dùng cỡ, tương phản, thời điểm để nhấn; các từ khác vào nhẹ hơn.
- Snap-in/punch scale = khẩn, tự tin; slide-in có easing = bình tĩnh, giải thích.
- Dựng nhịp hình trước, thêm chữ sau để chữ rơi đúng beat mạnh nhất; một cú nhấn chữ ở mốc 2–4 s giúp giảm rời bỏ
  (blog, chưa kiểm chứng).
- IN HOA chỉ cho 1–3 từ; câu dài viết thường dễ đọc hơn.
- Một bài hội thảo 2024 về kinetic typography trong video ngắn: một số kiểu nội suy chuyển động giúp dễ đọc, kiểu
  khác làm khó đọc → easing là quyết định thiết kế cần thử, không phải trang trí.
- Từ playbook short-form (claude-video-editor): ≥3 kiểu easing khác nhau trong một cảnh; chữ "slam/stamp" phải đáp
  **sau khi** chữ mục tiêu hiện đủ 0,10–0,25 s; điểm kết thúc tween khớp biên frame (1/30 s) vì easing gắt bị răng
  cưa; payoff giữ ≥1 s.

## 2. Bộ công cụ libass (vedit vẽ chữ bằng libass)
| Hiệu ứng | Thẻ ASS |
|---|---|
| Easing cho phép biến đổi | `\t(t1,t2,accel,tags)` — accel >1 chậm→nhanh (ease-in), <1 nhanh→chậm (ease-out) |
| Pop có vượt | `\fscx60\fscy60\t(0,140,\fscx110\fscy110)\t(140,240,\fscx100\fscy100)` |
| Lật 3D | `\fry90\t(0,250,0.6,\fry0)` hoặc `\frx` |
| Mờ → nét | `\blur12\t(0,300,\blur0)` |
| Quét lộ chữ | `\clip(x0,y0,x0+1,y1)\t(0,400,\clip(x0,y0,x1,y1))` |
| Trượt | `\move(x1,y1,x2,y2,t1,t2)` — **tuyến tính**; muốn easing: chia thành 2–3 event nối tiếp (đoạn đầu dài, đoạn sau ngắn) hoặc kết hợp `\fsc` vượt |
| Rung chữ | chuỗi `\t` đổi `\frz` ±3° mỗi 40–60 ms |
| Stagger từng ký tự/từ | mỗi ký tự một khối `{\alpha&HFF&\t(t,t+1,\alpha&H00&)}` (vedit `typewriter`, `word_pop`) |

## 3. Lower third
- Trên màn hình 3–6 s (có nguồn 5–7 s), chữ càng dài càng lâu; vào bằng fade hoặc trượt tiết chế; tương phản cao,
  ngắn gọn; không che chi tiết quan trọng.
- Khung dọc: "đáy" thật bị UI che 20–25% → đặt ở ~62–72% chiều cao, lệch trái.

## 4. Callout, mũi tên, khoanh vùng
- Callout chỉ vào **vật thật ở đúng khoảnh khắc**: chấm "ping" → đường kẻ mọc ra (draw-on) → nhãn pop sau ~0,3 s
  (vedit `callout` đang làm đúng chuỗi này).
- Mũi tên/khoanh tròn kiểu **vẽ tay** hợp vlog thẩm mỹ & đồ ăn hơn nhãn pill "corporate". Vẽ vòng tròn "đang vẽ":
  chia đường tròn thành 16–24 cung, mỗi cung một event hiện nối tiếp trong 0,3–0,5 s (libass không animate được
  `\clip` dạng vector).
- Gạch chân quét (underline sweep) dưới từ khoá, 0,2–0,3 s, ease-out.

## 5. Sticker, meme insert
- Sticker pop có vượt + nghiêng 3–8°, sau đó "sống" nhẹ (lắc ±2° chu kỳ 1–2 s) nếu ở lâu >2 s — tránh vật chết.
- "Yep, that's me": dừng hình + tiếng record scratch kéo dài đúng hết đoạn âm thanh; record scratch là hook gây chú ý.
- Meme/reaction cutaway 0,5–1,5 s, luôn có tiếng.

## 6. Chữ sau chủ thể (text behind subject)
- Tách chủ thể (CapCut "cutout"), đặt chữ giữa nền và chủ thể; để chữ **khuất một phần** sau vai/tay mới có chiều
  sâu; chủ thể di chuyển thì phải keyframe tay (CapCut không tự bám).
- Stack mã nguồn mở: rembg (ảnh, CPU được; có `rembg b` nhận luồng rawvideo từ ffmpeg) hoặc RobustVideoMatting (video
  người, 4K 76 fps / HD 104 fps trên GTX 1080 Ti — trên CPU sẽ chậm). Ghép: video nền → lớp chữ → lớp chủ thể có alpha.

## 7. Thẻ thời gian & bộ đếm
- Time-skip "3 ngày sau": thẻ chữ viết tay + lật lịch/đồng hồ, whoosh; hoặc dấu thời gian nhỏ kiểu vlog ("15:30").
- Bộ đếm số (0 → 100%, 1 → 3 ngày): mỗi giá trị một event ngắn 1–2 frame (libass không đổi được nội dung bằng `\t`).

## Áp dụng vào vedit
- Đang có: `texts.animation` (pop, bounce, typewriter, word_pop, slide_up, slide_left, blur_in, wipe, fade), `shape`
  pill/banner, `rotation`; `graphics` callout/badge/progress_bar/highlight/sparkles/flash; thoát luôn là fade 150 ms.
- Thiếu → đề xuất: (1) `exit` animation (pop_out, slide_out, wipe_out) và `easing` cho slide; (2) kiểu chữ mới:
  `flip_3d`, `shake`, `scale_stagger` (từng ký tự phóng + xoay), `stamp` (to → đập xuống + rung nhẹ khung);
  (3) đồ hoạ mới: `arrow` (draw-on, kiểu thẳng/cong/vẽ tay), `circle_draw`, `underline`, `counter`, `lower_third`,
  `timestamp`, `letterbox`; (4) chuyển động "idle" cho sticker/nhãn ở lâu; (5) chữ sau chủ thể (cần matting — khó).
- Với video ASMR/vlog bếp: ưu tiên chữ nhỏ, viết thường, viết tay, ít; nhãn nguyên liệu dạng tag + mũi tên vẽ tay
  thay cho callout pill; bỏ huy hiệu bước to nếu phong cách là "silent vlog" (xem
  `trends/phong-cach-vlog-tham-my-silent-vlog-douyin-cinematic-pov`).
- Xem thêm: `techniques/video-use-animation-overlay-easing-va-thoi-diem-payoff`, `typography/cap-font-he-thong-chu-theo-the-loai-video`.

_Ghi chú nguồn: trang ngoài GitHub đọc qua trích đoạn tìm kiếm; README rembg/RVM và tài liệu repo đọc trực tiếp.
Thẻ ASS đối chiếu với mã `vedit/ass.py` đang chạy._
