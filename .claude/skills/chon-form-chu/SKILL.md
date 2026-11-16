---
name: chon-form-chu
description: Chọn và dùng thư viện form chữ của vedit (`vedit styles`, trường `style` trong texts): bảng ghép kiểu chữ theo thể loại video, quy tắc phân cấp (1 tiêu đề + 1 nhãn + 1 phụ đề, tối đa 2 họ font), thời gian đọc, vùng an toàn, rồi kiểm bằng `vedit textcheck`. Dùng khi người dùng muốn chọn kiểu chữ, đổi giao diện chữ hoặc thêm form chữ mới cho video.
argument-hint: [slug dự án] [thể loại / tâm trạng video]
---

Yêu cầu: $ARGUMENTS

Trao đổi bằng tiếng Việt.

1. Nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh`.
2. Xem thư viện: `vedit styles` (danh sách), `vedit styles <tên>` (chi tiết + ví dụ JSON), ảnh mẫu
   `assets/styles/gallery.jpg` (gửi người dùng bằng SendUserFile khi họ cần nhìn để chọn). Cần ảnh mới sau khi sửa
   preset: `vedit styles --gallery assets/styles/gallery.jpg`.
3. Ghép theo thể loại (chọn **một bộ**, không trộn nhiều bộ):

   | Thể loại / tâm trạng | Tiêu đề | Nhãn / số | Phụ đề | Ghi chú |
   |---|---|---|---|---|
   | Đồ ăn, mèo, pastel, kể chuyện mềm | `the-pill-kem` | `nhan-pill-nho` | `phu-de-nho-trang` | nền kem giữ chữ đọc được trên mọi cảnh |
   | Công thức / hướng dẫn đếm bước | `tieu-de-anton-pill-kem` | `so-buoc-anton-vang` + `nhan-pill-nho` | `phu-de-nho-trang` | số bước lớn, tên bước nhỏ vào trễ 0.3 s |
   | Liệt kê âm thanh / mẹo / công cụ | `tieu-de-trang-vien-den` | `nhan-so-vang` | `phu-de-nho-trang` | thêm `khung-tim-am-thanh` (xem skill `edit-mau-am-thanh-danh-so`) |
   | Giáo dục, động lực, kể nhanh | `hormozi-nhan-manh` | — | — | bật từng từ, chữ HOA ngắn |
   | Hài, phản ứng | `hai-bangers-vang` | — | `phu-de-nho-trang` | đi kèm punch / shake |
   | Bán hàng, giá, khuyến mãi | `khuyen-mai-anton-do` | `nhan-pill-nho` | `phu-de-nho-trang` | số liệu phải có thật |
   | Cảm xúc, làm đẹp, trích dẫn | `trich-dan-prata` | — | — | nét mảnh: cần viền hoặc nền tối |
   | Hướng dẫn quay màn hình (hiệu ứng) | `tieu-gradient-lon-vang` + `chu-script-cam-nho` | `chu-thich-pill-trang` | — | xem skill `edit-huong-dan-nen-xanh-tieu-de-lon` |
   | Hướng dẫn quay màn hình (intro / template) | `buoc-in-hoa-trang-den` | — | — | từ khoá vàng = text thứ hai; skill `edit-huong-dan-chu-buoc-in-hoa` |
   | Hướng dẫn có người dẫn | `tieu-de-vang-trich-dan` | — | `chu-thich-nghieng-viet-tay` | skill `edit-huong-dan-nguoi-dan-nen-mo` |
   | Game HUD | dùng `hud` (`hud_theme`), không dùng `style` | | | xem `giao-dien-game-hud-bam-vat-cho-video` |

4. Luật phân cấp: mỗi video 1 form tiêu đề + 1 form nhãn + 1 form phụ đề, tối đa 2 họ font; mỗi lần cắt chỉ 1 thứ chữ
   mới; chữ không chép lại lời thoại; thời gian hiện ≥ ký tự / 15 + 0.5 s; tâm chữ trong `canvas.safe_area`
   (TikTok: `[0.05, 0.1, 0.85, 0.8]`).
5. Dùng trong EditPlan: `{"text": "...", "start": 2.0, "end": 3.5, "style": "nhan-so-vang"}`; chỉ ghi thêm trường muốn
   khác preset (ví dụ `y`, `size`, `color`) — trường ghi rõ luôn thắng.
6. Kiểm: `vedit validate <slug>` (font, ký tự thiếu) → `vedit textcheck <slug>` → xem khung bằng
   `vedit frame <slug> <giây> --source preview --grid`.
7. **Thêm form chữ mới**: thêm vào `STYLES` trong `vedit/textstyles.py` (font có trong `assets/fonts`, tên đúng như
   `thu-vien-font-cua-vedit`; không ký tự ngoài font), chạy `pytest tests/test_beat_textcheck.py`, tạo lại ảnh mẫu, ghi
   vào `knowledge/typography/thu-vien-form-chu-cua-vedit-preset-texts-style.md`. Chỉ thêm form đã render được và có nguồn (video đã dựng
   hoặc video mẫu), không thêm theo cảm giác.
8. Người dùng khen / chê kiểu chữ → `vedit note <slug> "..." --kind "phản hồi"` và cập nhật `profile/gu-nguoi-dung.md`.
