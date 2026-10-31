---
title: claude-video-editor: Chọn chuyển cảnh theo ý nghĩa
category: techniques
tags: [claude-video-editor, transition, chuyển cảnh, whip pan, motion blur, xfade, năng lượng, nhịp]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/transitions.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/transitions/catalog.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/transitions/css-dissolve.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/transitions/css-blur.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/transitions/css-light.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/transitions/css-scale.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/transitions/css-push.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/transitions/css-cover.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/transitions/css-distortion.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/techniques.md
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/MOTION_PHILOSOPHY.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/short-form-video/SKILL.md
---
# claude-video-editor: Chọn chuyển cảnh theo ý nghĩa

"A transition tells the viewer how two scenes relate." Chọn theo **điều nội dung đang làm về mặt cảm xúc**, không
theo cái nào trông hay.

## 1. Nghĩa của từng loại

- **Crossfade** = "chuyện này tiếp diễn". **Cắt cứng** = "tỉnh dậy!" / đổi giọng điệu. **Dissolve chậm** = "trôi
  cùng tôi". **Push/slide** = "ý tiếp theo". **Blur crossfade** = mơ màng.
- "You crossfade everything. Use hard cuts for disruption and register shifts." (guardrail cho LLM)
- **Một kiểu chính** cho 60–70% lần đổi cảnh + **1–2 kiểu nhấn**; "Never use a different transition for every scene."
  Kết hợp với luật short-form: **không hai transition liền nhau giống hệt** (xen kẽ chính/nhấn).

## 2. Năng lượng → transition

| Năng lượng | Kiểu chính (CSS) | Nhấn | Thời lượng | Easing |
|---|---|---|---|---|
| Êm (wellness, thương hiệu, xa xỉ) | blur crossfade, focus pull | light leak, circle iris | 0.5–0.8s | `sine.inOut`, `power1` |
| Vừa (doanh nghiệp, giải thích) | push slide, khối màu so le | squeeze, vertical push | 0.3–0.5s | `power2`, `power3` |
| Cao (promo, thể thao, nhạc) | zoom through, overexposure | khối so le, gravity drop | 0.15–0.3s | `power4`, `expo` |

Độ nhoè theo năng lượng: êm 20–30px, 0.8–1.2s, giữ đỉnh 0.3–0.5s · vừa 8–15px, 0.4–0.6s, giữ 0.1–0.2s ·
cao 3–6px, 0.2–0.3s, không giữ. Preset: snappy 0.2s · smooth 0.4s · gentle 0.6s · dramatic 0.5s · instant 0.15s ·
luxe 0.7s.

## 3. Theo vị trí trong câu chuyện

| Vị trí | Dùng | Lý do |
|---|---|---|
| Mở đầu | transition đặc trưng nhất, 0.4–0.6s | đặt ngôn ngữ hình ảnh cho cả video |
| Giữa các ý liên quan | kiểu chính, ~0.3s | không làm xao nhãng |
| Đổi chủ đề | kiểu khác hẳn (khối so le, shutter, squeeze) | báo "phần mới" |
| Cao trào / reveal | kiểu nhấn mạnh nhất, nhanh nhất | phần thưởng |
| Hạ nhiệt | êm lại (blur crossfade), 0.5–0.7s | cho người xem thở |
| Outro | chậm nhất, đơn giản nhất (crossfade, dip to black) 0.6–1.0s | khép lại, không thêm năng lượng mới |

## 4. Motion blur giấu điểm cắt (MOTION_PHILOSOPHY)

- "Hard cuts feel cheap; whip-streaks feel expensive." **Light-streak whip**: thanh gradient trắng→trong suốt, rộng
  ~40% khung, cao 8px, blur 6px, quét ngang 0.3–0.4s (`power3.in`); cảnh mới bắt đầu **đúng đỉnh vệt** (khoảng giữa
  thời lượng) — độ sáng che điểm cắt. "Hard cut on action — when a whip-streak peaks — that's the moment to cut."
- **Velocity-matched**: cảnh cũ thoát với ease tăng tốc (`power2.in`) + blur tăng; cảnh mới vào với ease giảm tốc
  (`power2.out`) + blur giảm; điểm nhanh nhất của hai đường cong gặp nhau ở điểm cắt → mắt thấy một chuyển động liên
  tục. Thông số mẫu: thoát `y:-150, blur 30px, 0.33s power2.in` → vào `y:150→0, blur 30→0, 1.0s power2.out`; whip
  ngang: thoát `x:-400, blur 24px, 0.3s power3.in` → vào `x:400→0, 0.3s power3.out`. Sai lệch vận tốc ≤ ~5%.
- **Flash-through-white** cho ngắt hồi lớn; **overexposure**: tăng `brightness` cảnh cũ 1.5→3, phủ trắng, đổi cảnh ở
  đỉnh trắng, trắng lùi 0.35s.
- **Recolor không cắt**: cùng bố cục, đổi palette (biến CSS) 0.6s — "one of the highest-value moves": hai ý liên quan
  mà không cần cảnh mới.

## 5. Luật khi có nhiều cảnh (HyperFrames)

1. Luôn có transition giữa các cảnh đồ hoạ; 2. mọi phần tử có entrance; 3. **cấm exit animation trước transition**
— "The transition IS the exit" (cảnh cũ phải còn đầy đủ khi transition bắt đầu); 4. chỉ cảnh cuối được fade out.
Tránh: transition tạo hoa văn hình học lặp (lưới ô, tổ ong, chấm đều) — "look cheap"; nhiễu hữu cơ thì được.

## Áp dụng vào vedit

**Đã có**: `Clip.transition` với 22 kiểu xfade (fade, fadeblack/white, dissolve, wipe*, slide*, smooth*, circleopen/
close, radial, zoomin, pixelize, hblur) + `acrossfade`; đồ hoạ `flash`; SFX `whoosh`; ghi chú cũ khuyên "cắt thẳng là
mặc định, transition tiết chế" — vẫn đúng cho jump cut trong lời nói.

**Còn thiếu**: transition có **motion blur** (whip/zoom-through); vệt sáng quét giấu cắt; quy tắc "kiểu chính + nhấn,
không lặp liền nhau, theo vị trí câu chuyện"; ffmpeg 6.1 còn nhiều kiểu xfade vedit chưa mở (`fadewhite`, `coverleft…`,
`revealleft…`, `squeezeh/v`, `hlwind…`, `fadefast/slow`, `diagtl…`).

**Đề xuất (ưu tiên)**:
1. Thêm transition **`whip_left/right/up/down`** = `xfade=slideleft` (0.2–0.3s) + `dblur=angle=0:radius=40–50` bật
   trong cửa sổ chuyển (đã thử: cho vệt nhoè đúng kiểu whip-pan — lệnh ở ghi chú công thức ffmpeg/ASS) + tự thêm SFX
   `whoosh`. Vừa.
2. Thêm graphic **`streak`** (thanh trắng blur quét ngang 0.35s, đã thử bằng ASS) để "giấu" điểm cắt cứng ở beat
   năng lượng cao. Dễ.
3. Mở thêm các kiểu xfade sẵn có trong ffmpeg 6.1 (`fadewhite`, `coverleft`, `revealleft`, `squeezeh`, `zoomin`…) vào
   schema. Dễ.
4. Prompt Agent 2: chọn **1 kiểu chính + 1–2 kiểu nhấn** theo năng lượng/vị trí (bảng mục 2–3), ghi lý do trong `note`;
   `vedit qa` cảnh báo 2 transition liền nhau cùng kiểu và transition > 0.6s ở video năng lượng cao. Dễ.
