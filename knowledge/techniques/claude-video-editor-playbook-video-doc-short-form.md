---
title: claude-video-editor: Playbook video dọc short-form
category: techniques
tags: [claude-video-editor, short-form, tiktok, reels, shorts, talking head, split screen, jaw-dropper, karaoke, nhịp]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/short-form-video/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/captions.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/audio-reactive.md
---
# claude-video-editor: Playbook video dọc short-form

Skill `short-form-video` chắt từ "May Shorts 19 iteration autopsy (v1 → v4)": video 1080×1920, 10–30s, **mặt người
nói + cảnh motion graphics chồng lên + phụ đề karaoke**. Đây là phần gần nhất với nhu cầu TikTok/Reels của vedit.

## 1. 11 luật chất lượng (chạy khi đang dựng, không phải sau)

1. **Không khung chết**: mỗi 100ms có ít nhất một phần tử đang chuyển động; entrance đầu tiên lệch 0.1–0.3s.
2. **Payoff giữ ≥ 1s** (lý tưởng 1.5s) — "Budget scenes by reveal time, not total time."
3. **Mặt người là nhân vật**: grade + Ken Burns + vignette hai bên.
4. **Không đường nối cứng** khi chia đôi khung (feather + đường quét).
5. **Một "jaw-dropper" mỗi 5 giây**: chữ đập (slam), glitch/tách màu, whip-pan, cú đập khớp âm thanh. Thiếu nó video
   thành "labeled talking head — correct but forgettable".
6. **Phản ứng theo âm thanh**: chữ 3–6% scale, nền 10–30%.
7. **Xoay vòng kiểu chuyển cảnh**: không hai transition liền nhau cùng kiểu — "Six hard cuts in a row is the #1 tell
   for AI editing." (áp cho chuyển **cảnh/đoạn**, không phải jump cut trong một câu nói — nhận định).
8. **Phụ đề phải "nổ", không lịch sự**: viền chữ thay vì nền pill; phóng + đổi màu từ đang đọc.
9. **Chuyển động suốt cảnh**: entrance xong sớm thì thêm chuyển động phụ (gạch chân quét, dấu tick bật, thẻ trôi nhẹ,
   glow dao động).
10. **Nền là một lớp, không phải một màu**: radial + noise + hạt + vignette tối thiểu.
11. **Chữ đập/con dấu đáp SAU khi mục tiêu đã hiện đủ**: `stamp_t ≥ target_visible_t + 0.10–0.25s` (target_visible
    = lúc **kết thúc** entrance). Ví dụ lỗi: "KILLED" đập ở 0.46s trong khi "CHATGPT" 0.66s mới hiện → mất câu đùa.

## 2. Bố cục "mặt người" cho nguồn ngang trong khung dọc

Hai chế độ (video nguồn 1920×1080 đặt trong wrapper, animate wrapper chứ không animate `<video>`):
- **BOTTOM**: video ngang chiếm nửa dưới, nửa trên để chữ/đồ hoạ. Mặc định `{x:0, y:1136, scale:0.5625}` (vừa khít
  ngang) để lại khoảng trống hai bên người nói → khuyên `{x:-180, y:1110, scale:0.75}` (cắt 180px mỗi bên); nguồn
  quay chặt dùng 0.65, quay rộng 0.80. **Xem thử 1 khung trước khi chốt.**
- **FULLSCREEN**: crop phủ kín `{x:-1166.5, y:0, scale:1.7778}`.
- Đổi chế độ bằng tween `expo.inOut` 0.32s, bắt đầu **0.15s trước** nội dung cảnh mới; với chuyển đổi "hero":
  0.45–0.55s, bắt đầu sớm 0.25–0.30s **và** đồng thời mờ + blur(6px) panel cảnh cũ trong 0.20–0.25s — "Three
  simultaneous changes = 'a real editor edited this.' Any one alone = rigid."
- "A face that snaps modes instantly is the single most jarring frame in a vertical video."

**Grade mặt**: CSS `contrast(1.08) saturate(1.08) brightness(0.97)` + Ken Burns **1.00 → 1.025** suốt video (linear)
+ vignette hai bên để mặt "chìm" vào nền.
**Đường nối** (khi nửa dưới là video): dải gradient 60–100px tại y=960 + đường quét 2px màu accent có glow nhẹ.

## 3. Đồng bộ âm thanh

"Audio is source of truth": cắt audio trước (bỏ take hỏng, khoảng lặng), đo độ dài bằng `ffprobe`, transcribe bản
**đã cắt**; mọi mốc theo edited-time. Phụ đề karaoke: Montserrat 900, 46–58px (khung rộng 1080), trắng; từ đang đọc
phóng 1.08 + đổi màu accent, pop 0.08–0.12s; viền bằng nhiều lớp `text-shadow` (không dùng `-webkit-text-stroke`).
"Captions should feel like graffiti on the frame, not a subtitle track."

## 4. Bài học từ bản v1 → v2 (may-shorts-18)

1. Logic tiết lộ quan trọng hơn khớp chữ (luật 11).
2. Đừng giữ scale mặc định của BOTTOM khi người nói chiếm < 70% khung nguồn.
3. Chuyển chế độ mặt: ba thay đổi cùng lúc (dài hơn, sớm hơn, cảnh cũ mờ + blur).
4. **Cảnh 3–5 của video 15–20s** (đoạn giữa, sụt chú ý nhất) dùng hình "mang thông tin" (đếm số, thanh đua, lưới
   chớp đỏ lần lượt, sparkline vẽ dần) thay cho hình trang trí — "Data-feel scenes feel like evidence."

## 5. Cổng kiểm tra bắt buộc

Lint → render nháp → trích 8–15 khung **đúng từng từ được nói** → Read mọi PNG (mặt không bị cắt, đúng chế độ mặt,
phụ đề đúng brand/không tràn, không khung trống) → sửa → render chuẩn → soi lại 3–4 khung.

## 6. Không làm

Animate kích thước `<video>` (đứng hình) · `repeat: -1` · `Math.random()` · `<br>` trong phụ đề · bỏ qua cổng kiểm
khung · trộn original-time với edited-time · nền phẳng một màu · cắt cứng giữa các cảnh đồ hoạ · phụ đề "lịch sự" ·
để mặt người đứng yên.

## Áp dụng vào vedit

**Đã có**: `fit: cover/blur/contain` + `focus_x`; zoom Ken Burns per clip (`zoom`, `zoom_amount` ≥ 0.02); karaoke
110% + màu highlight; punch/shake; ghi chú "Tư duy dựng sáng tạo" có mật độ sự kiện 1.5–3s.

**Còn thiếu**: bố cục chia đôi / mặt người nửa dưới; chuyển chế độ mặt có easing; luật "jaw-dropper mỗi 5s" và "stamp
sau mục tiêu" chưa thành quy tắc kiểm được; Ken Burns hiện dùng `zoompan` bị **giật bậc thang** ở zoom chậm (đo:
61/89 khung đứng yên, nhảy ~0.9px, 13 lần lùi với 1.00→1.025 trong 3s); phụ đề karaoke chưa có pop thời gian/viền
nhiều lớp.

**Đề xuất (ưu tiên)**:
1. **Ken Burns mượt**: zoom chậm (`zoom` in/out) render bằng `perspective` (interpolation cubic, eval=frame) — đo được
   bước 0.04–0.12px/khung, không giật; chậm hơn zoompan ~7 lần nên chỉ dùng cho zoom chậm; punch nhanh giữ zoompan.
   Sau đó mặc định zoom 0.02–0.03 cho clip talking-head dài > 2s. Dễ–vừa.
2. **Luật kiểm được trong `vedit qa`**: ≥ 1 "jaw-dropper" (punch mạnh / flash / chữ `bounce` lớn / transition whip /
   sparkles) mỗi 5s; đồ hoạ "stamp" phải bắt đầu ≥ 0.1s sau khi chữ mục tiêu xong entrance; không 2 transition liền
   nhau cùng `type`. Dễ.
3. **Layout chia đôi** cho nguồn ngang: `Clip.layout = "split_bottom"` (video scale ~0.75 bề ngang, neo đáy, nửa trên
   là nền mờ/màu + chữ) và chuyển chế độ có easing 0.3–0.5s. Khó–vừa.
4. **Grade mặt người** gợi ý: `eq=contrast=1.08:saturation=1.08` + giảm sáng ~3% (xấp xỉ CSS brightness 0.97) + vignette
   nhẹ — làm preset `look: talking_head`. Dễ.
5. Phụ đề karaoke: pop từ đang đọc 0.08–0.12s (`\t(0,100,\fscx108\fscy108)`), viền dày + bóng mềm thay cho box. Dễ.
