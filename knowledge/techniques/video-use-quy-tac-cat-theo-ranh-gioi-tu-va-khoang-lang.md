---
title: video-use: Quy tắc cắt theo ranh giới từ và khoảng lặng
category: techniques
tags: [video-use, cắt, điểm cắt, khoảng lặng, padding, take, word boundary, jump cut, nhịp]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/poster.html
  - https://github.com/browser-use/video-use/blob/main/helpers/timeline_view.py
---
# video-use: Quy tắc cắt theo ranh giới từ và khoảng lặng

Nguyên tắc gốc: "**Audio is primary, visuals follow.** Cut candidates come from speech boundaries and silence
gaps." Thêm vào đó: "Never reason audio and video independently. Every cut must work on both tracks."

## Quy tắc cứng (Hard Rules 6–8)
- **Không bao giờ cắt giữa một từ.** Mọi mép cắt phải snap vào ranh giới từ trong transcript.
- **Mép cắt nào cũng có padding**, khoảng làm việc **30–200 ms**. Lý do: "Scribe timestamps drift 50–100ms —
  padding absorbs the drift." Video nhịp nhanh thì padding chặt, video điện ảnh thì lỏng.
- **Chỉ dùng ASR cấp từ, verbatim.** Không dùng SRT hay chế độ câu (mất thông tin khoảng hở dưới 1 giây).
  Không để ASR chuẩn hoá từ đệm, vì "umm" là tín hiệu biên tập.

## Bảng khoảng lặng làm điểm cắt
| Khoảng lặng | Dùng thế nào |
|---|---|
| ≥ 400 ms | Sạch nhất, ưu tiên ("Prefer silences ≥ 400ms as cut targets") |
| 150–400 ms | Ranh giới cụm, dùng được nhưng phải kiểm tra hình |
| < 150 ms | Không an toàn, đang giữa câu |

## Thông số mẫu (lấy từ video launch thật, không bắt buộc)
- **Padding:** 50 ms trước từ đầu tiên được giữ, 80 ms sau từ cuối. Montage cần năng lượng thì chặt hơn, phim
  tài liệu thì lỏng hơn, miễn vẫn trong 30–200 ms.
- **Chuyển người nói (speaker handoff):** chừa 400–600 ms "khoảng thở". Nhịp nhanh thì ít hơn, điện ảnh thì
  nhiều hơn.
- **Giữ đỉnh cảm xúc:** "Extend past punchlines to include reactions — the laugh IS the beat." Các audio event
  `(laughs)`, `(sighs)`, `(applause)` đánh dấu beat, nên kéo đoạn qua khỏi chúng.

## Chọn take khi có nhiều lần quay
- Chọn take tốt nhất cho **từng beat**, rồi ghép "chronologically by beat, not by source clip order".
- Chỗ nói vấp mà không còn take nào sạch hơn thì vẫn giữ, nhưng ghi rõ trong `reason`.
- Vượt ngân sách thời lượng thì "drop a beat or trim tails", báo tổng thời lượng và tự sửa.
- Mỗi đoạn ghi `beat`, `quote`, `reason`, ví dụ `"Cleanest delivery, stops before slip at 38.46."`.
- Anti-pattern: "Hand-tuned moment-scoring functions. The LLM picks better than any heuristic you'll write."
  Cũng không lập sẵn các nhãn "USABILITY / tone tags / shot layers": cứ suy ra từ transcript lúc quyết định.

## Cách tính mép cắt (gợi ý triển khai, video-use không có code này)
```python
PAD_IN, PAD_OUT = 0.05, 0.08          # 50 ms / 80 ms, trong khoảng 30-200 ms

def snap_range(words, first_idx, last_idx):
    """words: [{'text','start','end'}] sorted. Keep words[first_idx..last_idx]."""
    w0, w1 = words[first_idx], words[last_idx]
    prev_end = words[first_idx - 1]["end"] if first_idx > 0 else 0.0
    next_start = words[last_idx + 1]["start"] if last_idx + 1 < len(words) else w1["end"] + 1.0
    # never eat into a neighbouring word: stay inside the gap (at most half of it)
    start = max(w0["start"] - PAD_IN, (prev_end + w0["start"]) / 2)
    end = min(w1["end"] + PAD_OUT, (w1["end"] + next_start) / 2)
    return round(start, 3), round(end, 3)
```

## Áp dụng vào vedit
**Đã có:**
- `silencedetect` (-35 dB, ≥ 0.6 s) và scene detect trong `analysis.json`.
- Mốc từng từ khi có faster-whisper.
- Prompt Agent 2: "Cắt bỏ khoảng lặng/đoạn thừa; clip thường 0.8-4 giây".
- Trường `Clip.note` đang được dùng giống `beat/reason` (plan gần nhất ghi rất chi tiết).

**Còn thiếu:**
- Không snap tự động.
- Không có quy định padding.
- `validate` không cảnh báo khi cắt giữa từ.
- Ngưỡng lặng 0.6 s bỏ sót các khoảng 150–600 ms vẫn dùng được.
- Với footage không lời (ASMR, nấu ăn), "ranh giới" tương ứng là **tiếng động**, nhưng chưa có dữ liệu onset.

**Đề xuất (ưu tiên giảm dần):**
1. **`vedit validate` cảnh báo cắt giữa từ** — độ khó thấp. Khi có `words`, cảnh báo nếu `clip.start` hoặc
   `clip.end` rơi vào trong một từ, hoặc cách mép từ dưới 30 ms.
2. **Thêm vào prompt Agent 2** — độ khó thấp:
   - bảng khoảng lặng ở trên;
   - padding 50/80 ms;
   - "cắt sau phản ứng/tiếng cười";
   - ghi `note` theo mẫu `BEAT — "trích lời" — lý do`;
   - tự cộng tổng thời lượng và tự cắt beat nếu vượt.
3. **Lệnh `vedit snap <slug>`** — độ khó trung bình. In đề xuất start/end đã snap (dùng hàm trên) cho từng
   clip có lời, Agent 2/3 tự chọn áp dụng.
4. **Áp dụng ý tưởng cho video không lời** — độ khó trung bình. Dò onset tiếng động, ví dụ bằng `astats` theo
   cửa sổ ngắn hoặc `silencedetect` ngưỡng cao. Coi onset như "từ": không cắt ngang đuôi vang của một tiếng va
   chạm, và đặt điểm cắt trong khoảng lặng giữa hai tiếng động. Ngưỡng cụ thể cần đo trên footage thật.
5. **Hạ ngưỡng `silencedetect`** xuống khoảng 0.15–0.4 s, nhưng gắn nhãn "cần kiểm tra hình" thay vì coi là
   điểm cắt sạch — độ khó thấp.
