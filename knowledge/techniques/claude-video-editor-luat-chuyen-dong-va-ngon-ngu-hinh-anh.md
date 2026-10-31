---
title: claude-video-editor: Luật chuyển động và ngôn ngữ hình ảnh
category: techniques
tags: [claude-video-editor, motion design, easing, nhịp, palette, style, callback, motion philosophy, sáng tạo]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/MOTION_PHILOSOPHY.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/motion-principles.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/house-style.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/visual-styles.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/data-in-motion.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/skills/manim-video/references/visual-design.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/skills/manim-video/references/production-quality.md
  - https://github.com/assafkip/claude-video-editor/blob/master/examples/promo/index.html
---
# claude-video-editor: Luật chuyển động và ngôn ngữ hình ảnh

> Bối cảnh: MOTION_PHILOSOPHY là bản "mổ xẻ" một quảng cáo motion graphics 30s (1920×1080, 30fps, 900 khung) —
> **thuần đồ hoạ**, không phải footage quay thật. Áp vào video người dùng quay (nấu ăn, vlog) thì lấy **tinh thần**
> (mỗi beat một ý, có nghĩa, có callback, chuyển động có chủ đích), đừng chép nguyên (nền đen 90%, chữ chrome).

## 1. 11 luật (MOTION_PHILOSOPHY §0, rút gọn)

1. **Một ý mỗi beat, cắt nhanh** — cảnh trung bình ~1.5s; cảnh nói hai điều thì tách đôi.
2. Nền tối là canvas, khoảng trống là thiết kế; màu phải "kiếm" được chỗ đứng bằng ý nghĩa.
3. "Light is the brand, not color" — gradient chrome, quầng sáng, vignette.
4. **Camera không bao giờ ngủ** — kể cả khung "tĩnh" cũng có trôi nhẹ, hạt bay, vignette thở. "Static = death."
5. **Motion blur là tính năng** — mọi transition có vệt/nhoè để vừa tạo năng lượng vừa giấu điểm cắt.
6. **Vật ẩn dụ mang nghĩa** — vật xuất hiện lại nhiều lần (đồng xu quay lại 3 lần) = nhận diện, **callback**.
7. **Palette mang biểu tượng**: mỗi màu sở hữu một khái niệm (đỏ = vấn đề cũ, teal = giải pháp...).
8. **Chữ là nhân vật** — phóng 8×, biến hình, nén, phát sáng; chữ gánh ~60% câu chuyện.
9. **Giữ khoảnh khắc anh hùng** — logo ~2s đứng yên, outro 5s+; tốc độ "mua" quyền được tĩnh.
10. Một kết cấu thống nhất xuyên suốt (lưới phối cảnh + dấu `+`), dù gần như vô hình.
11. Timeline phải lấp đầy slot (luật kỹ thuật của HyperFrames).

**"What Would Infinite Do?"** trước khi chốt: cắt cảnh này còn một nửa được không? màu này mang nghĩa gì? camera có
chuyển động trong beat không? motion blur ở đâu? vật này có quay lại sau không? chữ có **phóng** khi xuất hiện hay chỉ
fade ("lowest-effort move")? beat này tóm được trong 2 từ không? kết cấu thống nhất là gì? người xem nghỉ ở đâu?

## 2. Nguyên tắc chuyển động (motion-principles.md)

- **Easing là cảm xúc**: "The transition is the verb. The easing is the adverb." Cùng một cú trượt: `expo.out` = tự
  tin, `sine.inOut` = mơ màng, `elastic.out` = vui nhộn.
- **Hướng ease**: vào khung dùng `.out` (nhanh rồi chậm); rời khung dùng `.in`; di chuyển giữa hai vị trí dùng
  `.inOut`. Không bao giờ `linear` cho chuyển động ("looks robotic") — trừ camera trôi kiểu tài liệu.
- **Tốc độ = trọng lượng**: 0.15–0.3s năng lượng/khẩn; 0.3–0.5s chuyên nghiệp; 0.5–0.8s trang trọng/xa xỉ;
  0.8–2.0s điện ảnh/cảm xúc. Cảnh chậm nhất nên chậm **gấp 3** cảnh nhanh nhất.
- **Đa dạng**: không quá 2 tween độc lập cùng một ease trong một cảnh; ≥ 3 ease khác nhau mỗi cảnh; đổi hướng vào
  (trái, phải, scale, chỉ opacity, letter-spacing); mỗi cảnh một nhịp stagger riêng; đừng zoom nền ở mọi cảnh —
  "Stillness after motion is powerful."
- **Không bắt đầu ở t=0**: lệch 0.1–0.3s, nếu không sẽ như jump cut.
- **Cấu trúc cảnh build / breathe / resolve**: 0–30% vào lần lượt; 30–70% sống với **một** chuyển động nền;
  70–100% kết dứt khoát, thoát nhanh hơn vào (vào 0.4s, ra 0.25s).
- **Vũ đạo = thứ bậc**: thứ chuyển động trước được coi là quan trọng nhất; stagger theo tầm quan trọng; tổng chuỗi
  stagger < 500ms; vào chồng lên nhau, đừng chờ xong mới vào.
- **Không lộ hai thứ mới cùng lúc**: "the eye can't track two new things at once. One thing, pause, next thing."
- **Payoff timing**: lấy mốc từ "payoff" trong lời nói, bắt đầu animation sớm đúng bằng thời lượng reveal để **khung
  đáp đất trùng chữ được nói**; với punchline, cho hình đi trước tiếng ~0.2s "it reads as inevitable".
- Animation minh hoạ theo lời: sàn 3s, thẻ đơn giản 5–7s, sơ đồ phức tạp 8–14s; accent theo beat 0.5–2s; **giữ khung
  cuối ≥ 1s**; overlay trên lời đọc ≥ thời lượng câu + 1s.

## 3. Bố cục khung hình video

- **≥ 2 tiêu điểm** mỗi cảnh; **lấp khung** (chữ hero 60–80% bề ngang); **≥ 3 lớp**: nền (glow, chữ khổng lồ mờ,
  panel màu) · nội dung · điểm nhấn (gạch, nhãn, thanh dữ liệu).
- Nền không trống: "Pure solid #000 reads as 'nothing loaded'". Ý tưởng lớp nền 2–5 thứ/cảnh: glow tỏa tròn thở,
  chữ ma 3–8% opacity trôi chậm, đường kẻ mảnh, grain, hình học, đồ trang trí theo chủ đề — đều có chuyển động chậm.
- Neo vào mép (trái/trên hoặc phải/dưới), chia vùng; "centered-and-floating is a web pattern".
- Lớp opacity (Manim): chính 1.0, ngữ cảnh 0.3–0.4, cấu trúc 0.15; tối đa ~6 phần tử hoạt động cùng lúc; chừa ≥ 15%
  khung trống.

## 4. Palette & style có tên

- 1 nền, 1 chữ, 1 accent khai báo **trước**; neutral pha về sắc accent; không bịa màu cho từng phần tử.
- Sáng/tối theo nội dung: đồ ăn, sức khoẻ, trẻ em → sáng; công nghệ, điện ảnh, tài chính → tối.
- 8 style có tên (visual-styles.md) — chọn theo **cảm giác người xem**, kèm chữ ký easing:

| Style | Mood | Hợp với | Easing ký hiệu |
|---|---|---|---|
| Swiss Pulse | chính xác, lạnh | dữ liệu, SaaS | `expo.out`, `power4.out` — vào nhanh, khớp lưới |
| Velvet Standard | sang, vượt thời gian | cao cấp, keynote | `sine.inOut`, `power1` — lướt, giữ lâu |
| Deconstructed | thô, công nghiệp | tin công nghệ, punk | `back.out(2.5)`, `steps(8)`, `elastic` |
| Maximalist Type | ồn, động | ra mắt lớn, hype | `expo.out`, `back.out(1.8)` — chữ là hình, 50–80% khung |
| Data Drift | tương lai | AI/ML | `sine.inOut`, `power2.out` |
| Soft Signal | ấm, thân mật | wellness, câu chuyện cá nhân | `sine.inOut` — trôi, không "snap" |
| Folk Frequency | văn hoá, rực rỡ | **đồ ăn**, cộng đồng, lễ hội | `back.out(1.6)`, `elastic.out(1,0.5)` — nảy, xoay vui |
| Shadow Cut | tối, điện ảnh | tiết lộ kịch tính | `power4.in` ra, `power3.out` vào; khoảng lặng trước cú đánh |

Tự tạo style: đặt tên → palette 2–3 màu hex → 1 họ font 2 độ đậm → luật chuyển động → transition → 2–3 điều tránh.

## 5. Dữ liệu trong chuyển động

Con số cần "trọng lượng thị giác" (thanh đầy dần, vòng tiến trình, hình tỉ lệ); số liên tiếp cùng khái niệm thì giữ
cùng không gian, chỉ đổi giá trị; tránh pie chart, biểu đồ nhiều trục, dashboard 6 ô, gridline/legend. Ở giữa video
(chỗ người xem dễ bỏ), **cảnh "cảm giác dữ liệu"** (đếm số, thanh chạy, lưới sáng lần lượt) giữ chân tốt hơn cảnh
trang trí (bài học may-shorts-18 trong short-form-video).

## 6. Anti-pattern

Chữ căn giữa đứng yên chỉ fade · cắt cứng không cầu nối ở chuyển đoạn lớn · chữ trắng phẳng trên nền đen phẳng ·
≥ 6 màu · không callback · outro kết thúc ngay beat cuối · cảnh nói hai điều · nền tĩnh hoàn toàn · không render nháp
rồi xem khung.

## Áp dụng vào vedit

**Đã có**: ghi chú "Tư duy dựng sáng tạo" (hook có chuyển động, mật độ sự kiện 1.5–3s, hệ thống thiết kế thống nhất,
kiềm chế); vedit có 10 animation chữ, đồ hoạ vector, punch/shake, look, vignette/grain.

**Còn thiếu**: easing (mọi `\t`/`\move` hiện tuyến tính, trừ pop/bounce mô phỏng overshoot); khái niệm **màu có nghĩa**
và **callback**; bảng "style có tên" để Agent 2 chọn nhất quán; quy tắc payoff timing & "hai thứ mới không cùng lúc";
phân lớp nền/nội dung/nhấn cho video không phải motion graphics thuần.

**Đề xuất (ưu tiên)**:
1. **Easing trong `vedit/ass.py`**: thêm `accel` vào `\t` (accel ≈ 0.4–0.5 ≈ ease-out cho mọi entry; > 1 cho exit) và
   thay `\move` bằng chuỗi event theo khung tính ease_out_cubic (đã kiểm chứng — xem ghi chú công thức ffmpeg/ASS).
   Dễ–vừa.
2. Thêm trường **`style`** vào EditPlan/strategy (vd `folk_frequency`, `soft_signal`, `swiss_pulse`, `shadow_cut`)
   ánh xạ sang bộ mặc định: palette, font, animation vào/ra, transition chính, cường độ punch. Vừa.
3. Prompt Agent 2: mỗi beat **một ý**; ít nhất **1 callback** (chữ/đồ hoạ/vật lặp lại ở cuối); palette ≤ 3–5 màu có
   **ý nghĩa ghi rõ**; payoff đồ hoạ đáp đúng chữ/tiếng động; không lộ 2 phần tử mới cùng khung hình. Dễ.
4. Agent 3 chạy "What Would Infinite Do?" phiên bản vedit (10 câu) trước render final. Dễ.
