---
title: Thư viện form chữ của vedit (preset texts[].style)
category: typography
tags: [form chữ, preset, style, texts, thư viện, tiêu đề, nhãn, phụ đề]
updated: 2026-11-16
sources:
  - vedit/textstyles.py
  - video mẫu ref-mim-4 (2026-11)
  - projects canh chua, mèo búa thảo mộc (đã giao)
---
# Thư viện form chữ của vedit (preset texts[].style)

Form chữ = preset dựng sẵn cho `TextOverlay`. Trong EditPlan ghi `{"text": "1. Xắt xắt xắt", "start": 3.0, "end": 4.5,
"style": "nhan-so-vang"}`; mọi trường ghi rõ cạnh `style` (size, y, color...) thắng preset. Nguồn: `vedit/textstyles.py`.
Xem: `vedit styles` (danh sách) · `vedit styles <tên>` (chi tiết) · ảnh mẫu `assets/styles/gallery.jpg`
(tạo lại: `vedit styles --gallery assets/styles/gallery.jpg`).

## 12 form chữ (đều đã render được; font nằm trong `assets/fonts`)

| `style` | Font · cỡ | Nhìn | Dùng khi | Nguồn |
|---|---|---|---|---|
| `tieu-de-trang-vien-den` | Shantell Sans · 96 | trắng, viền đen 7, y 0.28 | hook / tiêu đề cả video (thêm sao lấp lánh bằng `graphics`) | video mẫu ref-mim-4 |
| `nhan-so-vang` | Baloo 2 · 84 | vàng #FFD93D, viền nâu tối, y 0.12 | đánh số mục: "1. Xắt xắt xắt" | ref-mim-4 |
| `phu-de-nho-trang` | Be Vietnam Pro · 52 | trắng nhỏ, y 0.70, fade | nhắc / CTA phụ: "lưu ngay nhé" | ref-mim-4 |
| `khung-tim-am-thanh` | Be Vietnam Pro · 38 | khung tối #1B1C24 94 %, y 0.66 | ô tìm âm thanh dưới hình (2 dòng) | ref-mim-4 |
| `the-pill-kem` | Baloo 2 · 100 | tím than trên pill kem, bounce, y 0.14 | dẫn truyện mềm, đồ ăn, pastel | dự án mèo búa, BẾP VR |
| `so-buoc-anton-vang` | Anton · 190 | vàng, viền tím than 8, y 0.20 | số bước 1/6 … 6/6 | dự án canh chua |
| `tieu-de-anton-pill-kem` | Anton · 150 | tím than trên pill kem, y 0.30 | tiêu đề / CTA khi nền rối | dự án canh chua |
| `nhan-pill-nho` | Be Vietnam Pro · 64 | tím than trên pill kem, slide_up | tên bước / nguyên liệu | dự án canh chua |
| `hormozi-nhan-manh` | Montserrat · 96 | trắng viền đen 9, bật từng từ | giáo dục, động lực | kieu-chu-trend-tren-tiktok-reels |
| `hai-bangers-vang` | Bangers · 140 | vàng viền đỏ, nghiêng −6° | hài, cảm thán | thu-vien-font-cua-vedit |
| `khuyen-mai-anton-do` | Anton · 130 | trắng trên băng đỏ nghiêng | giá, khuyến mãi | thu-vien-font-cua-vedit |
| `trich-dan-prata` | Prata · 78 | trắng kem, viền nâu 3, fade | trích dẫn, làm đẹp | thu-vien-font-cua-vedit |

## Cách ghép (xem skill `chon-form-chu`)
- Mỗi video: 1 form tiêu đề + 1 form nhãn + 1 form phụ đề, tối đa 2 họ font; chọn một bộ theo thể loại, không trộn.
- Bộ đã chạy thật: đồ ăn pastel = `the-pill-kem` + `nhan-pill-nho`; công thức = `tieu-de-anton-pill-kem` +
  `so-buoc-anton-vang` + `nhan-pill-nho`; liệt kê âm thanh = `tieu-de-trang-vien-den` + `nhan-so-vang` +
  `khung-tim-am-thanh` + `phu-de-nho-trang`.
- Tên font phải đúng như `thu-vien-font-cua-vedit`; không dùng ký tự ngoài font (ví dụ "♪" làm `vedit validate` báo thiếu
  ký tự — bài kiểm của thư viện bắt lỗi này).
- Sau khi dùng: `vedit textcheck <slug>` (thời gian đọc ≥ ký tự / 15 + 0.5 s, tối đa 2 dòng, vùng an toàn).

## Giới hạn
Preset chỉ giữ giao diện của một dòng chữ. Sao lấp lánh, biểu tượng dấu trang, nút "+" xanh của khung tìm âm thanh phải
thêm bằng `graphics` / `images`. Màu viền trắng-trên-nâu của ảnh mẫu khó thấy: thử trên cảnh thật trước khi chốt.
