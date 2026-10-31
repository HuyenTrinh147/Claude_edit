---
title: buttercut: Lên kế hoạch cut cùng người dùng trước khi dựng
category: scripting
tags: [lập kế hoạch, concept, beat, duyệt, script edit, selects, buttercut, đúng ý người dùng]
updated: 2026-10-31
sources:
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/roughcut_planning.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/roughcut_path.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/direct_path.md
  - https://github.com/barefootford/buttercut/blob/main/templates/plan_template.md
  - https://github.com/barefootford/buttercut/blob/main/docs/creating-a-cut.md
  - https://github.com/barefootford/buttercut/blob/main/CHANGELOG.md
---
# buttercut: Lên kế hoạch cut cùng người dùng trước khi dựng

**Vấn đề ButterCut đã gặp** (CHANGELOG 0.6.0): "Rough cut creation used to be one step where Claude inferred what you
wanted and built it. This was often the wrong story or the wrong footage. Now planning happens first." Từ đó, việc
**lên kế hoạch** là hội thoại với người dùng ở main thread; việc **dựng** là máy móc, chạy sau khi đã duyệt.

## Bước 1: hỏi loại cut, kể cả khi người dùng đã nói "roughcut"

Prompt ép rất mạnh: "'Roughcut' in the user's opening request is trained vocabulary, not a confirmed choice", "You
**absolutely must** tell them the next statement and question before moving forward". Câu mẫu: "Library is ready.
All footage processed. What kind of cut do you want to build?" Lựa chọn:

| Loại | Ý nghĩa |
|---|---|
| Scene | một beat câu chuyện, thường 30–90s |
| Selects / Find clips | cuộn clip phẳng theo tiêu chí (take tốt nhất, mọi lần nhắc tới chủ đề X, b-roll cùng chủ đề) |
| Script Edit | người dùng đưa kịch bản, agent tìm footage cho từng dòng |
| Custom task | bất kỳ yêu cầu nào khác |
| Agent Roughcut | bản dựng có cốt truyện đầy đủ; lập kế hoạch rồi giao sub-agent (tốn token, thử nghiệm) |

## Bước 2: quy trình lập kế hoạch (nhánh Roughcut)

Hỏi **từng câu một**, bỏ qua câu người dùng đã trả lời, dùng `AskUserQuestion` (nút chọn) thay cho danh sách chữ:
1. **Độ dài mục tiêu**: 2–4 phút / 5–8 phút / khác.
2. **Có kịch bản/dàn ý không?** Có (đưa cho agent) / Chưa, cùng nghĩ / Chưa, xuất toàn bộ lời ra text để tự cắt.
3. **Đọc mọi tóm tắt clip** (rẻ, cho cái nhìn toàn cục).
4. **Đề xuất 3 concept** (tiêu đề + 1–2 câu về mạch), mỗi cái một cấu trúc khác: "The first should be the
   straightforward, most-likely user goal, probably linear storytelling. The other two should be more creative takes."
5. **Triển khai concept được chọn**: Format, Beats (3–6 beat, mỗi beat có intent + tỉ trọng thời lượng + gợi ý
   footage), thời lượng ước tính.
6. **Lặp với người dùng**, mỗi lần sửa thì cho xem lại toàn bộ kế hoạch.
7. **Chỉ lưu khi có câu "đồng ý" rõ ràng**: "Tweaks are not consent. After every plan change, restate the whole plan
   back to the user before asking for the green light."
8. Lưu `plans/plan_<tên>_<YYYYMMDD_HHMMSS>.md` từ template, rồi mới giao sub-agent dựng.

## Khuôn kế hoạch (`templates/plan_template.md`)

```markdown
# [Working title]
## Concept          — 1–2 câu: góc nhìn, giọng, mạch
## Format           — vlog, YouTube Short, long-form, documentary, talking-head, montage... + nhịp/giọng đi kèm
## Target Duration  — vd "4–6 min" hoặc "45–60s sequence"
## Beats
### 1. [Tên beat]
- Intent: beat làm gì cho câu chuyện (open, escalate, turn, payoff...)
- Approx. share: tỉ trọng ("~30s", "~15% of total")
- Footage suggestions: tên file gợi ý; agent dựng được đổi sang khoảnh khắc mạnh hơn
## Required Dialogue  — câu bắt buộc: trích nguyên văn hoặc mô tả gần đúng ("đoạn kể về chú ảo thuật gia...")
## Notes for the Build — ràng buộc, thứ cấm dùng, quyết định của người dùng
```

Kế hoạch là **định hướng**, không phải paper cut có timestamp: "Beats are direction, not paper-cut timestamps."

## Nhánh Script Edit và Scene/Selects/Custom

- Dựng trực tiếp ở main thread, cho người dùng xem từng bản **dạng bảng**, sửa tới khi được duyệt rõ ràng.
- Script Edit: đi từ đầu tới cuối kịch bản; với mỗi dòng, đọc tóm tắt rồi `rg "<cụm trong kịch bản>" transcripts/`
  để ghim clip + mốc; dựng đúng thứ tự kịch bản. Dòng không tìm được footage: "don't invent or force a near-match —
  list those gaps for the user" để họ quyết bỏ, quay lại, hay thay bằng cảnh gần đúng.
- Selects: ghi tiêu chí chọn vào `description` để mở timeline là biết cut này là gì.

## Vì sao hiệu quả

- Sai hướng câu chuyện là lỗi đắt nhất; hỏi 3–5 câu rẻ hơn nhiều so với dựng lại.
- 3 concept khác cấu trúc buộc agent khám phá phương án sáng tạo, nhưng vẫn có một phương án "an toàn".
- Người dùng duyệt ở mức beat (dễ hiểu), không phải mức mốc giây.
- Sub-agent dựng nhận kế hoạch đã duyệt nên không phải hỏi giữa chừng ("the plan is already approved — don't
  re-propose").

## Áp dụng vào vedit

**Đã có**: Agent 2 viết `script.json` có `hook_options`, `title_options`, `concept`, bảng cảnh, insight trend;
`/lam-video` hỏi lại khi thiếu mục tiêu.

**Còn thiếu**: Agent 2 tự chọn một concept rồi viết luôn EditPlan, không có bước người dùng chọn/duyệt. Dự án gần nhất
(muối cà pháo ASMR) đi thẳng một hướng "kết quả trước, quy trình sau, vòng lặp" và bị chê "chưa đúng ý, thiếu sáng
tạo", đúng lỗi ButterCut mô tả ở 0.6.0. Ngoài ra subagent trong Claude Code không hỏi người dùng giữa chừng được, nên
cổng duyệt phải nằm ở main thread (ButterCut cũng để "This planning flow runs in the main thread, not in a sub-agent").

**Đề xuất theo ưu tiên**:
1. Thêm cổng duyệt concept vào `/lam-video` và `/kich-ban`, chạy ở main thread sau `vedit analyze`: Agent 2 (hoặc
   main thread) trả về 3 concept cho video ngắn, mỗi concept gồm hook 0–2s, chuỗi beat có giây, phong cách
   (chữ/đồ hoạ/nhạc/màu), thời lượng; concept 1 là cách kể thẳng (vd quy trình theo thứ tự), concept 2–3 là cách sáng
   tạo khác cấu trúc (vd kết quả trước, POV kể chuyện bằng chữ, listicle "3 bí quyết", trước/sau, đếm ngược tốc độ
   cao). Hỏi bằng `AskUserQuestion`, nhắc lại toàn bộ kế hoạch, chỉ dựng khi người dùng nói đồng ý. Dễ đến vừa.
2. Lưu kế hoạch đã duyệt vào `projects/<slug>/plan.md` (khuôn như trên, đổi "Approx. share" thành giây) và truyền
   nguyên văn cho Agent 2/3; thêm trường `approved_concept` vào schema script. Dễ.
3. Menu loại video cho người làm TikTok: Highlight/hook-first, Quy trình/hướng dẫn, Kể chuyện/POV, Listicle,
   Trước/sau, ASMR không lời, Dựng theo lời người dùng đưa (script edit). Dễ.
4. Mục "Khoảnh khắc bắt buộc" (Required moments) và "Cấm dùng" trong kế hoạch để người dùng ghim cảnh họ thích. Dễ.
5. Nhánh script edit cho người dùng đưa lời thoại/kịch bản: ghép footage theo từng dòng, liệt kê dòng thiếu cảnh
   thay vì bịa. Vừa (cần transcript).
