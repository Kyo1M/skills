# 指標の定義の型（既定）

対象リポジトリの規約に型があればそちらを優先する。この型の正本は [project-context-template](https://github.com/Kyo1M/project-context-template) の `docs/guide/data-definition-guide.md` 3 章で、3-1〜3-5 をそのまま写している（直すときはテンプレートを先に直し、`scripts/check-schema-copies.sh` で一致を確かめる）。共通の決まりは同じガイドの 1 章（本 skill の SKILL.md の絶対ルールと同じ）、作る流れは同じガイドの 3-6（本 skill の SKILL.md の Step 1〜7 と同じ）。

<!-- BEGIN: data-definition-guide 3-1..3-5 -->
### 3-1. YAML の型

記載例を兼ねます（架空の購入転換率）。自分の案件に翻訳して使ってください。

```yaml
type: metric                  # 種別（固定）
name: purchase-conversion-rate  # ファイル名と同じ slug（ASCII の kebab-case）
title: 購入転換率
aliases: [CVR]                # 資料・クライアント・SQL の列名での呼び名（任意）
date: "YYYY-MM-DD"            # 作成・最終更新日
status: draft                 # AI 案=draft。突き合わせが済んで人が確かめたら active（人が変える）
category: 売上                 # 指標の分類（任意。案件の KPI の分け方にそろえる）
derived_from:                 # もとにしたもの（定義書のファイル名とシート名／参考にした SQL のパス／「口頭」）
  - analysis/sql/monthly-conversion.sql
  - sample_metric_definition.xlsx の「KPI 定義」シート   # 会話に貼られた SQL なら「貼り付けの SQL（要旨）」
definition: 購入者数 ÷ 訪問者数 × 100。月は訪問日・受注日の暦月。返品だけの注文は購入に数えない
numerator: 購入者数（その月の訪問者のうち、その月に受注日がある注文を 1 件以上持つ会員のユニーク数。返品だけの注文と非会員の注文は含めない）   # 率の指標だけ
denominator: 訪問者数（その月にログインして訪問した会員のユニーク数）   # 率の指標だけ
unit: percent                 # count | people | percent | ratio | currency | score | days | months | years
scale: 100                    # 率の指標だけ（100 なら %、1 なら比）
grain: 月                      # 1 つの値が何の単位で決まるか
keys: [month]                 # grain を表す列（集計の出力の列名）
time_key: month               # 期間の列
# window: 直近 12 か月         # 窓がある指標だけ（任意）。この指標には窓が無いので書かない
population: 期間内にログインして訪問した会員（退会者・社員アカウントを除く）
tables: [web-sessions, order-detail, customer-master]  # docs/tables/ の slug
polarity: higher_is_better    # higher_is_better | lower_is_better | neutral
basis: ratio_of_sums          # 粒度より粗い単位（期間・区分）にまとめるときの束ね方（3-3）
# bands:                      # 区切りを持つ指標だけ（任意。3-5 の記載例）。この指標には区切りが無いので書かない
checks:                       # 別の出どころとの突き合わせ。結果は定性的に書き、件数は書かない
  - against: クライアントの月次レポートの CVR
    result: 訪問の数え方の違いでずれた（レポートは非ログインの訪問も分母に入れている）。違いを notes に残し、こちらの定義を正とした
    checked: "YYYY-MM-DD"
notes:
  - 月ごとの率を平均した値とは一致しない。四半期・年で見るときは、購入者数・訪問者数を四半期・年で数え直してから割る（月の人数を足さない）
```

### 3-2. 項目の書き方

| 項目 | 何を書くか |
|---|---|
| `aliases`・`category` | 任意。資料・クライアント・SQL の列名での呼び名と、案件の KPI の分け方にそろえた分類 |
| `status` | AI が案を出した時点は `draft`。`checks` の突き合わせが済み、人が確かめたら `active`。突き合わせ先が無い指標は `checks` に `against: なし（理由）` と書き、人が定義を確かめたら `active` にしてよい。突き合わせで合わないときは理由が分かるまで `draft` のまま |
| `derived_from` | もとにした定義書（ファイル名とシート名）・参考にした SQL のパス・「貼り付けの SQL（要旨）」・「口頭」。複数あれば列挙する。正とした取り方の SQL があれば、そのパスを先頭に書く |
| `definition` | 1 行の式か数え方。あわせて、期間に入れる日付の列（受注日か出荷日か）、基準日（いつ時点の値か、起点の日）、通貨、税込か税抜か、返品の扱いのように、取り方で値が変わる決めごとを書く。SQL のコメントにしか無い決めごとも、ここか `notes` に移す |
| `numerator`・`denominator`・`scale` | 率の指標だけ。分子・分母はそれぞれ何をどの条件で数えるか（ユニーク数か件数か）まで書く |
| `unit` | 3-1 の値から選ぶ。通貨の種類は `definition` に書く |
| `grain`・`keys`・`time_key` | 指標の値が決まる単位と、それを表す集計の出力の列名。会員ごとの値なら「会員×年」、率なら「月」「店舗×月」のように、値が 1 つに決まる単位にする |
| `window` | 任意。直近 12 か月のように、値を決める期間の窓がある指標だけ |
| `polarity` | 高いほど良い（`higher_is_better`）・低いほど良い（`lower_is_better`）・どちらでもない（`neutral`） |
| `population` | 対象に含める条件と除く条件。wiki の「用語」表に定義がある条件（社員アカウントの除外など）は、その用語を名指しして参照する。用語が無ければ条件をここに直接書く |
| `tables` | 使うテーブルの `docs/tables/` の slug（2 章）。定義が無いテーブルは配列に入れず、`notes` に「<物理名> のテーブル定義が無い（要確認）」と書き、先にテーブル定義を作ることを勧める |
| `basis` | 3-3 の 6 つから 1 つ。中央値なども並べて出すときは `notes` に書く |
| `bands` | 指標そのものの区切り（回数の区分、金額の帯など）。区切りの名前（`label`）と条件（`rule`）を書く。区分の切れ目の正本はここで、wiki の区分の行はこの YAML へリンクする |
| `checks` | 別の出どころ（クライアントのレポート・定義書の値・既存の SQL の出力）と突き合わせた結果。結果は定性的に書く。確認クエリは保存しない（要点を `result` に書く）。後に回すときは `checks: []` |
| `notes` | 使うときの注意（採らなかった取り方、旧定義との違い、クライアントの集計との違い、束ねたときの読み方） |

**変種の扱い**: 同じ指標で取り方が違うものがどちらも使われる場合（現地通貨と円、税込と税抜など）は、別の slug にします（例: `annual-sales-local`・`annual-sales-jpy`）。片方だけを正にする場合は、もう片方を `notes` に「採らなかった取り方」として残します。

### 3-3. 束ね方（basis）

| basis | 束ね方 | 例 |
|---|---|---|
| `ratio_of_sums` | 分子・分母をそれぞれ束ねる単位で取り直してから割る（合計できるものは合計し、ユニーク数は数え直す） | 転換率、達成率、前年比 |
| `sum` | 合計 | 売上、受注件数 |
| `recount` | 粗い単位で数え直す（足さない） | 購入者数・会員数などのユニーク数 |
| `snapshot` | 期間の最後の時点の値 | 在籍数、期末の会員数 |
| `weighted_avg` | 件数などで重みを付けた平均 | アンケートの点数 |
| `simple_avg` | 単純な平均 | 会員ごとの購入回数の平均、元データに分子・分母が無く率だけがある指標 |

- 率の指標は分子・分母を取り直してから割り、月ごとの率を平均しません。月ごとの率の平均を使うときは、使う側（集計のコメント・分析設計）にそう書きます。
- ユニーク数は月の値を足さず、束ねる単位で数え直します（月ごとの購入者数の合計は、年の購入者数になりません）。率の分子・分母がユニーク数のときも、束ねる単位で数え直してから割ります。

### 3-4. wiki と llms.txt への載せ方

`docs/wiki/index.md` の「用語」表に、1 指標 1 行で載せます。用語の列を YAML へのリンクにし、定義の列には 1 行の式と束ね方だけを書きます。区分（回数の区分など）の行がすでにあれば、定義の列を YAML の `bands` へのリンクに置き換えます。YAML へリンクした行の正本は YAML です。会議などで定義が変わったら、議事録ではネクストアクションに「指標の定義の YAML を直す」を置き、この章の流れで YAML を直してから行を合わせます。

```markdown
| 用語 | 定義 |
|------|------|
| [購入転換率](../metrics/purchase-conversion-rate.yaml) | 購入者数 ÷ 訪問者数 × 100（束ね方: 分子・分母を数え直してから割る） |
```

`llms.txt` の「Metrics」節には `- [docs/metrics/purchase-conversion-rate.yaml](./docs/metrics/purchase-conversion-rate.yaml): 購入転換率（購入者数 ÷ 訪問者数 × 100）` の形で 1 行足します。wiki に「直近更新」節があれば、その 1 行も差分に含めます。

### 3-5. 記載例 2（区分を持つ指標）

会員ごとの値を区分で束ねる指標の例です（架空の年間購入回数）。

```yaml
type: metric
name: annual-purchase-count
title: 年間購入回数
aliases: [購入頻度, F]
date: "YYYY-MM-DD"
status: active
category: 顧客
derived_from:
  - analysis/sql/customer-yearly-summary.sql
  - 口頭（年の区切りと返品の扱い）
definition: 会員ごとに、受注日の暦年に入る注文のうち、注文番号ごとの amount の合計（返品の行を含む）が正の注文を数える。年は受注日の暦年（1〜12 月）
unit: count
grain: 会員×年
keys: [customer_id, year]
time_key: year
population: その年に 1 回以上購入した会員（非会員の注文・社員アカウントを除く）
tables: [order-detail, customer-master]
polarity: higher_is_better
basis: simple_avg
bands:
  - label: 1 回
    rule: 1 回
  - label: 2 回
    rule: 2 回
  - label: 3〜4 回
    rule: 3 回以上 4 回以下
  - label: 5 回以上
    rule: 5 回以上
checks:
  - against: なし（クライアントに同じ指標の集計が無いため）
    result: 突き合わせ先が無いため、年の区切りと返品の扱いを担当者が確かめた
    checked: "YYYY-MM-DD"
notes:
  - 区分や年で束ねるときは会員ごとの値の単純な平均を取る。分布が偏るので中央値も並べて出すことが多い
  - 伝票数（order_id のユニーク数）で数える取り方は採らなかった。全額を返品した注文も 1 回に数えてしまうため
```

<!-- END -->
