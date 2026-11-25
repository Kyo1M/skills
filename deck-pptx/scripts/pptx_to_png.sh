#!/usr/bin/env bash
# pptx → PDF → 全ページの PNG。LibreOffice は別のプロファイルで動かす（使用中のプロファイルがあると、何も出さずに失敗する）。
#   pptx_to_png.sh <pptx> [出力のフォルダ（既定は <pptx の名前>-png）] [解像度 dpi（既定 80）]
# 出力は page-01.png … と、全ページを並べた contact.png（ImageMagick があるとき）。最後にページ数を出す。
set -euo pipefail
in="$1"
out="${2:-${in%.*}-png}"
dpi="${3:-80}"
SOFFICE="${SOFFICE:-$(command -v soffice || echo /Applications/LibreOffice.app/Contents/MacOS/soffice)}"
command -v pdftoppm >/dev/null || { echo "pdftoppm が無い（brew install poppler）" >&2; exit 1; }
[ -x "$SOFFICE" ] || command -v "$SOFFICE" >/dev/null || { echo "soffice が無い（brew install --cask libreoffice）" >&2; exit 1; }
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
"$SOFFICE" -env:UserInstallation="file://$tmp/profile" --headless --convert-to pdf --outdir "$tmp" "$in" >/dev/null 2>&1
pdf="$tmp/$(basename "${in%.*}").pdf"
[ -f "$pdf" ] || { echo "PDF にできなかった: $in" >&2; exit 1; }
mkdir -p "$out"
rm -f "$out"/page-*.png
pdftoppm -r "$dpi" -png "$pdf" "$out/page"
# pdftoppm の番号（page-1・page-01・page-001）を 2 桁以上にそろえる
for f in "$out"/page-*.png; do
  n="$(basename "$f" .png | sed 's/^page-0*//')"
  [ -z "$n" ] && n=0
  mv -n "$f" "$out/$(printf 'page-%02d.png' "$n")" 2>/dev/null || true
done
if command -v magick >/dev/null; then
  magick montage "$out"/page-*.png -tile 4x -geometry +6+6 -background '#bbbbbb' "$out/contact.png" 2>/dev/null || true
fi
ls "$out"/page-*.png | wc -l | tr -d ' '
