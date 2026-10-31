---
title: claude-video-editor: Vòng tự kiểm tra chất lượng sau render
category: techniques
tags: [claude-video-editor, qa, self-eval, kiểm tra khung hình, wcag, tương phản, dead zone, motion check, điểm cắt]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/README.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/scripts/animation-map.mjs
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/scripts/contrast-report.mjs
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/short-form-video/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/references/build-checklist.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-6-build.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-7-validate.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/generate-footage/scripts/motion_check.py
  - https://github.com/assafkip/claude-video-editor/blob/master/recipes/04-animate-stills.md
---
# claude-video-editor: Vòng tự kiểm tra chất lượng sau render

Nguyên tắc: "**Lint passing ≠ design working. VIEW THE FRAMES.**" và "Only present the preview once the self-eval
passes." Repo có 6 lớp kiểm tra, từ cơ học đến thẩm mỹ.

## 1. Self-eval ở mọi điểm cắt (video-use)

Chạy `timeline_view` trên **bản đã render** (không phải nguồn), cửa sổ **±1.5s quanh mỗi điểm cắt**, soi:
- gián đoạn hình / chớp / nhảy ở điểm cắt;
- **gai sóng âm tại biên** (tiếng bụp lọt qua fade 30ms);
- phụ đề bị overlay che (vi phạm "subtitles LAST");
- overlay lệch vị trí hoặc hiện sai khung (quên dời PTS).
Thêm: **2s đầu, 2s cuối, 2–3 điểm giữa** (đồng nhất màu, phụ đề đọc được, mạch lạc); `ffprobe` độ dài khớp EDL.
Hỏng → sửa → render lại → đánh giá lại; **tối đa 3 vòng**, quá thì báo người dùng.

## 2. Kiểm khung "đúng từng chữ" (short-form-video, make-a-video)

- Chọn **8–15 mốc**, mỗi mốc là **một từ được nói** mà lúc đó một hình cụ thể phải có trên màn — "Not round numbers.
  Not mid-scene. The exact word." Thêm mốc giữa mỗi transition (đỉnh vệt whip, giữa morph).
- `ffmpeg -y -ss <t> -i draft.mp4 -frames:v 1 -q:v 2 frames/t<t>-<nhãn>.png`, rồi **Read từng PNG** ("Do NOT just list
  filenames").
- Mỗi khung xác nhận: hình đúng lúc (không trễ 1s, không sớm) · mặt không bị cắt · chữ đúng palette, đọc được, không
  tràn · không khung trống, không chồng lấn ngoài ý muốn · chữ không ra ngoài khung.
- Sau render final: soi lại 3–4 khung cùng mốc để chắc bản encode chất lượng cao không đổi gì.

## 3. Audit tương phản WCAG (contrast-report.mjs)

Với 10 mốc rải đều: tìm mọi phần tử có chữ, lấy **vành 4px ngay ngoài khung bao chữ**, lấy **trung vị** từng kênh
màu làm nền, trộn màu chữ (nếu có alpha) lên nền, tính tỉ lệ WCAG 2.1:
`L = 0.2126R + 0.7152G + 0.0722B` (kênh đã tuyến tính hoá: `c/12.92` nếu `c ≤ 0.03928`, ngược lại
`((c+0.055)/1.055)^2.4`), `ratio = (L1+0.05)/(L2+0.05)`.
Ngưỡng AA: **4.5:1** chữ thường; **3:1** chữ lớn (**≥ 24px**, hoặc **≥ 19px và đậm ≥ 700**). Xuất ảnh sprite đánh dấu
hồng = trượt AA, vàng = chỉ đạt AA, xanh = AAA. Sửa: nền tối thì làm sáng màu chữ, nền sáng thì làm tối — **giữ trong
họ màu của palette**, đừng thêm màu mới.

## 4. Bản đồ animation (animation-map.mjs)

Liệt kê mọi tween, lấy mẫu bbox 6 lần/tween, tính cờ:
- `offscreen` (ra ngoài khung quá nửa kích thước), `invisible` (opacity < 0.01 suốt), `degenerate` (kích thước 0);
- `collision`: hai phần tử chồng nhau > **30%** diện tích tại cùng thời điểm;
- `paced-fast` < **0.2s** (cho x/y/opacity/scale), `paced-slow` > **2s**;
- **dead zone**: ≥ **1s** không có tween nào (gom theo ô 0.5s) — "Intentional hold or missing entrance?";
- phát hiện stagger (≥ 3 phần tử cùng props, cùng thời lượng) và độ đều của khoảng cách;
- snapshot các phần tử đang hiện ở 0%, 25%, 50%, 75%, cuối; biểu đồ Gantt ASCII 60 cột.
"Read the JSON … Check every flag — fix or justify."

## 5. Chứng minh có chuyển động (motion_check.py)

Lấy cặp khung xám 160×160 trong [t1, t2] **của cùng một cảnh**; độ khác trung bình tuyệt đối; lấy **trung vị** của 3
cặp (chống nhiễu từ caption bật/tắt). **> 3** (thang 0–255) = có chuyển động thật. Lưu ý: ảnh ít chi tiết (gradient
mịn) + push-in chậm có thể đo gần 0 dù render đúng — kiểm độ chi tiết ảnh trước khi đổ lỗi timeline.

## 6. Kiểm cấu trúc & âm thanh

- Bảng triệu chứng → nguyên nhân (build-checklist): chớp đen cuối cảnh = timeline ngắn hơn slot; video đứng hình =
  animate trực tiếp kích thước `<video>`; chữ bị xén = thiếu `overflow: visible`; transition rơi giữa từ = `data-start`
  lệch, căn vào **đỉnh** transition (thường giữa thời lượng).
- Âm thanh: `ffmpeg -af volumedetect` — lời thuyết minh kiểu tài liệu có mean quanh **−26 dB** (recipe 4).
- Contact sheet 5 khung (`hyperframes snapshot`) trước khi đăng: tràn chữ, font rơi về mặc định, phần tử hiện trước
  entrance, khung zoom.
- Self-review từng composition: mọi asset đã gán có trong HTML không (grep tên file), ≥ 2 lớp chiều sâu, mọi phần tử
  có chuyển động giữa cảnh, chữ ≥ 20px (nhãn ≥ 16px), **không gradient tuyến tính tối toàn màn** (H.264 bị banding).

## Áp dụng vào vedit

**Đã có**: `vedit validate` (schema + đối chiếu media); Agent 3 render preview, xem khung giữa mỗi clip + lúc mỗi chữ
xuất hiện, `inspect_render` với lưới; nhắc vùng an toàn 12%/22%.

**Còn thiếu**: không soi **điểm cắt** (hình nhảy, tiếng bụp); không kiểm tra tự động va chạm chữ/đồ hoạ, vùng an
toàn, tương phản, vùng chết; không kiểm "đúng từng chữ"; không có giới hạn vòng + báo cáo trung thực.

**Đề xuất (ưu tiên)** — gom thành lệnh **`vedit qa <slug> [--source preview]`** xuất `renders/.work/qa/report.md`:
1. **Vùng chết & mật độ** (tính từ EditPlan, không cần render): liệt kê khoảng > 2.5s không có sự kiện thị giác nào
   (cắt, chữ mới, đồ hoạ, motion) — ngưỡng cho video năng động; ASMR nới 3.5–4s. Dễ.
2. **Va chạm & vùng an toàn**: dùng `FontBook` (đã có trong `vedit/ass.py`) tính bbox mọi text/graphic theo thời gian;
   báo chồng > 30% và phần nằm trong 12% trên / 22% dưới / 12% phải. Vừa.
3. **Tương phản**: trích khung preview tại giữa mỗi text, tính tỉ lệ WCAG vành 4px quanh bbox như mục 3; báo < 4.5:1
   (chữ nhỏ) hoặc < 3:1 (chữ lớn). Vừa.
4. **Điểm cắt**: với mỗi biên clip, ghép filmstrip ±0.5s + waveform (xem ghi chú đọc video) và đo nhảy RMS trong
   ±20ms để phát hiện tiếng bụp. Vừa.
5. **Contact sheet** 6–9 khung (`ffmpeg … select,tile=3x3`) gửi kèm preview cho người dùng. Dễ.
6. Prompt Agent 3: chọn mốc **theo lời/sự kiện** (từ được nói, tiếng va chạm) thay vì chỉ giữa clip; **tối đa 3 vòng**
   rồi báo điều chưa sửa được. Dễ.
