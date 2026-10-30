---
title: Repo GitHub hữu ích cho dựng video tự động
category: tools
tags: [github, auto-editor, whisper, moviepy, remotion, scene detection]
updated: 2026-10-30
sources:
  - https://github.com/WyattBlue/auto-editor
  - https://github.com/SYSTRAN/faster-whisper
  - (ghi chú khởi tạo từ kiến thức nền — chạy Agent 1 để kiểm chứng & cập nhật)
---
# Repo GitHub hữu ích cho dựng video tự động

> (ghi chú khởi tạo từ kiến thức nền — chạy Agent 1 để kiểm chứng & cập nhật)

| Repo | Dùng để |
|---|---|
| [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg) | Nền tảng xử lý video/âm thanh — bộ render của vedit |
| [WyattBlue/auto-editor](https://github.com/WyattBlue/auto-editor) | Tự cắt khoảng lặng / đoạn ít chuyển động |
| [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Nhận dạng giọng nói + mốc từng từ (phụ đề karaoke) — vedit dùng tuỳ chọn |
| [openai/whisper](https://github.com/openai/whisper) | Mô hình nhận dạng giọng nói gốc |
| [Breakthrough/PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | Dò chuyển cảnh chính xác hơn ngưỡng scene của ffmpeg |
| [Zulko/moviepy](https://github.com/Zulko/moviepy) | Dựng video bằng Python (chậm hơn ffmpeg thuần nhưng dễ viết) |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Dựng video bằng React — motion graphics, template |
| [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | Lấy metadata / phụ đề YouTube, TikTok — Agent 1 & 2 dùng |
