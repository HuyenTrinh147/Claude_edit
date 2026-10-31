---
title: claude-video-editor: Typography cho video và font tiếng Việt
category: typography
tags: [claude-video-editor, typography, font tiếng việt, cặp font, độ đậm, google fonts, ofl, libass]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/typography.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/house-style.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/captions.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/MOTION_PHILOSOPHY.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/references/style-intake.md
  - https://github.com/assafkip/claude-video-editor/blob/master/recipes/01-launch-video.md
  - https://raw.githubusercontent.com/google/fonts/main/ofl/bevietnampro/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/anton/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/barlowcondensed/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/bebasneue/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/METADATA.pb
  - https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/METADATA.pb
---
# claude-video-editor: Typography cho video và font tiếng Việt

## 1. Luật typography của HyperFrames (typography.md)

- **Danh sách "cấm"** — font mặc định của dữ liệu huấn luyện, tạo "đồng phục AI": Inter, Roboto, Open Sans, Noto
  Sans, Arimo, Lato, Source Sans, PT Sans, Nunito, Poppins, Outfit, Sora, Playfair Display, Cormorant Garamond, Bodoni
  Moda, EB Garamond, Cinzel, Prata, Syne ("Syne … is an instant AI design tell"). Không tuyệt đối: dùng được nếu là
  lựa chọn có chủ đích cho nội dung.
- **Không ghép hai font sans**; ghép xuyên loại: serif + sans, hoặc sans + mono. Không ghép hai font "na ná nhưng
  khác" (hai geometric sans, hai transitional serif) — hoặc một font hai độ đậm, hoặc tương phản nhiều trục.
- **Một font biểu cảm mỗi cảnh** — "One performs, one recedes."
- **Tương phản độ đậm cực mạnh**: video cần **300 vs 900**, không phải 400 vs 700.
- **Cỡ video, không phải cỡ web** (khung 1920 ngang): tiêu đề ≥ 60px, thân ≥ 20px, nhãn dữ liệu ≥ 16px.
- **Thời gian đọc cố định**: "3 seconds on screen = must be readable in 2." Ít chữ hơn, chữ to hơn.
- **Tracking** cỡ hiển thị: −0.03 đến −0.05em (nén video làm mất chi tiết nét).
- **Nền tối**: chữ sáng trông đậm hơn và sát hơn → hạ độ đậm (350 thay 400 cho thân chữ), tăng line-height
  +0.05–0.1, tăng letter-spacing +0.01em ở cỡ lớn.
- **Số liệu**: bật `tabular-nums` cho bộ đếm/bảng (chữ số cùng bề rộng, không nhảy khi đếm).
- **Chọn font bằng tư duy, không theo phản xạ**: (1) gọi tên "register" (giọng uy quyền? tâm sự riêng? kỹ thuật?
  tếu?), (2) nghĩ như **vật thể thật** (biển hiệu vẽ tay, nhãn vải trong áo, sách thiếu nhi giấy rẻ, tờ khai thuế…),
  (3) **bác bỏ lựa chọn đầu tiên** (thường là mặc định của model), (4) kiểm lại giả định (editorial không nhất thiết
  serif).
- **Đổi register**: mỗi "giọng" một font — tuyên bố / dữ liệu / ghi nguồn. "Time is hierarchy" — trong video, thứ tự
  xuất hiện thay cho vị trí. "Motion is typography" — cú đập 0.1s và fade 2s nói hai điều khác nhau với cùng một font.
- Script tìm font của repo lọc metadata Google Fonts theo nhóm (sans/serif mới phổ biến, mono, condensed 800–900,
  viết tay), **xáo 5 kết quả đầu** để model không luôn chọn cùng một font.
- Thực tế render: **nhúng font cục bộ** (`@font-face` woff2) — link Google Fonts thất bại trong renderer sandbox và chữ
  rơi về font mặc định mà không báo (recipe 1).

## 2. Cảnh báo cho tiếng Việt (đã kiểm chứng 2026-10-31)

Kiểm tra trường `subsets` trong `METADATA.pb` của repo google/fonts: nhiều font repo này gợi ý **không có tiếng Việt**
→ dấu sẽ rơi về font khác hoặc hiện ô vuông.

**Không có subset `vietnamese`**: Bebas Neue, Archivo Black, Instrument Serif, Azeret Mono, Rubik, Fredoka, Lilita One,
Titan One, DM Serif Display, Young Serif, Bagel Fat One, Darumadrop One.

**Có `vietnamese`** (tất cả OFL; "VF" = file biến thiên trong repo google/fonts):

| Nhóm | Font (độ đậm) |
|---|---|
| Đập mạnh / condensed | Anton (400), Barlow Condensed (100–900), Big Shoulders Display (VF 100–900), Oswald (VF 200–700), Saira Condensed (100–900), Archivo (VF wdth 62–125, wght 100–900), Dela Gothic One |
| Sans có cá tính | Be Vietnam Pro (100–900), Bricolage Grotesque (VF opsz/wdth/wght 200–800), Space Grotesk (VF 300–700), Epilogue (VF), Lexend (VF), Plus Jakarta Sans (VF 200–800), Unbounded (VF 200–900), Chakra Petch (300–700), Kanit/Prompt (100–900), Exo 2 (VF), Montserrat (VF 100–900) |
| Tròn, vui | Paytone One, Baloo 2 (VF 400–800), Grandstander (VF 100–900), Rowdies (300–700), Bungee, Sigmar, Quicksand, Comfortaa, Lobster |
| Viết tay | Mali (200–700), Pangolin, Itim, Patrick Hand, Playpen Sans (VF), Shantell Sans (VF), Dancing Script (VF), Charm, Pacifico |
| Serif | Fraunces (VF SOFT/WONK/opsz/wght), Lora (VF), Literata (VF), Alegreya (VF), Merriweather (VF) |
| Mono (số, kỹ thuật) | JetBrains Mono (VF 100–800), Space Mono (400–700), IBM Plex Mono (100–700) |

Inter có tiếng Việt nhưng nằm trong danh sách "đồng phục AI".

## 3. Gợi ý cặp font theo thể loại vedit (nhận định, cần thử render)

- **Đồ ăn / đời thường vui** (gần "Folk Frequency"): Paytone One hoặc Baloo 2 ExtraBold (tiêu đề) + Be Vietnam Pro
  SemiBold (thông tin) + Mali/Pangolin cho ghi chú tay.
- **Hype / review / top-list**: Anton hoặc Barlow Condensed Black (tiêu đề, VIẾT HOA, tracking hẹp) + JetBrains Mono
  cho số/giá.
- **Kể chuyện ấm / vlog**: Fraunces (serif mềm) + Be Vietnam Pro.
- **Công nghệ sạch**: Space Grotesk hoặc Bricolage Grotesque + JetBrains Mono.
Luôn giữ: một font biểu cảm + một font thông tin; độ đậm 800–900 vs 400–500; tối đa 2 họ font mỗi video.

## Áp dụng vào vedit

**Đã có**: `FontBook` chuẩn hoá cỡ chữ theo metric win và đổi tên family cho libass; chữ tự co khi > 88% bề ngang;
`assets/fonts/` có Be Vietnam Pro (ExtraBold, SemiBold), Mali Bold, Pacifico (OFL); font mặc định cấu hình
`VEDIT_FONT` = **Inter**.

**Còn thiếu**: font mặc định là font "đồng phục AI"; thư viện font hẹp (thiếu nhóm condensed đập mạnh, serif, mono);
chưa có quy tắc cặp font/độ đậm trong prompt; chưa kiểm tra font có đủ dấu tiếng Việt.

**Đề xuất (ưu tiên)**:
1. Đổi mặc định `VEDIT_FONT` sang **Be Vietnam Pro** (đã có sẵn, đủ tiếng Việt). Dễ.
2. Bổ sung vào `assets/fonts/` (OFL, kèm file OFL): **Anton**, **Barlow Condensed** (ExtraBold/Black), **Paytone One**,
   **Fraunces**, **JetBrains Mono**, **Pangolin**. Với font chỉ có bản VF, tạo bản static bằng fontTools (vedit đã cài):
   `fonttools varLib.instancer Fraunces.ttf wght=800 --static --update-name-table -o Fraunces-ExtraBold.ttf`
   (font VF dùng trực tiếp với libass cần thử trước — ưu tiên file static). Dễ.
3. `vedit validate` cảnh báo khi font trong EditPlan **thiếu glyph** cho ký tự của chữ (đọc `cmap` bằng fontTools —
   bắt lỗi dấu tiếng Việt rơi font). Dễ–vừa.
4. Prompt Agent 2/3: "1 font biểu cảm + 1 font thông tin, 800–900 vs 400–500, ≤ 2 họ font; tiêu đề ≥ 6% chiều cao
   khung dọc; chữ trên màn đọc xong trong 2/3 thời gian hiển thị". Dễ.
5. Bật `tabular-nums` tương đương: dùng JetBrains Mono cho bộ đếm/giá khi có animation đếm số (tránh nhảy bề rộng). Dễ.
