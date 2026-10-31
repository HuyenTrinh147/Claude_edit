---
title: claude-video-editor: Brief, storyboard từng beat và kịch bản
category: scripting
tags: [claude-video-editor, storyboard, brief, design.md, kịch bản, hook, beat, động từ chuyển động, callback, cấu trúc]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/references/storyboard-template.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/references/style-intake.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-2-design.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-3-script.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-4-storyboard.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-5-vo.md
  - https://github.com/assafkip/claude-video-editor/blob/master/examples/promo/DESIGN.md
  - https://github.com/assafkip/claude-video-editor/blob/master/examples/promo/SCRIPT.md
  - https://github.com/assafkip/claude-video-editor/blob/master/examples/promo/STORYBOARD.md
  - https://github.com/assafkip/claude-video-editor/blob/master/recipes/01-launch-video.md
  - https://github.com/assafkip/claude-video-editor/blob/master/recipes/03-website-to-promo.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/skills/manim-video/references/scene-planning.md
---
# claude-video-editor: Brief, storyboard từng beat và kịch bản

Chuỗi tài liệu trước khi dựng: **BRIEF → DESIGN → SCRIPT → STORYBOARD**, mỗi file là cổng cho bước sau.
"The storyboard is the creative north star" — viết như đang brief cho một motion designer chưa từng thấy sản phẩm.

## 1. DESIGN.md (bảng nhận diện, ≤ 100 dòng)

6 mục: **Overview** (3–4 câu mô tả thực tế) · **Colors** (5–10 hex có vai trò, chép đúng giá trị) · **Typography**
(họ font, độ đậm, vai trò) · **Elevation** (viền / bóng / kính mờ / đổi màu phẳng) · **Components** (gọi tên cụ thể:
"Cinematic Accordion" chứ không phải "Cards") · **Do's and Don'ts** (3–5 mỗi loại, rút từ thứ thương hiệu thực sự làm).
Biến thể tối thiểu (khi không có thương hiệu): Style Prompt 1 đoạn + Colors 3–5 hex + Typography 1–2 họ + What NOT to
Do 3–5 điều. Ví dụ thật (`examples/promo/DESIGN.md`): "Cute neo-brutalist paper UI on warm cream… thick ink borders,
hard offset shadows, yellow marker highlights"; What NOT: "No gradients, no glassmorphism, no dark mode · No corporate
blue, no Inter/Roboto · No floaty 2s+ eases, no linear easing · No element appears fully formed".

## 2. SCRIPT — quy tắc viết lời

- Kịch bản là xương sống: **thời lượng cảnh lấy từ lời**, không đoán. Viết lời trước storyboard.
- Nhịp tiếng Anh: **2.5 từ/giây** (15s ≈ 37 từ; ví dụ 62s dùng ~140 từ = 2.3 từ/s). Kịch bản nên "ngắn hơn video" —
  khoảng lặng giữa câu là tính năng.
- Giọng người, không phải brochure: rút gọn, câu dài–ngắn xen kẽ, đọc to thử.
- Cấu trúc: **Hook → Story → Proof → CTA** (quảng cáo 15s có thể chỉ Hook + Proof + CTA).
- Câu mở đầu tạo căng thẳng/tò mò/bất ngờ trong 3s, **đổi loại hook giữa các video**: tuyên bố táo bạo · câu hỏi khiêu
  khích · tương phản · con số gây sốc (dùng ít). "If the opening is generic … start over."
- TTS đọc nguyên văn → viết số thành chữ ("10x" → "ten times", "API" → "A P I"); hình có thể hiện số chính xác.
- Video autoplay tắt tiếng (X, feed): **kịch bản câm, chữ gánh câu chuyện** — cung truyện cho video sản phẩm:
  **trạng thái vấn đề → bước ngoặt → loạt tiết lộ → zoom vào một chi tiết quan trọng → thẻ CTA**.
  "A zoom reads as product; cuts read as ad." · "One message per video."

## 3. Cấu trúc tổng

- 3 hồi: Hook ≈ **20%** · Thân ≈ **55%** · Payoff + outro ≈ **25%**. Quy tắc bộ ba (3 lợi ích, 3 bề mặt, 3 biểu tượng).
- Ít nhất **một callback** ở hồi 2/3 (vật/chữ/hình quay lại).
- Cung truyện khác (Manim): Discovery (hook → trực giác → hình thức hoá → "aha" → mở rộng) · Problem–Solution
  (vấn đề → thử thất bại → ý then chốt → giải pháp → kết quả) · Comparison · Build-up.
- Loại video (website-to-hyperframes): quảng cáo IG/TikTok 10–15s, 3–4 beat, lời tuỳ chọn · demo 30–60s, 5–8 beat ·
  thông báo tính năng 15–30s, 3–5 beat · brand reel 20–45s, 4–6 beat · teaser 10–20s, 2–4 beat.

## 4. STORYBOARD — mỗi beat là một "thế giới"

Đầu file: format, audio, hướng giọng đọc, style basis + bảng timing (beat · start · dur · file · ý). Mỗi beat:

```
## Beat N — TÊN (start–end, dur) — ý tưởng 1 câu
Concept: 2–3 câu — đang ở "thế giới" nào, ẩn dụ gì, người xem cảm thấy gì
VO cue: câu lời nào chạy trên beat
Visual: mô tả kiểu điện ảnh (pan, zoom, drift, settle), ≥ 5 phần tử, tiền/trung/hậu cảnh
Mood: tham chiếu văn hoá/thiết kế ("Bauhaus color studies", "nice notebook energy")
Assets: file nào, xử lý thế nào (vd ảnh nền full-bleed, zoom chậm 1→1.04 suốt beat)
Choreography: mỗi phần tử một ĐỘNG TỪ
Transition: kiểu + thông số (vd thoát y:-150, blur 30px, 0.33s power2.in)
Depth layers: ≥ 2 lớp · SFX: âm gì, lúc nào
```

Động từ theo năng lượng: **cao** SLAMS, CRASHES, PUNCHES, STAMPS, SHATTERS · **vừa** CASCADE, SLIDES, DROPS, FILLS,
DRAWS · **thấp** types on, FLOATS, morphs, COUNTS UP, fades in. "Every element gets a verb. If you can't name the verb,
the element is not yet designed."

Mô tả tầm thường vs xuất sắc: "Dark navy background. '$1.9T' in white, 280px. Logo top-left." ↔ "Camera is already
mid-flight over a vast dark canvas… '$1.9T' SLAMS into existence with such force the wave ripples in response. This
isn't a slide — it's a moment." Viết bản thứ hai trước, rồi mới tính pixel.

Quy định thêm (storyboard-template): beat ≤ 2s trừ beat hero/outro (cho motion graphics nhịp nhanh) · mỗi transition có
tên + thời lượng · mỗi beat nêu ease vào/ra (đừng để mọi beat là `power2.out`) · outro giữ 4–6s (cho promo; với
TikTok lặp vòng cần cân nhắc — nhận định) · nền xuyên suốt.

## 5. Kiểm kê tài sản (asset audit)

Bảng: tài sản · loại · gán cho beat · vai trò (hoặc SKIP + lý do). Tối thiểu: ≥ 50% ảnh sản phẩm/hero được dùng; logo
ở beat đầu **và** cuối; hình đặc trưng nhất của thương hiệu phải xuất hiện; **tối đa 2 beat liên tiếp chỉ có chữ**;
beat mở đầu phải có hình, không chỉ chữ. Mục tiêu 8–10 phần tử thị giác mỗi beat cho promo đồ hoạ.

## 6. Khoá thời gian bằng giọng đọc

Giọng đọc trước → transcribe → beat.start = mốc từ đầu tiên, beat.end = mốc từ cuối + **0.3–0.5s** thở; cập nhật
storyboard bằng mốc thật. Ranh giới beat rơi đúng **đầu từ** (hard cut theo lời). Thử 2–3 giọng với câu đầu;
"Never use the first voice you find."

## Áp dụng vào vedit

**Đã có**: `ScriptDoc` (tiêu đề + 3–5 phương án, hook + phương án, concept, insight trend có bằng chứng, từ khoá,
hashtag, cảnh với purpose/visual/voiceover/on_screen_text/edit_notes, nhạc, CTA); ghi chú hook 3 giây và cấu trúc
15–60s.

**Còn thiếu**: cảnh chỉ mô tả "cái gì", thiếu **cảm giác/ẩn dụ**, **động từ chuyển động**, **transition + lý do**,
**lớp chiều sâu**, **SFX cue**; không có style profile/DESIGN; không có asset audit (khoảnh khắc nguồn nào dùng/bỏ);
không bắt buộc callback; nhịp lời tiếng Việt chưa có số chuẩn.

**Đề xuất (ưu tiên)**:
1. Mở rộng `ScriptScene`: `concept` (cảm giác/ẩn dụ), `choreography` (mỗi phần tử một động từ: "chữ ĐẬP vào",
   "callout VẼ ra", "số ĐẾM lên"), `transition` (kiểu + lý do), `sfx`, `layers`. Agent 2 viết bản "xuất sắc" trước
   rồi mới quy ra EditPlan. Vừa.
2. Thêm `style_profile` vào script (palette ≤ 5 màu có nghĩa, 1–2 font hỗ trợ tiếng Việt, cảm giác chuyển động, 3–5
   điều không làm) — dùng chung cho Agent 3. Dễ.
3. **Asset audit** từ `analysis.json`: bảng mốc nguồn (cảnh đẹp nhất, hành động, thành phẩm) → beat/SKIP; quy tắc
   "beat mở đầu phải là hình hành động mạnh nhất, không phải chữ tĩnh". Dễ.
4. Bắt buộc **1 callback** và cấu trúc 20/55/25 trong prompt; đổi loại hook giữa các video của cùng người dùng (ghi
   vào `project.md`). Dễ.
5. Nhịp lời tiếng Việt: **đo số âm tiết/giây từ transcript** của chính người nói thay vì áp 2.5 từ/s tiếng Anh. Dễ.
