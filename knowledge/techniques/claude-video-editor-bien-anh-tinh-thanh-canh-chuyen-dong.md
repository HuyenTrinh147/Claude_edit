---
title: claude-video-editor: Biến ảnh tĩnh thành cảnh chuyển động
category: techniques
tags: [claude-video-editor, ảnh tĩnh, ken burns, push-in, drift, khí quyển, animate stills, manifest, explainer]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/recipes/04-animate-stills.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/generate-footage/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/generate-footage/scripts/build_scenes.py
  - https://github.com/assafkip/claude-video-editor/blob/master/templates/animate-stills/manifest.json
  - https://github.com/assafkip/claude-video-editor/blob/master/templates/animate-stills/index.html
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/rca/rca-generate-footage-animation-2026-06-11.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-6-build.md
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/MOTION_PHILOSOPHY.md
---
# claude-video-editor: Biến ảnh tĩnh thành cảnh chuyển động

Kỹ thuật Ken Burns điều khiển bằng manifest — "the deterministic motion path": không model sinh video, không dịch vụ
ngoài, render giống hệt mỗi lần. Ra đời sau RCA ngày 2026-06-11 khi actor image-to-video thuê ngoài chết giữa chừng.

## 1. Quy trình

1. **Giọng trước**: tạo lời đọc → transcribe → ranh giới câu = cửa sổ cảnh.
2. **Một ảnh mỗi cảnh** từ bất kỳ nguồn nào (ảnh AI, ảnh chụp màn hình, ảnh thật, HTML tự render). Khoá **một** mô tả
   style cho mọi ảnh; kiểm tra từng ảnh (chữ lỗi, watermark, sai thời đại, mặt cận cảnh dễ "trôi", sai palette) — một
   ảnh lệch style là tạo lại, không giữ. Kiểm **magic bytes** (có công cụ trả JPEG mang đuôi .png). Không dùng IP có tên
   hay gương mặt người thật còn sống cho ảnh sinh để đăng công khai.
3. Viết `manifest.json` → `build_scenes.py` sinh lớp cảnh + timeline (chỉ sửa trong vùng marker, phần ngoài marker
   người dùng tự chỉnh vẫn giữ khi build lại) → lint → render → mux giọng → kiểm chuyển động + âm lượng + contact sheet.

```json
{"size": [1080, 1080], "fps": 30,
 "scenes": [{"n": 1, "image": "assets/stills/s1.png", "window": [0.0, 6.0], "move": "push-in", "atmosphere": "mist"},
            {"n": 2, "image": "assets/stills/s2.png", "window": [6.0, 12.0], "move": "drift-left", "atmosphere": "light"}],
 "captions": [{"text": "Phrase-level caption.", "at": [0.6, 5.4]}]}
```

Ràng buộc: `n` từ 1, liên tục; cửa sổ nối nhau (hở ≤ 0.2s, không chồng); ảnh phải là PNG thật.

## 2. Ngôn ngữ chuyển động máy (giá trị trong `build_scenes.py`)

Tuyến tính suốt cả cửa sổ cảnh — "documentary register, no easing tricks":

| move | từ → đến |
|---|---|
| `push-in` | scale 1.03 → 1.15 |
| `pull-back` | scale 1.15 → 1.03 |
| `drift-left` | scale 1.08, xPercent +2.2 → −2.2 |
| `drift-right` | scale 1.08, xPercent −2.2 → +2.2 |
| `rise` | scale 1.08, yPercent +2.2 → −2.2 |
| `hold` | scale 1.04 → 1.065 (vẫn "thở", không đứng yên) |

Cảnh xếp chồng theo z và **fade in 0.45s** (`power1.inOut`) ở đầu cửa sổ — không cần dàn dựng fade out. Một "sentinel"
ẩn giữ tổng thời lượng bằng cuối cửa sổ cuối.

## 3. Lớp khí quyển (một lớp mỗi cảnh) + vignette chung

- `mist`: 2 radial-gradient trắng xám (opacity 0.34 & 0.26) blur 14px, trôi ngang xPercent −6 → +6 suốt cảnh.
- `rain`: sọc chéo 12° (`repeating-linear-gradient`, 7px trong suốt / 2px trắng 20%), opacity 0.5, cuộn nền 0 → 900px.
- `light`: đốm sáng ấm radial `rgba(255,236,200,0.5)`, `mix-blend-mode: screen`, quét xPercent −25 → +25, opacity
  0 → 0.55 (`sine.inOut`).
- **Vignette chung** `radial-gradient(78% 78% at 50% 46%, transparent 58%, rgba(8,8,10,0.55))` — "unifies mixed-source
  stills" và giúp phụ đề dễ đọc.
- Phụ đề cấp cụm từ, fade 0.3s vào/ra; **chớp trắng 0.28s ở các bước ngoặt câu chuyện**, crossfade mềm ở chỗ khác.

## 4. Kiểm tra & bẫy

- `motion_check.py` trên cảnh có chuyển động ít nhất: trung vị độ khác > 3 = có chuyển động thật.
- "Low-detail stills hide motion": push-in chậm trên gradient mịn có thể đo ~0 dù render đúng → ưu tiên ảnh nhiều chi
  tiết/kết cấu cho chuyển động chậm.
- Ảnh không bao giờ để phẳng (website-to-hyperframes): nghiêng phối cảnh (`rotationY −8°` + bóng), zoom chậm 1 → 1.03–1.04,
  khung thiết bị (laptop/điện thoại), tách phần UI trôi ở độ sâu khác (parallax), cuộn trong khung nhìn.
  "A still image on a still background is a JPEG with a progress bar."

## Áp dụng vào vedit

**Đã có**: clip ảnh (`duration`), `zoom: in|out` + `zoom_amount` (0.02–0.6), `fit: cover/contain/blur`, `look.vignette`,
đồ hoạ `flash` (chớp), `sparkles`.

**Còn thiếu**: chỉ zoom vào tâm (không drift/rise, không tâm lệch); zoompan bị giật ở tốc độ chậm (xem ghi chú công
thức ffmpeg/ASS); không có lớp khí quyển; không kiểm ảnh nguồn (định dạng, độ chi tiết).

**Đề xuất (ưu tiên)**:
1. Mở rộng `Clip.zoom` thành `move: push_in | pull_back | drift_left | drift_right | rise | hold` với đúng các giá trị
   mục 2, render bằng `perspective` subpixel (dịch tâm theo `focus_x/focus_y`). Vừa.
2. Thêm `Look`/graphic **`atmosphere: mist | light | rain`** vẽ bằng ASS (vệt sáng blur lớn trôi chậm, sọc mưa chéo) với
   opacity như mục 3. Vừa.
3. Khi video là chuỗi ảnh: mặc định vignette ~0.3 để thống nhất ảnh khác nguồn; `flash` 0.28s ở bước ngoặt. Dễ.
4. `vedit validate` kiểm ảnh: định dạng thật (magic bytes), kích thước đủ cho zoom (≥ canvas × (1+zoom_amount)). Dễ.
