"""Library of text forms ("form chữ"): named presets for `TextOverlay`, so a plan can say
``{"text": "1. Xắt xắt xắt", "style": "nhan-so-vang"}`` instead of repeating ten fields.

Every preset is something that already rendered in a delivered project or in a studied sample video (``source``), with
fonts from `assets/fonts` (see knowledge/typography/thu-vien-font-cua-vedit.md for the exact family names). Fields given
explicitly next to ``style`` always win over the preset, and the plan keeps working if a preset is later retuned.

Presets hold look only (font, size, colours, outline, shape, animation, default height). Timing, text and exact
position stay with the plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TextStyle:
    name: str
    label: str            # short Vietnamese name
    use: str              # when to use it
    source: str           # where the look comes from
    sample: str           # sample text for the gallery
    fields: dict = field(default_factory=dict)
    extras: str = ""      # what a text overlay alone cannot do (sparkles, icon...) and how to add it


def _s(name, label, use, source, sample, fields, extras="") -> TextStyle:
    return TextStyle(name=name, label=label, use=use, source=source, sample=sample, fields=fields, extras=extras)


STYLES: dict[str, TextStyle] = {s.name: s for s in (
    _s("tieu-de-trang-vien-den", "Tiêu đề trắng viền đen (hook)",
       "Câu hook mở đầu 1–3 s: tiêu đề video, chủ đề của cả video. Dễ đọc trên mọi nền, giọng vui viết tay.",
       "ref-mim-4 (10 mẫu âm thanh làm video nấu ăn)", "10 mẫu âm thanh\nlàm video nấu ăn",
       {"font": "Shantell Sans", "bold": True, "size": 96, "color": "#FFFFFF", "outline": 7, "outline_color": "#1B1B1B",
        "y": 0.28, "animation": "pop"},
       "Sao lấp lánh quanh chữ: thêm 4–6 `graphics` kiểu sparkles ở các góc chữ (hồng #F58FB0 và xanh nhạt #A9C7F5)."),
    _s("nhan-so-vang", "Nhãn số thứ tự vàng",
       "Đánh số từng mục / mẹo: '1. Xắt xắt xắt', '2. Xịt xịt'. Một nhãn mỗi lần cắt, đổi nội dung mỗi cảnh.",
       "ref-mim-4", "1. Xắt xắt xắt",
       {"font": "Baloo 2", "bold": True, "size": 84, "color": "#FFD93D", "outline": 5, "outline_color": "#3A2A1A",
        "y": 0.12, "animation": "pop"}),
    _s("phu-de-nho-trang", "Phụ đề nhỏ trắng",
       "Dòng nhắc / CTA phụ dưới hình hoặc dưới biểu tượng: 'lưu ngay nhé', 'xem tiếp ở phần 2'.",
       "ref-mim-4", "lưu ngay nhé",
       {"font": "Be Vietnam Pro", "bold": False, "size": 52, "color": "#FFFFFF", "outline": 3, "outline_color": "#000000",
        "y": 0.7, "animation": "fade"}),
    _s("khung-tim-am-thanh", "Khung tìm âm thanh (giao diện tối)",
       "Mô phỏng ô tìm âm thanh của app dựng, hiện dưới hình khi giới thiệu một mẫu âm thanh / công cụ. Chữ 2 dòng: "
       "từ khoá tìm + tên âm thanh.",
       "ref-mim-4", "chopping\nCut with a knife",
       {"font": "Be Vietnam Pro", "bold": False, "size": 38, "color": "#E6E6EC", "outline": 0, "box": True,
        "box_color": "#1B1C24", "box_opacity": 0.94, "y": 0.66, "animation": "slide_up"},
       "Nút xanh '+' và nút 'Hủy' của khung thật: thêm 1 `graphics` badge màu #1FD3DC ở mép phải khung nếu cần giống hẳn."),
    _s("the-pill-kem", "Thẻ pill kem (mềm, đồ ăn / pastel)",
       "Dòng chữ dẫn truyện, hài mềm, video đồ ăn và pastel. Nền kem bo tròn giữ chữ đọc được trên mọi cảnh.",
       "dự án mèo búa thảo mộc; BẾP VR", "Sếp mèo mỏi lưng quá…",
       {"font": "Baloo 2", "bold": True, "size": 100, "color": "#4E3A68", "outline": 0, "shape": "pill",
        "shape_color": "#FFF8EE", "y": 0.14, "animation": "bounce"}),
    _s("so-buoc-anton-vang", "Số bước Anton vàng",
       "Số bước lớn 1/6 … 6/6 của video công thức / hướng dẫn. Chỉ dùng cho con số, kèm một nhãn nhỏ cho tên bước.",
       "dự án canh chua", "3/6",
       {"font": "Anton", "bold": False, "size": 190, "color": "#FFD84D", "outline": 8, "outline_color": "#2A1B4D",
        "y": 0.2, "animation": "pop"}),
    _s("tieu-de-anton-pill-kem", "Tiêu đề Anton trên pill kem",
       "Tiêu đề hook và CTA cuối video (2 dòng chữ HOA, ≤ 3 từ mỗi dòng) khi nền hình rất rối.",
       "dự án canh chua", "CANH CHUA\n6 BƯỚC",
       {"font": "Anton", "bold": False, "size": 150, "color": "#3B2A6B", "outline": 0, "shape": "pill",
        "shape_color": "#FFF3D6", "y": 0.3, "animation": "pop"}),
    _s("nhan-pill-nho", "Nhãn nhỏ trên pill kem",
       "Tên nguyên liệu / tên bước đi kèm số bước (THÁI, CÀ CHUA, VỚT BỌT). Vào trễ ~0.3 s sau số để mỗi lần chỉ có một thứ mới.",
       "dự án canh chua", "CÀ CHUA",
       {"font": "Be Vietnam Pro", "bold": True, "size": 64, "color": "#3B2A6B", "outline": 0, "shape": "pill",
        "shape_color": "#FFF3D6", "y": 0.31, "animation": "slide_up"}),
    _s("hormozi-nhan-manh", "Hormozi: nhấn mạnh trắng viền dày",
       "Caption nhấn từng từ cho video giáo dục / động lực: chữ HOA, viền đen dày, bật từng từ.",
       "knowledge/typography/kieu-chu-trend-tren-tiktok-reels", "SAI LẦM SỐ MỘT",
       {"font": "Montserrat", "bold": True, "size": 96, "color": "#FFFFFF", "outline": 9, "outline_color": "#000000",
        "y": 0.6, "animation": "word_pop"}),
    _s("hai-bangers-vang", "Hài / phản ứng Bangers vàng",
       "Từ cảm thán, phản ứng, hài (BÙM!, TRỜI ƠI!). Một đến hai từ, đi kèm punch / shake.",
       "knowledge/typography/thu-vien-font-cua-vedit", "TRỜI ƠI!",
       {"font": "Bangers", "bold": False, "size": 140, "color": "#FFE600", "outline": 9, "outline_color": "#C1121F",
        "y": 0.42, "animation": "bounce", "rotation": -6}),
    _s("khuyen-mai-anton-do", "Giá / khuyến mãi Anton trên băng đỏ",
       "Giá, giảm giá, số liệu gây chú ý. Băng đỏ hơi nghiêng như tem khuyến mãi.",
       "knowledge/typography/thu-vien-font-cua-vedit", "GIẢM 50%",
       {"font": "Anton", "bold": False, "size": 130, "color": "#FFFFFF", "outline": 0, "shape": "banner",
        "shape_color": "#E63946", "y": 0.35, "animation": "pop"}),
    _s("trich-dan-prata", "Trích dẫn Prata thanh",
       "Câu trích, lời kết cảm xúc, làm đẹp / thời trang. Chữ mảnh nên cần viền 2–3 hoặc nền tối phía sau.",
       "knowledge/typography/thu-vien-font-cua-vedit", "Chậm lại một chút",
       {"font": "Prata", "bold": False, "size": 78, "color": "#FFF6E5", "outline": 3, "outline_color": "#2B1D12",
        "y": 0.5, "animation": "fade"}),
)}


def get(name: str) -> TextStyle:
    try:
        return STYLES[name]
    except KeyError:
        raise ValueError(f"style '{name}' không có; chọn: {', '.join(STYLES)}") from None


def apply(data: dict) -> dict:
    """Merge a preset under the explicit fields of a TextOverlay dict (explicit fields win)."""
    name = data.get("style")
    if not name:
        return data
    return {**get(name).fields, **data}


def gallery(out: "Path", fonts_dir: "Path", font: str = "Inter", cols: int = 4) -> "Path":
    """Render every preset on a sample background and tile them into one labelled JPEG (the visual catalogue)."""
    import tempfile
    from pathlib import Path

    from PIL import Image, ImageDraw, ImageFont

    from .edl import EditPlan
    from .media import extract_frame
    from .render import render

    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cell_w, full_h, bar = 360, 640, 64
    top, bottom = int(full_h * 0.28), int(full_h * 0.64)   # the band that holds the sample text (y=0.45)
    cell_h = bottom - top
    label_font = ImageFont.truetype(str(Path(fonts_dir) / "BeVietnamPro-ExtraBold.ttf"), 22)
    small_font = ImageFont.truetype(str(Path(fonts_dir) / "BeVietnamPro-SemiBold.ttf"), 16)
    cells = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        bg = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(bg)
        for y in range(1920):   # warm wooden-board gradient with a few lighter bands: neither too bright nor too dark
            k = y / 1920
            draw.line([(0, y), (1080, y)], fill=(int(92 - 40 * k), int(58 - 28 * k), int(42 - 22 * k)))
        for y in (300, 760, 1180, 1500):
            draw.rectangle([0, y, 1080, y + 16], fill=(116, 76, 54))
        bg.save(tmp_dir / "bg.png")
        for style in STYLES.values():
            plan = EditPlan.model_validate({
                "sources": {"bg": "bg.png"}, "clips": [{"source": "bg", "duration": 1.6}],
                "texts": [{"text": style.sample, "start": 0.1, "end": 1.6, "style": style.name, "y": 0.45}]})
            video = tmp_dir / f"{style.name}.mp4"
            render(plan, video, base_dir=tmp_dir, preview=True, font=font, fonts_dir=fonts_dir, work_dir=tmp_dir / "w")
            frame = extract_frame(video, 1.2, tmp_dir / f"{style.name}.png", width=cell_w)
            cells.append((style, Image.open(frame).convert("RGB").resize((cell_w, full_h)).crop((0, top, cell_w, bottom))))
        rows = -(-len(cells) // cols)
        sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + bar)), (251, 245, 233))
        d = ImageDraw.Draw(sheet)
        for i, (style, img) in enumerate(cells):
            x, y = (i % cols) * cell_w, (i // cols) * (cell_h + bar)
            sheet.paste(img, (x, y))
            d.text((x + 10, y + cell_h + 8), style.name, fill=(74, 59, 82), font=label_font)
            d.text((x + 10, y + cell_h + 36), style.label, fill=(138, 123, 140), font=small_font)
        sheet.save(out, quality=88)
    return out
