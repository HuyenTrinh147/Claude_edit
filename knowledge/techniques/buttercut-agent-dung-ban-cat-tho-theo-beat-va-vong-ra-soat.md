---
title: buttercut: Agent dựng bản cắt thô theo beat và vòng rà soát
category: techniques
tags: [agent dựng, roughcut, beat, rà soát, nhịp, ghi chú biên tập, prompt, buttercut]
updated: 2026-10-31
sources:
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/roughcut_launch_prompt.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/roughcut_agent_prompt.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/roughcut_path.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/SKILL.md
  - https://github.com/barefootford/buttercut/blob/main/skills/cut/cut_yaml_schema.md
  - https://github.com/barefootford/buttercut/blob/main/AGENTS.md
---
# buttercut: Agent dựng bản cắt thô theo beat và vòng rà soát

Sau khi kế hoạch được duyệt, main thread giao một **sub-agent general-purpose** dựng cut YAML. Prompt khởi chạy
(`roughcut_launch_prompt.md`) gói cả phương pháp trong một câu:

> "Create an initial draft that focuses on a coherent story with coherent dialogue, then review your work, focusing
> on the dialogue, consider what improvements should be made, then make those improvements and refine before
> returning."

Và vai trò của kế hoạch: "The plan is your compass. The library is your full toolkit."

## Phong cách làm việc

- **Bất đồng bộ**: "You do not ping the user mid-task." Làm trọn một bản rồi trả kèm lập luận và phương án khác.
- **Lặp, không làm một lèo**:
  1. Lấy từng beat của kế hoạch.
  2. Chỉ đọc transcript của clip thật sự cần.
  3. Thả clip ứng viên vào YAML, "close enough, not perfect".
  4. Sang beat tiếp.
  5. "After three beats **look back**. Improve earlier clips that get said better later. Tighten dragging beats.
     Swap in stronger moments."

## Mỗi beat làm gì

- Lướt tóm tắt để lập danh sách ngắn → với clip video: đọc contact sheet + lấy lời bằng `script_extractor.rb` →
  chốt in/out bằng grep mốc từ (xem `techniques/buttercut-cat-theo-moc-tung-tu-giu-thoai-lien-mach`).
- Cần chắc hơn thì tạo contact sheet cho đúng khoảng (`contact_sheet.rb <video> 02:00 02:30`), nhưng không zoom đệ
  quy đi tìm khung hoàn hảo.
- Ảnh tĩnh: chọn thời lượng giữ theo nhịp ("a title card might sit 2–3s; a hero photo longer"); ảnh không có tiếng nên
  cắt sang ảnh là cắt sang im lặng.
- Mỗi clip ghi kèm `dialogue` (lời đã sửa chính tả) và `visual_description` (mô tả cảnh trong ngoặc vuông), để người và
  máy đọc cut như đọc paper edit.

## Vòng rà soát theo format (bước 4 của prompt)

Khi đã có bản đầu đủ, rà lại có chủ đích theo loại sản phẩm (vlog, YouTube Short, long-form, documentary...):
- **Độ dài beat**: "A one-minute static exposition might be right for a documentary but probably not correct for a
  vlog. Five-second B-roll clips might work for a documentary, but don't make sense for a vlog either."
- **Độ gọn của lời**: có câu nào quá dài dòng với format/khán giả không; cắt trong câu để bỏ từ đệm, câu mở yếu, câu
  nói lại.
- **Trùng lặp**: một ý nói hai lần ở hai beat thì bỏ bản yếu.
- Dựa vào `user_context` (đã biết gì về người dùng) và quy ước của format.

Sau đó điền `metadata.total_duration` (tổng thời lượng clip), `created_date`, kiểm tra `description` còn đúng.

## Trả về: đường dẫn + ghi chú biên tập

Không tự xuất XML; trả "YAML path" và ghi chú dạng văn xuôi: phương án đã cân nhắc, chỗ phải phán đoán, chỗ lệch kế
hoạch, cảnh báo nhịp. Ví dụ gốc:

> "For the ending, the dinosaur-wins angle could work — we'd swap in clips X, Y, Z. Happy to rebuild if that's the
> direction." / "The intro currently runs 35s; if you want it tighter, just the helicopter takeoff (clip K) lands in 8s."

Main thread báo người dùng **rất ngắn gọn** các ghi chú này; sửa nhỏ thì main thread sửa thẳng YAML và xuất lại, đổi
cấu trúc lớn thì chạy lại sub-agent với kế hoạch mới. Mỗi lần dựng ra một file cut mới có timestamp.

## Ràng buộc của bản core

"Single-track timelines only": không đề xuất B-roll đè lên lời, picture-in-picture hay bất kỳ cấu trúc nào cần tiếng
clip này chạy tiếp khi hình đã sang clip khác; cắt sang cảnh khác là cắt cả tiếng.

## Áp dụng vào vedit

**Đã có**: Agent 3 có vòng kiểm tra **hình ảnh** (render preview, xem khung, sửa chữ tràn/che chủ thể, 1–3 vòng);
EditPlan có `note` cho từng clip; vedit có nhiều lớp (nhạc, SFX, chữ) nên không bị ràng buộc một track.

**Còn thiếu**: vòng rà soát **biên tập** (câu chuyện, nhịp từng beat, trùng lặp, lời dài dòng); dựng theo beat có
"nhìn lại"; ghi chú phương án thay thế cho người dùng chọn nhanh; lưu phiên bản (hiện ghi đè `edit_plan.json`).

**Đề xuất theo ưu tiên**:
1. Thêm vào prompt Agent 2 (viết EditPlan) quy trình 2 lượt: bản nháp theo beat của kế hoạch đã duyệt → rà soát theo
   checklist video ngắn → sửa. Checklist gợi ý: hook có xảy ra trong 1.5s đầu; mỗi beat có đúng số giây kế hoạch; mỗi
   clip có lý do tồn tại (bỏ clip chỉ "đẹp"); không lặp ý/lặp cảnh; câu thoại trọn vẹn; kết có vòng lặp hoặc CTA.
   Dễ.
2. Kết thúc Agent 2/3 bằng mục "Ghi chú biên tập": 2–3 phương án thay thế cụ thể có mốc (định dạng ví dụ: "hook khác: tay thả
   cà vào hũ, 13.0–14.3s nguồn"; "bản ngắn hơn: bỏ clip 4 và 6"), để main thread hỏi người dùng có muốn đổi không.
   Dễ.
3. Phiên bản hoá: mỗi lần sửa lưu `edit_plan_v<N>.json` và `renders/final_v<N>.mp4` (không ghi đè), main thread nêu
   khác biệt giữa các bản. Dễ.
4. Dựng theo beat với bước "nhìn lại sau 3 beat" cho video dài hơn 30s. Dễ (prompt).
5. Sửa nhỏ do main thread làm thẳng trên EditPlan + render lại; đổi cấu trúc thì quay lại cổng duyệt concept. Dễ.
