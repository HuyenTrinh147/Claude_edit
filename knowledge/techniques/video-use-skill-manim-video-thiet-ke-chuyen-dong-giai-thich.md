---
title: video-use: Skill manim-video, thiết kế chuyển động giải thích
category: techniques
tags: [video-use, manim, 3blue1brown, explainer, motion design, opacity, nhịp, typography, bố cục, spotlight]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/README.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/scripts/setup.sh
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/animation-design-thinking.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/production-quality.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/visual-design.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/scene-planning.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/rendering.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/animations.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/decorations.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/mobjects.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/equations.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/graphs-and-data.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/camera-and-3d.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/updaters-and-trackers.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/paper-explainer.md
  - https://github.com/browser-use/video-use/blob/main/skills/manim-video/references/troubleshooting.md
  - https://raw.githubusercontent.com/NousResearch/hermes-agent/main/skills/creative/manim-video/SKILL.md
---
# video-use: Skill manim-video, thiết kế chuyển động giải thích

`skills/manim-video/` chiếm 17/36 file của repo, vendored từ NousResearch/hermes-agent (MIT, tác giả
"SHL0MS, Hermes Agent"). Đây là pipeline làm video giải thích kiểu 3Blue1Brown bằng Manim Community Edition
(tài liệu thử với v0.20.1). Trong video-use, Manim là một engine để dựng *slot animation*. Phần giá trị nhất để
mang sang vedit là các **nguyên tắc thiết kế chuyển động**, áp dụng được cho đồ hoạ ASS.

## Pipeline và lệnh
`PLAN → CODE → RENDER → STITCH → AUDIO (tuỳ chọn) → REVIEW`
1. Viết `plan.md`: mạch truyện, danh sách cảnh, bảng màu, lời dẫn.
2. Viết `script.py`: mỗi cảnh một class, render độc lập được.
3. Render:
   - `manim -ql script.py Scene1 Scene2` cho nháp (854×480, 15 fps);
   - `-qm` (720p30) để xem chữ;
   - `-qh` (1080p60) cho bản cuối;
   - `manim -ql --format=png -s script.py Scene2` để lấy ảnh tĩnh khung cuối;
   - khung dọc: `--resolution 1080,1920`.
4. Ghép cảnh: `ffmpeg -f concat -safe 0 -i concat.txt -c copy final.mp4`.
5. Lời dẫn: nên dùng `manim-voiceover`. `tracker.duration` và bookmark `<bookmark mark="x"/>` giúp đồng bộ hình
   với từng từ.
6. Phụ thuộc: Python 3.10+, `pip install manim`, LaTeX (`texlive-full` hoặc MacTeX), ffmpeg. Kiểm tra bằng
   `scripts/setup.sh`.

## Chuẩn sáng tạo (trích nguyên văn)
- "This is educational cinema. Every frame teaches. Every animation reveals structure."
- "**Geometry before algebra.**" Cho thấy hình trước, công thức sau.
- "**First-render excellence is non-negotiable.** ... If something looks cluttered, poorly timed, or like
  'AI-generated slides,' it is wrong."
- **Phân lớp độ mờ:** phần chính 1.0, ngữ cảnh 0.4, cấu trúc (trục, lưới) 0.15.
- **Khoảng thở:** sau mỗi lần hiện ra đều có `self.wait()`. "A 2-second pause after a key reveal is never wasted."
- **Đa dạng theo cảnh:** mỗi cảnh khác màu chủ đạo, khác bố cục, khác kiểu xuất hiện (Write, FadeIn,
  GrowFromCenter, Create) và khác độ dày đặc.

## Bảng thông số
| Ngữ cảnh | Thời gian chạy | Chờ sau |
|---|---|---|
| Tiêu đề / mở đầu | 1.5 s | 1.0 s |
| Phương trình chính | 2.0 s | 2.0 s |
| Biến hình | 1.5 s | 1.5 s |
| Nhãn phụ | 0.8 s | 0.5 s |
| Dọn cảnh (FadeOut) | 0.5 s | 0.3 s |
| Khoảnh khắc "aha" | 2.5 s | 3.0 s |

- **Cỡ chữ:** tiêu đề 48, heading 36, thân 30, nhãn 24, chú thích 20; tối thiểu 18.
- **Font:** dùng monospace (Menlo), vì Pango của Manim làm hỏng kerning của font proportional. Đây là giới hạn
  riêng của Manim.
- **Bảng màu:**

  | Tên | Nền | Màu 1 | Màu 2 | Màu 3 |
  |---|---|---|---|---|
  | Classic 3B1B | `#1C1C1C` | `#58C4DD` | `#83C167` | `#FFFF00` |
  | Warm academic | `#2D2B55` | `#FF6B6B` | `#FFD93D` | `#6BCB77` |
  | Neon tech | `#0A0A0A` | `#00F5FF` | `#FF00FF` | `#39FF14` |

## 12 nguyên tắc thiết kế (visual-design.md)
1. Hình trước công thức.
2. Phân lớp độ mờ.
3. Mỗi cảnh **một** ý mới.
4. Cùng một khái niệm luôn ở cùng một vùng màn hình.
5. **Màu = ý nghĩa**: gán màu cho khái niệm, không gán cho vật thể, và giữ suốt video.
6. Hé lộ dần.
7. Biến đổi thay vì thay thế.
8. Chờ tối thiểu 1.5 s sau thứ mới.
9. Cân bằng thị giác.
10. Bộ chuyển động nhỏ và nhất quán.
11. Nền tối, nội dung sáng.
12. ≥ 15% khung để trống.

Giới hạn cứng trong production-quality.md: **tối đa 6 phần tử** đang hoạt động cùng lúc. Nhiều hơn thì làm mờ
phần cũ xuống 0.3, xoá, hoặc tách cảnh.

## Tư duy chuyển động (animation-design-thinking.md)
- **Có nên animate không?** "If you'd explain it with 'first X, then Y, then Z' — animate it. If you'd explain it by
  pointing at parts of one picture — show it static."
- **Viết lời dẫn trước**, rồi đánh dấu `[BEAT]` ở mỗi chỗ màn hình thay đổi. Mỗi beat là một `self.play()`.
- **"See then hear":** hình xuất hiện **hơi trước** lời mô tả nó, để não người xem được chuẩn bị. Nếu nghe trước
  rồi mới thấy, người xem sẽ đi tìm trên màn hình một thứ chưa có.
- **Đường cong nhịp:** chậm (mở) → vừa → **nhanh** (cao trào hoặc montage ứng dụng) → chậm (kết).
- **Lỗi phổ biến nhất là quá nhanh.** Cũng tránh nhịp đều đều kiểu mọi `run_time=1.5`, mọi `wait=1.0`. Đặt một
  quãng dừng kịch tính ngay trước "aha".
- **Vòng đời chú thích:** xuất hiện → giữ → **biến mất**. "Never leave annotations on screen indefinitely."
- **"Dim and reveal"** cho công thức dài: hiện cả công thức ở độ mờ 0.2, rồi làm sáng từng phần theo thứ tự cần
  hiểu.
- **Sơ đồ:** ít hộp (5 hộp có nhãn rõ tốt hơn 12 hộp viết tắt). Dựng dần trái → phải. Dùng mẫu zoom vào một hộp,
  bung chi tiết, rồi zoom ra.
- **Mẫu 5 phút cho video giải thích bài báo:** Hook 0:30 → Problem 1:00 → Key insight 1:30 → How it works 1:00 →
  Evidence 0:30 → Implications 0:30.

## Bẫy kỹ thuật Manim (troubleshooting.md)
- Luôn dùng raw string `r"\frac{1}{2}"`.
- Có `Text` thì dùng `Group`, không dùng `VGroup` (TypeError từ v0.20).
- `Group.save_state()` không hỗ trợ.
- `Text` không có `letter_spacing`; dùng `MarkupText` với `letter_spacing` tính bằng 1/1024 pt.
- `.to_edge(..., buff ≥ 0.5)`.
- Thay chữ cũ bằng `ReplacementTransform`, đừng `Write` đè lên.
- Ghép concat lỗi thì kiểm tra các cảnh có cùng độ phân giải, fps và codec không.

## Áp dụng vào vedit
**Không nên** tích hợp Manim lúc này. Nó cần LaTeX (rất nặng), font monospace không hợp chữ tiếng Việt kiểu
sticker, và chỉ mạnh với nội dung toán/kỹ thuật. Nên **mang nguyên tắc** sang đồ hoạ ASS và prompt.

**Đã có:**
- `highlight`, `callout`, `badge`, `progress_bar`.
- Fade ra ở cuối đồ hoạ (khớp vòng đời xuất hiện → giữ → biến mất).
- Checklist "tối đa 2 đồ hoạ cùng lúc", "hệ thống thiết kế thống nhất".

**Còn thiếu:**
- Không có cách **làm mờ ngữ cảnh** để dẫn mắt.
- Không có bộ đếm số.
- Không có quy tắc đa dạng theo cảnh. Plan gần nhất dùng cùng một kiểu `badge` + `pop` cho cả 5 bước.
- Chưa có khái niệm đường cong nhịp.
- Chưa có quy tắc "see then hear" cho nhãn thông tin.

**Đề xuất (ưu tiên giảm dần):**
1. **Đồ hoạ `spotlight`** — độ khó thấp, đã thử trên libass/ffmpeg 6.1. Phủ một lớp tối bán trong suốt lên toàn
   khung, chừa một vùng tròn hoặc chữ nhật bằng `\iclip`. Đây là "phân lớp độ mờ" cho video thật. Dòng ASS đã chạy
   được (khung 1080×1920, chừa vòng tròn bán kính 300 px quanh (540, 1060), tối dần trong 300 ms):
   ```
   {\an7\pos(0,0)\bord0\shad0\1c&H000000&\1a&HFF&\t(0,300,\1a&H50&)\iclip(1,m 540 760 b 705 760 840 895 840 1060 b 840 1225 705 1360 540 1360 b 375 1360 240 1225 240 1060 b 240 895 375 760 540 760)\p1}m 0 0 l 1080 0 l 1080 1920 l 0 1920{\p0}
   ```
2. **Thêm vào prompt Agent 2** — độ khó thấp:
   - kiểm tra đa dạng: hai bước liền nhau không dùng cùng màu, vị trí và kiểu xuất hiện;
   - đường cong nhịp chậm → nhanh → chậm;
   - nhãn thông tin hiện hơi trước lời hoặc tiếng; điểm nhấn thì đáp đúng payoff;
   - mỗi cảnh một ý mới;
   - màu = ý nghĩa.
3. **Đồ hoạ `counter`** — độ khó trung bình. Số chạy từ A tới B với easing kiểu `rush_from`, dựng bằng chuỗi event
   ASS mỗi khung một số. Dùng cho "3 ngày", giá tiền, phần trăm.
4. **Checklist trước khi render cho Agent 3** — độ khó thấp. Kiểm tra: ≥ 15% khung trống quanh chủ thể; không quá
   6 phần tử, khuyến nghị cho video ngắn là ≤ 2 đồ hoạ; chữ không nhỏ hơn cỡ đọc được trên điện thoại; mọi chú
   thích đều có lúc biến mất.
