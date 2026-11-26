#!/usr/bin/env bash
# deck-pptx の確認。別の Mac で導入したときもこれ 1 本で確かめる。出力は一時フォルダに書き、終わったら消す。
#   selftest.sh [--keep]   # --keep で一時フォルダを残す（画像を見たいとき）
# 要るもの: uv・LibreOffice（soffice）・poppler（pdftoppm）・Google Chrome（インフォグラフィックの確認）
set -euo pipefail
SK="$(cd "$(dirname "$0")/.." && pwd)"
IG="${DECK_INFOGRAPHIC:-$SK/../deck-infographic}"
[ -d "$IG" ] || IG="$HOME/.claude/skills/deck-infographic"
export DECK_PPTX="$SK"
tmp="$(mktemp -d)"
[ "${1:-}" = "--keep" ] && echo "一時フォルダ: $tmp" || trap 'rm -rf "$tmp"' EXIT
run() { uv run -q "$@"; }
ok() { echo "OK  $*"; }
ng() { echo "NG  $*" >&2; exit 1; }

for cmd in uv pdftoppm; do command -v $cmd >/dev/null || ng "$cmd が無い"; done
command -v soffice >/dev/null || [ -x /Applications/LibreOffice.app/Contents/MacOS/soffice ] || ng "LibreOffice が無い"

cd "$SK/references"
run ../scripts/outline.py --check example-outline.md >/dev/null || ng "構成 md の読み取り"
ok "構成 md を読めた"

# 1. テンプレートから組む（ロゴあり・ロゴなし）
for b in unbranded continova; do
  run example-build.py example-outline.md "$tmp/$b.pptx" "$b" >/dev/null || ng "$b の組み立て"
  run ../scripts/check_text.py example-outline.md "$tmp/$b.pptx" >/dev/null || { run ../scripts/check_text.py example-outline.md "$tmp/$b.pptx"; ng "$b の文言の照合"; }
  run ../scripts/check_package.py "$tmp/$b.pptx" >/dev/null || ng "$b のパッケージ"
  n="$(../scripts/pptx_to_png.sh "$tmp/$b.pptx" "$tmp/$b-png" 40)"
  want="$(run ../scripts/slide_text.py "$tmp/$b.pptx" --json | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))')"
  [ "$n" = "$want" ] || ng "$b の画像の枚数（$n、ページは $want）"
  ok "$b: 組み立て・文言の照合・パッケージ・画像 $n 枚"
done

# 2. ロゴなし版にロゴの画像とノートが無い
logo="$(python3 - "$SK/assets/templates/continova-business-template.pptx" <<'PY'
import hashlib, sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
print(",".join(sorted({hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if "/media/" in n})))
PY
)"
[ -n "$logo" ] || ng "ロゴあり版にロゴの画像が見つからない"
for f in "$SK/assets/templates/unbranded-business-template.pptx" "$SK/assets/templates/unbranded-business-template.potx" "$tmp/unbranded.pptx"; do
  run ../scripts/check_package.py "$f" --no-notes --no-media "$logo" >/dev/null || ng "ロゴなし: $(basename "$f")"
done
run ../scripts/check_package.py "$SK/assets/templates/continova-business-template.pptx" --no-notes >/dev/null || ng "ロゴあり版のノート"
python3 - "$SK/assets/templates" <<'PY' || ng "テンプレートに社名・他社の製品名が残っている"
import glob, re, sys, zipfile
for f in glob.glob(sys.argv[1] + "/*.p?tx"):
    z = zipfile.ZipFile(f)
    for n in z.namelist():
        if n.endswith(".xml") and not re.match(r"ppt/slides/", n):  # サンプルのページの本文以外のすべて
            b = z.read(n)
            for w in (b"ChatGPT", b"Walnut") + ((b"continova",) if "unbranded" in f else ()):
                if w in b:
                    sys.exit(f"{f}: {n} に {w.decode()}")
PY
ok "ロゴなし版にロゴの画像が無い・テンプレートにノートと社名・製品名が無い"

# 3. 版を上げる（前回の資料を土台に、並べ替え・複製・写し・文言と表と図の差し替え）
run example-revise.py "$tmp/unbranded.pptx" "$tmp/continova.pptx" "$tmp/revised.pptx" "$tmp/changes.json" >/dev/null || ng "版上げの組み立て"
run ../scripts/check_text.py --against "$tmp/unbranded.pptx" --changes "$tmp/changes.json" "$tmp/revised.pptx" >/dev/null \
  || { run ../scripts/check_text.py --against "$tmp/unbranded.pptx" --changes "$tmp/changes.json" "$tmp/revised.pptx"; ng "版上げの照合"; }
run ../scripts/check_package.py "$tmp/revised.pptx" >/dev/null || ng "版上げのパッケージ"
ok "版上げ: 差し替えた所だけが変わった"

# 3b. テンプレートの系統でない資料（1440×810pt、名前付きの枠）を土台にする
run ../scripts/selftest_named.py "$tmp/continova.pptx" "$tmp/named" >/dev/null || ng "名前付きの枠の資料からの組み立て"
run ../scripts/check_package.py "$tmp/named/named-out.pptx" >/dev/null || ng "名前付きの枠の資料のパッケージ"
n="$(../scripts/pptx_to_png.sh "$tmp/named/named-out.pptx" "$tmp/named/png" 40)"
[ "$n" = 4 ] || ng "名前付きの枠の資料の画像の枚数（$n）"
ok "前回の資料（1440×810pt・名前付きの枠）から組めた"

# 4. インフォグラフィック案（図 1 枚を書き出し、文字を pptx の文字にして足す）
if [ -d "$IG" ]; then
  mkdir -p "$tmp/ig/source" "$tmp/ig/inputs"
  cp "$IG/scripts/figlib.py" "$tmp/ig/source/"
  sed -E 's/^PAGE *=.*/PAGE = 8/; s/^TOP *=.*/TOP = 380/' "$IG/references/example-cycle.py" > "$tmp/ig/source/fig01_cycle.py"
  "$IG/scripts/render.sh" "$tmp/ig/source/fig01_cycle.py" "$tmp/ig/inputs/01-cycle.png" >/dev/null || ng "図の書き出し（Chrome）"
  run "$IG/scripts/build_deck.py" "$tmp/unbranded.pptx" "$tmp/ig/out.pptx" --figures "$tmp/ig/inputs" --meta "$tmp/ig/source" \
    --body-top 380 --lead-y 255 270 --title-y 100 110 --footer-name "" >/dev/null || ng "図の案の組み立て"
  run ../scripts/check_package.py "$tmp/ig/out.pptx" >/dev/null || ng "図の案のパッケージ"
  texts="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["figures"][0]["editableTexts"])' "$tmp/ig/source/build-report.json")"
  [ "$texts" -gt 0 ] || ng "図の文字が pptx の文字になっていない"
  multi="$(python3 -c 'import json,sys; print(sum(1 for t in json.load(open(sys.argv[1]))["texts"] if len(t.get("lines") or []) > 1))' "$tmp/ig/source/fig01_cycle.json")"
  [ "$multi" -gt 0 ] || ng "lines() で描いた複数行が 1 つのテキストボックスになっていない"
  printf 'from figlib import *\nwrite([text(600, 300, "外", 24)], page=1, top=380)\n' > "$tmp/ig/source/fig09_out.py"
  ! (cd "$tmp/ig/source" && python3 fig09_out.py x.html) >/dev/null 2>&1 || ng "本文の範囲の外の文字で止まらない"
  ok "インフォグラフィック案: 図の文字を $texts 個のテキストボックスにした（複数行のまとまり $multi 個）。範囲の外の文字で止まる"
else
  echo "--  deck-infographic が見つからないので、インフォグラフィック案の確認は飛ばした"
fi
echo "selftest: すべて通った"
