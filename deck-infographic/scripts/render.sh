#!/bin/bash
# 図のスクリプトから本文の範囲の HTML・SVG・JSON（大きさと文字の一覧）を書き出し、Chrome headless で 2 倍の PNG にする。
# 使い方: render.sh <図のスクリプト.py> <出力.png>
# <出力.png> は文字を抜いた図（pptx では文字をテキストボックスで重ねる）。
# 同じフォルダの with-text/<出力の名前>.png に文字入りの図（見た目の確かめ用・build_deck.py --text image 用）も書く。
# HTML・SVG・JSON はスクリプトと同じフォルダに <スクリプト名>.html / .notext.html / .svg / .json で置く。
# 図のスクリプトは同じフォルダの figlib.py を import する（figlib.write が JSON を書く）。
set -euo pipefail
script="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
dir="$(dirname "$script")"
name="$(basename "$script" .py)"
mkdir -p "$(dirname "$2")/with-text"
outdir="$(cd "$(dirname "$2")" && pwd)"
out="$outdir/$(basename "$2")"
out_full="$outdir/with-text/$(basename "$2")"
# Mac 以外では CHROME に Chrome（Chromium）の場所を渡す
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$chrome" ] || { echo "Chrome が無い（brew install --cask google-chrome、または CHROME に場所を渡す）" >&2; exit 1; }
# Pillow は uv があれば uv で用意する（無ければ手元の python3 の Pillow を使う）
if command -v uv >/dev/null; then PY=(uv run -q --no-project --with pillow python3); else PY=(python3); fi
# 図のスクリプトは標準ライブラリだけで動く。uv があれば uv の Python で動かす
if command -v uv >/dev/null; then FIG=(uv run -q --no-project python3); else FIG=(python3); fi
(cd "$dir" && "${FIG[@]}" "$script" "$dir/$name.html" "$dir/$name.svg")
[ -f "$dir/$name.notext.html" ] || { echo "$dir/$name.notext.html が無い。source/ の figlib.py が古いので、<スキル>/scripts/figlib.py を写し直す" >&2; exit 1; }
size="$(python3 -c "import json,sys; m=json.load(open(sys.argv[1])); print(f\"{m['width']},{m['height']}\")" "$dir/$name.json")"
rm -f "$out" "$out_full"   # Chrome が失敗したとき、前回の PNG で確認を通さないため
shot() {
  "$chrome" --headless=new --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --window-size="$size" \
    --screenshot="$2" "file://$1" 2>/dev/null
}
shot "$dir/$name.notext.html" "$out"
shot "$dir/$name.html" "$out_full"
# 本文の範囲の外に描いたもの（切れる部分）が無いかを、ページ全体の大きさの図で確かめる
page_png="$(mktemp -d)/page.png"
if [ -f "$dir/$name.page.html" ]; then
  "$chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1920,1080 \
    --screenshot="$page_png" "file://$dir/$name.page.html" 2>/dev/null
fi
# Chrome が高さを切ることがあるので、JSON の 2 倍の大きさになっているかを確かめる
"${PY[@]}" -c "
import json, sys
from PIL import Image
m = json.load(open(sys.argv[3]))
want = (m['width'] * 2, m['height'] * 2)
for f in sys.argv[1:3]:
    got = Image.open(f).size
    print(f, got)
    if got != want:
        sys.exit(f'expected {want}, got {got}')
print('pptx の文字にするまとまり:', len(m.get('texts') or []))
page = sys.argv[4]
try:
    im = Image.open(page).convert('L')
except FileNotFoundError:
    sys.exit(0)
x0, y0 = m['x'], m['top']
x1, y1 = x0 + m['width'], y0 + m['height']
mask = Image.new('L', im.size, 255)
mask.paste(0, (max(0, x0 - 2), max(0, y0 - 2), x1 + 2, y1 + 2))   # 本文の範囲（と縁の 2px）は見ない
dark = im.point(lambda v: 255 if v < 245 else 0)
from PIL import ImageChops
box = ImageChops.multiply(dark, mask).getbbox()
if box:
    import os
    for f in sys.argv[1:3]:
        os.remove(f)   # 切れた図を貼らないため
    sys.exit(f'本文の範囲（x={x0}〜{x1}・y={y0}〜{y1}）の外に描いたものがある（切れる）: {box}。図の座標を top・bottom に合わせて組み直す')
" "$out" "$out_full" "$dir/$name.json" "$page_png"
