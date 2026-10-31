---
title: video-use: Âm thanh, fade 30ms, SFX đúng khung, loudnorm 2 lượt
category: audio
tags: [video-use, âm thanh, afade, sfx, ducking, loudnorm, ebur128, lufs, true peak, asmr, đo lường]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/helpers/render.py
  - https://github.com/browser-use/video-use/blob/main/helpers/transcribe.py
---
# video-use: Âm thanh, fade 30ms, SFX đúng khung, loudnorm 2 lượt

SKILL.md mở đầu phần này bằng câu: "Sound is where generated videos sound cheap."

## Quy tắc từ video-use
1. **Fade 30 ms ở mọi mép đoạn** (Hard Rule 3):
   `afade=t=in:st=0:d=0.03,afade=t=out:st={dur-0.03}:d=0.03`. Thiếu bước này thì nghe tiếng "tách" ở mỗi điểm cắt.
2. **Ít hiệu ứng hơn.** Mỗi SFX gắn với một thứ nhìn thấy được: một cú cắt, một lần đáp, một cú click.
   "~20 stock whooshes/risers/impacts in 18s reads as generic; ~8 reads as designed." Anti-pattern: "Stock SFX on
   every transition."
3. **Đánh đúng khung hình.** Phần lớn SFX có attack, tức đoạn lặng hoặc đoạn dồn trước transient. Đo attack
   ("first sample above ~-30 dBFS of the peak"), rồi đặt file **sớm hơn `attack` giây** so với khung chạm.
4. **Duck nhạc dưới giọng nói** khoảng −12 đến −15 dB so với lúc chỉ có nhạc. Trước stinger hoặc end card, kéo
   nhạc ra hẳn chứ đừng để đuôi nhạc tự tắt dưới CTA.
5. **Master một lần:** trộn ra PCM, rồi chạy loudnorm 2 lượt (−14 LUFS, true peak ≤ −1 dBTP) trên bản trộn cuối.
6. **Đo, đừng đoán.** Đo `ebur128` (integrated + true peak) và RMS từng đoạn (thoại, chỉ nhạc, end card).
   "An end card 15 dB under the dialogue, or effects louder than speech, is a bug." "**You cannot listen: say so,
   and report the numbers.**"
7. **Gu nhạc là của người dùng.** Nhạc AI tạo thường mặc định "hype". Đưa 2 nền nhạc tương phản cho người dùng
   nghe rồi chọn.
8. **Trước khi gửi đi transcribe:** track có đỉnh dưới −60 dBFS coi là câm, không upload. Với file nhiều track
   (OBS: 0 = game, 1 = mic) phải chọn đúng track.

## Lệnh đo (đã chạy thử, ffmpeg 6.1)
```bash
# integrated loudness, LRA, true peak
ffmpeg -hide_banner -nostats -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -A14 "Summary:"
# RMS + peak của một đoạn (ví dụ hook 0–1.4 s)
ffmpeg -hide_banner -nostats -ss 0 -t 1.4 -i final.mp4 \
  -af astats=measure_perchannel=none:measure_overall=RMS_level+Peak_level -f null - 2>&1 | grep -E "RMS level|Peak level"
```

## Số đo thật trên bản dựng gần nhất của vedit
Dự án `20261030-video-01`, file `renders/final.mp4`, đo ngày 2026-10-31. Plan đặt `export.normalize_audio: false`.

**Toàn bài:** I = **−27.5 LUFS**, LRA 6.6 LU, true peak −2.2 dBFS. Như vậy thấp hơn 13.5 LU so với mức −14 LUFS
mà chính schema của vedit mô tả là "chuẩn TikTok/YouTube".

**Theo đoạn:**
| Đoạn | RMS | Peak |
|---|---|---|
| Hook 0–1.4 s | −34.1 dB | −17.2 dB |
| End card 14.3–15.8 s | −24.3 dB | −5.8 dB |

Hook, phần quan trọng nhất, nhỏ hơn đoạn kết **khoảng 10 dB**. Theo chuẩn của video-use, đây là chỗ phải quyết
định có chủ đích, không để mặc.

**Thử loudnorm trên chính file này.** Lượt đo ra `input_i −26.91`, `input_tp −2.25`, `LRA 6.40`.
| Cách | Kiểu loudnorm thực chạy | I đo lại (ebur128) | TP đo lại |
|---|---|---|---|
| 1 lượt (dynamic) | dynamic | −17.8 LUFS | −0.3 dBFS |
| 2 lượt, `linear=true`, mục tiêu −14 | **tự lùi về dynamic** | −15.0 LUFS | −0.0 dBFS (loudnorm tự báo −1.00) |
| 2 lượt, mục tiêu −20 | vẫn lùi về dynamic | — | — |

**Bài học:**
- **Chế độ linear chỉ dùng được khi PLR cho phép.** Mục tiêu linear tối đa
  = `measured_I + (TP_target − measured_TP)` = −26.91 + (−1 + 2.25) ≈ **−25.7 LUFS**. Footage ASMR có tiếng va
  chạm đỉnh cao ("cạch", "keng") thì muốn đạt −14 LUFS bắt buộc phải nén hoặc limit. Có 3 lựa chọn, đều phải có
  chủ đích:
  - (a) chấp nhận mức thấp hơn;
  - (b) dùng `acompressor`/`alimiter` trước loudnorm;
  - (c) dùng dynamic rồi đo lại.
- **Số loudnorm tự báo khác với số đo lại.** loudnorm báo TP −1.00, nhưng đo lại trên file 48 kHz ra −0.0 dBFS.
  Vì vậy luôn đo lại trên file xuất, chừa biên TP (−1.5 đến −2), và nếu cần thì thêm `alimiter` ở cuối chuỗi.

## Attack của SFX tổng hợp trong vedit (đo ngày 2026-10-31)
Đo bằng envelope RMS 5 ms trên đúng biểu thức `aevalsrc`/`anoisesrc` trong `vedit/render.py`:
| SFX | Dài | Bắt đầu nghe được (−30 dB so với đỉnh) | Đỉnh | Đặt `start` = |
|---|---|---|---|---|
| `pop` | 0.20 s | 0 ms | 3 ms | thời điểm sự kiện |
| `click` | 0.06 s | 0 ms | 2.5 ms | thời điểm sự kiện |
| `ding` | 1.30 s | 0 ms | 3 ms | thời điểm sự kiện |
| `thud` | 0.40 s | 0 ms | 3.6 ms | thời điểm va chạm |
| `sparkle` | 0.90 s | 0 ms | 163 ms (4 nốt ở 0/80/160/240 ms) | sự kiện, hoặc sớm 0.16 s nếu muốn nốt mạnh nhất trùng khung |
| `whoosh` | 0.60 s | 246 ms | **368 ms** | điểm cắt **− 0.37 s** |
| `rise` | 1.00 s | 28 ms | **897 ms** | điểm nhấn **− 0.9 s** |

Plan gần nhất đã làm đúng với `whoosh`. Đặt ở 1.05 s thì đỉnh rơi vào khoảng 1.42 s, khớp cú cắt 1.40 s; đặt ở
8.75 s thì đỉnh khoảng 9.12 s, khớp cú cắt 9.10 s. Tuy vậy, cách làm này mới là kinh nghiệm của agent, chưa thành
quy tắc trong hệ thống.

## Áp dụng vào vedit
**Đã có:**
- Bus giọng/SFX và bus nhạc, ducking `sidechaincompress` (threshold 0.02, ratio 8, attack 20, release 400).
- `fade_in`/`fade_out` cho track nhạc.
- 7 SFX tổng hợp.
- loudnorm 1 lượt (−14 / −1.5 / 11), tắt được bằng `normalize_audio`.

**Còn thiếu:**
- Không fade ở chỗ cắt thẳng.
- Không đo lại sau render, kể cả theo đoạn.
- Không có loudnorm 2 lượt hay limiter.
- Không giới hạn số SFX. Plan gần nhất có 10 SFX trong 15.8 s, gồm 6 `pop` giống hệt nhau cho mỗi badge.
- Không tự cân mức giữa các clip. Agent phải chỉnh tay `volume` khi nền nhảy +6.5–6.6 dB giữa hai clip kề nhau.
- Chưa biết mức duck thực tế tính bằng dB.

**Đề xuất (ưu tiên giảm dần):**
1. **Fade 30 ms ở mọi cắt thẳng** trong `render.py` — độ khó thấp. Code mẫu ở
   `ffmpeg/video-use-pipeline-render-tung-doan-overlay-phu-de-cuoi`.
2. **Đo sau render** — độ khó thấp. Sau mỗi render, hoặc trong `vedit qa`, in I/TP/LRA và RMS từng clip. Gắn cờ
   khi có một trong các điều kiện:
   - TP > −1 dBFS;
   - hai clip kề nhau chênh RMS > 6 dB (ngưỡng đề xuất, cần chỉnh);
   - hook nhỏ hơn phần còn lại;
   - SFX to hơn tiếng chính.

   Agent 3 phải báo con số cho người dùng.
3. **Loudnorm 2 lượt + `alimiter`** — độ khó trung bình. Mục tiêu theo thể loại, quyết định có chủ đích và ghi
   vào `notes`. Ví dụ ASMR có thể giữ dải động và đặt mục tiêu thấp hơn −14 LUFS, nhưng phải là con số đã chọn,
   không phải kết quả của việc tắt chuẩn hoá. Kiểm tra công thức PLR trước khi chọn `linear`.
4. **`AudioTrack.align: "start" | "peak"`** — độ khó thấp. Renderer tự trừ đi thời gian tới đỉnh theo bảng trên,
   để agent chỉ cần ghi đúng thời điểm sự kiện.
5. **Ngân sách SFX trong prompt và validate** — độ khó thấp. Khoảng ≤ 1 SFX mỗi 2 giây, tính từ con số
   "~8 / 18 s" của video-use. Không lặp cùng một SFX cho mọi đồ hoạ cùng loại. Mỗi SFX phải gắn với một sự kiện
   nhìn thấy được.
6. **Tự cân mức giữa các clip** — độ khó trung bình. Đo RMS mỗi clip nguồn trong `analyze`, đề xuất `volume` để
   chênh lệch giữa hai clip kề nhau không quá vài dB.
7. **Đo mức duck thật** — độ khó thấp. Render thử một đoạn có giọng + nhạc rồi so RMS nền nhạc, chỉnh tham số
   `sidechaincompress` để đạt −12 đến −15 dB.
