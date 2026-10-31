---
title: Màu sắc: grading theo thể loại và đồng bộ giữa các cảnh
category: techniques
tags: [màu, color grading, color correction, lut, tông da, shot matching, đồ ăn, vibrance, signalstats, ffmpeg]
updated: 2026-10-31
sources:
  - https://noamkroll.com/the-best-order-of-operations-for-color-grading-why-it-makes-all-the-difference/
  - https://workflow.frame.io/guide/primary-color-correction
  - https://josephnilo.com/blog/color-grading-in-premiere-pro-the-ultimate-guide-to-the-lumetri-color-panel/
  - https://www.vidio.ai/en-AU/blog/article/ways-to-achieve-consistent-color-across-your-video-project
  - https://imagen-ai.com/valuable-tips/color-grading-tips-for-food-photographers/
  - https://imagen-ai.com/valuable-tips/color-grading-best-practices-for-food-photographers/
  - https://foodshot.ai/blog/food-color-grading
  - https://uppbeat.io/blog/motion-graphics/color-grading/how-to-color-grade-your-videos
  - https://larryjordan.com/articles/the-secret-to-setting-skin-colors-accurately/
  - https://blog.frame.io/2020/10/05/skin-tones-in-davinci-resolve/
  - https://filmdaft.com/what-is-a-vectorscope-definition/
  - https://filmora.wondershare.com/video-creative-tips/aesthetic-daily-vlog-filters.html
  - https://filmora.wondershare.kr/video-editing-tips/best-vlog-subtitle-font.html
  - https://spliceapp.com/blog/cinematic-b-roll-editing-beginners-guide/
  - https://github.com/FFmpeg/FFmpeg/blob/release/6.1/doc/filters.texi
  - https://github.com/browser-use/video-use/blob/main/helpers/grade.py
---
# Màu sắc: grading theo thể loại và đồng bộ giữa các cảnh

## 1. Thứ tự làm (các nguồn thống nhất)
1. Quản lý màu & đọc scope trước khi chỉnh bằng mắt.
2. **Sửa kỹ thuật**: phơi sáng/tương phản → cân bằng trắng.
3. Tông da (nếu có người).
4. **Đồng bộ cảnh (shot matching)**: chọn một frame chuẩn đẹp nhất, chỉnh các cảnh khác theo nó; nhóm clip theo
   ánh sáng/địa điểm.
5. **Look sáng tạo / LUT** cuối cùng, nhẹ tay. Look phủ lên footage chưa sửa sẽ *khuếch đại* lỗi.

## 2. Đồ ăn
- Neo trung tính bằng vật trắng/xám (đĩa trắng, tường, thẻ xám): sốt kem không được ngả xanh hay vàng.
- **Vibrance trước saturation** (vibrance tha các vùng đã bão hoà); chỉnh theo HSL thay vì tăng bão hoà toàn cục —
  đẩy ấm toàn cục làm rau xanh "đục bùn".
- Giữ đỏ/cam/vàng ngon nhưng **dừng trước khi trông như nhựa** (lòng đỏ trứng cam đậm, không neon).
- Độ ấm theo món: ấm cho bánh nướng, đồ quay, món "comfort"; tông tối "moody" (bóng sâu + highlight ấm) cho comfort
  food/fine dining.
- Chỉnh một frame "hero" rồi áp cho cả buổi quay; LUT nên dùng ở 60–80% cường độ rồi chỉnh tương phản/bão hoà (gợi
  ý từ một blog, không phải chuẩn).

## 3. Tông da
- Đường skin tone trên vectorscope nằm giữa đỏ và vàng, khoảng **vị trí 11 giờ**; mọi màu da cân trên đường này,
  độ sáng/bão hoà là chuyện riêng. Cô lập vùng da (mask/zoom) khi đọc scope.
- Look cách điệu có thể cố ý kéo da lệch đường; quyết định hướng look trước, rồi kiểm tra da còn đọc đúng ý không;
  mask da để đẩy nền mà giữ mặt.

## 4. Look theo thể loại (tổng hợp)
| Thể loại | Hướng màu |
|---|---|
| Đồ ăn tự nhiên | trắng trung tính, vibrance nhẹ, đỏ/vàng ấm có chọn lọc, S-curve nhẹ, nét vừa |
| Comfort / moody | bóng sâu, highlight ấm, vignette nhẹ |
| Vlog café / cozy | tương phản mềm, nâu đậm ở vùng tối, grain nhẹ (trên điện thoại grain gần như không thấy) |
| Vlog thẩm mỹ Hàn | pastel, mềm, "dreamy"; chữ phụ đề tông pastel; giữ một filter cho cả series |
| Cinematic | 24 fps, grain vừa phải, tương phản điện ảnh |
| Tech / review | sạch, trung tính, tương phản rõ |

## 5. Đồng bộ cảnh bằng số đo (ffmpeg)
Đo trung bình mỗi clip: `ffmpeg -ss S -t D -i in.mov -vf "scale=180:320,signalstats,metadata=print:file=-" -f null -`
rồi lấy trung bình `YAVG` (sáng), `UAVG`/`VAVG` (lệch xanh–vàng/đỏ–lục), `SATAVG`.

**Đo trên nguồn cà pháo (2026-10-31)**, 9 đoạn dùng trong bản dựng: Y 96,9 → 118,5; V 132,1 → 138,9 (các cảnh sau
ấm hơn); SAT 7,6 → 17,5. Hai cú cắt nhảy sáng rõ: hook (Y 111,7) → đặt hũ (96,9) và cắt ớt (114,9) → đổ tỏi gừng
(100,7). Một phần do nội dung (mặt đá đen), nhưng cân phơi sáng từng clip sẽ giảm "nháy" khi cắt.

Sửa từng clip: `eq=brightness=…:gamma=…`, `colorbalance`, `colorlevels`; tự cân trắng: `colorcorrect=analyze=average`
(hoặc `median`), `grayworld`. Xem thêm `ffmpeg/video-use-chinh-mau-tu-dong-bang-signalstats-va-preset`.

## 6. Bộ lọc ffmpeg cho look (đã kiểm tra tham số trên 6.1)
```
colortemperature=temperature=5600:mix=0.5:pl=1     # ấm/lạnh (K), pl giữ độ sáng
vibrance=intensity=0.25                            # -2..2
selectivecolor=reds='0 0 0 -0.08':yellows='0 0 0.06 -0.04'
curves=all='0/0 0.25/0.22 0.5/0.5 0.75/0.79 1/0.97' # S-curve nhẹ, nén highlight
lut3d=file=look.cube:interp=tetrahedral
```
LUT ở 70% cường độ (đã đo: kênh R/B ra đúng 70% quãng thay đổi):
```
[v]format=gbrp,split[o][l];[l]lut3d=file=look.cube:interp=tetrahedral[lg];
[lg][o]blend=all_mode=normal:all_opacity=0.7[graded]
```
**Bài học khi thử**: đẩy `colortemperature` toàn cục (mix 0.6) làm tường trắng và hũ thuỷ tinh ngả kem → ấm nên đi
qua `selectivecolor`/vibrance vào đỏ–vàng, giữ vùng trắng trung tính.

## Áp dụng vào vedit
- Đang có: `look.preset` toàn cục (`warm_food` = eq bão hoà 1.22 + colorbalance + unsharp; `bright_clean`, `film`,
  `moody`, `vivid`, `bw`), `vignette`, `grain`. Không có chỉnh từng clip, LUT, cường độ look.
- Đề xuất: (1) `Clip.color: {exposure, temperature, tint, saturation}` + chế độ `"auto_match": true` (đo signalstats,
  kéo YAVG/UAVG/VAVG về clip chuẩn); (2) `look.lut` + `look.intensity` (0–1) qua `lut3d` + `blend`; (3) preset
  `food_natural` (vibrance + selectivecolor + S-curve, không đẩy nhiệt độ toàn cục); (4) bộ LUT miễn phí trong
  `assets/luts/` có giấy phép rõ.
- Agent 3 nên đo signalstats các clip trước khi chọn look, ghi vào `notes` clip nào lệch sáng >10 mức Y.
- Xem thêm: `ffmpeg/claude-video-editor-grade-mau-tu-dong-va-tonemap-hdr`.

_Ghi chú nguồn: trang ngoài GitHub đọc qua trích đoạn tìm kiếm; tham số filter đọc trực tiếp từ tài liệu FFmpeg 6.1
trên GitHub; số đo do Agent 1 chạy._
