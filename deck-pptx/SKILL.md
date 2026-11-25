---
name: deck-pptx
description: 構成 md（deck-outline の成果物）から、PowerPoint で直せる pptx を組むスキル。同梱の事業用テンプレート（ロゴあり・ロゴなし）か前回の資料を土台にし、共通の部品（文言・見出し帯カード・ステップ・マトリクス・表・図・版上げの道具）を呼ぶ資料ごとの短い組み立てスクリプトを書いて組む。組むたびに全ページを画像にし、構成 md との文言の照合とパッケージの確認を通す。依頼者が手直しした pptx の版上げ（文言・表・図の差し替え、ページの並べ替え・再掲）もここで行う。「pptx にして」「構成 md から資料を作って」「パワポで作って」「定例資料を組んで」「前回の資料を元に今週の版を」「pptx の文言を差し替えて」「/deck-pptx」等のリクエスト時に起動。構成がまだ無ければ先に deck-outline、図解案を足すのは deck-infographic、HTML スライドは html-slide-deck。
---

# deck-pptx — 構成 md から pptx を組む

構成 md の実文言を、PowerPoint で直せる pptx にする。文字は文字、帯・カードは図形、表は表で組み、ページ全体を 1 枚の画像で貼らない。組み方は資料ごとの短いスクリプト（`build.py`）に書き、部品と確かめ方はこのスキルのものを使う。

## 資料作成の流れでの位置

| 工程 | スキル | 成果物 |
|---|---|---|
| 1 | deck-outline | 構成 md（実文言） |
| 2 | deck-critique | 構成 md の批評 |
| 3 | **deck-pptx** | pptx |
| 4 | deck-infographic | 図の案のページを足した版（図の中の文字も PowerPoint で直せる） |

## 道具

`<スキル>` はこのスキルのフォルダ（`~/.claude/skills/deck-pptx`）。スクリプトは `uv run` で動き、依存は各ファイルの先頭に書いてある。

| ファイル | 役割 |
|---|---|
| `scripts/template.py` | 土台を開く（`open_deck`）、レイアウトでページを足す（`new_slide`）、題・リード文（`set_title`・`set_lead`・`set_text`）、本文の範囲（`body_area`）、サンプル・前回のページの複製（`find_sample`・`duplicate`）、並べ替え・外す（`keep_slides`・`move_slide`・`delete_slide`）、枠だけ残す（`strip_body`）、別の資料から写す（`import_slide`）、コメントを読む・外す、保存の後始末（`finalize`）。`--inspect` でレイアウト・ページ・図形の一覧 |
| `scripts/parts.py` | 部品。文言（`text`・`body_text`・`bullets`・`note`）、図形（`rect`・`arrow`・`heading`・`cards`・`steps`・`chevrons`・`flow`・`matrix`・`quad2`・`month_band`・`callout`・`ask_box`・`warn_band`）、表（`table`・`gantt`・`mark_cell`）、図（`picture`・`figure_page`・`shot_placeholder`）、版上げ（`shape`・`replace_paras`・`set_cell`・`rebuild_table`・`replace_picture`・`move`・`delete`・`clone_shape`）、見積もり（`text_height`・`fit_size`・`n_lines`） |
| `scripts/outline.py` | 構成 md を読む。`--check` で読めない行・知らない欄・ID の重複を出して止める。`--dump` で読んだ中身 |
| `scripts/check_text.py` | 構成 md と pptx の文言の照合（新しく作ったとき）、元の pptx と差し替えの一覧の照合（版を上げたとき） |
| `scripts/check_package.py` | パッケージの確認（PowerPoint が修復を求める壊れ方が無いか） |
| `scripts/pptx_to_png.sh` | pptx → 全ページの PNG（LibreOffice・poppler）。ImageMagick があれば全ページを並べた `contact.png` も |
| `scripts/slide_text.py` | 全ページの文言を書き出す |
| `scripts/selftest.sh` | スキルそのものの確認（別の Mac に入れたときもこれで確かめる）。テンプレートから組む・版を上げる・テンプレートの系統でない資料（1440×810pt・名前付きの枠、`selftest_named.py`）から組む・インフォグラフィック案、の 4 つの経路を通す |
| `scripts/clean_template.py` | テンプレートを改訂したときの掃除（ノート・使っていない画像を外し、potx も書く） |
| `references/type-map.md` | 構成 md の型 → テンプレートのレイアウト・サンプルページ・部品の対応表 |
| `references/example-build.py` | テンプレートから組む例。新しい資料はこれを写して始める |
| `references/example-revise.py` | 前回の資料を土台に版を上げる例 |
| `references/example-outline.md` | 例の構成 md（架空のテーマ） |
| `references/template-guide.md` | テンプレートの使い方・ロゴの差し替え方・改訂の手順 |

座標と文字の大きさは 1920×1080 の px で書く。土台のスライドの大きさに換算されるので、テンプレート（960×540pt）でも 1440×810pt の資料でも同じ値で書ける。文字列の記法は `**太字**`・`{強:…}`（青の太字）・`{悪:…}`（赤の太字）・`{良:…}`（緑の太字）・`{灰:…}`・`[文字](URL)`。「（TODO: …）」は自動で赤になる。

面の使い方（骨格と詳細、見出し帯カード・ステップノード列・マトリクス、表は列で読む必然があるページだけ）は `../html-slide-deck/references/design-system.md` に従う。文言は構成 md のとおりにし、組むときに言い換えない。

## 新しく作る（構成 md が正本）

1. **入力を確かめる。** 構成 md（必須）と図の PNG。`uv run <スキル>/scripts/outline.py --check <構成 md>` を通す。読めない行があれば、構成 md を直すか依頼者に聞く（黙って読み飛ばさない）。
2. **土台を決める。**
   - 前回の資料がある定例などは前回の最終版から始め、新しい資料はテンプレートから始める。
   - テンプレートはロゴあり（`continova`）・ロゴなし（`unbranded`）のどちらかを依頼者に聞く。リポジトリの規約に指定があればそれに従う。迷ったときはロゴなし。
   - 前回の資料は、制作記録・更新日時・ページ数で最新を確かめる。PowerPoint で開いているファイル（同じフォルダに `~$<名前>.pptx` がある）は読むだけにし、コピーから作る。
   - 前回の資料がテンプレートの系統でない（`01｜表紙` などのレイアウトが無い）ときは、`uv run <スキル>/scripts/template.py --inspect <pptx> --page <本文のあるページ>` で枠（題・リード文・ページ番号・罫線・フッター）の図形の名前を見て、`base = T.Base.from_deck(<pptx のパス>, page, title=…, lead=…, number=…, keep=(…))` で土台の設定を作り、`T.open_deck(<pptx のパス>, base=base)` で開く。測った本文の範囲・文字の大きさ・色が合わなければ引数で直す。
3. **型を決める。** 構成 md の図版指示を `references/type-map.md` に当て、ページごとの受け方（サンプル・レイアウト・写す）と部品を表にして依頼者に見せる。
4. **代表の 3〜4 枚を先に組む。** `references/example-build.py` を作業フォルダに写して `build.py` にし、代表のページだけ組む。題・リード文・フッターの位置、余白、強調色の量を画像で確かめてから全ページに広げる。
5. **全ページを組む。**
   - 文言は `outline.read()` で構成 md から読み、スクリプトに書き写さない。`build.py` に書くのは、どのページをどの部品で描くかだけ。
   - 箇条書きは 1 つのテキストボックス、帯・カードは 1 つの塗り矩形にする。
   - 図は PNG で貼る（SVG に頼らない）。図が無いときは `P.picture` が撮影前の枠を置く。
   - 最後に `T.finalize(prs, <出力>, title=<資料の題>)` で保存する。中身の無いプレースホルダー・使っていない画像・前の資料のページの題の一覧を外し、パッケージを確かめる。
6. **確かめる（組むたびに）。**
   - `uv run <スキル>/scripts/check_text.py <構成 md> <pptx>`：欠けた文言・別のページに入った文言・構成 md に無い文言（複製元の文言の残り）・重複を出す。フッターの資料名など構成 md に無い固定の文言は `--ignore` で外す。ページの対応が 1 対 1 でないときは `--map S1=1,S2=2,…`
   - `<スキル>/scripts/pptx_to_png.sh <pptx>` で全ページを画像にして見る。見る点は、型どおりか、はみ出し・重なり、1〜2 文字だけの折り返し・語の途中の折り返し、行頭の空白、同じ役割のページの位置のそろい。Read の表示は縮小されるので、文字が密な所は原寸で切り出して見る。
   - 3 回で収まらなければ残る差を添えて依頼者に聞く。型の読み違いに気づいたら最初から組み直す。
7. **渡す。** 残る差を並べ、PowerPoint か Keynote で見てもらう（LibreOffice の描画は PowerPoint と完全には一致しない）。置き場と名前はリポジトリの規約に従い、無ければ構成 md と同じフォルダに `<日付>_<題>_v1.pptx`。

## 版を上げる（依頼者が手直しした pptx が正本）

1. 依頼者が手直しした最新の pptx を元にする。構成 md から作り直して手直しを消さない。依頼者のコメントがあれば `T.comments(prs)` で読んで一覧にする。
2. 差し替える箇所（ページ・図形・新しい文言・表・図、ページの並べ替え・追加・再掲）を一覧にして依頼者に確かめる。
3. `references/example-revise.py` を写して、一覧の箇所だけを差し替える `build.py` を書く。版上げでは、差し替える文言をスクリプトか一覧のファイルに書いてよい。
   - 図形は `P.shape(s, <ID か名前か "text:文言の先頭">)` で取る。ID と名前は `template.py --inspect <pptx> --page N`
   - 文言は `P.replace_paras`（書式を保つ）、表は `P.set_cell`・`P.rebuild_table`（行・列の数が同じなら書式を保つ）、図は `P.replace_picture`
   - ページの複製は `T.duplicate`（ノート・コメントは持ち込まない。グラフは写す）、並べ替えは `T.keep_slides`、別の資料からの再掲は `T.import_slide`（大きさの異なる資料は比で換算する。グラフなど写せない関係を持つ図形は止まるので、画像にして貼るかを依頼者に聞く）
4. 差し替えの一覧の JSON を「旧の文言 → 新しい文言」で書き（形は `references/example-revise.py` の `changes`）、`uv run <スキル>/scripts/check_text.py --against <元の pptx> --changes <一覧.json> <新しい pptx>` で、元のページに差し替えを当てたものと新しいページの文言が一致することを確かめる（一覧に無い変更と差し替えの漏れの両方が出る）。画像とパッケージの確認は新しく作るときと同じ。
5. 最終版を保存したら、構成 md をその版に合わせる（deck-outline の決まり）。

## 置き場と外に出してよい範囲

出力の置き場、実名・実データの入る pptx をコミットしてよいか、外に出してよい範囲は、対象リポジトリの AGENTS.md / CLAUDE.md から読む。資料ごとの `build.py`・図・画像は、規約に置き場が無ければ pptx と同じ作業フォルダに置く。このスキルのフォルダには資料の中身を置かない。

案件リポジトリの規約に書かれている pptx の一般的な決まり（折り返しと行頭の点検、表の中の箇条書きを編集できる段落にする、左端の列のセルの結合など）は、手順 6 の見る点に足して使う。

## 別の Mac で使う

```bash
git clone https://github.com/Kyo1M/skills.git ~/Developer/Skills
~/Developer/Skills/scripts/link-skills.sh
brew install uv poppler
brew install --cask libreoffice google-chrome
~/Developer/Skills/deck-pptx/scripts/selftest.sh
```

書体はヒラギノ（Mac の標準）を前提にしている。Windows で開くときは、テーマの書体か「フォントの置換」で游明朝・游ゴシックに替え、改行を確かめる。

## 気をつけること

- python-pptx の `Slide` は取り出すたびに別のオブジェクトになる。`set_lead` の下端は内部でページごとに控えているので、`body_area(s)` は同じページに対して呼べば効く。
- `T.duplicate` は画像を元のページと共有し、グラフ・埋め込みは写す。別の資料から写すときは `T.import_slide` を使う（`duplicate` は同じ資料の中だけ）。
- 写したページの線（コネクタ）の接続先は振り直した図形の ID に合わせ、写さなかった図形への接続は外す。
- `T.finalize` はパッケージに問題があると止まる。止まったときはメッセージの部品を直す（無理に保存しない）。
- 外した図形を指すアニメーションが残ると PowerPoint が修復を求める。`T.finalize` はそのページのアニメーションを外して注意を出す。アニメーションを残したいページは、図形を外す前に依頼者に確かめる。`T.duplicate` はアニメーションを持ち込まない。
