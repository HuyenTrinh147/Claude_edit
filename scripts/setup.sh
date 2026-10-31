#!/usr/bin/env bash
# Cài vedit vào workspace (chạy lại nhiều lần không sao).
#   bash scripts/setup.sh
# Trong Claude Code trên web: thêm dòng sau vào Setup script của môi trường để mỗi phiên mới tự cài:
#   cd Claude_edit && bash scripts/setup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v ffmpeg >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1 && [ "$(id -u)" = "0" ]; then
    echo "• Cài ffmpeg..."
    apt-get update -qq && apt-get install -y -qq ffmpeg >/dev/null
  else
    echo "✗ Chưa có ffmpeg — cài theo https://ffmpeg.org/download.html rồi chạy lại." >&2
    exit 1
  fi
fi

if [ ! -x .venv/bin/python ]; then
  echo "• Tạo môi trường Python (.venv)..."
  python3 -m venv .venv
fi
echo "• Cài vedit + thư viện..."
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -e ".[gdrive,track,dev]"

# Đưa lệnh `vedit` ra PATH chung để mọi shell (kể cả subagent) gọi được
for dir in /usr/local/bin "$HOME/.local/bin"; do
  if mkdir -p "$dir" 2>/dev/null && [ -w "$dir" ]; then
    ln -sf "$ROOT/.venv/bin/vedit" "$dir/vedit"
    LINKED="$dir/vedit"
    break
  fi
done

mkdir -p inbox projects
echo "✓ vedit sẵn sàng: ${LINKED:-$ROOT/.venv/bin/vedit}"
"$ROOT/.venv/bin/vedit" doctor | sed -n '2,8p'
