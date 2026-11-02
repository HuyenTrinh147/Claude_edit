---
title: Bộ công cụ đồ hoạ & hiệu ứng của vedit
category: techniques
tags: [vedit, đồ hoạ, motion graphics, animation, callout, sfx, look, editplan]
updated: 2026-10-30
sources:
  - (tài liệu nội bộ vedit — đã kiểm chứng bằng render thật)
---
# Bộ công cụ đồ hoạ & hiệu ứng của vedit

**Đây là bảng tra cứu, KHÔNG phải danh sách bắt buộc** — chọn phong cách trước, rồi chỉ lấy những công cụ hợp phong cách đó (xem `techniques/tu-duy-dung-sang-tao-cho-video-ngan`).

Tra cứu nhanh mọi thứ EditPlan làm được ngoài cắt ghép. Toạ độ `x`, `y` là tỉ lệ khung (0..1) — đọc bằng
`vedit frame <dự án> <giây> --grid` (khung hình có lưới 10% kèm nhãn). Thời gian = giây TIMELINE.

## Chữ động (`texts`)
| Trường | Giá trị |
|---|---|
| `animation` | `pop`, `bounce` (nảy, hợp hook), `typewriter` (gõ từng chữ), `word_pop` (bật từng từ), `slide_up`, `slide_left`, `blur_in`, `wipe` (quét lộ dần), `fade`, `none` |
| `shape` | `pill` (viên bo tròn kiểu sticker), `banner` (băng chữ nhật nghiêng nhẹ), `none` |
| `shape_color`, `shape_opacity` | nền sticker; chữ trên nền tự bỏ viền |
| `x`, `y`, `rotation` | đặt tự do + nghiêng (−30..30°) kiểu sticker |
| `font` | `Be Vietnam Pro` (hiện đại), `Mali` (viết tay dễ thương), `Pacifico` (thư pháp, dùng ít), `Inter` |

`size` đã chuẩn hoá giữa các font (cùng size ≈ cùng độ lớn). Chữ quá dài tự thu nhỏ cho vừa khung.

```json
{"text": "Muối hũ cà pháo", "start": 0, "end": 2.2, "y": 0.18, "size": 92, "font": "Mali",
 "color": "#3A2A1A", "shape": "pill", "shape_color": "#FFF4D6", "animation": "bounce", "rotation": -3}
```

## Đồ hoạ (`graphics`)
| `type` | Dùng khi | Trường chính |
|---|---|---|
| `callout` | gọi tên nguyên liệu / chi tiết, có chấm + đường chỉ vào vật | `x,y` = điểm vật; `label_x,label_y` = nhãn; `text` |
| `badge` | đánh số bước quy trình | `text` = số; `label` = tên bước; `x,y` = tâm huy hiệu |
| `progress_bar` | video quy trình/listicle — giữ người xem tới cuối | `y` (0 = mép trên), `thickness`, `accent_color` |
| `highlight` | vòng tròn nhấn vào vật, nhịp đập nhẹ | `x,y,radius` |
| `sparkles` | khoảnh khắc "wow": thành phẩm, món đẹp | `x,y,radius,count,size,color` |
| `flash` | chớp sáng 0.1–0.25s ở điểm chuyển lớn / beat | `color` |

Màu: `color` (nền nhãn/huy hiệu), `text_color`, `accent_color` (chấm, đường, nền huy hiệu, thanh tiến trình).

```json
{"type": "callout", "start": 6.1, "end": 7.6, "x": 0.52, "y": 0.47, "label_x": 0.75, "label_y": 0.33,
 "text": "ớt tươi", "accent_color": "#E8432E"}
{"type": "badge", "start": 3.0, "end": 4.6, "x": 0.14, "y": 0.15, "text": "1", "label": "Pha nước muối"}
```

## Chuyển động máy (`motion`) — khớp với tiếng động / beat
- `{"type": "punch", "start": 1.65, "duration": 0.3, "amount": 0.08}` — zoom giật vào rồi nhả (0.05–0.15).
- `{"type": "shake", "start": 13.6, "duration": 0.3, "amount": 0.01}` — rung khi có va chạm (0.005–0.03).

## Màu (`look`)
`{"preset": "warm_food", "vignette": 0.3, "grain": 0.15}` — preset: `warm_food` (đồ ăn), `bright_clean`
(sạch, sáng), `film` (hoài cổ), `moody`, `vivid`, `bw`.

## Âm thanh hiệu ứng tổng hợp (không cần file)
`{"path": "sfx:pop", "role": "sfx", "start": 2.0, "volume": 0.35}` — `pop` (chữ/đồ hoạ bật ra), `click`,
`ding` (thành phẩm, ý chính), `sparkle` (lấp lánh), `whoosh` (chuyển cảnh, chữ trượt), `thud` (va chạm nặng),
`rise` (dồn nén trước điểm nhấn). Video ASMR: volume 0.15–0.35 để không át tiếng thật.
**SFX thật từ thư viện** (bộ người dùng đưa vào): `vedit sfx add <thư mục | .zip | link Drive> --name <tên bộ>` rồi
`vedit sfx list <từ khoá>` (hoặc `--category whoosh|impact|riser|pop|click|ding|magic|glitch|camera|cash|fail|funny|crowd|game`)
→ đường dẫn file + `đỉnh tiếng @x s`. Đặt `audio.start = mốc khung hình − x` để đỉnh tiếng rơi đúng khung. Ưu tiên SFX
thật khi hợp phong cách (whoosh, impact, riser nghe "đắt" hơn bản tổng hợp); file thật không có thì dùng `sfx:<tên>`.
Âm 8-bit cho phong cách game: `pickup`, `coin`, `lock`, `combo`, `levelup`, `slash`, `zip`, `tick`, `complete`, `buzz`.
`pitch` (nửa cung, −24..24) đổi cao độ — chuỗi combo cao dần 0, 2, 4.

## Nhạc nền tạo bằng code (`vedit music`)
`vedit music <dự án> --duration <giây>` sinh nhạc nền hộp nhạc / kalimba (không file, không bản quyền) vào
`<dự án>/audio/bed-pastel.wav`; dùng như `audio` role `music`, volume ~0.075 (−41 LUFS, dưới tiếng thật), `duck: false`.

## Giao diện game & bám vật (`hud`, `vedit track`)
Khung kính VR, khung ngắm bám vật, bảng nhiệm vụ tick dần, thanh đo có vùng chuẩn, số chạy / đồng hồ đếm lùi, chữ thưởng
PERFECT!, túi đồ (vật phẩm pixel-art cắt từ chính video), thẻ ★★★, nút tay cầm VR, icon, vệt chém — xem
`techniques/giao-dien-game-hud-bam-vat-cho-video`.

## Dừng hình (`Clip.freeze`)
`"freeze": 1.0` giữ khung cuối của clip thêm 1 giây (tiếng gốc im) — chỗ cho thẻ kết / khoảnh khắc "PAUSE".
