---
title: claude-video-editor: Tổng quan repo và so sánh với vedit
category: tools
tags: [claude-video-editor, video-use, hyperframes, claude code, plugin, kiến trúc, license, so sánh vedit]
updated: 2026-10-31
sources:
  - https://github.com/assafkip/claude-video-editor
  - https://github.com/assafkip/claude-video-editor/blob/master/README.md
  - https://github.com/assafkip/claude-video-editor/blob/master/LICENSE
  - https://github.com/assafkip/claude-video-editor/blob/master/LICENSES/video-use.LICENSE
  - https://github.com/assafkip/claude-video-editor/blob/master/LICENSES/hyperframes-student-kit.LICENSE
  - https://github.com/assafkip/claude-video-editor/blob/master/CHANGELOG.md
  - https://github.com/assafkip/claude-video-editor/blob/master/install.sh
  - https://github.com/assafkip/claude-video-editor/blob/master/.claude-plugin/plugin.json
  - https://github.com/assafkip/claude-video-editor/blob/master/.claude-plugin/marketplace.json
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-studio/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/README.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/install.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/video-use/helpers/render.py
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/hyperframes/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/skills/generate-footage/SKILL.md
  - https://github.com/assafkip/claude-video-editor/blob/master/templates/project/project.md
  - https://github.com/assafkip/claude-video-editor/blob/master/docs/rca/rca-generate-footage-animation-2026-06-11.md
  - https://github.com/heygen-com/hyperframes
  - https://raw.githubusercontent.com/heygen-com/hyperframes/main/LICENSE
  - https://github.com/browser-use/video-use
  - https://raw.githubusercontent.com/browser-use/video-use/main/SKILL.md
  - https://raw.githubusercontent.com/browser-use/video-use/main/helpers/render.py
  - https://raw.githubusercontent.com/browser-use/video-use/main/helpers/transcribe.py
  - https://github.com/nateherkai/hyperframes-student-kit
---
# claude-video-editor: Tổng quan repo và so sánh với vedit

> Quan sát ngày 2026-10-31 trên bản clone tại `research/repos/claude-video-editor` (commit `3f07b69`, 2026-06-11,
> nhánh `master`). Trang GitHub lúc đó: 37 sao, 8 fork, 11 commit. CHANGELOG ghi 0.3.0 nhưng `plugin.json` vẫn là
> 0.2.0 và mô tả còn nhắc "Wan 2.2 image-to-video" đã bị gỡ ở 0.3.0 — tài liệu chưa đồng bộ.

## 1. Mục đích

Plugin cho **Claude Code** để "Use Claude to edit videos and add captions — or generate a video from nothing":
thả footage vào thư mục, nói yêu cầu bằng lời, nhận `edit/final.mp4`. Hai lối vào:

- **Sửa footage có sẵn** (talking head, tutorial, montage, promo...): cắt từ đệm/khoảng chết, phụ đề, grade màu,
  motion graphics, speed ramp.
- **Tạo video từ con số 0** (`generate-footage`): giọng đọc trước, rồi ảnh tĩnh (AI, ảnh chụp màn hình, HTML tự
  render) được "làm sống" bằng chuyển động máy + hiệu ứng khí quyển — demo là video giải thích 2:46, 16 cảnh.

## 2. Kiến trúc: 4 lớp gộp thành một plugin

| Lớp | Thư mục | Vai trò | Nguồn & license |
|---|---|---|---|
| Điều phối | `skills/video-studio/` | Skill định tuyến giữa các lớp, "standard loop", hard rules | Gốc của repo — MIT + Commons Clause |
| Engine cắt | `skills/video-use/` (`SKILL.md` + `helpers/*.py`) | transcribe → pack → LLM suy luận → EDL → render → self-eval | browser-use/video-use — MIT |
| Motion | `skills/hyperframes*`, `gsap`, `website-to-hyperframes` | HTML + GSAP → headless Chrome → video (overlay alpha) | heygen-com/hyperframes — Apache-2.0 |
| Gu thẩm mỹ | `make-a-video`, `short-form-video`, `docs/MOTION_PHILOSOPHY.md` | Storyboard, brand, nhịp, "taste" | hyperframes-student-kit (Nate Herk) — MIT; upstream nay đổi tên thành herk-edit-kit |
| Tạo footage | `skills/generate-footage/` + `recipes/04` + `templates/animate-stills` | TTS ElevenLabs v3 → ảnh tĩnh → Ken Burns xác định | Gốc — MIT + Commons Clause |

Ngoài ra `skills/video-use/skills/manim-video/` (Manim, kiểu 3Blue1Brown) cho sơ đồ/công thức.

**Đóng gói**: `.claude-plugin/marketplace.json` + `plugin.json` với `"skills": "./skills/"`. Không có định nghĩa
subagent tĩnh (`.claude/agents`), không có MCP server riêng. Claude đọc skill theo `description`, và **tự spawn
sub-agent bằng `Agent` tool** ở 3 chỗ: (1) chọn take tốt nhất cho từng beat (editor brief, trả JSON EDL),
(2) mỗi animation một sub-agent chạy **song song** ("Never sequential"), (3) `website-to-hyperframes`: mỗi beat một
sub-agent để có context sạch. Chi tiết prompt: xem `tools/claude-video-editor-cach-viet-skill-va-prompt-cho-agent`.

Phân vai rõ: **Claude = đạo diễn/biên tập** (đọc transcript, hỏi, đề xuất chiến lược, viết EDL/HTML);
**script Python/CLI = "production-correctness"** (cắt, fade, concat, overlay, subtitle, loudnorm).
Câu khẩu hiệu: "Production-correctness rules are hard; everything else is artistic freedom."

## 3. Luồng xử lý: video thô → final.mp4

```
Inventory (ffprobe; KHÔNG tự transcribe khi chưa được yêu cầu)
 → transcribe_batch.py  (ElevenLabs Scribe v1: verbatim, diarize, audio events, word timestamps; cache theo file)
 → pack_transcripts.py  → takes_packed.md (dòng cụm từ [start-end], ngắt ở im lặng ≥0.5s / đổi người nói)
 → pre-scan lỗi nói → hỏi người dùng theo chất liệu → CHIẾN LƯỢC 4–8 câu → CHỜ ĐỒNG Ý
 → edl.json  (ranges giây nguồn + beat/quote/reason; editor sub-agent khi nhiều take)
 → animation slots (HyperFrames/Remotion/Manim/PIL, song song) → render --format mov (ProRes 4444 có alpha)
 → render.py: cắt từng đoạn (+grade +afade 30ms) → concat -c copy → overlay (dời PTS) → subtitles CUỐI → loudnorm 2 lượt
 → self-eval: timeline_view trên BẢN RENDER ở mọi điểm cắt ±1.5s + 2s đầu/cuối + 2–3 điểm giữa + ffprobe độ dài
   (sửa → render lại, tối đa 3 vòng; quá 3 vòng thì báo người dùng)
 → preview → góp ý bằng lời → render lại (không transcribe lại) → final → ghi project.md
```

Lối "tạo từ ảnh tĩnh": kịch bản có audio tag → `tts_v3.py` → transcribe → khoá cửa sổ cảnh theo ranh giới câu →
một ảnh/cảnh → `manifest.json` → `build_scenes.py` → lint/render → mux giọng bằng ffmpeg → `motion_check.py`
(chứng minh có chuyển động) + `volumedetect` + contact sheet.

## 4. AI "xem" video thế nào

- **Không xem từng khung**. README: "Naive approach: 30,000 frames × 1,500 tokens = 45M tokens of noise. Video Use:
  12KB text + a handful of PNGs." Giống browser-use đưa DOM thay vì ảnh chụp màn hình.
- Lớp 1 (luôn nạp): transcript cấp từ, gói thành `takes_packed.md`. Lớp 2 (theo yêu cầu): `timeline_view.py` vẽ
  PNG = dải N khung + waveform + nhãn từ + dải im lặng ≥400ms, chỉ dùng **ở điểm quyết định** — "Not a scan tool".
- Quyết định cắt **audio-first**: điểm cắt từ ranh giới từ và khoảng lặng, rồi mới soi hình. Chi tiết:
  `techniques/claude-video-editor-doc-video-bang-transcript-va-quy-tac-cat`.

## 5. EDL, render, chữ, đồ hoạ, màu, âm thanh (tóm tắt)

- **EDL** (`edl.json`): `sources`, `ranges[{source,start,end,beat,quote,reason}]`, `grade` (preset | chuỗi filter |
  `auto`), `overlays[{file,start_in_output,duration}]`, `subtitles` (SRT), `total_duration_s`.
- **Render** (`helpers/render.py`): `-ss` trước `-i`; scale cạnh dài về 1920 (giữ hướng dọc/ngang — **không** tự
  crop 16:9→9:16); libx264 `fast` CRF 20 (preview `medium` CRF 22, draft 720p `ultrafast` CRF 28); **ép `-r 24`**
  khi cắt đoạn; tự tonemap HDR (HLG/PQ) → SDR; composite cuối CRF 18; loudnorm 2 lượt −14 LUFS/−1 dBTP/LRA 11.
- **Chữ/phụ đề**: SRT 2 từ/dòng VIẾT HOA burn bằng `subtitles` + `force_style` (Helvetica 18 bold, MarginV=90);
  hoặc lower-third HTML render thành `.mov` alpha (`examples/captions`). Phụ đề **luôn áp CUỐI** chuỗi filter.
- **Đồ hoạ/hiệu ứng**: HyperFrames (HTML+GSAP), Remotion, Manim hoặc PIL + PNG sequence, chọn theo từng "slot".
- **Chuyển cảnh**: engine cắt chủ yếu cắt thẳng + overlay; lớp HyperFrames có catalog CSS/shader (xem
  `techniques/claude-video-editor-chon-chuyen-canh-theo-y-nghia`).
- **Màu**: `grade.py` (preset `subtle`, `neutral_punch`, `warm_cinematic`, hoặc `auto` đo signalstats, giới hạn ±8%).
- **Âm thanh**: afade 30ms mọi biên đoạn; loudnorm 2 lượt; giọng đọc ElevenLabs v3 (audio tag) hoặc Kokoro cục bộ.

## 6. Kiểm tra chất lượng & tương tác

- Tự kiểm tra trước khi đưa người dùng xem ("If you wouldn't ship it, don't present it"), tối đa 3 vòng; lớp
  HyperFrames có `lint`, `validate` (audit tương phản WCAG), `animation-map` (vùng chết, va chạm), `motion_check`,
  trích khung "đúng từng chữ" và **Read mọi PNG** — xem `techniques/claude-video-editor-vong-tu-kiem-tra-chat-luong-sau-render`.
- Tương tác: **Ask → confirm → execute → iterate → persist**, chiến lược phải được duyệt; bộ nhớ phiên trong
  `project.md` — xem `techniques/claude-video-editor-quy-trinh-hoi-chot-dung-va-ghi-nho`.

## 7. Phụ thuộc & cách chạy

- Hệ thống: `ffmpeg`/`ffprobe`, Node ≥ 22 (`npx hyperframes`, `install.sh` ghim `hyperframes@0.6.70`, ví dụ ghim
  0.6.88), Google Chrome/Chromium (render headless), Python ≥ 3.10 (venv riêng cho video-use: `requests`, `librosa`,
  `matplotlib`, `pillow`, `numpy`); `yt-dlp` tuỳ chọn.
- Khoá duy nhất: `ELEVENLABS_API_KEY` — Scribe để transcribe (README: "free tier covers transcription"; install.md
  vẫn dặn không transcribe thử vì "Scribe costs real money") và v3 TTS (tốn credit của gói).
- Cài: `git clone … && ./install.sh`, rồi trong Claude Code: `/plugin marketplace add ./` và
  `/plugin install claude-video-editor`. Dùng: `cp -r templates/project ~/my-video`, thả clip vào `sources/`,
  nói "edit these into a 60-second promo". Kết quả trong `edit/`.

## 8. Giới hạn quan sát được khi đọc mã

- Bước "hiểu video" phụ thuộc dịch vụ ngoài tính credit (Scribe); SKILL video-use còn xếp "Running Whisper locally
  on CPU" vào anti-pattern (chậm, chuẩn hoá mất từ đệm).
- Nặng: Node + Chrome headless cho mọi overlay; mỗi caption/overlay là một lần render HTML riêng.
- `render.py` ép 24 fps và 1080p cạnh dài; không có reframe dọc; overlay phải là video riêng.
- **Bản video-use vendored đã cũ**: so với `browser-use/video-use` nhánh main (đối chiếu 2026-10-31), `SKILL.md` khác
  22 dòng (upstream thêm: đo `ebur128` theo từng đoạn, **critic sub-agent** "roast, not praise" cho video sẽ đăng, mục
  "Music and sound effects" — ít SFX hơn (~8 thay vì ~20 trong 18s), SFX "hit on the frame", duck nhạc −12 đến −15 dB —
  và cảnh báo font web tải hỏng âm thầm); `helpers/render.py` khác 204 dòng (giữ fps nguồn/`--fps` thay vì ép 24,
  `chunk_words` 2–3 từ, báo lỗi khi thiếu file phụ đề); `transcribe.py` thêm chọn audio track. `grade.py`,
  `timeline_view.py`, `pack_transcripts.py` giống hệt. → Muốn tái dùng code video-use thì lấy bản upstream.
- Tham chiếu "treo": `shader-transitions.md`, `shader-setup.md`, skill `hyperframes-animation-map`,
  `/marker-highlight`, `/seedance-loop-prompt`, dự án `video-projects/may-shorts-19`, các file `feedback_*.md` —
  được nhắc trong skill nhưng không có trong repo.
- Mâu thuẫn nội bộ: `hyperframes-cli` nói `--format webm` có alpha, còn `video-studio`/recipe 2 khẳng định webm ra
  **đục**, phải dùng `--format mov`; SKILL.md ghi MarginV=35 nhưng code dùng 90.
- Chỉ tiếng Anh; nhiều font gợi ý (Bebas Neue, Instrument Serif, Azeret Mono...) **không có** bộ ký tự tiếng Việt
  (xem `typography/claude-video-editor-typography-cho-video-va-font-tieng-viet`).
- Bài học RCA 2026-06-11: bước animation phụ thuộc một Apify actor (2 người dùng) chết giữa chừng → chuyển sang
  đường xác định, offline (animate-stills). Nguyên tắc: không để bước cốt lõi phụ thuộc dịch vụ bên thứ ba không SLA.

## 9. License — có được tái sử dụng code/prompt không?

| Phần | License | Tái sử dụng trong vedit |
|---|---|---|
| Mã gốc (`video-studio`, `generate-footage` + scripts, `install.sh`, templates, recipes/docs) | MIT + **Commons Clause** | Được dùng, sửa, chia sẻ; **không được "Sell"** = bán/cho thuê dịch vụ có giá trị chủ yếu từ chính phần mềm. Dùng để làm video (kể cả cho khách trả tiền) là hợp lệ theo điều khoản làm rõ của tác giả. Chép code phải giữ thông báo license + Commons Clause. |
| `skills/video-use/` (SKILL.md + helpers) | MIT (© 2026 Browser Use) | Tự do, chỉ cần giữ copyright notice. |
| `skills/hyperframes*`, `gsap`, `website-to-hyperframes` | Apache-2.0 (© 2026 HeyGen) | Tự do, kèm bản license, ghi chú thay đổi. Lưu ý repo **không** kèm file license HyperFrames trong `LICENSES/`. |
| `make-a-video`, `short-form-video`, MOTION_PHILOSOPHY | MIT (© 2026 Nate Herk) | Tự do; **riêng** tài sản thương hiệu AIS (logo, brand tokens, dự án mẫu) không được cấp phép. |

Thực hành cho vedit (nhận định, không phải tư vấn pháp lý): **ý tưởng/kỹ thuật** thì áp dụng thoải mái (các ghi chú
trong kho đã diễn giải lại); muốn chép **mã** thì ưu tiên phần MIT/Apache (video-use helpers, HyperFrames) kèm
notice; phần MIT+Commons Clause (ví dụ `motion_check.py`, `build_scenes.py`) nên **tự viết lại** — chúng ngắn —
để vedit không vướng điều kiện "không bán" nếu sau này thương mại hoá.

## 10. So sánh với vedit

| Khía cạnh | claude-video-editor | vedit hiện tại |
|---|---|---|
| Đối tượng | Mọi loại footage tiếng Anh (talking head, tutorial, promo...); ví dụ chủ yếu 16:9, có skill riêng cho 9:16 | Video ngắn dọc tiếng Việt (TikTok/Reels), cả video không lời (ASMR, nấu ăn) |
| Vai trò Claude | Một agent + skills, spawn sub-agent động | 3 subagent cố định (nghiên cứu, kịch bản, dựng) + bản API |
| Hiểu video | Transcript cấp từ (Scribe) + timeline_view khi cần | `analysis.json`: cảnh, khoảng lặng, khung giữa cảnh, faster-whisper; `vedit frame --grid` |
| Hợp đồng dựng | EDL tối giản + overlay là video render sẵn | EditPlan giàu: clips, texts, captions, graphics, motion, look, audio, transitions |
| Render | Nhiều lượt ffmpeg (cắt → concat → composite → loudnorm) | Một filter graph duy nhất, khung hình nguyên |
| Đồ hoạ | HTML/GSAP tự do (vô hạn khả năng, nặng) | libass vector có sẵn (callout, badge, progress, highlight, sparkles, flash) — nhẹ, giới hạn kiểu |
| Phụ đề | SRT 2 từ VIẾT HOA hoặc overlay HTML; quy tắc chunk/nhấn từ | 4 style (clean/boxed/bold_pop/karaoke), Agent 2 tự tính mốc |
| Chuyển cảnh | Catalog CSS/shader + luật "ý nghĩa" | 22 kiểu xfade |
| Màu | Grade theo đoạn, auto ±8%, tonemap HDR | 6 preset `look` cho cả timeline, chưa nhận diện HDR |
| Âm thanh | afade 30ms mọi biên, loudnorm 2 lượt | Không fade biên cắt, loudnorm 1 lượt, ducking sidechain, SFX tổng hợp |
| QA | Self-eval ở mọi điểm cắt, WCAG, animation-map, motion_check, cap 3 vòng | Khung giữa clip + lúc chữ xuất hiện |
| Tương tác | Bắt buộc duyệt chiến lược + style; 2 cổng preview; `project.md` | `/lam-video` chạy thẳng tới bản final, không bước duyệt, không bộ nhớ dự án |

## 11. Bản đồ ghi chú chi tiết (dùng với `vedit kb show <ref>`)

| Chủ đề | Ref |
|---|---|
| Cách viết skill/prompt cho agent | `tools/claude-video-editor-cach-viet-skill-va-prompt-cho-agent` |
| Quy trình hỏi – chốt – dựng – ghi nhớ | `techniques/claude-video-editor-quy-trinh-hoi-chot-dung-va-ghi-nho` |
| Đọc video bằng transcript, quy tắc cắt | `techniques/claude-video-editor-doc-video-bang-transcript-va-quy-tac-cat` |
| Vòng tự kiểm tra chất lượng | `techniques/claude-video-editor-vong-tu-kiem-tra-chat-luong-sau-render` |
| Luật chuyển động, ngôn ngữ hình ảnh | `techniques/claude-video-editor-luat-chuyen-dong-va-ngon-ngu-hinh-anh` |
| Playbook video dọc short-form | `techniques/claude-video-editor-playbook-video-doc-short-form` |
| Chuyển cảnh theo ý nghĩa | `techniques/claude-video-editor-chon-chuyen-canh-theo-y-nghia` |
| Phụ đề động, nhấn từ | `techniques/claude-video-editor-phu-de-dong-theo-nang-luong-va-nhan-tu` |
| Ảnh tĩnh → cảnh chuyển động | `techniques/claude-video-editor-bien-anh-tinh-thanh-canh-chuyen-dong` |
| Brief, storyboard, kịch bản | `scripting/claude-video-editor-brief-storyboard-tung-beat-va-kich-ban` |
| Typography & font tiếng Việt | `typography/claude-video-editor-typography-cho-video-va-font-tieng-viet` |
| Grade màu, tonemap HDR | `ffmpeg/claude-video-editor-grade-mau-tu-dong-va-tonemap-hdr` |
| Công thức ffmpeg/ASS đã kiểm chứng | `ffmpeg/claude-video-editor-cong-thuc-ffmpeg-va-ass-rut-ra-tu-repo` |
| Âm thanh: fade 30ms, loudnorm 2 lượt | `audio/claude-video-editor-am-thanh-fade-30ms-va-loudnorm-2-luot` |

## Áp dụng vào vedit

**Đã có (vedit làm tốt hơn hoặc ngang)**: một filter graph (không mã hoá lại nhiều lần), timeline theo khung nguyên,
tự thêm track im lặng cho nguồn không tiếng, speed native trong EditPlan, ducking sidechain, đồ hoạ vector nhẹ không
cần Chrome, ASS áp sau overlay ảnh (đúng Hard Rule 1), lưới toạ độ đo vị trí.

**Còn thiếu — đề xuất theo ưu tiên** (chi tiết ở các ghi chú cùng tiền tố `claude-video-editor:`):

1. **Cổng duyệt chiến lược + style profile trước khi dựng** (nguyên nhân khả dĩ nhất của "chưa đúng ý") — sửa
   skill `/lam-video` + Agent 2 trả "chiến lược 4–8 câu + bảng style" và chờ OK. Dễ.
2. **Viết lại prompt Agent 2/3** theo mẫu Hard Rules / Guardrails (gọi tên thói quen mặc định) / Gates + checklist
   "jaw-dropper mỗi ~5s, callback, payoff giữ ≥ 1s, stamp sau mục tiêu". Dễ.
3. **Critic sub-agent sau preview** ("roast, not praise": vấn đề xếp hạng kèm timecode + 5 việc sửa đầu tiên). Dễ.
4. **Fade âm 30ms ở mọi biên clip** trong `render.py` (chống tiếng "bụp" khi cắt) + loudnorm 2 lượt cho final. Dễ.
5. **Bộ nhớ dự án `projects/<slug>/project.md`** (quyết định, phản hồi người dùng, lý do) — agent đọc khi bắt đầu. Dễ.
6. **Easing cho chữ/đồ hoạ**: thêm `accel` vào `\t`, tách `\move` thành event theo khung (đã kiểm chứng). Dễ–vừa.
7. **Ken Burns mượt bằng `perspective`** thay zoompan cho zoom chậm (zoompan bị bậc thang — đã đo). Dễ–vừa.
8. **Tonemap HDR tự động** cho nguồn iPhone HLG/PQ; sau đó `look.auto` hiệu chỉnh nhẹ theo clip. Dễ / vừa.
9. **`vedit captions`**: tự sinh phụ đề từ transcript theo đoạn cắt (chunk 2–4 từ, nhấn từ khoá, cường độ karaoke). Vừa.
10. **`vedit qa`**: soi mọi điểm cắt (filmstrip + waveform), vùng chết > 2.5s, va chạm/vùng an toàn, tương phản,
    contact sheet. Vừa.
11. **Transition "whip" có motion blur** (xfade slide + `dblur`) và đồ hoạ `streak`, `marker` (đã kiểm chứng). Vừa.
12. **Font**: mặc định Be Vietnam Pro thay Inter; thêm font condensed/serif/mono có tiếng Việt; validate thiếu glyph. Dễ.
13. Dài hạn: layout chia đôi/PiP cho talking head; overlay video có alpha để nhận HyperFrames/Remotion. Khó.
