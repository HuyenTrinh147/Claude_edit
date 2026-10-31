---
title: buttercut: Cắt theo mốc từng từ, giữ thoại liền mạch
category: techniques
tags: [word-level, điểm cắt, transcript, whisperx, thoại, jump cut, buttercut]
updated: 2026-10-31
sources:
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/roughcut_agent_prompt.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/cut_yaml_schema.md
  - https://github.com/barefootford/buttercut/blob/main/templates/roughcut_template.yaml
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/prepare_audio_script.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/script_extractor.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/export_core.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/editor_base_core.rb
  - https://github.com/barefootford/buttercut/blob/main/CHANGELOG.md
---
# buttercut: Cắt theo mốc từng từ, giữ thoại liền mạch

ButterCut 0.6.0: "Before, edits could basically only land on sentence boundaries, so a clip carried whatever filler or
restarts came with it. Now it uses the transcript's per-word timing and trims inside a sentence down to hundredths of
a second." Điểm cắt lấy từ **mốc từng từ** của WhisperX, không từ mắt nhìn.

## Dữ liệu dùng

Transcript JSON sau `prepare_audio_script.rb` (đã xoá `score`, thêm `video_path`):

```text
{ "segments": [ { "start": <s>, "end": <s>, "text": "<câu>",
                  "words": [ { "word": "<từ>", "start": <s>, "end": <s> }, ... ] }, ... ],
  "word_segments": [ { "word": ..., "start": ..., "end": ... }, ... ],
  "video_path": "/abs/path/clip.mov" }
```

Hai mục `words` thật trong ví dụ của prompt (grep chữ "issues"):

```json
{ "word": "issues",  "start": 16.152, "end": 16.272 },
{ "word": "issues.", "start": 17.054, "end": 17.195 }
```

## Cách làm (từ `roughcut_agent_prompt.md`)

1. Đọc lời nhanh: `ruby lib/buttercut/script_extractor.rb <transcript.json>` (mỗi segment một dòng, không mốc).
2. Chọn câu cần giữ, xác định từ đầu và từ cuối.
3. **Grep đúng từ**, không đọc cả file: `grep -B 1 -A 2 '"word": "issues' transcripts/DJI_123.json`.
4. Có nhiều lần xuất hiện thì chọn theo ngữ cảnh; `in_point` = `start` của từ đầu, `out_point` = `end` của từ cuối.
5. Ghi `HH:MM:SS.ss` (luôn có giờ; làm tròn tới phần trăm giây, "don't carry more precision than the audio
   transcript actually provides").

**Ví dụ gốc**: câu "We're also using AI on the back end to try to find issues as well as try to find more test
issues." lặp ý. Kết thúc sau chữ "issues" đầu tiên (end 16.272s, chữ cuối "issues." end 17.195s) →
`in_point: 00:00:15.13`, `out_point: 00:00:16.27`, "Drops nearly a second of redundant phrasing."

## Luật biên tập đi kèm

- "When a clip has dialogue, coherent dialogue wins over visual timing. Set cuts to complete the sentence even if a
  tighter visual cut exists. A mid-sentence cut breaks audience attention; a slightly held visual doesn't."
- Cắt chữ trong câu là việc chính của vòng rà soát, không phải ngoại lệ: "Word-level trimming is a first-class part
  of this pass, not an edge case": bỏ từ đệm, câu mở yếu, câu nói lại (restart).
- Ý lặp ở hai beat: giữ bản nói hay hơn, bỏ bản yếu.
- Clip không lời (b-roll): coi là chỉ có hình, không căn theo chữ.
- Lời sai chính tả do Whisper: sửa trong trường `dialogue` của cut ("Cloud Code" → "Claude Code"), **không bao giờ
  sửa file transcript JSON** ở bước dựng vì đó là nguồn mốc thời gian.
- Độ chính xác: "One second of precision is the goal, not perfect-frame... Don't recursively zoom hunting for an
  exact frame" (vì đây là bản cắt thô, editor sẽ tinh chỉnh trong NLE).

## Khi xuất

`export_core.rb` đổi `HH:MM:SS.ss` sang giây; từ chối clip có `out ≤ in` (out = in thành clip 0s; out < in mất dấu và
thành clip dương "quietly plays footage nobody asked for"). Bộ sinh XML làm tròn điểm vào theo lưới khung hình của
nguồn (`round_to_frame_boundary`), rồi với FCPXML làm tròn tiếp theo lưới khung của sequence nhưng không sớm hơn
khung đầu của media.

## Áp dụng vào vedit

**Đã có**: `media.transcribe()` (faster-whisper, `word_timestamps=True`, `vad_filter=True`) lưu `words` vào
`analysis.json`; `CaptionSegment.words` cho phụ đề karaoke; renderer đặt clip theo khung nguyên.

**Còn thiếu**: transcript thường không có vì chưa cài faster-whisper; Agent 2 chỉ thấy segment (`analysis_brief` in
`[start–end] text`, không có mốc từ); không có công cụ tra mốc từ; `vedit validate` không cảnh báo khi clip bắt đầu
hay kết thúc giữa một từ/câu. Với video ngắn, vedit là bản **thành phẩm**, nên cần chính xác hơn mức ~1s của
ButterCut.

**Đề xuất theo ưu tiên**:
1. Lệnh `vedit words <slug> "<cụm từ>"`: in mọi lần xuất hiện kèm `start/end` từng từ và câu chứa nó (tiếng Việt:
   Whisper tách "word" theo dấu cách nên mỗi "word" thường là một âm tiết, cụm "cà pháo" là 2 mục). Dễ.
2. `vedit validate` cảnh báo: mốc `start`/`end` của clip rơi vào giữa `[word.start, word.end]`; clip kết thúc khi câu
   chưa xong (không có dấu câu/khoảng nghỉ); khoảng nghỉ giữa hai từ quá ngắn để cắt sạch. Vừa.
3. Quy tắc đệm điểm cắt cho thành phẩm (giá trị khởi điểm, cần nghe thử để chốt): vào sớm hơn từ đầu 0.05–0.15s, ra
   muộn hơn từ cuối 0.1–0.2s, và nếu có khoảng lặng giữa hai từ thì cắt vào giữa khoảng lặng. Ghi vào kho sau khi thử.
4. Đưa vào prompt Agent 2/3 luật "thoại liền mạch thắng nhịp hình" và vòng tỉa chữ (bỏ "à, ừm, thì là", câu nói lại),
   sửa lỗi nhận dạng trong phụ đề chứ không sửa transcript gốc. Dễ.
5. Phụ đề sinh từ các từ nằm trong khoảng giữ lại sau khi cắt (quy đổi giây nguồn → timeline) để phụ đề không chứa
   chữ đã bị cắt. Vừa.
