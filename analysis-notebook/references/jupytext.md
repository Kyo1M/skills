# スクリプトを書いて notebook に変換する形式（jupytext）

スクリプト（percent format）を唯一の編集対象にし、jupytext で `.ipynb` に同期して実行する。出力は `.ipynb` に残るので、ファイルを渡すだけで結果も見せられる。

言語（Python・R など）、スクリプトと `.ipynb` の置き場、実行のコマンドやコンテナは規約から読む。以下は規約に無いときの既定。

## percent format の書き方

```python
# %% [markdown]
# # 0. 概要
# - **問い**: …
# - **判定単位**: …

# %%
import pandas as pd

# %% [markdown]
# ## 1.y 問い 1 への回答
# - **回答**: 部分的
```

- `# %% [markdown]` の後は、各行を `# ` で始める（箇条書きも同じ）
- `# %%` でコードのセルを始める
- 見出しと項目は SKILL.md の「推奨の notebook 構成」に合わせる
- 回答のセルの数値は、実行した出力から写す。データを取り込み直したら、再実行して写し直す（写し忘れを防ぐため、主要な数値は回答の直前のセルで出力しておく）

## 編集の決まり

- **`.ipynb` を直接編集しない**。スクリプトだけを編集し、同期で `.ipynb` に反映する
- スクリプトの中の相対パスは、`.ipynb` を実行するフォルダを基準に書く（スクリプトの置き場と `.ipynb` の置き場が違う規約では特に注意する）
- 表示のヘルパーは、notebook の外（スクリプトとして実行）でも動くよう、文字の表示に切り替える fallback を付ける

```python
def show_table(df, title=None):
    if title:
        print(f"## {title}")
    try:
        from IPython.display import display
        display(df)
    except ImportError:
        print(df.to_string())
```

- 表の多い notebook では、このヘルパーで表示をそろえ、`title` で表の所在を分かるようにする
- 代表インスタンスは選ぶ規則をコードに書き、ID は実行時に求める（SKILL.md の「分析方針」）

## 同期と実行

1. 同期する

   ```sh
   jupytext --sync <スクリプト>
   ```

   初めて `.ipynb` を作るときは `jupytext --set-formats ipynb,py:percent <スクリプト>` の後に `--sync`。

2. 実行して出力を確かめる

   ```sh
   jupyter nbconvert --to notebook --execute --inplace <notebook>.ipynb
   ```

   - 実行が重い・環境が別（コンテナなど）の規約では、規約のコマンドで実行する
   - 同期の道具が実行環境に無いときは、同期を手元で行い、実行だけを実行環境で行う（実行環境で同期をやり直さない）

3. 出力を読む

   実行した `.ipynb` の出力（`outputs`）を読み、回答のセルと出力が食い違っていないかを見る。エラーのセル（`output_type: error`）があれば直して 1 からやり直す。

## 図を png に書き出す

- レポートに図を載せるときは、notebook の中で png に書き出す（書き出す先は規約のレポート・図の置き場）
- 書き出した png を開き、文字欠け・軸の文字の切れが無いかを確かめる。描画のライブラリが日本語を描けないときは、図の中の文字を英語にし、日本語はレポートの本文に書く（規約に図の文字の制約があれば従う）
- 図に個人を指す値（ID・氏名）や自由記述の原文を入れない
