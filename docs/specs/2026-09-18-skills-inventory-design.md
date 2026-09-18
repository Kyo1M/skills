# スキル棚卸し 設計書

- 日付: 2026-09-18
- ステータス: 承認済み（brainstorming で論点ごとに合意。実装は本設計書に基づき別作業で行う）
- 対象: Claude Code・Codex・claude.ai に散らばった自作スキルの置き場と配り方
- 対象外: `~/.claude/commands` の旧コマンド 3 件（agmsg、speed-commit、ui-skills）、continova-slides の slide-creation、pair-budget の第三者製 3 件、`~/.cursor/skills`・`~/.copilot/skills`、gog、議事録の情報管理の見直しとテンプレート回収（今後の候補）

## 1. 現状（2026-09-18 調査）

### 1.1 各ツールが読む場所

| ツール | 読む場所 | 根拠 |
|---|---|---|
| Claude Code | `~/.claude/skills`（personal）、リポジトリの `.claude/skills`（project）、プラグイン、claude.ai 同期分（`~/.claude/skills/synced/`、`anthropic-skills:<name>`） | 公式文書 code.claude.com/docs/en/skills |
| Claude Code の同名優先 | Enterprise > Personal > Project > Bundled。プラグインは `plugin:name` で名前空間が別、衝突しない | 同上、plugins ページ |
| claude.ai 同期 | claude.ai で無効化・削除すると Claude Code の synced からも消える | plugins-reference |
| Codex | `~/.agents/skills`、cwd から `.git` のある階層までの各 `.agents/skills`、`~/.codex/skills`（ソース内で deprecated）、リポジトリの `.codex/skills`、`.system`（同梱キャッシュ）、プラグイン | learn.chatgpt.com/docs/build-skills、openai/codex `codex-rs/ext/skills/src/host_roots.rs` |
| Codex の同名 | 統合せず両方並ぶ。`$name` 指定は Repo > User > System の先頭を取るが未公開の挙動 | 同上、`selection.rs` |
| Codex の symlink | フォルダの symlink を追従してスキャンする（公式に明記） | build-skills |

Claude Code が `.agents/skills` を読む記述は公式文書に無く、セッション記録にも `.agents` 由来の一覧は無い。

### 1.2 自作スキルの実体と重複

| 系統 | 場所 | 件数 | 問題 |
|---|---|---|---|
| 一般 | `~/Developer/Skills`（git、`~/.claude/skills` へ symlink） | 10 | Codex から見えない。html-slide-deck と meeting-minutes は claude.ai に古い同名版がある |
| 案件（vac-*） | `~/Developer/Skills/vac-*`（gitignore）。vaccinechoice_HH の `.claude/skills` から symlink、`.agents/skills` に実体コピー 4 件（git 管理）、`~/.claude/skills` に symlink 4 件 | 8 | 3 か所に散り、`.agents` のコピーは 07-03 で止まっている。07-03 設計書の「global に出さない」と矛盾 |
| 業務 | kyo1M-business の `.claude/skills` と `.agents/skills` に実体コピー | 9 + 1 | meeting-minutes（09-06 版）は Claude Code では global 版に隠れて動いていない。interview-prep-drafter は `~/.codex/skills` への symlink |
| Codex 専用 | `~/.codex/skills` | 2 | business-slide-writing・gemini-ja-proofread が git 外。前者は `~/.claude/skills/html-slide-deck/...` の絶対パスを参照 |
| claude.ai | 自作 7 件（`anthropic-skills:*`） | 7 | Claude Code からの起動 0 件。4 件はローカルと同名で中身が古い |
| 廃止・破損 | `~/.codex/skills` | 9 | 旧版 5 件（git 履歴に無い）、空ディレクトリ 1、壊れた symlink 4。vaccinechoice_HH の `.codex/skills` にも壊れた symlink 4 |

利用実績（直近 30 日、セッション記録から集計）: deck-outline 17、grill-me 15、meeting-minutes 23（うち DXB リポジトリ 15）、business-slide-writing 6、gemini-ja-proofread 4、vac-report-html 4、vac-report 3、deck-critique 3。業務スキル 9 件の Claude Code からの起動は 0、Codex では過去に使用あり。

## 2. 決定事項

### 2.1 正本は 2 系統

| 系統 | 正本 | 入るもの |
|---|---|---|
| Skills リポジトリ（`~/Developer/Skills`、GitHub Kyo1M/skills） | git 管理 | どのリポジトリでも使う自作スキル。一般 10 件に加え、Codex 専用の自作 2 件（business-slide-writing、gemini-ja-proofread）を移す |
| 各業務・案件リポジトリ | その repo | その repo の規約に依存するもの。kyo1M-business の業務 9 件 + interview-prep-drafter、vaccinechoice_HH の vac-* 8 件（git 管理しない、後述） |

Skills リポジトリに業務・案件スキルの実体を置かない。`~/.codex/skills` と claude.ai に自作の実体を置かない。

### 2.2 同名は 1 つの名前に 1 つの実装

- 同じ名前のスキルを複数の置き場に置かない。リポジトリごとの違いは、そのリポジトリの CLAUDE.md / AGENTS.md に書き、スキルが規約として読む。
- meeting-minutes は Skills の規約駆動版だけを残す。kyo1M-business の `.claude/skills/meeting-minutes` と `.agents/skills/meeting-minutes` は削除し、repo 版の方針は kyo1M-business の CLAUDE.md へ移す（2.6）。
- ツールごとの置き場（`~/.claude/skills`、`~/.agents/skills`）は Skills への symlink だけを置く。実体を置かない。

### 2.3 claude.ai の自作 7 件は無効化または削除

- brutal-advisor、hypothesis-map、meeting-minutes、html-slide-deck、note-writing-assistant、project-overview、kpi-structure をすべて claude.ai で無効化または削除する（村上さんが claude.ai の設定画面で行う）。
- ローカルに無い 3 件（note-writing-assistant、project-overview、kpi-structure）は削除前に `~/Developer/Skills/archive/claude-ai-skills/<name>/` に synced の中身をコピーして残す。
- `~/.claude/skills/synced/` は Claude Code が自動で片付けるので手で触らない。
- 将来 claude.ai や Chrome から使いたいスキルが出たら、Skills の正本を上げ直す。README の管理表に「claude.ai 専用」区分を設けて記録する（今回は 0 件）。

### 2.4 Codex への配り方

- 一般スキルと Codex 専用の自作は `~/.agents/skills/<name>` → `~/Developer/Skills/<name>` の symlink で配る。`~/.claude/skills` と同じ方式。
- `~/.codex/skills` には自作の実体を置かない。第三者製 `linear` は `~/.agents/skills/linear` へ移す。整理後の `~/.codex/skills` は `.system` だけになる。
- 業務スキル（kyo1M-business）は `.agents/skills/<name>` に実体、`.claude/skills/<name>` は `../../.agents/skills/<name>` への相対 symlink（git には symlink として登録）。理由: Codex は symlink 追従を公式に保証しており、Claude Code は実績のみ。
- 第三者製（find-skills、orca-cli、orchestration、agmsg）は `~/.agents/skills` に残す。agmsg は `VERSION`・`uninstall.sh` を持つ導入物として第三者製に分類する。

### 2.5 vac-* は vaccinechoice_HH 内のローカル管理（git 管理しない）

- 実体を `~/Developer/Skills/vac-*` から `~/Developer/vaccinechoice_HH/.agents/skills/vac-*` へ移す（8 件）。`.claude/skills/vac-*` は `../../.agents/skills/vac-*` への相対 symlink。
- どちらも git 管理しない。`.gitignore` の `.claude/skills/vac-*` を残し、`.agents/skills/vac-*` を足す。現在 git 管理されている `.agents/skills/vac-gdocs-report`・`vac-minutes`・`vac-nb`・`vac-report` は `git rm --cached` で追跡を外す。旧パスを書いたコメント行は書き換える。
- `~/.claude/skills/vac-*` の global symlink 4 本は削除する（07-03 設計書の方針に戻す。vac-* は vaccinechoice_HH を cwd にして使う）。
- vaccinechoice_HH の `spec-to-readable-html`（`.agents/skills` の実体コピーと `.claude/skills` の symlink）は削除する。Skills の正本が `~/.claude/skills` と `~/.agents/skills` から見えるため不要。
- vaccinechoice_HH の `.codex/skills`（壊れた symlink 4 本）は削除する。`.codex/` に他の中身は無いのでディレクトリごと消す。
- Skills リポジトリの `.gitignore` から `vac-*/` を消す。README の「project-private スキル」節は「案件スキルは各リポジトリで管理」に書き換える。
- 移動時に vaccinechoice_HH の CLAUDE.md の「`.claude/skills/` に登録済み」の記述を現状（`.agents/skills` に実体、`.claude/skills` は symlink、git 管理外）に合わせる。

### 2.6 meeting-minutes の軽量化

Skills の規約駆動版を改修する。設計原則（対象リポジトリの CLAUDE.md / AGENTS.md から規約を読んで動く）は変えない。

| 項目 | 現行 | 改修後 |
|---|---|---|
| 質問 | 2〜3 ラウンド、観点別の質問一覧 | 日付と人物を同定できないときだけ聞く。それ以外の不足は「要確認」として草案に残す。空欄を埋めるためだけの問答を増やさない |
| git | Step 1 ブランチ切替、Step 7 コミット確認、Step 8 push 提案 | 規約が議事録作成時のブランチ・コミット運用を定めているときだけ、その規約どおりに行う。定めが無ければ行わず、明示依頼のときだけ。DXB リポジトリは規約があるので従来どおり進む。kyo1M-business は「明示依頼のときだけ」なので止まる |
| 派生ファイル | 決定は decisions/、アクションは tasks/ や Issue へ派生を提案 | 派生先が規約にあり、かつ依頼の範囲に含まれるときだけ。既定は議事録内の「決定事項」「ネクストアクション」に留める。候補の一つ一つを ADR やタスクファイルにしない |
| 記録の作法 | 明示なし | repo 版の原則を取り込む: 会議日と作成日を分ける。発言者と観察者、本人の意思と他者の提案、合意と検討案、予定と実施を区別する。原メモに無い参加者・担当・期限・法的・金銭的結論を作らない。元メモや過去記録を黙って消さず、訂正は日付と根拠を付ける |
| 完了 | lint → コミット案 → push | frontmatter とリンクを検証し、規約の lint を実行し、議事録と重要な未確認事項を短く報告する |

`description` と冒頭の「旧 meeting-minutes-drafter は統合された」注記は残す。Step 0 の規約ディスカバリ、Step 4 の本文構成、contact プロファイルへのリンクは残す。

kyo1M-business の CLAUDE.md に「議事録の作り方」の箇条書きを足す（保存先 `notes/meetings/`、命名 `YYYY-MM-DD-<slug>`、`type: meeting`、参加者は `notes/contacts/` へリンク、決定は重大な方針変更だけ ADR、横断作業はボード・相手別進行は pipeline が正本で別のタスクファイルや Issue を作らない、git 操作は明示依頼のときだけ）。既存の「情報の正本と更新境界」と重複する項目は参照に留める。

### 2.7 廃止・破損の処理

| 対象 | 処理 |
|---|---|
| `~/.codex/skills/vac-minutes`・`vac-nb`・`vac-plan`・`vac-report`（壊れた symlink） | 削除 |
| `~/Developer/vaccinechoice_HH/.codex/`（壊れた symlink 4 本のみ） | ディレクトリごと削除 |
| `~/.codex/skills/codex-primary-runtime`（空） | 削除 |
| `~/.codex/skills/contact-profile-drafter`・`project-update-from-meetings`・`meeting-minutes-drafter`・`git-staged-commit-ja`（旧版、git 履歴に無い） | `~/Developer/_archive/2026-09-18-codex-skills/<name>/` へ移す |
| `~/.codex/skills/interview-prep-drafter` | 廃止でなく移設。kyo1M-business の `.agents/skills/interview-prep-drafter` に実体として移し、`.claude/skills/interview-prep-drafter` の symlink を `../../.agents/skills/interview-prep-drafter` に張り替える |
| `~/.codex/skills/linear`（第三者製） | `~/.agents/skills/linear` へ移す |
| `~/.codex/skills/business-slide-writing`・`gemini-ja-proofread` | `~/Developer/Skills/<name>` へ移し、`~/.agents/skills` と `~/.claude/skills` から symlink。business-slide-writing の `~/.claude/skills/html-slide-deck/references/automatic-slide-numbers.md` 参照は `../html-slide-deck/references/automatic-slide-numbers.md` に書き換える（Skills 直下でも symlink 先でも html-slide-deck が隣にある） |
| `~/.claude/skills/synced/` の自作 7 件 | 3 件を Skills の `archive/claude-ai-skills/` へコピーした後、claude.ai 側で無効化・削除（村上さん） |

削除は壊れた symlink と空ディレクトリだけ。中身のあるものは移動か退避にし、消さない。

### 2.8 再発防止

- **symlink スクリプト**: Skills リポジトリに `scripts/link-skills.sh` を置く。symlink を張る対象は README でなく Skills 直下のスキルディレクトリ（`SKILL.md` を持ち、`archive/`・`docs/`・`scripts/` を除く）とし、`~/.claude/skills/<name>` と `~/.agents/skills/<name>` の symlink を張る。既存の実体ディレクトリがあれば上書きせず報告する。`--check` で、壊れた symlink、Skills に無い symlink、`~/.claude/skills`・`~/.agents/skills`・cwd リポジトリの `.claude/skills`・`.agents/skills` にまたがる同名の重複、README 管理表に無いスキルディレクトリを報告する。
- **README の管理表**: 4 区分にする。(1) Skills 管理の自作（説明付き）、(2) リポジトリ管理の業務・案件（リポジトリ名と場所だけ）、(3) 第三者製（場所と出所だけ）、(4) claude.ai 専用（今回 0 件）。新規スキル追加手順は「Skills に作成 → `scripts/link-skills.sh` → README に追記」に改める。
- **グローバル CLAUDE.md（`~/.claude/CLAUDE.md`「開発環境」節）**: 次の 3 行を書き換える。「`~/.claude/skills/` に symlink 配置」を「`~/.claude/skills/` と `~/.agents/skills/` に symlink 配置（`scripts/link-skills.sh`）」に。「新規 skill は …」をスクリプト経由の手順に。「同じ名前のスキルは 1 実装。リポジトリごとの違いはそのリポジトリの CLAUDE.md / AGENTS.md に書く。業務・案件スキルはそのリポジトリの `.agents/skills` に実体、`.claude/skills` は symlink」を足す。
- **kyo1M-business の CLAUDE.md**: 「`.agents/skills/` と `.claude/skills/` の同名スキルは参照資料も含めて同じ内容を維持する。このリポジトリの meeting-minutes も両方に配置する」を「業務スキルは `.agents/skills/` に実体、`.claude/skills/` は同名の symlink。meeting-minutes は Skills の共通版を使い、このリポジトリの方針は本ファイルの『議事録の作り方』に書く」に改める。利用可能なスキル表の meeting-minutes 行は説明を共通版に合わせる。
- **定期点検**: 月初の weekly-review の前に `scripts/link-skills.sh --check` を 1 回走らせる。weekly-review スキルには手を入れず、グローバル CLAUDE.md の手順に 1 行足す。
- **記憶メモ**: `skills-topology.md` を本設計の内容に書き換える（Codex は symlink 追従可、`~/.agents/skills` を読む、同名 1 実装）。

### 2.9 Skills リポジトリの衛生

- 作業ブランチ `chore/20260703-env-overhaul`（main より 20 コミット先行、13 コミット未 push）を push し、main へマージする。棚卸しの変更はその後の新ブランチで行う。
- deck-outline と html-slide-deck の未コミット変更は、棚卸しの変更と混ぜず、先に別コミットにする（内容の確認は村上さん）。
- 本設計書は `docs/specs/` に置く。

## 3. 実行後の配置

```
~/Developer/Skills/                    正本（git）
├── <一般 10 件>/
├── business-slide-writing/            ← ~/.codex/skills から
├── gemini-ja-proofread/               ← ~/.codex/skills から
├── archive/claude-ai-skills/          ← claude.ai の 3 件を退避
├── docs/specs/
└── scripts/link-skills.sh

~/.claude/skills/<name>  → ~/Developer/Skills/<name>   （12 本。vac-* は無し。gog と synced/ はそのまま）
~/.agents/skills/<name>  → ~/Developer/Skills/<name>   （12 本）+ 第三者製 5 件（agmsg, find-skills, orca-cli, orchestration, linear）
~/.codex/skills/                        .system だけ

~/Developer/kyo1M-business/
├── .agents/skills/<業務 9 件 + interview-prep-drafter>/   実体（git）。meeting-minutes は無し
└── .claude/skills/<同名>  → ../../.agents/skills/<同名>   symlink（git）

~/Developer/vaccinechoice_HH/
├── .agents/skills/vac-* (8 件)          実体（git 管理外）
└── .claude/skills/vac-*  → ../../.agents/skills/vac-*    symlink（git 管理外）
```

## 4. 実行順と確認

1. Skills の衛生（2.9）: 未コミット変更の切り離し → ブランチ push → main マージ → 棚卸し用ブランチ作成。
2. Skills 側: business-slide-writing・gemini-ja-proofread の移設、`scripts/link-skills.sh` 作成、`.gitignore` と README の更新、meeting-minutes の改修、設計書のコミット。
3. symlink の張り直し（`~/.claude/skills`、`~/.agents/skills`）と `~/.codex/skills` の整理（2.7）。
4. kyo1M-business: meeting-minutes 削除、interview-prep-drafter 移設、`.claude/skills` の symlink 化、CLAUDE.md 更新、lint。コミットは村上さんの依頼時（同リポジトリの規約）。
5. vaccinechoice_HH: vac-* の移設、git 追跡の解除、`.gitignore`・CLAUDE.md の更新、`.codex/` と spec-to-readable-html の削除。コミットは村上さんの確認後。
6. グローバル CLAUDE.md と記憶メモの更新。
7. 村上さんが claude.ai で 7 件を無効化・削除（退避コピーの完了後）。
8. Claude Code と Codex を再起動し、`scripts/link-skills.sh --check` で重複ゼロ・壊れリンクゼロを確認。kyo1M-business で `/meeting-minutes` の説明が共通版になっていることを確認。

各ステップは独立しており、途中で止めても既存の動作は壊れない（symlink の張り直しは実体を動かした直後に行う）。

## 5. 今回やらない（今後の候補）

- 議事録の情報管理の見直しとテンプレートの回収（村上さんの意向。meeting-minutes の改修が先）。
- `~/.claude/commands` の旧コマンド 3 件の整理。
- continova-slides の slide-creation、pair-budget の第三者製 3 件、`~/.cursor/skills`・`~/.copilot/skills` の整理。
- daily-log の launchd plist の移植性。
- 07-03 設計書の「今回やらない」に残る項目（status 語彙の統一、AGENTS.md 共通部分のテンプレ抽出）。
