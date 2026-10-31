---
title: Âm thanh cho video ngắn
category: audio
tags: [âm thanh, loudness, lufs, loudnorm, ducking, nhạc nền, khoảng lặng, micro-fade, asmr, bản quyền]
updated: 2026-10-31
sources:
  - https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026
  - https://openclip.app/learn/audio-normalization
  - https://opus.pro/blog/best-loudness-normalizers
  - https://sounddesign.irpr.agency/guides/how-to-mix-audio-for-youtube/
  - https://www.overseeros.com/blog/background-music-volume-under-voiceover
  - https://vidpros.com/fix-background-music-too-loud-video/
  - https://openclip.app/learn/audio-ducking
  - https://forum.shotcut.org/t/about-the-loudness-meter/11355
  - https://sparki.io/blog/how-to-edit-food-asmr-videos
  - https://sonilo.com/blog/guides/funny-sound-effects-for-videos
  - https://www.pippit.ai/blog/using-silence-in-video-editing
  - https://blog.frame.io/2017/05/08/edit-with-silence/
  - https://www.allaccess.com/consultant-tips/archive/36314/dead-air-is-good
  - https://www.finhay.com.vn/cach-lam-video-tiktok-len-xu-huong-bang-capcut
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/helpers/render.py
  - https://github.com/FFmpeg/FFmpeg/blob/release/6.1/doc/filters.texi
---
# Âm thanh cho video ngắn

## 1. Loudness
- **Không có thông số chính thức** của TikTok/Meta; một bảng so sánh mô tả chuẩn hoá của họ là "thích ứng". Mặc định
  an toàn: **−14 LUFS integrated, true peak ≤ −1 dBTP** (true peak là con số thống nhất nhất). Một số nguồn gợi ý bản
  to hơn −9 đến −12 LUFS cho TikTok/Reels — chưa kiểm chứng.
- YouTube hạ âm lượng bản upload to hơn mục tiêu → mix "nóng" chỉ mất dải động, không to hơn.
- `loudnorm` của ffmpeg: 1 lượt = chế độ **dynamic** (nén dải động). 2 lượt (đo trước, truyền `measured_*`) với
  `linear=true` chỉ nhân tuyến tính **khi** mức tăng không đẩy true peak vượt TP và LRA mục tiêu ≥ LRA nguồn; nếu
  không thì tự quay về dynamic. video-use chạy loudnorm 2 lượt −14 LUFS / −1 dBTP / LRA 11 ở bước cuối.

### Thế khó của ASMR (đo trên bản cà pháo, 2026-10-31)
Bản xuất không chuẩn hoá: −26,9 LUFS, true peak −2,25 dBTP, LRA 6,4 — tiếng nhấn (cạch, keng) gần đỉnh, nền rất nhỏ.
| Cách xử lý | Kết quả |
|---|---|
| loudnorm 2 lượt, `linear=true`, I = −16 / −20 / −24 | cả ba **quay về dynamic** (chỉ còn ~0,75 dB headroom); I=−16 ra −19,2 LUFS, LRA 6,4 → 4,4 (bị nén) |
| `highpass=f=80,afftdn=nr=12:nf=-42,volume=8dB,alimiter=limit=0.75:attack=2:release=60:level=disabled` | −22,1 LUFS, TP −1,4 dBTP; nền phòng −33,7 → −27,0 dB (+6,7); đỉnh "cạch" −3,9 → −2,5 dB; tương phản tiếng nhấn/nền 29,8 → 24,5 dB |
| Không xử lý | −27,5 LUFS, giữ nguyên tương phản nhưng nhỏ hơn video thường |

Không có chuẩn loudness riêng cho ASMR; chọn theo tai nghe và ghi rõ đánh đổi trong `notes`. `afftdn` ở mức vừa
chỉ giảm nền ~1 dB trên đoạn này — giảm ồn mạnh sẽ làm hỏng tiếng.

## 2. Nhạc dưới lời nói
- Khi có lời: nhạc thấp hơn giọng **15–20 dB** (có nguồn 18–24 dB cho thuyết minh; tài chính 20–26; cảm xúc 15–20);
  nâng nhạc lên ở khoảng nghỉ.
- ASMR: nếu dùng nhạc, chỉ thấp hơn tiếng "trigger" khoảng 4–6 dB (một nguồn) — hoặc không nhạc (nhiều kênh ASMR nấu
  ăn có bản "No Music").
- Nghe thử trên loa điện thoại và tai nghe rẻ trước khi đăng; ASMR thử thêm tai nghe tốt.

## 3. Âm thanh tại điểm cắt
- Fade 30 ms ở **mọi** biên đoạn (luật cứng của video-use) để không "tách"; hoặc cắt ở zero-crossing + crossfade ngắn.
  Đo bản cà pháo: 4/8 điểm cắt có bước nhảy biên độ gấp 1,9–3,8 lần mức lân cận.
- Room tone/ambience liên tục dưới các cú cắt (−45 đến −50 dB dưới lời thoại) giúp giấu chỗ nối; J/L-cut cho tiếng
  dẫn cảnh (xem `techniques/ky-thuat-cat-jump-cut-j-l-cut-match-cut-cat-theo-beat`).

## 4. Khoảng lặng có chủ đích
- Dọn nhạc bận rộn **trước** punchline để chữ/tiếng sau có chỗ "đáp"; setup → khoảng dừng → punchline; không nhét
  thêm tiếng hài vào khoảng dừng; phụ đề không lộ chữ cuối sớm.
- Đặt cho khoảng lặng một nhiệm vụ ("người xem nhìn gì lúc này?"). Quy ước sân khấu/phát thanh: dừng kịch tính 2–3 s.
- Công cụ tự cắt khoảng lặng đo âm lượng chứ không đo ý đồ → nghe lại, giữ khoảng lặng tạo chờ đợi.
- Cắt tiếng đột ngột (im bặt) cũng là một "hiệu ứng": dừng hình + im lặng, hoặc ngay trước tiếng giòn/tiếng nắp.

## 5. Nhạc trend & bản quyền
- Âm thanh trend giúp được đề xuất, nhưng tài khoản doanh nghiệp thường chỉ được dùng thư viện nhạc thương mại của
  nền tảng → có thể xuất **không nhạc** rồi chọn sound trong app. Một bài viết Việt Nam cho rằng trend TikTok thường
  chỉ kéo dài 1–3 ngày (chưa kiểm chứng) → dùng sớm.

## Áp dụng vào vedit
- Hiện có: `export.normalize_audio` = loudnorm 1 lượt I −14 / TP −1.5 / LRA 11; `AudioTrack.duck` = `sidechaincompress
  threshold=0.02 ratio=8 attack=20 release=400` (bus giọng gồm cả SFX nên SFX cũng ép nhạc); `volume`, `fade_in/out`
  cho track; `Clip.volume`/`mute`.
- Đề xuất: (1) micro-fade 10–30 ms mọi biên clip (dễ, ưu tiên cao); (2) `export.loudness_mode`: `social` (loudnorm
  2 lượt, linear khi được), `asmr` (EQ nhẹ + gain + alimiter, mục tiêu ~−20/−22 LUFS, giữ LRA), `off`;
  (3) `Clip.audio_lead/audio_tail` (J/L-cut); (4) track `role: "ambience"` lặp nền phòng dưới toàn video;
  (5) `AudioTrack.duck_amount_db` để chỉnh độ ép (ASMR 4–6 dB, lời nói 15–20 dB).
- Sound design nhiều lớp: xem `audio/sound-design-nhieu-lop-ambience-foley-whoosh-riser-impact`.
- Xem thêm: `audio/video-use-am-thanh-fade-30ms-sfx-dung-khung-loudnorm-2-luot`, `audio/claude-video-editor-am-thanh-fade-30ms-va-loudnorm-2-luot`.

_Ghi chú nguồn: trang ngoài GitHub đọc qua trích đoạn tìm kiếm; tài liệu loudnorm đọc trực tiếp (FFmpeg 6.1); số đo
do Agent 1 chạy trên `projects/20261030-video-01/renders/final.mp4`._
