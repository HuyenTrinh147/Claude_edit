---
title: buttercut: Mẫu phối hợp agent, cổng kiểm tra và giao tiếp
category: techniques
tags: [agent, sub-agent, điều phối, kiểm tra chất lượng, ux, giao tiếp, claude code, buttercut]
updated: 2026-10-31
sources:
  - https://github.com/barefootford/buttercut/blob/main/AGENTS.md
  - https://github.com/barefootford/buttercut/blob/main/skills/analyze-video/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/analyze-video/agent_prompt.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/buttercut/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/misc-task/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/report-bug/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/missing_footage.md
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/job.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/job_runner.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/footage_processor.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/run_log.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/library.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/library.md
  - https://github.com/barefootford/buttercut/blob/main/templates/settings_template.yaml
  - https://github.com/barefootford/buttercut/blob/main/.claude/settings.json
---
# buttercut: Mẫu phối hợp agent, cổng kiểm tra và giao tiếp

Những mẫu thiết kế giúp ButterCut chạy ổn định với người dùng không rành kỹ thuật, độc lập với chuyện dựng hình.

## 1. Máy móc vào code, phán đoán cho LLM

`job.rb`: các bước WhisperX/ffmpeg từng nằm trong prompt nên "came out differently depending on which model read the
prompt (different ordering, parallelism, batching). Moving them into Jobs makes the work identical on every run".
- Job = 1 clip, thuần (chỉ nhận tham số), idempotent; `JobRunner` (thread pool, `parallel_jobs` mặc định 2) giữ quyền
  ghi trạng thái; chạy lại chỉ làm phần còn thiếu, `--force --clips a.mov` để làm lại.
- Hai bước máy móc chạy **nối tiếp** (transcript xong mới contact sheet) để tổng tải không vượt trần.
- Log mỗi thư viện mỗi ngày `tmp/logs/processing/<lib>/<YYYY-MM-DD>.log`, dòng có giờ; agent `tail -f | grep` để báo
  tiến độ.
- Phần phán đoán (hiệu đính transcript, tóm tắt, lên kế hoạch, chọn cảnh) ở lại với Claude.

## 2. Một người ghi trạng thái chung

- Chỉ main thread ghi `library.yaml`, qua lớp `Library` (khoá `flock` file `.lock` riêng + ghi file tạm rồi `rename`
  nguyên tử); "Sub-agents must NEVER call it (race conditions on the shared file)".
- Sub-agent nhận mọi đầu vào **trong prompt** ("Do NOT read library.yaml or settings.yaml"), ghi artifact ra đĩa, trả
  lời cực ngắn (`✓ <clip> analyzed`), không dán nội dung vào câu trả lời. Nếu sub-agent lỡ dán (tưởng `Write` bị chặn)
  thì parent tự ghi ra file, không chạy lại.
- Đánh dấu tiến độ **từng đợt** (`complete summary a.mov b.mov`), không dồn cuối, để hỏng giữa chừng vẫn giữ được.
- `complete` kiểm tra nguyên khối: clip có trong thư viện, file artifact tồn tại, loại media phù hợp; sai một là không
  ghi gì.

## 3. Chia việc cho sub-agent

- Tóm tắt: 10 clip/agent, tối đa 10 agent, **dispatch cuốn chiếu** (xong agent nào phát agent mới ngay).
- Chọn model theo việc: Sonnet cho đọc ảnh (chi tiết hơn Haiku); hiệu đính 2–4 agent song song.
- Prompt sub-agent nằm ở file riêng (`agent_prompt.md`), parent "inline" nội dung đó khi gọi; `SKILL.md` là bản giao
  việc cho parent, không đưa cho sub-agent.
- Sub-agent dựng làm việc bất đồng bộ, không hỏi người dùng; mọi hội thoại ở main thread.

## 4. Cổng kiểm tra (gate)

| Cổng | Khi nào | Hành vi |
|---|---|---|
| Migration | mỗi lần đọc `library.yaml` | thiếu trường/tên cũ → chạy migrate cho mọi thư viện trước khi làm gì khác |
| `ready` | trước khi dựng | exit 0/1; chưa xong thì dừng, chỉ sang `process-library`, "Don't try to cut around missing clips" |
| `verify_media` | ngay trước khi xuất (không phải lúc đầu) | ok/missing/phantom; gợi ý relink nhưng "Never relink automatically" |
| Kiểm tra cut | khi xuất | từ chối clip thiếu nguồn, out ≤ in, ảnh thiếu `duration` |
| DTD | sau khi xuất FCPXML | `xmllint --dtdvalid`, sai thì exit 1 |
| Báo lỗi | khi lỗi do chính ButterCut | hỏi đồng ý một lần (always/ask/never), lọc tên clip/thư viện/transcript, không gửi trùng |

Đặt `verify_media` sát lúc xuất là có chủ đích: người dùng vẫn lên kế hoạch được khi ổ cứng đang rút.

## 5. Giao tiếp với người dùng

- **Nói như editor**: "rough cut, sequence, beat, B-roll..."; giấu YAML, tên công cụ, trường dữ liệu. Ví dụ trong
  skill: "Bad: 'Got it — 3-second podium clips only. I'll write the YAML now.' Good: 'Got it. Three second podium
  clips only. I'll start the edit.'"; tên thư viện bỏ gạch nối và viết hoa ("Wedding 94 library").
- Hỏi **từng câu một**, bằng `AskUserQuestion` (nút chọn), sắp lựa chọn theo độ mới; không giải thích vì sao hỏi.
- **Hỏi một lần, nhớ mãi**: editor ưa dùng, copy ra Desktop, tự mở NLE, thư mục backup lưu ở `settings.yaml`;
  `user_context` lưu điều đã biết về người dùng/nhân vật.
- **Todo hiển thị** bằng lời thường kèm bộ đếm ("Create transcripts (5/20)").
- **Menu cửa trước** (`/buttercut`, `/bc`): chào ngắn, hỏi muốn làm gì (cut mới / thêm footage / việc lặt vặt) rồi
  chuyển skill.
- **Việc ngoài khả năng** (`misc-task`): nói thẳng là chưa hỗ trợ, đề nghị thử theo kiểu best-effort, làm trong `tmp/`,
  không sửa `lib/`; thành công thì đề nghị lưu cách làm thành skill riêng `user-...`.
- "Flag areas needing human judgment rather than making assumptions"; không bao giờ sửa file nguồn; không xoá thư mục
  "phantom" còn file bên trong.
- Kết quả cuối: đường dẫn file + một câu hướng dẫn nhập + ghi chú biên tập rút gọn; không đưa file nội bộ.

## 6. Quyền chạy lệnh

`.claude/settings.json` cho phép sẵn các lệnh của quy trình (`ruby lib/buttercut/*.rb`, `ffmpeg`, `ffprobe`,
`whisperx`, ghi trong `libraries/**`, xoá trong `tmp/**`) để người dùng không bị hỏi quyền liên tục.

## Áp dụng vào vedit

**Đã có**: CLI cho bước máy móc (`analyze`, `validate`, `render`, `frame`); 3 subagent + 4 skill tiếng Việt; Agent 3
tự kiểm tra preview; skill dặn báo tiến độ sau mỗi bước.

**Còn thiếu**: hội thoại duyệt ở main thread (subagent không hỏi được người dùng); trí nhớ sở thích người dùng; todo
tiến độ; phiên bản hoá kết quả; nhánh "việc ngoài khả năng"; cổng "sẵn sàng" (vd chưa có transcript thì nói rõ ảnh
hưởng tới phụ đề trước khi dựng).

**Đề xuất theo ưu tiên**:
1. Chuyển mọi câu hỏi/duyệt (loại video, chọn concept, xác nhận hiểu footage) về main thread trong skill
   `/lam-video`; subagent chỉ nhận đầu vào đã chốt và trả kết quả + ghi chú ngắn. Dễ.
2. Hồ sơ sở thích người dùng được commit (vd `profile/nguoi-dung.md`: nền tảng, độ dài, font, màu thương hiệu, thích/
   ghét hiệu ứng, phản hồi cũ như "thiếu sáng tạo"), main thread đọc đầu phiên và cập nhật sau mỗi phản hồi. Dễ.
3. Todo hiển thị bằng lời thường ("Phân tích video", "Chọn ý tưởng", "Dựng bản xem trước", "Xuất video") kèm bộ đếm khi
   có nhiều clip. Dễ.
4. Cổng "sẵn sàng" trước khi viết EditPlan: kiểm tra có transcript, contact sheet, `user_context`; thiếu thì nói rõ hậu
   quả và hỏi tiếp tục hay bổ sung. Dễ.
5. Ghi log có giờ cho `analyze`/`render` vào `projects/<slug>/logs/` để xem lại khi lỗi. Dễ.
6. Nhánh "việc lặt vặt" (tách tiếng, cắt nhanh một đoạn, đổi định dạng, ảnh thumbnail) với quy ước thư mục ra, và gợi
   ý lưu cách làm thành skill khi thành công. Vừa.
