---
title: Khung viết hook, kịch bản, caption, hashtag và UGC
category: content
tags: [hook, kịch bản, caption, hashtag, UGC, quảng cáo, voiceover, agent-4]
updated: 2026-11-04
sources:
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/skills/ad-copy/SKILL.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/skills/direct-response-copy/SKILL.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/skills/tweet-copy/SKILL.md
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/core/prompts/platforms/linkedin.yaml
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/core/prompts/platforms/linkedin_comment.yaml
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/core/prompts/platforms/reddit.yaml
  - https://github.com/kanishkkatara/omniwrite/blob/HEAD/backend/core/prompts/agents/strategy.yaml
  - https://github.com/taha-rafi/shortgenie/blob/HEAD/services/gemini.ts
  - https://github.com/mituljn14/LangGraph-AI-Content-Generator/blob/HEAD/prompts/prompts.py
  - https://github.com/bikram73/SocialSpark_AI/blob/HEAD/server.ts
  - https://github.com/tubaarif-dev/content-craft/blob/HEAD/server/services/generatePosts.js
  - https://github.com/tvcnet/social-toolkit/blob/HEAD/assets/js/tst-config.js
---
# Khung viết hook, kịch bản, caption, hashtag và UGC

Tóm tắt: chắt **nguyên tắc + khung** từ các prompt / skill; không chép nguyên văn. Phần lớn chất liệu tốt nằm ở
hedgehog-core (4 skill định dạng); các skill này ghi rõ được chuyển thể từ kỹ năng copywriting của Rob Palmer (CC BY 4.0) và
`x-post-writer` của Sergey Bulaev (MIT), nên khi lấy ý thì ghi nguồn. Ví dụ tiếng Việt bên dưới là **do người ghi chú viết
mới**, không có trong repo. Ý "ánh xạ sang TikTok" là suy luận, đánh dấu *(suy luận)*.

Bổ sung cho `knowledge/scripting/cong-thuc-hook-3-giay-dau` và `cau-truc-kich-ban-video-ngan-15-60-giay` (đã có 6 dạng hook
và khung 5 phần); ghi chú này thêm *khi nào dùng dạng nào*, kiểm tra sau khi viết, và cách giao kịch bản.

## 1. Hook

### 1.1 Tám dạng hook và khi dùng (`ad-copy/SKILL.md:207-218`)

| Dạng | Hình dạng | Dùng khi người xem… | Ví dụ viết mới (VN) |
|---|---|---|---|
| Tò mò | Giữ một lỗ hổng thông tin | chưa biết vấn đề | "Có một mẹo muối cà mà bà tôi không bao giờ kể" |
| Phản biện | Đi ngược điều ai cũng tin | đã biết vấn đề, hoài nghi | "Rửa gạo ba lần là sai — đây là lý do" |
| Bằng chứng xã hội | Con số người đã làm | đã biết giải pháp | "312 người đã thử cách này, chỉ 9 người bỏ" *(số minh hoạ — chỉ dùng số có thật)* |
| Câu chuyện | Mở giữa lúc đang khổ | thị trường cảm xúc | "Tháng trước tôi đổ nguyên mẻ cà vì một cái nắp" |
| Gọi đích danh nhóm | "Dành cho ai …" | nhắm hẹp | "Ai hay bị mất nước muối giữa chừng, xem đây" |
| Kết quả trước | Thành phẩm / số đo | đã ấm, retarget | "Mẻ này: 14 ngày, không một chấm mốc" |
| Ngắt mạch | "Dừng lại, cái này đáng xem" | thị trường bão hoà | (hình / âm đột ngột thay vì chữ) |
| Sự thật thú vị | Một dữ kiện lạ | chưa biết, thích học | "Cà pháo muối mặn hơn nước biển mà vẫn giòn" *(chỉ dùng nếu đúng)* |

*(suy luận)* Các dạng này trùng 6 dạng đã có trong kho; điểm thêm là cột "khi dùng": mức hiểu biết của khán giả quyết định
dạng hook. Repo dùng 5 mức nhận thức của Schwartz (chưa biết → biết vấn đề → biết giải pháp → biết sản phẩm → sẵn sàng mua)
để quyết định mở bằng gì, độ dài và nơi đưa người xem đến (`ad-copy/SKILL.md:153-175`): người **chưa biết** thì mở bằng danh
tính / cảm xúc, người **sẵn sàng mua** thì mở bằng ưu đãi. Video TikTok đến người lạ → thường là "chưa biết / biết vấn đề".

### 1.2 Luật hook (tổng hợp `ad-copy/SKILL.md:219-236`, `tweet-copy/SKILL.md:110-123`)

1. **Dòng đầu / 3 giây đầu phải đứng được một mình.** Phép thử của repo: đọc riêng dòng đầu — nếu nó chỉ là "dạo đầu cho dòng 2"
   thì viết lại. Mở bài "dạo đầu" chính là lỗi.
2. **Giữ hở, đừng giải hết.** Khơi gợi mảnh nhỏ cho người xem muốn biết tiếp; hé lộ đầy đủ là đóng vòng, hết lý do xem tiếp.
3. **Cụ thể.** Con số lẻ tạo cảm giác "đã đếm", số tròn tạo cảm giác "nói phóng". Ràng buộc đi kèm: **không làm tròn lên,
   không bịa ca điển hình** (`tweet-copy` mục X11). Con số lẻ phải có nguồn trong `facts.md`.
4. **Nói điều nó *không* phải để làm nổi điều nó là** ("không phải diet, không phải thuốc, không phải tập luyện…").
   Cẩn thận: đây là biến thể của công thức phủ định mà cổng chống văn AI bắt — chỉ dùng với chi tiết cụ thể, không dùng khuôn
   "không chỉ … mà còn".
5. **Gợi ý một chi tiết riêng** ("nhỏ hơn đồng xu", "chỉ mọc trên 2.000 m") thay cho tính từ.
6. Hook thắng có thể sống nhiều tháng — thử hook mới song song với hook thắng, đừng thay hết.
7. Tránh sáo ngữ quảng cáo: "đừng bỏ lỡ", "bạn sẽ không tin", "nâng tầm … lên một tầm cao mới", "bạn đã sẵn sàng chưa?"
   (danh sách "ad clichés" ở `ad-copy/SKILL.md:401-402`).

### 1.3 Chọn hook theo mục tiêu (tweet-copy, 7 khuôn X1–X11; `tweet-copy/SKILL.md:125-231`)

Repo ghép khuôn với mục tiêu: **trả lời** ← tự thú xây dựng công khai, quan điểm đối lập; **chia sẻ lại** ← quan điểm đối lập,
thêm lớp cho quan điểm của người khác, ca thật của người khác; **thích** ← khoảnh khắc đời thường kể ở thì hiện tại; **lưu**
← một con số lẻ, danh sách ngắn, ca nghiên cứu. "Nhắm cả bốn là nhắm vào không ai."

*(suy luận, ánh xạ sang mục tiêu trong brief Agent 4)*: bình luận ← tự thú / phản biện / câu hỏi cần kiến thức để trả lời;
chia sẻ ← phản biện, "ai cũng nên biết", ca thật; thích / xem hết ← POV, khoảnh khắc đời thường; **lưu** ← checklist, con
số, quy trình, công thức. Mỗi nội dung chọn **một** mục tiêu.

Khuôn tiêu biểu (diễn đạt lại):
- *Con số lẻ*: [số + đơn vị + phạm vi] → [nghĩa của nó, một dòng] → [hệ quả với người xem].
- *Tự thú*: [con số thẳng, không làm mềm] → [mình đã làm gì tạo ra nó] → [mình đổi gì]. Điều kiện: lời thú phải **tốn kém** thật; khoe khéo thì hỏng.
- *Ca của người khác*: [Ai] đã làm [việc cụ thể] và được [kết quả cụ thể] → [cơ chế, một dòng] → [vì sao chép được / không].
- *Quan điểm đối lập*: chỉ dùng nếu nêu được người phản đối; không thì đừng gắn mác "unpopular opinion"
  (`format/false-contrarian`).
- *Khoảnh khắc đời thường*: một chi tiết giác quan, không "ai cũng từng như vậy".

## 2. Kịch bản video ngắn

### 2.1 Cấu trúc UGC / talking head (`ad-copy/SKILL.md:328-365`)

Khung gốc cho 15–60 giây: `HOOK 0–3s` (ngắt mạch, câu hỏi, tuyên bố mạnh) → `VẤN ĐỀ 3–10s` (nêu nỗi đau đủ cụ thể để gật đầu) →
`CƠ CHẾ 10–25s` (hé lộ phát hiện, giải thích vừa đủ, có cảnh minh hoạ) → `KẾT QUẢ 25–40s` (biến đổi kèm số) → `CTA 40–60s`
(kết như lời khuyên của bạn bè). Bản kể chuyện 60–120 giây: mở giữa lúc đang vật lộn → các lần thử thất bại → bước ngoặt →
kết quả có số và mốc thời gian thật → kết bằng lời khuyên, không bằng lời chào hàng.

*(suy luận, áp cho TikTok 15–30 giây)*: nén tỷ lệ — hook 0–2s, vấn đề + cơ chế gộp 2–12s, kết quả 12–22s, CTA 1 câu; không đủ chỗ cho 5 phần
đầy đủ thì bỏ "vấn đề" (hook đã nói). Kiểm tra nhịp với `vedit kb show techniques/nhip-cat-va-ky-thuat-giu-chan-nguoi-xem`.
Shortgenie mặc định ~1 cảnh / 5 giây (`gemini.ts:44-45`: số cảnh ≈ thời lượng / 5) — **chậm hơn** nhịp TikTok của kho này; chỉ
dùng làm chặn trên số "ý" (mỗi 5 giây ≤ 1 ý mới), không làm nhịp cắt.

### 2.2 Cấu trúc WHY / WHAT / HOW (`ad-copy/SKILL.md:273-298`)

- **WHY (vấn đề)**: mở bằng tò mò hoặc phản biện, gọi tên vấn đề, khuấy nó lên.
- **WHAT (cơ chế)**: chuyển sang cách giải pháp hoạt động, hé lộ mà chưa giải hết.
- **HOW (sản phẩm + CTA)**: lộ vừa đủ để bấm là bước hiển nhiên; CTA viết thành lợi ích khi bấm, dùng động từ mệnh lệnh.

Cơ chế tốt: đáng tin (có nguồn có thẩm quyền), hiếm / khó tìm, nhỏ và cụ thể ("mẹo 7 giây" thắng "quy trình 20 phút"), ít công sức.

### 2.3 Bốn việc kiểm trước khi giao (cổng không bắt được)

Từ danh sách "last pass" (`ad-copy/SKILL.md:422-430`): (1) dòng đầu có chặn được ngón tay lướt không; (2) mỗi tuyên bố gắn một
con số / bằng chứng cụ thể; (3) nghe như người nói; (4) có vòng mở kéo tới cuối; (5) về **biến đổi của người xem** hay về sản
phẩm; (6) nhịp có xen câu gọn và chỗ thở; (7) CTA là lợi ích, không phải lệnh trần. Và **chuỗi "Thì sao?"** (`ad-copy:299-327`):
hỏi "thì sao?" ba tầng từ tính năng tới cảm xúc / tiền: "database nhanh → truy vấn mất mili giây → người dùng không rời đi →
bạn đỡ thức đêm lo mất khách". Câu chữ nằm ở tầng ba ("đóng laptop lúc 5 giờ chiều thay vì 9 giờ tối" thắng "tiết kiệm 4 giờ / tuần").

**Phép thử giọng thật** (`ad-copy/SKILL.md:361-365`): một người thật có nói câu này thành tiếng, vào camera điện thoại của mình, không?
Nghe như copywriter viết thì viết lại. Kịch bản UGC nên hơi "không hoàn hảo" mới đáng tin. Giọng: ngôi thứ nhất, chuyện trò, vài
tiếng đệm tự nhiên ("thật ra", "nói thật", "mình nghĩ"), chi tiết cụ thể, CTA như lời khuyên.

### 2.4 Giao kịch bản cho editor: lời thoại là sản phẩm chính (`direct-response-copy/SKILL.md:422-480`)

Đây là phần liên quan nhất tới vedit (Agent 4 → Agent 2/3).

- Editor đọc ghi chú trong ngoặc như **mệnh lệnh** chứ không phải gợi ý. Kịch bản đầy `[CUT TO]`, `[B-ROLL]`, `[TRANSITION]` trên
  mỗi dòng đọc như hợp đồng → editor phải họp để chốt trước khi cắt. Kịch bản trông kỹ hơn lại chậm hơn.
- **Mặc định là chỉ lời đọc**: đoạn văn thường, ngắt chỗ người nói thở; không đặt nhãn "Hook / Vấn đề / Lời hứa" trong chính kịch bản (nếu cần thì một
  dòng chú ở đầu).
- Chỉ thêm ghi chú hình ảnh khi: (a) một con số / tuyên bố / trích dẫn **phải hiện trên màn hình** thì người xem mới nhận (giá,
  thống kê, điều khoản, URL); (b) một cảnh sản phẩm / ghi màn hình / tư liệu cụ thể phải rơi đúng thời điểm mà âm thanh không
  nói rõ; (c) nhịp hài / kịch tính phụ thuộc thời điểm hình (lật, cắt cứng, dừng hình); (d) B-roll không hiển nhiên đến mức
  thiếu nó thì câu nghĩa khác đi.
- Quy ước: ghi chú một dòng, thẻ IN HOA trong ngoặc: `[ON-SCREEN: "4 giờ = 1.460 giờ / năm"]`, `[B-ROLL: ...]`, `[PRODUCT SHOT]`.
  Ghi chú cần cả đoạn giải thích thì nói thẳng với editor, đừng nhét vào kịch bản.
- Mặc định đừng đưa shot list / kịch bản quay, trừ khi người dùng yêu cầu; hỏi xác nhận.

### 2.5 Lược đồ kịch bản gọn (shortgenie, `gemini.ts:63-87`)

Kịch bản = `title`, `description` (có hashtag), `tags[]`, `scenes[{id, script, imagePrompt}]`. Prompt chỉ rõ: lời đọc theo ngôn ngữ
đích, `imagePrompt` luôn tiếng Anh (cho mô hình ảnh), tiêu đề gây chú ý, mô tả giàu, danh sách tag, cấu trúc Hook – Thân – Kết với CTA mạnh.
Nhược: không có kiểm sự thật, đặt mục tiêu "viral", nhiệt độ 1.0, không có tiếng Việt trong danh sách ngôn ngữ (`types.ts`). Điểm
đáng lấy: **đo thời lượng giọng đọc thật** sau khi tạo (`gemini.ts:161-164`: byte PCM chia tốc độ lấy mẫu) rồi mới khớp với cảnh,
thay vì tin vào ước tính chữ / giây.

## 3. Caption

### 3.1 Nguyên tắc chung

- **Dòng đầu là hook độc lập**, vì phần sau bị cắt sau dấu "xem thêm". Quảng cáo Meta: **125 ký tự đầu** là cả quảng cáo với đa
  số lượt hiển thị (`ad.mjs:22, 63-77`); LinkedIn prompt của omniwrite: người đọc chỉ thấy dòng đầu trước "xem thêm"
  (`linkedin.yaml:9`). Agent 4 hiện dùng "câu đầu < 100 ký tự" — an toàn hơn, giữ.
- Kết thúc phần hiển thị bằng câu trọn vẹn **hoặc** một vòng mở; đừng cắt giữa ý. Cổng của repo cảnh báo khi 125 ký tự đầu kết thúc giữa ý.
- Một ý một bài. Ý thứ hai ăn mất chú ý của ý đầu — cũng là cách sửa rẻ nhất khi vượt giới hạn ký tự (`tweet-copy/SKILL.md:234`).
- Xuống dòng là nhịp thở: đặt chỗ cần ngừng, không đặt trang trí.
- Một con số cụ thể nếu tuyên bố cho phép; không có số thì một thực thể có tên (công cụ, nơi chốn, phiên bản).
- Kết bằng câu **hạ cánh**: câu sắc nhất, hoặc câu hỏi đủ cụ thể để trả lời cần phải biết điều gì ("Bạn muối bao nhiêu phần trăm
  muối?" thắng "Bạn nghĩ sao?").
- Emoji: tối đa 1 (tweet-copy), 0–3 (LinkedIn omniwrite), 1–2/bài (content-craft); **không** emoji cho quan điểm nghiêm túc / phản biện.
  Các repo kia ép 8–12 emoji cho Instagram và 6–10 cho Facebook (`tst-config.js:38-45`) — đó là mẫu *cần tránh* (đồng phục).
- Không đệm cho đủ giới hạn: social-toolkit đặt "khoảng mục tiêu 240–280 ký tự" cho X, 1.800–2.200 cho Instagram (`tst-config.js:38-45`);
  hedgehog xếp "độn một ý một dòng cho trông đồ sộ" vào danh sách lỗi (`tweet-copy` mục Anti-patterns). Nếu ý chỉ một dòng, đăng một dòng.

### 3.2 Bình luận ghim / bình luận đầu tiên (`linkedin_comment.yaml`)

Bốn mục đích: thêm tài nguyên / link làm rối bài chính; bối cảnh / giai thoại; câu hỏi nối để mồi thảo luận; một thống kê / trích
dẫn củng cố. Luật: **cùng giọng** với bài chính; ngắn (prompt đặt 50–120 từ, ví dụ dưới 100); như bước tiếp tự nhiên, không phải quảng
cáo; mở bằng ý nối với bài (không "Ngoài ra…", "À tiện thể…"); link để `[link]` giữ chỗ; cấm "like và follow để xem thêm". Với TikTok
ngắn hơn nhiều, giữ nguyên *mục đích* và *giọng*, rút độ dài. *(suy luận)*

### 3.3 Caption Reddit-style (nếu cần cộng đồng, `reddit.yaml:8-30`)

Tiêu đề tò mò / có giá trị ngay; thân ≤ 600 từ, đoạn 2–4 câu; có `TL;DR` 1–2 câu; không hashtag, không quảng cáo lộ liễu, "nghe như
mình vừa khám phá điều hay và muốn kể". Dành cho nội dung dài (bài đăng nhóm), không dùng cho caption video.

## 4. Hashtag — các repo mâu thuẫn nhau, **không repo nào có bằng chứng đo**

| Nguồn | Số hashtag | Ghi chú |
|---|---|---|
| hedgehog (X) | ≤ 1 (error nếu hơn) | Lập luận: chồng hashtag trông như "đuổi tiếp cận" và bị hạ thứ hạng (`tweet.mjs:42-49`; chưa kiểm chứng ngoài repo) |
| omniwrite (LinkedIn) | 0, hoặc 3–5 ở cuối | `linkedin.yaml:13` |
| content-craft | 2–3 / bài, không quá 3 liền nhau | `generatePosts.js:90-94, 106` |
| mituljn14 | 3–6 | `prompts.py:55`; "tránh chung chung và quá nhiều" |
| SocialSpark | README: Instagram 5–8; prompt: **6–10** cho mọi bài, ≥ 4 liên quan chủ đề, 1 hashtag thương hiệu, tránh #Strategy #GrowthMindset... | README và prompt tự mâu thuẫn (`README.md` mục Features vs `server.ts` phần HASHTAG RULES); hàm `sanitizeHashtags` lọc trùng / chung chung / đủ số (`server.ts:50-`) |

Điểm đúng hướng (nên giữ): (a) **cơ cấu** = vài tag đúng chủ đề + một tag thương hiệu / series, có lý do từng tag; (b) **chặn tag
chung chung** (danh sách cấm ghi cụ thể); (c) lọc bằng hàm xác định, không nhờ LLM. Số lượng tối ưu thì chưa có bằng chứng — giữ 3–6
như Agent 4 hiện đặt và đánh dấu "giả định cần đo".

**Lỗi dành riêng tiếng Việt**: `sanitizeHashtags` bỏ ký tự ngoài `[a-zA-Z0-9]` (`server.ts:56`), nên tên "Bếp Việt" thành "BpVit" — xoá mất chữ có
dấu thay vì chuyển không dấu. Khi tự viết hàm: chuẩn hoá NFD, bỏ dấu (đ → d), bỏ khoảng trắng, rồi hạ chữ thường; hoặc giữ nguyên Unicode
có chủ đích và ghi rõ.

## 5. Mẫu prompt: nguyên tắc rút ra (không chép nguyên văn)

- **Tách "ý" khỏi "chữ"** (omniwrite `strategy.yaml`): sinh N *khái niệm* hook khác nhau trước, rồi mới viết câu chữ cho khái niệm đã chọn.
- **Danh sách phủ định cụ thể** (SocialSpark `server.ts` phần CRITICAL CONTENT RELEVANCE RULES): nêu rõ vài câu mẫu KHÔNG được viết
  ("game-changing insights", "industry evolution"…) hiệu quả hơn "đừng chung chung". Mỗi bài phải gắn ít nhất một chủ đề (≥ 5/7 bài).
- **Ràng buộc đầu ra** (content-craft `generatePosts.js:79-106`): không nhắc mình là AI; không mở bằng "Here are your posts…"; không kết bằng "Hope this
  helps"; không đánh số / gạch đầu dòng; câu phải khác nhau về cấu trúc giữa các bài; **không đưa ý ngoài transcript**; không
  dùng ngày giờ trừ khi được cung cấp. Lưu ý repo cũng tự mâu thuẫn: lớp bọc ngoài bảo "giọng chuyên nghiệp, hữu ích" trong khi prompt bảo "giọng bình dân"
  (`generatePosts.js:115` vs `:84`) — mỗi lần chỉ một giọng.
- **Tạo lại ≠ làm lại**: truyền bản trước + yêu cầu khác góc, cấu trúc, mở đầu (`prompts.py:103-112`).
- **Tinh chỉnh = sửa đúng yêu cầu**: giữ thông tin hữu ích, giữ loại và giọng (`prompts.py:83-101`).
- **Đừng nhờ LLM đếm ký tự**: social-toolkit bảo model nhắm thấp hơn giới hạn 25 ký tự "vì đếm sai" (`tst-content.js:49`) — rõ ràng là
  nên đếm bằng mã (`vedit content check`).
- **UGC ≠ quảng cáo**: Reddit / UGC: "nghe như vừa khám phá điều hay", CTA như lời khuyên, kịch bản hơi không hoàn hảo.

## Áp dụng vào vedit

**Đã có**: Agent 4 đã đặt hook ≥ 3 phương án (tò mò, mâu thuẫn, kết quả trước, câu hỏi, con số, POV, thử thách), hook đọc ≤ 1,5 giây,
nhịp lời 2,5–3,5 từ/giây, chữ ≤ 6–8 từ/dòng, 3 phương án caption với câu đầu < 100 ký tự, 3–6 hashtag có lý do, bình luận ghim.
Kho `scripting/` đã có 6 dạng hook và khung 5 phần.

**Thiếu / đề xuất theo ưu tiên**:
1. **Giao kịch bản kiểu "lời trước, ghi chú ít"** vào cuối Agent 4: bảng `Thời gian | Lời | Chữ trên màn hình` giữ nguyên, nhưng thêm luật
   "ghi chú hình ảnh chỉ khi (a)–(d) của mục 2.4; ghi `đề xuất cho Agent 2`, không ra lệnh cắt / chuyển cảnh". Tránh trùng lặp với
   `video-scriptwriter.md` (Agent 2 sở hữu quyết định dựng).
2. **Cột "khi dùng" cho hook** theo mức nhận thức khán giả và **một mục tiêu cho mỗi nội dung** (mục 1.3) trong bước 3 của Agent 4.
3. **Phép thử giọng thật** + bảy câu "last pass" (mục 2.3) thành checklist cuối của bước 5 (phần cổng không bắt được).
4. **Quy tắc caption**: dòng đầu hook độc lập, một ý một bài, hạ cánh bằng câu hỏi cụ thể, **cấm đệm cho đủ giới hạn**, emoji ≤ 1–3.
5. **Hàm hashtag xác định** (`vedit content hashtags`?) chuẩn hoá tiếng Việt (NFD → bỏ dấu, đ → d), lọc trùng, chặn tag chung chung
   từ file danh sách, đếm giới hạn; Agent 4 chỉ chọn lý do.
6. Ghi trong `post.md` mục tiêu duy nhất + dạng hook + mức nhận thức khán giả, để agent phản biện soi "hook có hợp mục tiêu không".
7. Chưa có số liệu cho hashtag / giờ đăng: ghi "giả định cần đo", không viết như sự thật.
