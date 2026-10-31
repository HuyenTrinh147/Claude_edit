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
import unicodedata
from pathlib import Path
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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
BUILTIN_SFX = ("pop", "click", "ding", "sparkle", "whoosh", "thud", "rise",
               # chiptune game sounds (square / triangle waves)
               "pickup", "lock", "combo", "levelup", "slash", "zip", "coin", "tick", "complete", "buzz")


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


def nfc(value):
    """Vietnamese typed on some keyboards arrives decomposed (NFD): base letter + combining marks, which
    every font renders with misplaced diacritics. Store all on-screen text precomposed (NFC)."""
    return unicodedata.normalize("NFC", value) if isinstance(value, str) else value


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
    freeze: float = Field(0, ge=0, le=10, description="Dừng hình ở khung cuối thêm N giây (freeze frame cho "
                                                      "khoảnh khắc thưởng / thẻ hoàn thành); tiếng gốc im lặng")
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
        return self.source_duration / self.speed + self.freeze


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

    _nfc = field_validator("text", mode="before")(nfc)

    @model_validator(mode="after")
    def _times(self) -> "TextOverlay":
        if self.end <= self.start:
            raise ValueError(f"text {self.text[:30]!r}: end phải lớn hơn start")
        return self


class CaptionWord(_Model):
    text: str
    start: float = Field(ge=0)
    end: float = Field(gt=0)

    _nfc = field_validator("text", mode="before")(nfc)


class CaptionSegment(_Model):
    start: float = Field(ge=0, description="Timeline (giây)")
    end: float = Field(gt=0, description="Timeline (giây)")
    text: str = Field(min_length=1)
    words: list[CaptionWord] = Field(default_factory=list, description="Mốc từng từ (cho style karaoke)")

    _nfc = field_validator("text", mode="before")(nfc)


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

    _nfc = field_validator("text", "label", mode="before")(nfc)

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
    pitch: float = Field(0, ge=-24, le=24, description="Đổi cao độ theo nửa cung (vd chuỗi combo 0, 2, 4, 7 cao dần); "
                                                       "đổi cả độ dài như tua băng")

    @property
    def builtin(self) -> str | None:
        return self.path[4:] if self.path.startswith("sfx:") else None

    @model_validator(mode="after")
    def _check_builtin(self) -> "AudioTrack":
        if self.builtin is not None and self.builtin not in BUILTIN_SFX:
            raise ValueError(f"âm thanh tổng hợp '{self.path}' không có; chọn: {', '.join(BUILTIN_SFX)}")
        return self


# ---- game HUD ----------------------------------------------------------------------------------------

HudPoint = Literal["center", "top", "bottom", "left", "right", "top_left", "top_right", "bottom_left", "bottom_right"]
HudEase = Literal["pop", "slide", "stamp", "fade", "none"]
HudIcon = Literal["star", "check", "lock", "coin", "heart", "hand", "clock", "drop", "bolt", "flame"]
HUD_ICONS = ("star", "check", "lock", "coin", "heart", "hand", "clock", "drop", "bolt", "flame")


def nfc_list(value):
    return [nfc(v) for v in value] if isinstance(value, list) else nfc(value)


class Anchor(_Model):
    """Stick a HUD item to a tracked object (world-space UI). Tracks are made with `vedit track`."""

    track: str = Field(description="Tên track: projects/<slug>/analysis/tracks/<tên>.json (tạo bằng `vedit track`)")
    point: HudPoint = Field("center", description="Điểm trên hộp bám: center, top (mép trên), bottom, left, right, "
                                                  "top_left, top_right, bottom_left, bottom_right")
    dx: float = Field(0, ge=-1, le=1, description="Lệch ngang thêm, theo tỉ lệ chiều rộng khung")
    dy: float = Field(0, ge=-1, le=1, description="Lệch dọc thêm, theo tỉ lệ chiều cao khung (âm = lên trên)")
    lag: float = Field(0, ge=0, le=0.9, description="0 = dính chặt vật; 0.3-0.6 = trôi theo mềm như UI lơ lửng")


class ValueKey(_Model):
    t: float = Field(ge=0, description="Timeline (giây)")
    v: float = Field(description="Giá trị tại mốc này (meter: 0..1; counter: số, hoặc số giây với format timer)")
    ease: Literal["linear", "in", "out", "inout", "hold"] = Field(
        "inout", description="Cách đi TỪ mốc trước tới mốc này: inout mượt, out = nhanh rồi chậm, hold = nhảy cóc")


class _Hud(_Model):
    start: float = Field(ge=0, description="Timeline (giây)")
    end: float = Field(gt=0, description="Timeline (giây)")
    x: float = Field(0.5, ge=0, le=1, description="Tâm ngang (tỉ lệ khung) khi không bám vật")
    y: float = Field(0.5, ge=0, le=1, description="Tâm dọc (tỉ lệ khung) khi không bám vật")
    anchor: Anchor | None = Field(None, description="Bám theo vật đã track (thay cho x/y)")
    enter: HudEase = Field("pop", description="Vào: pop (bật nảy), slide (trượt lên), stamp (đập xuống), fade, none")
    exit: HudEase = Field("fade", description="Ra: fade, pop (thu nhỏ), slide (trượt lên), stamp, none")
    color: str = Field("#3CF2FF", pattern=HEX_COLOR, description="Màu neon chính (viền, chữ HUD)")
    accent_color: str = Field("#FFD23F", pattern=HEX_COLOR, description="Màu thưởng / khoá / tick / vùng chuẩn")
    text_color: str = Field("#FFFFFF", pattern=HEX_COLOR)
    size: int = Field(44, ge=14, le=240, description="Cỡ chữ chính (px canvas)")
    font: str | None = Field(None, description="Font chữ HUD, vd 'Chakra Petch'; mặc định theo cấu hình")

    @model_validator(mode="after")
    def _times(self):
        if self.end <= self.start:
            raise ValueError(f"hud {getattr(self, 'type', '')}: end phải lớn hơn start")
        return self


class Sprite(_Model):
    """A pixel-art item cut from the video itself (8-bit inventory look): crop a box at a source moment,
    downscale to a few pixels and a few colours."""

    t: float = Field(ge=0, description="Giây NGUỒN của khung hình lấy vật")
    box: tuple[float, float, float, float] = Field(
        description="[x, y, w, h] tỉ lệ khung nguồn bao sát vật (góc trên-trái + rộng, cao) — đo bằng `vedit frame --grid`")
    source: str = Field("main", description="Khoá nguồn trong sources (mặc định video chính)")
    pixels: int = Field(16, ge=6, le=40, description="Số pixel theo cạnh dài (ít = đậm chất 8-bit)")
    colors: int = Field(10, ge=2, le=24, description="Số màu sau khi lượng tử hoá")

    @model_validator(mode="after")
    def _check_box(self) -> "Sprite":
        x, y, w, h = self.box
        if not (0 <= x < 1 and 0 <= y < 1 and 0 < w <= 1 and 0 < h <= 1 and x + w <= 1.001 and y + h <= 1.001):
            raise ValueError(f"sprite box {list(self.box)} phải là [x, y, w, h] trong khung 0..1")
        return self


class Reticle(_Hud):
    type: Literal["reticle"]
    text: str = Field("", description="Nhãn cạnh khung ngắm, vd 'CHILI'")
    sub: str = Field("", description="Dòng nhỏ dưới nhãn; mặc định 'SCANNING…' rồi 'LOCKED' khi khoá")
    lock_at: float | None = Field(None, description="Timeline (giây) khoá mục tiêu: khung co sát vật, đổi "
                                                    "accent_color, chớp sáng. Mặc định start + 0.4")
    w: float = Field(0.3, gt=0, le=1, description="Rộng khung (tỉ lệ khung) khi không bám vật")
    h: float = Field(0.3, gt=0, le=1, description="Cao khung khi không bám vật")
    pad: float = Field(0.06, ge=0, le=0.5, description="Nới khung ra ngoài hộp track (tỉ lệ cạnh)")

    _nfc = field_validator("text", "sub", mode="before")(nfc)


class Panel(_Hud):
    type: Literal["panel"]
    text: str = Field("QUEST", description="Tiêu đề bảng, vd 'QUEST: CÀ PHÁO MUỐI'")
    items: list[str] = Field(min_length=1, max_length=8, description="Các dòng nhiệm vụ / công thức")
    checks: list[float | None] = Field(default_factory=list,
                                       description="Timeline (giây) tick từng dòng, cùng thứ tự items; null = chưa tick")
    width: float = Field(0.62, gt=0.1, le=0.96, description="Rộng bảng (tỉ lệ khung)")

    _nfc = field_validator("text", "items", mode="before")(nfc_list)

    @model_validator(mode="after")
    def _check_checks(self) -> "Panel":
        if len(self.checks) > len(self.items):
            raise ValueError(f"panel: {len(self.checks)} mốc checks nhưng chỉ có {len(self.items)} dòng items")
        return self


class Meter(_Hud):
    type: Literal["meter"]
    text: str = Field("", description="Nhãn, vd 'WATER LEVEL'")
    keys: list[ValueKey] = Field(min_length=1, description="Giá trị 0..1 theo thời gian")
    zone: tuple[float, float] | None = Field(None, description="Vùng chuẩn [từ, đến] trong 0..1, sáng lên khi giá "
                                                               "trị nằm trong")
    style: Literal["fill", "needle"] = Field("fill", description="fill = thanh đầy dần; needle = kim chạy (canh thời điểm)")
    orientation: Literal["horizontal", "vertical"] = "horizontal"
    length: float = Field(0.5, gt=0.05, le=0.95, description="Dài thanh (tỉ lệ rộng khung nếu ngang, cao nếu dọc)")
    thickness: int = Field(26, ge=6, le=120, description="Độ dày (px)")
    show_value: bool = Field(True, description="Hiện % cạnh nhãn")

    _nfc = field_validator("text", mode="before")(nfc)

    @model_validator(mode="after")
    def _check_zone(self) -> "Meter":
        if self.zone is not None and not 0 <= self.zone[0] < self.zone[1] <= 1:
            raise ValueError(f"meter: zone {list(self.zone)} phải là [từ, đến] với 0 ≤ từ < đến ≤ 1")
        return self


class Counter(_Hud):
    type: Literal["counter"]
    text: str = Field("", description="Nhãn nhỏ phía trên số, vd 'SCORE', 'COMBO', 'FERMENTING'")
    keys: list[ValueKey] = Field(min_length=1, description="Giá trị theo thời gian (đếm mượt giữa các mốc)")
    format: Literal["int", "timer", "combo", "percent"] = Field(
        "int", description="int = 1,250; timer = HH:MM:SS (v là số giây: 259200 = 72:00:00); combo = ×3; percent = 87%")
    prefix: str = ""
    suffix: str = ""
    box: bool = Field(True, description="Nền HUD mờ phía sau")

    _nfc = field_validator("text", "prefix", "suffix", mode="before")(nfc)


class Popup(_Hud):
    type: Literal["popup"]
    text: str = Field(min_length=1, description="Chữ thưởng: 'PERFECT!', '+50', 'COMBO ×3'")
    sub: str = Field("", description="Dòng nhỏ bên dưới, vd '+100 PTS'")
    enter: HudEase = "stamp"
    exit: HudEase = "pop"
    rise: float = Field(0.05, ge=0, le=0.3, description="Bay lên bao nhiêu (tỉ lệ cao khung) trong lúc hiện")
    burst: bool = Field(True, description="Tia sáng toả ra phía sau lúc bật lên")
    tilt: float = Field(-4, ge=-25, le=25, description="Nghiêng (độ, dương = ngược kim đồng hồ)")
    shadow_color: str = Field("#FF3D7F", pattern=HEX_COLOR, description="Màu bóng đổ cứng phía sau chữ")

    _nfc = field_validator("text", "sub", mode="before")(nfc)


class Slots(_Hud):
    type: Literal["slots"]
    count: int = Field(4, ge=1, le=8, description="Số ô túi đồ")
    items: list[str] = Field(default_factory=list, description="Tên vật phẩm theo thứ tự vào túi (ngắn: 'TỎI')")
    icons: list[HudIcon | None] = Field(default_factory=list, description="Icon cho từng vật phẩm (tuỳ chọn)")
    sprites: list[Sprite | None] = Field(default_factory=list,
                                         description="Ảnh pixel-art cắt từ video cho từng vật phẩm (ưu tiên hơn icons)")
    times: list[float] = Field(default_factory=list, description="Timeline (giây) vật phẩm thứ i chạm vào ô")
    sources: list[Anchor | None] = Field(default_factory=list,
                                         description="Vật phẩm thứ i bay ra từ vật thật này (track); thiếu = from_x/y")
    from_x: float = Field(0.5, ge=0, le=1)
    from_y: float = Field(0.45, ge=0, le=1)
    fly: float = Field(0.45, ge=0.1, le=2, description="Thời gian bay (giây)")
    slot_size: int = Field(96, ge=40, le=240, description="Cạnh ô (px)")

    _nfc = field_validator("items", mode="before")(nfc_list)

    @model_validator(mode="after")
    def _check_items(self) -> "Slots":
        if len(self.times) > self.count:
            raise ValueError(f"slots: {len(self.times)} mốc times nhưng chỉ có {self.count} ô")
        return self


class Card(_Hud):
    type: Literal["card"]
    text: str = Field("DISH COMPLETE!", description="Tiêu đề thẻ")
    stars: int = Field(3, ge=0, le=3, description="Số sao đạt được (trên 3)")
    star_delay: float = Field(0.5, ge=0, le=5, description="Sao đầu tiên hiện sau khi thẻ vào bao lâu (giây)")
    star_gap: float = Field(0.28, ge=0.05, le=2)
    items: list[str] = Field(default_factory=list, max_length=5, description="Dòng phụ, vd 'Độ giòn: 100%'")
    width: float = Field(0.78, gt=0.2, le=0.96)
    sprite: Sprite | None = Field(None, description="Ảnh pixel-art của món (cắt từ video) trên thẻ, phía trên hàng sao")

    _nfc = field_validator("text", "items", mode="before")(nfc_list)


class Prompt(_Hud):
    type: Literal["prompt"]
    button: str = Field("A", min_length=1, max_length=3, description="Chữ trên nút tay cầm: A, B, X, Y, LT, RT")
    text: str = Field("GRAB", description="Hành động: GRAB, POUR, HOLD TO SEAL…")
    hold: tuple[float, float] | None = Field(None, description="Vòng giữ-nút chạy đầy từ giây này tới giây kia "
                                                               "(timeline)")
    blink: bool = Field(True, description="Nhấp nháy nhẹ chờ bấm (dừng khi vòng giữ chạy)")

    _nfc = field_validator("text", mode="before")(nfc)

    @model_validator(mode="after")
    def _check_hold(self) -> "Prompt":
        if self.hold is not None and self.hold[1] <= self.hold[0]:
            raise ValueError("prompt: hold phải là [giây bắt đầu, giây đầy vòng] với giây sau lớn hơn")
        return self


class Icon(_Hud):
    type: Literal["icon"]
    icon: HudIcon | None = Field(None, description="star, check, lock, coin, heart, hand, clock, drop, bolt, flame")
    sprite: Sprite | None = Field(None, description="Hoặc ảnh pixel-art cắt từ video thay cho icon vẽ sẵn")
    spin: bool = Field(False, description="Lắc / xoay nhẹ liên tục (đồng xu, sao)")

    @model_validator(mode="after")
    def _one(self) -> "Icon":
        if (self.icon is None) == (self.sprite is None):
            raise ValueError("icon: cần đúng một trong hai — 'icon' (vẽ sẵn) hoặc 'sprite' (cắt từ video)")
        return self


class Slash(_Hud):
    """A sword-swipe streak (game 'cut' feedback): a bright tapered stroke sweeps across, leaves an afterimage
    and bursts into particles. Lasts ~0.3 s; centre it on the cut (or anchor it to a track)."""

    type: Literal["slash"]
    angle: float = Field(-28, ge=-180, le=180, description="Hướng vệt (độ): 0 = ngang trái→phải, dương = chéo lên")
    length: float = Field(0.55, gt=0.05, le=1.5, description="Dài vệt (tỉ lệ chiều rộng khung)")
    thickness: int = Field(22, ge=2, le=90, description="Độ dày chỗ dày nhất (px)")
    particles: int = Field(14, ge=0, le=40, description="Số mảnh vỡ bắn ra")
    color: str = Field("#FFFFFF", pattern=HEX_COLOR, description="Lõi vệt chém")
    accent_color: str = Field("#FF4A3D", pattern=HEX_COLOR, description="Quầng sáng + mảnh vỡ")
    enter: HudEase = "none"
    exit: HudEase = "none"


class Visor(_Hud):
    type: Literal["visor"]
    text: str = Field("LEVEL 1", description="Tên màn chơi ở thanh trên, vd 'LEVEL 1 · CÀ PHÁO MUỐI'")
    rec: bool = Field(True, description="Chấm REC nhấp nháy góc trên phải")
    clock: bool = Field(True, description="Đồng hồ chạy góc trên trái")
    scanlines: bool = Field(False, description="Vạch quét mờ toàn màn hình")
    margin: float = Field(0.035, ge=0, le=0.2, description="Khoảng cách góc khung kính tới mép (tỉ lệ rộng)")

    _nfc = field_validator("text", mode="before")(nfc)


HudItem = Annotated[Union[Reticle, Panel, Meter, Counter, Popup, Slots, Card, Prompt, Icon, Visor, Slash],
                    Field(discriminator="type")]


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
    hud: list[HudItem] = Field(default_factory=list, description="Giao diện game: reticle, panel, meter, counter, "
                                                                  "popup, slots, card, prompt, icon, visor, slash")
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
        extras = [f"{len(self.texts)} chữ", f"{len(self.graphics)} đồ hoạ", f"{len(self.hud)} HUD",
                  f"{len(self.motion)} motion",
                  f"captions {len(self.captions.segments) if self.captions else 0} đoạn", f"{len(self.audio)} audio",
                  f"look {self.look.preset}"]
        lines.append("  " + ", ".join(extras))
        return "\n".join(lines)


def frame_layout(plan: EditPlan, fps: int) -> tuple[list[int], list[int], int]:
    """Lay the timeline out in whole frames: frames per clip, frames each clip overlaps the previous one
    (transition length, 0 for a hard cut) and total frames. Clip boundaries are rounded from the plan's
    exact offsets rather than summed from rounded lengths, so video, audio and text never drift apart by
    more than half a frame, however many clips there are."""
    frames: list[int] = []
    overlaps: list[int] = []
    prev_end = 0
    for clip, offset in zip(plan.clips, plan.clip_offsets()):
        start = round(offset * fps) if clip.transition else prev_end
        end = max(start + 1, round((offset + clip.timeline_duration) * fps))
        overlap = 0
        if clip.transition and frames:
            overlap = min(max(prev_end - start, 1), frames[-1] - 1, end - start - 1)
            start = prev_end - overlap
        frames.append(end - start)
        overlaps.append(overlap)
        prev_end = end
    return frames, overlaps, prev_end


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
    for i, item in enumerate(plan.hud):
        where = f"hud #{i} ({item.type})"
        if item.start >= total:
            problems.append(f"{where} bắt đầu ({item.start:.2f}s) sau khi video kết thúc ({total:.2f}s)")
            continue
        spans = [(item.anchor, item.start, item.end)] if item.anchor else []
        if item.type == "slots":
            spans += [(src, max(item.times[k] - item.fly, 0), item.times[k])
                      for k, src in enumerate(item.sources) if src is not None and k < len(item.times)]
        for anchor, a, b in spans:
            from .world import check_anchor

            problems += check_anchor(plan, base_dir, anchor, a, b, where, probe)
        sprites = [sp for sp in getattr(item, "sprites", []) if sp] + (
            [item.sprite] if getattr(item, "sprite", None) else [])
        for sp in sprites:
            src = plan.resolve(sp.source, base_dir)
            if not src.exists():
                problems.append(f"{where}: sprite lấy từ '{sp.source}' nhưng không có file {src}")
            elif sp.t > probe(src).duration:
                problems.append(f"{where}: sprite t={sp.t:.2f}s vượt quá độ dài nguồn {probe(src).duration:.2f}s")
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
