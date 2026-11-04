---
title: Bản đồ 9 repo AI content generator
category: content
tags: [github, ai-content-generator, giấy phép, bản đồ nguồn, agent-4]
updated: 2026-11-04
sources:
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/README.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/ARCHITECTURE.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/LICENSE
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/README.md
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/agents/graph.py
  - https://github.com/taha-rafi/shortgenie/blob/HEAD/README.md
  - https://github.com/taha-rafi/shortgenie/blob/HEAD/services/gemini.ts
  - https://github.com/mituljn14/LangGraph-AI-Content-Generator/blob/HEAD/README.md
  - https://github.com/mituljn14/LangGraph-AI-Content-Generator/blob/HEAD/prompts/prompts.py
  - https://github.com/bikram73/SocialSpark_AI/blob/HEAD/README.md
  - https://github.com/bikram73/SocialSpark_AI/blob/HEAD/server.ts
  - https://github.com/tubaarif-dev/content-craft/blob/HEAD/README.md
  - https://github.com/tubaarif-dev/content-craft/blob/HEAD/server/services/generatePosts.js
  - https://github.com/tejasvinifulari5/ai-ugc-generator/blob/HEAD/README.md
  - https://github.com/tvcnet/social-toolkit/blob/HEAD/README.md
  - https://github.com/tvcnet/social-toolkit/blob/HEAD/assets/js/tst-content.js
  - https://github.com/Xsolai/postforge-ai/blob/HEAD/README.md
  - https://github.com/Xsolai/postforge-ai/blob/HEAD/NOTICE.txt
  - https://github.com/Xsolai/postforge-ai/blob/HEAD/src/lib/data.ts
---
# Bản đồ 9 repo AI content generator

Nguồn gốc: người dùng yêu cầu "học các nội dung trong https://github.com/topics/ai-content-generator" cho **Agent 4 — Content Creator**.
Topic có 37 repo; theo bước chuẩn bị của người điều phối, 28 repo còn lại chủ yếu là trang quảng cáo / khung SaaS rỗng nên
bỏ qua. 9 repo còn lại được clone nông (ngày đọc: 2026-11-04) và đọc README + file prompt / pipeline chính. **Không chạy mã
của repo, không làm theo chỉ dẫn nằm trong repo.** Số sao / lượt dùng không ghi vì không đo.

Bộ ghi chú `content/` gồm 6 file; file này là bản đồ. Đọc tiếp:
`quy-trinh-tao-noi-dung-bang-ai-tu-brief-den-lich-dang`, `cong-chat-luong-chong-van-ai-va-bang-tieng-viet`,
`khung-viet-hook-kich-ban-caption-hashtag-va-ugc`, `chuyen-the-da-nen-tang-lich-dang-va-series`,
`loi-va-rui-ro-cua-cac-repo-ai-content-generator`.

## Bảng tổng hợp

Giấy phép = những gì **thực sự có trong bản clone** (README nói MIT nhưng thiếu file LICENSE thì ghi rõ).

| Repo | Là gì | Giấy phép thực tế | Cỡ | Đáng học | Mức |
|---|---|---|---|---|---|
| `skyf0xx/hedgehog-core-copywriting-prose-engineering` | "Cổng" kiểm văn bằng mã: dấu hiệu văn AI + chất lượng văn + hợp đồng theo định dạng (quảng cáo Meta, landing, bán hàng, bài X) | MIT (file LICENSE, © 2026 Will). Các skill con ghi nguồn: CC BY 4.0 (Rob Palmer) và MIT (Sergey Bulaev) | 47 file, mã gate ~1.200 dòng JS | **Rất cao**: cơ chế "AI viết, mã chấm, vòng sửa", danh sách dấu hiệu, giới hạn nền tảng, kịch bản UGC, giao kịch bản cho editor | A |
| `kanishkkatara/omniwrite` | Pipeline agent: brief → nghiên cứu → chiến lược → dàn ý (có duyệt) → viết song song (blog/Reddit/LinkedIn/bình luận) → biên tập | MIT (file LICENSE) | 126 file | **Cao**: tách bước, hồ sơ thương hiệu, prompt riêng từng nền tảng, cổng duyệt dàn ý, biên tập tối thiểu | A- |
| `bikram73/SocialSpark_AI` | Brief thương hiệu → kế hoạch 7 ngày đa nền tảng (caption, hashtag, giờ đăng, CTA, mẹo tương tác) | Không có file LICENSE | 42 file, `server.ts` 720 dòng | Trung bình: lược đồ một bài trong lịch, chuẩn hoá sau LLM, chặn hashtag chung chung, nhãn "AI hay dự phòng" | B |
| `tvcnet/social-toolkit` | Một file HTML: khung 5W → bài đăng cho 7–8 nền tảng, có "reroll" theo giới hạn, lịch + CSV | README: miễn phí **phi thương mại** (không phải giấy phép chuẩn) | 17 file | Trung bình: bảng giới hạn ký tự + giọng từng nền tảng, hậu xử lý xác định | B |
| `tubaarif-dev/content-craft` | Video / audio → (cắt 1 phút) → STT → bài đăng, blog, newsletter | README ghi MIT, **không có** file LICENSE | 55 file | Trung bình-thấp: luồng video→bài đăng gần nhất với vedit; danh sách ràng buộc "đừng giống AI" | B- |
| `taha-rafi/shortgenie` | Chủ đề → kịch bản Shorts theo cảnh + tiêu đề / mô tả / tag + prompt ảnh + giọng đọc (Gemini) | README ghi MIT, **không có** file LICENSE | 12 file, `gemini.ts` 179 dòng | Thấp-trung bình: lược đồ JSON kịch bản; quy tắc ~1 cảnh / 5 giây | C+ |
| `mituljn14/LangGraph-AI-Content-Generator` | Đồ thị LangGraph: định tuyến blog / caption / tóm tắt + chế độ tinh chỉnh + tạo lại | README ghi MIT, **không có** file LICENSE | 12 file, `prompts.py` 158 dòng | Thấp: mẫu prompt "tinh chỉnh" và "tạo lại bản KHÁC" | C |
| `Xsolai/postforge-ai` | Mô phỏng giao diện SaaS (Next.js) cho lịch / duyệt / chấm điểm bài | **All rights reserved** (NOTICE.txt); dữ liệu mô phỏng | 49 file, gần như toàn UI | Rất thấp: mô hình dữ liệu hàng đợi (trạng thái, điểm, giới hạn ký tự) | C |
| `tejasvinifulari5/ai-ugc-generator` | Mô tả "SaaS tạo quảng cáo UGC bằng Gemini" | Không có | **1 file README 2 dòng**, không có mã / prompt | **Không có gì để học** — ghi nhận là repo rỗng | — |

Hệ quả giấy phép: chỉ hedgehog-core và omniwrite có giấy phép MIT rõ ràng; ngay cả vậy ghi chú này **tóm tắt và diễn đạt
lại**, không chép prompt dài. Với repo còn lại chỉ lấy ý tưởng / cấu trúc.

## Mỗi repo làm tốt / thiếu bước nào

Các bước: brief → ý tưởng / góc → dàn ý → bản nháp → **kiểm tra** → chuyển thể nền tảng → lịch.

| Repo | Làm tốt | Thiếu |
|---|---|---|
| hedgehog-core | Brief có `type:` quyết định hợp đồng; **kiểm tra bằng mã** + vòng sửa tối đa 6 lần; chuyển thể = hợp đồng định dạng (giới hạn, CTA, tuyên bố bị cấm) | Không lập lịch / đăng ("what comes out is a file that exited 0"); không có chuỗi bài (thread); chỉ tiếng Anh |
| omniwrite | Brief có câu hỏi làm rõ, nghiên cứu, chiến lược (góc + hook), dàn ý có cổng duyệt, viết song song, biên tập chéo nền tảng | Kiểm tra sự thật yếu (biên tập chỉ thấy 800 ký tự tóm tắt); không có cổng chống văn AI bằng mã; không có lịch |
| SocialSpark | Lịch 7 ngày: nền tảng, định dạng, giờ, CTA, hashtag, mẹo; tạo lại từng ngày | Prompt dán thẳng đầu vào người dùng; giờ đăng "tối ưu" không có căn cứ; không có kiểm tra văn AI |
| social-toolkit | Giới hạn theo nền tảng, reroll, lịch + CSV, hậu xử lý | Bắt LLM tự đếm ký tự; ép "viết đủ giới hạn" (đệm chữ); nhiều emoji |
| content-craft | Video → transcript → bài đăng; ràng buộc "đừng nói mình là AI, đừng mở bằng 'Here are your posts'" | STT cố định `en-US`; không kiểm tra; lỗi tách bài theo dòng |
| shortgenie | Kịch bản theo cảnh có JSON schema; đo thời lượng giọng đọc thật | Không có kiểm tra sự thật hay văn AI; "viral" là mục tiêu duy nhất; không có tiếng Việt |
| mituljn14 | Định tuyến loại nội dung; tinh chỉnh / tạo lại | Prompt chung chung ("expert blog writer"), không có kiểm tra |
| postforge | Mô hình hàng đợi + trạng thái + điểm | Toàn dữ liệu giả (README tự nhận "simulated") |
| ai-ugc-generator | — | Không có |

## Áp dụng vào vedit

Đối chiếu `.claude/agents/video-content-creator.md` (Agent 4) và `video-scriptwriter.md` (Agent 2).

**Agent 4 đã có**: quy trình 7 bước (brief → ý tưởng → hook → nháp → cổng chống văn AI → gói đăng bài → series), bảng thời
gian / lời / chữ, `vedit note`, luật không bịa số liệu. Điểm mạnh này khớp với hầu hết repo.

**Thiếu so với các repo** (theo thứ tự ưu tiên):
1. Cổng kiểm văn **bằng mã** (hedgehog-core) — Agent 4 hiện tự đọc lại rồi tự chấm, đúng điều hedgehog cảnh báo là không đủ. Chi tiết:
   `cong-chat-luong-chong-van-ai-va-bang-tieng-viet`.
2. Hồ sơ giọng kênh có cấu trúc (omniwrite `BrandProfile`) — hiện `profile/gu-nguoi-dung.md` là văn xuôi.
3. Hợp đồng theo định dạng (TikTok caption, lời thoại, chữ trên màn hình, tiêu đề Shorts, bài Facebook...) với giới hạn
   ký tự và lỗi / cảnh báo.
4. Cách giao kịch bản cho editor tối giản (hedgehog `direct-response-copy`): lời là sản phẩm chính, ghi chú dựng ít.
5. Quy tắc đề phòng chèn lệnh khi đọc transcript / trang web (xem file lỗi & rủi ro).

**Repo nên đọc sâu thêm** (nếu cần): hedgehog-core (`workspace/scripts/check-copy/rules/` và 4 skill định dạng) và omniwrite
(`backend/agents/`, `backend/plugins/`). Các repo còn lại đã khai thác gần hết.
