#!/bin/bash
# 図のスクリプトから本文の範囲の HTML・SVG・JSON（大きさ）を書き出し、Chrome headless で 2 倍の PNG にする。
# 使い方: render.sh <図のスクリプト.py> <出力.png>
# HTML・SVG・JSON はスクリプトと同じフォルダに <スクリプト名>.html / .svg / .json で置く。
# 図のスクリプトは同じフォルダの figlib.py を import する（figlib.write が JSON を書く）。
set -euo pipefail
script="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
dir="$(dirname "$script")"
name="$(basename "$script" .py)"
mkdir -p "$(dirname "$2")"
outdir="$(cd "$(dirname "$2")" && pwd)"
out="$outdir/$(basename "$2")"
# Mac 以外では CHROME に Chrome（Chromium）の場所を渡す
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
(cd "$dir" && python3 "$script" "$dir/$name.html" "$dir/$name.svg")
size="$(python3 -c "import json,sys; m=json.load(open(sys.argv[1])); print(f\"{m['width']},{m['height']}\")" "$dir/$name.json")"
rm -f "$out"   # Chrome が失敗したとき、前回の PNG で確認を通さないため
"$chrome" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size="$size" \
  --screenshot="$out" "file://$dir/$name.html" 2>/dev/null
# Chrome が高さを切ることがあるので、JSON の 2 倍の大きさになっているかを確かめる
python3 -c "
import json, sys
from PIL import Image
m = json.load(open(sys.argv[2]))
want = (m['width'] * 2, m['height'] * 2)
got = Image.open(sys.argv[1]).size
print(sys.argv[1], got)
sys.exit(0 if got == want else f'expected {want}, got {got}')
" "$out" "$dir/$name.json"
