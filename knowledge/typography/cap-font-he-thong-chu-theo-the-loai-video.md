---
title: Cặp font & hệ thống chữ theo thể loại video
category: typography
tags: [cặp font, font pairing, hệ thống chữ, thể loại, ẩm thực, review, giáo dục, làm đẹp, hài, tin tức, editplan]
updated: 2026-10-31
sources:
  - https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/modules/choosing_type/lessons/pairing_typefaces/content.md
  - https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/modules/choosing_type/lessons/emotive_considerations_for_choosing_typefaces/content.md
  - https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/modules/using_type/lessons/breaking_the_rules/content.md
  - https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/modules/choosing_type/lessons/exploring_width_in_type/content.md
  - https://www.videomaker.com/how-to/editing/motion-graphics/type-in-video-picking-the-right-fonts/
  - https://editframe.com/skills/brand-video-generator/typography-personalities
  - https://www.submagic.co/blog/how-to-make-alex-hormozi-captions
  - https://submagic.co/blog/how-to-make-captions-like-iman-gadzhi
  - (công thức của Agent 1 — từng đoạn JSON đã validate + render trên video thật, 2026-10-31)
---
# Cặp font & hệ thống chữ theo thể loại video

Chữ trong video ngắn là một **hệ thống**, không phải từng dòng rời: mỗi vai trò (hook, thông tin, phụ đề, nhấn
cảm xúc) có một font, một màu, một kiểu nền, một kiểu xuất hiện — giữ nguyên suốt video. Danh sách font và tên
dùng trong EditPlan: ghi chú "Thư viện font của vedit".

## Nguyên tắc ghép font

- **Hỏi trước: có cần font thứ hai không?** Google Fonts Knowledge khuyên khai thác hết một họ (độ đậm, cỡ, chữ
  HOA/thường) trước. Thêm font thứ hai khi: đổi ngữ cảnh (số liệu cạnh lời kể), cần thêm cá tính (font nghiêm túc +
  font viết tay thân thiện), font chính thiếu độ đậm, hoặc thiếu ngôn ngữ (với ta: thiếu tiếng Việt).
- **Khác đủ nhưng không quá khác** ("distinction và harmony"). Khi phân vân: ghép serif + sans. Hai font cùng loại
  na ná nhau (Montserrat + Be Vietnam Pro, hai sans hình học) là lỗi phổ biến — chọn một, dùng hai độ đậm.
- **"Họ hàng"**: font ghép tốt thường chung chiều cao x, độ tương phản nét, bề rộng hoặc tâm trạng.
- **Cảm xúc trước, kỹ thuật sau**: người xem phản ứng cảm xúc với hình chữ trước khi đọc; chọn theo tâm trạng rồi
  kiểm tra kỹ thuật (đủ độ đậm, đủ tiếng Việt).
- **Quy tắc vận hành cho vedit** (tổng hợp): tối đa 2 họ + 1 font nhấn mỗi video; font nhấn (Pacifico, Lobster,
  Shantell Sans…) chỉ cho 1–3 từ; tương phản độ đậm mạnh (800–900 cho hook vs 500–600 cho thông tin); hook to gấp
  1.5–1.8 lần chữ thông tin; màu lấy 2–3 tông từ chính khung hình + trắng/gần đen.
- Chữ sáng trên nền tối trông đậm hơn, chữ tối trên nền sáng trông mảnh hơn (Google Fonts Knowledge, "breaking the
  rules") → chữ tối trên sticker sáng nên dùng mặt đậm hơn một bậc.

## Hệ thống vai trò (dùng cho mọi thể loại)

| Vai trò | `size` | Font gợi ý | Nền / viền | `animation` |
|---|---|---|---|---|
| Hook / tiêu đề (0–3 s) | 96–150 | font biểu cảm của thể loại | `pill`/`banner` hoặc viền 8–12 | `bounce`, `pop`, `wipe` |
| Thông tin, bước, nhãn | 52–66 | sans dễ đọc (TikTok Sans, Be Vietnam Pro, Barlow Condensed) | `pill` màu nhấn hoặc viền 4–6 | `slide_left`, `slide_up`, `fade` |
| Phụ đề (`captions`) | 64–90 | TikTok Sans, Be Vietnam Pro, Montserrat | `bold_pop`/`karaoke`/`clean`/`boxed` | (theo style) |
| Nhấn cảm xúc | 70–110 | viết tay / script | viền 3–5 hoặc `pill`, `rotation` ±4–8° | `pop`, `word_pop` |
| Số / giá / điểm | 120–160 | Anton, Barlow Condensed, Phudu | viền 8–10 | `bounce` |
| Nhãn phụ (nguồn, ngày giờ) | 38–46 | Montserrat Medium / TikTok Sans Medium (`bold: false`) | `pill` tối 35–55% hoặc viền 3 | `fade` |

## Bảng chọn nhanh theo thể loại

| Thể loại | Tiêu đề | Thông tin / phụ đề | Nhấn | Màu gợi ý |
|---|---|---|---|---|
| Ẩm thực | Baloo 2 / Paytone One | Be Vietnam Pro, `bold_pop` | Playpen Sans, Mali | đỏ ớt #E8432E, vàng nghệ #FFD23F, kem #FFF4D6, nâu #3A2A1A |
| ASMR / chill | (không tiêu đề to) | TikTok Sans Medium nhỏ | Playpen Sans | trắng, kem, nền tối 35% |
| Vlog đời sống | Playpen Sans | TikTok Sans, `clean` | Pacifico | pastel, xanh than #2D3A4A |
| Review | Montserrat Black (HOA) | TikTok Sans, `karaoke` Montserrat | Anton cho điểm/giá | trắng, vàng #FFE14D, xanh #1E9E5A, đỏ #D93A3A |
| Công nghệ | Chakra Petch | TikTok Sans Medium | JetBrains Mono cho số | xanh lơ #3DE0FF trên #0F1720 |
| Giáo dục | Be Vietnam Pro | TikTok Sans, `bold_pop` | màu nhấn cho từ khoá | xanh đậm #1B2A4A, vàng #FFD23F |
| Làm đẹp / thời trang | Prata / Yeseva One | Montserrat Medium, `clean` | Pacifico | kem #FFF6E5, hồng #F7C6D0, nâu #3B2A2A |
| Hài | Bangers (viền kép) | Montserrat HOA từng từ, `bold_pop` | Shantell Sans | vàng #FFE14D, đen #111111, trắng |
| Tin tức | Barlow Condensed + Phudu | TikTok Sans, `boxed` | — | đỏ #E8232E, đen 85%, trắng |
| Truyền cảm hứng | Yeseva One + Anton | Montserrat, `clean` | — | trắng, vàng đồng #E9C46A, look `moody` |

## Công thức JSON theo thể loại

Mỗi khối là một phần EditPlan (`texts`, `captions`, đôi khi `look`) cho khung 1080×1920 — đổi `start`/`end` theo
timeline thật và `y` theo vùng trống của khung (`vedit frame <dự án> <giây> --grid`). Font chỉ có Regular luôn kèm
`"bold": false`.

### Ẩm thực — ấm, nhà làm, "thèm"
Hook trên sticker kem nghiêng nhẹ, dòng phụ viết tay bật từng từ; bước làm trên viên màu đỏ ớt.
```json
{
 "texts": [
  {"text": "Cà pháo muối xổi", "start": 0.0, "end": 2.6, "y": 0.17, "size": 100, "font": "Baloo 2", "color": "#3A2A1A", "shape": "pill", "shape_color": "#FFF4D6", "rotation": -3, "animation": "bounce"},
  {"text": "giòn rụm sau 1 đêm", "start": 0.35, "end": 2.6, "y": 0.235, "size": 62, "font": "Playpen Sans", "color": "#FFFFFF", "outline": 5, "outline_color": "#3A2A1A", "rotation": -3, "animation": "word_pop"},
  {"text": "Bước 1 · Pha nước muối", "start": 3.0, "end": 5.5, "y": 0.14, "size": 60, "font": "Be Vietnam Pro", "color": "#FFFFFF", "shape": "pill", "shape_color": "#E8432E", "animation": "slide_left"}
 ],
 "captions": {"style": "bold_pop", "font": "Be Vietnam Pro", "size": 72, "position": "lower", "segments": [{"start": 3.0, "end": 5.5, "text": "Nước muối pha loãng thôi nha"}]}
}
```

### ASMR / chill — ít chữ, nhỏ, không giật
Chữ thường, nền tối mờ, chỉ `fade`; để tiếng thật dẫn nhịp (SFX `pop` gần như không dùng).
```json
{
 "texts": [
  {"text": "cà pháo muối · tập 3", "start": 0.0, "end": 3.0, "y": 0.13, "size": 46, "font": "TikTok Sans Medium", "bold": false, "color": "#FFFFFF", "shape": "pill", "shape_color": "#000000", "shape_opacity": 0.35, "animation": "fade"},
  {"text": "nghe tiếng giòn nè", "start": 3.2, "end": 5.8, "y": 0.66, "size": 56, "font": "Playpen Sans", "color": "#FFF4D6", "outline": 3, "outline_color": "#2B2118", "animation": "fade"}
 ]
}
```

### Vlog đời sống — thân mật, như nhật ký
Tiêu đề viết tay gõ dần, nhãn giờ/địa điểm trên viên trắng, phụ đề `clean` chữ thường; một từ cảm xúc bằng script.
```json
{
 "texts": [
  {"text": "một ngày đi chợ\ncùng mẹ", "start": 0.0, "end": 2.8, "y": 0.2, "size": 84, "font": "Playpen Sans", "color": "#FFFFFF", "outline": 6, "outline_color": "#2D3A4A", "rotation": -2, "animation": "typewriter"},
  {"text": "06:30 · chợ Bà Chiểu", "start": 0.6, "end": 2.8, "y": 0.29, "size": 42, "font": "TikTok Sans Medium", "bold": false, "color": "#2D3A4A", "shape": "pill", "shape_color": "#FFFFFF", "shape_opacity": 0.9, "animation": "fade"},
  {"text": "xinh xỉu", "start": 3.2, "end": 5.6, "x": 0.68, "y": 0.6, "size": 88, "font": "Pacifico", "bold": false, "color": "#FFD6E0", "outline": 4, "outline_color": "#5A2D3C", "rotation": -8, "animation": "pop"}
 ],
 "captions": {"style": "clean", "font": "TikTok Sans", "size": 66, "position": "lower", "segments": [{"start": 0.3, "end": 2.6, "text": "Sáng nay dậy sớm đi chợ nè"}]}
}
```

### Review sản phẩm / quán — dứt khoát, có phán quyết
Câu hỏi hook chữ HOA đen đặc, điểm số Anton to vàng, ưu/nhược trên viên xanh/đỏ, phụ đề karaoke chữ HOA.
```json
{
 "texts": [
  {"text": "CÓ ĐÁNG 89K?", "start": 0.0, "end": 2.6, "y": 0.16, "size": 112, "font": "Montserrat Black", "color": "#FFFFFF", "outline": 9, "outline_color": "#111111", "animation": "pop"},
  {"text": "8.5/10", "start": 3.0, "end": 5.6, "y": 0.2, "size": 150, "font": "Anton", "bold": false, "color": "#FFE14D", "outline": 10, "outline_color": "#111111", "animation": "bounce"},
  {"text": "Điểm cộng: giòn, vừa mặn", "start": 3.4, "end": 5.6, "y": 0.29, "size": 56, "font": "TikTok Sans", "color": "#FFFFFF", "shape": "pill", "shape_color": "#1E9E5A", "animation": "slide_left"},
  {"text": "Điểm trừ: hơi cay", "start": 3.8, "end": 5.6, "y": 0.34, "size": 56, "font": "TikTok Sans", "color": "#FFFFFF", "shape": "pill", "shape_color": "#D93A3A", "animation": "slide_left"}
 ],
 "captions": {"style": "karaoke", "font": "Montserrat", "uppercase": true, "size": 80, "position": "lower", "highlight_color": "#FFE600", "segments": [{"start": 0.3, "end": 2.6, "text": "hũ này giòn thật sự"}]}
}
```
Biến thể **công nghệ**: thông số bằng Chakra Petch trên nền tối, chữ xanh lơ.
```json
{
 "texts": [
  {"text": "PIN 5000 mAh", "start": 0.0, "end": 2.6, "y": 0.16, "size": 96, "font": "Chakra Petch", "color": "#3DE0FF", "shape": "pill", "shape_color": "#0F1720", "shape_opacity": 0.9, "animation": "wipe"},
  {"text": "sạc đầy 45 phút", "start": 0.4, "end": 2.6, "y": 0.225, "size": 54, "font": "TikTok Sans Medium", "bold": false, "color": "#FFFFFF", "outline": 4, "outline_color": "#0F1720", "animation": "fade"}
 ]
}
```

### Giáo dục / mẹo / giải thích — rõ ràng trước, đẹp sau
Câu hỏi trên khối xanh đậm, ý chính màu vàng, phụ đề chữ thường (đọc nhanh hơn chữ HOA). Dùng `badge` +
`progress_bar` (font `Be Vietnam Pro`) cho video nhiều bước.
```json
{
 "texts": [
  {"text": "Vì sao cà pháo\nphải ngâm muối?", "start": 0.0, "end": 3.0, "y": 0.18, "size": 90, "font": "Be Vietnam Pro", "color": "#FFFFFF", "shape": "pill", "shape_color": "#1B2A4A", "shape_opacity": 0.92, "animation": "slide_up"},
  {"text": "Muối rút nước khỏi quả", "start": 3.2, "end": 5.8, "y": 0.15, "size": 64, "font": "Be Vietnam Pro", "color": "#FFD23F", "outline": 6, "outline_color": "#1B2A4A", "animation": "pop"}
 ],
 "captions": {"style": "bold_pop", "font": "TikTok Sans", "size": 72, "position": "lower", "segments": [{"start": 3.2, "end": 5.8, "text": "nên quả co lại và giòn"}]}
}
```

### Làm đẹp / thời trang — thanh lịch, nhiều khoảng thở
Serif mảnh **phải có viền tối 2–3 hoặc nền tối** (đã thử: Prata màu kem không viền trên tường sáng gần như không
đọc được). Nhãn nhỏ chữ HOA trên viên nâu mờ; một từ script màu hồng.
```json
{
 "texts": [
  {"text": "Lớp nền mỏng nhẹ", "start": 0.0, "end": 3.0, "y": 0.15, "size": 100, "font": "Prata", "bold": false, "color": "#FFF6E5", "outline": 2.5, "outline_color": "#3B2A2A", "animation": "blur_in"},
  {"text": "3 BƯỚC · 5 PHÚT", "start": 0.5, "end": 3.0, "y": 0.215, "size": 40, "font": "Montserrat Medium", "bold": false, "color": "#FFFFFF", "shape": "pill", "shape_color": "#3B2A2A", "shape_opacity": 0.55, "animation": "fade"},
  {"text": "xinh", "start": 3.4, "end": 5.6, "x": 0.7, "y": 0.6, "size": 100, "font": "Pacifico", "bold": false, "color": "#F7C6D0", "outline": 3, "outline_color": "#5A2D3C", "rotation": -6, "animation": "fade"}
 ],
 "captions": {"style": "clean", "font": "Montserrat", "size": 62, "position": "lower", "segments": [{"start": 3.2, "end": 5.6, "text": "tán mỏng từ giữa mặt ra"}]}
}
```

### Hài / giải trí — to, lệch, viền kép
Chữ truyện tranh viền kép (hai `texts` giống hệt: dưới viền đen 20, trên viền trắng 9), sticker bút dạ, phụ đề
từng từ ở giữa khung.
```json
{
 "texts": [
  {"text": "KHOAN ĐÃ!", "start": 0.0, "end": 2.0, "y": 0.2, "size": 150, "font": "Bangers", "bold": false, "color": "#FFE14D", "outline": 20, "outline_color": "#111111", "rotation": -6, "animation": "bounce"},
  {"text": "KHOAN ĐÃ!", "start": 0.0, "end": 2.0, "y": 0.2, "size": 150, "font": "Bangers", "bold": false, "color": "#FFE14D", "outline": 9, "outline_color": "#FFFFFF", "rotation": -6, "animation": "bounce"},
  {"text": "mặn xỉu luôn á", "start": 2.4, "end": 5.6, "x": 0.64, "y": 0.66, "size": 70, "font": "Shantell Sans", "color": "#111111", "shape": "pill", "shape_color": "#FFFFFF", "rotation": 5, "animation": "pop"}
 ],
 "captions": {"style": "bold_pop", "font": "Montserrat", "uppercase": true, "size": 104, "position": "center", "segments": [{"start": 2.4, "end": 2.9, "text": "ai"}, {"start": 2.9, "end": 3.3, "text": "cho"}, {"start": 3.3, "end": 3.9, "text": "nhiều"}, {"start": 3.9, "end": 4.6, "text": "muối"}]}
}
```

### Tin tức / thông tin nhanh — khẩn, đáng tin
Băng đỏ "TIN NÓNG", tít condensed HOA trên khối đen, dòng nguồn nhỏ; phụ đề `boxed` (nền đen theo từng dòng).
```json
{
 "texts": [
  {"text": "TIN NÓNG", "start": 0.0, "end": 3.0, "y": 0.13, "size": 96, "font": "Barlow Condensed", "color": "#FFFFFF", "shape": "banner", "shape_color": "#E8232E", "animation": "slide_left"},
  {"text": "GIÁ CÀ PHÁO TĂNG GẤP ĐÔI", "start": 0.3, "end": 3.0, "y": 0.205, "size": 80, "font": "Phudu", "color": "#FFFFFF", "shape": "pill", "shape_color": "#111111", "shape_opacity": 0.85, "animation": "wipe"},
  {"text": "Nguồn: chợ đầu mối · 31/10", "start": 0.6, "end": 3.0, "y": 0.255, "size": 38, "font": "Montserrat Medium", "bold": false, "color": "#FFFFFF", "outline": 3, "outline_color": "#111111", "animation": "fade"}
 ],
 "captions": {"style": "boxed", "font": "TikTok Sans", "size": 62, "position": "lower", "segments": [{"start": 0.3, "end": 3.0, "text": "Giá tăng từ 20 lên 40 nghìn/kg"}]}
}
```

### Truyền cảm hứng / quote — điện ảnh, chậm
Serif mềm cho nửa câu đầu, condensed HOA vàng đồng cho nửa sau (tương phản loại chữ + độ đậm), look `moody`.
```json
{
 "texts": [
  {"text": "Chậm cũng được,", "start": 0.0, "end": 3.5, "y": 0.42, "size": 96, "font": "Yeseva One", "bold": false, "color": "#FFFFFF", "outline": 2, "outline_color": "#1A1A1A", "animation": "blur_in"},
  {"text": "MIỄN LÀ ĐỪNG DỪNG", "start": 0.8, "end": 3.5, "y": 0.5, "size": 110, "font": "Anton", "bold": false, "color": "#E9C46A", "outline": 4, "outline_color": "#1A1A1A", "animation": "wipe"}
 ],
 "look": {"preset": "moody", "vignette": 0.35}
}
```
Phụ đề kiểu Iman Gadzhi (chữ thường, Montserrat mảnh): `{"style": "clean", "font": "Montserrat", "size": 60}`.

## Lỗi hay gặp khi ghép chữ

- Ba–bốn font trong một video, mỗi đoạn một kiểu → trông nghiệp dư. Giữ hệ thống ở trên từ đầu đến cuối.
- Hai sans na ná (Montserrat tiêu đề + Be Vietnam Pro thông tin) → chọn một họ, đổi độ đậm/cỡ.
- Font script (Pacifico, Lobster) cho câu dài hoặc phụ đề → khó đọc; chỉ 1–3 từ.
- Serif mảnh, chữ sáng không viền đặt lên nền sáng → biến mất (đã thấy trên render).
- Cùng một loại thông tin mà lúc `pop` lúc `slide_left` → người xem mất "nhịp đọc".

## Áp dụng vào vedit

Còn thiếu (vấn đề → giải pháp → độ khó):
1. Phải lặp lại font/màu/shape ở từng `texts` → thêm `text_styles` (bộ kiểu đặt tên, vd `"hook"`, `"info"`) và trường
   `style` trong `texts` tham chiếu tới nó; kèm vài preset theo thể loại ở trên → dễ–vừa.
2. Không có giãn chữ (tracking) cho nhãn nhỏ chữ HOA kiểu thời trang → thêm `letter_spacing` (thẻ ASS `\fsp`) → dễ.
3. Không có chữ nghiêng (`\i1`) cho trích dẫn → thêm `italic` (chỉ dùng khi font có mặt Italic thật) → dễ.
4. Không tô màu riêng một từ trong một dòng → cú pháp đánh dấu (vd `*từ khoá*` → `highlight_color`) → vừa.
5. Viền kép phải nhân đôi `texts` → thêm `outline2`/`outline2_color` (vẽ thêm một lớp viền phía dưới) → dễ.
6. Chưa kiểm tra "quá 2 họ font / font script cho câu dài" → `vedit validate` cảnh báo theo hệ thống ở trên → dễ.
