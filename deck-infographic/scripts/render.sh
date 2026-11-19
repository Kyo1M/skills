#!/bin/bash
# 図のスクリプトから HTML・SVG を書き出し、Chrome headless で 3840x2160 の PNG にする。
# 使い方: render.sh <図のスクリプト.py> <出力.png>
# HTML・SVG はスクリプトと同じフォルダに <スクリプト名>.html / .svg で置く。
set -euo pipefail
script="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
dir="$(dirname "$script")"
name="$(basename "$script" .py)"
out="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
python3 "$script" "$dir/$name.html" "$dir/$name.svg"
"$chrome" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1920,1080 \
  --screenshot="$out" "file://$dir/$name.html" 2>/dev/null
python3 -c "from PIL import Image; import sys; s=Image.open(sys.argv[1]).size; print(sys.argv[1], s); sys.exit(0 if s==(3840,2160) else 1)" "$out"
