---
title: Quy trình tạo nội dung bằng AI từ brief đến lịch đăng
category: content
tags: [pipeline, brief, chiến lược, dàn ý, biên tập, cổng duyệt, agent-4]
updated: 2026-11-04
sources:
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/agents/graph.py
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/core/prompts/agents/brief_extractor.yaml
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/core/prompts/agents/strategy.yaml
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/core/prompts/agents/outline.yaml
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/core/prompts/agents/editor.yaml
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/agents/editor_agent.py
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/agents/research_agent.py
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/models/brand.py
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/skills/hedgehog-copywriting-loop/SKILL.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/agents/copy-writer.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/workspace/core.yaml
  - https://github.com/mituljn14/LangGraph-AI-Content-Generator/blob/HEAD/backend/graph.py
  - https://github.com/mituljn14/LangGraph-AI-Content-Generator/blob/HEAD/prompts/prompts.py
  - https://github.com/bikram73/SocialSpark_AI/blob/HEAD/server.ts
  - https://github.com/bikram73/SocialSpark_AI/blob/HEAD/docs/BUG_FIXES.md
  - https://github.com/taha-rafi/shortgenie/blob/HEAD/services/gemini.ts
  - https://github.com/tvcnet/social-toolkit/blob/HEAD/assets/js/tst-content.js
---
# Quy trình tạo nội dung bằng AI từ brief đến lịch đăng

Tóm tắt: các repo chia việc thành nhiều bước nhỏ, mỗi bước một "vai" và một đầu ra có cấu trúc. Hai repo làm tốt nhất ở
hai đầu khác nhau: **omniwrite** mạnh ở phần *nghĩ* (brief → chiến lược → dàn ý → viết → biên tập), **hedgehog-core** mạnh
ở phần *kiểm* (cổng bằng mã + vòng sửa). Chưa repo nào có cả hai; vedit có thể ghép.

## Ma trận: repo nào làm tốt bước nào

`++` làm tốt, có mã thật · `+` có nhưng mỏng · `-` không có

| Bước | omniwrite | hedgehog | SocialSpark | social-toolkit | content-craft | shortgenie | mituljn14 |
|---|---|---|---|---|---|---|---|
| Brief + hỏi làm rõ | ++ | ++ | + (form) | + (5W) | + | - | - |
| Nghiên cứu / dữ kiện | + (web search) | - (chỉ cấm bịa) | - | + (đọc link) | + (transcript) | - | - |
| Góc / chiến lược / hook | ++ | + | + | - | - | + | - |
| Dàn ý có duyệt | ++ | - | - | - | - | - | - |
| Bản nháp | ++ | ++ | ++ | ++ | + | ++ | + |
| **Kiểm tra bằng mã** | - | ++ | + (chuẩn hoá) | + (hậu xử lý) | - | - | - |
| Biên tập / tinh chỉnh | + (LLM) | ++ (vòng ≤ 6) | + | + (polish) | - | - | + (refine) |
| Chuyển thể nền tảng | ++ | + (4 định dạng) | ++ | ++ | + | - | + |
| Lịch / đăng | - | - | + (7 ngày) | + (lịch + CSV) | - | - | - |

## Luồng của omniwrite (mẫu cho phần "nghĩ")

`backend/agents/graph.py:1-25` mô tả luồng: `brief_extractor → research → strategy → outline → writers (song song) → editor`.
Có hai điểm dừng chờ người: sau brief nếu thiếu thông tin (`graph.py:125-136`), sau dàn ý nếu bật duyệt (`graph.py:139-145`).

Điểm đáng lấy:
- **Brief ra JSON có `is_complete` và `clarifying_questions`**, luật "chỉ hỏi khi thật sự mơ hồ, đừng hỏi thừa"
  (`brief_extractor.yaml:19-23`). Khớp luật "hỏi tối đa 3 câu" của Agent 4.
- **Chiến lược tách "ý" khỏi "chữ"**: `primary_angle`, `narrative_hook` ("ý đằng sau hook, chưa phải câu chữ"),
  `hook_variants` (N khái niệm khác nhau), `tone_per_platform`, `audience_assumptions` (`strategy.yaml:8-22`). Nguyên tắc ghi
  trong prompt: ưu tiên **khác biệt** ("góc nào chưa bị làm nát?"), giọng khớp văn hoá nền tảng (Reddit khác LinkedIn khác
  blog).
- **Dàn ý đưa người duyệt** với tiêu đề 2–3 phương án, mô tả hook, từng mục kèm 2–4 ý và số từ ước tính, CTA, ghi chú SEO
  (`outline.yaml:8-23`); prompt dặn "cụ thể" (ví dụ nêu "giải thích GPT-4 turbo giảm độ trễ thế nào", đừng nêu "bàn về AI").
- **Hồ sơ thương hiệu tiêm vào mọi agent**: tên, tagline, ngành, khán giả, thuộc tính giọng, góc nhìn người viết (ngôi),
  đối thủ cần khác biệt, chủ đề CẤM, chỉ dẫn riêng, và đoạn văn mẫu (`models/brand.py:51-91`; mẫu cắt 400 ký tự ở
  `prompts/system/brand_injector.yaml:24-29`).
- **Biên tập tối thiểu**: "chỉ sửa chỗ thật sự cần, giữ giọng người viết, nội dung tốt thì nói là tốt"; ưu tiên sửa sai giọng
  nền tảng hơn sửa sở thích văn phong (`editor.yaml:16-21`). Việc biên tập chạy sau cùng, nhìn **tất cả** đầu ra để giữ
  nhất quán sự kiện giữa các nền tảng.
- Bình luận đầu tiên của tác giả (`linkedin_comment`) phụ thuộc bài chính nên chạy sau, không song song
  (`graph.py:113-115`) — mẫu cho "bình luận ghim" sinh sau caption.

Hạn chế đã thấy trong mã (xem `loi-va-rui-ro-cua-cac-repo-ai-content-generator`): bước nghiên cứu cắt hết URL khỏi bản tóm
tắt (`research_agent.py:119`) nên mất dấu nguồn; biên tập chỉ nhận 800 ký tự đầu của tóm tắt (`editor_agent.py:80`) nên
không thể kiểm sự thật thật sự; biên tập thay nguyên văn đầu ra bằng JSON mô hình trả về, không có cổng mã
(`editor_agent.py:109-124`).

## Luồng của hedgehog-core (mẫu cho phần "kiểm")

`workspace/core.yaml` định nghĩa hai tầng: `brief` (file không rỗng) rồi `draft` (cổng `check-copy` phải thoát 0).
`skills/hedgehog-copywriting-loop/SKILL.md`:
- Brief ghi `type:` (prose / ad / landing-page / direct-response / tweet) ở dòng đầu; **loại bài quyết định hợp đồng định
  dạng** (dòng 20-40). Brief chỉ đọc sau khi bắt đầu viết (dòng 353); brief sai thì sửa ở gốc, không vá trong bản nháp.
- Hỏi lại khi loại bài mơ hồ vì chọn sai loại sẽ cho "cả tường lỗi định dạng" (dòng 194-200).
- **Mọi phương án brainstorm (tiêu đề, hook, góc) cũng phải qua cổng** trước khi đưa người dùng chọn; phương án không qua
  sau 3 lần sinh lại thì vẫn **hiện ra nhưng gắn nhãn rule nào trượt**, đừng giấu (dòng 154-188).
- Vòng viết → chạy cổng → sửa đúng điều bị báo, **tối đa 6 lần**, quá thì dừng và báo xung đột giữa brief và cổng, không
  sửa mù (dòng 286; `agents/copy-writer.md` bước 5).
- Luật cấm "chơi cổng": xoá đúng chữ bị bắt mà cấu trúc vẫn y nguyên; đổi / bỏ `--format` để qua báo cáo (dòng 338-352).
- Bản nháp cuối chỉ giao khi báo cáo JSON (không phải lời kể lại) cho thấy đã chạy đúng định dạng
  (`copy-writer.md` phần Self-test).

## Các chi tiết nhỏ đáng bắt chước

- **Chuẩn hoá sau LLM** (SocialSpark): sau khi model trả JSON, duyệt lại đủ 7 ngày theo thứ tự chuẩn, thiếu trường thì điền /
  loại trùng (`docs/BUG_FIXES.md` mục 2); lọc hashtag bằng hàm xác định (`server.ts:50-`). Đừng tin model tự giữ đúng cấu
  trúc.
- **Nhãn nguồn** (SocialSpark): mỗi kết quả có `source: "ai" | "fallback"` và giao diện hiện rõ — để người dùng biết nội dung
  do mô hình hay do khuôn dự phòng (`docs/BUG_FIXES.md` mục 5; `server.ts:347-348`).
- **Lược đồ JSON ép đầu ra** (shortgenie `services/gemini.ts:63-87`, SocialSpark `server.ts` phần `responseSchema`): kịch bản
  = danh sách cảnh `{id, script, imagePrompt}` + `title`, `description`, `tags`.
- **Tạo lại ≠ viết lại cùng ý** (mituljn14 `prompts.py:103-112`): lệnh tạo lại yêu cầu "góc khác, cấu trúc khác, mở đầu
  khác, đừng dùng lại câu của bản trước" và truyền kèm bản trước để tránh trùng. **Tinh chỉnh** (`prompts.py:83-101`)
  thì ngược lại: giữ thông tin hữu ích, chỉ áp dụng đúng chỉnh sửa được yêu cầu, giữ loại nội dung và giọng.
- **Giới hạn đầu vào** (SocialSpark): tên thương hiệu 2–100 ký tự, chỉ dẫn thêm ≤ 500 ký tự (`server.ts` đoạn validation;
  `docs/BUG_FIXES.md` mục 1).
- **Khung 5W** (social-toolkit `tst-content.js:19-30`): Ai – Gì – Ở đâu – Vì sao – Khi nào + giọng + độ dài (3 mức) làm
  brief tối thiểu cho một bài đăng; ô "Gì" ghi rõ có cho phép URL hay không.

## Quy trình đề xuất cho Agent 4 (ghép hai nửa)

1. **Brief** → `brief.md` có `loai_noi_dung:` (lời thoại / chữ trên màn hình / caption TikTok / caption Reels / tiêu đề Shorts /
   bài Facebook / thread / quảng cáo), mục tiêu (xem / lưu / chia sẻ / follow / bán), giọng kênh, dữ kiện thật, giả định.
2. **Dữ kiện** → `facts.md`: mỗi con số / tuyên bố một dòng kèm nguồn (URL hoặc mốc giây transcript). Thiếu nguồn = `[cần xác nhận]`.
3. **Góc** → 6–10 góc, chọn 3, mỗi góc có `narrative_hook` (ý) tách khỏi câu chữ; người dùng chọn (như cổng chọn hướng của Agent 2).
4. **Dàn ý** → chỉ với nội dung dài (blog, thread, video > 45 giây); video ngắn thì bỏ, đi thẳng beat.
5. **Nháp** → viết theo loại bài; dùng khung ở `khung-viet-hook-kich-ban-caption-hashtag-va-ugc`.
6. **Cổng bằng mã** → `vedit content check` (đề xuất) ≤ 6 vòng; cả phương án hook cũng qua cổng.
7. **Biên tập tối thiểu** → một lượt đọc thành tiếng, sửa đúng chỗ vấp, giữ giọng.
8. **Chuyển thể + lịch** → xem `chuyen-the-da-nen-tang-lich-dang-va-series`.

## Áp dụng vào vedit

**Đã có**: Agent 4 đã có brief (hỏi ≤ 3 câu), 6–10 góc → chọn 3, hook ≥ 3 phương án, cổng chống văn AI, gói đăng bài, series;
Agent 2 đã có cổng "người dùng chọn hướng" (`concepts.md`).

**Thiếu / đề xuất theo thứ tự ưu tiên**:
1. Thêm `facts.md` (sổ dữ kiện) vào bước 1 của Agent 4 — cấp cho cổng kiểm tra "mọi số liệu có nguồn" một chỗ để kiểm.
2. Cổng bằng mã `vedit content check` thay cho "tự đọc lại" ở bước 5; ghi rõ trần 6 vòng và luật "không chơi cổng".
3. Cho **phương án hook / tiêu đề cũng chạy qua cổng** trước khi trình người dùng; trượt thì gắn nhãn, đừng giấu.
4. Agent 4 hỏi người dùng chọn góc (ghi bằng `vedit note`) trước khi viết lời, giống cổng của Agent 2 — tránh viết nguyên bản
   nháp cho góc người dùng không thích.
5. Hồ sơ giọng kênh có cấu trúc `profile/giong-kenh.md` (ngôi xưng, thuộc tính giọng, từ cấm / chủ đề cấm, 2–3 đoạn mẫu
   ≤ 400 ký tự do người dùng cung cấp, đối thủ cần khác) theo `BrandProfile` của omniwrite.
6. Lược đồ `vedit schema content` (pydantic) cho `ideas.md` / `post.md` / `calendar.md` để chuẩn hoá và kiểm đủ trường như
   SocialSpark, thay vì chỉ Markdown tự do.
