---
title: claude-video-editor: Phụ đề động theo năng lượng và nhấn từ
category: techniques
tags: [claude-video-editor, phụ đề, captions, karaoke, nhấn từ, chunking, marker highlight, vùng an toàn, ass]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/helpers/render.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/captions.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/dynamic-techniques.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/css-patterns.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/short-form-video/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/examples/captions/index.html
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/MOTION_PHILOSOPHY.md
---
# claude-video-editor: Phụ đề động theo năng lượng và nhấn từ

## 1. Ba chiều cần quyết (video-use)

- **Chunking**: 1 / 2 / 3 từ hay cả câu mỗi dòng. **Case**: VIẾT HOA / Title / tự nhiên. **Vị trí**: lề dưới.
- Kiểu `bold-overlay` (đã xuất bản, mặc định trong `render.py`): **2 từ/dòng, VIẾT HOA, ngắt ở dấu câu**, Helvetica
  18 bold, chữ trắng viền đen 2, không bóng, `Alignment=2`, `MarginV=90` (theo PlayRes mặc định 288 → chân chữ cao
  ~30% từ đáy, tránh UI TikTok/Reels/Shorts che ~25–30% dưới — "MarginV is NOT taste — it is a platform safe-zone
  rule").
- Kiểu `natural-sentence` (tài liệu/giáo dục): 4–7 từ, sentence case, ngắt ở chỗ nghỉ tự nhiên, MarginV 60–80, chữ to.
- Hard rules: phụ đề **áp cuối cùng** (sau mọi overlay); mốc theo timeline đầu ra:
  `output_time = word.start - segment_start + segment_offset`.

Thuật toán dựng SRT tổng (`build_master_srt`): lấy từ trong [start,end] của từng range → gom 2 từ, ngắt sớm nếu từ
kết thúc bằng `.,!?;:` → đổi sang timeline đầu ra → bỏ dấu `,;:` cuối → VIẾT HOA; nếu end ≤ start thì end = start + 0.4s.

## 2. Chọn kiểu theo giọng điệu (HyperFrames captions.md)

Đọc **toàn bộ** transcript trước khi chọn; 4 trục: cảm giác hình ảnh, palette, mood font, tính cách animation.

| Giọng | Font | Animation | Màu | Cỡ (khung 1080 ngang) |
|---|---|---|---|---|
| Hype/ra mắt | đậm nén 800–900 | scale-pop, `back.out(1.7)`, 0.1–0.2s | sáng trên nền tối | 72–96px |
| Doanh nghiệp | sans sạch 600–700 | fade + trượt, `power3.out` 0.3s | trắng/trung tính | 56–72px |
| Hướng dẫn | mono/sans 500–600 | typewriter/fade 0.4–0.5s | tương phản cao | 48–64px |
| Kể chuyện | serif 400–500 | fade chậm `power2.out` 0.5–0.6s | ấm, dịu | 44–56px |
| Mạng xã hội | sans bo tròn 700–800 | nảy `elastic.out`, từng từ | pill màu vui | 56–80px |

**Gom từ**: năng lượng cao 2–3 từ · trò chuyện 3–5 · chậm rãi 4–6. Ngắt ở ranh giới câu, chỗ nghỉ **≥ 150ms**, hoặc
khi đủ số từ tối đa. **Mỗi lúc chỉ một nhóm phụ đề**; mỗi nhóm có "hard kill" đúng lúc kết thúc (không để sót).
Khung dọc 1080×1920: phụ đề ở "lower middle ~600–700px from bottom" (≈ y 0.64–0.69), **không che mặt**.

## 3. Nhấn từng từ

Quét transcript tìm từ đáng xử lý riêng: **tên thương hiệu/sản phẩm** (to hơn, màu riêng) · **VIẾT HOA** (phóng,
chớp, màu accent) · **con số/thống kê** (đậm, màu accent) · **từ cảm xúc** (animation phóng đại: overshoot, nảy) ·
**CTA** (highlight, gạch chân, đổi màu). "Emphasis words always break the pattern."

Karaoke là nền cho mọi mức năng lượng, chỉ khác cường độ:

| Năng lượng | Highlight | Thoát | Chu kỳ đổi kiểu |
|---|---|---|---|
| Cao | màu accent + glow + phóng **15%** | tung/rơi | mỗi 2 nhóm |
| Vừa–cao | đổi màu | tung/thu | mỗi 3 nhóm |
| Vừa | trắng nhẹ | fade + trượt | mỗi 3 nhóm |
| Vừa–thấp | phóng tối thiểu | fade | 1 kiểu, đổi ease |
| Thấp | tông ấm, chuyển chậm, phóng **3%** | thu | mỗi 4 nhóm |

Short-form-video: Montserrat 900, 46–58px, từ đang đọc phóng **1.08** + màu accent, pop 0.08–0.12s, viền bằng nhiều
lớp text-shadow, **bỏ nền pill** — "graffiti on the frame".

## 4. Hiệu ứng "bút dạ" cho từ nhấn (css-patterns.md)

5 chế độ, đều xác định (không ngẫu nhiên):
- **highlight**: dải vàng `#fdd835` opacity 0.35 sau chữ, `scaleX 0→1` từ trái, 0.5s `power2.out` (có thể nghiêng
  `skewX -2°` cho cảm giác vẽ tay);
- **circle**: viền elip đỏ 3px, rộng 130%/cao 160% chữ, xoay −3°, `scale 0→1` 0.6s `back.out(1.7)`;
- **burst**: 12 tia quanh chữ, dài **so le 40–80px** ("Equal lengths look mechanical"), stagger 0.03s;
- **scribble**: gạch chân lượn sóng tự vẽ (`stroke-dashoffset`), 0.8s;
- **sketchout**: hai nét gạch chéo ±12° cho "giá cũ".
Chọn theo năng lượng: burst cho hype, circle cho thuật ngữ chính, highlight cho mức thường, scribble cho nhẹ. Đổi chế
độ mỗi 2–3 nhóm (cao), 3–4 (vừa), 4–5 (thấp). Với nhạc: biên độ phản ứng âm thanh trên chữ chỉ 3–6%.

## 5. Lower-third có biến (examples/captions)

Composition 5s nhận biến `{num, label, text}`: thanh accent 7px gradient teal + glow, thân nền tối 92% opacity, kicker
mono 21px giãn chữ 0.32em VIẾT HOA (`01 · INTAKE`), chữ chính 46px đậm; vào: trượt lên 34px + fade 0.5s `expo.out`;
ra: lên 12px + fade 0.45s `power2.in` ở 4.45s. Mỗi caption render thành `.mov` ProRes 4444 có alpha rồi chồng lên
video. Recipe: "5 seconds per caption is the floor"; > 12 caption thì video quá dài, nên tách.

## Áp dụng vào vedit

**Đã có**: `captions` với `clean / boxed / bold_pop / karaoke`, `uppercase`, `highlight_color`, `position`
(lower ≈ đáy chữ ở 76% chiều cao), karaoke phóng 110% từ đang đọc; chữ tự co khi quá rộng (texts).

**Còn thiếu**: Agent 2 phải **tự tính mốc** phụ đề sau khi cắt (dễ sai); không có chunking tự động theo năng lượng;
không nhấn riêng từ khoá/số/tên; không có hiệu ứng bút dạ; karaoke chỉ một cường độ.

**Đề xuất (ưu tiên)**:
1. **`vedit captions <slug> --words 2|3|4 [--upper] [--style …]`**: đọc transcript (`words`) + EditPlan, tự đổi mốc sang
   timeline (tính cả `speed` và transition overlap), ngắt ở dấu câu / nghỉ ≥ 150ms / đủ số từ, ghi vào
   `captions.segments` kèm `words`. Bỏ hẳn việc tính tay. Vừa.
2. **Nhấn từ**: thêm `Captions.emphasis` (danh sách từ/regex → màu accent, phóng 115%, có thể kèm `marker`) và tự nhấn
   số liệu (regex chữ số). Dễ–vừa.
3. **Cường độ karaoke** `energy: high|medium|low` → phóng 1.15 / 1.08 / 1.03, pop 0.08–0.12s, màu accent hoặc trắng. Dễ.
4. Graphic **`marker`** (highlight / circle / underline) vẽ bằng ASS: dải màu nghiêng + `\clip` mở dần với
   `accel 0.45` (đã thử — xem ghi chú công thức ffmpeg/ASS). Vừa.
5. Mặc định vị trí phụ đề dọc ≈ y 0.64–0.70 khi có mặt người ở giữa dưới; luôn kiểm không che mặt bằng khung lưới. Dễ.
