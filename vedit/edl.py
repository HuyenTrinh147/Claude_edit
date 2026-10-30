"""EditPlan: the edit decision list shared by Agent 2 (writes it) and Agent 3 (renders it).

Timeline model
--------------
* ``clips`` play back-to-back on one main track. A clip's ``transition`` blends it
  with the previous clip, overlapping the two by ``transition.duration`` seconds.
* ``texts``, ``captions``, ``images`` and ``audio`` use *timeline* seconds
  (the time in the exported video), not source seconds.
* ``Clip.start``/``Clip.end`` are *source* seconds inside the clip's media file.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

CANVAS_PRESETS: dict[str, tuple[int, int]] = {
    "tiktok": (1080, 1920),
    "reels": (1080, 1920),
    "shorts": (1080, 1920),
    "portrait45": (1080, 1350),
    "square": (1080, 1080),
    "youtube": (1920, 1080),
}

XFADE_TRANSITIONS = (
    "fade", "fadeblack", "fadewhite", "dissolve", "wipeleft", "wiperight", "wipeup", "wipedown",
    "slideleft", "slideright", "slideup", "slidedown", "smoothleft", "smoothright", "smoothup",
    "smoothdown", "circleopen", "circleclose", "radial", "zoomin", "pixelize", "hblur",
)
TransitionType = Literal[
    "fade", "fadeblack", "fadewhite", "dissolve", "wipeleft", "wiperight", "wipeup", "wipedown",
    "slideleft", "slideright", "slideup", "slidedown", "smoothleft", "smoothright", "smoothup",
    "smoothdown", "circleopen", "circleclose", "radial", "zoomin", "pixelize", "hblur",
]

HEX_COLOR = r"^#[0-9A-Fa-f]{6}$"
TextPosition = Literal["top", "upper", "center", "lower", "bottom"]
TextAnimation = Literal[
    "none", "fade", "pop", "bounce", "slide_up", "slide_left", "typewriter", "word_pop", "blur_in", "wipe",
]
LOOK_PRESETS = ("none", "warm_food", "bright_clean", "film", "moody", "vivid", "bw")
BUILTIN_SFX = ("pop", "click", "ding", "sparkle", "whoosh", "thud", "rise")


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Canvas(_Model):
    width: int = Field(1080, ge=144, le=4096, description="Chiều rộng khung hình (px), số chẵn")
    height: int = Field(1920, ge=144, le=4096, description="Chiều cao khung hình (px), số chẵn")
    fps: int = Field(30, ge=12, le=60)
    background: str = Field("#000000", pattern=HEX_COLOR, description="Màu nền khi fit=contain")

    @model_validator(mode="after")
    def _even(self) -> "Canvas":
        if self.width % 2 or self.height % 2:
            raise ValueError("canvas width/height phải là số chẵn (yêu cầu của H.264 yuv420p)")
        return self


class Transition(_Model):
    type: TransitionType = "fade"
    duration: float = Field(0.4, gt=0.05, le=2.0)


class Clip(_Model):
    source: str = Field(
        description="Khóa trong EditPlan.sources, đường dẫn file (video/ảnh), hoặc 'color:#RRGGBB' cho thẻ màu"
    )
    start: float = Field(0.0, ge=0, description="Điểm vào trong file nguồn (giây)")
    end: float | None = Field(None, description="Điểm ra trong file nguồn (giây). Bắt buộc với video")
    duration: float | None = Field(None, gt=0, description="Độ dài cho ảnh tĩnh / thẻ màu (giây)")
    speed: float = Field(1.0, ge=0.25, le=4.0, description="Tốc độ phát: 2.0 = nhanh gấp đôi")
    fit: Literal["cover", "contain", "blur"] = Field(
        "cover", description="cover = cắt cho đầy khung; contain = viền màu; blur = nền mờ phía sau"
    )
    focus_x: float = Field(0.5, ge=0, le=1, description="Tâm cắt ngang khi fit=cover (0 = trái, 1 = phải)")
    focus_y: float = Field(0.5, ge=0, le=1, description="Tâm cắt dọc khi fit=cover (0 = trên, 1 = dưới)")
    zoom: Literal["none", "in", "out"] = Field("none", description="Hiệu ứng zoom chậm (Ken Burns)")
    zoom_amount: float = Field(0.12, ge=0.02, le=0.6)
    volume: float = Field(1.0, ge=0, le=4)
    mute: bool = False
    transition: Transition | None = Field(None, description="Chuyển cảnh TỪ clip trước VÀO clip này")
    note: str = Field("", description="Vai trò của clip trong kịch bản (hook, b-roll, CTA...)")

    @model_validator(mode="after")
    def _check_range(self) -> "Clip":
        if self.end is not None and self.end <= self.start:
            raise ValueError(f"clip {self.source!r}: end ({self.end}) phải lớn hơn start ({self.start})")
        if self.end is None and self.duration is None:
            raise ValueError(f"clip {self.source!r}: cần 'end' (video) hoặc 'duration' (ảnh / thẻ màu)")
        return self

    @property
    def is_color(self) -> bool:
        return self.source.startswith("color:")

    @property
    def source_duration(self) -> float:
        if self.end is not None:
            return self.end - self.start
        return float(self.duration)  # type: ignore[arg-type]

    @property
    def timeline_duration(self) -> float:
        return self.source_duration / self.speed


class TextOverlay(_Model):
    text: str = Field(min_length=1, description="Chữ hiển thị. Dùng '\\n' để xuống dòng")
    start: float = Field(ge=0, description="Thời điểm xuất hiện trên timeline (giây)")
    end: float = Field(gt=0, description="Thời điểm biến mất trên timeline (giây)")
    position: TextPosition = "center"
    size: int = Field(80, ge=16, le=300, description="Cỡ chữ theo pixel của canvas")
    color: str = Field("#FFFFFF", pattern=HEX_COLOR)
    outline_color: str = Field("#000000", pattern=HEX_COLOR)
    outline: float = Field(5, ge=0, le=20)
    box: bool = Field(False, description="Nền hộp phía sau chữ")
    box_color: str = Field("#000000", pattern=HEX_COLOR)
    box_opacity: float = Field(0.6, ge=0, le=1)
    bold: bool = True
    font: str | None = Field(None, description="Family font, vd 'Be Vietnam Pro', 'Mali', 'Pacifico', 'Inter'")
    animation: TextAnimation = Field(
        "pop", description="Hiệu ứng xuất hiện: pop, bounce (nảy), typewriter (gõ chữ), word_pop (bật từng từ), "
                           "slide_up, slide_left, blur_in, wipe (quét lộ dần), fade, none")
    shape: Literal["none", "pill", "banner"] = Field(
        "none", description="Nền sticker phía sau chữ: pill = viên bo tròn, banner = băng chữ nhật hơi nghiêng")
    shape_color: str = Field("#FFFFFF", pattern=HEX_COLOR)
    shape_opacity: float = Field(1.0, ge=0, le=1)
    x: float | None = Field(None, ge=0, le=1, description="Tâm ngang tuỳ chỉnh (0..1); bỏ trống = giữa")
    y: float | None = Field(None, ge=0, le=1, description="Tâm dọc tuỳ chỉnh (0..1); ghi đè position")
    rotation: float = Field(0, ge=-30, le=30, description="Nghiêng chữ kiểu sticker (độ, dương = ngược kim đồng hồ)")

    @model_validator(mode="after")
    def _times(self) -> "TextOverlay":
        if self.end <= self.start:
            raise ValueError(f"text {self.text[:30]!r}: end phải lớn hơn start")
        return self


class CaptionWord(_Model):
    text: str
    start: float = Field(ge=0)
    end: float = Field(gt=0)


class CaptionSegment(_Model):
    start: float = Field(ge=0, description="Timeline (giây)")
    end: float = Field(gt=0, description="Timeline (giây)")
    text: str = Field(min_length=1)
    words: list[CaptionWord] = Field(default_factory=list, description="Mốc từng từ (cho style karaoke)")


class Captions(_Model):
    segments: list[CaptionSegment] = Field(default_factory=list)
    style: Literal["clean", "boxed", "bold_pop", "karaoke"] = "bold_pop"
    position: TextPosition = "lower"
    size: int = Field(70, ge=16, le=200)
    color: str = Field("#FFFFFF", pattern=HEX_COLOR)
    highlight_color: str = Field("#FFE600", pattern=HEX_COLOR, description="Màu từ đang đọc (karaoke)")
    uppercase: bool = False
    font: str | None = None


class ImageOverlay(_Model):
    path: str = Field(description="Ảnh PNG/JPG (logo, sticker, watermark)")
    start: float = Field(0, ge=0)
    end: float | None = Field(None, description="None = đến hết video")
    x: float = Field(0.5, ge=0, le=1, description="Tâm ngang theo tỉ lệ khung (0..1)")
    y: float = Field(0.1, ge=0, le=1, description="Tâm dọc theo tỉ lệ khung (0..1)")
    width: float = Field(0.25, gt=0, le=1, description="Chiều rộng theo tỉ lệ khung")
    opacity: float = Field(1.0, ge=0, le=1)


class Graphic(_Model):
    """Motion graphic drawn over the video (vector, animated). Positions are fractions of the canvas."""

    type: Literal["callout", "badge", "progress_bar", "highlight", "sparkles", "flash"] = Field(
        description="callout = nhãn + đường chỉ vào vật; badge = huy hiệu tròn số bước (+ nhãn); "
                    "progress_bar = thanh tiến trình chạy dần; highlight = vòng tròn nhấn mạnh; "
                    "sparkles = lấp lánh quanh một điểm; flash = chớp sáng toàn màn hình")
    start: float = Field(ge=0, description="Timeline (giây)")
    end: float = Field(gt=0, description="Timeline (giây)")
    x: float = Field(0.5, ge=0, le=1, description="callout/highlight/sparkles: điểm cần chỉ; badge: tâm huy hiệu")
    y: float = Field(0.5, ge=0, le=1, description="Tương tự x; progress_bar: vị trí dọc của thanh")
    label_x: float | None = Field(None, ge=0, le=1, description="callout: tâm nhãn (mặc định phía trên điểm)")
    label_y: float | None = Field(None, ge=0, le=1)
    text: str = Field("", description="callout: nhãn; badge: số/chữ trong huy hiệu")
    label: str = Field("", description="badge: chữ phụ bên phải huy hiệu, vd 'Pha nước muối'")
    color: str = Field("#FFFFFF", pattern=HEX_COLOR, description="Màu chính: nền nhãn / huy hiệu / thanh / vòng / sao")
    text_color: str = Field("#1E1E1E", pattern=HEX_COLOR)
    accent_color: str = Field("#FF5A36", pattern=HEX_COLOR, description="Màu nhấn: đường chỉ, chấm, viền")
    size: int = Field(54, ge=16, le=200, description="Cỡ chữ (callout/badge) hoặc cỡ sao (sparkles)")
    radius: float = Field(0.12, gt=0, le=0.6, description="highlight: bán kính vòng; sparkles: bán kính rải sao")
    count: int = Field(7, ge=1, le=24, description="sparkles: số ngôi sao")
    thickness: int = Field(10, ge=2, le=60, description="progress_bar: độ dày (px)")
    font: str | None = None

    @model_validator(mode="after")
    def _check(self) -> "Graphic":
        if self.end <= self.start:
            raise ValueError(f"graphic {self.type}: end phải lớn hơn start")
        if self.type in ("callout", "badge") and not self.text.strip():
            raise ValueError(f"graphic {self.type}: cần 'text'")
        return self


class Motion(_Model):
    """Camera move on the whole frame at a timeline moment — sync it to a sound or a beat."""

    type: Literal["punch", "shake"] = Field(description="punch = zoom giật vào rồi trả về; shake = rung khung hình")
    start: float = Field(ge=0, description="Timeline (giây)")
    duration: float = Field(0.3, gt=0.05, le=3)
    amount: float = Field(0.08, gt=0, le=0.4, description="punch: mức zoom (0.05-0.15); shake: biên độ (0.005-0.03)")


class Look(_Model):
    preset: Literal["none", "warm_food", "bright_clean", "film", "moody", "vivid", "bw"] = Field(
        "none", description="Tông màu: warm_food (ấm, tươi cho đồ ăn), bright_clean, film, moody, vivid, bw")
    vignette: float = Field(0, ge=0, le=1, description="Tối góc khung (0..1)")
    grain: float = Field(0, ge=0, le=1, description="Hạt film (0..1)")


class AudioTrack(_Model):
    path: str = Field(description="File audio, hoặc âm thanh tổng hợp sẵn: " + ", ".join(f"'sfx:{n}'" for n in BUILTIN_SFX))
    role: Literal["music", "voiceover", "sfx"] = "music"
    start: float = Field(0, ge=0, description="Bắt đầu trên timeline (giây)")
    source_start: float = Field(0, ge=0, description="Điểm vào trong file audio (giây)")
    duration: float | None = Field(None, gt=0, description="None = đến hết video")
    volume: float = Field(0.25, ge=0, le=4)
    fade_in: float = Field(0.5, ge=0, le=10)
    fade_out: float = Field(1.0, ge=0, le=10)
    loop: bool = Field(True, description="Lặp lại nếu file ngắn hơn video")
    duck: bool = Field(True, description="Tự giảm âm lượng nhạc khi có giọng nói (chỉ áp dụng role=music)")

    @property
    def builtin(self) -> str | None:
        return self.path[4:] if self.path.startswith("sfx:") else None

    @model_validator(mode="after")
    def _check_builtin(self) -> "AudioTrack":
        if self.builtin is not None and self.builtin not in BUILTIN_SFX:
            raise ValueError(f"âm thanh tổng hợp '{self.path}' không có; chọn: {', '.join(BUILTIN_SFX)}")
        return self


class ExportSettings(_Model):
    filename: str = Field("final.mp4", pattern=r"^[\w.\- ]+\.(mp4|mov|mkv)$")
    crf: int = Field(20, ge=14, le=35, description="Chất lượng H.264: thấp hơn = đẹp hơn, nặng hơn")
    encoder_preset: Literal["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow"] = "medium"
    audio_bitrate: str = Field("192k", pattern=r"^\d{2,3}k$")
    normalize_audio: bool = Field(True, description="Chuẩn hoá loudness về -14 LUFS (chuẩn TikTok/YouTube)")
    thumbnail_at: float | None = Field(None, ge=0, description="Xuất ảnh thumbnail tại giây này")


class EditPlan(_Model):
    version: int = 1
    title: str = ""
    sources: dict[str, str] = Field(
        default_factory=dict, description="Tên ngắn -> đường dẫn file, ví dụ {'main': 'input/video.mp4'}"
    )
    canvas: Canvas = Field(default_factory=Canvas)
    clips: list[Clip] = Field(min_length=1)
    texts: list[TextOverlay] = Field(default_factory=list)
    captions: Captions | None = None
    graphics: list[Graphic] = Field(default_factory=list)
    motion: list[Motion] = Field(default_factory=list)
    look: Look = Field(default_factory=Look)
    images: list[ImageOverlay] = Field(default_factory=list)
    audio: list[AudioTrack] = Field(default_factory=list)
    export: ExportSettings = Field(default_factory=ExportSettings)
    notes: str = ""

    @model_validator(mode="after")
    def _check_transitions(self) -> "EditPlan":
        if self.clips[0].transition is not None:
            raise ValueError("clip đầu tiên không thể có transition (transition là chuyển cảnh từ clip trước)")
        for i in range(1, len(self.clips)):
            tr = self.clips[i].transition
            if tr is None:
                continue
            shortest = min(self.clips[i - 1].timeline_duration, self.clips[i].timeline_duration)
            if tr.duration >= shortest:
                raise ValueError(
                    f"clip #{i}: transition {tr.duration}s phải ngắn hơn clip ngắn nhất kề nó ({shortest:.2f}s)"
                )
        return self

    # ---- timeline helpers -------------------------------------------------

    def clip_offsets(self) -> list[float]:
        """Timeline start time of every clip."""
        offsets = [0.0]
        for prev, clip in zip(self.clips, self.clips[1:]):
            overlap = clip.transition.duration if clip.transition else 0.0
            offsets.append(offsets[-1] + prev.timeline_duration - overlap)
        return offsets

    @property
    def duration(self) -> float:
        return self.clip_offsets()[-1] + self.clips[-1].timeline_duration

    def resolve(self, ref: str, base_dir: Path) -> Path:
        """Resolve a source key or relative path against the plan's base directory."""
        raw = self.sources.get(ref, ref)
        path = Path(raw).expanduser()
        return path if path.is_absolute() else (base_dir / path)

    # ---- persistence ------------------------------------------------------

    @classmethod
    def load(cls, path: Path) -> "EditPlan":
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))

    def save(self, path: Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(self.model_dump_json(indent=2, exclude_none=True), encoding="utf-8")

    def summary(self) -> str:
        lines = [f"{self.title or '(chưa đặt tên)'} — {self.canvas.width}x{self.canvas.height}@{self.canvas.fps}, "
                 f"{self.duration:.2f}s, {len(self.clips)} clip"]
        for i, (clip, off) in enumerate(zip(self.clips, self.clip_offsets())):
            span = f"{clip.start:.2f}-{clip.end:.2f}s" if clip.end is not None else f"{clip.source_duration:.2f}s"
            extra = f" x{clip.speed}" if clip.speed != 1 else ""
            tr = f" [{clip.transition.type} {clip.transition.duration}s]" if clip.transition else ""
            lines.append(f"  #{i} @{off:6.2f}s  {clip.source} {span}{extra}{tr}  {clip.note}".rstrip())
        extras = [f"{len(self.texts)} chữ", f"{len(self.graphics)} đồ hoạ", f"{len(self.motion)} motion",
                  f"captions {len(self.captions.segments) if self.captions else 0} đoạn", f"{len(self.audio)} audio",
                  f"look {self.look.preset}"]
        lines.append("  " + ", ".join(extras))
        return "\n".join(lines)


def validate_against_media(plan: EditPlan, base_dir: Path, probe) -> list[str]:
    """Check the plan against real files. ``probe(path)`` must return an object with
    ``duration``/``has_video``. Returns human-readable problems (empty list = OK)."""
    problems: list[str] = []
    for i, clip in enumerate(plan.clips):
        if clip.is_color:
            if not re.fullmatch(r"color:#[0-9A-Fa-f]{6}", clip.source):
                problems.append(f"clip #{i}: màu không hợp lệ {clip.source!r}, dạng đúng 'color:#RRGGBB'")
            continue
        path = plan.resolve(clip.source, base_dir)
        if not path.exists():
            problems.append(f"clip #{i}: không tìm thấy file {path}")
            continue
        info = probe(path)
        if info.is_image:
            if clip.duration is None:
                problems.append(f"clip #{i}: ảnh tĩnh cần 'duration'")
            continue
        if clip.end is None:
            problems.append(f"clip #{i}: video cần 'end'")
        elif clip.end > info.duration + 0.05:
            problems.append(f"clip #{i}: end={clip.end:.2f}s vượt quá độ dài nguồn {info.duration:.2f}s")
    total = plan.duration
    for i, text in enumerate(plan.texts):
        if text.start >= total:
            problems.append(f"text #{i} bắt đầu ({text.start:.2f}s) sau khi video kết thúc ({total:.2f}s)")
    if plan.captions:
        for i, seg in enumerate(plan.captions.segments):
            if seg.end <= seg.start:
                problems.append(f"caption #{i}: end phải lớn hơn start")
            elif seg.start >= total:
                problems.append(f"caption #{i} bắt đầu ({seg.start:.2f}s) sau khi video kết thúc ({total:.2f}s)")
    for i, g in enumerate(plan.graphics):
        if g.start >= total:
            problems.append(f"graphic #{i} ({g.type}) bắt đầu ({g.start:.2f}s) sau khi video kết thúc ({total:.2f}s)")
    for i, m in enumerate(plan.motion):
        if m.start >= total:
            problems.append(f"motion #{i} bắt đầu ({m.start:.2f}s) sau khi video kết thúc ({total:.2f}s)")
    for i, img in enumerate(plan.images):
        if not plan.resolve(img.path, base_dir).exists():
            problems.append(f"image #{i}: không tìm thấy file {img.path}")
    for i, track in enumerate(plan.audio):
        if track.builtin is not None:
            continue
        path = plan.resolve(track.path, base_dir)
        if not path.exists():
            problems.append(f"audio #{i}: không tìm thấy file {path}")
        elif not probe(path).has_audio:
            problems.append(f"audio #{i}: file {path.name} không có luồng âm thanh")
    return problems


def plan_json_schema() -> str:
    return json.dumps(EditPlan.model_json_schema(), ensure_ascii=False)
