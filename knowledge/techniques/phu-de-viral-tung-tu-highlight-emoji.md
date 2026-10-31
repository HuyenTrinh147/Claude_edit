---
title: Phụ đề viral: từng từ, highlight, emoji
category: techniques
tags: [phụ đề, caption, karaoke, word-by-word, highlight, hormozi, emoji, libass, pycaps, safe zone]
updated: 2026-10-31
sources:
  - https://www.submagic.co/blog/how-to-make-alex-hormozi-captions
  - https://exemplary.ai/blog/alex-hormozi-captions
  - https://sendshort.ai/guides/hormozi-captions/
  - https://autocaptionsstudio.com/guides/hormozi-style-captions.html
  - https://joyspace.ai/hormozi-editing-style-2026-analysis
  - https://www.opus.pro/blog/tiktok-caption-subtitle-best-practices
  - https://pictory.ai/blog/tiktok-captions
  - https://blitzcutai.com/blog/best-caption-placement-short-form-video
  - https://reap.video/blog/short-form-video-safe-zones
  - https://ads.tiktok.com/help/article/tiktok-reservation-in-feed-ads-reach-frequency?lang=en
  - https://sonilo.com/blog/guides/funny-sound-effects-for-videos
  - https://github.com/francozanardi/pycaps/blob/main/README.md
  - https://github.com/francozanardi/pycaps/blob/main/docs/EFFECTS_AND_ANIMATIONS.md
  - https://github.com/francozanardi/pycaps/blob/main/src/pycaps/template/preset/hype/pycaps.template.json
  - https://github.com/francozanardi/pycaps/blob/main/src/pycaps/template/preset/explosive/pycaps.template.json
  - https://github.com/francozanardi/pycaps/blob/main/src/pycaps/template/preset/word-focus/styles.css
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/short-form-video/SKILL.md
  - https://github.com/libass/libass/blob/master/Changelog
  - https://trac.ffmpeg.org/ticket/9002
  - https://community.render.com/t/ffmpeg-libass-subtitles-filter-not-using-fontsdir-parameter-on-render-deployment/39185
---
# Phụ đề viral: từng từ, highlight, emoji

Phụ đề trong video ngắn là **đồ hoạ chuyển động**, không phải "subtitle track". Ba biến số tạo khác biệt: cách
chia cụm (bao nhiêu từ/lần), cách nhấn từ đang đọc, và animation vào/ra.

## 1. Chia cụm & thời gian đọc
- Kiểu **từng từ / 1–3 từ mỗi lần**: chữ to, nhịp nhanh (Hormozi, hype). Kiểu **cụm 3–7 từ**, tối đa 2 dòng,
  hiện 1–3 s: dễ đọc hơn cho giáo dục.
- Tốc độ đọc trên điện thoại ~200–250 từ/phút ≈ 3–4 từ/s → cụm 5 từ cần ~1,5–2 s.
- pycaps chia theo ký tự: `hype` 10–15 ký tự/cụm, `explosive` 10–25, `word-focus` 15–20; tối đa 2 dòng, rộng
  75–85% khung. Submagic (Hormozi): ≤15 ký tự/dòng, 4–6 từ cho 2 dòng.
- Chỉ nhấn **1–2 từ khoá** mỗi cụm; viết hoa toàn bộ chỉ cho 1–3 từ.
- Không để phụ đề lộ trước punchline (chữ cuối hiện sớm hơn tiếng sẽ giết câu đùa).

## 2. Các "preset" đo được từ mã nguồn mở (pycaps)
| Preset | Bố cục | Animation | Màu / chữ |
|---|---|---|---|
| `hype` | đáy, lệch −10%, ≤2 dòng | mỗi từ phóng 0.8→1.0 trong **0,12 s**, vượt 5% ở 70%; cụm fade in/out 0,15 s; emoji vào 85% số cụm | Komika Axis; chưa đọc `#DDDDDD` → đang đọc `#FFFF00` → đã đọc trắng; viền đen 2 px + bóng mờ |
| `explosive` | giữa | từ phóng 0.5→1.0 trong 0,2 s vượt 10%; cụm trượt vào từ trái 80 px 0,4 s ease-out, trượt ra phải 0,3 s; tiếng "ding" vol 0.2 ở cụm khoá (AI gắn thẻ) | chữ vàng `#FFDD00` phát sáng cam |
| `word-focus` | giữa | — | IN HOA, từ đang đọc có **hộp nền cam `#f76f00`** bo 5% |

Animation mặc định của pycaps: `pop_in` 0,3 s (phóng từ 50% có nảy), `zoom_in` 0,3 s, `slide_in` 0,3 s; overshoot
mặc định 10% đạt đỉnh ở 70% thời lượng; easing `ease_out` cho vật đi vào.

claude-video-editor (karaoke): Montserrat 900, 46–58 px ở khung rộng 1080, từ đang đọc phóng 1.08 + màu nhấn,
pop 0,08–0,12 s, **viền thay vì hộp nền** ("như graffiti trên khung, không phải phụ đề").

## 3. Phong cách Hormozi
Chữ sans rất đậm IN HOA (Montserrat Black/Anton; bản cũ dùng TheBoldFont — không có thông số chính thức), viền +
bóng, từ đang đọc vàng (hoặc xanh lá), 1–3 từ/lần, animation pop. Phân tích 2026: bản "tinh gọn" giữ phụ đề từng
từ + cắt + zoom, **bỏ emoji, chớp màu, SFX dày**.

## 4. Vị trí (khung 9:16)
Giữ chữ trong ~70% giữa theo chiều dọc và ~80% theo chiều ngang, điểm ngọt hơi trên tâm; tránh ~130 px trên
(tab For You) và ~120 px mép phải (nút tương tác) — số liệu blog, mỗi nguồn khác nhau. Tài liệu quảng cáo TikTok:
caption bài đăng càng dài thì vùng an toàn càng nhỏ. Kiểm tra trên cả iOS và Android.

## 5. Emoji
- **libass không vẽ emoji màu**: thử với Noto Color Emoji (2026-10-31) → emoji ra dạng nét đơn sắc theo màu chữ.
  Changelog libass không nhắc hỗ trợ font màu; ticket ffmpeg #9002 và thread Render cho thấy emoji phụ thuộc
  fontconfig và dễ ra ô đen.
- Cách làm được (đã thử): dựng emoji bằng Pillow rồi overlay PNG:
```python
from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)  # CBDT: cỡ 109
img = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
ImageDraw.Draw(img).text((5, 5), "🔥", font=f, embedded_color=True)
img.save("fire.png")
```
  rồi `overlay` theo thời gian từ (có thể thu phóng pop bằng `scale` + `overlay` trước khi ghép).

## 6. Công thức libass cho các kiểu nhấn
- Pop từng từ có vượt: `{\fscx80\fscy80\t(0,84,\fscx105\fscy105)\t(84,120,\fscx100\fscy100)}TỪ`.
- Đổi màu từ đang đọc: một event cho mỗi khoảng từ, từ hiện tại bọc `{\c&H00FFFF&}…{\r}` (vàng = &H00FFFF& BGR).
- Hộp nền cho từ đang đọc: vẽ `round_rect_path` (lệnh `\p1`) đúng toạ độ từ — tính x bằng độ rộng font (FontBook
  của vedit đã đo được), đặt ở layer dưới chữ.
- Quét màu kiểu karaoke: `\kf<centi-giây>` trước mỗi từ (màu SecondaryColour → PrimaryColour chạy dần).

## Áp dụng vào vedit
- Đang có: `captions.style` = clean / boxed / bold_pop / karaoke (từ đang đọc đổi màu + 110%), `uppercase`,
  `position`, `size`, `font`, `highlight_color`; mốc từng từ từ faster-whisper.
- Thiếu → đề xuất (độ khó thấp–vừa, toàn bộ bằng libass):
  1. `captions.chunk`: `words` (1–3) | `chars` (10–25) | `phrase` — tự chia cụm theo mốc từ.
  2. Preset: `hype`, `explosive`, `word_box` (hộp nền từ đang đọc), `hormozi` với thông số mục 2–3.
  3. Nhấn từ khoá: `captions.emphasis: [{"word": "giòn", "color": "#FFD400", "scale": 1.2, "sfx": "pop"}]`.
  4. Animation vào/ra theo cụm (fade 0,15 s, slide 80 px) và theo từ (pop 0,12 s vượt 5%).
  5. Emoji màu qua PNG (Pillow) + animation pop; tự chèn emoji theo từ khoá (tuỳ chọn).
- Video không lời (ASMR cà pháo) không cần phụ đề; chữ ở đó là kinetic typography — xem
  `techniques/kinetic-typography-callout-lower-third-va-sticker`.
- Xem thêm: `techniques/video-use-phu-de-cum-2-3-tu-theo-moc-tung-tu`, `techniques/claude-video-editor-phu-de-dong-theo-nang-luong-va-nhan-tu`, `typography/cap-font-he-thong-chu-theo-the-loai-video`.

_Ghi chú nguồn: trang ngoài GitHub đọc qua trích đoạn tìm kiếm; thông số preset đọc trực tiếp trong mã pycaps;
thử nghiệm emoji do Agent 1 chạy._
