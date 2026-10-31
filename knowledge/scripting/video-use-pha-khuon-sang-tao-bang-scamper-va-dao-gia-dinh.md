---
title: video-use: Phá khuôn sáng tạo bằng SCAMPER và đảo giả định
category: scripting
tags: [video-use, sáng tạo, ý tưởng, concept, scamper, đảo giả định, kịch bản, thiếu sáng tạo]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/production-quality.md
---
# video-use: Phá khuôn sáng tạo bằng SCAMPER và đảo giả định

Ghi chú này dành cho lời chê "thiếu sáng tạo". Nó gom ba thứ từ video-use:
- triết lý tự do sáng tạo của SKILL.md;
- ví dụ hook "show the edit";
- phương pháp "Creative Divergence" trong `skills/manim-video/SKILL.md`.

## Triết lý gốc (SKILL.md của video-use)
- "**Artistic freedom is the default.** Every specific value, preset, font, color, duration, pitch structure, and
  technique in this document is a *worked example* from one proven video — not a mandate... **The only things you
  MUST do are in the Hard Rules section.**"
- "**Invent freely.** If the material calls for a technique not described here — split-screen, picture-in-picture,
  lower-third identity cards, reaction cuts, speed ramps, freeze frames, crossfades, match cuts, L-cuts, J-cuts,
  speed ramps over breath, whatever — build it... Do not wait for permission."
- "12 hard rules, artistic freedom elsewhere. Production-correctness is non-negotiable. Taste isn't."
- Ví dụ hook "show the edit": hình được lái bằng **cùng dữ liệu với âm thanh**. Ý tưởng sinh ra từ chính câu
  chuyện của nội dung, không phải chọn từ một danh sách hiệu ứng.

## Phương pháp "Creative Divergence" (manim-video)
Skill gốc chỉ dùng phương pháp này khi người dùng muốn kết quả thử nghiệm, sáng tạo, độc đáo. Với lời chê "thiếu
sáng tạo" thì đây đúng là lúc dùng. Quy tắc: chọn chiến lược và suy luận **trước** khi thiết kế.

**SCAMPER.** Bản trong skill chỉ liệt kê 5 thao tác:
| Thao tác | Nghĩa (theo skill) | Dịch sang video ngắn |
|---|---|---|
| **Substitute** | Thay ẩn dụ hình ảnh chuẩn | Thay "chữ gọi tên bước" bằng âm thanh dẫn nhịp; thay badge bằng chính đồ vật trong cảnh |
| **Combine** | Trộn hai cách giải thích | Trộn ASMR với kể chuyện POV; trộn trước/sau trong cùng khung (split-screen) |
| **Reverse** | Đi ngược: từ kết quả về gốc | Mở bằng thành phẩm rồi tua ngược về hũ rỗng; kể từ cuối |
| **Modify** | Phóng đại một tham số để thấy nó quan trọng | Phóng đại thời gian (time-lapse, speed ramp), phóng đại âm (tiếng giòn), phóng đại cỡ (macro) |
| **Eliminate** | Bỏ hết ký hiệu, chỉ dùng chuyển động | Bỏ hết chữ, badge, progress bar, chỉ còn cắt theo tiếng động + một dòng tiêu đề |

**Đảo giả định (Assumption Reversal):**
1. Liệt kê những gì "chuẩn" khi làm loại video này.
2. Chọn giả định nền tảng nhất.
3. Đảo ngược nó.
4. Xem việc đảo ngược làm lộ ra điều gì mà cách chuẩn che mất.

**Đi cùng phương pháp:**
- "If something looks... like 'AI-generated slides,' it is wrong."
- Kiểm tra đa dạng: hai cảnh liền nhau không dùng cùng kiểu chuyển động, cùng màu nhấn, cùng bố cục, cùng nhịp.

## Quy trình đề xuất cho Agent 2 của vedit
1. Viết **một câu "ý tưởng dựng"** trước khi chọn hiệu ứng, ví dụ: "Để tiếng động kể công thức".
2. Đưa ra 3 hướng:
   - (A) chuẩn thể loại, an toàn;
   - (B) một thao tác SCAMPER;
   - (C) một giả định bị đảo.

   Mỗi hướng 2–3 câu, kèm hook 1.5 s đầu.
3. Đưa cho người dùng chọn (xem `scripting/video-use-quy-trinh-hoi-de-xuat-chien-luoc-va-cho-duyet`).
4. Chỉ sau đó mới chọn công cụ. Mọi hiệu ứng phải phục vụ câu ý tưởng. Hiệu ứng nào không phục vụ thì bỏ.
5. Chỉ dùng footage có thật. Đảo giả định **không** được bịa ra cảnh không quay.

## Minh hoạ trên footage "muối hũ cà pháo" (dự án `20261030-video-01`)
Đây là ví dụ cách nghĩ, không phải đáp án.

**Giả định chuẩn của video công thức:**
- các bước theo thứ tự;
- đánh số bước;
- gọi tên nguyên liệu bằng chữ;
- kết bằng thành phẩm;
- có nhạc nền.

Plan đã dựng làm đúng tất cả các giả định này: 5 badge, 5 callout, progress bar, sparkles, highlight và 10 SFX
trong 15.8 s.

**Các hướng đảo:**
- **Eliminate:** không chữ, chỉ còn tiếng "cạch, xoẹt, lách tách, keng" dẫn nhịp. Mỗi cú cắt rơi đúng một tiếng
  động, cộng một dòng tiêu đề. Đúng tinh thần "~8 hiệu ứng là thiết kế, ~20 là chung chung".
- **Reverse:** mở bằng hũ đầy sát camera (đã có ở 20.47–21.59 s nguồn), rồi cắt "tua ngược" từng bước về hũ rỗng.
  vedit chưa có `reverse`, cần thêm.
- **Modify:** phóng đại một tiếng động đắt nhất, ví dụ tiếng kéo cắt ớt: slow-mo 0.5× + punch-in + giữ khung 0.5 s.

## Áp dụng vào vedit
**Đã có:**
- Ghi chú "Tư duy dựng sáng tạo cho video ngắn" (có mục "Kiềm chế").
- Bộ công cụ chữ, đồ hoạ, motion và SFX phong phú.

**Còn thiếu:**
- Prompt Agent 2 và Agent 3 ghi "**Lớp sáng tạo (bắt buộc...)**" rồi liệt kê sẵn hiệu ứng (punch + sticker + badge
  + callout + progress_bar + SFX). Kết quả là mọi video ra cùng một khuôn, và plan gần nhất đúng là như vậy.
- Không có bước "ý tưởng trước, công cụ sau".
- Thiếu các kỹ thuật trong danh sách "Invent freely" của video-use: `reverse`, freeze frame, split-screen/PiP,
  J/L-cut, speed ramp trong một clip.

**Đề xuất (ưu tiên giảm dần):**
1. **Sửa prompt** (`.claude/agents/video-scriptwriter.md`, `video-editor.md`, `vedit/agents/scriptwriter.py`,
   `editor.py`) — ưu tiên cao, độ khó thấp:
   - đổi "Lớp sáng tạo (bắt buộc)" thành hai khối: "Quy tắc kỹ thuật bắt buộc" (vùng an toàn, cắt đúng ranh giới,
     fade, đọc kịp, không che chủ thể) và "Ví dụ, không bắt buộc";
   - bắt buộc có câu ý tưởng và 2–3 hướng tương phản.
2. **Critic kiểm tra riêng tính sáng tạo** — độ khó thấp. Thêm câu hỏi: "Có một ý tưởng xuyên suốt không, hay chỉ
   là chồng sticker?"
3. **Mở rộng EditPlan** — độ khó trung bình:
   - `Clip.reverse` (dùng `reverse`/`areverse`, chỉ cho clip ngắn vì tốn RAM);
   - `Clip.freeze_end` (dùng `tpad=stop_mode=clone:stop_duration=...`);
   - `Clip.audio_offset` cho J/L-cut. Hiện có thể làm tạm bằng cách tắt tiếng clip rồi thêm `AudioTrack` trỏ vào
     chính file nguồn, với `role=voiceover`, `fade_in`/`fade_out` nhỏ.
4. **Split-screen / PiP** qua mục overlay clip video — độ khó trung bình đến cao. Xem
   `ffmpeg/video-use-pipeline-render-tung-doan-overlay-phu-de-cuoi`.
