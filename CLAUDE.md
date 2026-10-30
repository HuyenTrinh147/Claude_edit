# vedit — ghi chú cho Claude Code

Hệ thống 3 agent dựng video ngắn (Python + Claude API + ffmpeg). Người dùng nói tiếng Việt; giao diện, prompt,
kho kiến thức viết tiếng Việt, mã nguồn & comment tiếng Anh.

- `vedit/edl.py` — schema `EditPlan` (pydantic), hợp đồng giữa Agent 2 và Agent 3. Clip start/end = giây nguồn;
  texts/captions/audio = giây timeline.
- `vedit/render.py` — EditPlan → một filter graph ffmpeg (concat/xfade, fit cover/contain/blur, zoompan, ASS qua
  libass cho chữ & phụ đề, amix + sidechaincompress + loudnorm).
- `vedit/media.py` — ffprobe, dò cảnh/khoảng lặng, trích khung hình, faster-whisper (tuỳ chọn).
- `vedit/agents/` — `base.py` (tool runner streaming, web_search/web_fetch server tools, caching, fallbacks),
  `tools.py` (công cụ dùng chung), `researcher.py` (Agent 1), `scriptwriter.py` (Agent 2), `editor.py` (Agent 3).
- `vedit/knowledge.py` — kho `knowledge/<category>/<slug>.md`; `vedit/gdrive.py` — Drive (scope drive.file).
- Subagent Claude Code tương ứng trong `.claude/agents/`.

Lệnh: `pip install -e ".[dev]"`, `pytest` (cần ffmpeg; không gọi API thật), `vedit -h`.
Không commit `projects/` (video nặng) hay `.env`.
