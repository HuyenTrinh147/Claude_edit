Font dùng cho chữ, phụ đề & đồ hoạ của vedit. Mọi font dưới đây đều có tiếng Việt và được kiểm tra ngày 2026-10-31:
`fc-query` có `vi`, và render thật bằng `vedit render` (dấu chồng Ẫ Ỗ Ữ Ợ Ệ đúng, log libass `fontselect` chọn
đúng file, không rơi về Inter). Giấy phép: **SIL Open Font License 1.1** — file `OFL-<Tên>.txt` đi kèm từng họ.
Hướng dẫn chọn font theo thể loại: `vedit kb show typography/thu-vien-font-cua-vedit`.

| `font` trong EditPlan | File | `bold: true` → / `bold: false` → | Phong cách | Giấy phép |
|---|---|---|---|---|
| `Be Vietnam Pro` | BeVietnamPro-ExtraBold.ttf, BeVietnamPro-SemiBold.ttf | ExtraBold 800 / SemiBold 600 | Sans hiện đại, thiết kế cho tiếng Việt | OFL-BeVietnamPro.txt |
| `Montserrat` | Montserrat-Medium.ttf, Montserrat-ExtraBold.ttf, Montserrat-Black.ttf ¹ | ExtraBold 800 / Medium 500 (Black 900: `Montserrat Black`) | Sans hình học đậm — caption kiểu Hormozi, tiêu đề | OFL-Montserrat.txt |
| `TikTok Sans` | TikTokSans-Medium.ttf, TikTokSans-Bold.ttf, TikTokSans-Black.ttf ¹ ² | Bold 700 / Medium 500 (Black 900: `TikTok Sans Black`) | Font gốc của TikTok — phụ đề, chữ "native" | OFL-TikTokSans.txt |
| `Anton` | Anton-Regular.ttf | Regular (rất đậm sẵn) — dùng `bold: false` | Condensed kiểu Impact — caption viral, meme, giá | OFL-Anton.txt |
| `Barlow Condensed` | BarlowCondensed-SemiBold.ttf, BarlowCondensed-ExtraBold.ttf | ExtraBold 800 / SemiBold 600 | Condensed dễ đọc — tin tức, số liệu, nhãn | OFL-BarlowCondensed.txt |
| `Phudu` | Phudu-Black.ttf ¹ | Black 900 (mọi trường hợp) | Condensed toàn chữ HOA, của nhà thiết kế Việt (Dương Trần) — tít báo, thể thao | OFL-Phudu.txt |
| `Bangers` | Bangers-Regular.ttf | Regular — dùng `bold: false` | Truyện tranh, toàn chữ HOA, nghiêng — hài, giải trí | OFL-Bangers.txt |
| `Bungee` | Bungee-Regular.ttf | Regular — dùng `bold: false` | Biển hiệu đường phố khối vuông, chữ HOA — gaming, đường phố | OFL-Bungee.txt |
| `Paytone One` | PaytoneOne-Regular.ttf | Regular — dùng `bold: false` | Sans tròn đậm, thân thiện — đồ ăn, khuyến mãi | OFL-PaytoneOne.txt |
| `Chakra Petch` | ChakraPetch-Bold.ttf | Bold 700 (mọi trường hợp) | Góc cạnh kỹ thuật — công nghệ, gaming, thông số | OFL-ChakraPetch.txt |
| `Lobster` | Lobster-Regular.ttf | Regular — dùng `bold: false` | Script retro đậm — quán ăn, đồ uống, vintage | OFL-Lobster.txt |
| `Baloo 2` | Baloo2-ExtraBold.ttf ¹ | ExtraBold 800 (mọi trường hợp) | Tròn mập dễ thương — đồ ăn, trẻ em, vui | OFL-Baloo2.txt |
| `Playpen Sans` | PlaypenSans-ExtraBold.ttf ¹ | ExtraBold 800 (mọi trường hợp) | Viết tay dễ đọc — vlog, ghi chú, mẹo | OFL-PlaypenSans.txt |
| `Shantell Sans` | ShantellSans-ExtraBold.ttf ¹ | ExtraBold 800 (mọi trường hợp) | Bút dạ marker — hài, phản ứng, sticker | OFL-ShantellSans.txt |
| `Mali` | Mali-Bold.ttf | Bold 700 (mọi trường hợp) | Viết tay tròn dễ thương — vlog, đồ ăn | OFL-Mali.txt |
| `Pacifico` | Pacifico-Regular.ttf | Regular — dùng `bold: false` | Script chữ ký — điểm nhấn 1–3 từ, dùng ít | OFL-Pacifico.txt |
| `Prata` | Prata-Regular.ttf | Regular — dùng `bold: false` | Serif Didone thanh lịch — làm đẹp, thời trang, quote | OFL-Prata.txt |
| `Yeseva One` | YesevaOne-Regular.ttf | Regular — dùng `bold: false` | Serif hiển thị đậm, mềm — làm đẹp, quote, ẩm thực sang | OFL-YesevaOne.txt |
| `Inter`, `Inter Display`, `JetBrains Mono` | (font hệ thống của môi trường này, không nằm trong thư mục) | Bold / Regular | Thông tin, số liệu | — |

¹ Bản **static tạo từ font variable** của google/fonts bằng fontTools (libass/vedit chỉ đọc được instance mặc định của
font variable — Montserrat sẽ thành Thin). OFL cho phép bản sửa đổi; các họ này **không có Reserved Font Name** nên giữ
tên gốc. Lệnh đã dùng (ví dụ):
`python -m fontTools.varLib.instancer "Montserrat[wght].ttf" wght=800 --update-name-table -o Montserrat-ExtraBold.ttf`
² TikTok Sans: `opsz=36 wdth=100 slnt=0 wght=500|700|900` (đúng toạ độ named instance), sau đó bỏ nhãn "36pt" khỏi
bảng `name` để tên gọn (`TikTok Sans Black`, `TikTok Sans Medium`).

Ghi nhớ:
- Tên `font` không phân biệt hoa thường; gọi theo tên họ (`Montserrat`) hoặc tên đầy đủ của một độ đậm
  (`Montserrat Black`, `TikTok Sans Medium`, `Be Vietnam Pro SemiBold`). Gọi độ đậm ≤ 500 theo tên thì đặt
  `bold: false`, nếu không libass tô đậm giả.
- Font chỉ có Regular: đặt `bold: false` (bold: true → libass làm đậm giả, nét dày thêm ~1–2 px, mất nét thiết kế).
  Đồ hoạ (`graphics`) và phụ đề `bold_pop`/`karaoke`/`boxed` luôn in đậm → nên dùng font có độ đậm ≥ 600 ở trên.
- Nguồn: https://github.com/google/fonts (thư mục `ofl/<tên>`), riêng TikTok Sans còn có https://github.com/tiktok/TikTokSans.

Thêm font mới (quy trình đã dùng):
1. Chỉ lấy font OFL/Apache từ nguồn chính thức (google/fonts, repo GitHub của tác giả) — **không** dùng font "Việt hoá"
   (SVN-, UTM, iCiel…) không rõ giấy phép.
2. `fc-query --format '%{family} | %{style} | %{lang}\n' file.ttf` phải có `vi` (`fc-validate -l vi file.ttf` cho biết
   ký tự còn thiếu). Font variable → tạo bản static như trên (kiểm tra Reserved Font Name trong OFL trước khi sửa).
3. Render thử bằng `vedit render` (khung `color:#333333`, chữ "Muối hũ cà pháo giòn rụm ỆỮỢẪ"), xem khung hình và
   log `fontselect` trong `renders/.work/ffmpeg.log`.
4. Đặt `OFL-<Tên>.txt` cạnh font, cập nhật bảng này và ghi chú `knowledge/typography/thu-vien-font-cua-vedit.md`.

Đã thử và loại (2026-10-31): Playfair Display (thiếu U+031B dấu móc tổ hợp; có RFN), Patrick Hand (thiếu U+0302,
U+0306), Coiny (thiếu U+0309, U+031B), Comforter Brush & Splash (nét mảnh, dấu chồng lệch — khó đọc trên điện
thoại), Dancing Script (chỉ có variable + RFN), M PLUS Rounded 1c (3,6 MB vì có chữ Nhật).
