---
title: buttercut: Quy trình AI hiểu footage trước khi dựng
category: techniques
tags: [phân tích footage, transcript, contact sheet, tóm tắt clip, user context, buttercut, sub-agent]
updated: 2026-10-31
sources:
  - https://github.com/barefootford/buttercut/blob/main/skills/analyze-video/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/analyze-video/agent_prompt.md
  - https://github.com/barefootford/buttercut/blob/main/skills/process-library/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/create-library/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/transcribe-audio/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/transcribe-audio/agent_prompt.md
  - https://github.com/barefootford/buttercut/blob/main/AGENTS.md
  - https://github.com/barefootford/buttercut/blob/main/templates/library_template.yaml
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/transcribe_job.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/prepare_audio_script.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/script_extractor.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/footage_processor.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/full_transcript.rb
  - https://github.com/barefootford/buttercut/blob/main/docs/example-library-setup.md
  - https://github.com/barefootford/buttercut/blob/main/CHANGELOG.md
  - https://raw.githubusercontent.com/m-bain/whisperX/main/whisperx/alignment.py
---
# buttercut: Quy trình AI hiểu footage trước khi dựng

Nguyên tắc gốc: **dựng giỏi bắt đầu từ hiểu footage**. ButterCut biến mỗi clip thành 3 artifact rẻ cho LLM đọc
(transcript, contact sheet, tóm tắt), cộng 2 trường trí nhớ cấp dự án, và **không bao giờ cho LLM đọc file video**
("Never read the video file directly").

## Các artifact cho mỗi clip

| Artifact | Tạo bằng | Nội dung |
|---|---|---|
| `transcripts/<clip>.json` | WhisperX (code, không phải LLM) | `segments[]{start,end,text,words[{word,start,end}]}`, `word_segments[]`, `video_path`; đã xoá `score` cho gọn |
| `contact_sheets/<clip>_full.jpg` | ffmpeg | 16 khung 4x4 có mốc giờ (xem `ffmpeg/buttercut-contact-sheet-bang-ffmpeg-de-ai-xem-ca-clip`) |
| `summaries/summary_<clip>.md` | sub-agent Sonnet | tóm tắt theo khuôn cố định (bên dưới) |
| ảnh tĩnh | sub-agent | chỉ tóm tắt 3–4 câu "greppable": chủ thể, bối cảnh, bố cục, chữ trên ảnh |

Cấp dự án trong `library.yaml`: `footage_summary` (10–20 dòng tổng quan, cập nhật dần) và `user_context`
("Whenever you ask the user questions about the library, save a summarized version here", ví dụ: người mặc áo
xanh dài tay là "Andrew", chú chó nâu nhỏ là "Sammy", quay trong một buổi tối).

## Trình tự (skill `analyze-video`)

1. Hỏi có giữ máy thức không (`caffeinate -i -w $$`), tạo **todo hiển thị cho người dùng** bằng lời không kỹ thuật:
   "Keep computer awake / Create transcripts (0/30) / Analyze footage (0/30) / Let computer sleep again / Review the
   footage together".
2. **Transcript** (máy móc): `process_footage.rb transcripts <lib>` chạy nền, 2 clip song song, ghi log và đánh dấu
   từng clip xong ngay khi xong. WhisperX: `--language <iso> --model small --compute_type float32 --device cpu
   --output_format json`. Clip không có luồng âm thanh hoặc không có lời → transcript rỗng `_note: "no dialogue"`
   thay vì lỗi. Prompt sub-agent `transcribe-audio` (vẫn còn trong repo) nhấn mạnh: "Use WhisperX, NOT standard Whisper. WhisperX preserves the original video
   timeline including leading silence".
3. **Contact sheet** (máy móc): chạy SAU khi transcript xong, không bao giờ chồng lên WhisperX (tốn RAM).
4. **Hiệu đính transcript** (phán đoán, tuỳ chọn): 2–4 sub-agent; xem `audio/buttercut-hieu-dinh-transcript-ma-khong-pha-moc-thoi-gian`.
5. **Tóm tắt** (phán đoán): sub-agent chạy model **Sonnet** ("reads the contact sheet with noticeably more visual
   specificity than Haiku (catches clothing, architecture, camera framing)"), **10 clip mỗi agent, tối đa 10 agent,
   dispatch cuốn chiếu** (agent nào xong thì phát agent mới ngay, nếu chờ cả đợt sẽ mất ~30% thời gian). Mỗi clip
   3 lệnh: đọc contact sheet → chạy `script_extractor.rb` lấy lời → `Write` một lần.
6. **Cùng người dùng rà lại** ("Review the footage together"): xác nhận tên nhân vật, địa điểm, mạch truyện, clip lạc
   đề, ý đồ sáng tạo; cập nhật `footage_summary`, `user_context`, sửa tóm tắt gọi sai người. "This is the one place
   to do this thorough pass. Every later roughcut planning run inherits the resulting context".

## Khuôn tóm tắt từng clip (nguyên văn cấu trúc)

```markdown
# <video_filename>
**Duration:** <duration>

## Overview
<2-3 câu về mạch diễn biến. Cụ thể; tránh kết thúc mơ hồ kiểu "the clip ends with...">

## Key Visuals
- <3-6 gạch đầu dòng: địa điểm, cú máy đặc biệt, thay đổi hình ảnh — đọc từ contact sheet>

## Notable Dialogue
> "<0-3 câu trích; bỏ câu đệm ('um', 'you know'); không có thì ghi None>"

## B-Roll
<Cảnh cắt chèn khác chủ thể chính; clip một cảnh thì None. Không suy đoán clip này dùng làm b-roll ở đâu>
```

Giữ nguyên 4 tiêu đề vì code phía sau phụ thuộc (vd `full_transcript.rb` lấy câu đầu của `## Overview`).

## Cách đọc khi dựng: "Read smallest first; grep the rest"

- Tóm tắt trước (rẻ, đọc hết được kể cả 90+ clip) → contact sheet của clip đang cân nhắc → transcript thì **grep**
  (`rg "claude code" libraries/<name>/transcripts/`), không đọc cả file.
- Lời thoại xem nhanh bằng `script_extractor.rb` (mỗi segment một dòng, không mốc). Transcript JSON là nguồn sự thật
  duy nhất; không lưu bản script riêng để khỏi lệch.
- Không suy diễn từ tên file/hãng máy: "A `dji` clip is not 'drone footage' just because of the brand".
- Luôn gọi clip bằng tên file thật, không "Video 1", "Clip A".
- `full_transcript.rb` xuất toàn bộ lời của thư viện vào một file text (tên clip, câu tóm tắt, lời) để người dùng tự
  "paper edit".

## Bài học từ lịch sử phiên bản

- ≤ 0.6: "visual transcript" do LLM mô tả từng khung, chậm (~1x thời lượng footage). 0.7.0: thay bằng contact sheet.
- 0.5.0: model mặc định `medium` → `small` + bước hiệu đính; benchmark clip nói 5 phút (CPU, float32): medium
  90.1s (3.3x thời gian thực), small 47.7s (6.3x).
- 0.7.2: xử lý footage tốn ít hơn 2/3 token; thư viện 37 phút, 93 clip dùng khoảng 10% hạn mức 5 giờ (Max 5x).
- Chuyển các bước WhisperX/ffmpeg từ prompt vào code "so footage analysis comes out identical across models".

## Áp dụng vào vedit

**Đã có** (`vedit analyze` → `analysis/analysis.json`): ffprobe, dò cảnh (`scene > 0.15`, cảnh tối thiểu 0.8s), dò
khoảng lặng (−35 dB, ≥ 0.6s), loudness, tối đa 16 khung giữa cảnh (512px), transcript faster-whisper có mốc từng
từ **nếu đã cài** (`pip install -e ".[transcribe]"`). Thực tế: `scripts/setup.sh` chỉ cài `.[gdrive,dev]`, môi
trường hiện tại không có `faster_whisper`, dự án gần nhất `20261030-video-01` có `transcript: null`.

**Còn thiếu**: contact sheet; bản tóm tắt nội dung do agent viết sau khi xem; bước xác nhận hiểu footage với người
dùng; `user_context`; transcript mặc định; bản đồ "sự kiện âm thanh" cho video không lời (ASMR, nấu ăn).

**Đề xuất theo ưu tiên**:
1. Cài transcript mặc định: thêm `transcribe` vào `setup.sh`, chạy thử tải model (faster-whisper tải từ Hugging
   Face; nếu mạng chặn thì báo rõ tên miền cần mở). Cân nhắc WhisperX: `whisperx/alignment.py` có mô hình căn chỉnh
   tiếng Việt `"vi": 'nguyenvulebinh/wav2vec2-base-vi-vlsp2020'`. Dễ (cài) / vừa (WhisperX).
2. Sau `analyze`, Agent 2 viết `analysis/summary.md` theo khuôn: Tổng quan (2–3 câu mạch diễn biến) / Hình ảnh chính
   (có mốc giây) / Lời thoại đáng chú ý / Âm thanh nổi bật (mốc tiếng va chạm, tiếng động ASMR) / Ứng viên hook
   (2–3 mốc đẹp nhất) / Cảnh nên bỏ (vd cảnh bồn rửa 10.6–12.9s ở dự án gần nhất). Dễ.
3. Bước "xác nhận hiểu footage" ở main thread: 2–3 câu hỏi (ai/cái gì trong video, mục đích, muốn nhấn vào đâu),
   lưu `user_context` vào `project.json` và truyền cho Agent 2/3. Dễ.
4. Video không lời: sinh danh sách sự kiện âm thanh (đỉnh âm lượng/onset) như một "transcript âm thanh" để cắt
   theo tiếng động. Vừa.
5. Dự án nhiều clip (thư viện): mỗi clip có summary + contact sheet, agent đọc summary trước rồi mới mở sheet. Khó.
