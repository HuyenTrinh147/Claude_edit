---
title: Cổng chất lượng chống văn AI và bảng tiếng Việt
category: content
tags: [chống văn AI, hedgehog-core, tells, burstiness, cổng kiểm tra, tiếng Việt, agent-4]
updated: 2026-11-04
sources:
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/README.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/ARCHITECTURE.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/CLAUDE.core.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/skills/tells-detector/SKILL.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/skills/prose-quality/SKILL.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/skills/hedgehog-copywriting-loop/SKILL.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/agents/copy-writer.md
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/workspace/scripts/check-copy/index.mjs
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/workspace/scripts/check-copy/report.mjs
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/workspace/scripts/check-copy/rules/tells.mjs
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/workspace/scripts/check-copy/rules/prose.mjs
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/workspace/scripts/check-copy/rules/formats/shared.mjs
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/workspace/scripts/check-copy/rules/formats/ad.mjs
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/workspace/scripts/check-copy/rules/formats/tweet.mjs
  - https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering/blob/HEAD/workspace/scripts/check-copy/rules/formats/direct-response.mjs
  - https://github.com/tvcnet/social-toolkit/blob/HEAD/assets/js/tst-content.js
---
# Cổng chất lượng chống văn AI và bảng tiếng Việt

Nguồn chính: `skyf0xx/hedgehog-core-copywriting-prose-engineering` (MIT). Đây là repo duy nhất trong topic có **cổng kiểm
bằng mã** thật. Phần "bảng tiếng Việt" là **đề xuất của người ghi chú** (dựa trên hiểu biết về văn phong tiếng Việt do AI
sinh, **chưa kiểm chứng trên kho văn bản thật**); mỗi mục ghi mức tin cậy. Cần hiệu chỉnh bằng mẫu người viết thật trước khi
đặt thành lỗi chặn.

## 1. Ý tưởng cốt lõi: người viết không được tự chấm

README của repo nói thẳng: mô hình viết đồng thời tự kiểm thì người dùng thành người kiểm; kiểm bằng mã thì không bỏ sót
chi tiết. Luật nền (`CLAUDE.core.md`, mục "Core rule"): **"Đạt" là mã thoát 0, không phải một câu nhận xét** — không ai
giao bản nháp vì "đọc thấy sạch".

- Cổng là CLI: `node index.mjs <file> [--format <loại>]`, thoát 0 khi không có lỗi mức *error*, thoát 1 nếu có
  (`index.mjs:1-15, 101-103`); thoát 2 nếu `--format` lạ (không âm thầm rơi về mặc định).
- Báo cáo JSON (`report.mjs:20-54`): `pass`, `errorCount`, `warningCount`, `violations[{rule, severity, grain, excerpt}]`,
  `metrics{format, wordCount, sentenceCount, paragraphCount, fleschReadingEase, ..., passiveVoiceRatio, sentenceLengthStdDev}`.
  `pass = (errorCount == 0)`: **cảnh báo không chặn**.
- Hai hợp đồng chung luôn chạy: `tells` (dấu hiệu AI) và `prose` (chất lượng văn). Hợp đồng **định dạng** chỉ *thêm*, không
  bao giờ nới (`ARCHITECTURE.md`, `formats/shared.mjs:9-11`): "không loại bài nào được phép giống LLM hơn chỉ vì nó đăng ở đâu".
- Lý do có hợp đồng định dạng: trước đó một "tweet" 446 ký tự với 5 hashtag, hay quảng cáo Meta có headline 81 ký tự hứa "kiếm
  tiền nhanh, không rủi ro", vẫn qua cổng 0 lỗi — vì câu chữ không có gì sai (`SKILL.md` của loop, mục "Copy types").
- **Tần suất mới là tín hiệu, sự hiện diện thì chưa chắc** (`tells.mjs:9-15`): từ cấm và cụm cấm bị bắt ở *mọi* lần xuất hiện;
  các kiểu cấu trúc (bộ ba, header Title Case) chỉ cảnh báo khi vượt ngưỡng trong cả tài liệu.

## 2. Dấu hiệu văn AI mà `tells.mjs` bắt (tiếng Anh) → đề xuất tương đương tiếng Việt

Mức độ trong repo: **error** = chặn; **warning** = nhắc. Cột "VN đề xuất" là mức *khuyến nghị cho tiếng Việt*, không phải
của repo.

### 2.1 Từ vựng và cụm sáo rỗng

`BANNED_WORDS` (`tells.mjs:17-30`, 64 từ, error ở *mọi* lần): delve, tapestry, robust, seamless, leverage, crucial,
pivotal, elevate, unlock, empower, foster, showcase, landscape, holistic, comprehensive, cutting-edge, transformative,
groundbreaking, innovative, game-changer, harness, revolutionize, streamline, ecosystem, synergy, myriad, nuanced, dynamic...
Repo tự thừa nhận từ này đúng trong văn kỹ thuật (ví dụ "robust" trong thống kê) và dặn nâng vấn đề lên người dùng, đừng lách
(`tells-detector/SKILL.md` mục "When a violation looks wrong").

| Dấu hiệu EN (repo) | Tương đương tiếng Việt (đề xuất) | VN đề xuất | Tin cậy |
|---|---|---|---|
| Từ "đỉnh cao" rỗng: innovative, cutting-edge, groundbreaking, game-changer, transformative | "đột phá", "cách mạng hoá", "mang tính cách mạng", "đỉnh cao", "tuyệt vời", "hoàn hảo", "đẳng cấp", "thế hệ mới" khi không kèm bằng chứng | warning khi ≥ 2 trong một bài; error trong hook / tiêu đề | Cao |
| Động từ "nâng tầm": elevate, unlock, empower, harness, unleash, revolutionize | "nâng tầm", "nâng cao trải nghiệm", "mở khoá / khai phá / khai mở tiềm năng", "trao quyền", "kiến tạo", "định hình", "bứt phá" | warning; đổi bằng hành động cụ thể | Cao |
| Danh từ trang trọng rỗng: landscape, ecosystem, tapestry, realm, beacon, cornerstone, journey | "bức tranh toàn cảnh", "hệ sinh thái", "thế giới của …", "hành trình", "kim chỉ nam", "nền tảng vững chắc" | warning | Trung bình ("hành trình" đôi khi đúng nghĩa) |
| Tính từ "toàn diện": comprehensive, holistic, multifaceted, nuanced, meticulous, vibrant | "toàn diện", "đa chiều", "đa dạng và phong phú", "sâu sắc", "tỉ mỉ", "sống động", "tinh tế" | warning khi ≥ 2 | Trung bình |
| Từ nối kiểu bài luận: moreover, furthermore | "hơn nữa", "ngoài ra", "bên cạnh đó", "đồng thời" mở nhiều câu liên tiếp | warning khi ≥ 3 lần / bài | Trung bình |
| Từ tăng cường mơ hồ (`prose/weasel-word`): very, quite, arguably | "rất", "vô cùng", "cực kỳ", "thực sự", "hoàn toàn", "khá", "tương đối", "có lẽ" | warning theo mật độ (≥ 1 / 25 tiếng) | Trung bình |

`BANNED_PHRASES` (`tells.mjs:32-43`, error): "it's important/worth noting that", "at its core", "when it comes to", "in the
realm of", "plays a vital role in", "delve into the intricacies", "in today's fast-paced world", "unlock the potential of",
"in conclusion", "in summary", "I hope this helps", "studies show", "experts agree", "research suggests", "the future looks
bright", "only time will tell".

| Cụm EN (repo) | Tương đương tiếng Việt (đề xuất) | VN đề xuất |
|---|---|---|
| in today's fast-paced world | "trong thế giới ngày nay", "trong thời đại ngày nay", "trong bối cảnh hiện nay", "trong xã hội hiện đại", "cuộc sống hối hả" | **error** ở mở đầu; warning ở giữa bài |
| delve into / explore | "hãy cùng khám phá", "hãy cùng tìm hiểu", "cùng đi sâu vào", "cùng điểm qua", "cùng nhau" + động từ khám phá | warning (lời thoại TikTok: nhắc, đừng chặn — xem lưu ý dưới bảng) |
| it's important/worth noting that | "điều quan trọng cần lưu ý là", "cần lưu ý rằng", "đáng chú ý là", "một điều cần nhớ là", "không thể phủ nhận rằng" | **error** (cụm báo hiệu rỗng) |
| plays a vital role in | "đóng vai trò quan trọng / then chốt / vô cùng quan trọng trong việc …" | error |
| at its core / when it comes to | "về cốt lõi", "xét cho cùng", "suy cho cùng", "khi nói đến", "đối với việc" | warning |
| in conclusion / in summary | "tóm lại", "nói tóm lại", "có thể thấy rằng", "tựu trung", "kết luận" | warning trong bài ngắn; error nếu là câu đóng ở caption ≤ 150 từ |
| I hope this helps | "hy vọng bài viết này hữu ích với bạn", "chúc bạn thành công", "đừng ngần ngại liên hệ" | **error** |
| unlock the potential of | "khai phá tiềm năng", "mở khoá tiềm năng", "phát huy tối đa" | error |
| studies show / experts agree (cấm vì nguồn mơ hồ) | "các nghiên cứu cho thấy", "theo các chuyên gia", "nhiều người cho rằng", "theo thống kê" mà **không nêu tên nguồn** | **error** nếu không có nguồn trong `facts.md` |
| the future looks bright / only time will tell | "tương lai đầy hứa hẹn", "tương lai rộng mở", "chỉ có thời gian mới trả lời" | warning |

Lưu ý riêng cho video: trong lời thoại TikTok khẩu ngữ, "mọi người ơi", "hôm nay mình…" là tự nhiên; vấn đề là **khuôn mở
đầu máy móc** ("Bạn có bao giờ tự hỏi…?", "Trong thế giới ngày nay…", "Hãy cùng khám phá…"). Với lời thoại hạ cấp các cụm
trên từ error xuống warning và chỉ chặn khi chúng nằm ở 2 giây đầu hoặc câu kết.

### 2.2 Khuôn câu

| Dấu hiệu EN (repo) | Cách bắt trong repo | Tương đương tiếng Việt | VN đề xuất | Tin cậy |
|---|---|---|---|---|
| **Công thức phủ định** "it's not just X, it's Y" (`NEGATION_FORMULA`, `NEGATION_CONTRAST`, `NEGATION_TRAILING`, `tells.mjs:48-59`) — error mọi lần | regex; chú thích thừa nhận có thể bắt nhầm câu tương phản thật của người ("ưu tiên độ chính xác hơn độ phủ") | "**không chỉ … mà còn …**", "không đơn thuần là … mà là …", "không phải … mà là …", "đây không chỉ là X, đây còn là Y", câu kết "…, chứ không phải …." | Vì "không chỉ … mà còn" là ngữ pháp thường, **đếm mật độ**: ≥ 1 trong hook / caption ≤ 80 từ → warning; ≥ 2 trong bài → warning mạnh; "không phải … mà là …" ở câu hook → warning | Cao (khuôn này rất đặc trưng văn AI tiếng Việt) |
| **Mảnh nhấn mạnh** "Nothing else is left behind.", "Every time, not once." (`EMPHATIC_FRAGMENT`, `tells.mjs:60-65`) — câu ≤ 6 từ lặp ý trước | regex theo từ tuyệt đối (Nothing, Always, Never, Only, Just, Every time) | "Không gì cả.", "Mỗi lần. Không ngoại lệ.", "Chỉ vậy thôi.", "Đơn giản vậy đó.", "Thế thôi.", "Luôn luôn.", "Và đó là điều làm nên khác biệt." | warning; lời thoại video cho phép **tối đa 1 câu nhấn / bài**, mọi caption: cắt hoặc gộp vào câu trước | Trung bình (câu ngắn hiệu quả trong voiceover — repo chỉ bắt khi nó *lặp lại* ý trước) |
| **Chồng rào đón** "could potentially", "may eventually" (`HEDGE_STACK`, `tells.mjs:66`) | regex | "có thể sẽ có khả năng", "có lẽ có thể", "dường như có thể", "phần nào có thể", "ít nhiều có thể" | error (chọn một mức chắc chắn) | Cao |
| **Tránh động từ "là"** "serves as / stands as / functions as / represents a" (`COPULA_AVOIDANCE`, `tells.mjs:67`) | regex | "đóng vai trò là", "đóng vai trò như", "được xem là", "được coi là", "là một minh chứng cho", "đánh dấu một bước ngoặt", "mang đến / mang lại … giá trị" | warning; đổi thành "là" | Cao |
| **Dấu gạch dài (em dash)** — error ở *mọi* lần (`tells.mjs:134-148`), repo gọi là "house style" | đếm ký tự `—` | Dấu "—" dày đặc trong caption / lời thoại; cả "–" và " - " dùng như dấu ngắt ý | warning khi ≥ 2 / bài ngắn. **Không bắt chước error** vì "—" là chuẩn viết văn bản tiếng Việt chính thống và ghi chú trong kho này dùng nó | Thấp-trung bình |
| **Bộ ba** "X, Y, and Z" lặp (`RULE_OF_THREE`, `tells.mjs:45, 150-160`) — warning khi > 1 lần | regex 3 từ đơn | "X, Y và Z"; "nhanh chóng, tiện lợi và hiệu quả"; "nhanh – gọn – đẹp"; "một cách A, B và C" | warning khi ≥ 2 bộ ba trong 1 bài ngắn; chấp nhận 1 | Cao |
| **Header Title Case** (`TITLE_CASE_HEADER`, `tells.mjs:46`) — warning | regex header Markdown | Tiêu đề "Viết Hoa Mỗi Chữ Cái", hoặc khuôn "Chủ đề: Phụ đề giật gân" cho mọi tiêu đề, gạch đầu dòng **"In đậm: mô tả"** đều tăm tắp | warning | Trung bình |

### 2.3 Chất lượng văn (`prose.mjs`) — phần lớn *không* áp dụng nguyên xi cho tiếng Việt

| Quy tắc repo | Ngưỡng repo | Áp dụng cho tiếng Việt |
|---|---|---|
| `prose/low-burstiness` — độ lệch chuẩn độ dài câu | **< 3 từ** khi có ≥ 4 câu (`prose.mjs:93-99`), warning | Giữ ý, **đơn vị đổi sang "tiếng"** (âm tiết tách bằng dấu cách) vì tiếng Việt 1 từ ≈ 1–3 tiếng. Ngưỡng 3 từ của repo không thể bê sang; thử `< 4 tiếng` rồi hiệu chỉnh trên 10 mẫu người viết thật (xem mục 4). Luật cho Agent 4: trộn ít nhất một câu ≤ 5 tiếng với một câu ≥ 15 tiếng |
| `prose/nominalization-density` — danh từ hoá (-tion, -ment...) | **> 3 % số từ** (`prose.mjs:110-118`) | Tiếng Việt danh từ hoá bằng "việc / sự / quá trình / tính / hoá": "thực hiện việc tối ưu hoá quá trình", "sự gia tăng", "tiến hành triển khai". Đếm (việc\|sự\|quá trình\|tính) trên tổng tiếng; ngưỡng đề xuất 4–5 %, **chưa hiệu chỉnh** |
| `prose/passive-voice` | retext-passive | Tiếng Việt: dấu hiệu là **câu dịch từ tiếng Anh**: "được … bởi", "được biết đến như là", "như một", "tiến hành / thực hiện việc …". Bắt theo cụm, không theo ngữ pháp bị động |
| `prose/reading-ease`, `grade-level` (Flesch ≥ 50, lớp ≤ 10) | công thức đếm âm tiết tiếng Anh | **Không áp dụng**. Thay bằng độ dài câu trung bình theo tiếng và số từ mỗi dòng chữ trên màn hình (luật có sẵn của Agent 4) |
| `prose/wall-of-text` — đoạn > 100 từ | `prose.mjs:63` | Caption: cảnh báo đoạn > 60 tiếng; xuống dòng sớm hơn trên mobile |
| `prose/repeated-word` | **error duy nhất** ở nhóm `prose` | Giữ nguyên, bắt "của của", "là là", "và và" |
| `prose/hard-to-read-sentence`, `write-good` (cụm dài dòng, sáo ngữ) | thư viện | Tự biên danh sách cụm dài dòng tiếng Việt: "một cách", "do đó có thể thấy rằng", "nhằm mục đích", "trên cơ sở đó", "bởi vì lý do là" |

### 2.4 Dấu hiệu chỉ có ở tiếng Việt (không có trong repo; người ghi chú đề xuất, tin cậy trung bình)

- Câu mở "Bạn có bao giờ tự hỏi …?", "Bạn đã bao giờ …?"; câu kết "Hãy cùng nhau …", "Đừng quên like, share và subscribe!".
- Emoji đầu mỗi dòng / gạch đầu dòng (✅🔥🚀💡), emoji rải đều mọi câu.
- Tiêu đề "Bật mí / Khám phá / Top N bí quyết / Hành trình" liên tiếp.
- Từ Hán-Việt trang trọng trong khẩu ngữ: "tối ưu", "đảm bảo", "nâng cao", "mang lại", "thiết thực".
- Văn dịch: "có một …", "nó là", "tại thời điểm này", đảo ngữ kiểu Anh.
- Lỗi kỹ thuật: Unicode **NFD** thay vì NFC (dấu bị tách, `fc-list` / libass có thể vẽ sai), dấu nháy cong lẫn thẳng, "…" lẫn "...".

## 3. Hợp đồng theo định dạng (`rules/formats/`) — mẫu cho vedit

Mỗi định dạng = tập luật *thêm vào* hai hợp đồng chung. Phân biệt rõ **error** (nền tảng từ chối / cấm) và **warning**
(bị cắt hiển thị, writer có thể chấp nhận). Mẫu để Agent 4 xây các định dạng riêng:

| Định dạng | Luật chính (nguồn) |
|---|---|
| Quảng cáo Meta (`ad.mjs`) | Hạn cứng: nội dung chính 2.200, headline 40, mô tả 30 ký tự → error. Hiển thị: **125 ký tự đầu** của nội dung chính là "cả quảng cáo" với đa số lượt xem (sau đó là "xem thêm"), headline mobile cắt ở ~27 → warning. Bắt buộc có CTA (error); headline chỉ là nhãn nút ("Learn more", "Shop now") → error; > 200 ký tự mà không có con số / nguồn / mốc thời gian → warning `missing-proof` |
| Bán hàng / email (`direct-response.mjs`) | CTA, ≥ 1 con số, danh sách "lợi ích mơ hồ" ("take it to the next level", "unlock your potential", "world-class", "state-of-the-art", "businesses of all sizes", "achieve your goals"), chứng cứ khi dài > 150 từ |
| Landing (`landing-page.mjs`) | Có headline + CTA + bằng chứng; ≤ 500 từ; đoạn ≤ 60 từ (mobile) |
| Bài X (`tweet.mjs`) | ≤ 280 ký tự **tính kiểu X** (URL luôn = 23, emoji / CJK = 2 — `shared.mjs:71-93`); **≤ 1 hashtag** (error); mồi tương tác ("RT if you", "reply YES", "tag a friend", "follow me for more" — error); dòng đầu > 120 ký tự → warning; dòng đầu IN HOA → error; "Unpopular opinion:" mà không nêu quan điểm đối lập → warning; link trong thân bài → warning (nên để ở reply) |
| Tuyên bố bị cấm (`shared.mjs:100-110`, áp cho ad + bán hàng) | "guaranteed you'll…", "100% risk-free", "zero risk", "results are typical", "make money fast", "get rich quick", "no effort required", "cures your…", "lose N lbs": error |

Tương đương tiếng Việt cho nhóm tuyên bố bị cấm (đề xuất): "cam kết 100%", "đảm bảo hiệu quả", "không rủi ro", "kiếm tiền
nhanh", "làm giàu nhanh", "không cần làm gì cả", "chữa khỏi / trị dứt điểm", "giảm X kg trong Y ngày", và tuyệt đối "số 1",
"duy nhất", "tốt nhất" không có căn cứ. Theo hiểu biết chung, pháp luật quảng cáo Việt Nam hạn chế các cách nói so sánh nhất /
tuyệt đối và tuyên bố sức khoẻ không có căn cứ — **ghi chú này chưa kiểm chứng điều khoản cụ thể**; Agent 4 gắn
`[cần xác nhận pháp lý]` và để người dùng quyết.

## 4. Cách sửa khi bị bắt (quy tắc "sửa gốc, không sửa vỏ")

Cả repo xoay quanh luật: **sửa đúng thứ cổng chỉ ra, không chỉ đổi từ vừa đủ để qua regex** (`copy-writer.md` phần Constraints;
`hedgehog-copywriting-loop/SKILL.md:338-352`). Ví dụ trong repo: xoá chữ "delve" khỏi một câu vẫn mang cấu trúc rào đón thì
là chơi cổng. Bảng sửa (diễn đạt lại):

| Bị bắt | Sửa gốc |
|---|---|
| Từ / cụm sáo | Nói hành động hoặc con số thật: thay "giải pháp toàn diện" bằng việc nó làm ra gì, trong bao lâu, cho ai |
| Công thức phủ định | Viết thẳng ý khẳng định; bỏ vế "không chỉ…" |
| Mảnh nhấn mạnh | Cắt, hoặc gộp vào câu trước; để chi tiết cụ thể làm nhấn |
| Chồng rào đón | Chọn một mức: "sẽ" hoặc "có thể", không cả hai |
| Bộ ba | Dùng hai, hoặc một, hoặc bốn; mỗi ý một chi tiết riêng |
| Câu đều tăm tắp | Chèn một câu rất ngắn cạnh một câu dài; đừng chỉ tách đôi câu |
| Danh từ hoá | Đưa động từ và chủ thể trở lại câu |
| Đoạn dài | Tách theo nhịp thở, đừng tách tuỳ tiện |
| Thiếu số liệu / bằng chứng | Thêm đúng thứ có thật trong `facts.md`; không có thì nói "chưa có số" thay vì bịa |

Quy trình: chạy cổng → đọc **báo cáo JSON** (không đọc kể lại) → sửa → chạy lại; **trần 6 vòng**, quá thì báo mâu thuẫn giữa
brief và cổng (ví dụ cần dùng đúng từ bị cấm) cho người dùng quyết, không im lặng nới ngưỡng cho riêng bản nháp. Cảnh báo
chỉ cân nhắc theo giọng của brief; đừng sửa tới 0 cảnh báo nếu câu tệ đi.

## 5. Giới hạn của cổng (trung thực về độ tin cậy)

- Chỉ bắt **bề mặt**. Không kiểm sự thật, không đo độ hấp dẫn, không phát hiện "văn AI tinh vi" không dùng từ cấm. Repo không
  công bố tỉ lệ dương tính giả / bỏ sót; bộ test chỉ có ví dụ AI cố ý và ví dụ sạch (`test/check-copy.test.mjs`, `formats.test.mjs`).
- Danh sách từ cấm của repo có từ vô hại ("align", "dynamic", "boundaries", "navigate", "ecosystem"); đồng thời
  `NEGATION_TRAILING` thừa nhận bắt nhầm câu tương phản thật của người (`tells.mjs:50-58`).
- Ngưỡng Flesch ≥ 50 / lớp ≤ 10 là "hợp đồng khán giả phổ thông" cố định, một bộ cho mọi dự án (`CLAUDE.core.md`); không phải kết quả đo.
- Có thể thấy chính mẫu dữ liệu trong `Xsolai/postforge-ai` (`src/lib/data.ts:18-20`) chứa khuôn "3 pitfalls. 3 fixes. Real
  outcomes." và "drive real impact" — nói lên rằng sản phẩm AI content hay tự sa vào đúng bẫy mà cổng bắt.
- Một mình cổng không đủ: cần đọc thành tiếng, so với giọng kênh, kiểm dữ kiện (xem `loi-va-rui-ro-cua-cac-repo-ai-content-generator`).

## Áp dụng vào vedit

**Đã có trong Agent 4** (bước 5 + Luật): danh sách ngắn "xoá cụm sáo rỗng", "tránh khuôn máy" (đúng 3 ý, câu cùng độ dài,
mở – kết đối xứng, emoji rải đều, tiêu đề "X: Y"), chi tiết cụ thể thay tính từ, đọc thành tiếng, NFC, `[cần xác nhận]`, giọng
khớp hồ sơ gu. Đây là tương đương **mục 2.2 và 4** nhưng **do chính LLM tự chấm** — đúng điều hedgehog-core bác bỏ.

**Thiếu** (theo thứ tự ưu tiên):
1. **`vedit content check <file> --format <loại>`** (Python, `vedit/contentcheck.py`), thoát 0/1/2, in JSON như `report.mjs`.
   - Chuẩn hoá NFC trước khi so khớp; tách "tiếng" bằng khoảng trắng; đếm ký tự bằng code point.
   - Luật `tells/*` đọc từ một file dữ liệu `vedit/data/vi_tells.yaml` (danh sách từ / cụm / regex + mức + lý do) để Agent 4 và
     agent phản biện mở rộng mà không sửa mã; thêm cột `lang: vi`.
   - Mức khởi điểm theo bảng mục 2: đa số **warning**, chỉ error cho cụm báo hiệu rỗng rõ ràng ("điều quan trọng cần lưu ý
     là", "hy vọng bài viết này hữu ích", "trong thế giới ngày nay" ở mở đầu), chồng rào đón, lặp từ, vượt giới hạn ký tự,
     tuyên bố cấm, số liệu / nguồn mơ hồ.
2. **Định dạng**: `voiceover` (tiếng/giây ~ nhịp trong Agent 4, câu ≤ 18 tiếng, có câu ngắn xen), `onscreen` (≤ 8 từ / dòng,
   ≤ 2 dòng, thời lượng hiển thị ≥ ký tự / 15 + 0,5 giây — các luật *đã có* trong Agent 4), `tiktok-caption`, `reels-caption`,
   `shorts-title`, `facebook-post`, `x-post`, `ad-meta`. Mỗi định dạng khai báo ngưỡng cứng (error) và ngưỡng hiển thị (warning).
3. **Hiệu chỉnh bằng mẫu thật**: dùng `vedit analyze` lấy transcript của 5–10 video tham chiếu do người viết thật làm
   (`ref-*`), đo tiếng / giây, độ lệch chuẩn độ dài câu, tần suất "không chỉ … mà còn", rồi chốt ngưỡng; ghi ngưỡng và ngày đo.
4. **Luật vòng lặp** vào Agent 4: tối đa 6 vòng; đọc JSON; cấm "chơi cổng" (đổi `--format`, xoá đúng chữ bị bắt mà giữ
   khuôn); phương án hook / tiêu đề cũng qua cổng, trượt thì gắn nhãn thay vì giấu.
5. **Test**: `tests/test_contentcheck.py` với 2 nhóm mẫu (cố ý văn AI tiếng Việt vs văn người viết sạch) như bộ test của repo —
   để chắc cổng *phân biệt được*, không đóng dấu cho tất cả.
6. Không bê nguyên: ngưỡng Flesch, danh sách từ cấm tiếng Anh, em dash = error.
