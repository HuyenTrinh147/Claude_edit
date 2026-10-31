---
title: Thư viện font của vedit
category: typography
tags: [font, tiếng việt, thư viện font, editplan, libass, fontbook, google fonts, ofl, tiktok sans, montserrat]
updated: 2026-10-31
sources:
  - https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/tiktoksans/METADATA.pb
  - https://raw.githubusercontent.com/tiktok/TikTokSans/main/README.md
  - https://raw.githubusercontent.com/google/fonts/main/ofl/anton/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/barlowcondensed/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/phudu/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/bangers/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/bungee/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/paytoneone/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/chakrapetch/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/lobster/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/baloo2/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/playpensans/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/shantellsans/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/prata/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/yesevaone/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/modules/choosing_type/lessons/exploring_x_height_the_em_square/content.md
  - https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/modules/using_type/lessons/language_support_in_fonts/content.md
  - (kiểm chứng bằng render vedit + log libass fontselect, 2026-10-31)
---
# Thư viện font của vedit

Toàn bộ font trong `assets/fonts/` (24 file, 19 họ kể cả Inter hệ thống). Mỗi font đã: (1) `fc-query` có `vi`;
(2) render bằng `vedit render` câu "Muối hũ cà pháo giòn rụm ỆỮỢẪ" — dấu chồng đúng, đúng font (log libass
`fontselect` trỏ đúng file, không rơi về Inter), cỡ tương đương; (3) thử trên nền sticker `pill` và với viền dày.
Giấy phép: OFL 1.1 (xem ghi chú "Bản quyền font khi làm video").

## Bảng font

`font` = giá trị ghi vào EditPlan. "Hệ số cỡ" = nhân `size` để chữ trông cao bằng Be Vietnam Pro cùng `size`
(đo chiều cao x; font toàn chữ HOA đo chiều cao chữ HOA). "Dòng" = chiều cao dòng libass dùng (usWinAscent +
usWinDescent, tính theo em) — quyết định độ cao nền `pill` và khoảng cách dòng.

| `font` | `bold: true` / `false` | Phong cách | Hợp với | Hệ số cỡ | Dòng | Lưu ý |
|---|---|---|---|---|---|---|
| `Be Vietnam Pro` | ExtraBold / SemiBold | Sans hiện đại, vẽ riêng cho tiếng Việt | tiêu đề, nhãn, giáo dục, review | 1.00 | 1.53 | font chuẩn của bảng |
| `Montserrat` | ExtraBold / Medium; `Montserrat Black` | Sans hình học, rộng | caption Hormozi, review, tạo động lực | 1.00 | 1.56 | rộng: ~24 ký tự/dòng ở size 80 |
| `TikTok Sans` | Bold / Medium; `TikTok Sans Black` | Font gốc của TikTok, hơi hẹp | phụ đề, vlog, giáo dục, tin | 1.00 | 1.36 | trông "native" nhất |
| `Anton` | Regular → `bold: false` | Condensed cực đậm kiểu Impact | hook, giá, meme, động lực | **0.80** | 1.73 | chiều cao x 0.73 em (Be Vietnam Pro 0.53) — trông to hơn ~40% |
| `Barlow Condensed` | ExtraBold / SemiBold | Condensed dễ đọc | tin tức, số liệu, list, thể thao | 1.10 | 1.35 | 2 dòng chữ HOA gần chạm dấu |
| `Phudu` | Black | Condensed toàn chữ HOA (nhà thiết kế Việt) | tít báo, thể thao, quote | 1.00 | 1.24 | gõ chữ thường vẫn ra HOA |
| `Bangers` | Regular → `bold: false` | Truyện tranh, nghiêng, toàn HOA | hài, reaction, gaming | 1.00 | 1.76 | thay thế Komika Axis (kiểu MrBeast) |
| `Bungee` | Regular → `bold: false` | Khối vuông biển hiệu, toàn HOA, rất rộng | gaming, đường phố, sự kiện | 1.00 | **2.57** | `pill` cao quá mức → dùng viền, không dùng shape |
| `Paytone One` | Regular → `bold: false` | Sans tròn đậm, thân thiện | đồ ăn, khuyến mãi, trẻ em | 1.05 | 1.63 | |
| `Chakra Petch` | Bold | Góc cạnh, kỹ thuật | công nghệ, gaming, thông số | 1.05 | 1.81 | |
| `Lobster` | Regular → `bold: false` | Script retro đậm | quán ăn, đồ uống, vintage | 1.00 | 1.49 | chỉ tiêu đề ngắn |
| `Baloo 2` | ExtraBold | Tròn mập dễ thương | đồ ăn, trẻ em, vui | 1.10 | 1.57 | |
| `Playpen Sans` | ExtraBold | Viết tay dễ đọc | vlog, mẹo, ghi chú | 0.95 | 1.80 | |
| `Shantell Sans` | ExtraBold | Bút dạ marker | hài, sticker phản ứng | 1.00 | 1.73 | |
| `Mali` | Bold | Viết tay tròn | vlog, đồ ăn | 1.00 | 2.12 | `pill` cao |
| `Pacifico` | Regular → `bold: false` | Script chữ ký | điểm nhấn 1–3 từ | **1.15** | 1.94 | chiều cao x thấp |
| `Prata` | Regular → `bold: false` | Serif Didone thanh mảnh | làm đẹp, thời trang, quote | 1.00 | 1.56 | nét mảnh: cần viền 2–3 hoặc nền tối |
| `Yeseva One` | Regular → `bold: false` | Serif hiển thị đậm, mềm | làm đẹp, quote, ẩm thực sang | 1.05 | 1.39 | |
| `Inter` (hệ thống) | Bold / Regular | Sans trung tính | thông tin | 1.00 | **1.21** | 2 dòng chữ HOA: dấu chạm nhau |

Font hệ thống khác có tiếng Việt trong môi trường này (không nằm trong `assets/fonts`, máy khác có thể thiếu):
`Inter Display` (Inter cắt cho cỡ lớn), `JetBrains Mono` (số, giá, đồng hồ đếm — chữ số cùng bề rộng).

## Cách vedit tìm font (đọc trước khi chọn)

- `font` không phân biệt hoa thường, khớp tên họ (`Montserrat`) hoặc tên đầy đủ một độ đậm (`Montserrat Black`,
  `TikTok Sans Medium`, `Be Vietnam Pro SemiBold`). Sai tên → vedit lấy font hệ thống gần nhất (thường là Inter
  hoặc DejaVu) **không báo lỗi** — chép đúng tên trong bảng.
- `bold: true` → mặt chữ gần 700 nhất (hoà thì lấy mặt đậm hơn); `bold: false` → gần 400 nhất.
- Font chỉ có Regular mà để `bold: true` → libass **tô đậm giả** (nét dày thêm ~1–2 px ở size 80): mất nét thiết kế
  của Anton/Bangers/Pacifico/Prata. Luôn đặt `bold: false` cho các font ghi "Regular → bold: false".
- Gọi theo tên một độ đậm ≤ 500 (`Montserrat Medium`, `TikTok Sans Medium`) thì cũng phải `bold: false`.
- `graphics` (callout, badge) và phụ đề `bold_pop`/`karaoke`/`boxed` luôn in đậm → chọn font có mặt ≥ 600:
  Be Vietnam Pro, Montserrat, TikTok Sans, Barlow Condensed, Phudu, Chakra Petch, Baloo 2, Playpen Sans, Shantell
  Sans, Mali. Phụ đề `clean` in thường → Montserrat/TikTok Sans ra Medium, Be Vietnam Pro ra SemiBold.
- `size` đã chuẩn hoá theo em (em ≈ 0.8 × size px), **không** theo độ cao nhìn thấy — nhân "hệ số cỡ" ở bảng khi
  đổi font hoặc đặt hai font cạnh nhau (Google Fonts Knowledge: cùng cỡ chữ, font có chiều cao x lớn trông to hơn).
- Font variable (`[wght].ttf`) **không dùng được trực tiếp**: libass chỉ vẽ instance mặc định (Montserrat VF → Thin,
  TikTok Sans VF → Light, tên `Montserrat Black` không tìm thấy → rơi về Inter). Phải tạo bản static (xem README
  trong `assets/fonts`).

## Tiếng Việt: các bẫy đã kiểm chứng

- **Văn bản phải ở dạng dựng sẵn (NFC).** Chuỗi dạng tổ hợp (NFD — chữ + dấu rời, hay gặp khi chép từ macOS hoặc
  bộ gõ "Unicode tổ hợp") làm **vỡ dấu trên mọi font**, kể cả Inter ("Muoi ̃hu ̃"). Agent viết EditPlan phải giữ
  NFC (Python: `unicodedata.normalize("NFC", s)`).
- **Hai dòng chữ HOA**: dấu nặng dòng trên (Ặ, Ệ, Ợ) có thể chạm dấu chồng dòng dưới (Ẫ, Ỗ). Khoảng hở đo được:
  Inter −0.12 em (chạm — đã thấy trên render), Barlow Condensed +0.03 em (sát), Be Vietnam Pro +0.09, TikTok Sans
  +0.14–0.17, Montserrat +0.22–0.37, Anton +0.33. Với Inter/Barlow Condensed: viết chữ thường, hoặc tách 2 `texts`
  đặt `y` cách nhau ≥ 1.6 × size/1920.
- Google Fonts Knowledge xếp tiếng Việt vào nhóm chữ "cao" (dấu chồng như Ớ cần thêm khoảng dọc) — đừng ép dòng.
- **Emoji không có trong font nào**: libass vẽ emoji thành nét đơn sắc lấy từ font dự phòng (FreeSerif, Unifont) — xấu.
  Dùng ảnh PNG qua `images` (xem ghi chú "Kiểu chữ trend trên TikTok/Reels").
- Nền `pill` tính theo chiều cao dòng → font "Dòng" lớn (Bungee 2.57, Mali 2.12, Pacifico 1.94, Chakra Petch 1.81)
  cho viên sticker cao, thô; font dòng thấp (Inter 1.21) thì dấu chồng chữ HOA sát mép trên viên.

## Chọn nhanh theo vai trò

- **Hook / tiêu đề mạnh**: `Montserrat Black`, `Anton`, `Bangers`, `Phudu`, `Baloo 2`, `Paytone One`.
- **Phụ đề**: `TikTok Sans`, `Be Vietnam Pro`, `Montserrat` (karaoke/bold_pop, chữ HOA), `Inter`.
- **Thông tin, nhãn, số**: `Barlow Condensed`, `Chakra Petch`, `TikTok Sans Medium`, `JetBrains Mono`.
- **Điểm nhấn cảm xúc**: `Pacifico`, `Lobster`, `Playpen Sans`, `Shantell Sans`, `Mali`.
- **Sang trọng**: `Prata`, `Yeseva One` + nhãn nhỏ `Montserrat Medium`.

Prata (cùng Inter, Montserrat…) nằm trong danh sách "font mặc định đồng phục AI" của repo claude-video-editor
(xem ghi chú typography của repo đó trong kho) — dùng khi có chủ đích, không dùng theo phản xạ.

## Đã thử và loại (2026-10-31)

| Font | Lý do |
|---|---|
| Playfair Display | `fc-query` không có `vi`: thiếu U+031B (dấu móc tổ hợp); có Reserved Font Name nên không tạo bản static cùng tên |
| Patrick Hand | thiếu U+0302, U+0306 (dù google/fonts ghi subset vietnamese) |
| Coiny | thiếu U+0309, U+031B |
| Comforter Brush, Splash | đủ dấu nhưng nét mảnh/xù, dấu chồng lệch — khó đọc trên điện thoại |
| Dancing Script | chỉ có bản variable, có Reserved Font Name |
| M PLUS Rounded 1c | 3,6 MB mỗi độ đậm (kèm chữ Nhật) |

Ứng viên có tiếng Việt chưa thêm (còn dư địa): Sriracha (viết tay nghiêng), Itim, Charm, Grandstander, Nunito,
Sigmar One, Kanit, Lexend, Oswald, Big Shoulders Display, Fraunces, Lora — font variable thì phải tạo bản static.

## Áp dụng vào vedit

Còn thiếu / nên làm (vấn đề → giải pháp → độ khó):
1. Chuỗi NFD vỡ dấu → `ass_text()` gọi `unicodedata.normalize("NFC", ...)` → rất dễ.
2. Sai tên font rơi về Inter âm thầm → `vedit validate` cảnh báo font không có trong `assets/fonts`/hệ thống và ký
   tự thiếu trong `cmap` (fontTools) → dễ.
3. Chỉ có `bold` true/false → thêm `weight` (100–900) chọn mặt gần nhất, tránh tô đậm giả → dễ–vừa.
4. Nền `pill`/`banner` tính theo chiều cao dòng của font → tính theo khung mực thật (chữ HOA + dấu chồng) → vừa.
5. Không chỉnh được khoảng cách dòng → thêm `line_spacing` (đặt từng dòng bằng `\pos`) → vừa.
6. `size` chuẩn theo em, chưa theo độ cao nhìn thấy → tuỳ chọn chuẩn hoá theo chiều cao x (dùng hệ số ở bảng) → vừa.
7. Emoji trong chữ → tự đổi emoji thành ảnh PNG Noto Emoji đặt cạnh chữ → vừa.
