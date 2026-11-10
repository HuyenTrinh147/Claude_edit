---
name: edit-man-hinh-roi-ket-qua
description: Cấu trúc video mẹo dựng ngắn 10–13 s - mở bằng 1–4 s quay màn hình app dựng (keyframe/timeline) rồi trả kết quả cắt nhanh, không chữ. Dùng khi người dùng muốn video hướng dẫn hiệu ứng nhanh kiểu CapCut.
argument-hint: <tên hiệu ứng> <clip quay màn hình> <clip kết quả>
---

**Chỉ là một tuỳ chọn**: dùng sau khi người dùng đã chọn hướng dựng và hướng đó hợp với chiêu này; không ép vào mọi video. Nếu không hợp, bỏ qua.

## Khi nào dùng
Người dùng có (hoặc cần) video quay màn hình thao tác trong app và kết quả cuối. Muốn hook "ra mà không cần giải thích".

## Số đo
v2: màn hình 0–3.98 s (3 cảnh 1.05 / 1.13 / 1.80) -> kết quả 3.98–10.68 s. v3: màn hình 0–3.95 s (cảnh 0.98 + 2.97) -> kết quả 3.95–11.05 s. Màn hình chiếm ~35% độ dài. Không chữ chèn của người dựng.

## Các bước
1. Clip 1: quay màn hình, `fit: "cover"` (nếu tỉ lệ khác, `fit: "blur"`), 0.9–1.1 s đầu đã thấy giao diện + vật; clip 2–3 = đoạn thao tác chính (1.0–3.0 s), `speed: 1.3–2.0` để rút gọn.
2. Nhấn điểm cần nhìn bằng `graphics`: `callout` (mũi tên/vòng) ở toạ độ nút bấm, 0.6–1.0 s; không viết đoạn chữ dài.
3. Chuyển sang kết quả bằng cắt cứng hoặc `transition hblur 0.15 s` đúng nhịp; kết quả cắt đều ~1.2 s (xem `edit-nhip-cat-deu`).
4. Kết thúc: gag/đảo ngữ cảnh 1.0–1.7 s (v3) hoặc dừng ở cảnh đẹp nhất; không cần CTA.
5. Âm thanh: một bản nhạc to đều (v2 -5 LUFS, v3 -12 LUFS, LRA < 4); với vedit giữ `loudnorm` mặc định, không cần làm to hơn.

## Lỗi hay gặp
Màn hình quay có UI/số điện thoại cá nhân (v3 hiện giờ và thông báo) -> che/crop trước khi đăng; quá nhiều chữ app nhỏ không đọc được trên điện thoại -> zoom (`zoom`) vào nút thao tác.

Nguồn: ref-mim-1..3 (mẫu 3 video, chưa phải cả kênh; quan sát 2026-11). Chi tiết số đo: `vedit kb show techniques/so-do-nhip-cat-toc-do-am-thanh-3-video-mau-ref-mim`.
