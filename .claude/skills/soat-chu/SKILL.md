---
name: soat-chu
description: Agent 6 — Soát chữ: soát chữ trên màn hình và phụ đề của một dự án bằng luật cứng (`vedit textcheck`) cộng chính tả tiếng Việt, đối chiếu lời thoại và dữ kiện, trả danh sách lỗi có mốc giây để sửa trước khi dựng. Dùng khi người dùng muốn kiểm tra chữ, chính tả, thời gian đọc hoặc vùng an toàn.
argument-hint: [slug dự án]
---

Yêu cầu soát chữ: $ARGUMENTS

Trao đổi bằng tiếng Việt.

1. Nếu `command -v vedit` không thấy lệnh, chạy `bash scripts/setup.sh`.
2. Xác định dự án (slug hoặc dự án mới nhất có `edit_plan.json`). Chưa có EditPlan → nói rõ chưa có gì để soát
   (cần `kich-ban` bước 2 trước).
3. Agent tool `subagent_type: video-text-checker`: truyền slug. Có preview thì nói để nó xem khung hình.
4. Phán quyết CẦN SỬA → giao danh sách lỗi cho `video-editor` (thời gian / vị trí) hoặc `video-scriptwriter` (lời / chữ),
   chạy lại `vedit textcheck <slug>` đến khi hết LỖI (tối đa 2 vòng, sau đó nói thật điều còn vướng).
5. Gửi `projects/<slug>/script/textcheck.md` bằng SendUserFile kèm tóm tắt: số lỗi, 3 lỗi nặng nhất, đã sửa gì.
6. Ghi `vedit note <slug> "<kết quả soát chữ>" --kind "Agent 6"`.
