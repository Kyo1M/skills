---
name: html-slide-deck
description: ビジネス・コンサル向けの定例・提案・議論・報告用スライドを「事業用スライド デザインシステム（白地・明朝タイトル・Klein Blue シグナル、1920×1080）」で `.dc.html`（deck-stage 形式・Claude Design 互換）として作成するスキル。「スライドを作りたい」「資料化したい」「定例・部会の資料を」「構成 md を HTML 化して」「提案資料を」「議論用の資料を」などのリクエスト時に使用。deck-outline の構成 md を入力に、型を選び、アイコンと構造で受け止め、構成 md の中身を落とさずに実装し、機械チェックとセルフレビューを通して出力する。pptx 化は生成した `.dc.html` を Claude Design に持ち込んで行う。
---

# HTML Slide Deck（v2・事業用スライド DS）

ビジネス向けの議論用・提案用スライドを、Claude Design と同じ **`.dc.html`（deck-stage 形式・1920×1080）** で作成する。デザインシステムとルールの正本は `references/design-system.md`。構成（何を載せるか）は `deck-outline` skill の構成 md が担い、本 skill は **型の選択 → 実装 → 検証** を担う。

## このスキルが解決する課題

- 文字ばかりのスライドにならないよう、型（表・進行表・ステップ・カード列）とアイコンで構造を立てる
- 構成 md の中身を「読みやすさのため」に削らない（脱落チェックを必須にする）
- ルールを 1 箇所（`design-system.md`）に置き、Claude Design 側の制作ルールもそこから派生させる
- 機械チェック（はみ出し・フォント下限・禁止表記・発表者ノート・アイコン密度）で提示前に潰す
- 生成した `.dc.html` をそのまま Claude Design に持ち込んで pptx 化できる

## 初稿で適用する文章ルール

日本語の業務スライドは、構成・実文言を書き始める前に `~/.codex/skills/business-slide-writing/references/principles.md` を読む。共有する対象と相談事項を先に定め、概要には利用状況・機能・作業を載せる。管理履歴を機械的に転載せず、指定された内容・必要な制約は維持する。表や役割欄は対象と作業が分かる自然な名詞句を使える。共通ルールは文章と情報選択に適用し、過去の担当・日程・状態を引き継ぐ根拠にしない。

## ワークフロー

```
Phase 1-2: 構成（問い・全体構成・実文言）   ← deck-outline skill が担う。構成 md が入力
   ↓
Phase 3: 型の選択（references/slide-patterns.md）
   ↓
Phase 4: .dc.html 実装（assets/template.dc.html を複製して差し替え）＋ 機械チェック
   ↓
Phase 5: セルフレビュー（references/self-review-checklist.md）→ 提示
   ↓
（必要なら）Claude Design に持ち込んで pptx 化
```

**構成 md が無いまま HTML に入らない。** 無ければ先に `deck-outline` で構成を固めてレビューを通す（Phase 1-2 の最低限は下の「フォールバック」に残す）。**Phase 5 を飛ばさない。** HTML を書き終わった瞬間に提示せず、必ず機械チェックとチェックリストを通す。

---

## Phase 1-2（フォールバック）: 構成 md が無いときの最低限

`deck-outline` が使えない／ごく簡易な資料のときだけ、以下を決めてから Phase 3 へ。

- 誰のための資料か、何を決める場か、答える問い・答えない問い、枚数の目安（議論用 8〜10、報告用 12〜15）
- **議論駆動デッキかどうか**: 定例・部会・レビュー会など「その場で決める／合意する」資料は議論駆動デッキ。全ページに役割バッジ（報告／確認／議論／参考／再掲）を付け、【議論】は 1 論点 1 枚、網羅情報は【参考】として付録へ、議論の手前に【再掲】の全体像 1 枚、まとめに次回までの動き（＋その場で答えが返る「お伺いしたいこと」）。
- 各スライドの 1 メッセージ、タイトル（副題なしの名詞句）、リード文（結論＋判断理由・結果 1〜3 行。**表紙には置かない**）、ボディの実文言、型、見出し帯カードを使うならアイコンの概念名
- 既定は方針＝たたきの直接提示。選択肢の並列比較は明示依頼のときだけ
- 定例の表紙は定例名そのもの。リード文に本日ご相談することを 1〜2 文、下に本日の流れ

---

## Phase 3: 型の選択

構成 md の各スライドの「図版指示」に書かれた **型の名前** と **アイコンの概念名** に従う。書かれていなければ `references/slide-patterns.md` §0 の早見表で選ぶ。

まず `design-system.md` §4「骨格と詳細」で描き方を決める。**1 枚の骨格（流れ・対比・階層・並列の論点）は図（ステップ列・見出し帯カード・2 分割）で受け、その中身は箇条書きで書く。** 全部を箇条書きにするとコンサルの資料にならず、全部を箱に入れると読めない。**表は列で読む必然があるとき（比較・進行表・突合・ガント）だけ。**

- 20 型: 表紙／目次／自己紹介／章扉／現状と目指す姿／提供価値 3 軸／比較表／4 ステップ／推進体制／スケジュール（月帯）／ガント（タスク×週）／KPI／ロードマップ／振り返り／確認事項／議論／まとめ／付録 早見表／お問い合わせ／**進行表**（仕組み／利用の 2 段）／**流用枠**（前回資料のページ差し替え）
- 文字だけの枚（箇条書きだけの軽い共有、論点を絞った議論）も可。骨格が言える枚は図で受ける
- 選び方の指針:
  - 案件ごとの現在地 → 進行表（定例で更新し続ける）。前回の振り返り／今週実施したこと → 振り返り（左右 2 カラムの箇条書き・時間の欄なし）
  - 前回資料から流用できる枚（目的・コンセプト・全体像）→ 作り直さず流用枠（部品 L）に元 pptx のファイル名・ページ番号・見出しを書く
  - 手順・段階 → 4 ステップ（横）か縦フロー。3〜4 本の柱 → 提供価値 3 軸（アイコン付き）
  - 週単位の実績・予定 → ガント（1 枚に統合・実施済み ✓）。月単位 → スケジュール（月帯）
  - 1 論点の相談 → 議論（方針＝たたきを直接提示。比較は依頼時のみ）
  - 上のどれでもない → 箇条書き型（部品 A）
- アイコンは **見出し帯カード（部品 B）の見出しだけ**（章扉の章名も可）。箇条書き・番号付きリスト・表の行・ガントのトラック名・工程ノード・表紙の流れ・目次には付けない。1 枚 0〜4 個で、0 個の枚があってよい。概念は `references/icons.md` の対応表で 1:1 に固定し、無い概念は登録してから使う

---

## Phase 4: 実装

### 手順

1. `assets/template.dc.html` を出力先にコピーして `yyyymmdd_<slug>.dc.html` にする（ゼロから組まない）。先頭に frontmatter の HTML コメントを置く（project-context-template の規約。下記）。
2. 使わない `<section>` を削り、使う型の `<section>` を複製して順に並べる。`data-label`（スライド名）と `data-screen-label`（連番）を振る。**`data-speaker-notes` は付けない。**
3. 各 `<section>` の中身を構成 md の実文言で差し替える。**ボディ項目を落とさない**。箇条書きは 1 テキストボックス（1 div に `<br>` 区切り）。見出しが要る箇条書きは「太字見出し行＋本文」か「見出し：本文」。`──` を使わない。
4. アイコンは `<svg width="32" height="32" style="color:#2F3135"><use href="#ic-…"/></svg>`。スプライト（`<defs>`）はテンプレートに全種入っている。使わなかった `<symbol>` は残してよい。
5. footer の `<span data-footer-title>` に資料名、`<span data-page>` はそのまま（runtime が振り直す）。役割バッジを右上に。 **フッターに作成日は表示しない。**
6. スタイルは inline のまま（class 依存にしない。PPTX 化は inline を解決する）。
7. runtime（`support.js`・`deck-stage.js`）を出力ディレクトリに同名で置く（`assets/runtime/` からコピー。repo では `docs/deliverables/` 直下に 1 組だけ置き git 管理）。
8. 機械チェック:
   ```bash
   node <skill-dir>/assets/check-slides.mjs <path/to/deck.dc.html> [--shots <dir>]
   ```
   FAIL（はみ出し／内側クリップ／フォント下限／`──`／`data-speaker-notes`）がゼロになるまで直す。WARN（アイコン 7 個以上・塗りボックス 4 個以上・絵文字）は理由を言えるときだけ残す。
9. ローカル表示: `file://` では runtime の fetch が失敗するので http 経由で開く。
   ```bash
   (cd <出力ディレクトリ> && python3 -m http.server 8765) ; open http://localhost:8765/<file>.dc.html
   ```
   runtime は React/Babel を unpkg から読むため、表示・チェックにはネットワークが要る。

### 出力契約（`.dc.html` の構造）

テンプレートと同じ並びを保つ: `<script src="./support.js">` → `<x-dc>` → `<helmet>`（Google Fonts・最小 style）→ アイコンスプライト `<svg><defs><symbol id="ic-…">` → `<x-import component-from-global-scope="deck-stage" from="./deck-stage.js" width="1920" height="1080" hint-size="100%,100%">` → `<section data-label data-screen-label style>` × N → `</x-import></x-dc>` → `<script type="text/x-dc" data-dc-script>`（ページ番号・資料名の振り直し）。footer の `data-footer-title` / `data-page` は必ず残す。`data-deck-skip` は付録区切り等に使ってよい。

### PowerPoint の自動ページ番号

PPTX を出力・再掲する際は [automatic-slide-numbers.md](references/automatic-slide-numbers.md) を読む。HTML の `[data-page]` に加えて、PPTX は標準のスライド番号フィールドを使う。固定テキストのまま渡さず、最終エクスポート後にも保持を確認する。

### HTML タグ開閉の検証（任意）

```bash
python3 - <<'PY'
from html.parser import HTMLParser
class V(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]; self.errors=[]
        self.void={'br','hr','img','input','meta','link','rect','line','circle','path','polygon','text','use','marker','stop','polyline','ellipse'}
    def handle_starttag(self,t,a):
        if t not in self.void: self.stack.append(t)
    def handle_endtag(self,t):
        if t in self.void: return
        if not self.stack: self.errors.append(f'unmatched </{t}>')
        elif self.stack[-1]!=t: self.errors.append(f'mismatch <{self.stack[-1]}>/</{t}>')
        else: self.stack.pop()
v=V(); v.feed(open('FILENAME.dc.html',encoding='utf-8').read())
print('errors:',v.errors[:5] or 'none'); print('unclosed:',v.stack or 'none')
PY
```

---

## Phase 5: セルフレビュー

`references/self-review-checklist.md` を通読しながら点検し、1 項目でも該当があれば修正してから提示する。特に:

1. **構成 md からの脱落**（各スライド・各ボディ項目・数値・固有名詞。間引いた箇所は「構成 md からの変更点」として提示文に列挙）
2. 1 枚 1 テーマ／リード文 1〜3 行／タイトルは副題なしの名詞句
3. `──`・`data-speaker-notes`・絵文字ゼロ
4. アイコンの置き場所・量・概念 1:1
5. 文字量の目安超過と分割の判断／はみ出し・フォント下限
6. 面・色（塗りボックス 2〜3 個・Klein Blue は要所だけ）
7. 構成・章間整合・表記揺れ・役割バッジ・footer
8. 読者配慮・自己完結（内部パス・内情・相手側の宿題を書かない）
9. 画像枠・スクショ枠（報告ページの実物。`assets/` にあれば埋め込み、無ければ指示文）・プレースホルダ数値・PPTX 手直しの作り

提示文には、構成 md からの変更点、機械チェックの結果（FAIL 0・WARN の理由）、ローカル表示のコマンド、Claude Design への持ち込み手順を添える。

---

## Claude Design への持ち込み（pptx 化）

pptx が必要なときは、生成した `.dc.html`（runtime 2 本と同じディレクトリに置いた状態）を Claude Design の該当プロジェクトに持ち込み、Claude Design 側で pptx 出力する。Claude Design 側の制作ルール（プロジェクトの `CLAUDE.md`）は `references/claude-design-rules.md` の内容に揃える（正本を変えたら貼り直す）。持ち込みが通らない場合は、構成 md を Claude Design に渡して生成する従来運用に戻す（この場合も Claude Design の `CLAUDE.md` が正本と揃っていれば同じルールで出る）。

---

## デザインシステム概要（詳細は `references/design-system.md`）

- **最終成果物は pptx を作り手が手で仕上げたもの。** HTML 側で作り込むほど手直しが重くなる。凝った作りより直しやすい作りを選ぶ
- 1920×1080。地は白 `#FFFFFF`（オフホワイト版 `#F6F5F2`）、本文 `#2F3135`、タイトル `#111111`、注釈 `#6F7175`、罫線 `#D8D6D0`、淡ベージュ `#F4F2EE`、Klein Blue `#002FA7`（推奨・本命・キー数値・現在地・強調語句のみ、面積 5〜12%）、淡ブルー `#EAF1FF`
- タイトル＝明朝 64px、リード文 36px（28〜38）、本文 28px（26〜30・**最低 24**）、補助 24px（最低 22）、kicker・STEP のみ 18〜20 可
- 本文スライドは `padding:56px 96px 104px`＋天地中央寄せ。footer・バッジは absolute
- 脱ボックス（塗りは区切る意味があるものだけ・1 枚 2〜3 個）、グラデ・影・角丸なし、画像は破線枠＋指示文（報告ページの実物スクショは `assets/` にあれば `<img>` で埋め込み、キャプション 1 行を添える）
- PPTX 手直し前提: 箇条書きは 1 テキストボックス、帯・カードは 1 つの塗り矩形、ガントは全体を 1 つの grid で組む（行ごとの flex ＋入れ子 grid にしない）

---

## project-context-template での使用

[`project-context-template`](https://github.com/Kyo1M/project-context-template) 規約のリポジトリ（cwd の `AGENTS.md` で判定）では:

- 出力: `docs/deliverables/yyyymmdd_<slug>.dc.html`（スラグは ASCII kebab-case）。runtime `support.js`・`deck-stage.js` は `docs/deliverables/` 直下に 1 組（無ければ `assets/runtime/` からコピーしてコミット）
- frontmatter（ファイル先頭の HTML コメント。`<!DOCTYPE html>` の前）:
  ```html
  <!--
  ---
  type: deliverable
  title: <日本語タイトル>
  date: YYYY-MM-DD
  status: active
  topics: [<関連 topic>]
  tags: []
  derived_from: [docs/explorations/<構成 md>, docs/minutes/...]
  related: []
  audience: client | internal | exec | team
  format: slide
  source_prompt: <生成プロンプトの要約>
  ---
  -->
  ```
- Git: `AGENTS.md` の運用ルールに従う（`deliverable/<yyyymmdd>-<slug>` ブランチ、frontmatter/ファイル名を変えたら `npm run lint:changed --prefix scripts`、コミットメッセージ案 → 確認 → commit → push 提案）
- 改訂版は diff 編集でなく別ファイル `yyyymmdd_<slug>-vN.dc.html` として再生成。最新版と提示版は直下に残し、中間版は `_old/` へ `status: superseded` で移動。`llms.txt`・トピックハブの掲載を更新し、リンク切れを残さない
- 最終提示した pptx は `docs/deliverables/pptx/`（git 管理外）に原名のまま置き、構成 md の `related:` に追記する

---

## 留意事項

### 資料の自己完結性
議事録・タスク・decision のパス、社内 URL、内部運用メモを本文に書かない。派生関係は frontmatter `derived_from` / `related` で表す。後から開く人・社内パスにアクセスできない人・印刷で見る人が単体で読み切れること。

### 読者配慮
説明対象のメンバー本人も読む前提で、評価的・批判的に響く表現を避け、提供する支援と段取りのトーンで書く。案件間の優劣に読める比較を出さない。相手側の宿題・固有の約束・未確定の担当者名や期日を書かない。pptx をクライアントに渡すため、内情（守りの理屈・社内事情）はデッキに残さず構成 md の設計判断節に置く。

### やるべきこと
- 構成 md を入力に Phase 3 から始める。構成 md が無ければ先に deck-outline
- 定例・部会の資料は議論駆動デッキ（役割バッジ・1 論点 1 枚・【参考】は付録・【再掲】の全体像）
- 各枚の型とアイコンを決めてから書く。アイコンは対応表で 1:1
- 構成 md の項目を落とさない。間引いたら変更点として明示する
- 機械チェック → セルフレビュー → 提示。提示文に変更点・チェック結果・表示コマンド・持ち込み手順
- 新しく決めた方針は `references/design-system.md` に追記し、`claude-design-rules.md` を作り直す

### やってはいけないこと
- 構成 md なしで HTML に直行する／ゼロからテンプレートを組む
- 「太字キーワード ── 短い説明」の 1 行圧縮、`──`・`―` の使用、タイトルの副題、「〜を、〜に。」構文、動詞締めのタイトル／表紙にリード文を置く
- 骨格（流れ・対比・並列の論点）を箇条書きに潰す／列で読む必然がないものを表にする／前回資料から流用できる枚を作り直す
- ガントを行ごとの flex ＋入れ子 grid で組む（月・週・帯の縦線がずれる）
- `data-speaker-notes` を付ける（発表者ノートは使わない）
- 見出し帯カードの見出し以外にアイコンを付ける（箇条書き・番号・表の行・トラック名・工程ノード・表紙の流れ・目次）／1 枚に 5 個以上／同じ概念に別のアイコン／絵文字・アイコンフォント
- フォントを 24px 未満に落として詰め込む／はみ出し・クリップを残す
- 塗りボックスを並べる（1 枚 4 個以上）、青ベタ広面、グラデ・影・角丸カード
- 画像を生成する（破線枠＋指示文にする）／数値を本物のように見せる（プレースホルダに）
- 議事録・内部パス・内部運用メモ・相手側の宿題を本文に書く
- 依頼されていないのに選択肢を並べて比較させる／【議論】に網羅情報を詰める／毎ページに「決めたいこと」欄を置く
- 締めのスライドで合意済みの事項を論点として並べる
- HTML を書き終わった瞬間に提示する（Phase 5 を飛ばす）

---

## 参照ファイル

- `references/design-system.md`: ルールの正本（トークン・レイアウト・脱ボックス・アイコン・文章・構成・PPTX 手直し・禁止事項）
- `references/slide-patterns.md`: 20 型とボディ部品（構造・スニペット・見本 PNG）
- `references/icons.md`: アイコンの対応表・置き方・外部生成の指示書・取り込み手順
- `references/self-review-checklist.md`: Phase 5 の観点
- `references/claude-design-rules.md`: Claude Design の `CLAUDE.md` に貼る制作ルール
- `references/previews/*.png`: 型・部品のデザインイメージ（`node assets/render-previews.mjs` で再生成）
- `references/legacy/continova-v1/`: 旧 DS（1672×941・スクロール形式）の退避
- `assets/template.dc.html`: 20 型のベーステンプレート（複製して使う）
- `assets/runtime/`: `support.js`・`deck-stage.js`（ローカル表示用 runtime。出力先にもコピー）
- `assets/tokens/`: `colors.css`・`typography.css`・`spacing.css`
- `assets/icons/`: 個別 SVG と `sprite.svg`
- `assets/check-slides.mjs`: 機械チェック（`--shots` で各枚 PNG）
- `assets/render-previews.mjs`: 見本 PNG の再生成
- `assets/previews-src/`: 見本の元 HTML（slides/ と guidelines/）
