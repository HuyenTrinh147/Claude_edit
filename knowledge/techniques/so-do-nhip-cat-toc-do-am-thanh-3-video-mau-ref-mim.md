---
title: Số đo nhịp cắt, tốc độ, âm thanh của 3 video mẫu ref-mim
category: techniques
tags: [nhip-cat, speed-ramp, am-thanh, loudness, tiktok, mau-3-video]
updated: 2026-11-10
sources:
  - người dùng tải lên: ref-mim-1..3 (TikTok dọc 576x1024, quan sát 2026-11)
---
# Số đo nhịp cắt, tốc độ, âm thanh của 3 video mẫu ref-mim

**Phạm vi và cảnh báo.** Mẫu chỉ có 3 video (12.3 / 12.7 / 13.1 s, ~29.2 fps, có tiếng, không có lời thoại nhận
diện được, không có transcript). Người dùng nói là kênh @editwithmim, nhưng watermark trong file ghi `@gmvisuals9029`
(video 1) và `@tmthntrung` (video 2, 3) — nên đây là clip TikTok của người khác (có thể là clip được kênh đó đăng lại /
dẫn); chưa xem được kênh thật (mạng chặn). Đừng suy ra "phong cách cả kênh" từ 3 clip này. Cuối mỗi file có **thẻ kết
TikTok** (nền tối, "Khám phá thêm các nhà sáng tạo…", ô tìm kiếm) dài 1.7–2.5 s, im lặng ~0.98 s: đó là phần do TikTok
gắn khi tải, KHÔNG phải do người dựng — đã loại ra khi tính số đo dưới đây.

## Nhịp cắt (đã loại thẻ kết)
| Video | Nội dung | Nội dung thật (s) | Số cảnh | ASL | Min–max | Ghi chú |
|---|---|---|---|---|---|---|
| ref-mim-1 | quán cà phê, ánh vàng ấm, đường cong tốc độ + keyframe CapCut chồng góc dưới | 9.78 | 8 | 1.22 s | 0.90–1.47 | rất đều (độ lệch ~0.2 s) |
| ref-mim-2 | chai trà trên bệ cửa sổ, quay màn hình app dựng rồi kết quả | 10.68 | 6 (phát hiện) | 1.78 s (trung vị 1.27) | 0.97–4.33 | cảnh 4.33 s thực chất là nhiều shot nối bằng whip/nhoè mà dò cảnh không bắt |
| ref-mim-3 | lon cola + chai nước xanh trên bàn, quay màn hình app → kết quả → gag cuối | 11.05 | 7 | 1.58 s | 0.98–2.97 | cảnh 2.97 s là quay màn hình |

- Mốc cắt thật: v1 = 0.98, 2.35, 3.35, 4.65, 6.11, 7.48, 8.88, 9.78; v2 = 1.05, 2.18, 3.98, 8.31, 9.71; v3 = 0.98,
  3.95, 5.05, 6.11, 8.35, 9.38.
- Quy tắc rút ra (3 mẫu): **cắt mỗi ~1.0–1.5 s**, cảnh dài hơn (2–3 s) chỉ khi người xem cần đọc giao diện/nhìn
  hiệu ứng. Cảnh đầu luôn ≈ 1.0 s (0.98 / 1.05 / 0.98): hook được "chốt" trong 1 s đầu.
- Cắt dạng: v1 toàn cắt theo chuyển động máy (đi xuyên quán, lia, vuốt) — cuối cảnh trước và đầu cảnh sau cùng
  hướng chuyển động, có nhoè mờ chuyển động (motion blur) ở rìa cắt (quan sát khung 8.85 s, 9.16 s ở v2). v2/v3 là
  jump-cut cùng một cảnh quay (cùng bàn/cửa sổ) đổi cỡ cảnh: toàn → cận (chai 5.18 s → 6.16 s ở v3).
- Chuyển cảnh: hầu như không có dissolve; chỉ cắt cứng + nhoè chuyển động/whip (v2 6.77 s, 9.16 s; v1 8.85 s).

## Tốc độ
- v1: ảnh chụp bảng đồ thị tốc độ chồng ở góc dưới cho thấy mỗi cảnh có đường cong riêng — dạng "chữ U" (chậm vào, nhanh giữa,
  chậm ra), "vòm" (nhanh vào – chậm ra) hoặc "hai gợn" — tức mỗi cảnh ~1.2 s có một cú ramp trong cảnh (speed
  ramp cong, không phải tăng tốc hằng số). Không đo được hệ số tốc độ chính xác, chỉ thấy hình đường cong.
- Hiệu ứng có thể quan sát nhưng chưa đo: cảnh trôi mượt như gimbal đi xuyên quán ở 1.9–2.7 s.

## Âm thanh (đo bằng ffmpeg ebur128, numpy)
| Video | Loudness tích hợp | LRA | Peak | Ghi chú |
|---|---|---|---|---|
| ref-mim-1 | -9.7 LUFS | 2.8 LU | ~0 dBFS | nhạc có xung đều (~1.3–1.4 s/lần), 2 điểm cắt (0.98, 3.35) trùng onset ±0.06 s, còn lại không |
| ref-mim-2 | -5.1 LUFS | 1.5 LU | 0 dBFS | rất to và bị nén; chỉ 3 onset rõ, cắt không bám onset |
| ref-mim-3 | -12.3 LUFS | 3.5 LU | ~0 dBFS | onset đều ~0.54 s (≈ 111 BPM); 5/6 điểm cắt nằm trong ±0.08 s của lưới này |

- Cả 3 clip to hơn chuẩn của vedit (loudnorm thường nhắm ~-14 LUFS): -5…-12 LUFS. Nghe "to sát trần", ít dao động
  (LRA 1.5–3.5). TikTok chuẩn hoá nên không có lợi thế thật, chỉ là cảm giác "đậm".
- Không phát hiện tiếng nói rõ ràng bằng số; không bịa lời. Âm thanh là nhạc/beat + tiếng động; bộ dò onset tự động
  là chỉ dấu, không phải bằng chứng "SFX tại điểm cắt".
- Im lặng cuối ~0.98 s ở cả 3 = thẻ kết TikTok, không phải thiết kế.

## Áp dụng vào vedit
- Đã có: cắt theo giây (`Clip.start/end`), `speed` hằng số, `transition` (`hblur`, `slideleft`…), `motion` punch/shake,
  `loudnorm`, nhạc nền tạo bằng code (`vedit music`).
- Thiếu: **speed ramp cong trong một clip** (chỉ có `Clip.speed` hằng số). Cách vòng: tách clip thành 3 đoạn
  speed 0.6 / 1.6 / 0.6 (xem skill `edit-toc-do-cong-chu-u`); đề xuất thêm trường `speed_curve`.
- Thiếu: motion blur theo hướng chuyển động ở điểm cắt (có `hblur` ngang, chưa có blur dọc/hướng).
- Thiếu: căn điểm cắt vào lưới beat của nhạc ngoài (có thể tính từ onset bằng `vedit analyze`).
- Ưu tiên: (1) lưới nhịp 1.0–1.5 s + cảnh mở ≤ 1 s; (2) speed_curve; (3) công cụ bắt nhịp từ nhạc nguồn.
