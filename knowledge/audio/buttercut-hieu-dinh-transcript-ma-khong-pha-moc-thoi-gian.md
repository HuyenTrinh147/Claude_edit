---
title: buttercut: Hiệu đính transcript mà không phá mốc thời gian
category: audio
tags: [transcript, whisper, phụ đề, hiệu đính, tên riêng, mốc từng từ, buttercut, tiếng việt]
updated: 2026-10-31
sources:
  - https://github.com/barefootford/buttercut/blob/main/skills/transcribe-audio/refine_instructions.md
  - https://github.com/barefootford/buttercut/blob/main/skills/transcribe-audio/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/analyze-video/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/create-library/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/cut_yaml_schema.md
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/transcribe_job.rb
  - https://github.com/barefootford/buttercut/blob/main/CHANGELOG.md
---
# buttercut: Hiệu đính transcript mà không phá mốc thời gian

Whisper nghe sai tên riêng, thương hiệu, thuật ngữ, giọng địa phương. ButterCut (0.5.0) thêm bước **refinement**: sau
khi WhisperX chạy xong (bước máy móc), sub-agent dùng ngữ cảnh của thư viện để sửa chữ **ngay trong transcript JSON**
mà không làm lệch mốc từng từ (thứ dùng để chọn điểm cắt). Bật mặc định cho thư viện mới; câu hỏi lúc tạo thư viện:
"Can I proofread the transcripts after they're generated? I'll use the video's context to fix mistakes."
Kết hợp model `small` + hiệu đính được tác giả đánh giá vừa nhanh vừa chính xác hơn mặc định `medium` cũ.

## Đầu vào

`transcript_path`, `user_context`, `footage_summary` do parent truyền thẳng (rỗng vẫn chạy). Không mở `library.yaml`,
không lục file khác. Xem lời bằng `script_extractor.rb` trước, chưa đọc JSON đầy đủ.

## LUẬT CỨNG: giữ số từ, không đổi mốc

`segments[].words[]` khớp 1–1 với các token cách nhau bởi dấu cách trong `segments[].text`.
- **Được**: sửa chính tả 1→1 (`Tenderlohn` → `Tenderloin`); sửa cụm N→N (`Walnut Creak` → `Walnut Creek`).
- **Cấm**: tách 1→2 (`Sanjose` → `San Jose`, vì phải đoán chỗ chia thời gian); gộp 2→1.
- **Kỹ thuật "squash"**: tên nhiều chữ bị dính thành một token thì sửa thành một token viết hoa giữa
  (`Sanjose` → `SanJose`, `Saintvincent` → `SaintVincent`).
- Không bao giờ sửa `start`, `end`, `duration`, `word.start`, `word.end`.
- Không squash được thì **không sửa**, ghi vào báo cáo ("Skipped: 'everysingle' ... a 1→2 split would corrupt timing").

## Khi nào được sửa (thang tin cậy)

1. **Có trong ngữ cảnh**: thuật ngữ xuất hiện trong `user_context`/`footage_summary` và transcript có dạng nghe nhầm
   gần giống (`Sanoma` → `Sonoma` khi tóm tắt ghi đám cưới ở Sonoma).
2. **Token vô nghĩa**: chuỗi không phải từ thật, chỉ có một cách viết đúng hợp ngữ cảnh (`Pleasantton` → `Pleasanton`).
3. **Tự chứng (self-witness)**: dạng đúng xuất hiện ở chỗ khác trong CHÍNH transcript đó và token nghi ngờ đọc gần
   giống (`Pasific Hites` → `Pacific Heights` khi hai đoạn khác đã ghi đúng).
4. **Cấm sửa chỉ dựa trên hiểu biết chung**: "Andrew dropped by a little market on Fillmore" không được đoán ra tên
   một cửa hàng nổi tiếng; cụm chung chung có thể đúng là điều đã nói.

## Áp dụng sửa vào JSON (3 chỗ phải khớp nhau)

1. `segments[].text`: luôn kèm ít nhất một từ bên cạnh làm "neo"; không bao giờ `replace_all` trên một từ trần (sửa
   "car" → "far" sẽ biến "carrot" thành "farrot").
2. `segments[].words[].word` và 3. `word_segments[].word`: neo bằng dòng `"start": ...` ngay sau để duy nhất; copy
   đúng thụt lề của file đã pretty-print.
- Giữ nguyên chữ hoa/thường như transcript (trừ chữ hoa giữa do squash).
- Trả về danh sách `cũ → mới`, hoặc "Refinement: no corrections needed", hoặc danh sách bị bỏ qua vì đổi số từ.

## Ở bước dựng

Cut YAML có trường `dialogue`: sửa lời hiển thị tại đây khi rõ ngữ cảnh ("RubyVeedums" → "Ruby Meetups", "Cloud Code"
→ "Claude Code", "Hot Wide Native" → "HotWire Native"); "Never edit the transcript JSON files themselves — they're the
timing source of truth."

## Áp dụng vào vedit

**Đã có**: transcript faster-whisper có mốc từng từ (khi đã cài), phụ đề `captions` (kể cả karaoke theo từng từ) dựng
thẳng từ transcript; `--transcript file.srt` khi người dùng có phụ đề sẵn.

**Còn thiếu**: không có bước hiệu đính, nên lỗi nhận dạng đi thẳng lên phụ đề hiển thị (lỗi dễ thấy nhất với người xem
Việt: sai dấu, sai tên món/địa danh/thương hiệu, từ lóng, xen tiếng Anh); không có ngữ cảnh người dùng để đối chiếu.

**Đề xuất theo ưu tiên**:
1. Bước hiệu đính tiếng Việt cho Agent 2 trước khi viết captions, theo đúng luật trên. Với tiếng Việt, Whisper tách
   "word" theo dấu cách nên mỗi "word" thường là một âm tiết: sửa dấu/chính tả 1→1 từng âm tiết là an toàn; cụm tên
   nhiều âm tiết vốn đã nhiều token nên ít khi cần squash. Lưu thay đổi vào `analysis/transcript_fixes.json`
   (`segment`, `cũ`, `mới`, `lý do`: ngữ cảnh / vô nghĩa / tự chứng) thay vì ghi đè transcript gốc. Vừa.
2. Nguồn ngữ cảnh: `user_context` hỏi ở bước xác nhận footage (tên người, món, thương hiệu, địa điểm), tiêu đề/caption
   người dùng đưa, chữ đọc được trong khung hình (bao bì, biển hiệu). Dễ.
3. Kiểm tra tự động trong `vedit validate`: số từ và mọi mốc thời gian của transcript sau hiệu đính phải giống bản gốc.
   Dễ.
4. Thử cho faster-whisper biết trước từ vựng của video (tham số gợi ý từ vựng/prompt ban đầu): **chưa kiểm chứng**
   trong phiên này, cần đọc tài liệu faster-whisper và đo trước khi dùng. Vừa.
