---
title: video-use: Animation overlay, easing và thời điểm payoff
category: techniques
tags: [video-use, animation, motion graphics, easing, payoff, hyperframes, remotion, pil, font, overlay]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/helpers/render.py
  - https://raw.githubusercontent.com/heygen-com/hyperframes/main/README.md
---
# video-use: Animation overlay, easing và thời điểm payoff

Trong video-use, animation là các clip rời. Mỗi slot `edit/animations/slot_<id>/` do một sub-agent dựng, xuất
`render.mp4`, rồi được overlay theo `start_in_output` và `duration`. Nguyên tắc chung: "Animations match the
content and the brand... never assume a default."

## Chọn engine theo từng slot
| Engine | Hợp với | Ghi chú |
|---|---|---|
| **HyperFrames** (HTML/CSS/GSAP) | UI sản phẩm, website/mockup thành video, kinetic typography, promo kiểu landing page, overlay WebM trong suốt | `npx --yes hyperframes init . --example blank --non-interactive --skip-skills` → `lint`/`validate`/render nháp → `npx --yes hyperframes render . -o render.mp4` (theo SKILL.md, `--format webm` khi cần alpha). README HyperFrames: Node 22+, FFmpeg, headless Chrome, Apache-2.0; README chỉ mô tả MP4, nên phải thử trước khi dựa vào alpha |
| **Remotion** (React) | Khi người dùng muốn React, hoặc đã có brand system trên Remotion | Dự án tách riêng trong slot, kiểm tra kích thước và độ dài bằng ffprobe |
| **Manim** | Sơ đồ chính thức, state machine, biến đổi phương trình, đồ thị | Xem `techniques/video-use-skill-manim-video-thiet-ke-chuyen-dong-giai-thich` |
| **PIL + chuỗi PNG + ffmpeg** | Thẻ đơn giản: bộ đếm, gõ chữ, thanh tăng dần, nét vẽ dần | Nhanh, tự do thẩm mỹ. Video launch mẫu dùng cách này |

"Do not default to Remotion just because the animation is web-adjacent." Được phép ghép, ví dụ nền PIL và lớp
HyperFrames ở trên.

## Thời lượng (quy tắc kinh nghiệm)
- **Giải thích đi kèm lời thoại:** người xem phải hiểu được ở tốc độ 1×. Sàn khoảng **3 s**; thẻ đơn giản thường
  **5–7 s**; sơ đồ phức tạp **8–14 s**.
- **Điểm nhấn theo beat** (MV, montage nhanh): **0.5–2 s** là được, vì chỉ cần "recognizable at 1×", không cần
  "fully parseable".
- **Giữ khung cuối ≥ 1 s** trước khi cắt. Áp dụng mọi trường hợp.
- **Chạy trên voiceover:** tổng thời lượng ≥ độ dài lời + 1 s.
- **Không bao giờ cho hai phần tử độc lập hiện ra cùng lúc:** "the eye can't track two new things at once. One
  thing, pause, next thing."

## Thời điểm payoff (đồng bộ với lời)
Lấy timestamp của từ payoff. Bắt đầu overlay sớm hơn `reveal_duration` giây, để **khung đáp** trùng đúng lúc từ
đó được nói. "Without this sync the animation feels disconnected."
`overlay_start = t(từ payoff) − reveal_duration`.

## Easing: không bao giờ dùng `linear` ("it looks robotic")
```python
def ease_out_cubic(t):    return 1 - (1 - t) ** 3          # một lần xuất hiện: đáp chậm
def ease_in_out_cubic(t):
    if t < 0.5: return 4 * t ** 3
    return 1 - (-2 * t + 2) ** 3 / 2                        # nét vẽ / chuyển động liên tục
```

## Mẹo và bẫy
- **Chữ gõ dần:** căn giữa theo độ rộng của **cả chuỗi**, không theo phần đã gõ. Nếu không, chữ trôi sang trái
  khi dài ra.
- **Font hỏng không báo lỗi:** web font không tải được sẽ âm thầm thay bằng font khác, và video ra "almost Arial".
  Với HyperFrames/Remotion, chờ font tải xong rồi assert:
  `if (!document.fonts.check('700 76px "Inter"')) throw new Error(...)`. Với PIL, luôn truyền đường dẫn font
  tường minh.
- **Bảng màu mẫu** (video launch, một phong cách trong vô số):
  - nền `(10,10,10)`, accent `#FF5A00`, nhãn `(110,110,110)`;
  - font Menlo Bold (`/System/Library/Fonts/Menlo.ttc`, index 1);
  - ≤ 2 màu nhấn, khoảng 40% khoảng trống, tối thiểu chrome.
- **Ví dụ mẫu, hook "show the edit":** thay cho title card, 3 s đầu hiển thị chính việc dựng.
  - Mỗi từ trong transcript bật lên đúng timestamp Scribe, bên dưới là các thanh vẽ từ envelope âm thanh thật.
  - Từ đệm "ummm" dài dần theo từng chữ cái khi đang được nói, chuyển cam, rồi bị cắt khỏi màn hình đúng khung
    mà âm thanh bị cắt.

  Nó hiệu quả vì "the picture is *driven by the same data as the sound*". Python xuất JSON chính xác tới từng khung
  (từ và envelope), một composition Remotion đọc JSON đó, nên không thể lệch. Bài học chung: khi câu chuyện là
  "chúng tôi đã bỏ đi thứ gì", hãy **làm cho việc bỏ đi đó nhìn thấy được**.

## Áp dụng vào vedit
**Đã có:**
- Chữ động ASS: `pop` và `bounce` có keyframe vượt đà, `word_pop` giãn 140 ms mỗi từ, `typewriter`, `blur_in`,
  `wipe`, `slide_up`/`slide_left`.
- `typewriter` đặt toàn chuỗi rồi mở alpha từng ký tự, nên **đã đúng** mẹo neo theo cả chuỗi.
- Đồ hoạ vector: callout, badge, progress, highlight, sparkles, flash.
- `FontBook` chuẩn hoá cỡ chữ.

**Còn thiếu (đã kiểm chứng):**
- **Font fallback âm thầm.** `FontBook._find` hỏi `fc-match`. Ngày 2026-10-31,
  `fc-match 'Khong Ton Tai Font:weight=200'` trả về **Inter** chứ không báo lỗi. Vì vậy gõ sai tên font trong plan
  sẽ render bằng Inter mà không ai biết.
- **`\move` của libass luôn tuyến tính**, nên `slide_up`/`slide_left` đang chạy kiểu `linear` mà video-use cấm.
  Các `\t(...)` trong vedit cũng chưa dùng tham số `accel`.
- **Nhiều phần tử mới cùng bật** ("parallel reveal"). Trong 0.3 s đầu của plan `20261030-video-01` có: tiêu đề
  `bounce`, `progress_bar`, `punch`, `sparkles` (0.15 s), banner `wipe` (0.3 s), cộng 2 SFX. Hai callout "muối"
  (3.2 s) và "đường" (3.65 s) cũng chồng lên nhau.
- **Không phân biệt overlay "nhấn" với overlay "thông tin".** Nhãn bước như "Pha nước muối" chỉ hiện khoảng
  1–1.6 s, ngắn hơn sàn đọc ~3 s cho thông tin của video-use.
- Không có cơ chế canh khung đáp theo từ hoặc tiếng.
- Không overlay được animation dựng sẵn.

**Đề xuất (ưu tiên giảm dần):**
1. **Kiểm font trong `validate`** — độ khó thấp. Chạy `fc-match -f '%{family}' '<font>'` và so với tên yêu cầu
   (hoặc tìm trong `assets/fonts`). Lệch thì báo lỗi, không chỉ cảnh báo.
2. **Easing** — độ khó thấp. Thay `\move` tuyến tính bằng chuỗi event ngắn, mỗi event một khung trong khoảng
   0.25–0.3 s đầu, với `\pos` tính theo `ease_out_cubic`. Cách khác là chuyển hiệu ứng trượt sang `\t(0,T,accel,...)`
   cho các tag hỗ trợ (scale, alpha, `\clip`, `\blur`) với `accel` < 1. Theo đặc tả ASS, `accel` < 1 nghĩa là bắt
   đầu nhanh rồi chậm dần.
3. **`validate` cảnh báo "parallel reveal"** — độ khó thấp. Cảnh báo khi ≥ 2 `texts`/`graphics` mới bắt đầu
   trong cùng khoảng 0.3 s (ngưỡng đề xuất), trừ trường hợp chúng thuộc cùng một nhóm như chữ và nền sticker của
   nó.
4. **`TextOverlay.land_at` / `Graphic.land_at`** — độ khó thấp đến trung bình. Ghi thời điểm animation **đáp**;
   renderer tự lùi `start` theo độ dài hiệu ứng (`pop` khoảng 0.24 s, `bounce` khoảng 0.4 s, `slide_up`
   0.26 s...). Agent 2 lấy mốc từ, hoặc mốc tiếng động, làm `land_at`.
5. **Hai loại overlay trong prompt Agent 2** — độ khó thấp. Loại "nhấn" dài 0.5–2 s, chỉ cần nhận ra (số bước,
   một từ). Loại "thông tin" cần đọc thì ≥ 3 s, hoặc phải giảm chữ.
6. **Về lâu dài: overlay clip có alpha** — độ khó trung bình đến cao. Dùng `setpts` + `-c:v libvpx-vp9` cho WebM.
   Khi đó có thể dựng các animation "lái bằng dữ liệu" như bộ đếm, biểu đồ, hay hiệu ứng "xoá từ đệm" ngay trong
   vedit.
