---
title: Tư duy dựng sáng tạo cho video ngắn
category: techniques
tags: [luật dựng, quy tắc, sáng tạo, phong cách, duyệt, guardrails, nhịp, payoff]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/assafkip/claude-video-editor
  - https://github.com/barefootford/buttercut/blob/main/CHANGELOG.md
  - knowledge/techniques/ban-do-nang-luc-dung-vedit-da-co-va-con-thieu.md
---
# Tư duy dựng sáng tạo cho video ngắn

Bộ luật chung của Agent 2, Agent 3 và agent phản biện. Rút ra từ video-use, claude-video-editor, buttercut và nghiên
cứu nghề dựng (xem nguồn). Phần **Luật cứng** là kỹ thuật — luôn tuân thủ. Phần **Tự do sáng tạo** là nguyên tắc và
ví dụ — KHÔNG phải danh sách hiệu ứng bắt buộc.

## Luật cứng

1. **Duyệt trước, dựng sau.** Không viết EditPlan khi người dùng chưa chọn hướng dựng (trừ khi họ nói "cứ làm").
   Bài học buttercut: AI tự đoán ý rồi dựng một lèo thì "often the wrong story or the wrong footage".
2. **Đọc gu trước khi làm**: `profile/gu-nguoi-dung.md` (gu & phản hồi cũ của người dùng) và `projects/<slug>/project.md`.
3. **Không cắt giữa lời / giữa tiếng động.** Điểm cắt rơi vào khoảng lặng ≥ 150 ms (≥ 400 ms là sạch nhất); đệm
   khoảng 50 ms trước và 80 ms sau lời nói. Video ASMR: cắt trước onset tiếng động 1–2 frame, không cắt cụt đuôi tiếng vang.
4. **Mốc thời gian**: clip `start/end` = giây NGUỒN; texts / captions / graphics / motion / audio = giây TIMELINE.
5. **Vùng an toàn 9:16**: chữ và đồ hoạ quan trọng nằm trong 12%–78% chiều cao, tránh 12% mép phải.
6. **Chữ**: chỉ dùng font trong thư viện (`assets/fonts/README.md`, `vedit validate` báo lỗi font lạ); không emoji trong
   text (libass vẽ đơn sắc); chữ cần đọc hiển thị ít nhất (số ký tự / 15 + 0,5) giây; size ≥ 40.
7. **Một thứ mới mỗi lần**: không để ≥ 2 phần tử mới xuất hiện trong cùng 0,3 s, trừ khi cố ý theo nhịp.
8. **Payoff đáp đúng khung**: hiệu ứng nhấn (punch, flash, chữ đập) phải *đáp* đúng khung hình của khoảnh khắc chính —
   bắt đầu sớm hơn đúng bằng độ dài hiệu ứng; SFX đặt sớm hơn để đỉnh tiếng trùng khung hình.
9. **Âm thanh**: true peak ≤ −1 dBTP; nhạc nền thấp hơn lời 12–15 dB; renderer tự fade 25 ms ở mọi điểm cắt.
10. **Không lặp khuôn**: một hiệu ứng hay âm thanh y hệt không quá 3 lần trong video ngắn, trừ khi là motif có chủ đích.
11. **Tự kiểm tra trên bản đã render** (preview) ở mọi điểm cắt trước khi xuất; agent phản biện soi lỗi trước khi giao.
12. **Ghi lại mọi phản hồi** nguyên văn của người dùng vào `project.md` (`vedit note`) và bài học chung vào hồ sơ gu.

## Tự do sáng tạo

- **Chọn phong cách trước, rồi dùng 3–5 chiêu chữ ký của phong cách đó** — đừng rải mọi công cụ vedit có.
  Phong cách tham khảo: silent vlog / ASMR, food "satisfying", velocity / dựng theo beat, Hormozi (chữ từng từ),
  vlog cinematic, POV, game HUD / AR, giáo dục / giải thích (xem `knowledge/trends/` và `techniques/`).
- **Thói quen phải tránh** (vedit đã từng mắc):
  - dùng ngôn ngữ video *hướng dẫn* (huy hiệu bước, thanh tiến trình, nhãn) cho nội dung *cảm xúc / ASMR*;
  - nhịp đều đều — mọi clip dài như nhau, toàn cắt thẳng;
  - `pop` cho mọi thứ, chữ ở mọi cảnh, bounce cho mọi chữ, crossfade mọi chỗ;
  - đồ hoạ che mất chủ thể hoặc bàn tay đang thao tác.
- **Nhịp có biến thiên**: đoạn dồn (cắt nhanh, theo beat hoặc tiếng động) xen cảnh thở (giữ ≥ 1,5 s cho khoảnh khắc đẹp).
- **Khoảng 5 giây một khoảnh khắc "wow"**: payoff, speed ramp, dừng hình, chuyển cảnh có nghĩa, một câu chữ đắt.
- **Chuyển cảnh có nghĩa**: cắt thẳng là mặc định; chọn 1 kiểu chính + 1–2 kiểu nhấn; crossfade = "tiếp diễn".
- **Âm thanh là nửa video**: với ASMR, tiếng thật là nhân vật chính; SFX ít, khác nhau, có lý do.
- **Hệ thống chữ thống nhất**: 1 font tiêu đề có cá tính + 1 font thông tin, 2–3 màu lấy từ khung hình
  (`typography/cap-font-he-thong-chu-theo-the-loai-video`).
- **Kết có chủ đích**: vòng lặp liền về hook, hoặc một thẻ CTA ngắn.

Tra cứu công cụ: `techniques/bo-cong-cu-do-hoa-hieu-ung-cua-vedit` · Còn thiếu gì: `techniques/ban-do-nang-luc-dung-vedit-da-co-va-con-thieu`
· Ẩm thực/ASMR: `techniques/dung-video-nau-an-asmr-va-satisfying`.

## Áp dụng vào vedit

Agent 2 (đề xuất hướng dựng, viết EditPlan), Agent 3 (dựng) và agent phản biện đều đọc ghi chú này trước khi làm;
agent phản biện chấm bản dựng theo đúng 12 luật cứng ở trên.
