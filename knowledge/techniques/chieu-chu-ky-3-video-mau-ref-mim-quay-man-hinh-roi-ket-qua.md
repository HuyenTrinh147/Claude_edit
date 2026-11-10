---
title: Chiêu chữ ký của 3 video mẫu ref-mim: quay màn hình app dựng rồi ra kết quả, nhân bản vật, nền mờ
category: techniques
tags: [tiktok, capcut, screen-recording, nhan-ban-vat, blur-fill, mau-3-video]
updated: 2026-11-10
sources:
  - người dùng tải lên: ref-mim-1..3 (quan sát 2026-11)
---
# Chiêu chữ ký của 3 video mẫu ref-mim

Mẫu chỉ có 3 video, watermark ghi `@gmvisuals9029` / `@tmthntrung` (không phải @editwithmim) — xem cảnh báo ở
`techniques/so-do-nhip-cat-toc-do-am-thanh-3-video-mau-ref-mim`. Số đo nhịp/loudness nằm ở note đó.

## Mẫu chung
1. **Không có chữ chèn (text overlay) nào do người dựng thêm** ở cả 3 video (chỉ chữ giao diện app trong cảnh quay
   màn hình và watermark TikTok). Truyền đạt bằng hình, không bằng chữ — khác hẳn phong cách Hormozi.
2. **Cảnh đầu ≤ 1 s** ngay vào vấn đề; không logo/intro.
3. **Cắt đều ~1.0–1.5 s**, cảnh quay vật tĩnh ở cự ly gần, bố cục dọc.
4. Hầu như không có bình luận/lời thoại; âm thanh là nhạc + tiếng động, to (-5…-12 LUFS).
5. Kết thúc đột ngột (không CTA do người dựng) — phần cuối chỉ là thẻ TikTok gắn tự động.

## Ba công thức theo từng video
**ref-mim-1 (quán cà phê, 9.8 s)** — "tour quán ấm áp": 8 cảnh ~1.2 s. Khung dọc nhưng ảnh chính **hẹp hơn khung**:
vùng hình rộng ≈ x 0.20–0.80 (60% bề ngang), hai bên là **nền mờ phóng to** của chính cảnh (fit blur). Màu **ấm
vàng/cam, tối (low-key), tương phản vừa**, bóng đèn vàng. Góc dưới chồng **đồ thị đường cong tốc độ + bảng keyframe**
(ảnh chụp màn hình CapCut) ở y≈0.55–0.95 — mỗi cảnh đổi đường cong khác: U / vòm / hai gợn. Cắt theo chuyển động,
nhoè ở cuối cảnh (8.85 s). Cảnh cuối (9.33 s) là cận ly nước: kết bằng món ăn/đồ uống.

**ref-mim-2 (chai trà, 10.7 s)** — "dạy hiệu ứng": 0–4.0 s quay màn hình CapCut với đường keyframe (đường đỏ dọc, dải
cam dưới timeline, kim cương keyframe) trên cảnh chai đang rơi/nhân bản; 4.0–10.7 s là **kết quả**: 1 chai (4.38 s) →
3 chai (5.18 s) → 5 chai (5.98 s) → 2 chai cận (8.37 s) → 5 chai (9.96 s); xen nhoè nhoè chuyển động ở 6.77 và 9.16 s.
Màu lạnh, ít bão hoà (trời nhiều mây, toà nhà xám), chai đỏ là điểm nhấn.

**ref-mim-3 (lon + chai, 11.0 s)** — "dạy bám vật / nhân bản": 0–3.9 s quay màn hình app dựng điện thoại (chọn 4 clip,
chế độ "ổn định bám vật 稳定跟踪", thanh tiến trình xanh), rồi kết quả 3.95–9.4 s: chai nước xanh và lon cola đỏ
xuất hiện lần lượt trên cùng mặt bàn, đổi cỡ cảnh từ cận chai (4.52 s) → cả hai (5.34 s) → cận lon (6.16 s) → cận
chai (6.99 s) → hai vật (7.81 s) → rộng cả bàn (8.63–9.45 s); **gag cuối** 10.27 s: cắt sang người ngủ trên ghế (cú
"đảo ngữ cảnh" bất ngờ, 1.0–1.7 s). Màu trung tính, ánh sáng huỳnh quang văn phòng, không grade.

## Chiêu chữ ký (có ở ≥ 2/3 video)
- **A. "Quay màn hình app rồi trả kết quả"** (v2, v3, một phần v1): hơn 1/3 thời lượng đầu là màn hình dựng (timeline,
  keyframe) → người xem vừa thấy cách làm vừa thấy kết quả. Là format hướng dẫn nhanh, không phải clip thẩm mỹ thuần.
- **B. Nhân bản/xuất hiện vật theo từng nhịp** (v2, v3): vật được "thêm" một cái mỗi ~1 s, cắt khớp nhịp.
- **C. Cắt đều ~1.2–1.5 s + cảnh mở ≤ 1 s** (cả 3).
- **D. Nền mờ phóng to khi ảnh không phủ khung** (v1; v2 cũng có lớp nhoè khi chuyển).
- **E. Gag đảo ngữ cảnh ở cuối** (v3 duy nhất — chỉ 1/3, không tính chữ ký).

## Áp dụng vào vedit
| Chiêu | vedit đã có? | Thiếu / đề xuất |
|---|---|---|
| Cắt đều ~1.2 s | có (clip + `vedit analyze`) | công cụ tự dựng lưới nhịp từ nhạc (ưu tiên 1) |
| Nền mờ (fit blur) | có `Clip.fit="blur"` | ảnh chính chỉ rộng 60% khung: thêm `fit_scale` (ưu tiên 3) |
| Speed ramp cong | chỉ `speed` hằng số | `speed_curve` (ưu tiên 2) |
| Quay màn hình app → kết quả | dùng được: clip quay màn hình + clip kết quả | khuôn mẫu ở skill `edit-man-hinh-roi-ket-qua` (ưu tiên 4) |
| Nhân bản vật theo nhịp | một phần: lặp clip + `ImageOverlay` (cắt vật ra bằng ảnh PNG) | bám vật (`vedit track`) đã có; thiếu tách nền/mask (ưu tiên 5) |
| Gag cuối đảo ngữ cảnh | có (clip cuối 1.0–1.7 s) | không cần |
| Đồ thị tốc độ chồng góc | không | thấp (chỉ khi làm video dạy) |

Skill tạo ra từ ghi chú này: `edit-nhip-cat-deu`, `edit-toc-do-cong-chu-u`, `edit-man-hinh-roi-ket-qua`,
`edit-nhan-ban-vat-theo-nhip`, `edit-nen-mo-phong-to`. Chỉ dùng như tuỳ chọn sau khi người dùng đã chọn hướng dựng.
