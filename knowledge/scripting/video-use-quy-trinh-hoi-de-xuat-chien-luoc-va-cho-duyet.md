---
title: video-use: Quy trình hỏi, đề xuất chiến lược và chờ duyệt
category: scripting
tags: [video-use, quy trình, chiến lược, hỏi người dùng, xác nhận, memory, project.md, đúng ý]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/README.md
  - https://github.com/browser-use/video-use/blob/main/install.md
---
# video-use: Quy trình hỏi, đề xuất chiến lược và chờ duyệt

Đây là phần video-use dùng để làm **đúng ý** người dùng. Nguyên tắc:
"**Ask → confirm → execute → iterate → persist.** Never touch the cut until the user has confirmed the strategy
in plain English." Điều này cũng là Hard Rule 11. Kèm theo: "**Generalize.** Do not assume what kind of video
this is. Look at the material, ask the user, then edit." Anti-pattern tương ứng: "Assuming what kind of video it
is. Look first, ask second, edit last."

## Các bước trước khi dựng
1. **Inventory:** probe, transcribe, pack, xem 1–2 ảnh timeline.
2. **Pre-scan:** đọc transcript một lượt, ghi "verbal slips, obvious mis-speaks, or phrasings to avoid" thành
   danh sách gạch đầu dòng, để đưa vào brief cho người dựng.
3. **Converse:** "Describe what you see in plain English. Ask questions *shaped by the material*." Các ý cần
   thu thập:
   - thể loại nội dung;
   - độ dài và tỉ lệ khung;
   - hướng thẩm mỹ hoặc thương hiệu;
   - cảm giác nhịp;
   - **khoảnh khắc bắt buộc giữ**, **khoảnh khắc bắt buộc cắt**;
   - mong muốn về animation và màu;
   - có cần phụ đề không.

   "Do not use a fixed checklist — the right questions are different every time."
4. **Propose strategy:** viết **4–8 câu**: hình dạng video, chọn take nào, hướng cắt, kế hoạch animation, hướng
   màu, kiểu phụ đề, độ dài ước tính. **Chờ xác nhận.**

## Những chỗ khác cũng phải hỏi
- **Bảng màu và font cho animation:** "Get the palette, font, and visual language from the conversation — never
  assume a default. If the user hasn't told you, propose a palette in the strategy phase and wait for
  confirmation before building anything."
- **Nhạc:** "Music taste is the user's call. Generated music defaults to 'hype'; offer two contrasting beds and
  let the user listen."
- **Định dạng xuất:** "Worth asking the user which delivery format matters."
- **Lúc cài đặt** chỉ hỏi những thứ agent không tự tạo được (API key, xác nhận trước khi `brew install`), và hỏi
  đúng một lần.

## Sau khi dựng
- Chỉ đưa preview cho người dùng **sau khi** bản dựng đã qua self-eval.
- Người dùng góp ý bằng lời → lập lại kế hoạch → render lại. "Never re-transcribe."
- **Bộ nhớ:** ghi thêm vào `edit/project.md` sau mỗi phiên:
```markdown
## Session N — YYYY-MM-DD

**Strategy:** one paragraph describing the approach
**Decisions:** take choices, cuts, grades, animations + why
**Reasoning log:** one-line rationale for non-obvious decisions
**Outstanding:** deferred items
```
- Khi khởi động: "read `project.md` if it exists and summarize the last session in one sentence before asking
  whether to continue". Banner của repo cho thấy tinh thần này: agent nhớ kế hoạch cũ ("45s launch... 13
  takes") qua bộ nhớ của Claude Code, thấy chưa có thư mục `edit/` nên kiểm tra lại trước khi chạy. Task list
  trên banner cũng cho thấy agent dừng ở bước "Converse + propose strategy, wait for confirmation".

## Mẫu đề xuất chiến lược cho vedit (ví dụ minh hoạ, tiếng Việt)
Ví dụ dưới đây dựa trên footage "muối hũ cà pháo" của dự án `20261030-video-01`. Đây là minh hoạ cách trình bày,
không phải kết luận về video.
> **Mình thấy:** 25.6 s quay dọc, không lời. Tay làm từng bước: rót nước, muối, đường, khuấy, cắt ớt, tỏi gừng,
> thả cà, đậy nắp. Có nhiều tiếng động rõ ("cạch", "xoẹt", "keng"). Ánh sáng bếp ổn định.
> **Hai hướng:**
> (A) *ASMR tối giản:* ~15 s, không badge hay callout, chỉ 1 dòng tiêu đề. Cắt theo tiếng động, punch-in nhẹ
> khớp 3 tiếng va chạm lớn nhất, kết bằng tiếng "keng" đậy nắp và nối vòng về cảnh hũ thành phẩm.
> (B) *Công thức nhanh:* ~20 s, đánh số 5 bước, chữ to dễ đọc, nhạc nền nhẹ, CTA "lưu lại công thức".
> **Cần bạn chọn:** hướng A hay B? Có khoảnh khắc nào bắt buộc giữ hoặc cắt không? Có dùng nhạc không, hay chỉ
> giữ tiếng thật?

## Áp dụng vào vedit
**Đã có:**
- `/lam-video` hỏi khi thiếu mục tiêu, mặc định TikTok, khoảng 30 s, tiếng Việt.
- Agent 2 tóm tắt ý tưởng, hook, cảnh và hashtag **sau khi** đã viết xong plan; sau đó Agent 3 dựng luôn.

**Còn thiếu:**
- Không có điểm dừng để người dùng duyệt chiến lược trước khi dựng.
- Không đưa ra các hướng tương phản để chọn.
- Không có bộ nhớ phiên: `projects/` không được commit nên phản hồi cũ như "chưa đúng ý, thiếu sáng tạo" bị mất.

**Đề xuất (ưu tiên giảm dần):**
1. **Thêm bước "đề xuất & chờ duyệt" vào `.claude/skills/lam-video/SKILL.md`** — ưu tiên cao, độ khó thấp.
   Đặt giữa `vedit analyze` và lúc Agent 2 viết plan:
   - mô tả video bằng lời;
   - hỏi 2–4 câu theo chất liệu;
   - đề xuất 4–8 câu với 2 hướng tương phản (A/B);
   - **dừng chờ** người dùng chọn.

   Chỉ bỏ qua bước này khi người dùng nói rõ "cứ làm luôn".
2. **Gom các mặc định cần hỏi thành một tin nhắn** — độ khó thấp. Mặc định TikTok/30 s chỉ dùng khi người dùng
   không trả lời. Trong cùng tin nhắn đó, hỏi luôn bảng màu/font và việc dùng nhạc hay giữ tiếng thật.
3. **`projects/<slug>/project.md`** theo mẫu Session ở trên — độ khó thấp. Agent 3 ghi thêm sau mỗi lần sửa.
   Agent 2/3 đọc file này trước khi làm, rồi tóm tắt phiên trước trong một câu.
4. **Gu người dùng lâu dài** — độ khó thấp. Lập một ghi chú riêng trong `knowledge/` (được commit) ghi lại phản
   hồi đã nhận và lựa chọn đã duyệt. Agent 2 đọc ghi chú này đầu mỗi dự án.
5. **Pre-scan trong Agent 2 khi video có lời** — độ khó thấp. Liệt kê chỗ nói vấp, nói nhầm trước khi chọn cảnh.
