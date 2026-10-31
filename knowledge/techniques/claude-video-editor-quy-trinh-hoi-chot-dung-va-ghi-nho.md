---
title: claude-video-editor: Quy trình hỏi, chốt, dựng và ghi nhớ
category: techniques
tags: [claude-video-editor, quy trình, duyệt chiến lược, brief, style profile, preview, project.md, tương tác người dùng]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-studio/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/references/interview-questions.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/references/style-intake.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/references/build-checklist.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-7-validate.md
  - https://github.com/assafkip/claude-video-editor/blob/master/templates/project/project.md
  - https://github.com/assafkip/claude-video-editor/blob/master/templates/project/README.md
---
# claude-video-editor: Quy trình hỏi, chốt, dựng và ghi nhớ

Cốt lõi tương tác của repo: **Ask → confirm → execute → iterate → persist**. Câu then chốt (Hard Rule 11):

> "Strategy confirmation before execution. Never touch the cut until the user has approved the plain-English plan."

## 1. Năm bước của một phiên dựng (video-use)

1. **Inventory** — `ffprobe` mọi nguồn, transcribe + pack, xem 1–2 `timeline_view` để có ấn tượng hình ảnh đầu tiên.
   Không tự transcribe khi người dùng chưa trỏ footage và nói muốn gì.
2. **Pre-scan** — đọc lướt transcript, liệt kê câu nói vấp/sai để tránh (đưa vào brief của editor).
3. **Converse** — mô tả bằng lời những gì thấy, rồi hỏi **theo chất liệu**, không theo checklist cố định:
   loại nội dung, độ dài/tỉ lệ khung, hướng thẩm mỹ/thương hiệu, cảm giác nhịp, khoảnh khắc **phải giữ**, khoảnh
   khắc **phải bỏ**, mong muốn về animation & màu, nhu cầu phụ đề.
4. **Propose strategy** — **4–8 câu**: hình hài video, chọn take nào, hướng cắt, kế hoạch animation, hướng màu, kiểu
   phụ đề, ước lượng độ dài. **Chờ xác nhận.**
5. **Execute → Preview → Self-eval (trước khi cho xem) → Iterate → Persist.** Góp ý bằng lời → lập lại kế hoạch →
   render lại; không transcribe lại; render final khi được xác nhận.

## 2. Phỏng vấn kiểu make-a-video (người mới, video từ ý tưởng)

- 2 pha, 8 cổng; pha 1 (cổng 1–4) gom **mọi thứ** trước khi đụng code, tổng hợp thành `BRIEF.md` rồi **chờ "yes,
  build it"**.
- Hỏi **từng câu một**, ưu tiên trắc nghiệm (dùng công cụ `AskUserQuestion`); câu trả lời bất thường (vd "quảng cáo
  TikTok 4 tiếng") thì xác nhận lại; **không hỏi thứ đã biết** — kiểm kê `assets/` trước.
- Ngân hàng câu hỏi (rút gọn): mục đích (promo/quảng cáo/teaser/demo/tutorial/explainer) · khán giả · độ dài
  (10–20s / 20–45s / 45–90s / 1.5–3 phút) · tỉ lệ (16:9 / 9:16 / 1:1) · fps (30 / 60 UI / 24 điện ảnh) · nguồn lời
  (dán kịch bản / dàn ý / tự ghi âm / TTS / không lời) · phụ đề (tắt / hype / corporate / karaoke / tối giản) ·
  style guide · palette · font · logo · video tham chiếu · nhịp (kinetic 1–2s / balanced 2–3s / relaxed 3–5s) ·
  nhạc (không / pad 0.15 / music bed 0.4 / full 0.8) · CTA và thời gian giữ CTA.
- **Không áp thương hiệu lên người dùng**: chỉ dùng mặc định khi họ chủ động từ chối cung cấp style.

## 3. Cổng nhận diện hình ảnh (Visual Identity Gate)

Trước khi làm đồ hoạ phải có một trong: DESIGN.md · style người dùng đặt tên · hoặc hỏi đúng **3 câu**:
mood (explosive / cinematic / fluid / technical / chaotic / warm) · nền sáng hay tối · màu/font/tham chiếu thương hiệu.
Từ đó viết DESIGN.md tối thiểu: `Style Prompt` (1 đoạn), `Colors` (3–5 hex có vai trò), `Typography` (1–2 họ font),
`What NOT to Do` (3–5 điều). Quy tắc màu: **≤ 5 màu biểu tượng, mỗi màu gắn một ý nghĩa** (lưu ở `style-profile.md`).

## 4. Hai cổng xem trước

- Cổng 1: preview trực tiếp (HyperFrames Studio) — "**WAIT for explicit 'looks good, render a draft'** … Silence is
  not approval."
- Cổng 2: bản MP4 nháp qua server có hỗ trợ HTTP Range (`npx serve`, không dùng `python http.server` vì tua hỏng) —
  chờ người dùng xác nhận phát/âm thanh khớp rồi mới render final.
- Sau giao hàng: ghi mục `## Delivery` vào BRIEF.md, **chủ động mời một vòng sửa** ("the user almost always has one").

## 5. Bộ nhớ phiên — `project.md`

Mỗi phiên **append** một mục:

```markdown
## Session N — YYYY-MM-DD
**Strategy:** một đoạn mô tả cách tiếp cận
**Decisions:** chọn take, cắt, grade, animation + lý do
**Reasoning log:** một dòng lý do cho mỗi quyết định không hiển nhiên
**Outstanding:** việc hoãn lại
```

Khi khởi động: đọc `project.md`, **tóm tắt phiên trước trong một câu** rồi hỏi có tiếp tục không. Template dự án còn
có "Beat map (source timestamps)", "Pipeline notes" và lệnh re-render. `website-to-hyperframes` dùng `HANDOFF.md`
(bảng beat/trạng thái, audio, việc còn lại, lệnh) cho nhiều phiên.

## 6. Nguyên tắc ứng xử khác

- "Generalize. Do not assume what kind of video this is. Look at the material, ask the user, then edit."
- "Look first, ask second, edit last." (anti-pattern: "Assuming what kind of video it is.")
- Nếu không có style mà vẫn phải làm: **đề xuất palette trong bước chiến lược và chờ xác nhận** trước khi dựng đồ hoạ.

## Áp dụng vào vedit

**Đã có**: `/lam-video` hỏi khi thiếu mục tiêu (mặc định TikTok ~30s); Agent 2 viết `script.md` có nhiều phương án
hook/tiêu đề; Agent 3 tự xem preview 1–3 vòng; `/sua-video` cho vòng sửa bằng lời.

**Còn thiếu** (khả năng cao là lý do bản dựng bị chê "chưa đúng ý"): luồng chạy thẳng analyze → kịch bản → dựng →
final **không có điểm người dùng duyệt hướng dựng/phong cách**; không có bộ nhớ dự án nên vòng sửa sau không biết vì
sao bản trước bị chê; không gửi preview trước final.

**Đề xuất (ưu tiên)**:
1. **Cổng chốt chiến lược** trong `/lam-video` sau bước phân tích: Agent 2 trả `script/strategy.md` gồm (a) 4–8 câu
   chiến lược (hook, cấu trúc, cảnh giữ/bỏ, nhịp, phong cách chữ/đồ hoạ, look, phụ đề, nhạc/SFX, độ dài), (b) style
   profile (2–3 màu lấy từ khung hình + ý nghĩa, 1 font tiêu đề + 1 font thông tin, cảm giác chuyển động, 3 điều
   **không** làm), (c) 2–3 phương án hook. Người điều phối gửi người dùng và chờ OK (cho phép "cứ làm theo mặc định").
   Dễ.
2. **`projects/<slug>/project.md`**: Agent 2/3 append quyết định + phản hồi nguyên văn của người dùng ("bản 1: chưa
   đúng ý, thiếu sáng tạo") + hành động đã sửa; agent đọc đầu phiên và tóm tắt 1 câu. Dễ.
3. **Gửi preview trước final**: sau `vedit render --preview`, gửi file preview + contact sheet cho người dùng; chỉ
   render final khi họ OK (hoặc khi họ đã nói "làm luôn"). Dễ.
4. **Bộ câu hỏi tiếng Việt** ngắn, trắc nghiệm, hỏi tối đa 3 câu khi thiếu: mục tiêu/nền tảng · mood (sôi động /
   ấm áp / sang trọng / hài hước / ASMR thư giãn) · có giọng đọc/nhạc/phụ đề không · khoảnh khắc phải giữ · video mẫu
   thích. Dễ.
5. Ghi "Delivery" (lệnh render, độ dài, file) và luôn mời một vòng sửa bằng `/sua-video`. Dễ.
