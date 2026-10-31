---
title: claude-video-editor: Âm thanh, fade 30ms và loudnorm 2 lượt
category: audio
tags: [claude-video-editor, âm thanh, afade, tiếng bụp, loudnorm, lufs, mix, sfx, audio-reactive, tts, elevenlabs v3]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/helpers/render.py
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/MOTION_PHILOSOPHY.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/references/interview-questions.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/audio-reactive.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/dynamic-techniques.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/gsap/scripts/extract-audio-data.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/gsap/references/effects.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/generate-footage/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/generate-footage/scripts/tts_v3.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/tts.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/transcript-guide.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-4-storyboard.md
  - https://github.com/assafkip/claude-video-editor/blob/master/recipes/04-animate-stills.md
---
# claude-video-editor: Âm thanh, fade 30ms và loudnorm 2 lượt

## 1. Fade 30ms ở mọi biên cắt (Hard Rule 3)

"30ms audio fades at every segment boundary … Otherwise audible pops at every cut." Mỗi đoạn được cắt ra kèm:

```bash
-af "afade=t=in:st=0:d=0.03,afade=t=out:st={dur-0.03}:d=0.03"
```

Self-eval còn soi **gai sóng âm ở biên** trên bản render để bắt tiếng bụp lọt qua. Cùng nhóm luật: không cắt giữa từ,
đệm 30–200ms, chừa 400–600ms khi đổi người nói, kéo qua tiếng cười/vỗ tay — "Never reason audio and video
independently."

## 2. Loudness: −14 LUFS / −1 dBTP / LRA 11, đo 2 lượt

`render.py` ghi chú đây là mục tiêu chuẩn hoá của YouTube / Instagram / TikTok / X / LinkedIn (theo repo).

1. **Lượt đo**: `ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -vn -f null -` → lấy khối `{…}`
   **cuối cùng** trong stderr: `input_i`, `input_tp`, `input_lra`, `input_thresh`, `target_offset`.
2. **Lượt áp**: `loudnorm=I=-14:TP=-1:LRA=11:measured_I=…:measured_TP=…:measured_LRA=…:measured_thresh=…:offset=…:linear=true`
   với `-c:v copy -c:a aac -b:a 192k -ar 48000` (không mã hoá lại hình).
3. Preview/draft dùng 1 lượt cho nhanh; đo hỏng → rơi về 1 lượt. Nguồn không có tiếng thật → `--no-loudnorm`.

Lý do (nhận định, kiến thức nền về filter `loudnorm`): chế độ 1 lượt là **dynamic** — có thể "bơm" âm lượng; 2 lượt
với `linear=true` chỉ dịch mức tuyến tính khi đủ điều kiện, giữ nguyên dải động.

## 3. Mức mix mặc định

| Lớp | Mức | Ghi chú |
|---|---|---|
| Giọng đọc / lời thoại | 1.0 | chính, dẫn nhịp |
| Pad nền ấm (underscore) | 0.15 | "barely there" — thường là lựa chọn đúng |
| SFX (click, lấp lánh, whoosh) | 0.2 | đuôi tiếng được tràn sang beat sau |
| Music bed (promo thường) | 0.4 | |
| Nhạc dẫn dắt (edit theo nhạc) | 0.8 | |

"Music-free is a valid choice; pad-only is premium; full 'music' cue is last resort." SFX gợi ý trong storyboard rất cụ
thể và dùng cả **khoảng lặng**: "faint low drone. On fold: drone cuts. Silence. Then a single clean chime."
QA: `volumedetect` — lời thuyết minh kiểu tài liệu có mean ~ −26 dB.

## 4. Hình phản ứng theo âm thanh

Trích dữ liệu trước (xác định, không phân tích lúc render): `extract-audio-data.py` giải mã mono 44.1 kHz, cửa sổ FFT
**4096** mẫu (Hann, ~10.8 Hz/bin) đặt giữa mỗi khung hình, chia **dải log 30 Hz–16 kHz** (mặc định 16 dải), lấy biên
độ đỉnh mỗi dải, **chuẩn hoá riêng từng dải** (để treble không bị bass lấn); `rms` từng khung chuẩn hoá theo đỉnh cả bài.

| Tín hiệu | Thuộc tính hình | Hiệu ứng |
|---|---|---|
| Bass (dải 0–1) | scale | đập theo beat |
| Treble (dải cao) | glow / text-shadow | độ sáng viền |
| Biên độ tổng | opacity, y, màu nền | thở, nâng, đổi màu |
| Trung (dải giữa) | bo góc, độ rộng | biến hình |

Biên độ: **chữ 3–6%** (to hơn sẽ khó đọc), nền/hình khối 10–30%. Làm mượt `prev*s + raw*(1−s)` với s 0.1–0.2 (gắt)
đến 0.3–0.5 (mềm). "Content, not medium": **không** thêm thanh EQ, phổ, hiển thị waveform, nốt nhạc clip-art, hạt chung
chung, đổi màu cầu vồng, chớp trắng theo beat, quả cầu phát sáng. Với nội dung là nhạc, phụ đề phản ứng âm thanh là
**bắt buộc** (nhóm lời to vào khung mạnh hơn, glow hơn).

## 5. Giọng đọc tạo bằng AI

- **Giọng trước, hình sau**: tốc độ đọc v3 không xác định — "a 120s estimate can come out 100s or 166s" — nên dựng hình
  trước luôn phải canh lại.
- ElevenLabs `eleven_v3` + audio tag trong kịch bản: `[excited]`, `[whispers]`, `[softly]`, `[dramatic tone]`,
  `[warmly]`, `[shouts]`. Stability 0.0 = Creative, 0.5 = Natural, 1.0 = Robust; "A 'flat' read is fixed by lowering
  stability and re-tagging the script, not by louder words." Đòn bẩy: VIẾT HOA từ mạnh, `...` để ngừng, hạ xuống
  `[whispers]` ngay trước câu lớn. Thử 2–3 giọng với câu đầu ("The first voice is never the pick"). v3 có thể đọc
  chệch chữ → transcribe và đọc lại, sai câu quan trọng thì tạo lại.
- Kokoro-82M (chạy CPU, không cần key, 54 giọng/8 ngôn ngữ qua `npx hyperframes tts`): tốc độ 0.7–0.8 cho hướng dẫn,
  1.0 tự nhiên, 1.1–1.2 cho intro; ≥ 1.5 hiếm khi hợp. (Repo không nói gì về tiếng Việt.)
- Phiên âm bài hát: model nhỏ đoán sai lời; > 20% token `♪` hoặc chữ vô nghĩa = thất bại → model lớn hơn hoặc nhập lời
  thủ công.

## Áp dụng vào vedit

**Đã có**: mix 2 bus (giọng+SFX / nhạc), `sidechaincompress` ducking (threshold 0.02, ratio 8, attack 20, release 400),
`loudnorm=I=-14:TP=-1.5:LRA=11` một lượt trong graph, fade in/out cho track nhạc, `acrossfade` ở transition, SFX tổng
hợp bằng `aevalsrc`/`anoisesrc`.

**Còn thiếu**: **không có fade ở biên cắt cứng** (các clip được `concat` thẳng → nguy cơ tiếng bụp ở mỗi jump cut);
loudnorm 1 lượt (dynamic); không có dữ liệu beat/onset để khớp punch, cắt, chữ với nhạc/tiếng động; `whoosh` dùng seed
ngẫu nhiên.

**Đề xuất (ưu tiên)**:
1. **Fade 30ms** vào chuỗi audio mỗi clip trong `render.py` (`afade=t=in:d=0.03`, `afade=t=out:st=<dur−0.03>:d=0.03`
   trước `apad`), bỏ qua phía có transition (đã có `acrossfade`). Dễ.
2. **Loudnorm 2 lượt cho bản final**: render → đo → mux lại audio với `linear=true` và `-c:v copy` (rẻ, chỉ xử lý âm);
   preview giữ 1 lượt. Dễ.
3. **`vedit beats <file|slug>`**: liệt kê mốc đỉnh năng lượng/onset (ffmpeg `astats` theo khung hoặc FFT như mục 4) cho
   nhạc và tiếng động thật — Agent đặt punch/cắt/pop chữ đúng beat. Vừa.
4. Mức mặc định SFX ~0.2 tương đối so với lời; gợi ý "pad 0.15" khi video cần không khí nhưng không muốn nhạc lấn. Dễ.
5. Nhạc/beat → hoạt ảnh "pulse" (phóng 3–6%) cho chữ tiêu đề tại các mốc beat (sinh `\t` ngắn ở mỗi mốc) — phiên bản
   libass của audio-reactive. Vừa.
