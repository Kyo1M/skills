# 画像生成（codex CLI）

記事に挿入する画像を codex CLI のネイティブ画像生成で作り、記事フォルダ内の `assets/` に配置する。

## 仕組み

- codex には組み込みの画像生成（`imagegen` システムスキル / `image_gen` ツール）がある。`OPENAI_API_KEY` 不要、ChatGPT サブスクのログインで動く。
- codex は生成画像を `~/.codex/generated_images/<session-id>/ig_*.png` に保存する（実測 1672×941、約 16:9）。
- `codex exec` は信頼ディレクトリ（git リポジトリ）内から、または `--skip-git-repo-check` 付きで実行する必要がある。

## 手順

記事 1 枚ごとに次を行う。`writing-articles` リポジトリ内で実行すること。

1. 画像の挿入位置と図解パターンを決める（`image-prompts.md` の 10 種）。
2. 日本語の画像生成プロンプトを組み立てる。
3. codex に画像生成 → 記事フォルダ内の `assets/` への保存まで依頼する。codex は `--sandbox workspace-write` でリポジトリ内に書き込める。

```bash
codex exec --skip-git-repo-check --sandbox workspace-write \
  "画像を1枚生成してください。
  【プロンプト】
  <image-prompts.md のパターンに沿った日本語プロンプト>

  生成できたら、その画像を articles/<yyyymmdd>_<slug>/assets/<NN>-<desc>.png にコピーしてください。
  最後の行に、コピー先の相対パスだけを出力してください。" < /dev/null
```

4. `articles/<yyyymmdd>_<slug>/assets/<NN>-<desc>.png` が出来たことを確認する。
5. 記事本文の挿入位置に Markdown 画像を入れる:

   ```markdown
   ![<alt テキスト>](assets/<NN>-<desc>.png)
   ```

   `article.md` と `assets/` は同じ記事フォルダ内にあるため、相対パスは `assets/...`。公開時にフォルダごと `published/` へ移動してもこの相対パスは有効。

## 命名

- `<NN>` は記事内の画像連番（`01`, `02`, ...）
- `<desc>` は内容を表す kebab-case の短い英語（例: `before-after-workflow`）
- 例: `articles/20260520_ai-driven-mvp/assets/01-before-after-workflow.png`

## 複数枚

画像が複数あるときは 1 枚ずつ `codex exec` を呼ぶ。codex 側の品質が安定し、各画像のプロンプトを個別に調整できる。

## トラブル時・フォールバック

- codex が画像生成に失敗する / 使えない場合は、本文の挿入位置に画像生成プロンプトをインラインで記載する方式にフォールバックする（旧 `note-writing-assistant` 方式）。形式:

  ```
  ---
  【画像N：〇〇の図】
  ■ 画像生成プロンプト（日本語）
  <プロンプト>
  ---
  ```

- codex が直接 `assets/` にコピーできなかった場合は、出力された `~/.codex/generated_images/.../ig_*.png` の絶対パスを読み取り、こちら側で記事フォルダ内の `assets/` へコピーする。
- 生成画像のアスペクト比は約 16:9。厳密な比率や透過が必要な場合は codex 側の `imagegen` スキルの指示に従う。
