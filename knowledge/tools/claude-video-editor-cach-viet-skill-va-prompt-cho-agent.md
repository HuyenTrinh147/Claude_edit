---
title: claude-video-editor: Cách viết skill và prompt cho agent
category: tools
tags: [claude-video-editor, prompt engineering, skill, sub-agent, hard rules, guardrails, gate, agent dựng video]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-studio/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/house-style.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/motion-principles.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/references/typography.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/make-a-video/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-1-capture.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-4-storyboard.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/website-to-hyperframes/references/step-6-build.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/generate-footage/scripts/check_skill_md.py
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/MOTION_PHILOSOPHY.md
---
# claude-video-editor: Cách viết skill và prompt cho agent

Repo này đáng học nhất ở **cách viết hướng dẫn cho LLM** — nhiều mẫu câu giúp agent bớt "dựng kiểu AI" (an toàn,
đồng phục, thiếu sáng tạo). Các trích dẫn giữ nguyên tiếng Anh.

## 1. Tách "đúng kỹ thuật" khỏi "gu" — ví dụ chứ không phải mệnh lệnh

`video-use/SKILL.md` mở đầu bằng nguyên tắc:

> "Every specific value, preset, font, color, duration, pitch structure, and technique in this document is a
> *worked example* from one proven video — not a mandate. … **The only things you MUST do are in the Hard Rules
> section below.** Everything else is yours."

> "**Invent freely.** If the material calls for a technique not described here — split-screen, picture-in-picture,
> lower-third identity cards, reaction cuts, speed ramps, freeze frames, … — build it. … Do not wait for permission."

Rồi một mục **Hard Rules (non-negotiable)** gồm 12 quy tắc chỉ thuần kỹ thuật (subtitle áp cuối, fade âm 30ms,
không cắt giữa từ, cache transcript, duyệt chiến lược trước khi cắt...). Hiệu ứng: agent biết chỗ nào **phải** cứng
nhắc, chỗ nào **được** sáng tạo — thay vì chép nguyên các con số ví dụ cho mọi video.

## 2. "Guardrails" gọi tên chính thói quen mặc định của model

`motion-principles.md` và `typography.md` viết thẳng vào điểm mù của LLM:

> "You know these rules but you violate them. Stop."
> "**Don't use the same ease on every tween.** You default to `power2.out` on everything."
> "You default to 0.4-0.5s for everything. The slowest scene should be 3× slower than the fastest."
> "You crossfade everything. Use hard cuts for disruption and register shifts."
> "**Video sizes, not web sizes.** … You will try to use 14px. Don't."

Và danh sách "Lazy Defaults to Question" (`house-style.md`) — các dấu hiệu "AI design tell": chữ gradient, sọc
nhấn mép trái, cyan trên nền tối, `#000`/`#fff` thuần, lưới thẻ giống hệt nhau, mọi thứ căn giữa. Không cấm tuyệt
đối: "The goal is intentionality, not avoidance."

## 3. Cổng cứng (HARD-GATE) sinh ra file

`hyperframes/SKILL.md` đặt `<HARD-GATE>` "Visual Identity Gate": chưa có DESIGN.md / style người dùng nêu / 3 câu trả
lời (mood, nền sáng/tối, màu-font-tham chiếu thương hiệu) thì **không được viết HTML**. Kèm câu tự kiểm tra rất cụ thể:

> "If you're reaching for `#333`, `#3b82f6`, or `Roboto` — you skipped this step."

`make-a-video`: "Two phases, eight sequential gates. Every gate produces a concrete artifact the next gate consumes."
(BRIEF.md → STORYBOARD.md → compositions → draft → frames → final). Artifact giữa các bước = bộ nhớ ngoài + điểm duyệt.

## 4. Câu hỏi tự soát thay cho checklist khô

MOTION_PHILOSOPHY có "What Would Infinite Do?" — 10 câu hỏi trước khi chốt một motion graphic, ví dụ: "Could I cut
this scene in half? If yes, do it." · "Is this color carrying a meaning? If no, kill it." · "Does the type SCALE
during its reveal, or just fade in? Fading in is the lowest-effort move." · "Where does the viewer rest?"

Storyboard: "Every element gets a verb. If you can't name the verb, the element is not yet designed." Và ví dụ đối
lập **Mediocre vs Great** (mô tả pixel vs mô tả trải nghiệm) — dạy bằng cặp ví dụ hiệu quả hơn tính từ chung chung.

## 5. Brief cho sub-agent (mẫu 10 điểm)

Mỗi animation = một sub-agent, spawn song song; prompt phải **tự đủ** vì sub-agent không có context cha:

1. Mục tiêu 1 câu: "Build ONE animation: [spec]. Nothing else."
2. Đường dẫn output tuyệt đối.
3. Thông số kỹ thuật: độ phân giải, fps, codec, pix_fmt, CRF, thời lượng.
4. Palette bằng giá trị cụ thể (hex/RGB).
5. Font: đường dẫn + index.
6. Timeline từng khung (cái gì xảy ra lúc nào, easing gì).
7. Anti-list ("no chrome, no extras, no titles unless specified").
8. Mẫu code tham chiếu (chép helper inline, không import chéo slot).
9. Checklist bàn giao (script, render, ffprobe độ dài, báo cáo).
10. "**Do not ask questions. If anything is ambiguous, pick the most obvious interpretation and proceed.**"

"One sub-agent = one file (unique filenames, parallel agents don't overwrite each other)."

`website-to-hyperframes/step-6`: "**Pass file PATHS, not file contents.** The #1 failure mode is reading an asset file
and pasting its SVG/image data into the sub-agent prompt." Mỗi beat một sub-agent vì "context is full … the detailed
rules below compete with thousands of tokens of prior work".

Brief chọn take (editor sub-agent) có cấu trúc INPUTS / archetype / RULES / OUTPUT JSON và câu tự sửa: "If over
budget, revise: drop a beat or trim tails. Report total and self-correct." — xem
`techniques/claude-video-editor-doc-video-bang-transcript-va-quy-tac-cat`.

## 6. Quản lý context

- "Write-down-and-forget" (step-1-capture): đọc mỗi file xong viết 1–2 câu tóm tắt — "These summaries are your working
  memory — the raw file content may be cleared from context later."
- Nhiều ảnh (30+) → giao sub-agent lập catalog một dòng/ảnh.
- Tham chiếu tải theo nhu cầu: SKILL.md chính ngắn, `references/*.md` chỉ đọc khi cần ("loaded on demand").

## 7. Ví dụ hoàn chỉnh để "pattern-match"

README: "Pattern-match it; don't start from a blank file." `examples/promo/` có đủ DESIGN.md, SCRIPT.md,
STORYBOARD.md và `index.html` thật của một video đã xuất bản.

## 8. Thất bại có giới hạn, trung thực

- Self-eval tối đa 3 vòng: "if issues remain after 3, flag them to the user rather than looping forever."
- "Verify your own output before showing it to the user. If you wouldn't ship it, don't present it."
- "Lint passing ≠ design working. VIEW THE FRAMES."
- Tài liệu skill cũng có test: `check_skill_md.py` kiểm cấu trúc SKILL.md (dịch vụ bên thứ ba chỉ được nhắc dưới
  heading "Optional…"), viết sau một RCA — prompt được bảo trì như code.

## Áp dụng vào vedit

**Đã có**: `.claude/agents/video-editor.md` và `video-scriptwriter.md` có quy trình, nhắc "lớp sáng tạo", trỏ tới kho
kiến thức; Agent 3 có vòng preview 1–3 lần.

**Còn thiếu**: không tách Hard Rules / taste (mọi con số đều như mệnh lệnh → video đồng phục); không có guardrails gọi
tên thói quen mặc định; không có cổng duyệt sinh file; không có ví dụ EditPlan mẫu xuất sắc để bắt chước.

**Đề xuất (ưu tiên)**:
1. Thêm vào prompt Agent 2/3 mục **"Quy tắc cứng"** (chỉ kỹ thuật, ví dụ: clip start/end = giây nguồn; texts/captions
   = giây timeline; không cắt giữa từ, đệm 30–200ms; chữ trong vùng an toàn 12% trên/22% dưới/12% phải; tối đa 2 đồ
   hoạ cùng lúc; `vedit validate` sạch; xem khung hình trước khi xuất) và câu "mọi con số khác là ví dụ, hãy quyết
   theo chất liệu". Dễ.
2. Thêm **"Guardrails" tiếng Việt** gọi tên thói quen của chính agent vedit: "Bạn hay đặt mọi chữ `center` + `pop`",
   "Bạn hay dùng một `look` cho mọi thể loại", "Bạn hay quên SFX khớp đồ hoạ", "Bạn hay để clip 3–4s đều nhau",
   "Bạn hay mở đầu bằng chữ tiêu đề tĩnh thay vì hành động". Dễ.
3. **Gate sinh file**: Agent 2 ghi `script/strategy.md` (chiến lược + style profile) → người điều phối đưa người dùng
   duyệt → mới viết `edit_plan.json`. Dễ.
4. Tạo **thư mục ví dụ** `knowledge/` hoặc `examples/` với 1–2 EditPlan "chuẩn editor" (đã render đẹp) để agent
   pattern-match. Vừa.
5. Khi cần nhiều phần độc lập (vd 3 phương án hook, nhiều biến thể), dùng **brief 10 điểm** cho sub-agent song song
   và "Do not ask questions…". Dễ.
