---
title: Công thức ffmpeg cho video dọc
category: ffmpeg
tags: [ffmpeg, crop, blur, xfade, loudnorm, subtitles, zoompan]
updated: 2026-10-30
sources:
  - https://ffmpeg.org/ffmpeg-filters.html
  - (ghi chú khởi tạo từ kiến thức nền — chạy Agent 1 để kiểm chứng & cập nhật)
---
# Công thức ffmpeg cho video dọc

> (ghi chú khởi tạo từ kiến thức nền — chạy Agent 1 để kiểm chứng & cập nhật) — các lệnh dưới đã chạy thử với ffmpeg 6.1.

### Crop ngang → dọc (giữ chủ thể ở 40% chiều ngang)
```
ffmpeg -i in.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)*0.4:(ih-1920)*0.5" out.mp4
```
### Nền mờ phía sau (blur fill)
```
-filter_complex "[0:v]split[a][b];[a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=10:2,scale=1080:1920[bg];[b]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2"
```
(Làm mờ ở độ phân giải 1/4 rồi phóng lại — nhanh hơn nhiều so với blur ở 1080x1920.)
### Tìm khoảng lặng / chuyển cảnh
```
ffmpeg -i in.mp4 -af silencedetect=noise=-35dB:d=0.6 -f null -
ffmpeg -i in.mp4 -vf "scale=320:-2,select='gt(scene,0.3)',showinfo" -f null -
```
### Chuyển cảnh xfade (cần cùng fps, kích thước, timebase → thêm `settb=1/30`)
```
[v0][v1]xfade=transition=fade:duration=0.3:offset=<độ dài v0 - 0.3>
[a0][a1]acrossfade=d=0.3
```
### Zoom chậm (Ken Burns) trên video
```
zoompan=z='1+0.12*on/<số frame>':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30
```
### Chuẩn loudness cho mạng xã hội & ducking nhạc
```
loudnorm=I=-14:TP=-1.5:LRA=11
[music][voice]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400
```
### Phụ đề ASS (hỗ trợ tiếng Việt, viền, hộp nền, hiệu ứng)
```
-vf "subtitles=subs.ass:fontsdir=assets/fonts"
```
