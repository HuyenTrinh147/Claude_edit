---
title: claude-video-editor: Đọc video bằng transcript và quy tắc cắt
category: techniques
tags: [claude-video-editor, video-use, transcript, điểm cắt, word boundary, khoảng lặng, timeline view, edl, chọn take]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/README.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/helpers/transcribe.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/helpers/transcribe_batch.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/helpers/pack_transcripts.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/helpers/timeline_view.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/transcript-guide.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/short-form-video/SKILL.md
  - https://github.com/chidiwilliams/buzz/discussions/1390
---
# claude-video-editor: Đọc video bằng transcript và quy tắc cắt

## 1. Hai lớp "nhìn" video

| Lớp | Công cụ | Khi nào | Chi phí |
|---|---|---|---|
| 1. Transcript (luôn nạp) | `transcribe.py` → `pack_transcripts.py` → `takes_packed.md` | Mọi quyết định | ~12KB text cho nhiều take |
| 2. Hình + sóng âm (theo yêu cầu) | `timeline_view.py <video> <start> <end>` | Điểm cắt mơ hồ, so sánh take, kiểm điểm cắt | Vài PNG |

**Transcript**: ElevenLabs Scribe `scribe_v1` với `diarize=true`, `tag_audio_events=true`,
`timestamps_granularity=word`; audio trích mono 16 kHz PCM; cache theo file (`transcripts/<tên>.json`, không bao giờ
transcribe lại nguồn không đổi); batch 4 luồng song song.

**Packed transcript** — mỗi take một khối, mỗi dòng một cụm từ, ngắt khi im lặng ≥ 0.5s **hoặc** đổi người nói;
audio event viết trong ngoặc:

```
## C0103  (duration: 43.0s, 8 phrases)
  [002.52-005.36] S0 Ninety percent of what a web agent does is completely wasted.
  [006.08-006.74] S0 We fixed this.
```

"it gives word-boundary precision from text alone at 1/10 the tokens of raw JSON."

**timeline_view** — PNG rộng ≥1920: dải N khung (mặc định 10, mỗi khung cao 180px) + waveform RMS (đọc WAV mono
16 kHz) + nhãn từ phía trên waveform + dải tô màu cho im lặng ≥ 400ms + thước thời gian 6 vạch. "Use this at decision
points … Do NOT call it in a scan loop over every utterance."

## 2. Quy tắc cắt (số liệu cụ thể)

- **Audio-first**: ứng viên điểm cắt lấy từ ranh giới từ và khoảng lặng; chỉ soi hình ở điểm quyết định.
- **Không bao giờ cắt giữa một từ** — snap mọi mép cắt vào ranh giới từ trong transcript.
- **Đệm mép cắt 30–200ms** vì timestamp Scribe lệch 50–100ms. Ví dụ đã xuất bản: **50ms trước từ đầu, 80ms sau từ
  cuối**. Montage nhanh → đệm ít; tài liệu → đệm nhiều.
- **Khoảng lặng là ứng viên cắt**: ≥ 400ms sạch nhất; 150–400ms dùng được nếu soi hình; < 150ms không an toàn
  (giữa cụm từ).
- **Chuyển người nói**: chừa 400–600ms "không khí" giữa hai lượt (nhanh thì ít, điện ảnh thì nhiều).
- **Giữ đỉnh cảm xúc**: tiếng cười, punchline, chỗ nhấn — kéo dài **qua** phản ứng ("the laugh IS the beat");
  audio event `(laughs)`, `(sighs)`, `(applause)` đánh dấu beat.
- **Không suy luận âm thanh và hình tách rời** — mọi điểm cắt phải ổn trên cả hai track.
- Chỉ dùng **ASR cấp từ, nguyên văn** (giữ "ừm, à"): SRT/cụm câu mất dữ liệu khoảng hở dưới 1 giây; chuẩn hoá từ đệm
  làm mất tín hiệu biên tập.

## 3. Brief cho sub-agent chọn take (nhiều take/clip)

Cấu trúc "load-bearing" (giữ khung, thay nội dung):

```
You are editing a <type> video. Pick the best take of each beat and
assemble them chronologically by beat, not by source clip order.
INPUTS: takes_packed.md · product/narrative context (2 câu) · speaker(s) + delivery note
        · expected structure (archetype) · verbal slips to avoid · target runtime
RULES:  start/end on word boundaries · pad 30–200ms · prefer silences ≥ 400ms
        · unavoidable slips kept only if no better take, note in "reason"
        · over budget → drop a beat or trim tails; report total and self-correct
OUTPUT (JSON array, no prose):
  [{"source": "C0103", "start": 2.42, "end": 6.85, "beat": "HOOK", "quote": "...", "reason": "..."}]
```

Archetype gợi ý: Tech launch `HOOK → PROBLEM → SOLUTION → BENEFIT → EXAMPLE → CTA` · Tutorial
`INTRO → SETUP → STEPS → GOTCHAS → RECAP` · Interview `(QUESTION → ANSWER → FOLLOWUP)×n` · Travel/event
`ARRIVAL → HIGHLIGHTS → QUIET MOMENTS → DEPARTURE` · Documentary `THESIS → EVIDENCE → COUNTERPOINT → CONCLUSION` ·
Music `INTRO → VERSE → CHORUS → BRIDGE → OUTRO` — hoặc tự đặt.

Mỗi range trong EDL mang `beat`, `quote`, `reason` — vừa là lý do biên tập, vừa là dữ liệu để kiểm tra lại.

## 4. Anti-pattern (từ repo)

- Định dạng "codec" tính trước nhiều tầng (USABILITY, tag tông, lớp shot) — "Over-engineering. Derive from the
  transcript at decision time."
- Hàm chấm điểm khoảnh khắc viết tay — "The LLM picks better than any heuristic you'll write."
- Whisper SRT/cụm câu; chạy Whisper CPU cục bộ (chậm, chuẩn hoá từ đệm).

## 5. Đồng bộ theo thời gian sau khi cắt (short-form-video)

Khi audio đã được cắt, **mọi** mốc phải ở "edited-time" — "Never mix." Nếu dùng hàm `shift(originalTime) = editedTime`
để đổi transcript gốc sang timeline mới, hàm đó áp cho **mọi** mốc cảnh/caption. Đo độ dài cũ/mới bằng `ffprobe` →
hiệu số = tổng thời gian đã cắt. Kế hoạch retime trình bày dạng bảng: Cảnh | start cũ | dur cũ | start mới | dur mới
| lý do.

## 6. Ghi chú cho tiếng Việt / vedit (nhận định)

- vedit chạy faster-whisper offline (miễn phí) thay vì Scribe. Mẹo "prompt có từ đệm để Whisper giữ 'umm'" **không
  ổn định**: nhà phát triển Buzz báo "experiments with initial prompts has not resulted in any meaningful differences";
  có người gợi ý CrisperWhisper (model chuyên giữ từ đệm) nhưng chưa ai xác nhận trong thread → cần tự thử với tiếng Việt.
- Video **không lời** (ASMR nấu ăn, review đồ vật): "audio-first" chuyển thành "**sự kiện âm thanh**-first" — tiếng
  va chạm, xèo xèo, cắt rau là điểm cắt/punch tốt; dùng waveform để tìm đỉnh năng lượng.

## Áp dụng vào vedit

**Đã có**: `vedit analyze` → `analysis.json` (cảnh bằng scene score 0.15, khoảng lặng −35 dB ≥ 0.6s, khung giữa mỗi
cảnh, transcript faster-whisper có `words`); `vedit frame <slug> <giây> --grid`.

**Còn thiếu**: bản transcript gọn để đọc (transcript đầy đủ kèm `words` rất tốn token); không có ảnh filmstrip +
waveform tại điểm quyết định; EditPlan không kiểm tra cắt giữa từ; clip chỉ có `note`, không có `quote/reason` để
đối chiếu.

**Đề xuất (ưu tiên)**:
1. `vedit analyze` sinh thêm **`analysis/transcript_packed.md`** (dòng `[start-end] text`, ngắt ở im lặng ≥ 0.5s) —
   Agent 2 đọc file này thay cho JSON. Dễ.
2. **`vedit timeline <slug> <start> <end> [--source preview]`**: ghép N khung (`select` + `tile`) + sóng âm
   (`showwavespic`) + nhãn từ + dải im lặng bằng Pillow — không cần numpy. Dùng khi chọn điểm cắt và khi QA. Vừa.
3. **`vedit validate` cảnh báo**: mép clip rơi vào giữa một từ, hoặc cách mép từ < 30ms; gợi ý giá trị snap
   (đầu từ − 0.05s / cuối từ + 0.08s). Vừa.
4. Thêm trường tuỳ chọn **`quote`, `reason`** cho Clip; validate so `quote` với chữ trong transcript ở [start,end]
   (fuzzy) để bắt lỗi lệch điểm cắt. Dễ–vừa.
5. Đưa các con số mục 2 vào prompt Agent 2 (phần "Quy tắc cứng"), kèm archetype cấu trúc. Dễ.
