---
name: chon-nhac
description: Agent 5 — Âm thanh: rà nhạc hợp vibe / trend cho video, PHÂN LOẠI RỦI RO BẢN QUYỀN từng bài kèm bằng chứng (giấy phép, quy định nền tảng), đo BPM / nhịp đầu từ assets/music, đề xuất điểm vào, âm lượng, lưới beat; chưa có nhạc thì tạo nhạc bằng code. Dùng khi người dùng muốn chọn nhạc, tìm nhạc trend, kiểm nhạc có dính bản quyền không, hoặc bám beat.
argument-hint: [slug dự án] [tâm trạng, độ dài, bám beat hay không...]
---

Yêu cầu chọn nhạc: $ARGUMENTS

Trao đổi bằng tiếng Việt.

1. Nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh`.
2. Xác định dự án: slug trong yêu cầu hoặc `vedit projects` (dự án mới nhất). Ghi yêu cầu nguyên văn
   `vedit note <slug> "<yêu cầu>" --kind "yêu cầu"`.
3. Người dùng gửi file nhạc trong chat (`/root/.claude/uploads/...`) → chép vào `assets/music/` (không ghi đè file cũ).
   Họ gửi link Drive → `vedit sfx add` chỉ dành cho SFX; nhạc thì `vedit fetch "<link>"` rồi chép vào `assets/music/`.
4. Agent tool `subagent_type: video-music-picker`: truyền slug, yêu cầu nguyên văn, độ dài video, có giọng đọc không.
5. Gửi `projects/<slug>/audio/music.md` bằng SendUserFile kèm 3–5 dòng tóm tắt: bài chọn, BPM và độ chắc, thông số, lưới beat.
   Nếu có nhạc tạo bằng code, đính kèm file nghe thử.
6. Người dùng chấp nhận → Agent 3 (`video-editor`) đưa thông số vào `audio` của EditPlan; khen / chê nhạc thì ghi nguyên
   văn `vedit note <slug> "..." --kind "phản hồi"` và cập nhật `profile/gu-nguoi-dung.md` (commit + push).
7. Khi người dùng muốn **tìm nhạc mới / nhạc trend / kiểm bản quyền**: nói rõ agent chỉ phân loại rủi ro theo giấy phép đã đọc (không cam kết "không dính bản quyền"); gửi `projects/<slug>/audio/candidates.json` (và bảng trong `music.md`) kèm tóm tắt: bài dùng được ngay, bài cần tự xác nhận, bài không nên dùng cho video hợp tác. Cập nhật `music/<slug>` trên trang Studio nếu họ đang dùng.
