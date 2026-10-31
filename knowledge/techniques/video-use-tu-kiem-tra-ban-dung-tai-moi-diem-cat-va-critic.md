---
title: video-use: Tự kiểm tra bản dựng tại mọi điểm cắt và critic
category: techniques
tags: [video-use, qa, self-eval, critic, kiểm tra, điểm cắt, vòng lặp tự sửa, ffprobe, ebur128]
updated: 2026-10-31
sources:
  - https://github.com/browser-use/video-use/blob/main/SKILL.md
  - https://github.com/browser-use/video-use/blob/main/README.md
  - https://github.com/browser-use/video-use/blob/main/helpers/timeline_view.py
  - https://github.com/browser-use/video-use/blob/main/helpers/render.py
---
# video-use: Tự kiểm tra bản dựng tại mọi điểm cắt và critic

Nguyên tắc 7: "**Verify your own output before showing it to the user.** If you wouldn't ship it, don't present
it." README tóm gọn: "You see the preview only after it passes."

## Quy trình self-eval (bước 7 trong SKILL.md)
1. **Xem tại mọi điểm cắt, trên bản đã render** (không phải trên nguồn). Chạy `timeline_view` trong cửa sổ
   **±1.5 s** quanh mỗi điểm cắt và soi 4 lỗi:
   - hình gián đoạn, chớp hoặc giật tại điểm cắt;
   - **gai trên waveform** ngay tại điểm cắt, tức tiếng "tách" lọt qua fade 30 ms;
   - phụ đề bị overlay che (vi phạm Rule 1);
   - overlay lệch hoặc hiện sai khung (vi phạm Rule 4).
2. **Lấy mẫu thêm** ở 2 s đầu, 2 s cuối và 2–3 điểm giữa. Kiểm tra màu có đồng đều không, phụ đề đọc được
   không, tổng thể có liền mạch không.
3. **Đối chiếu độ dài** bằng `ffprobe` với thời lượng mà EDL dự kiến.
4. **Đo âm thanh:** `ebur128` (integrated + true peak) và RMS từng đoạn. "You cannot listen: say so, and report
   the numbers."
5. **Critic sub-agent** cho thứ sẽ đăng công khai. Đầu vào: file render, EDL, video tham chiếu. Brief: "roast, not
   to praise". Đầu ra: phán quyết, danh sách vấn đề xếp hạng kèm mốc giây và bằng chứng (khung hình, số đo), và
   5 sửa đổi làm trước.
6. Có lỗi thì sửa → render lại → kiểm lại. **Tối đa 3 vòng.** Sau 3 vòng vẫn còn lỗi thì báo người dùng, không lặp
   mãi. Chỉ trình bày preview khi đã qua.

Để kiểm nhanh điểm cắt, video-use có chế độ `--draft` (720p, ultrafast, CRF 28): "cut-point verification only".

## Bộ lệnh QA cho một dự án vedit (đã chạy thử 2026-10-31 trên `20261030-video-01`)
```bash
cd /home/user/Claude_edit
SLUG=20261030-video-01; V=projects/$SLUG/renders/preview.mp4   # hoặc final.mp4
CUTS=$(python3 -c "
import sys; sys.path.insert(0, '.')
from pathlib import Path; from vedit.edl import EditPlan
p = EditPlan.load(Path('projects/$SLUG/edit_plan.json'))
print(' '.join(f'{o:.3f}' for o in p.clip_offsets()[1:]))")
mkdir -p projects/$SLUG/renders/qa; FONT=/usr/share/fonts/opentype/inter/Inter-Bold.otf
for T in $CUTS; do
  S=$(python3 -c "print(f'{max(0.0,$T-1.5):.3f}')"); D=3; N=8; X=$(python3 -c "print(f'{($T-$S)/$D:.4f}')")
  ffmpeg -hide_banner -loglevel error -y -ss $S -t $D -i $V -filter_complex \
  "[0:v]fps=$N/$D,scale=-2:240,drawtext=fontfile=$FONT:text='%{pts\:flt\:$S}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=${N}x1:padding=4:color=0x121216[strip];[strip]scale=1600:-2[s];[0:a]aformat=channel_layouts=mono,showwavespic=s=1600x200:colors=0x8CB4FF:scale=sqrt,drawbox=x=iw*$X-1:y=0:w=2:h=ih:color=red@0.9:t=fill[w];[s][w]vstack[out]" \
  -map "[out]" -frames:v 1 projects/$SLUG/renders/qa/cut_$T.png
done
ffprobe -v error -show_entries format=duration -of csv=p=0 $V          # so với plan.duration
ffmpeg -hide_banner -nostats -i $V -af ebur128=peak=true -f null - 2>&1 | grep -A14 "Summary:"
```
- Mỗi ảnh gồm 8 khung có nhãn giây, waveform, và một **vạch đỏ đúng tại điểm cắt**.
- Với plan trên, lệnh tạo đủ 8 ảnh cho 8 điểm cắt: 1.4, 3.0, 4.6, 6.0, 7.7, 9.1, 11.9, 13.6 s.

## Bảng tra: lỗi → dấu hiệu trên ảnh → cách sửa trong EditPlan
| Lỗi | Dấu hiệu | Sửa |
|---|---|---|
| Tiếng "tách" ở điểm cắt | Gai nhọn đứng một mình ở vạch đỏ | Fade 30 ms; dời điểm cắt vào khoảng lặng |
| Cú cắt ẩn trong nguồn | Khung kề vạch đỏ đổi cảnh 1–2 khung | Rút `start`/`end` tránh khung chớp (plan gần nhất đã phải sửa tay 3 chỗ như vậy) |
| Cắt cụt payoff | Waveform đang ở đỉnh thì bị cắt | Kéo `end` qua hết tiếng hoặc phản ứng |
| Chữ đọc không kịp | Cue hoặc nhãn đổi trước khi đủ ~0.35 s; chữ nhỏ ở cỡ điện thoại | Kéo dài, phóng to, bớt chữ |
| Hai thứ mới cùng xuất hiện | Nhiều đồ hoạ cùng bật trong 1–2 khung kề nhau | Giãn ra ("one thing, pause, next thing") |
| Màu nhảy giữa 2 clip | Hai bên vạch khác hẳn độ sáng hoặc tông | Auto-correct theo clip |

## Áp dụng vào vedit
**Đã có:**
- Agent 3 render preview, xem khung **giữa mỗi clip** và **lúc chữ xuất hiện** (bản API: tối đa 6 clip + 4 chữ),
  có lưới toạ độ.
- Kiểm tra chữ tràn, che chủ thể, vùng an toàn, crop.
- Giới hạn 1–3 vòng.

**Còn thiếu:**
- Không kiểm tra **tại điểm cắt** (cả hình và tiếng).
- Không đo âm thanh.
- Không đối chiếu độ dài.
- Không có critic với góc nhìn mới.
- Không có quy định "chưa qua QA thì không gửi".

**Đề xuất (ưu tiên giảm dần):**
1. **Lệnh `vedit qa <slug> [--source preview|final]`** — độ khó thấp đến trung bình. Đóng gói bộ lệnh trên, sinh
   ra:
   - `renders/qa/cut_*.png`, `head.png` (0–2 s), `tail.png`, `mid_k.png`;
   - `qa.json` gồm: độ dài so với plan, I/TP/LRA, RMS từng clip, và các cờ (TP > −1, chênh RMS giữa clip kề nhau,
     cue < 0.35 s, ≥ 2 phần tử mới bật trong cùng 0.3 s).

   Prompt Agent 3: "đọc mọi ảnh cut_*.png và qa.json trước khi kết luận".
2. **Subagent `video-critic`** (brief ở `scripting/video-use-mau-brief-giao-viec-cho-sub-agent`) — độ khó thấp.
   Gọi trong `/lam-video` và `/sua-video` sau QA. Agent 3 sửa theo 5 điểm đầu.
3. **Quy định giao hàng** — độ khó thấp. Chỉ gửi `final.mp4` khi QA và critic không còn lỗi nghiêm trọng, hoặc đã
   hết 3 vòng; khi đó phải nêu rõ lỗi còn lại kèm số đo.
4. **Chế độ draft** — độ khó thấp. Nếu chỉ cần kiểm điểm cắt thì render bản rẻ (ví dụ CRF 28, `ultrafast`) để
   vòng sửa nhanh hơn.
