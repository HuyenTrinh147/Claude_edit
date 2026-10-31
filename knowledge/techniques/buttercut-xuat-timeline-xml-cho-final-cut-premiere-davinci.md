---
title: buttercut: Xuất timeline XML cho Final Cut, Premiere, DaVinci
category: techniques
tags: [fcpxml, xmeml, final cut pro, premiere, davinci resolve, timeline, nle, timecode, buttercut]
updated: 2026-10-31
sources:
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/export_core.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/editor_base_core.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/fcpx_core.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/fcp7_core.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/premiere_core.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/resolve_core.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/resolve_legacy_core.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/media_verifier.rb
  - https://github.com/barefootford/buttercut/blob/main/lib/buttercut/library.rb
  - https://github.com/barefootford/buttercut/blob/main/dtd/FCPXMLv1_12.dtd
  - https://github.com/barefootford/buttercut/blob/main/spec/fixtures/full_media_all_clips.fcpxml
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/missing_footage.md
  - https://github.com/barefootford/buttercut/blob/main/docs/basic-xml-generation.md
  - https://github.com/barefootford/buttercut/blob/main/AGENTS.md
  - https://github.com/barefootford/buttercut/blob/main/README.md
---
# buttercut: Xuất timeline XML cho Final Cut, Premiere, DaVinci

ButterCut không render. Đầu ra là **timeline** để editor mở trong NLE và hoàn thiện: "Output: Working XML file ready to
import into the non-technical user's video editor". Cut YAML → `ruby lib/buttercut/export.rb --editor <x> cut.yaml out`.

| `--editor` | Định dạng | Ghi chú |
|---|---|---|
| `fcpx` | FCPXML 1.12 (`.fcpxml`) | Final Cut Pro (chỉ macOS) |
| `resolve` | FCPXML 1.12 (`_resolve.fcpxml`) | Resolve 19.1.1+ đọc được; anchor timecode khác FCP |
| `resolve_legacy` | xmeml v5 (FCP7 XML) | dự phòng khi clip lệch frame rate với timeline |
| `premiere` | xmeml v5 | thêm filter Basic Motion để xoay + scale vừa khung |

Dùng trực tiếp không qua Claude: `ButterCut.new([{path:, start_at:, duration:}], editor: :fcpx).save('t.fcpxml')`
(`docs/basic-xml-generation.md` còn ghi `editor: :fcp7`, nhưng code chỉ nhận `:fcpx, :resolve, :resolve_legacy,
:premiere`; tài liệu đã cũ, tin code).

## Khung FCPXML ButterCut sinh ra (rút từ fixture)

```xml
<fcpxml version="1.12">
  <resources>
    <format id="r1" width="1280" height="720" frameDuration="1001/24000s" colorSpace="1-1-1 (Rec. 709)"/>
    <asset id="r<md5 đường dẫn>" name="MVI_0309_720p.mov" uid="<md5 dạng uuid>" start="0s"
           audioRate="48000" hasAudio="1" hasVideo="1" format="r1" duration="101101/24000s">
      <media-rep kind="original-media" src="file:///duong/dan/ma%20hoa.mov"/>
    </asset>
  </resources>
  <library location="./"><event name="..."><project name="... <UTC timestamp>">
    <sequence duration="..." format="r1" tcStart="0s" audioRate="48k"><spine>
      <asset-clip name="MVI_0309_720p.mov" ref="r..." start="<timecode nguồn + in>" offset="<vị trí timeline>"
                  duration="..." audioRole="dialogue"><adjust-volume amount="-13.1"/></asset-clip>
    </spine></sequence>
  </project></event></library>
</fcpxml>
```

- Thời gian là **số hữu tỉ** `N/Ds` (giây), rút gọn bằng ƯCLN; giây thập phân đổi qua mẫu số 10000 rồi làm tròn theo
  lưới khung. Từ 1.9 asset trỏ file qua `<media-rep>` chứ không phải thuộc tính `src`.
- Mute = `adjust-volume amount="-96"` (Resolve chỉ hiểu số trần, bỏ qua `-96dB`). Clip thường `-13.1` (code không
  nói lý do; đừng chép mù).
- Ảnh tĩnh: format `FFVideoFormatRateUndefined` (không có frameDuration), asset `duration="0s"`, đặt bằng `<video>`;
  mặc định giữ 5s.
- Nguồn khác thông số timeline có `<format>` riêng, id dễ đọc `r_fmt_3840x2160_1000_30000_9-1-9`; màu: Rec.709
  `1-1-1`, Rec.2020 `9-1-9`, PQ `9-16-9`, HLG `9-18-9`.

## Những bẫy đã xử lý (đáng học nếu vedit làm exporter)

- **Lưới khung**: mọi giá trị trong sequence FCP đo theo lưới khung của SEQUENCE. Clip 23.976 trên timeline 24p phải
  làm tròn `start` về khung sequence gần nhất nhưng **không sớm hơn khung đầu của media**, và cắt `duration` cho không
  vượt phần media còn lại; nếu không FCP báo "not on an edit frame boundary" và để lại mẩu 1 khung.
- **xmeml**: `<in>/<out>` của clipitem tính theo lưới khung sequence (đã kiểm bằng nguồn 25fps trong timeline 30fps ở cả
  Premiere và Resolve); chỉ `<duration>`/`<timecode>` cấp file dùng khung gốc. Định nghĩa `<file>` đầy đủ một lần,
  các lần sau chỉ `<file id="..."/>`; `channelcount` không bao giờ 0; `<filter>` phải nằm sau `<file>`, trước
  `<sourcetrack>` (Premiere bỏ qua filter sai thứ tự).
- **Timecode nguồn**: `start` của asset = timecode của máy quay (track `tmcd`). Drop-frame (`;`) trừ 2 khung/phút
  (30) hoặc 4 (60) trừ mỗi phút thứ 10, kể cả khi media báo 30/1 (Final Cut Camera). Track timecode không đọc được thì
  **từ chối xuất** (anchor 0 sẽ làm FCP báo "invalid edit with no respective media"). Resolve đọc cả timecode không
  nằm trong `tmcd` (Sony XAVC `rtmd`, tag cấp format), FCP thì không.
- **Xoay**: FCP/Resolve tự xoay theo cờ của nguồn; Premiere thì phải ghi Basic Motion `rotation` (270 ghi -90) và
  `scale` = `min(seqW/dispW, seqH/dispH) × 100` (%). Timeline dọc khi clip đầu là nguồn xoay 1/4 vòng.
- **Frame rate lẫn lộn trong Resolve**: FCPXML làm clip lệch rate nhập vào bị offline vĩnh viễn; exporter in cảnh báo
  nêu tên clip và chỉ sang `resolve_legacy`.
- **Đường dẫn**: mã hoá phần trăm từng đoạn đường dẫn (dấu cách, ngoặc, #, &...); Windows `file://localhost/C%3a/...`.
- **ID ổn định**: `r` + MD5 đường dẫn tuyệt đối, xuất lại không đổi ID.
- **Kiểm tra**: `xmllint --noout --dtdvalid dtd/FCPXMLv1_12.dtd out.fcpxml`; trước khi ffprobe thì `verify_media`
  (ok/missing/phantom), thiếu footage là dừng, không bao giờ tự relink.
- **Định dạng nhập** là giao của 3 NLE: video `mov mp4 mts m2ts mxf avi`, ảnh `jpg jpeg png`; loại `mkv/webm` (FCP
  không nhập), `m4v`, `braw/r3d`, `heic/tiff/gif`. Container khác codec: cần thì remux/convert rồi thay.

## Giao cho người dùng

Copy ra Desktop (hỏi một lần, lưu `save_to_desktop_after_export`), mở bằng `open -a "Final Cut Pro" file`, kèm một câu
hướng dẫn nhập: FCP "File → Import → XML"; Premiere "File → Import"; Resolve "File → Import → Timeline". Không đưa
đường dẫn YAML cho người dùng.

## Những gì FCPXML 1.12 có mà ButterCut core chưa dùng

Kiểm trong DTD: `marker` (`start`, `duration`, `value`, `note`), `caption` (có `role`), `title`, `transition` trong
`spine`, `timeMap`/`timept` (đổi tốc độ), `adjust-conform type="fit|fill|none"`, `adjust-transform`
(`position`, `scale`), `adjust-crop`. Mỗi NLE hiểu các phần này khác nhau, phải thử nhập thật.

## Áp dụng vào vedit

**Đã có**: EditPlan đủ thông tin cho một cut list (nguồn, `start/end` giây nguồn, `speed`, `volume`, `mute`,
`transition`, `fit`, `focus_x/y`), audio tracks, captions có mốc; renderer tự làm tròn theo khung.

**Còn thiếu**: không có đầu ra nào để người dùng tinh chỉnh tay; mọi chỉnh sửa phải qua agent và render lại.

**Có nên xuất timeline cho NLE không?** Có, nhưng là **tuỳ chọn bổ sung, ưu tiên trung bình**, vì:
- Lợi: khi AI chưa "đúng ý", người dùng tự kéo lại điểm cắt; định dạng chuẩn; không ảnh hưởng luồng render hiện có.
- Hạn chế: giá trị riêng của vedit (chữ động ASS, đồ hoạ vector, SFX tổng hợp, look màu, punch/shake) không có tương
  đương gốc trong NLE nên sẽ mất nếu chỉ xuất cut list; chính README ButterCut thừa nhận khó "maintain working XML
  across three different editors". Người làm TikTok ở Việt Nam hay dùng CapCut, việc CapCut nhập FCPXML/xmeml **chưa
  được kiểm chứng**.

**Đề xuất theo ưu tiên**:
1. Hỏi người dùng có dùng phần mềm dựng nào (CapCut, Premiere, DaVinci, Final Cut) trước khi xây. Dễ.
2. Nếu có: `vedit export <slug> --format fcpxml|xmeml` giai đoạn 1 = cut list (asset-clip theo `start/end`, mute/volume,
   `adjust-conform fill` cho `fit: cover`), chữ/đồ hoạ thành `marker` (value = nội dung chữ), nhạc/SFX file thành
   clip âm thanh nối kèm (SFX tổng hợp phải render ra WAV trước), phụ đề xuất file `.srt` riêng. Nhắm DaVinci Resolve
   trước (miễn phí, đa nền tảng). Kiểm bằng `xmllint --dtdvalid` + nhập thật. Vừa.
3. Giai đoạn 2: render lớp chữ/đồ hoạ thành video nền trong suốt (ví dụ ProRes 4444
   `-c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le`, cần thử nghiệm) đặt ở track trên, để người dùng giữ được
   đồ hoạ của vedit khi chỉnh nhẹ phần hình. Khó.
4. `speed` → `timeMap` và `transition` → phần tử `transition`: chỉ làm khi đã có người dùng thật cần. Khó.
5. Khi viết exporter, giữ các quy tắc an toàn: ID ổn định theo MD5 đường dẫn, mã hoá URL, kiểm tra file nguồn còn tồn
   tại ngay trước khi xuất. (EditPlan đã chặn clip `end ≤ start` bằng `Clip._check_range`; `vedit validate` đã đối
   chiếu media thật.) Dễ.
