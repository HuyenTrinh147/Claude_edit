---
title: Quy tắc chữ dễ đọc trên điện thoại
category: typography
tags: [dễ đọc, cỡ chữ, viền, bóng đổ, vùng an toàn, phụ đề, thời gian đọc, tiếng việt, captions]
updated: 2026-10-31
sources:
  - https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/modules/readability_and_accessibility/lessons/how_type_influences_readability/content.md
  - https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/modules/readability_and_accessibility/lessons/introducing_accessibility_in_typography/content.md
  - https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/modules/using_type/lessons/track_carefully_or_not_at_all/content.md
  - https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/modules/using_type/lessons/choosing_a_suitable_line_height/content.md
  - https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/modules/using_type/lessons/language_support_in_fonts/content.md
  - https://backlothelp.netflix.com/hc/en-us/articles/220447048-Vietnamese-Timed-Text-Style-Guide
  - https://backlothelp.netflix.com/hc/en-us/articles/215758617
  - https://clevercast.com/bbc-subtitling-guidelines
  - https://blitzcutai.com/blog/best-caption-size-tiktok-2026
  - https://blitzcutai.com/blog/caption-background-vs-outline-vs-shadow
  - https://sovran.ai/blog/tiktok-video-ad-specs
  - https://blog.adnabu.com/?p=36891
  - (đo bằng FontBook của vedit + render thử trên video thật, 2026-10-31)
---
# Quy tắc chữ dễ đọc trên điện thoại

Khung 1080×1920. Trong vedit `size` là cỡ em chuẩn hoá: **em ≈ 0.8 × size px** với mọi font; `outline` tính bằng
px của khung. Khung khác: nhân mọi số với `width / 1080`. Ước tính vật lý: trên máy 6,1 inch (ngang ~65 mm),
1 px khung ≈ 0,06 mm.

## 10 quy tắc nhanh

1. Phụ đề `size` 72–90; hook 100–150; nhãn phụ ≥ 40. Không có chữ nào cần đọc mà < 40.
2. Mặt chữ ≥ 600 (SemiBold) khi đè lên video; hook 800–900. Medium chỉ trên nền `pill` hoặc vùng tối yên.
3. Chữ đè video **luôn** có viền (4–7 px cho phụ đề) hoặc nền `pill` — độ tương phản của video đổi từng khung.
4. Chữ HOA chỉ cho 1–5 từ; câu dài viết thường (đọc nhanh hơn).
5. `captions` **không tự xuống dòng, không tự co** → mỗi đoạn ≤ số ký tự trong bảng dưới, dài hơn thì chèn `\n`.
6. Thời gian hiển thị chữ không đọc lên: ≥ số ký tự ÷ 15 + 0,5 s, tối thiểu 1 s; tối đa ~7 s.
7. Chữ quan trọng có tâm `y` trong 0,13–0,72; không dùng `position: top`/`bottom` cho chữ quan trọng.
8. Tối đa 2 khối chữ + phụ đề cùng lúc; không che mặt, tay đang thao tác, sản phẩm.
9. Văn bản tiếng Việt ở dạng NFC; 2 dòng chữ HOA tránh Inter/Barlow Condensed.
10. Xem lại khung hình thật (`vedit frame … --grid`) ở mọi mốc chữ xuất hiện, trên cả vùng sáng và vùng tối.

## Cỡ chữ theo vai trò

| Vai trò | `size` | em (px) | Ghi chú |
|---|---|---|---|
| Hook 1–4 từ | 110–150 | 88–120 | chữ HOA được; Anton nhân 0.8 |
| Tiêu đề 1–2 dòng | 84–100 | 67–80 | ≤ 18–22 ký tự/dòng |
| Phụ đề nói (karaoke, bold_pop) | 72–90 | 58–72 | các hướng dẫn caption khuyên 60–75 px cho talking-head, 75–95 px cho video năng lượng cao (nguồn: blog công cụ caption) |
| Phụ đề `clean` / tối giản | 60–70 | 48–56 | cần viền hoặc bóng rõ |
| Phụ đề 1 từ giữa khung | 96–120 | 77–96 | |
| Thông tin, bước, callout | 52–66 | 42–53 | `size` 54 ≈ cỡ chữ đọc bình thường trên điện thoại (ước tính) |
| Nhãn phụ (nguồn, giờ) | 38–46 | 30–37 | nền `pill` tối hoặc viền 3 |

Đổi font thì nhân "hệ số cỡ" trong ghi chú "Thư viện font của vedit" (vd Anton ×0.8, Pacifico ×1.15).

## Độ đậm

- Video nén làm mảnh nét → trên video dùng SemiBold trở lên; Black/ExtraBold cho hook.
- Chữ tối trên sticker sáng trông mảnh hơn → tăng một bậc độ đậm; chữ sáng trên nền tối trông đậm hơn
  (Google Fonts Knowledge, "breaking the rules").
- Font chỉ có Regular: `bold: false` (tránh tô đậm giả của libass).

## Viền, bóng, nền

| Trường hợp | Cách làm trong vedit |
|---|---|
| Phụ đề `size` 72–90 | `bold_pop`/`karaoke` tự viền ≈ 8% chiều cao dòng (~6–8 px) + bóng 2 |
| Chữ thông tin 52–66 | `outline` 4–6, màu tối (#111111 hoặc màu tối của bảng màu) |
| Hook 100–150 | `outline` 8–12 |
| Sticker viền kép | 2 `texts` giống nhau: dưới `outline` 18–20 màu tối, trên `outline` 8–9 màu trắng |
| Serif mảnh (Prata, Yeseva One) | `outline` 2–3 màu tối, hoặc `pill` tối 55%; viền dày làm hỏng nét thanh |
| Câu dài / nền rối | `shape: pill`, `shape_opacity` 0.55–0.9 (nền chữ đọc tốt nhất), hoặc phụ đề `boxed` |

- Xếp hạng độ dễ đọc trong một hướng dẫn caption (blog công cụ, không phải chuẩn): nền hộp đặc > viền > bóng đổ;
  bóng đổ chỉ nên bổ trợ cho viền, không dùng một mình.
- Chuẩn tương phản WCAG (Google Fonts Knowledge): chữ nhỏ 4,5:1, chữ lớn 3:1, nên nhắm 7:1. Trên video không đo
  được từng khung → dùng viền/nền để tự tạo tương phản.
- Trường `box`/`box_color`/`box_opacity` của `texts` **hiện không được renderer vẽ** → dùng `shape: "pill"`.
- Bóng đổ của `texts` cố định (2 px, đen 55%); muốn bóng dài/3D phải xếp nhiều bản sao lệch (xem ghi chú trend).

## Chữ HOA, khoảng chữ, khoảng dòng

- Hình dáng từ viết thường dễ nhận hơn chữ HOA → người đọc đọc chữ thường nhanh hơn (Google Fonts Knowledge).
  Phụ đề > 5 từ: viết thường; HOA cho hook 1–3 từ, nhãn ngắn, từ khoá.
- Chữ HOA và chữ nhỏ nên giãn chữ một chút; chữ cỡ hiển thị lớn có thể khít lại nhẹ ("track carefully"). vedit
  chưa có giãn chữ.
- Tiếng Việt là chữ "cao" (Ớ, Ẫ cần thêm khoảng dọc). Đo được trên 2 dòng chữ HOA: Inter chạm dấu (−0,12 em),
  Barlow Condensed sát (+0,03 em), Montserrat thoáng (+0,22 em). Chữ cỡ lớn có thể để dòng khít, nhưng không được
  để dấu dòng dưới chạm dòng trên.

## Số ký tự mỗi dòng

`captions` dùng 84% bề ngang và **không xuống dòng** (đã thử: câu 60 ký tự tràn ra hai mép). Số ký tự tối đa mỗi
dòng (đo bằng FontBook trên câu tiếng Việt thường; "HOA" khi `uppercase: true`):

| Font (phụ đề) | size 64 | size 72 | size 80 | size 90 |
|---|---|---|---|---|
| Montserrat (ExtraBold) | 31 / HOA 27 | 27 / 24 | 24 / 22 | 22 / 19 |
| TikTok Sans (Bold) | 37 / 31 | 33 / 27 | 29 / 24 | 26 / 22 |
| Be Vietnam Pro (ExtraBold) | 33 / 29 | 30 / 25 | 27 / 23 | 24 / 20 |
| Inter (Bold) | 34 / 29 | 30 / 26 | 27 / 23 | 24 / 21 |
| Barlow Condensed (ExtraBold) | 45 / 43 | 40 / 38 | 36 / 34 | 32 / 31 |
| Anton | 41 | 37 | 33 | 29 |
| Bangers (luôn HOA) | 47 | 42 | 38 | 33 |
| Phudu (luôn HOA) | 38 | 34 | 30 | 27 |
| Playpen Sans | 32 / 28 | 29 / 25 | 26 / 22 | 23 / 20 |
| Baloo 2 | 37 / 33 | 33 / 30 | 30 / 26 | 26 / 23 |

- `texts` tự co khi dòng > 88% bề ngang → tiêu đề dài một dòng sẽ bé đi; tự ngắt bằng `\n` để giữ cỡ.
- Netflix (tiếng Việt): tối đa 42 ký tự/dòng, 2 dòng — đó là trần cho phim; video ngắn nên 1–3 từ mỗi nhịp
  (kiểu Hormozi) hoặc ≤ 2 dòng ngắn.
- Ngắt dòng ở ranh giới cụm: sau dấu phẩy, trước "và / nhưng / vì / nên"; không tách từ ghép ("cà | pháo"), không
  tách số khỏi đơn vị ("5 | phút"), không để một chữ lẻ ở dòng cuối.

## Thời gian hiển thị

- Netflix, hướng dẫn tiếng Việt: tốc độ đọc tối đa 17 ký tự/giây (người lớn), 13 ký tự/giây (trẻ em); mỗi phụ đề
  ≥ 5/6 giây (~0,83 s) và ≤ 7 giây. BBC: 160–180 từ/phút, ~0,3 s mỗi từ.
- Quy tắc làm việc của vedit (suy từ trên): chữ **không đọc lên** hiển thị ≥ ký tự ÷ 15 + 0,5 s và ≥ 1 s —
  "Cà pháo muối xổi" (16 ký tự) ≥ 1,6 s; câu 40 ký tự ≥ 3,2 s. Video cho trẻ em: chia 13 thay vì 15.
- Chữ **trùng lời nói** (karaoke, từng từ) được ngắn hơn vì tai đã nghe; mỗi cụm vẫn nên ≥ 0,3 s để khỏi nháy.
- Hook phải đọc xong trước khi cảnh đổi; nếu không kịp → bớt chữ, đừng tăng tốc.

## Vùng an toàn

- TikTok không công bố số pixel cố định (phát file mẫu theo định dạng; vùng che đổi theo độ dài mô tả); các bài
  bên thứ ba đưa số khác nhau (vd trên 160 px, dưới 440 px, hai bên 80 px). Thực hành trong vedit (theo ghi chú
  platforms): tránh 12% trên, 22% dưới, 12–15% cạnh phải.
- Vị trí của vedit: `top` = 8% từ mép trên (dính thanh tab) → tránh; `upper` = 20%; `center`; `lower` = đáy chữ ở
  76% chiều cao (vị trí phụ đề an toàn); `bottom` = 9% từ đáy (bị tên tài khoản/mô tả che) → tránh.
- Chữ dài ở nửa dưới: đặt `x` 0,44–0,46 để né cột nút bên phải.

## Áp dụng vào vedit

Còn thiếu (vấn đề → giải pháp → độ khó):
1. Phụ đề tràn khung → tự xuống dòng cân đối theo bề rộng đo được (FontBook) hoặc tự co như `texts` → dễ–vừa.
2. Chưa có kiểm tra độ đọc → `vedit validate` cảnh báo: chữ < 40, thời lượng < ký tự/15 + 0,5 s, tâm chữ ngoài
   0,13–0,72, phụ đề quá bề ngang, chữ không viền/không nền → dễ.
3. Bóng đổ cố định → thêm `shadow`, `shadow_color`, `shadow_blur` (thẻ `\shad`, `\4c`, `\blur`) → dễ.
4. `box` có trong schema nhưng không vẽ → vẽ nền hộp (hoặc bỏ trường) → dễ.
5. Không chỉnh khoảng chữ/khoảng dòng → `letter_spacing` (`\fsp`), `line_spacing` → dễ / vừa.
6. Chuỗi NFD vỡ dấu → chuẩn hoá NFC khi dựng ASS → rất dễ.
