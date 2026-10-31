---
title: video-use: Phụ đề cụm 2-3 từ theo mốc từng từ
category: techniques
tags: [video-use, phụ đề, captions, srt, chunk, uppercase, safe zone, libass, force_style, tiếng việt]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/helpers/render.py
  - https://github.com/browser-use/video-use/blob/main/tests/test_render_captions.py
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
---
# video-use: Phụ đề cụm 2-3 từ theo mốc từng từ

Phụ đề có 3 chiều cần cân nhắc:
- **chunking:** 1, 2, 3 từ hay cả câu mỗi lần hiện;
- **case:** IN HOA, Title Case hay viết thường tự nhiên;
- **placement:** cách mép dưới bao nhiêu.

"The right combo depends on content." video-use tự sinh phụ đề từ transcript cấp từ cộng với EDL
(`render.py --build-subtitles` → `edit/master.srt`).

## Thuật toán chia cụm `chunk_words` (nguyên văn, MIT © 2026 Browser Use)
```python
CHUNK_WORDS = 2         # target words per cue
CHUNK_MAX_WORDS = 3     # a too-short chunk may grow to this many words
CHUNK_MIN_S = 0.35      # a cue shorter than this reads as a flash
CHUNK_PAUSE_S = 0.3     # a gap this long between words ends the cue
PUNCT_BREAK = set(".,!?;:")

def chunk_words(words):
    words = [w for w in words if (w.get("text") or "").strip()]
    chunks, current = [], []
    for i, w in enumerate(words):
        current.append(w)
        text = w["text"].strip()
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["start"] - w["end"]) if nxt else 0.0
        dur = w["end"] - current[0]["start"]
        if (nxt is None or text[-1] in PUNCT_BREAK or gap >= CHUNK_PAUSE_S
                or len(current) >= CHUNK_MAX_WORDS
                or (len(current) >= CHUNK_WORDS and dur >= CHUNK_MIN_S)):
            chunks.append(current)
            current = []
    return chunks
```
Một cue đóng lại khi gặp một trong các điều kiện:
- từ có dấu câu ở cuối;
- khoảng nghỉ tới từ kế ≥ 0.3 s;
- đủ 3 từ;
- có ≥ 2 từ **và** đã kéo dài ≥ 0.35 s.

Ví dụ từ test, câu "90% of what a web agent does is completely wasted. We fix this." được chia thành
`90% of | what a web | agent does | is completely | wasted. | We fix this.` Cách cũ ghép cứng từng cặp từ cho ra
"does is", vắt qua một khoảng nghỉ 0.34 s. Còn "what a" nói quá nhanh nên được nới thành 3 từ để không chớp.

## Mốc thời gian trên timeline xuất (Hard Rule 5)
`output_time = word.start − segment_start + segment_offset`. Trong đó `segment_offset` là tổng độ dài các đoạn
trước.

Chi tiết cách làm:
- Lấy mọi từ `type == "word"` có giao với `[start, end]` của đoạn.
- Kẹp mốc vào trong đoạn.
- Nếu `end ≤ start` thì gán `end = start + 0.4`.
- Bỏ `,;:` ở cuối cue, chuyển IN HOA, sắp xếp lại rồi ghi SRT.

Ví dụ trong test: đoạn nguồn 2.55–6.8 s → cue đầu tiên `"90% OF"`, `00:00:00,090 --> 00:00:00,590`.

## Kiểu chữ `bold-overlay` (mặc định trong code)
```
FontName=Helvetica,FontSize=18,Bold=1,
PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H00000000,
BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=90
```
- SRT đưa qua filter `subtitles` dùng không gian PlayRes 384×288 (mặc định của ffmpeg), nên libass scale theo
  chiều cao.
- `FontSize=18` ≈ 18/288 = **6.25% chiều cao khung** (khoảng 120 px trên khung 1920).
- `MarginV=90` đặt chân chữ ở khoảng **31% từ đáy lên**.
- Comment trong code: "MarginV is NOT taste — it is a platform safe-zone rule". Giao diện TikTok/Reels/Shorts che
  khoảng 25–30% phía dưới khung 1080×1920. "Do not drop this below ~75" (75/288 ≈ 26%).
- **Đo thực tế** (2026-10-31, khung 1080×1920, ffmpeg 6.1): chữ "TEST CAPTION" có chân chữ cách đáy **623 px
  (32.4%)**, chữ in hoa cao **74 px**. Helvetica không có trên máy nên fontconfig âm thầm thay bằng
  **Liberation Sans**, đúng lỗi "fonts fail silently".
- **Lệch tài liệu:** SKILL.md vẫn ghi `MarginV=35` (≈ 12% từ đáy, nằm dưới giao diện app); code đã sửa thành 90.
- Phụ đề luôn được áp **sau cùng** (Rule 1).

Kiểu thứ hai SKILL.md gợi ý là `natural-sentence`, cho video kể chuyện, tài liệu, giáo dục:
- 4–7 từ mỗi cue, viết thường như câu;
- ngắt ở chỗ nghỉ tự nhiên;
- `MarginV` 60–80, chữ to hơn, khung rộng hơn.

Kiểu này không có `force_style` dựng sẵn, cần tự thiết kế.

## Chuyển sang tiếng Việt (đề xuất, cần thử trên footage thật)
- Whisper và các ASR khác tách tiếng Việt theo **âm tiết** (cách nhau bằng dấu cách). Một "từ" trong JSON vì thế
  thường chỉ là nửa từ ghép: "cà | pháo", "nước | muối". Giữ nguyên `CHUNK_WORDS = 2` sẽ cắt đôi rất nhiều từ ghép.
  Nên thử 3–4 âm tiết mỗi cue, tối đa 5–6, giữ `CHUNK_MIN_S = 0.35` và `CHUNK_PAUSE_S = 0.3`.
- Nếu muốn tránh tách từ ghép, cần một bộ tách từ tiếng Việt. Đây là một phụ thuộc mới, phải cân nhắc trước khi
  thêm.
- Viết IN HOA tiếng Việt thì dấu chồng lên chữ hoa (Ế, Ộ, Ữ), làm khối chữ cao hơn. Cần font hỗ trợ đầy đủ dấu
  (vedit có Be Vietnam Pro) và kiểm tra khoảng cách dòng khi xuống dòng.

## Áp dụng vào vedit
**Đã có** (ở một số điểm vedit mạnh hơn):
- `Captions` có `segments`, `words`, 4 style (`clean`, `boxed`, `bold_pop`, `karaoke`), `uppercase`,
  `highlight_color`.
- PlayRes = kích thước canvas, nên vị trí tính chính xác theo pixel.
- `lower` neo ở 24% từ đáy.
- ASS được vẽ sau cùng.

**Còn thiếu:**
- Không có bước **tự sinh** cue từ mốc từng từ.
- Agent 2 tự quy đổi mốc theo đoạn cắt bằng tay. Mỗi lần Agent 3 đổi độ dài hay thứ tự clip thì phải "dời mốc"
  thủ công, rất dễ lệch.
- Không có luật chống cue chớp (dưới 0.35 s).

**Đề xuất (ưu tiên giảm dần):**
1. **`captions.auto: true`** (hoặc lệnh `vedit captions <slug>`) — độ khó trung bình. Renderer tự dựng
   `segments` từ `analysis.json` mỗi lần render, nên không bao giờ lệch sau khi sửa clip:
   - Với clip `i` (offset lấy từ `plan.clip_offsets()`), lấy các từ giao với `[clip.start, clip.end]`.
   - Mốc ra `t = offset_i + (w.start − clip.start) / clip.speed`, kẹp vào trong clip.
   - Ở đoạn chồng của transition, kết thúc cue cũ trước khi cue mới bắt đầu.
   - Chia cụm bằng `chunk_words` đã chỉnh cho âm tiết tiếng Việt, giữ lại `words` để style `karaoke` dùng.
2. **`validate` cảnh báo cue ngắn** — độ khó thấp. Cảnh báo cue dưới 0.35 s, cue nằm trong 22% đáy khung dọc, và
   cue trùng thời điểm với một `texts` ở cùng vùng khung.
3. **Hai preset phụ đề rõ ràng** — độ khó thấp. "nhanh" gồm 3–4 âm tiết, `bold_pop`, `lower`; "kể chuyện" gồm
   5–8 âm tiết, `clean`/`boxed`. Agent 2 chọn theo thể loại thay vì luôn dùng một kiểu.
