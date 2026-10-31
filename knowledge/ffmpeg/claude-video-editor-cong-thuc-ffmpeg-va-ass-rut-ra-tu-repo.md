---
title: claude-video-editor: Công thức ffmpeg và ASS rút ra từ repo
category: ffmpeg
tags: [claude-video-editor, ffmpeg, ass, libass, easing, whip pan, dblur, ken burns, perspective, overlay alpha, contact sheet]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/helpers/render.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/helpers/timeline_view.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-studio/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/recipes/01-launch-video.md
  - https://github.com/assafkip/claude-video-editor/blob/master/recipes/02-tutorial-edit.md
  - https://github.com/assafkip/claude-video-editor/blob/master/examples/captions/render-cmd.sh
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/MOTION_PHILOSOPHY.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/generate-footage/scripts/motion_check.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/generate-footage/scripts/build_scenes.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/css-patterns.md
---
# claude-video-editor: Công thức ffmpeg và ASS rút ra từ repo

Phần A là lệnh lấy từ repo (nguyên văn trong tài liệu, hoặc dựng lại từ code `render.py` với tham số thay bằng
`{…}`); phần B là bản chuyển sang ffmpeg/libass cho vedit, **đã chạy thử ngày 2026-10-31** với ffmpeg 6.1.1 (Ubuntu,
có libass, libzimg) của môi trường vedit.

## A. Lệnh trong repo

**Cắt một đoạn kèm grade + fade âm 30ms** (render.py — `-ss` trước `-i` để seek nhanh):
```bash
ffmpeg -y -ss {start} -i SRC -t {dur} -vf "{tonemap?},scale=1920:-2,{grade}" \
  -af "afade=t=in:st=0:d=0.03,afade=t=out:st={dur-0.03}:d=0.03" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -r 24 -c:a aac -b:a 192k -ar 48000 -movflags +faststart seg_00.mp4
```
**Nối không mã hoá lại**: `ffmpeg -f concat -safe 0 -i list.txt -c copy -movflags +faststart base.mp4`.

**Chồng overlay video (có alpha) đúng khung đầu** — dời PTS để khung 0 của overlay rơi đúng lúc bắt đầu, phụ đề áp
**sau cùng**:
```bash
ffmpeg -i base.mp4 -i cap1.mov -filter_complex \
 "[1:v]setpts=PTS-STARTPTS+4.0/TB[a1];[0:v][a1]overlay=enable='between(t,4.000,9.000)'[v1];\
  [v1]subtitles='master.srt':force_style='FontName=Helvetica,FontSize=18,Bold=1,Outline=2,Shadow=0,Alignment=2,MarginV=90'[outv]" \
 -map "[outv]" -map 0:a -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -c:a copy out.mp4
```
Overlay có alpha phải là **ProRes 4444 `.mov`** — repo ghi webm của HyperFrames ra **đục** (dù tài liệu CLI nói webm có
alpha). Render caption có biến: `npx hyperframes@0.6.70 render index.html --format mov --variables '{"num":"01",…}' -o cap1.mov`.

**Nguồn không tiếng → thêm track stereo im lặng** (bắt buộc với engine này):
```bash
ffmpeg -i source.mov -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -shortest -c:v copy -c:a aac source_a.mp4
```
**Speed ramp**: đoạn chạy dài được render trước bằng `setpts` (45–50×) thành nguồn riêng trong EDL.
**Ảnh poster / khung cuối** (chống chớp đầu/cuối video):
`ffmpeg -y -ss 0 -i clip.mp4 -frames:v 1 -q:v 2 poster.jpg` · `ffmpeg -y -sseof -0.04 -i clip.mp4 -frames:v 1 -q:v 2 lastframe.jpg`
**GIF cho README**:
`ffmpeg -i in.mp4 -vf "fps=10,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4" out.gif`
**Trích khung kiểm tra**: `ffmpeg -y -ss <t> -i draft.mp4 -frames:v 1 -q:v 2 frames/t<t>.png`.
**Chứng minh có chuyển động** (motion_check): `ffmpeg -v error -ss T -i v.mp4 -frames:v 1 -vf format=gray,scale=160:160 -f rawvideo -`
cho 2 thời điểm trong cùng cảnh → trung bình |a−b|; trung vị 3 cặp > 3 = có chuyển động.
**Âm lượng**: `ffmpeg -i final.mp4 -af volumedetect -f null -` (lời thuyết minh tài liệu ~ −26 dB mean).

## B. Chuyển sang vedit (đã kiểm chứng)

### B1. Easing trong libass
`\t(t1,t2,accel,tags)`: `accel < 1` = nhanh rồi chậm (ease-out), `> 1` = chậm rồi nhanh (ease-in), 1 = tuyến tính.
Đo bằng thanh `\fscx0→100` trong 1s, tại 25% thời gian: tuyến tính 24%, **accel 0.4 → 56.5%** (ease_out_cubic lý
thuyết 57.8%), accel 2.5 → 2.8%; tại 50%: 52% / 77% / 19.5%. → Dùng **accel 0.4–0.5 cho mọi entry**, 2–2.5 cho exit.

`\move` **luôn tuyến tính** (đo: 0.24s/1s → 24.5% quãng đường). Muốn trượt có easing: tách thành **một event mỗi
khung** với `\pos` tính bằng `1-(1-p)^3`, thời gian event nối liền (end của event k = start của event k+1, làm tròn
centi-giây) rồi một event giữ ở vị trí cuối. Đo thực tế khớp đúng đường cong (p=0.24 → 56%, p=0.48 → 86%), không hở
khung. Entry 0.3s ở 30fps chỉ tốn ~9 event.

### B2. Dải highlight kiểu bút dạ + vệt sáng quét (ASS, khung 1080×1920)
```text
Dialogue: 1,0:00:00.00,0:00:03.00,G,,0,0,0,,{\an7\pos(0,0)\bord0\shad0\1c&H35D2FF&\1a&H40&\clip(170,640,171,800)\t(200,650,0.45,\clip(170,640,910,800))\p1}m 170 655 l 910 640 905 790 175 800{\p0}
Dialogue: 2,0:00:00.00,0:00:03.00,G,,0,0,0,,{\an5\pos(540,720)\bord0\shad0\1c&H1A1A1A&}CÀ PHÁO GIÒN
Dialogue: 3,0:00:01.00,0:00:01.40,G,,0,0,0,,{\an5\move(-500,1100,1600,1100)\bord0\shad0\blur18\1c&HFFFFFF&\p1}m -350 -10 l 350 -10 350 10 -350 10{\p0}
```
Dòng 1: tứ giác vàng (`&H35D2FF&` = BGR của #FFD235) hơi nghiêng, lộ dần trái→phải bằng `\clip` có accel 0.45, đặt
**layer thấp hơn** chữ. Dòng 3: thanh trắng 700×20 blur 18 quét ngang 0.4s — "light-streak whip" để giấu một điểm cắt
cứng (cắt đúng giữa vệt). Đã render thử: cả hai hiển thị đúng với font Be Vietnam Pro ExtraBold.

### B3. Transition whip có motion blur
```bash
[a][b]xfade=transition=slideleft:duration=0.3:offset=1.7,dblur=angle=0:radius=45:enable='between(t,1.72,1.98)'[v]
```
`dblur` (directional blur, hỗ trợ timeline) bật trong cửa sổ chuyển → vệt nhoè ngang mạnh giống whip-pan; dọc dùng
`slideup` + `angle=90`. Kèm SFX `whoosh` bắt đầu ~0.05s trước offset (nhận định). Phương án khác: `tmix=frames=3`
trong cửa sổ để tạo vệt "ghost" — tmix có hỗ trợ `enable`, nhưng hiệu quả hình ảnh **chưa thử**. Đã render thử cả
`slideleft` + `angle=0` (nhoè ngang) và `slideup` + `angle=90` (nhoè dọc) trên khung 540×960.

### B4. Ken Burns mượt (subpixel) bằng `perspective`
`zoompan` với zoom chậm bị lượng tử hoá: thử 1.00→1.025 trong 3s (90 khung, 1080×1920), một điểm sáng gần mép
**đứng yên 61/89 khung rồi nhảy ~0.9px, 13 lần giật lùi**; phóng 4× trước zoompan đỡ hơn nhưng vẫn rung (37 lần lùi
nhỏ). `perspective` nội suy cubic theo từng khung cho bước **0.04–0.12px/khung, không đứng, không lùi**:
```bash
Z="(1+0.025*in/90)"   # in = số thứ tự khung vào; 90 = số khung của clip
perspective=x0='W/2-W/(2*$Z)':y0='H/2-H/(2*$Z)':x1='W/2+W/(2*$Z)':y1='H/2-H/(2*$Z)':\
x2='W/2-W/(2*$Z)':y2='H/2+H/(2*$Z)':x3='W/2+W/(2*$Z)':y3='H/2+H/(2*$Z)':interpolation=cubic:eval=frame
```
Chi phí: 2.4s so với 0.32s của zoompan cho 3s 1080×1920 (4 nhân) — dùng cho zoom chậm; punch nhanh (0.2–0.4s)
vẫn dùng zoompan vì bước nhảy pixel không thấy được ở tốc độ đó. Lệch tâm: thay `W/2`, `H/2` bằng toạ độ tiêu điểm.

### B5. Ảnh kiểm tra nhanh
- Contact sheet 3×3 (1 khung/giây): `ffmpeg -i preview.mp4 -vf "fps=1,scale=240:-2,tile=3x3:padding=6:color=black" -frames:v 1 sheet.jpg`
- Sóng âm một đoạn (cho "timeline view" tự làm): `ffmpeg -ss 2 -t 3 -i v.mp4 -filter_complex "[0:a]aformat=channel_layouts=mono,showwavespic=s=1200x200:colors=0x8cb4ff:scale=sqrt" -frames:v 1 wave.png`
  (kết hợp dải khung `select`+`tile` và nhãn từ bằng Pillow — không cần numpy như bản gốc).

### B6. Khác
- `anoisesrc` mặc định `seed=-1` (ngẫu nhiên) → SFX `whoosh` của vedit khác nhau mỗi lần render; đặt `seed=…` cố
  định nếu cần render tái lập (repo HyperFrames coi tính xác định là luật cứng).
- Tonemap HDR: xem `ffmpeg/claude-video-editor-grade-mau-tu-dong-va-tonemap-hdr`. Loudnorm 2 lượt: xem
  `audio/claude-video-editor-am-thanh-fade-30ms-va-loudnorm-2-luot`.

## Áp dụng vào vedit

**Đã có**: một filter graph cho mọi thứ (không cần concat/overlay nhiều lượt); ASS cho chữ/đồ hoạ; xfade/acrossfade;
zoompan cho zoom/punch/shake; anullsrc cho clip không tiếng.

**Còn thiếu & đề xuất (ưu tiên)**:
1. `vedit/ass.py`: thêm accel 0.45 vào `\t` của entry (pop/bounce/blur_in/wipe…), thay `\move` (slide_up/slide_left)
   bằng event theo khung có ease_out_cubic (B1). Dễ–vừa.
2. `render.py`: zoom chậm per-clip dùng `perspective` (B4) thay zoompan. Dễ.
3. Transition `whip_*` (B3) + graphic `streak`, `marker` (B2). Vừa.
4. Seed cố định cho `anoisesrc` (B6). Dễ.
5. `vedit qa`/`vedit timeline` dùng B5 cho contact sheet và filmstrip + waveform. Vừa.
6. Dài hạn: `images[]` nhận cả **video có alpha** (`.mov` ProRes 4444) với `setpts=PTS-STARTPTS+T/TB` để nhập đồ hoạ
   render từ HyperFrames/Remotion khi cần hiệu ứng ngoài khả năng libass. Vừa–khó.
