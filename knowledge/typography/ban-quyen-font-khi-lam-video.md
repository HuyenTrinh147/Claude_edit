---
title: Bản quyền font khi làm video
category: typography
tags: [bản quyền, giấy phép, ofl, font việt hoá, svn, utm, google fonts, thương mại]
updated: 2026-10-31
sources:
  - https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/OFL.txt
  - https://raw.githubusercontent.com/google/fonts/main/ofl/lobster/OFL.txt
  - https://raw.githubusercontent.com/google/fonts/main/ofl/paytoneone/OFL.txt
  - https://raw.githubusercontent.com/google/fonts/main/ofl/yesevaone/OFL.txt
  - https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/OFL.txt
  - https://raw.githubusercontent.com/google/fonts/main/ofl/dancingscript/OFL.txt
  - https://raw.githubusercontent.com/google/fonts/main/ofl/bebasneue/METADATA.pb
  - https://tug.ctan.org/fonts/gentium/OFL-FAQ.txt
  - https://developers.google.com/fonts/faq
  - https://developers.tiktok.com/blog/tiktok-sans-open-source
  - https://cellphones.com.vn/sforum/top-7-font-viet-hoa-dep-dac-sac-danh-cho-designer
  - https://fptshop.com.vn/tin-tuc/for-gamers/utm-avo-204736
  - https://www.fontspace.com/utm-ong-do-gia-font-f30417
  - https://www.fontspace.com/utm-thuphap-thien-an-font-f22678
  - https://www.vng.com.vn/guidelines/brand/typography.html
  - https://www.submagic.co/blog/how-to-make-captions-like-mrbeast
---
# Bản quyền font khi làm video

Không phải lời khuyên pháp lý — đây là quy tắc làm việc của vedit (cập nhật 2026-10-31).

**Tóm tắt:** chỉ dùng font có giấy phép mở rõ ràng (SIL OFL 1.1, Apache 2.0, Ubuntu Font License — toàn bộ
`assets/fonts` là OFL). Video làm bằng font OFL được dùng thương mại, không cần ghi công. Font "Việt hoá" (SVN-,
UTM, iCiel…) và font tải từ trang "font miễn phí" không kèm file giấy phép → coi là **không rõ giấy phép**, không
dùng cho video của khách hàng, quảng cáo hay kênh kiếm tiền.

## OFL 1.1 — 5 điều kiện (trích từ file OFL đi kèm font)

1. Không bán riêng font (bản gốc hay bản sửa) như một sản phẩm độc lập.
2. Được phân phối lại / đóng gói kèm phần mềm, với điều kiện mỗi bản có thông báo bản quyền và giấy phép.
3. Bản sửa đổi không được dùng **Reserved Font Name** (RFN), trừ khi có văn bản cho phép.
4. Không dùng tên tác giả để quảng bá bản sửa đổi.
5. Font phải giữ giấy phép OFL — nhưng "yêu cầu này **không áp dụng cho tài liệu tạo ra bằng font**" → video,
   ảnh bìa, thumbnail làm bằng font OFL không bị ràng buộc OFL.

OFL FAQ: dùng font OFL cho tác phẩm đồ hoạ (có nêu ví dụ chữ tiêu đề video) là được, và tác phẩm không trở thành
OFL; không bắt buộc ghi công (tác giả vẫn quý nếu có). Google Fonts FAQ: dùng thương mại được, kể cả trong sản phẩm
bán ra và trong logo; giấy phép cụ thể theo từng font (đa số OFL). Ngoại lệ: Product Sans là font riêng của Google.
TikTok Sans được TikTok mở mã nguồn theo OFL 1.1 (7/2025).

## Áp vào repo vedit

- `assets/fonts` được commit lên git = **phân phối lại** → mỗi họ font phải có `OFL-<Tên>.txt` đi kèm (đã có đủ
  15 + 3 họ cũ). Mọi file font còn nhúng sẵn câu giấy phép OFL trong bảng `name` (ID 13/14).
- 6 họ là **bản sửa đổi** (bản static tạo từ font variable): Montserrat, TikTok Sans (đổi thêm tên bỏ "36pt"),
  Phudu, Baloo 2, Playpen Sans, Shantell Sans. Cả 6 **không có RFN** nên giữ tên gốc hợp lệ; vẫn phát hành theo OFL.
- Họ **có RFN** — chỉ dùng nguyên bản, muốn subset/chuyển định dạng/sửa thì phải đổi tên: Lobster ("Lobster"),
  Paytone One ("Paytone", "Paytone One"), Yeseva One ("Yeseva"). Cũng có RFN nên không tạo bản static: Playfair
  Display ("Playfair Display"), Dancing Script ("Dancing Script").
- Không đóng gói font vào template/preset rồi bán riêng font.

## Font "Việt hoá" và font không rõ nguồn

- Font Việt hoá là bản thêm dấu tiếng Việt vào một font có sẵn → quyền dùng phụ thuộc **giấy phép font gốc** cộng
  điều khoản của người Việt hoá. Ví dụ: Gilroy gốc là font bán trên Fontspring; VNG ghi SVN-Gilroy là font thương
  hiệu của họ (doanh nghiệp tự lo giấy phép — trang không nêu điều kiện).
- Sforum (CellphoneS) khuyên chỉ dùng font Việt hoá cho mục đích cá nhân, dùng cho thương hiệu thì mua bản quyền.
  FPT Shop: một số font UTM có điều kiện sử dụng riêng, dùng thương mại phải đọc kỹ giấy phép.
- Mỗi font một kiểu: trên FontSpace, "UTM Ong Do Gia" ghi Freeware, **Non-Commercial**; "UTM ThuPhap Thien An" ghi
  Public Domain → không suy ra cả dòng UTM/SVN là "miễn phí".
- Việt hoá một font **OFL** là bản sửa đổi hợp lệ nếu giữ OFL, kèm file giấy phép và không dùng RFN; Việt hoá một
  font **thương mại** mà không có phép của chủ font gốc thì bản Việt hoá cũng không cho bạn quyền dùng.
- Font "giống người nổi tiếng": caption MrBeast hay được gán cho Komika Axis, Hormozi cho "The Bold Font" — thông tin
  giấy phép trên các trang tổng hợp mâu thuẫn ("personal use"/"free commercial"). Dùng bản thay thế OFL bên dưới.
- Font có sẵn trong app (CapCut, TikTok): dùng trong app đó theo điều khoản của app; muốn dùng ngoài app thì tìm bản
  OFL tương đương (TikTok Sans đã mở OFL).

## Bảng thay thế OFL có tiếng Việt

| Thường thấy | Thay bằng (trong `assets/fonts`) |
|---|---|
| SVN-Gilroy, SVN-Poppins, UTM Avo (sans hình học) | `Montserrat`, `Be Vietnam Pro`, `TikTok Sans` |
| UTM Bebas, SVN-Bebas Neue (Bebas Neue gốc là OFL nhưng không có tiếng Việt) | `Phudu`, `Barlow Condensed`, `Anton` |
| "The Bold Font" (kiểu Hormozi) | `Montserrat Black`, `Anton` |
| Komika Axis (kiểu MrBeast) | `Bangers` |
| Font viết tay Việt hoá (UVF, MTD…) | `Playpen Sans`, `Mali`, `Shantell Sans`, `Pacifico` |
| Serif thời trang Việt hoá | `Prata`, `Yeseva One` |

## Checklist trước khi thêm một font

1. Nguồn chính thức: google/fonts, repo GitHub của tác giả, trang foundry.
2. Có file giấy phép và đọc nó: OFL / Apache / UFL → được. "Personal use only", "Non-commercial", "Demo",
   "Free for personal use" → không dùng cho video kiếm tiền hay của khách.
3. Sẽ sửa font (tạo static, subset, Việt hoá) → kiểm tra RFN trong dòng copyright của OFL.
4. Đặt `OFL-<Tên>.txt` cạnh font, ghi nguồn trong `assets/fonts/README.md`.
5. Kiểm tra tiếng Việt (`fc-query` có `vi`) và render thử (ghi chú "Thư viện font của vedit").

## Áp dụng vào vedit

1. Chưa có kiểm tra giấy phép → `vedit doctor`/`validate` liệt kê font dùng trong plan, đọc name ID 13/14 và báo
   font không có `OFL-*.txt`/giấy phép mở đi kèm → dễ.
2. Khi libass phải mượn font dự phòng (FreeSerif, Unifont — thường do emoji hoặc ký tự lạ) thì không ai biết →
   đọc log `fontselect` sau render và cảnh báo → dễ.
3. Tuỳ chọn ghi "credits" font vào `script.md` (không bắt buộc với OFL, nhưng lịch sự với tác giả) → dễ.
