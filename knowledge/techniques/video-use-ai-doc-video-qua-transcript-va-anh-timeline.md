---
title: video-use: AI đọc video qua transcript và ảnh timeline
category: techniques
tags: [video-use, transcript, scribe, timeline view, filmstrip, waveform, phân tích video, token, whisper]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/README.md
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/helpers/transcribe.py
  - https://github.com/browser-use/video-use/blob/main/helpers/transcribe_batch.py
  - https://github.com/browser-use/video-use/blob/main/helpers/pack_transcripts.py
  - https://github.com/browser-use/video-use/blob/main/helpers/timeline_view.py
  - https://github.com/browser-use/video-use/blob/main/poster.html
  - https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/Whisper_prompting_guide.ipynb
  - https://raw.githubusercontent.com/SYSTRAN/faster-whisper/master/faster_whisper/transcribe.py
---
# video-use: AI đọc video qua transcript và ảnh timeline

video-use giải quyết câu hỏi "LLM hiểu video thế nào" mà không đưa từng khung hình cho model:
"Same idea as browser-use giving an LLM a structured DOM instead of a screenshot — but for video."
Có hai lớp. Lớp 1 là văn bản, luôn được nạp. Lớp 2 là ảnh, chỉ tạo khi cần quyết định.

## Lớp 1 — transcript cấp từng từ (luôn nạp)
**Bước 1, tách âm thanh và chặn track câm:**
```bash
ffmpeg -y -i SRC.mp4 -map 0:a:0 -vn -ac 1 -ar 16000 -c:a pcm_s16le take.wav
```
- Nếu đỉnh nhỏ hơn **-60 dBFS** thì từ chối upload, vì "Uploading silence costs the same as uploading speech".
- Có `--audio-track K` để chọn track. Ví dụ OBS ghi game ở track 0, mic ở track 1; mặc định ffmpeg lại chọn
  track có nhiều kênh nhất. Transcript của track khác 0 lưu tên `<tên>.trackK.json`.

**Bước 2, gọi Scribe:** `POST https://api.elevenlabs.io/v1/speech-to-text` với
`model_id=scribe_v1, diarize=true, tag_audio_events=true, timestamps_granularity=word`. Tuỳ chọn thêm
`language_code` và `num_speakers`. Timeout 1800 s. Kết quả cache ở `edit/transcripts/<tên>.json` và không bao
giờ transcribe lại ("Immutable outputs of immutable inputs").
- Mỗi phần tử trong `words[]` có `type` là `word`, `spacing` hoặc `audio_event`, kèm `start`, `end`,
  `speaker_id` (dạng `"speaker_0"`).
- Hard Rule 8: "Word-level verbatim ASR only. Never SRT/phrase mode (loses sub-second gap data). Never
  normalized fillers (loses editorial signal)."

**Bước 3, pack thành bản đọc chính (`takes_packed.md`):**
- Gom từ thành cụm. Ngắt cụm khi một `spacing` ≥ **0.5 s**, khi khoảng hở so với token trước ≥ 0.5 s, hoặc
  khi **đổi người nói**.
- `audio_event` được đặt trong ngoặc, ví dụ `(laughter)`.
- Dấu câu dính liền với từ trước (`" ,"` → `","`).
```
## C0103  (duration: 43.0s, 8 phrases)
  [002.52-005.36] S0 Ninety percent of what a web agent does is completely wasted.
  [006.08-006.74] S0 We fixed this.
```
- Mốc định dạng `{:06.2f}` để các dòng thẳng cột.
- "duration" trong tiêu đề là khoảng từ cụm đầu đến cụm cuối, **không phải** độ dài file.
- Theo docstring, cách này đặt được một giờ footage vào khoảng 1/10 số token so với JSON thô, mà vẫn giữ độ
  chính xác ở cấp ranh giới từ.

## Lớp 2 — `timeline_view` (chỉ khi cần)
Lệnh: `python helpers/timeline_view.py <video> <start> <end> [-o out.png] [--n-frames 10] [--transcript t.json]`.
Ảnh ghép rộng tối thiểu 1920 px, gồm:
- Tiêu đề: tên file, khoảng thời gian, số khung.
- **Filmstrip:** N khung chia đều. Mỗi khung lấy bằng một lệnh `ffmpeg -ss t -i v -frames:v 1 -q:v 4 -vf scale=320:-2`, cao 180 px.
- **Waveform RMS:** WAV 16 kHz, cửa sổ = số mẫu / độ rộng, chuẩn hoá về 0..1, cao 220 px.
- **Vùng lặng ≥ 400 ms** tô xanh mờ, kèm chú thích "safe cut candidates".
- **Nhãn từ** phía trên waveform: bỏ từ ngắn hơn 50 ms, các nhãn cách nhau ít nhất 28 px.
- Thước 7 mốc thời gian.

Quy tắc dùng: "**Not a scan tool** — use it at decision points, not constantly". Chỉ mở ở các chỗ sau:
- Chỗ dừng mơ hồ.
- So sánh các take.
- Kiểm tra điểm cắt.
- Lúc mở đầu, xem 1–2 ảnh để có "ấn tượng thị giác".
- Self-eval trên **bản đã render**.

## Vì sao cách này hiệu quả
1. Văn bản là bề mặt chính. README ước tính: "30,000 frames × 1,500 tokens = 45M tokens of noise" so với
   "12KB text + a handful of PNGs".
2. "Audio is primary, visuals follow": điểm cắt được rút ra từ ranh giới từ và khoảng lặng, là số đo chính
   xác, không phải ước lượng từ ảnh.
3. Hình ảnh chỉ dùng ở điểm quyết định, nên mỗi ảnh đều có câu hỏi cụ thể đi kèm.

## Công thức ffmpeg thuần cho ảnh timeline (đã chạy thử, ffmpeg 6.1, 2026-10-31)
Không cần PIL. Lệnh tạo filmstrip 8 khung có nhãn giây (theo giây của file), waveform, và một vạch đỏ ở giữa
(dùng khi tâm cửa sổ là một điểm cắt):
```bash
S=1.5; D=3; N=8   # bắt đầu, độ dài cửa sổ, số khung
ffmpeg -hide_banner -loglevel error -y -ss $S -t $D -i in.mp4 -filter_complex \
"[0:v]fps=$N/$D,scale=-2:240,drawtext=fontfile=/usr/share/fonts/opentype/inter/Inter-Bold.otf:\
text='%{pts\:flt\:$S}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6,\
tile=${N}x1:padding=4:color=0x121216[strip];[strip]scale=1600:-2[s];\
[0:a]aformat=channel_layouts=mono,showwavespic=s=1600x200:colors=0x8CB4FF:scale=sqrt,\
drawbox=x=iw/2-1:y=0:w=2:h=ih:color=red@0.9:t=fill[w];[s][w]vstack[out]" \
-map "[out]" -frames:v 1 timeline.png
```
- `scale=sqrt` giúp thấy rõ âm nhỏ (ASMR). Muốn so mức tuyệt đối thì bỏ tham số này.
- Nhãn `%{pts\:flt\:S}` in giây dạng `1.500000`. Bản `hms` dài 12 ký tự, dễ tràn khung dọc nhỏ.
- File không có âm thanh thì bỏ nhánh `[0:a]`.

## Bảng: xem gì khi nào
| Câu hỏi | Dùng |
|---|---|
| Nội dung nói gì, beat nào nằm ở đâu, take nào sạch | `takes_packed.md` |
| Cắt ở đâu để không cụt từ | Mốc từ trong JSON, khoảng lặng ≥ 400 ms |
| Hai take giống lời, take nào diễn tốt hơn | `timeline_view` từng take |
| Điểm cắt có giật hình hay "tách" tiếng không | `timeline_view` trên bản render, ±1.5 s quanh điểm cắt |

## Áp dụng vào vedit
**Đã có:**
- `vedit analyze` → `analysis.json` gồm:
  - cảnh (scene > 0.15, tối thiểu 0.8 s);
  - lặng (`silencedetect` -35 dB, ≥ 0.6 s);
  - tối đa 16 khung ở giữa các cảnh;
  - loudness;
  - transcript faster-whisper (tuỳ chọn, `small`, `vi`, có `word_timestamps`, `vad_filter`).
- `vedit frame <dự án> <giây> --grid`.

**Còn thiếu:**
- Chưa có bản đọc gọn: Agent 2 phải đọc JSON dài.
- Transcript chia theo segment của Whisper, không theo khoảng lặng.
- Không có ảnh filmstrip + waveform.
- Không có diarization hay audio event.
- Với video không lời, không có danh sách tiếng động. Plan gần nhất (`20261030-video-01`) phải ghi tay các
  mốc như tiếng "cạch" ở 0.75–1.0 s nguồn hay "keng" ở 18.25 s.

**Đề xuất (ưu tiên giảm dần):**
1. **`analysis/packed.md`** — độ khó thấp. Mỗi cảnh một dòng `[start-end] cảnh k`, transcript ngắt cụm ở lặng
   ≥ 0.5 s, và (mới) danh sách onset tiếng động lớn. Agent 2 đọc file này trước; JSON chỉ để tra cứu.
2. **`vedit timeline <dự án|file> <start> <end> [--source preview|final] [--cut T]`** dựa trên lệnh ffmpeg ở
   trên — độ khó thấp. Agent 2 dùng để chọn điểm cắt, Agent 3 dùng để QA.
3. **Giữ từ đệm khi dùng faster-whisper** — độ khó thấp, cần thử. Có tham số `initial_prompt`. Cookbook của
   OpenAI ghi: "Transcripts follow the style of the prompt", và chỉ 224 token cuối của prompt được dùng. Thử một
   prompt có sẵn "ừm, à, ờ, thì, kiểu là" xem Whisper có giữ từ đệm tiếng Việt không.
4. **Scribe cho tiếng Việt** — độ khó trung bình, có phí. Theo kết quả tìm kiếm, trang ElevenLabs
   (elevenlabs.io/speech-to-text/vietnamese) liệt kê tiếng Việt trong 99 ngôn ngữ; tôi chưa đọc trực tiếp vì
   môi trường chặn `elevenlabs.io`. Muốn dùng phải mở `api.elevenlabs.io` và để người dùng tự đưa key.
