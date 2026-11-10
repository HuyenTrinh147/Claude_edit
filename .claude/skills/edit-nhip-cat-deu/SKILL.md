---
name: edit-nhip-cat-deu
description: Công thức nhịp cắt đều ~1.0–1.5 s, cảnh mở ≤ 1 s, bám lưới beat nhạc, học từ 3 video TikTok mẫu. Dùng khi dựng clip ngắn 8–15 s kiểu showcase/tour (quán, sản phẩm) cần cảm giác nhanh, đều, không chữ.
argument-hint: <số giây tổng> [bpm]
---

**Chỉ là một tuỳ chọn**: dùng sau khi người dùng đã chọn hướng dựng và hướng đó hợp với chiêu này; không ép vào mọi video. Nếu không hợp, bỏ qua.

## Khi nào dùng
Video 8–15 s, nhiều cảnh quay đẹp (quán, đồ ăn, sản phẩm), ít thoại, nhạc nền là chính.

## Số đo thật
ASL 1.22 s (v1, 8 cảnh 0.90–1.47), 1.58 s (v3), 1.78 s kể cả cảnh giải thích 4.3 s (v2). Cảnh đầu luôn ≈ 1.0 s
(0.98 / 1.05 / 0.98). v3: điểm cắt rơi trong ±0.08 s lưới beat ~0.54 s (≈ 111 BPM).

## Các bước
1. Tổng  giây; chia thành N = tổng / 1.2 cảnh (10 s -> 8 cảnh). Cảnh 1 dài 0.9–1.0 s, các cảnh sau 0.9–1.5 s (không đều tuyệt đối: đừng cho 2 cảnh liền bằng nhau đến từng frame).
2. Nếu có BPM: độ dài cảnh = bội số của một nhịp (0.54 s ở 111 BPM -> 1.08 s hoặc 1.62 s). Đặt `clips[i].end - start` / `speed` cho khớp; ưu tiên nhạc từ `vedit music` đúng BPM.
3. Mỗi cảnh một chuyển động cùng hướng với cảnh sau (đi tới -> đi tới) để cắt "ẩn". Chuyển cảnh: cắt cứng; chỉ 1–2 chỗ `transition: {type: "hblur", duration: 0.2}` hoặc `smoothleft`.
4. Không chữ chèn nếu chủ đề là hình ảnh; nếu cần, tối đa 1 dòng ở cảnh cuối.
5. Cảnh cuối là cận món/đồ uống/sản phẩm, 1.5–2.5 s, rồi dừng hẳn (không CTA dài).

## Lỗi hay gặp
Cắt đều tăm tắp -> máy móc; để cảnh đầu 2 s+ -> mất hook; cắt lệch beat > 0.1 s.

Nguồn: ref-mim-1..3 (mẫu 3 video, chưa phải cả kênh; quan sát 2026-11). Chi tiết số đo: `vedit kb show techniques/so-do-nhip-cat-toc-do-am-thanh-3-video-mau-ref-mim`.
