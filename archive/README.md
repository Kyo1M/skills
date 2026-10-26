# archive

使わなくなった skill の退避先。`scripts/link-skills.sh` はこの `archive/` を symlink の対象にしない。戻すときは `git mv archive/<name> <name>` して `scripts/link-skills.sh` を走らせ、README の管理表に戻す。

| skill | 退避日 | 理由 |
|---|---|---|
| business-slide-writing | 2026-10-26 | 文章ルール（`references/principles.md`）が書き方原則の正本と別の言い回しで重なっていた。正本に無い規則は正本へ移し、要約は `deck-outline/references/principles-digest.md`、最終版から学ぶ手順は deck-outline に移した |
| brutal-advisor | 2026-10-26 | grill-me の一度で評価モードにまとめた。直近 30 日の呼び出しが Claude Code・Codex とも 0 回 |
| gemini-ja-proofread | 2026-10-26 | 直近 30 日の呼び出しが Claude Code・Codex とも 0 回。共通ルール（`references/preferences.md`）は書き方原則 7 の写し |
| doc-maintenance | 2026-10-07 | 点検をスクリプト中心で作ったが、skill・プロンプトとして作り直す方針になった。作り直すまで退避（点検の観点・設定の例は scripts/・references/ に残る） |
| spec-to-readable-html | 2026-09-29 | 直近 30 日の呼び出しが Claude Code・Codex とも 0 回。使い続けている案件リポジトリの `.agents/skills/` に写しがあり、そちらが正本（2026-10-26 にこの控えの新しい差分をそちらへ移した） |
| empirical-prompt-tuning | 2026-09-29 | 直近 30 日の呼び出しが Claude Code・Codex とも 0 回。skill の評価と改善は skill-creator でも回せる |
| claude-ai-skills/（note-writing-assistant、project-overview、kpi-structure） | 2026-09-18 | claude.ai にだけあった自作 skill の控え。claude.ai 側は 2026-09-29 に無効化済み |
