---
title: Kiểu chữ trend trên TikTok/Reels
category: typography
tags: [trend, caption, hormozi, mrbeast, karaoke, viền kép, chữ 3d, sticker, emoji, tiktok sans, reels]
updated: 2026-10-31
sources:
  - https://www.submagic.co/blog/how-to-make-alex-hormozi-captions
  - https://sendshort.ai/guides/hormozi-captions/
  - https://www.kapwing.com/explore/hormozi-style-captions-template
  - https://www.submagic.co/blog/how-to-make-captions-like-mrbeast
  - https://submagic.co/blog/how-to-make-captions-like-iman-gadzhi
  - https://blitzcutai.com/blog/tiktok-caption-trends-2026
  - https://blitzcutai.com/blog/best-caption-style-tiktok
  - https://developers.tiktok.com/blog/tiktok-sans-open-source
  - https://raw.githubusercontent.com/tiktok/TikTokSans/main/README.md
  - https://www.kapwing.com/resources/about-the-new-instagram-fonts
  - https://forum.figma.com/ask-the-community-7/how-to-recreate-the-tiktok-classic-text-background-effect-in-figma-without-making-separate-layers-for-each-line-50902
  - https://feedback.descript.com/feature-requests/p/fancy-captions-rounded-background-corners
  - https://raw.githubusercontent.com/googlefonts/noto-emoji/main/README.md
  - (mọi công thức JSON đã render thử trên video thật bằng vedit, 2026-10-31)
---
# Kiểu chữ trend trên TikTok/Reels

**Thời điểm quan sát: 2026-10-31.** Tổng hợp từ bài viết 2025–2026, phần lớn là blog của công cụ làm caption
(Submagic, SendShort, Blitzcut, Kapwing) — coi là tín hiệu xu hướng, không phải số liệu kiểm chứng. Không xem
trực tiếp được TikTok/YouTube từ môi trường này (bị chặn mạng).

## Bức tranh chung

- Caption **từng từ, chạy theo giọng nói** là chuẩn mặc định của video nói chuyện năm 2026; khác biệt nằm ở biến
  thể (font, màu nhấn, chuyển động). Kiểu Hormozi (HOA, vàng chói) được một số nguồn coi là "bão hoà".
- Hướng "tối giản động" (dynamic minimalism): chữ thường/sentence case, một màu nền + một màu nhấn, font script
  không còn dùng cho phụ đề chính; TikTok Sans được cho là đang lên (nguồn: Blitzcut — chưa kiểm chứng độc lập).
- TikTok Sans (font của chính TikTok) mở mã nguồn OFL 1.1 tháng 7/2025, có tiếng Việt; đã có trong vedit.
- Instagram có bộ chữ trong app: Classic, Modern, Typewriter, Strong, Meme, Elegant, Directional, Literature và
  từ 8/2024 thêm Signature, Editor, Poster, Bubble, Deco, Squeeze. Thay thế gần trong vedit (gợi ý): Modern →
  `TikTok Sans`; Strong/Poster/Squeeze → `Anton`, `Barlow Condensed`, `Phudu`; Bubble → `Baloo 2`;
  Literature/Editor/Elegant → `Prata`, `Yeseva One`; Signature → `Pacifico`; Meme → `Anton` trắng viền đen;
  Typewriter → `JetBrains Mono` (font hệ thống).

## Bảng kiểu chữ: làm được gì bằng vedit hiện tại

| Kiểu | Mô tả | vedit hiện tại |
|---|---|---|
| Karaoke kiểu Hormozi | HOA, sans đen đặc, từ đang nói đổi màu vàng/xanh | ✅ `captions.style: karaoke` |
| Từng từ một (kiểu MrBeast) | mỗi lần 1 từ, to, viền đen dày | ✅ mỗi `segment` một từ, `bold_pop` |
| Từ khoá đổi màu cố định | một từ khoá nổi màu suốt câu | ✅ mẹo dồn mốc `words` (1 màu/khối) |
| Tối giản động | chữ thường, TikTok Sans, 1 màu nhấn | ✅ `style: clean` |
| Đổi độ đậm theo lời (Iman Gadzhi) | từ đang nói chuyển mảnh → đậm | ❌ thiếu |
| Viền kép sticker | viền trắng trong + viền đen ngoài | ✅ mẹo 2 `texts` chồng nhau |
| Nền chữ kiểu TikTok "Classic" | nền trắng bo góc ôm từng dòng | ⚠️ `pill` (1 khối), `boxed` (từng dòng, góc vuông) |
| Bóng dài / chữ 3D | khối chữ đùn sâu | ✅ mẹo xếp 5–8 bản sao lệch 3 px |
| Neon / glow | viền sáng nhoè | ❌ thiếu (`\blur` chưa mở) |
| Gradient / chrome | chữ chuyển màu, ánh kim | ❌ thiếu |
| Viết tay "tự viết ra" | nét chữ chạy ra | ⚠️ `wipe` / `typewriter` + font viết tay |
| Băng tin / lower third | băng màu nghiêng sau chữ | ✅ `shape: banner` |
| Emoji cạnh chữ | 🔥😋 trong caption | ⚠️ libass vẽ emoji đơn sắc xấu → dùng ảnh PNG qua `images` |
| Chữ sau chủ thể | chữ nằm sau người/vật | ❌ cần mặt nạ tách chủ thể |
| Bút dạ quang sau từ | vệt màu quét sau một từ | ❌ thiếu |

## Công thức đã kiểm chứng

### 1. Karaoke kiểu Hormozi
Cụm 2–4 từ, `words` lấy từ mốc từng từ của phụ đề (whisper); không có `words` thì vedit chia theo số ký tự.
```json
{"captions": {"style": "karaoke", "font": "Montserrat", "uppercase": true, "size": 84, "position": "lower", "highlight_color": "#FFE600",
  "segments": [{"start": 0.0, "end": 1.6, "text": "đừng đổ nước sôi",
    "words": [{"text": "đừng", "start": 0.0, "end": 0.4}, {"text": "đổ", "start": 0.4, "end": 0.75}, {"text": "nước", "start": 0.75, "end": 1.15}, {"text": "sôi", "start": 1.15, "end": 1.6}]}]}}
```
Màu nhấn theo ý nghĩa (theo các hướng dẫn kiểu Hormozi): vàng = nhấn mạnh, xanh lá = tiền/thắng, đỏ = cảnh báo/lỗi.
vedit chỉ cho **một** `highlight_color` mỗi khối phụ đề.

### 2. Từng từ một, giữa khung
```json
{"captions": {"style": "bold_pop", "font": "Montserrat Black", "uppercase": true, "size": 110, "position": "center",
  "segments": [{"start": 2.4, "end": 2.9, "text": "ai"}, {"start": 2.9, "end": 3.3, "text": "cho"}, {"start": 3.3, "end": 3.9, "text": "nhiều"}, {"start": 3.9, "end": 4.6, "text": "muối"}]}}
```

### 3. Một từ khoá đổi màu suốt câu (mẹo karaoke)
Cho mọi từ đến hết từ khoá bắt đầu ở `start` của đoạn, các từ sau từ khoá bắt đầu sát `end` → vedit chỉ sinh một
sự kiện: cả câu hiện, riêng từ khoá đổi màu (và to 110%).
```json
{"captions": {"style": "karaoke", "font": "Montserrat", "uppercase": true, "size": 74, "position": "center", "highlight_color": "#39E75F",
  "segments": [{"start": 0.0, "end": 3.0, "text": "đừng đổ nước sôi vào hũ",
    "words": [{"text": "đừng", "start": 0.0, "end": 3.0}, {"text": "đổ", "start": 0.0, "end": 3.0}, {"text": "nước", "start": 0.0, "end": 3.0},
              {"text": "sôi", "start": 0.0, "end": 3.0}, {"text": "vào", "start": 2.999, "end": 3.0}, {"text": "hũ", "start": 2.999, "end": 3.0}]}]}}
```

### 4. Tối giản động
```json
{"captions": {"style": "clean", "font": "TikTok Sans", "size": 66, "position": "lower",
  "segments": [{"start": 0.3, "end": 2.6, "text": "Sáng nay dậy sớm đi chợ nè"}]}}
```

### 5. Viền kép sticker
Hai bản giống hệt (cùng font, cỡ, vị trí, góc, animation); bản sau vẽ đè lên bản trước.
```json
{"texts": [
  {"text": "GIÒN RỤM!", "start": 0, "end": 3, "y": 0.72, "size": 140, "font": "Bangers", "bold": false, "color": "#FFE14D", "outline": 20, "outline_color": "#1E1E1E", "rotation": -6, "animation": "bounce"},
  {"text": "GIÒN RỤM!", "start": 0, "end": 3, "y": 0.72, "size": 140, "font": "Bangers", "bold": false, "color": "#FFE14D", "outline": 9, "outline_color": "#FFFFFF", "rotation": -6, "animation": "bounce"}
]}
```

### 6. Chữ 3D / bóng dài
Các lớp "đùn" màu tối đặt trước, mỗi lớp lệch thêm 3 px (`x` + 0.0028, `y` + 0.0016); lớp trên cùng đặt cuối.
Đã thử 7 lớp với Anton 150 — khối chữ rõ chiều sâu. Ví dụ rút gọn 3 lớp:
```json
{"texts": [
  {"text": "MUỐI HŨ", "start": 0, "end": 3, "x": 0.5084, "y": 0.1548, "size": 150, "font": "Anton", "bold": false, "color": "#B8321C", "outline": 6, "outline_color": "#1E1E1E", "animation": "none"},
  {"text": "MUỐI HŨ", "start": 0, "end": 3, "x": 0.5056, "y": 0.1532, "size": 150, "font": "Anton", "bold": false, "color": "#B8321C", "outline": 6, "outline_color": "#1E1E1E", "animation": "none"},
  {"text": "MUỐI HŨ", "start": 0, "end": 3, "x": 0.5028, "y": 0.1516, "size": 150, "font": "Anton", "bold": false, "color": "#B8321C", "outline": 6, "outline_color": "#1E1E1E", "animation": "none"},
  {"text": "MUỐI HŨ", "start": 0, "end": 3, "x": 0.5, "y": 0.15, "size": 150, "font": "Anton", "bold": false, "color": "#FFD23F", "outline": 6, "outline_color": "#1E1E1E", "animation": "none"}
]}
```
Có animation thì mọi lớp phải cùng `animation` và cùng `start` để chạy khớp.

### 7. Nền chữ kiểu TikTok
Một dòng: `shape: pill` (chữ trên nền tự bỏ viền). Nhiều dòng có nền riêng từng dòng: dùng phụ đề `boxed`
(nền đen mờ, góc vuông). Kiểu gốc của TikTok là nền ôm từng dòng **bo góc** — cả Figma lẫn Descript đều có người
dùng đòi tính năng này, vedit cũng chưa có.
```json
{"captions": {"style": "boxed", "font": "TikTok Sans", "size": 64, "position": "upper",
  "segments": [{"start": 0, "end": 3, "text": "Muối cà pháo 3 ngày\nlà giòn ăn được rồi nha"}]}}
```

### 8. Băng tin / lower third
```json
{"texts": [
  {"text": "TIN NÓNG", "start": 0, "end": 3, "y": 0.13, "size": 96, "font": "Barlow Condensed", "color": "#FFFFFF", "shape": "banner", "shape_color": "#E8232E", "animation": "slide_left"},
  {"text": "Muối cà pháo 3 ngày đã ăn được?", "start": 0, "end": 3, "y": 0.205, "size": 54, "font": "TikTok Sans", "color": "#FFFFFF", "shape": "pill", "shape_color": "#111111", "shape_opacity": 0.78, "animation": "fade"}
]}
```

### 9. Emoji
Không gõ emoji vào `text`/`captions` (libass vẽ thành nét đơn sắc từ FreeSerif/Unifont). Tải PNG Noto Emoji
(Apache 2.0) vào thư mục dự án rồi đặt bằng `images` (đường dẫn tương đối theo thư mục dự án):
`curl -L -o emoji_u1f525.png https://raw.githubusercontent.com/googlefonts/noto-emoji/main/2D/png/512/emoji_u1f525.png`
(tên file = `emoji_u` + mã Unicode viết thường: 1f525 🔥, 1f60b 😋, 1f924 🤤, 1f44d 👍).
```json
{"images": [{"path": "emoji_u1f525.png", "start": 0.0, "end": 1.6, "x": 0.86, "y": 0.70, "width": 0.13}]}
```
Ảnh xuất hiện/biến mất cắt cứng (chưa có animation) — đặt `start` trùng lúc nói từ đó; ghép thêm `sfx:pop`.

## Chọn kiểu theo thể loại

- Talking-head, kiến thức, kinh doanh: karaoke (1) hoặc từ khoá cố định (3); hook bằng chữ 3D (6) hoặc viền kép (5).
- Hài, phản ứng: từng từ một (2) + sticker viền kép (5) + emoji (9).
- Vlog, làm đẹp, lifestyle: tối giản động (4); chữ to chỉ ở hook.
- Tin tức, thông tin: băng tin (8) + `boxed` (7).
- Đừng chồng mọi kiểu trong một video: chọn 1 kiểu phụ đề + 1 kiểu hook.

## Áp dụng vào vedit

Còn thiếu, theo mức đáng làm (vấn đề → giải pháp → độ khó):
1. Không tô nhiều màu theo nghĩa → `captions.keywords: {"tiền": "#39E75F", "đừng": "#FF4D4D"}` hoặc cú pháp `*từ*`
   trong `text` → dễ–vừa.
2. Emoji vỡ → tự tách emoji khỏi chữ, tải/cache PNG Noto Emoji và đặt cạnh từ (đo vị trí bằng FontBook) → vừa.
3. Viền kép, bóng dài phải nhân bản `texts` → `outline2`, `outline2_color`, `extrude` (số lớp, hướng, màu) sinh nhiều
   lớp ASS trong `ass.py` → dễ.
4. Từ đang nói chỉ đổi màu + to 110% → thêm hiệu ứng nảy (`\t` scale 0→120→100%) và kiểu đổi độ đậm (đổi `\fn`
   sang mặt Medium/Black) cho karaoke → dễ.
5. Glow/neon → `glow` = viền màu sáng + `\blur` 6–12 ở lớp dưới → dễ.
6. Nền bo góc ôm từng dòng (TikTok Classic) → đo từng dòng bằng FontBook, vẽ mỗi dòng một `round_rect_path` →
   vừa.
7. Gradient / chrome → xếp nhiều dải `\clip` ngang mỗi dải một màu → vừa.
8. Bút dạ quang quét sau từ, gạch chân chạy → hình chữ nhật/đường kẻ với `\clip` mở dần (như `wipe`) → vừa.
9. Chữ sau chủ thể → mặt nạ tách người (MediaPipe/rembg) + `alphamerge` trong ffmpeg → khó.
