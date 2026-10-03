# marimo の書き方と実行（既定の形式）

marimo の notebook は `.py` のファイルそのもので、変換や同期は要らない。セルの出力はファイルに入らず、実行すると `__marimo__/session/` に書き出される。

実行のコマンドの前置き（`uv run` など）と置き場は規約から読む。以下のコマンドは前置きを省いて書く。

## セルの書き方

```python
import marimo

__generated_with = "<marimo のバージョン>"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import plotly.express as px

    return mo, px


@app.cell
def _(mo):
    mo.md("""
    # 0. 概要

    - **問い**: …
    - **判定単位**: …
    """)
    return


@app.cell
def _(df, mo):
    _stores = df["store_code"].nunique()
    mo.md(f"""
    ## 1.y 問い 1 への回答

    - **回答**: 部分的
    - **根拠**: 対象は {_stores} 店舗。…
    """)
    return


if __name__ == "__main__":
    app.run()
```

- 説明のセルは `mo.md`。見出しと項目は SKILL.md の「推奨の notebook 構成」に合わせる
- 説明文の数値は、計算した値を `mo.md(f"…")` で差し込む。手で書き写すと、データを取り込み直したときに古くなる
- 新規作成は、規約の雛形をコピーするか、ファイルを直接書く（`marimo new` に引数を渡すと AI で生成するので使わない）。`__generated_with` は `marimo check` が求めるので消さない
- 1 セルの最後の式がそのセルの出力になる。表や図を出すセルは、最後にその変数を置く

## リアクティブな実行の注意

- 同じ変数名を 2 つのセルで定義しない（marimo が止める）。上書きしたいときは別の名前にする
- セルの中だけで使う名前は `_` で始める（`_total`、`_fig` など）。他のセルから見えず、名前がぶつからない
- セルは依存関係の順に実行される。ファイルの並び順に頼らない
- 他のセルが使う値は `return` に並べる
- 関数を他のセルで使うときは、関数を定義したセルで `return` する

## 表の出し方

- DataFrame をセルの最後に置けば、表として出る（行が多ければページ送り付き）
- 列を絞る・並べ替えるなど、見せ方を決めたいときは `mo.ui.table(df, page_size=…)`
- 出力の JSON には、表の先頭の 1 ページ（既定は 10 行）しか残らない。`read_session.py` で全行を読みたい表（レポートに引く表）は `mo.ui.table(df.reset_index(), page_size=<行数以上>)` で出す
- `mo.vstack` の中に入れた表や、dict・tuple で返した複数の表は、出力の JSON で先頭の 1 つしか読めないことがある。レポートに引く表は 1 セル 1 表にするか、`pd.concat` で 1 つの表にまとめる
- 集計表の注目行を展開するヘルパーは、集計のセルの近くで関数として定義し、セルの中で呼ぶ

```python
@app.cell
def _(df):
    def show_group_detail(key_column, key_value, columns):
        """集計の注目行に含まれる行を、指定した列だけ並べて返す（notebook の出力の中だけで見る）"""
        return df.loc[df[key_column] == key_value, columns]

    return (show_group_detail,)
```

- 代表インスタンスは、冒頭のセルで選ぶ規則（例: 指標が中央値に最も近い行）を書き、ID は実行時に求める

```python
@app.cell
def _(summary):
    # 代表インスタンス: 退職率が中央値に最も近い店舗（ID はコードに書かない）
    _median = summary["退職率"].median()
    representative = summary.loc[(summary["退職率"] - _median).abs().idxmin()]
    return (representative,)
```

## 実行と検証

1. 書き方を検査する

   ```sh
   marimo check --strict <notebook>
   ```

   `--strict` で warning も失敗にする。終了コードが 0 でなければ直す。

2. 最後まで実行し、出力を書き出す

   ```sh
   marimo export session --force-overwrite --no-sandbox <notebook>
   ```

   - `--force-overwrite` を必ず付ける。付けないとコードが変わっていない notebook は実行が飛ばされ（`skip: … up-to-date`）、データを取り込み直しても古い出力が残る
   - 出力は `<notebook のフォルダ>/__marimo__/session/<ファイル名>.py.json`
   - セルが 1 つでも失敗すると、終了コードは 1 になる（出力の JSON には `type: error` が入る）

3. 出力を読む

   ```sh
   python3 <このスキルのフォルダ>/scripts/read_session.py <notebook>
   ```

   セルごとに、説明文・表（先頭 20 行と全体の行数）・図（タイトル・軸・系列の数）・エラーを文字で出す。失敗したセルがあれば終了コード 1。これを読んで、回答のセルと出力が食い違っていないかを見る。

- `__marimo__/` はコミットしない（`.gitignore` に入れる）
- 実行をユーザーの画面で確かめてもらうときは `marimo edit <notebook>`。marimo の AI 機能を使わない決まりが規約にあれば従う

## 図を png に書き出す

レポートに図を載せるときは、notebook の中で png に書き出す。

```python
_fig = px.bar(summary, x="店舗", y="人数", title="店舗別の人数")
_fig.write_image(FIG_DIR / "store_headcount.png", width=1000, height=600, scale=2)
_fig
```

- Plotly の `write_image` には kaleido（Python のパッケージ）と Chrome が要る。無ければ規約の依存の決め方に従って足すかをユーザーに相談する
- 書き出す先（`FIG_DIR`）は規約のレポート・図の置き場。図を commit する時点に決まりがあれば従う
- 書き出した png を開き、日本語の文字欠け・軸の文字の切れが無いかを確かめる
- 図に個人を指す値（ID・氏名）や自由記述の原文を入れない
