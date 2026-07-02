# Claude 環境総点検・改善 設計ドキュメント

- 日付: 2026-07-03
- ステータス: 承認済み(セクション別に承認、同日実行)
- 背景: memory / skills の棚卸しを 3 方面調査(skills 全体・memory 全 73 件・主要 7 リポジトリの利用実態)で実施した結果に基づく改善設計。

## 診断サマリー

1. **memory の孤児化(最重要)**: 2026-06-06 のリポジトリ移転(`~/Documents/Develop/*` → `~/Developer/*`)で、旧パスに紐づく memory 約 30 件が自動ロードされない状態になっていた。事業戦略・DXB 文脈・ワクチン分析の作法 feedback など土台の文脈が取り残され、新旧で正面矛盾も 2 件(commit 確認ポリシー、DXB 顧客名ポリシー)。
2. **批判的壁打ちの道具が実質不在**: grill-me は 10 行のみ。superpowers:brainstorming は設計向けで論点整理・ヌケモレ指摘の観点がない。
3. **資料作成の知見が分散**: 書き方原則 11 点が dxb プロジェクトの memory に閉じており、推敲・批評の独立工程が無い。ユーザーのアイデアメモが黙って省略される構造的原因は、トレーサビリティ表の対象が「フィードバック・決定事項・要件」でメモを含まないこと。
4. **skills 管理の綻び**: README の実体パスが旧パスのまま、自作 4 skill が git 管理外、spec-to-readable-html の物理コピー、vac-report-html のグローバル露出矛盾。
5. **ワクチン分析は成熟**: AGENTS.md 5 原則と vac-* skill が 1:1 対応。改善余地は 3 系統ミラーの手動同期と旧 feedback の復活。

## 決定事項

### 3 層の置き場所ルール

| 層 | 置くもの |
|---|---|
| グローバル(`~/.claude/CLAUDE.md`) | どのプロジェクトでも効く事実・原則(書き方原則 11 点の要約、gh アカウント機構、skills 配置、自走ポリシー、Linear 運用) |
| スキル(`~/Developer/Skills` に一元管理) | 明示起動する行動プロセス(壁打ち・deck 作成・批評) |
| プロジェクト(per-project memory) | そのプロジェクト固有の事実のみ |

- 批判的壁打ちは常時オンにせず**明示起動**(/grill-me、/brainstorming)で効かせる(会話のテンポ優先、ユーザー決定)。
- 書き方原則の正本は `deck-outline/references/writing-principles.md`(git 管理)。グローバル CLAUDE.md には要約 11 行を常設。新 FB は両方に反映。
- 昇格済み memory は元の場所から削除し二重管理を防ぐ。

### memory 整理

- 移設: 旧 kyo1M 6 本 / 旧 vaccinechoice 12 本 / DXB 文脈の AGENTS.md 未収載差分 / 旧 pair-budget(accounting-model + refactor-roadmap 縮約版)/ 旧 continova-slides 1 本 / user_tax_network(→ kyo1M)。frontmatter は現行形式に正規化。
- 削除 7 件(承認済み): confirm-commit-pr-messages / project_dxb_confidentiality / redact-dxb-client-names / analysis-project-template-location / slide-deck-no-codex-images + slide-illustrations-svg-over-ai(skill へ本文化の上)/ income-delete-bug-rootcause / project_freelance_transition。
- 更新 1 件: mahjong-trainer-followups(PR 実状態を確認しブランチ状態の段落のみ書き直し)。
- 再発防止: 「リポジトリを移動したら memory ディレクトリも移設」をグローバル CLAUDE.md に明記。

### skills 整理

- README 修正(実体パス `~/Developer/Skills/`、管理表を全 skill に更新)。
- orphan 4 skill(empirical-prompt-tuning / continova-business-card / daily-log / grill-me)をリポジトリへ移管し symlink 化。gog は第三者製のため管理外のまま(README に記録)。
- vaccinechoice の spec-to-readable-html 物理コピーを symlink 方式に統一(git 管理状況を確認の上)。
- vac-report-html のグローバル symlink を解除し project-only に統一。
- git 衛生: package-lock 差分のコミット、`__pycache__` 削除。

### skill 改修・新設

- **grill-me 刷新**: 2 モード構成。①アイデア壁打ち(前提を疑う→論点ツリー md 可視化→ヌケモレ・反証・根拠の指摘→終了時に論点整理 md を規約駆動で保存)②プラン精査(現行の決定木 grilling + ADR 等との矛盾照合)。質問は 1 問ずつ・推奨付き。
- **deck-critique 新設**: 構成 md / 完成 HTML を入力に批評専用。狙い一文の逆算抽出→ストーリー一貫性、タイトル・リード・ボディの自然さ(原則 7 全チェック)、1 ページ 1 決定、元素材との脱落突合。出力は重要度順の指摘リスト+修正案(勝手に直さない)。可能ならサブエージェント(新しいコンテキスト)で実行。
- **deck-outline 改修**: Phase 1 に「アイデアメモの番号付きインベントリ化」、Phase 5 に「全項目の反映先突合+落とす項目の明示承認」を追加。
- **html-slide-deck 追記**: 挿絵ポリシー(手書き SVG 優先、Pattern 11/12 の AI 生成画像不使用)の本文化、実装後セルフレビューに構成 md からの脱落チェックを追加。

### ワクチン分析(ライトタッチ)

- 旧 feedback 12 本の復活(移設で対応)。
- skill ミラー: 実体を `~/Developer/Skills` の vac-* に一本化し、gitignore 済みなら symlink・git tracked なら同期スクリプトで再生成(共同研究者への影響を実行時に確認)。
- vac-nb 冒頭に「問い・仮説・反証可能性・先行結果との整合」の軽量チェック(3〜5 問)。本格的な論点整理は grill-me を使う旨を AGENTS.md に 1 行追記。vac-report に「考察の深さ」(解釈・限界・次の問い)のチェック項目を追加。

## 今回やらない(今後の候補)

- status 語彙の統一(現状リポジトリ間で 2〜6 値が混在)、AGENTS.md 共通部分のテンプレ抽出
- kyo1M-business の「updated 自動更新 hook」の他リポジトリ横展開
- 議事録 3 実装(meeting-minutes / vac-minutes / Copilot プロンプト)の統合
- empirical-prompt-tuning による新 skill(grill-me / deck-critique)の実戦検証サイクル(数回使ったら両面評価で改善)

## 実行順

memory 整理 → グローバル CLAUDE.md → skills 構造整理 → skill 改修・新設 → vac。各ステップは独立しており途中で止めても壊れない。
