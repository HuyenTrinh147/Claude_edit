---
title: video-use: Mẫu brief giao việc cho sub-agent
category: scripting
tags: [video-use, prompt, sub-agent, brief, chọn take, animation, critic, song song, cấu trúc]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/install.md
  - https://github.com/browser-use/video-use/blob/main/README.md
---
# video-use: Mẫu brief giao việc cho sub-agent

video-use giao việc cho sub-agent ngắn hạn (qua `Agent` tool) bằng các brief có cấu trúc cố định. Ghi chú này
gom các brief đó kèm bản phỏng theo cho vedit.

## 1. Editor sub-agent — chọn take tốt nhất cho từng beat (nguyên văn)
"The structure is load-bearing; the pitch-shape example is not."
```
You are editing a <type> video. Pick the best take of each beat and
assemble them chronologically by beat, not by source clip order.

INPUTS:
  - takes_packed.md (time-annotated phrase-level transcripts of all takes)
  - Product/narrative context: <2 sentences from the user>
  - Speaker(s): <name, role, delivery style note>
  - Expected structure: <pick an archetype or invent one>
  - Verbal slips to avoid: <list from the pre-scan pass>
  - Target runtime: <seconds>

RULES:
  - Start/end times must fall on word boundaries from the transcript.
  - Pad cut boundaries (working window 30–200ms).
  - Prefer silences ≥ 400ms as cut targets.
  - Unavoidable slips are kept if no better take exists. Note them in "reason".
  - If over budget, revise: drop a beat or trim tails. Report total and self-correct.

OUTPUT (JSON array, no prose):
  [{"source": "C0103", "start": 2.42, "end": 6.85, "beat": "HOOK",
    "quote": "...", "reason": "..."}, ...]

Return the final EDL and a one-line total runtime check.
```
Các khung cấu trúc ("pick, adapt, or invent"):
| Thể loại | Chuỗi beat |
|---|---|
| Ra mắt sản phẩm / demo | HOOK → PROBLEM → SOLUTION → BENEFIT → EXAMPLE → CTA |
| Hướng dẫn | INTRO → SETUP → STEPS → GOTCHAS → RECAP |
| Phỏng vấn | (QUESTION → ANSWER → FOLLOWUP), lặp lại |
| Du lịch / sự kiện | ARRIVAL → HIGHLIGHTS → QUIET MOMENTS → DEPARTURE |
| Tài liệu | THESIS → EVIDENCE → COUNTERPOINT → CONCLUSION |
| Âm nhạc / biểu diễn | INTRO → VERSE → CHORUS → BRIDGE → OUTRO |

## 2. Animation sub-agent — mỗi animation một con, chạy song song
Hard Rule 10: "Parallel sub-agents for multiple animations. Never sequential. Spawn N at once... total wall time
≈ slowest one." Mỗi prompt phải tự đủ thông tin, vì sub-agent không có ngữ cảnh của agent cha. Brief gồm 10 mục:
1. Mục tiêu một câu: "Build ONE animation: [spec]. Nothing else."
2. Đường dẫn xuất tuyệt đối: `<edit>/animations/slot_<id>/render.mp4`.
3. Thông số kỹ thuật chính xác: độ phân giải, fps, codec, pix_fmt, CRF, thời lượng.
4. Bảng màu bằng giá trị cụ thể (RGB, hex, hoặc trỏ tới design system).
5. Đường dẫn font, kèm index nếu là file `.ttc`.
6. Timeline từng khung hình: cái gì xảy ra lúc nào, easing gì.
7. Danh sách cấm: "no chrome, no extras, no titles unless specified".
8. Mẫu code tham chiếu: chép helper inline, không import chéo giữa các slot.
9. Checklist bàn giao: script, render, kiểm thời lượng bằng ffprobe, báo cáo.
10. "**Do not ask questions. If anything is ambiguous, pick the most obvious interpretation and proceed.**"

"One sub-agent = one file (unique filenames, parallel agents don't overwrite each other)."

## 3. Critic sub-agent — phê bình trước khi giao
Dùng cho mọi video người dùng sẽ đăng (launch, promo, quảng cáo).
- Đầu vào: file đã render, EDL, video tham chiếu người dùng đưa.
- Brief: "**roast, not to praise**: a verdict, ranked problems with timecodes and evidence (frames, levels), and
  the 5 fixes to do first."
- Lý do: "Fresh eyes catch what the author stopped seeing — cut-off payoff lines, 0.5s memes, unreadable 28px
  text at phone size."

## 4. Hợp đồng prompt cài đặt (install.md)
- "Do everything yourself. Only ask the user for things you cannot generate."
- "After install, verify by running one real command against one real file. Don't declare success on
  file-existence checks alone."
- README có sẵn một "setup prompt" để dán vào agent bất kỳ. Prompt này dặn "don't transcribe anything on your
  own — just tell me it's ready and wait".

## Bản phỏng theo cho vedit (tiếng Việt)
**A. Brief chọn cảnh cho Agent 2** (đặt trước khi viết `edit_plan.json`):
```
Bạn dựng video <thể loại> cho <nền tảng>, dài mục tiêu <N> giây, theo hướng đã được duyệt: <A/B + 1 câu>.
ĐẦU VÀO: analysis/packed.md (cảnh, cụm lời, tiếng động có mốc giây), danh sách khoảnh khắc bắt buộc giữ/cắt,
  chỗ nói vấp cần tránh, khung beat: <chọn hoặc tự đặt>.
QUY TẮC: mép cắt ở ranh giới từ / khoảng lặng (ưu tiên ≥ 0.4 s), padding 50 ms trước / 80 ms sau;
  không cắt ngang đuôi tiếng động; xếp theo beat, không theo thứ tự quay; vượt thời lượng thì bỏ beat hoặc
  cắt đuôi, rồi tự cộng lại.
ĐẦU RA: clips trong edit_plan.json, mỗi clip có note = "BEAT — 'trích lời/âm thanh' — lý do",
  kèm một dòng kiểm tra tổng thời lượng.
```
**B. Subagent `video-critic`** (chỉ đọc, chạy sau preview, trước khi gửi người dùng):
```
Bạn là người phê bình khó tính. Hãy "roast", không khen.
ĐẦU VÀO: renders/preview.mp4 (hoặc final.mp4), edit_plan.json, script/script.md, yêu cầu gốc của người dùng,
  ảnh QA ở renders/qa/ (filmstrip + waveform tại mọi điểm cắt), số đo loudness.
ĐẦU RA:
  1. Phán quyết 1 câu: có đăng được không.
  2. Tối đa 10 vấn đề xếp theo mức nghiêm trọng, mỗi vấn đề có mốc giây và bằng chứng (ảnh nào, số đo nào).
  3. 5 sửa đổi làm ngay, viết thành thay đổi cụ thể trên EditPlan.
  Soi kỹ: hook 1.5 s đầu, chữ đọc kịp không (cỡ trên điện thoại), payoff có bị cắt cụt không,
  hiệu ứng nào là "khuôn mẫu", có ý tưởng dựng hay chỉ là chồng sticker, âm thanh ở điểm cắt.
```

## Áp dụng vào vedit
**Đã có:**
- Subagent `video-scriptwriter` và `video-editor`.
- Trường `Clip.note` đã được dùng giống `beat/reason`.
- Prompt Agent 3 có giới hạn "1-3 vòng".

**Còn thiếu:**
- Không có critic.
- Brief của Agent 2 không có khối QUY TẮC/ĐẦU RA chặt chẽ và không có bước tự kiểm thời lượng.
- Chưa tận dụng sub-agent song song cho các việc độc lập.

**Đề xuất (ưu tiên giảm dần):**
1. **Tạo `.claude/agents/video-critic.md`** theo brief B, rồi gọi nó trong `/lam-video` và `/sua-video` trước khi
   gửi file — độ khó thấp, giá trị cao.
2. **Chèn brief A vào `.claude/agents/video-scriptwriter.md` và `vedit/agents/scriptwriter.py`** — độ khó thấp.
3. **Song song hoá khi có nhiều phần độc lập** — độ khó trung bình. Ví dụ nhiều biến thể hook, hoặc nhiều
   animation dựng sẵn khi vedit hỗ trợ overlay clip. Áp dụng luật "một sub-agent = một file".
4. **Câu "Do not ask questions... pick the most obvious interpretation"** — độ khó thấp. Dùng cho mọi sub-agent
   con. Riêng điều phối viên vẫn phải hỏi người dùng ở bước duyệt chiến lược.
