---
title: Giao diện game (HUD) bám vật thật — biến video thành màn chơi
category: techniques
tags: [vedit, hud, game, vr, ar, tracking, bám vật, reticle, combo, chiptune, freeze frame, editplan]
updated: 2026-10-31
sources:
  - (tài liệu nội bộ vedit — đã kiểm chứng bằng render thật trên video cà pháo)
---
# Giao diện game (HUD) bám vật thật — biến video thành màn chơi

Dùng khi hướng dựng là "video như đang chơi game" (game nấu ăn VR/AR, nhiệm vụ, mini-game). Đây là **bộ đồ nghề của một
phong cách**, không phải hiệu ứng rải vào mọi video. Mỗi đồ hoạ phải là **một luật chơi gắn với một hành động thật + một
tiếng thật** (rót nước → thanh đo đầy; cắt ớt đúng nhịp → PERFECT CUT!; thả cà → COMBO ×3; đậy nắp → SEAL).

## 0. Phong cách giao diện — `hud_theme`
`"hud_theme": "neon"` (mặc định): viền mảnh phát sáng trên kính tối, sci-fi; font Chakra Petch + Bungee.
`"hud_theme": "pastel"`: **tươi tắn, dễ thương** — thẻ kem pha tông màu của từng mục, viền + bóng tím than kiểu sticker,
kẹo hồng / mint / lavender / vàng bơ / xanh trời, font tròn **Baloo 2** (HUD) + **Paytone One** (chữ thưởng). Người dùng
(2026-11-02) thích pastel hơn neon cho đồ hoạ.
- Màu `color` / `accent_color` / `text_color` của từng mục **bỏ trống = mặc định của theme** (neon: cyan / vàng / trắng;
  pastel: xanh trời / vàng bơ / tím than). Đặt `color` khác nhau theo vai để thẻ có tông riêng: điểm = vàng bơ
  `#FFD66E`, combo = hồng `#FF9DBA`, nhiệm vụ / kính = lavender `#C9B3FF`, đồng hồ = mint `#8DE4B2`, thẻ qua màn = hồng.
- Bảng màu pastel: xanh trời `#8CCBFF`, vàng bơ `#FFD66E`, mint `#8DE4B2`, hồng dâu `#FF8FAE`/`#FF9DBA`, lavender `#C9B3FF`,
  đào `#FFB07A`; kem `#FFF8EE`; mực tím than `#4E3A68`.
- Pastel mờ trên nền sáng → chữ HUD luôn màu mực có viền kem, đường mảnh đổi sang mực, khung ngắm có viền mực. Font
  Baloo 2 / Paytone One **không có** ký hiệu ▶ ★ ✓ (dùng » × · thay) — `vedit validate` báo nếu thiếu glyph.

## 1. Bám vật (tracking) — `vedit track`
```
vedit frame <dự án> <giây nguồn> --grid          # đo hộp quanh vật: x,y (góc trên-trái), w,h theo tỉ lệ 0..1
vedit track <dự án> <tên> --at <giây nguồn> --box x,y,w,h [--until <giây>] [--back <giây>]
vedit track <dự án>                               # liệt kê track đã có
```
- Lưu `analysis/tracks/<tên>.json` (toạ độ NGUỒN 0..1, đã làm mượt) + ảnh kiểm tra `<tên>_sheet.jpg` (khung xanh = bám,
  đỏ = mất dấu) — **luôn Read ảnh này** trước khi dùng.
- Tự dừng ở điểm cắt cảnh (báo "dừng ở điểm cắt cảnh"). Mỗi cảnh một track.
- Chọn vật có hoa văn/tương phản (hũ có cà, quả ớt đỏ, bàn tay) — mặt phẳng trơn một màu thì không bám được.
- Hộp nên bao sát phần vật đặc trưng; vật quá to (chiếm cả khung) thì khung ngắm sẽ bị kẹp vào mép.
- ~6 khung/giây trên CPU: track đúng đoạn cần, đừng track cả video.

## 2. Bám vào HUD — `anchor`
Mọi mục trong `hud` có thể đặt cố định (`x`, `y` tỉ lệ khung) **hoặc** bám vật:
```json
"anchor": {"track": "ot", "point": "top", "dx": 0, "dy": -0.03, "lag": 0}
```
`point`: center, top, bottom, left, right, top_left, top_right, bottom_left, bottom_right (điểm trên hộp bám).
`lag` 0.3–0.6 = UI trôi theo mềm như hologram. Vị trí đã tính cả crop/fit, zoom chậm và punch/shake của khung hình.
Mục bám vật tự né mép khung; khi cảnh không còn chiếu video của track thì tự ẩn (`vedit validate` báo nếu mốc giây
của mục vượt ra ngoài đoạn đã track hoặc rơi vào cảnh khác).

## 3. Bộ HUD (`hud`, mốc giây TIMELINE)
Chung: `start`, `end`, `x`, `y` | `anchor`, `enter` (pop, slide, stamp, fade, none), `exit`, `color` (neon chính, mặc
định #3CF2FF), `accent_color` (thưởng/tick/khoá, #FFD23F), `text_color`, `size` (cỡ chữ chính), `font`.
Font mặc định: **Chakra Petch** (chữ HUD công nghệ), **Bungee** (chữ thưởng của popup và tiêu đề card). Cả hai đều có
tiếng Việt. Chữ HUD tự có quầng tối nên đọc được trên nền sáng.

| `type` | Vai trò trong "game" | Trường riêng |
|---|---|---|
| `visor` | khung kính VR toàn màn hình: 4 góc, thanh tên màn chơi, REC nhấp nháy, đồng hồ T+ | `text`, `rec`, `clock`, `scanlines`, `margin` |
| `reticle` | khung ngắm 4 góc bám vật: dò (xoay, vạch quét) → khoá (đổi accent, chớp) | `text` (nhãn tab), `sub`, `lock_at`, `pad`, `w`,`h` (khi không bám) |
| `panel` | bảng nhiệm vụ / công thức: tiêu đề + ô tick, tick theo mốc giây | `text`, `items[]`, `checks[]` (giây hoặc null), `width` |
| `meter` | thanh đo có vùng chuẩn: rót nước tới vạch (fill) / canh thời điểm (needle) | `keys[{t,v,ease}]` (v 0..1), `zone[lo,hi]`, `style`, `orientation`, `length`, `thickness` |
| `counter` | số chạy: điểm, combo, đồng hồ đếm lùi | `keys[]`, `format` int/timer/combo/percent, `text` (nhãn), `prefix`, `suffix`, `box` |
| `popup` | chữ thưởng đập xuống + tia sáng: PERFECT!, +50, COMBO ×3 | `text`, `sub`, `rise`, `burst`, `tilt`, `shadow_color` (mặc định vào stamp, ra pop) |
| `slots` | túi đồ N ô, vật phẩm bay từ vật thật vào ô theo đường cong | `count`, `items[]`, `icons[]`, `times[]` (giây chạm ô), `sources[]` (anchor từng món), `fly`, `slot_size` |
| `card` | thẻ hoàn thành: tiêu đề, 0–3 sao đập vào lần lượt, dòng phụ | `text`, `stars`, `star_delay`, `star_gap`, `items[]`, `width` |
| `prompt` | nút tay cầm VR "A" + hành động, vòng giữ-nút chạy đầy | `button`, `text`, `hold[from,to]`, `blink` |
| `icon` | icon vector: star, check, lock, coin, heart, hand, clock, drop, bolt, flame — hoặc `sprite` cắt từ video | `icon` hoặc `sprite`, `spin` |
| `slash` | vệt chém sáng quét qua điểm cắt (~0,3 s) rồi vỡ thành mảnh — PERFECT CUT | `angle` (0 = ngang, dương = chéo lên), `length`, `thickness`, `particles`, `color` (lõi), `accent_color` (quầng) |

**Vật phẩm cắt từ chính video (`sprite`)**: `{"t": <giây NGUỒN>, "box": [x, y, w, h], "pixels": 16, "colors": 10}`
→ khung hình tại `t` được cắt theo hộp, thu về vài chục pixel và vài màu thành **pixel-art 8-bit** (bo góc như ô vật
phẩm). Dùng trong `slots.sprites[i]` (thay icon từng món — cục muối, hạt đường thật), `card.sprite` (món thành phẩm phía
trên hàng sao), `icon.sprite`. Hộp bao sát vật; `pixels` 12–16 cho vật nhỏ, 20–24 cho món trên thẻ.

`keys` = giá trị theo thời gian: `{"t": 3.2, "v": 0.8, "ease": "out"}`; `ease` là cách đi TỪ mốc trước tới mốc này
(linear, in, out, inout, hold = nhảy cóc). Timer: `v` là số giây (259200 = 72:00:00) — đếm lùi tua nhanh bằng hai mốc.

## 4. Âm thanh game
SFX tổng hợp kiểu 8-bit (không cần file): `sfx:pickup` (nhặt đồ), `sfx:coin`, `sfx:lock` (khoá mục tiêu), `sfx:combo`,
`sfx:levelup`, `sfx:slash` (dao cắt), `sfx:zip` (vật bay vào túi), `sfx:tick` (đồng hồ), `sfx:complete` (xong nhiệm
vụ), `sfx:buzz` (sai/hết giờ) — cùng `pop`, `click`, `ding`, `sparkle`, `whoosh`, `thud`, `rise`.
SFX **thật** (bộ người dùng nhập, vd "BASIC SFX QUẠ HD"): `vedit sfx list <từ khoá>` / `--category whoosh|impact|ding|…`
in đường dẫn + mốc đỉnh tiếng `hit` → `"path": "<đường dẫn>", "start": <mốc khung hình> - hit`.
`pitch` (nửa cung) cho chuỗi cao dần: combo 1-2-3 = pitch 0, 2, 4 (hoặc 0, 4, 7). Giữ tiếng thật làm chính; SFX
`volume` 0.3–0.6, đặt đúng khung của hành động; không tiếng nào y hệt quá 3 lần.

## 4b. Nhạc nền & độ dày âm thanh
Người dùng muốn **âm thanh dày hơn** (2026-11-02): mọi sự kiện HUD đều có tiếng (tick khi tick nhiệm vụ, zip khi vật bay
vào túi, combo cao dần ×4–×7 bằng `pitch`, khoá mục tiêu = `lock`, đếm lùi = `tick` mỗi giây…), tiếng game ≈ +2 dB so với
tiếng thật (vẫn kêu SAU tiếng thật 10–20 ms), và nhạc nền nhẹ:
`vedit music <dự án> --duration <giây>` → `<dự án>/audio/bed-pastel.wav` (hộp nhạc / kalimba, 8 ô nhịp vừa đúng độ dài
video, ô cuối kết bằng chuông + hợp âm giữ — rơi đúng lúc thẻ qua màn). Thêm vào plan:
`{"path": "audio/bed-pastel.wav", "role": "music", "volume": 0.075, "duck": false, "loop": false, "fade_in": 0.4,
"fade_out": 1.6}` — không duck (nhiều SFX sẽ làm nhạc "thở" liên tục). Cân bằng đã dùng (đo trước loudnorm):
tiếng thật −36,8 LUFS, tiếng game −34, nhạc −41 → bản xuất −15,4 LUFS.

## 5. Dừng hình — `Clip.freeze`
`"freeze": 1.2` giữ khung cuối của clip thêm 1.2s (tiếng gốc im, zoom chậm vẫn chạy) — chỗ cho `card` hoàn thành
hoặc khoảnh khắc "PAUSE" của game.

## 6. Công thức một màn chơi (ví dụ)
1. 0–0.5s: `visor` boot + `panel` QUEST hiện (enter slide) → người xem hiểu ngay "đây là game".
2. Mỗi thao tác = 1 mini-game: `reticle` dò → khoá đúng lúc tay chạm vật (`sfx:lock`); `meter` khi rót; `popup`
   PERFECT! đúng khung tiếng thật; tick một dòng trong `panel` (`sfx:tick`/`pickup`); cú cắt = `slash` + `sfx:slash`.
3. Nhặt nguyên liệu: `slots` với `sources` bám từng vật, `sfx:zip` lúc bay, `sfx:pickup` lúc chạm ô.
4. Cao trào: COMBO ×2, ×3 (`popup` + `sfx:combo` pitch 0/2/4 + `motion` punch).
5. Kết: `freeze` + `card` ★★★ (`sfx:complete`), `counter` timer 72:00:00 tua về 00:00:00, "LEVEL 2 UNLOCKS IN 3 DAYS".

## 7. Lỗi hay gặp
- Quá nhiều HUD cùng lúc che món ăn → tối đa 3–4 mục trên màn hình; panel/counter để ở dải trên hoặc dưới.
- Mục bám vật nhưng vật ra khỏi khung → dùng `point`/`dx`/`dy` đặt nhãn phía có khoảng trống.
- Popup trùng chỗ panel → đặt popup bám vật (`anchor` point top) hoặc dời panel.
- Chữ HUD quá nhỏ: `size` ≥ 40 cho nhãn, ≥ 100 cho popup trên khung 1080×1920.
