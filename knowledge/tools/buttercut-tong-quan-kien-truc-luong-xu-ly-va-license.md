---
title: buttercut: Tổng quan kiến trúc, luồng xử lý và license
category: tools
tags: [buttercut, claude code, roughcut, fcpxml, whisperx, contact sheet, agent, license]
updated: 2026-10-31
sources:
  - https://github.com/barefootford/buttercut
  - https://github.com/barefootford/buttercut/blob/main/README.md
  - https://github.com/barefootford/buttercut/blob/main/AGENTS.md
  - https://github.com/barefootford/buttercut/blob/main/CHANGELOG.md
  - https://github.com/barefootford/buttercut/blob/main/LICENSE
  - https://github.com/barefootford/buttercut/commits/main/LICENSE
  - https://raw.githubusercontent.com/barefootford/buttercut/8fffff0/LICENSE
  - https://github.com/barefootford/buttercut/blob/main/docs/usage.md
  - https://github.com/barefootford/buttercut/blob/main/docs/creating-a-cut.md
  - https://github.com/barefootford/buttercut/blob/main/docs/example-library-setup.md
  - https://github.com/barefootford/buttercut/blob/main/docs/installation.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/analyze-video/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/misc-task/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/library.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/export_core.rb
  - https://github.com/barefootford/buttercut/blob/main/requirements.txt
  - https://github.com/barefootford/buttercut/blob/main/templates/library_template.yaml
  - https://github.com/barefootford/buttercut/blob/main/templates/roughcut_template.yaml
---
# buttercut: Tổng quan kiến trúc, luồng xử lý và license

> Đọc toàn bộ mã, prompt, skill, tài liệu tại commit `352c1e0` (23/09/2026, mới nhất trên `main` khi kiểm tra
> ngày 31/10/2026; phiên bản 0.9.1). Repo: 613 sao, 98 fork, 223 commit (quan sát 31/10/2026).
> Không xem được video demo trên YouTube và trang buttercut.io vì mạng của phiên bị chặn hai tên miền này.

## Tóm tắt một câu

ButterCut ("Edit Video with Claude Code") là **một thư mục dự án mở bằng Claude Code/Codex**: skill (prompt) điều
khiển Claude phân tích footage thô (WhisperX + contact sheet + tóm tắt từng clip), cùng người dùng lên kế hoạch rồi
**xuất timeline XML** (FCPXML 1.12 / xmeml v5) để editor mở trong Final Cut Pro, Premiere hoặc DaVinci Resolve và
dựng tiếp. Nó **không render video**, không làm chữ, phụ đề hay đồ hoạ (bản core).

## Kiến trúc

| Phần | Vai trò |
|---|---|
| `AGENTS.md` (CLAUDE.md chỉ `@AGENTS.md`) | Luật chung: quy trình 4 bước, nguyên tắc bắt buộc, từ vựng nói chuyện với editor |
| `skills/` (symlink `.claude/skills -> ../skills`) | Prompt cho từng bước: `create-library`, `process-library`, `analyze-video`, `transcribe-audio`, `cut`, `contact-sheet`, `full-transcript`, `backup-library`, `misc-task`, `buttercut`/`bc` (menu chính), `report-bug`, `request-feature`, `setup`, `update-buttercut` |
| `lib/buttercut/*.rb` (Ruby 3.3) | Mọi thứ máy móc: lớp `Library` (đọc/ghi `library.yaml`), `ContactSheet`, `TranscribeJob`, `JobRunner`, `script_extractor.rb`, `export.rb` + bộ sinh XML (`fcpx_core.rb`, `fcp7_core.rb`, `premiere_core.rb`, `resolve_core.rb`) |
| `templates/` | `library_template.yaml`, `roughcut_template.yaml` (cut YAML), `plan_template.md`, `settings_template.yaml` |
| `libraries/<tên>/` (gitignore) | Dữ liệu người dùng: `library.yaml`, `transcripts/`, `contact_sheets/`, `summaries/`, `cuts/`, `plans/`, `misc/` |

Hai khái niệm chính: **library** (một dự án/series footage, gồm video và ảnh) và **cut** (bản dựng: scene, selects,
script edit, custom, roughcut). `library.yaml` là "trí nhớ bền vững": metadata, `footage_summary`, `user_context`
(vd "người mặc áo xanh dài tay là Andrew"), danh sách media với trạng thái từng artifact (rỗng = chưa làm,
tên file = xong).

## Luồng xử lý: footage thô → timeline

1. **create-library**: hỏi từng câu một (tên, thư mục footage, ngôn ngữ, có cho Claude hiệu đính transcript
   không), `Library.create` ffprobe thời lượng, tạo cây thư mục.
2. **process-library / analyze-video** (chi tiết: `techniques/buttercut-quy-trinh-ai-hieu-footage-truoc-khi-dung`):
   giữ máy thức (`caffeinate -i -w $$`) → job WhisperX (word-level, chạy nền, 2 clip song song) → job contact
   sheet ffmpeg (chạy SAU transcript, không chồng nhau) → sub-agent hiệu đính transcript (tuỳ chọn) → sub-agent
   **Sonnet** viết tóm tắt từng clip (10 clip/agent, tối đa 10 agent, dispatch cuốn chiếu) → **cùng người dùng
   rà lại hiểu biết về footage** (tên nhân vật, địa điểm, mạch truyện, ý đồ) và lưu vào `footage_summary`,
   `user_context` → backup.
3. **cut**: kiểm tra `library.rb <tên> ready` → **bắt buộc hỏi loại cut** → nhánh *Roughcut*: lập kế hoạch với
   người dùng (3 concept → beat → duyệt rõ ràng), rồi giao sub-agent dựng YAML; nhánh *Scene/Selects/Script/Custom*:
   main thread dựng YAML cùng người dùng, cho xem từng bản dạng bảng → `verify_media` (footage còn đó không) →
   chọn NLE → `ruby lib/buttercut/export.rb --editor fcpx|premiere|resolve <cut.yaml> <out>` → copy ra Desktop,
   `open -a "Final Cut Pro" ...` → backup → báo kết quả + ghi chú biên tập ngắn.

## Vai trò của AI và cách các phần phối hợp

- **Claude Code main thread** = người điều phối + người nói chuyện với editor; là nơi DUY NHẤT ghi `library.yaml`
  (qua lớp `Library`, có `flock` + ghi nguyên tử).
- **Sub-agent** chỉ nhận đầu vào truyền thẳng trong prompt, ghi artifact ra đĩa, trả về dòng `✓` ngắn; cấm đọc/ghi
  `library.yaml` (tránh race).
- **Code xử lý phần máy móc** (WhisperX, ffmpeg) để kết quả "giống hệt nhau dù model nào chạy"; **LLM chỉ làm phần
  phán đoán** (hiệu đính transcript, tóm tắt, lên kế hoạch, chọn cảnh/điểm cắt).
- Chi tiết mẫu phối hợp: `techniques/buttercut-mau-phoi-hop-agent-cong-kiem-tra-va-giao-tiep`.

## AI "xem" footage thế nào

AI **không bao giờ đọc file video**. Nó dùng 4 lớp, đọc từ rẻ đến đắt ("Read smallest first; grep the rest"):
1. `summaries/summary_<clip>.md` (Overview / Key Visuals / Notable Dialogue / B-Roll), đọc hết được kể cả 90+ clip;
2. `contact_sheets/<clip>_full.jpg`: 16 khung 4x4 có mốc giờ in sẵn, xem "cả clip trong một ảnh"; cần chính xác hơn
   thì tạo sheet cho một khoảng (`contact_sheet.rb <video> 02:00 02:30`);
3. transcript WhisperX JSON (segments + words có start/end): đọc lời qua `script_extractor.rb` (mỗi segment một
   dòng, không mốc), lấy điểm cắt bằng `grep` từ cần tìm;
4. `footage_summary` + `user_context` trong `library.yaml`.
Xem `ffmpeg/buttercut-contact-sheet-bang-ffmpeg-de-ai-xem-ca-clip`.

## Định dạng đầu ra và lý do

- **Cut YAML** (hợp đồng giữa AI và bộ xuất): `description`, `timeline` (tuỳ chọn: frame_rate/width/height),
  `clips[]` gồm `source_file` (chỉ tên file), `in_point`/`out_point` dạng `HH:MM:SS.ss`, `duration` (ảnh tĩnh),
  `mute`, `dialogue` (lời đã sửa chính tả), `visual_description`; `metadata.total_duration`, `created_date`.
  Mỗi cut là file mới `cuts/<slug>_<YYYYMMDD_HHMMSS>.yaml`, không ghi đè.
- **XML**: Final Cut → FCPXML 1.12; Resolve → FCPXML 1.12 (lệch frame rate thì dùng `resolve_legacy` xmeml v5);
  Premiere → xmeml v5 có filter Basic Motion để xoay/scale. Xem
  `techniques/buttercut-xuat-timeline-xml-cho-final-cut-premiere-davinci`.
- **Vì sao XML**: người dùng là editor, sản phẩm là *bản cắt thô* để họ hoàn thiện trong NLE quen thuộc
  ("We're building a roughcut, not finishing it — the editor will tighten in their NLE"). Mục tiêu chính xác ~1 giây.
- **Render**: không có; ffmpeg chỉ dùng cho contact sheet và ffprobe metadata.

## Chữ, phụ đề, hiệu ứng, âm thanh

- Core: **một track duy nhất**, mỗi clip mang tiếng của chính nó; chỉ có `mute`; FCPXML ghi `adjust-volume -13.1`
  cho mọi clip có tiếng (code không ghi lý do), `-96` khi mute. Không phụ đề, không title, không motion graphics,
  không nhạc. Skill `misc-task` dặn nói thẳng "ButterCut doesn't support it yet (subtitles, motion graphics, etc)"
  rồi đề nghị thử sửa XML trong `tmp/`, không hứa chắc.
- Bản Pro ($49/năm; mã Pro không nằm trong repo, chỉ có các "seam" `_pro` để nạp thêm): multi-track (B-roll đè lên A-roll), nhạc/voiceover riêng, đồng bộ âm thanh rời bằng
  cách "nghe" cả hai file, volume theo dB từng clip, multicam (beta, đồng bộ góc máy theo transcript), app Preview.

## Prompt, kiểm tra chất lượng, tương tác người dùng (điểm nổi bật)

- Hỏi loại cut dù người dùng đã nói "roughcut": "'Roughcut' in the user's opening request is trained vocabulary,
  not a confirmed choice".
- Lập kế hoạch: 3 concept khác cấu trúc (concept 1 thẳng thắn, 2 concept sáng tạo), beat, "Tweaks are not consent".
  Xem `scripting/buttercut-len-ke-hoach-cut-cung-nguoi-dung-truoc-khi-dung`.
- Sub-agent dựng: làm từng beat, "After three beats look back", vòng rà soát theo format, trả ghi chú biên tập kèm
  phương án thay thế. Xem `techniques/buttercut-agent-dung-ban-cat-tho-theo-beat-va-vong-ra-soat`.
- Cắt theo từng từ: `techniques/buttercut-cat-theo-moc-tung-tu-giu-thoai-lien-mach`.
- Hiệu đính transcript: `audio/buttercut-hieu-dinh-transcript-ma-khong-pha-moc-thoi-gian`.
- Cổng kiểm tra: `ready` trước khi dựng, `verify_media` trước khi xuất (ok/missing/phantom, không bao giờ tự relink),
  từ chối clip có out ≤ in, validate FCPXML bằng `xmllint --dtdvalid`, kiểm tra migration mỗi lần đọc library.
- Nói như editor: giấu YAML và tên công cụ, tên library bỏ gạch nối, hỏi từng câu, dùng `AskUserQuestion`.

## Phụ thuộc, cách chạy, giới hạn

- Ruby 3.3.6 (gem `nokogiri`), Python 3.12.8, FFmpeg 8.1.x có `drawtext` (script tải bản ghim + SHA-256),
  WhisperX 3.8.6 + pyannote-audio 4.0.7 + torch 2.8.0 (ghim chặt trong `requirements.txt`), chạy CPU float32,
  model mặc định `small`; `parallel_jobs: 2` (WhisperX tốn RAM).
- macOS Apple Silicon là chính; Windows 10/11 beta (Git Bash); Linux không hỗ trợ chính thức.
- Chạy: `git clone` → mở trong Claude Code → skill `/setup` → nói "tạo library mới" hoặc gõ `/buttercut`.
- Giới hạn: một track; không phụ đề/đồ hoạ/nhạc (core); độ chính xác ~1s; mỗi clip chỉ "nhìn" 16 khung (phải zoom
  khi cần); Resolve + FCPXML không link được clip lệch frame rate; danh sách định dạng nhập hẹp (mov, mp4, mts,
  m2ts, mxf, avi; jpg, jpeg, png; không mkv/webm/heic); tốn token (tác giả: thư viện 37 phút, 93 clip dùng khoảng
  10% hạn mức 5 giờ của gói Max 5x sau bản 0.7.2).

## Chỗ tài liệu lệch với code (tin code)

- Contact sheet clip ≤ 10s: `skills/contact-sheet/SKILL.md` ghi "4 frames in a 2x2 grid", code dùng 8 khung 4x2
  (dọc: 9 khung 3x3).
- `docs/basic-xml-generation.md` dùng `editor: :fcp7`; code chỉ nhận `:fcpx, :resolve, :resolve_legacy, :premiere`.
- `skills/setup/advanced-setup.md` còn ghim `whisperx==3.4.2`, `pyannote-audio==3.4.0`; `requirements.txt` hiện là
  3.8.6 / 4.0.7.
- Số bước bị lệch sau khi thêm bước kiểm tra footage: `roughcut_path.md`/`direct_path.md` ghi "Editor resolution ...
  (SKILL.md step 4)" và "Continue at step 5 of SKILL.md (Export the YAML)", trong khi `cut/SKILL.md` hiện là bước 4
  `verify_media`, bước 5 chọn NLE, bước 6 xuất; `roughcut_planning.md` lại nói NLE "already resolved". Không nguy hiểm
  vì `export_core.rb` tự kiểm tra media trước khi xuất, nhưng là bài học: prompt nhiều file phải đánh số bằng tên bước,
  không bằng số.

## License (quan trọng)

- Hiện tại: **PolyForm Noncommercial 1.0.0 + "Additional Permission: Commercial Output"**,
  `Required Notice: Copyright 2025 TubeSalt LLC`. Được dùng ButterCut để làm video thương mại (output thuộc về
  người dùng); **không** được bán, host SaaS, hay nhúng phần mềm (kể cả bản sửa) vào sản phẩm/plugin/dịch vụ
  thương mại. Dùng cá nhân, nghiên cứu, học tập: được, nhưng khi phân phối phải kèm điều khoản và dòng
  `Required Notice`.
- Lịch sử: commit đầu `8fffff0` (10/11/2025) là **MIT** ("Copyright (c) 2025 Andrew Ford"); chuyển sang PolyForm
  ở commit `d9ac5da` (07/05/2026). Theo CHANGELOG, bản 0.6.0 (03/05/2026: bước lập kế hoạch, cắt theo từng từ) ra
  trước mốc này, còn contact sheet (0.7.0, 21/05/2026) ra sau. Các bản phát hành trước mốc về nguyên tắc vẫn theo MIT
  (phải giữ dòng copyright), nhưng đó là code Ruby cũ, vedit viết bằng Python nên giá trị chép code thấp.
- PR gửi vào repo chuyển giao bản quyền cho TubeSalt LLC.
- **Kết luận cho vedit**: học ý tưởng, quy trình, thông số và tự viết lại bằng Python với lời văn riêng; **không
  chép nguyên code hay prompt hiện tại** vào vedit (vedit sẽ bị ràng buộc phi thương mại). Đây là đánh giá kỹ thuật,
  không phải tư vấn pháp lý; nếu định dùng thương mại thì cần người dùng tự kiểm tra.

## So sánh nhanh với vedit

| Khía cạnh | ButterCut | vedit |
|---|---|---|
| Người dùng | editor/YouTuber, hoàn thiện trong NLE | người làm video ngắn, cần file MP4 xong |
| Đầu vào | library nhiều clip + ảnh | 1 video/dự án (EditPlan có `sources` nhưng `analyze` nhận 1 file) |
| Hiểu footage | transcript WhisperX word-level, contact sheet, tóm tắt từng clip, `user_context` | scene/silence detect, tối đa 16 khung rời 512px, transcript faster-whisper **tuỳ chọn** (chưa cài trong `setup.sh`; dự án gần nhất có `transcript: null`) |
| Lên kế hoạch | hỏi loại cut, 3 concept, duyệt rõ ràng | Agent 2 tự chọn concept, chỉ liệt kê phương án hook/tiêu đề |
| Điểm cắt | mốc từng từ, `HH:MM:SS.ss` | giây nguồn, khung nguyên; chưa có công cụ tra mốc từ |
| Đầu ra | XML timeline | MP4 + thumbnail (render ffmpeg) |
| Chữ/đồ hoạ/âm thanh | không (core) | ASS chữ động, phụ đề karaoke, đồ hoạ vector, SFX tổng hợp, ducking, loudnorm |
| QA | `ready`, `verify_media`, DTD, rà soát biên tập | `validate` schema + media, xem khung preview |
| Phiên bản | cut mới mỗi lần, có timestamp | ghi đè `edit_plan.json`, `final.mp4` |

## Áp dụng vào vedit

**Đã có**: render hoàn chỉnh với lớp sáng tạo mạnh hơn hẳn ButterCut core; QA hình ảnh bằng preview; CLI tách
bước máy móc (`analyze`, `validate`, `render`, `frame --grid`) khỏi agent.

**Còn thiếu** so với ButterCut: bước duyệt concept với người dùng, contact sheet, transcript mặc định + tra mốc từ,
hiệu đính transcript, vòng rà soát biên tập, bộ nhớ `user_context`, đa clip, phiên bản hoá đầu ra, xuất timeline.

**Đề xuất theo ưu tiên** (chi tiết trong từng ghi chú con):
1. Cổng duyệt concept (3 phương án, 1 an toàn + 2 sáng tạo) ở main thread trước khi viết EditPlan: trị đúng lỗi
   "chưa đúng ý". Dễ đến vừa.
2. Contact sheet trong `vedit analyze` + lệnh zoom theo khoảng thời gian. Dễ (công thức đã chạy thử).
3. Cài transcript mặc định (`.[transcribe]`) và kiểm tra tải model; cân nhắc WhisperX (có mô hình căn chỉnh
   tiếng Việt). Dễ đến vừa.
4. Vòng rà soát biên tập 2 lượt + ghi chú phương án thay thế trong prompt Agent 2/3. Dễ.
5. Công cụ tra mốc từ + cảnh báo cắt giữa từ trong `vedit validate`. Vừa.
6. Hiệu đính transcript tiếng Việt theo luật "giữ số từ, không đổi mốc". Vừa.
7. `user_context` cho dự án + hồ sơ sở thích người dùng; phiên bản hoá `edit_plan`/render. Dễ.
8. Xuất FCPXML/xmeml/SRT cho người muốn chỉnh tay: chỉ làm sau khi hỏi người dùng có dùng NLE nào (CapCut nhập
   XML hay không thì chưa kiểm chứng). Vừa đến khó.
