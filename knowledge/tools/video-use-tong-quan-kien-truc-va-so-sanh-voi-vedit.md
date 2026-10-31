---
title: video-use: Tổng quan kiến trúc và so sánh với vedit
category: tools
tags: [video-use, browser-use, claude-code, skill, edl, ffmpeg, scribe, kiến trúc, so sánh, license]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use
  - https://github.com/browser-use/video-use/blob/main/README.md
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/install.md
  - https://github.com/browser-use/video-use/blob/main/LICENSE
  - https://github.com/browser-use/video-use/blob/main/pyproject.toml
  - https://github.com/browser-use/video-use/blob/main/helpers/render.py
  - https://github.com/browser-use/video-use/blob/main/helpers/grade.py
  - https://github.com/browser-use/video-use/blob/main/helpers/transcribe.py
  - https://github.com/browser-use/video-use/blob/main/helpers/transcribe_batch.py
  - https://github.com/browser-use/video-use/blob/main/helpers/pack_transcripts.py
  - https://github.com/browser-use/video-use/blob/main/helpers/timeline_view.py
  - https://github.com/browser-use/video-use/blob/main/poster.html
  - https://github.com/browser-use/video-use/tree/main/tests
  - https://github.com/browser-use/video-use/tree/main/skills/manim-video
  - https://raw.githubusercontent.com/NousResearch/hermes-agent/main/LICENSE
  - https://raw.githubusercontent.com/NousResearch/hermes-agent/main/skills/creative/manim-video/SKILL.md
  - https://raw.githubusercontent.com/heygen-com/hyperframes/main/README.md
---
# video-use: Tổng quan kiến trúc và so sánh với vedit

> Đã đọc đủ 36 file của repo tại commit `43cfc56` (2026-10-08). Trang GitHub xem ngày 2026-10-31: khoảng
> 30.2k sao, 3.5k fork, 23 commit, license MIT. Các ghi chú chi tiết có tiền tố `video-use-` trong
> `techniques/`, `scripting/`, `ffmpeg/`, `audio/`.

## Tóm tắt
- **Là gì:** một *skill* cho agent có shell (Claude Code, Codex, Hermes, OpenClaw). Người dùng bỏ footage thô
  vào một thư mục, mở agent ở đó, chat ("edit these into a launch video") và nhận `edit/final.mp4`. Không có
  app, GUI hay server. "Bộ não" là chính model đang chạy agent: nó đọc `SKILL.md` rồi gọi 6 script Python
  trong `helpers/`. Ảnh banner chụp phiên Claude Code chạy Opus 4.6 (1M context).
- **Ý tưởng cốt lõi:** "The LLM never watches the video. It **reads** it." Lớp 1 là transcript cấp từng từ,
  luôn được nạp. Lớp 2 là ảnh ghép filmstrip + waveform, chỉ tạo khi cần quyết định. README so sánh
  "30,000 frames × 1,500 tokens = **45M tokens of noise**" với "**12KB text + a handful of PNGs**".
- **Mạnh nhất với** video có lời nói, nhiều take (talking head, launch, tutorial, phỏng vấn), vì nó cắt chính
  xác theo ranh giới từ.

## Thành phần
| File | Vai trò |
|---|---|
| `SKILL.md` (342 dòng) | Prompt chính: 7 nguyên tắc, 12 Hard Rules, quy trình 8 bước, cut craft, brief cho sub-agent, màu, phụ đề, animation, âm thanh, EDL, memory, anti-pattern |
| `install.md` | Prompt cài đặt dành cho agent: clone, `uv sync`, ffmpeg, symlink skill, hỏi key ElevenLabs, kiểm tra bằng một lệnh thật |
| `helpers/transcribe.py` | ffmpeg → WAV mono 16 kHz → ElevenLabs Scribe (`scribe_v1`, diarize, audio events, mốc từng từ) → `edit/transcripts/<tên>.json` (có cache) |
| `helpers/transcribe_batch.py` | Chạy cả thư mục với 4 luồng song song |
| `helpers/pack_transcripts.py` | JSON → `takes_packed.md`: các cụm câu, ngắt khi lặng ≥ 0.5 s hoặc đổi người nói |
| `helpers/timeline_view.py` | Ảnh PNG gồm filmstrip N khung, waveform RMS, nhãn từ, tô vùng lặng ≥ 400 ms |
| `helpers/render.py` | EDL → trích từng đoạn (grade, fade 30 ms, tone-map HDR) → concat `-c copy` → overlay dời PTS → phụ đề sau cùng → loudnorm 2 lượt |
| `helpers/grade.py` | Preset màu, cộng auto-grade theo `signalstats` (mọi chỉnh sửa giới hạn ±8%) |
| `skills/manim-video/` | Skill con cho animation Manim (vendored từ NousResearch/hermes-agent) |
| `tests/` | 3 file unittest: chia cụm phụ đề, fps, nhận dạng video dọc khi có xoay |
| `poster.html`, `static/` | Hình minh hoạ cho README |

## Luồng xử lý
```
Transcribe ──> Pack ──> LLM Reasons ──> EDL ──> Render ──> Self-Eval
                                                              └─ issue? fix + re-render (max 3)
```
Quy trình 8 bước trong SKILL.md:
1. **Inventory:** `ffprobe` mọi nguồn, chạy `transcribe_batch.py`, chạy `pack_transcripts.py`, xem 1–2
   `timeline_view` để có "visual first impression".
2. **Pre-scan:** đọc `takes_packed.md` một lượt, liệt kê chỗ nói vấp, nói nhầm, câu nên tránh.
3. **Converse:** mô tả lại bằng lời những gì thấy, rồi hỏi các câu "shaped by the material". Không dùng
   checklist cố định.
4. **Propose strategy:** viết 4–8 câu, rồi **chờ người dùng xác nhận**.
5. **Execute:** editor sub-agent viết `edl.json`; xem `timeline_view` ở chỗ mơ hồ; dựng animation bằng
   sub-agent song song; grade từng đoạn; ghép bằng `render.py`.
6. **Preview:** chạy `render.py --preview`.
7. **Self-eval** trên bản đã render, tại mọi điểm cắt. Thứ sẽ đăng công khai thì thêm một critic sub-agent.
   Tối đa 3 vòng.
8. **Iterate + persist:** sửa theo phản hồi, không transcribe lại, ghi thêm vào `edit/project.md`.

## AI "hiểu" video thế nào
- Code không gọi API thị giác nào. Phần nhìn là các PNG do `timeline_view.py` tạo; agent tự đọc ảnh bằng
  khả năng đa phương thức của model đang chạy.
- Phần nghe dùng ElevenLabs Scribe, một API trả phí cần `ELEVENLABS_API_KEY`. Kết quả là transcript verbatim
  (giữ "umm", nói lại), có speaker diarization, audio event như `(laughter)` và mốc từng từ. SKILL.md xếp
  Whisper chạy local trên CPU vào anti-pattern: "Slow and it normalizes fillers".
- Ra quyết định: LLM đọc transcript rồi tự chọn cảnh. Viết "hand-tuned moment-scoring functions" là
  anti-pattern ("The LLM picks better than any heuristic you'll write"). Không có scene detection, beat
  detection hay nhận diện khuôn mặt.

## EDL (`edit/edl.json`)
```json
{"version": 1,
 "sources": {"C0103": "/abs/path/C0103.MP4"},
 "ranges": [{"source": "C0103", "start": 2.42, "end": 6.85, "beat": "HOOK",
             "quote": "...", "reason": "Cleanest delivery, stops before slip at 38.46."}],
 "grade": "warm_cinematic",
 "overlays": [{"file": "edit/animations/slot_1/render.mp4", "start_in_output": 0.0, "duration": 5.0}],
 "subtitles": "edit/master.srt",
 "total_duration_s": 87.4}
```
`grade` có thể là tên preset, chuỗi filter ffmpeg thô hoặc `"auto"`. Không có schema hay validator.

## Render, chữ, đồ hoạ, âm thanh (tóm tắt)
- **Render:** chỉ dùng ffmpeg qua subprocess, không moviepy. HyperFrames, Remotion, Manim và PIL chỉ dùng để
  dựng *clip animation rời*, sau đó overlay lên video. Xem `ffmpeg/video-use-pipeline-render-tung-doan-overlay-phu-de-cuoi`.
- **Phụ đề:** SRT + `force_style` (Helvetica 18 Bold, viền 2, `MarginV=90`), cụm 2–3 từ IN HOA. Xem
  `techniques/video-use-phu-de-cum-2-3-tu-theo-moc-tung-tu`.
- **Đồ hoạ:** mỗi animation do một sub-agent viết code rồi render ra `animations/slot_<id>/render.mp4`. Xem
  `techniques/video-use-animation-overlay-easing-va-thoi-diem-payoff`.
- **Âm thanh:** fade 30 ms ở mọi đoạn, loudnorm 2 lượt (-14 LUFS / -1 dBTP / LRA 11). Với nhạc và SFX, SKILL.md
  chỉ có hướng dẫn; helpers **không có code** trộn nhạc, ducking hay transition. Xem
  `audio/video-use-am-thanh-fade-30ms-sfx-dung-khung-loudnorm-2-luot`.

## Câu prompt then chốt (nguyên văn)
- "Artistic freedom is the default. Every specific value, preset, font, color, duration, pitch structure, and
  technique in this document is a *worked example* from one proven video — not a mandate."
- "**The only things you MUST do are in the Hard Rules section below.** Everything else is yours."
- "Never touch the cut until the user has confirmed the strategy in plain English."
- "Verify your own output before showing it to the user. If you wouldn't ship it, don't present it."
- Về critic: "Brief it to roast, not to praise".
- Về âm thanh: "You cannot listen: say so, and report the numbers."

## Phụ thuộc và cách chạy
- Python ≥ 3.10. `pyproject.toml` khai báo `requests, librosa, matplotlib, pillow, numpy`, nhưng helpers chỉ
  import `requests`, `numpy`, `PIL`; librosa và matplotlib không được dùng. Cần ffmpeg/ffprobe (bản ≥ 4.x là
  đủ). yt-dlp tuỳ chọn. HyperFrames cần Node 22+. Remotion và Manim (cộng LaTeX) chỉ cài khi cần.
- Cài: `git clone` → `uv sync` (hoặc `pip install -e .`) → `ln -sfn ~/Developer/video-use ~/.claude/skills/video-use`
  (symlink **cả thư mục** để `helpers/` nằm cạnh SKILL.md) → `.env` chứa `ELEVENLABS_API_KEY=` (kiểm tra:
  `GET https://api.elevenlabs.io/v1/user` trả 200).
- Lệnh helper:
  `python helpers/transcribe_batch.py <dir> [--num-speakers N] [--audio-track K]`,
  `python helpers/pack_transcripts.py --edit-dir <dir>/edit`,
  `python helpers/timeline_view.py <video> <start> <end> [--n-frames 10]`,
  `python helpers/render.py edit/edl.json -o edit/final.mp4 [--preview|--draft] [--build-subtitles] [--fps 30]`,
  `python helpers/grade.py --analyze <video>`.

## Giới hạn (quan sát từ code)
1. Phụ thuộc vào lời nói. Với footage không thoại (ASMR, B-roll, montage nhạc) chỉ còn `timeline_view` xem tay.
2. Bắt buộc có API trả phí ElevenLabs. Môi trường vedit hiện chặn `elevenlabs.io`.
3. `render.py` chỉ nối thẳng một track: không có transition, không crop sang khung dọc (chỉ scale về 1080 theo
   chiều của nguồn), không trộn nhạc/SFX, overlay là clip phủ toàn khung. Lệnh không ép decoder
   `-c:v libvpx-vp9`, nên overlay WebM trong suốt **mất alpha**. Đã thử trên ffmpeg 6.1: decoder VP9 mặc định đọc
   ra `yuv420p`, không có kênh alpha.
4. Video bị encode 2 lần khi có overlay/phụ đề: trích đoạn ở CRF 20, rồi composite ở CRF 18.
5. Font phụ đề là Helvetica. Linux thường không có font này nên sẽ fallback âm thầm, đúng cái lỗi chính
   SKILL.md cảnh báo.
6. Tài liệu lệch với code:
   - SKILL.md ghi `MarginV=35`, code dùng `MarginV=90`.
   - SKILL.md nói `--preview` ra 720p, nhưng trong code preview là 1080p CRF 22; chỉ `--draft` mới ra 720p.
   - `timeline_view` chú thích lọc từ "≥ 120ms" nhưng code lọc ở 50 ms.
   - Chế độ `--edl` chưa làm.
   - Poster vẽ "speaker track" và vạch "CUT", nhưng tool thật không vẽ hai thứ đó.
7. Không có schema kiểm tra EDL.

## License (quan trọng khi tái sử dụng)
- **MIT**, "Copyright (c) 2026 Browser Use". Được dùng, sửa, gộp và phân phối, kể cả thương mại. Điều kiện duy
  nhất: giữ thông báo bản quyền và văn bản MIT trong mọi bản sao hoặc "substantial portions".
- `skills/manim-video` có nguồn gốc từ NousResearch/hermes-agent (`skills/creative/manim-video`, cũng MIT,
  "Copyright (c) 2025 Nous Research", front matter gốc ghi tác giả "SHL0MS, Hermes Agent"). Nếu chép phần này
  thì ghi cả hai nguồn.
- HyperFrames (heygen-com) dùng Apache-2.0 theo README của nó.
- **Kết luận:** vedit được phép port code (`chunk_words`, `auto_grade_for_clip`, loudnorm 2 lượt, ý tưởng
  `timeline_view`...). Khi port, thêm header ghi nguồn + license vào file, hoặc lập `THIRD_PARTY_NOTICES.md`.

## So sánh từng điểm với vedit
| Khía cạnh | video-use | vedit hiện tại | Nhận xét |
|---|---|---|---|
| Kiến trúc agent | 1 agent chính + sub-agent tạm thời (chọn take, mỗi animation một con, critic) | 3 agent cố định (nghiên cứu, kịch bản, dựng) + điều phối viên | vedit có kịch bản/trend; video-use có critic và animation song song |
| Hiểu video | Transcript Scribe cấp từ, verbatim, diarize, audio event → `takes_packed.md`; `timeline_view` khi cần | `analysis.json`: cảnh (scene > 0.15), lặng (-35 dB, ≥ 0.6 s), ≤ 16 khung giữa cảnh, faster-whisper tuỳ chọn, loudness; `vedit frame --grid` | vedit hợp hơn với footage không lời; thiếu bản đọc gọn và ảnh filmstrip + waveform |
| Hợp đồng dựng | `edl.json` tự do, không validate | `EditPlan` pydantic, validate với media thật | vedit tốt hơn |
| Render | Nhiều bước, concat copy, encode 2 lần | Một filter graph, encode 1 lần, timeline theo khung nguyên | vedit cho chất lượng tốt hơn; video-use sửa lặp nhanh hơn nhờ cache từng đoạn |
| Transition / khung dọc | Không có | 22 kiểu xfade; cover/contain/blur + focus | vedit |
| Phụ đề | Tự sinh từ transcript (cụm 2–3 từ, tự tính offset) | 4 style ASS + karaoke; Agent 2 tự quy đổi mốc bằng tay | video-use tự động hơn |
| Đồ hoạ | Clip animation viết bằng code (PIL/HyperFrames/Remotion/Manim) | Vector ASS dựng sẵn: callout, badge, progress, highlight, sparkles, flash; 10 kiểu chữ động | vedit nhanh và đồng bộ; video-use không giới hạn ý tưởng |
| Màu | Auto-grade từng đoạn ±8%, preset, filter tự do | 6 look cho cả timeline + vignette/grain | Nên ghép cả hai |
| HDR (iPhone HLG) | Tone-map sang SDR | Chưa có | Thiếu |
| Âm ở điểm cắt | `afade` 30 ms mỗi đoạn | Cắt thẳng không fade (chỉ có `acrossfade` khi dùng transition) | Thiếu, dễ có tiếng "tách" |
| Loudness | loudnorm 2 lượt, đo lại bằng ebur128 | loudnorm 1 lượt trong graph (-14 / -1.5 / 11), tắt được; không đo lại | Thiếu bước đo |
| Nhạc / SFX | Chỉ có hướng dẫn | Track nhạc/voiceover/SFX, ducking sidechain, 7 SFX tổng hợp | vedit |
| QA | `timeline_view` ±1.5 s tại mọi điểm cắt, 2 s đầu/cuối, ffprobe, ebur128, critic, ≤ 3 vòng | Xem khung giữa clip và lúc chữ xuất hiện, 1–3 vòng | Thiếu kiểm điểm cắt, âm thanh và critic |
| Làm việc với người dùng | Hỏi → đề xuất chiến lược → chờ duyệt | Mặc định TikTok/30 s, chỉ hỏi khi thiếu mục tiêu | Có thể là nguyên nhân "chưa đúng ý" |
| Bộ nhớ | `project.md` ghi sau mỗi phiên | Không có | Thiếu |
| Triết lý sáng tạo | 12 Hard Rules về kỹ thuật, còn lại tự do; "Invent freely" | "Lớp sáng tạo (bắt buộc)" liệt kê sẵn các hiệu ứng | vedit dễ ra video theo khuôn |

## Áp dụng vào vedit
**Đã có (giữ nguyên):**
- Một graph ffmpeg encode một lần.
- `EditPlan` có validate.
- Transition, reframe dọc, ASS động, ducking, SFX tổng hợp.
- Thứ tự lớp đúng Hard Rule 1: chữ/phụ đề ASS được vẽ sau ảnh overlay.

**Còn thiếu (bằng chứng cụ thể):**
- Không có bước duyệt chiến lược trước khi dựng.
- Prompt bắt buộc một bộ hiệu ứng cố định. Plan gần nhất (`20261030-video-01`, dài 15.8 s) có 13 đồ hoạ và
  10 SFX, trong đó 6 tiếng `pop` đi kèm badge.
- Không fade âm ở chỗ cắt thẳng.
- Không đo loudness sau render: bản final gần nhất đo được **-27.5 LUFS**, TP -2.2 dBFS (ebur128, ngày 2026-10-31).
- QA không kiểm tra điểm cắt.
- Không có critic.
- Không có bộ nhớ phiên.

**Đề xuất theo ưu tiên** (chi tiết trong các ghi chú riêng):
1. **Duyệt chiến lược trước khi dựng.** Sau `vedit analyze`, mô tả video bằng lời, hỏi 2–4 câu theo chất
   liệu, đề xuất 4–8 câu kèm 2 hướng sáng tạo tương phản, chờ người dùng chọn. Độ khó: thấp, chỉ sửa
   `.claude/skills/lam-video` và prompt Agent 2. → `scripting/video-use-quy-trinh-hoi-de-xuat-chien-luoc-va-cho-duyet`
2. **Tách "Hard rules" khỏi "gợi ý thẩm mỹ" trong prompt Agent 2/3.** Bỏ chữ "bắt buộc" ở lớp sáng tạo, yêu
   cầu có một câu "ý tưởng dựng" rồi mới chọn hiệu ứng. Độ khó: thấp. → `scripting/video-use-pha-khuon-sang-tao-bang-scamper-va-dao-gia-dinh`
3. **Thêm `afade` 30 ms ở mọi chỗ cắt thẳng** trong `render.py`. Độ khó: thấp. → `audio/video-use-am-thanh-fade-30ms-sfx-dung-khung-loudnorm-2-luot`
4. **Thêm `vedit qa <slug>`:** tạo ảnh filmstrip + waveform ±1.5 s ở mọi điểm cắt, kiểm tra độ dài, đo
   I/TP/LRA và RMS từng đoạn; kèm subagent `video-critic`. Độ khó: thấp–trung bình. → `techniques/video-use-tu-kiem-tra-ban-dung-tai-moi-diem-cat-va-critic`
5. **Phụ đề tự sinh** từ mốc từng từ + clip (offset theo speed và transition), chia cụm theo âm tiết tiếng
   Việt. Độ khó: trung bình. → `techniques/video-use-phu-de-cum-2-3-tu-theo-moc-tung-tu`
6. **Tone-map HDR** (HLG/PQ) khi probe thấy `color_transfer` là HDR. Độ khó: thấp; `zscale` đã có trong
   ffmpeg 6.1 của môi trường. → `ffmpeg/video-use-pipeline-render-tung-doan-overlay-phu-de-cuoi`
7. **Snap điểm cắt vào ranh giới từ/khoảng lặng** + padding 30–200 ms; `validate` cảnh báo khi cắt giữa từ.
   Độ khó: trung bình. → `techniques/video-use-quy-tac-cat-theo-ranh-gioi-tu-va-khoang-lang`
8. **Bản đọc gọn `analysis/packed.md`** và lệnh `vedit timeline`. Độ khó: thấp. → `techniques/video-use-ai-doc-video-qua-transcript-va-anh-timeline`
9. **`project.md` cho từng dự án**, cộng một ghi chú gu người dùng lâu dài. Độ khó: thấp.
10. **Kiểm font fallback, easing cho `\move`, cảnh báo "parallel reveal".** Độ khó: thấp–trung bình. →
    `techniques/video-use-animation-overlay-easing-va-thoi-diem-payoff`
11. **Auto-correct màu từng clip** (port `grade.py`, giữ ghi chú MIT) chạy trước look sáng tạo. Độ khó: thấp. →
    `ffmpeg/video-use-chinh-mau-tu-dong-bang-signalstats-va-preset`
12. **Về lâu dài: overlay clip video có alpha** (PiP, animation dựng sẵn, "spotlight" bằng `\iclip`). Độ khó:
    trung bình. → `techniques/video-use-skill-manim-video-thiet-ke-chuyen-dong-giai-thich`
