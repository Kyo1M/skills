# 画像生成プロンプト集

note記事に差し込むAI生成画像のプロンプトパターン。

## 基本原則

### 情報密度の原則

**抽象的な図解は読者に価値を提供しない。** 画像は「見ればわかる」ではなく「見て学べる」レベルの情報密度を目指す。

悪い例：
- 「左右に2つのボックスを配置」
- 「矢印でつなぐ」
- 「ポジティブな状態を示す」

良い例：
- 「左側に具体的なツール名（Claude Code、Cursor、GitHub Copilot）を列挙」
- 「各ステップに所要時間（30分、1時間など）を明記」
- 「成熟度バー80%（緑で塗りつぶし）で定量的に表現」

### Before/Afterの原則

変化を伝える図では、**具体的な数字・時間・作業内容**を含める。抽象的な「良い/悪い」ではなく、読者が自分の状況と比較できる情報を提供する。

悪い例：
- 「現状」vs「理想」
- 「ネガティブ」vs「ポジティブ」

良い例：
- 「従来：コード作業7時間、示唆出し1時間」vs「改善後：コード作業2時間、示唆出し3時間」
- 「Before：手戻り3回、合計8時間」vs「After：レビューで事前検出、合計3時間」

### 対話・具体例の原則

概念を説明する図では、**実際の発話例や具体的なシナリオ**を吹き出し形式で含める。

悪い例：
- 「人間の役割：問いの設計」
- 「AIの役割：コード生成」

良い例：
- 人間の吹き出し「分析目的：優良顧客の定義と購買傾向を明らかにしたい」
- AIの吹き出し「SQLでRFMスコアを算出するコードを生成します。JOINするテーブルはorders、customersで合っていますか？」

---

## 基本スタイル

すべての画像に共通する設定：

```
【日本語プロンプト】
スタイル：コンサルティングスライド風、PowerPointスライド、情報密度高め
デザイン：スタイリッシュ、クリーン、フラットデザイン
背景：白背景
配色：青とグレーを基調、アクセントに緑
強調：重要な箇所は**太字**または赤字で表現
フォント：モダンなサンセリフ体
テキスト：日本語で記載
アスペクト比：16:9

【English prompt for AI tools】
Style: Consulting slide style, PowerPoint slide, information-dense
Design: Stylish, clean, flat design
Background: White background
Color scheme: Blue and gray base colors, green accents
Emphasis: Bold text or red color for important elements
Font: Modern sans-serif
Text: Japanese text
Aspect ratio: 16:9
```

### 強調表現のルール

- **太字**：重要なキーワードやメッセージに使用
- **赤字**：警告、注意点、ネガティブな要素、課題に使用
- **緑**：ポジティブな要素、完了、成功、改善後の状態に使用

---

## 図解パターン

### 1. 詳細比較図（2カラム比較）

用途：ツール比較、領域比較、成熟度比較

**ポイント：各カラムに具体的な項目（ツール名、事例、数値）を3〜5個列挙する**

```
■ 画像生成プロンプト（日本語）

スタイル：コンサルティングスライド風、PowerPointスライド、情報密度高め、白背景

構成：
- 左右2カラムの詳細比較表
- 左側「〇〇領域」（緑枠で強調）
  - 項目1：具体的なツール名や事例を列挙
  - 項目2：ベストプラクティスや手法を具体的に記載
  - 項目3：コミュニティや情報源の状況
  - 成熟度バー：N%（緑色で塗りつぶし）
- 右側「〇〇領域」（グレー枠）
  - 項目1：具体的なツール名や事例を列挙
  - 項目2：現状の課題を具体的に記載
  - 項目3：情報共有の状況
  - 成熟度バー：N%（グレーで塗りつぶし）
- 中央下部に矢印と結論メッセージ

配色：青とグレー基調、アクセントに緑
アスペクト比：16:9
テキスト：日本語で記載

■ English prompt for AI tools
Consulting slide style, PowerPoint slide, information-dense, white background, blue and gray color scheme, green accents, Japanese text, aspect ratio 16:9, detailed two-column comparison table with specific tool names examples and maturity bars showing percentage
```

### 2. Before/After時間配分図

用途：業務改善、効率化、時間の使い方の変化

**ポイント：各作業に具体的な時間（30分、1時間など）と割合（%）、作業内容の説明を含める**

```
■ 画像生成プロンプト（日本語）

スタイル：コンサルティングスライド風、PowerPointスライド、情報密度高め、白背景

構成：
- 上下2段のBefore/After比較
- 上段「Before：〇〇」（グレー背景で課題感を表現）
  - 横棒グラフで時間配分を表示
  - 作業A：N時間（N%）「具体的な作業内容」
  - 作業B：N時間（N%）「具体的な作業内容」→赤字で「課題ポイント」
  - 作業C：N時間（N%）「具体的な作業内容」
  - **本来重要な作業：N時間（N%）**「時間が足りない」（赤字で警告）
  - 合計：N時間
- 下段「After：〇〇」（緑背景でポジティブ感）
  - 横棒グラフで時間配分を表示
  - 作業A：N時間（N%）「改善後の作業内容」
  - 作業B：N時間（N%）「改善後の作業内容」
  - **本来重要な作業：N時間（N%）**「ここに集中」（緑字で強調）
  - 合計：N時間
- 右側に「〇〇N倍」などの効果を示す吹き出し

配色：青とグレー基調、アクセントに緑と赤
アスペクト比：16:9
テキスト：日本語で記載

■ English prompt for AI tools
Consulting slide style, PowerPoint slide, information-dense, white background, blue and gray color scheme, green and red accents, Japanese text, aspect ratio 16:9, before-after comparison with horizontal bar charts showing time allocation with specific hours and percentages, before section in gray with red warnings, after section in green with highlighted improvements, callout bubble showing multiplier effect
```

### 3. 対話フロー図（役割分担）

用途：人とAIの協働、チーム間連携、コミュニケーションフロー

**ポイント：吹き出しに実際の発話例・指示文例を含める**

```
■ 画像生成プロンプト（日本語）

スタイル：コンサルティングスライド風、PowerPointスライド、情報密度高め、白背景

構成：
- 中央に対話形式のフロー図
- 左側「〇〇（役割A）」の吹き出し（緑枠）
  - 「具体的な発話例1：目的や意図を示す文」
  - 「具体的な発話例2：仮説や要件を示す文」
  - 「具体的な発話例3：期待する結果を示す文」
- 中央に双方向矢印「対話・フィードバック」
- 右側「〇〇（役割B）」の吹き出し（青枠）
  - 「具体的な発話例1：実行内容を示す文」
  - 「具体的な発話例2：確認質問の文」
  - 「具体的な発話例3：結果報告の文」
- 下部に結論ボックス
  - 「役割A：担当する責務を箇条書き」（緑で強調）
  - 「役割B：担当する責務を箇条書き」（青で表示）

配色：青とグレー基調、アクセントに緑
アスペクト比：16:9
テキスト：日本語で記載

■ English prompt for AI tools
Consulting slide style, PowerPoint slide, information-dense, white background, blue and gray color scheme, green accents, Japanese text, aspect ratio 16:9, dialogue flow diagram with speech bubbles containing specific example statements, left side role A in green showing intentions and requirements, right side role B in blue showing actions and confirmations, bidirectional arrow in center, conclusion box at bottom summarizing responsibilities
```

### 4. Before/Afterワークフロー比較図

用途：プロセス改善、ワークフロー変革、手順の比較

**ポイント：各ステップに所要時間と具体的な作業内容、課題/改善点を明記**

```
■ 画像生成プロンプト（日本語）

スタイル：コンサルティングスライド風、PowerPointスライド、情報密度高め、白背景

構成：
- 上下2段のワークフロー比較図
- 上段「従来型〇〇」（グレー背景）
  - N個のステップがフロー形式で並ぶ
  - 各ステップの下に詳細
  - ステップ1「作業名（N分/N時間）」「具体的な作業内容」
  - ステップ2「作業名（N分/N時間）」「具体的な作業内容」→赤字で「課題」
  - ステップ3「作業名（N分/N時間）」「具体的な作業内容」→赤字で「課題」
  - 合計：N時間、品質：△
- 下段「改善型〇〇」（緑背景）
  - N個のステップがフロー形式で並ぶ
  - 各ステップの下に詳細
  - ステップ1「作業名（N分/N時間）」「具体的な作業内容」→緑字で「ここに投資」
  - ステップ2「作業名（N分/N時間）」「具体的な作業内容」
  - ステップ3「作業名（N分/N時間）」「具体的な作業内容」
  - 合計：N時間、品質：◎
- 右側に効果を示す吹き出し「時間N%削減、品質向上」

配色：青とグレー基調、アクセントに緑と赤
アスペクト比：16:9
テキスト：日本語で記載

■ English prompt for AI tools
Consulting slide style, PowerPoint slide, information-dense, white background, blue and gray color scheme, green and red accents, Japanese text, aspect ratio 16:9, two-row workflow comparison, top row traditional workflow in gray with steps showing time and red warnings on problem areas, bottom row improved workflow in green with steps showing time and green highlights on key investments, callout bubble showing time reduction and quality improvement
```

### 5. チェックリスト図（詳細版）

用途：条件の列挙、ステップの確認、要件定義

**ポイント：各項目に補足説明や具体例を添える**

```
■ 画像生成プロンプト（日本語）

スタイル：コンサルティングスライド風、PowerPointスライド、情報密度高め、白背景

構成：
- タイトル：「〇〇の条件」（**太字**）
- N行のチェックボックス付きリスト（各項目に補足説明）
  ✓ 条件1（緑のチェックマーク）
    └ 補足：具体的な説明や例
  ✓ 条件2
    └ 補足：具体的な説明や例
  ✓ 条件3
    └ 補足：具体的な説明や例
- 下部に補足テキスト：「〇〇〇〇〇〇」

配色：青とグレー基調、チェックマークは緑
アスペクト比：16:9
テキスト：日本語で記載

■ English prompt for AI tools
Consulting slide style, PowerPoint slide, information-dense, white background, checklist format with green checkmarks, each item with supplementary explanation or example below, blue and gray color scheme, Japanese text, aspect ratio 16:9
```

### 6. ファネル図（詳細版）

用途：コンバージョン、ステップの減衰、プロセスの可視化

**ポイント：各段に具体的な数値（人数、割合、金額など）を含める**

```
■ 画像生成プロンプト（日本語）

スタイル：コンサルティングスライド風、PowerPointスライド、情報密度高め、白背景

構成：
- 縦にN段のファネル図（上が広く、下が狭い）
- 各段のラベルと数値（上から）：
  - ステップ1：N人/N%「具体的な状態の説明」
  - ステップ2：N人/N%「具体的な状態の説明」
  - ステップ3：N人/N%「具体的な状態の説明」
- 各段の間に離脱率を示す**赤いテキスト**（例：「-30%」）
- 右側に各ポイントの離脱理由を吹き出しで追加
- **最終ステップは緑で成功を表現**

配色：ファネルは青のグラデーション、離脱は赤、成功は緑
アスペクト比：16:9
テキスト：日本語で記載

■ English prompt for AI tools
Consulting slide style, PowerPoint slide, information-dense, white background, funnel diagram with specific numbers and percentages at each stage, blue gradient for stages, red text showing drop-off rates between stages, callout bubbles explaining reasons, green accents for success at final stage, Japanese text, aspect ratio 16:9
```

### 7. サイクル図（詳細版）

用途：PDCAサイクル、継続的改善、反復プロセス

**ポイント：各ノードに具体的なアクション例を含める**

```
■ 画像生成プロンプト（日本語）

スタイル：コンサルティングスライド風、PowerPointスライド、情報密度高め、白背景

構成：
- N個のノードが円形に配置され、矢印でつながるループ図
- ノード（時計回り）：
  1. ステップ1「具体的なアクション例」
  2. ステップ2「具体的なアクション例」
  3. ステップ3「具体的なアクション例」
  4. ステップ4「具体的なアクション例」
- 中央にサイクルの名称またはメッセージ（**太字**）
- 各ノード間の矢印に「成果物」や「インプット」を記載

配色：青基調、矢印は濃い青、アクセントに緑
アスペクト比：16:9
テキスト：日本語で記載

■ English prompt for AI tools
Consulting slide style, PowerPoint slide, information-dense, white background, cycle diagram with nodes in circular arrangement, each node containing specific action example, arrows labeled with outputs or inputs, blue color scheme, green accents, Japanese text, aspect ratio 16:9
```

### 8. マトリクス図（詳細版）

用途：ポジショニング、優先順位、分類

**ポイント：各象限に具体的な例や該当するケースを記載**

```
■ 画像生成プロンプト（日本語）

スタイル：コンサルティングスライド風、PowerPointスライド、情報密度高め、白背景

構成：
- 2x2のマトリクス（4象限）
- 縦軸ラベル：〇〇（高/低）（**太字**）
- 横軸ラベル：〇〇（高/低）（**太字**）
- 各象限にラベルと具体例
  - 左上：「象限名」＋具体例2〜3個
  - 右上：「象限名」＋具体例2〜3個（最重要は**緑で強調**）
  - 左下：「象限名」＋具体例2〜3個
  - 右下：「象限名」＋具体例2〜3個
- 推奨アクションを矢印で示す（オプション）

配色：象限ごとに色分け（青、緑、グレー、薄いグレー）
アスペクト比：16:9
テキスト：日本語で記載

■ English prompt for AI tools
Consulting slide style, PowerPoint slide, information-dense, white background, 2x2 matrix with four quadrants, each quadrant containing label and 2-3 specific examples, blue and gray color scheme, green accents for priority quadrant, optional arrows showing recommended actions, Japanese text, aspect ratio 16:9
```

### 9. メーター図（詳細版）

用途：進捗、達成度、比較

```
■ 画像生成プロンプト（日本語）

スタイル：コンサルティングスライド風、PowerPointスライド、情報密度高め、白背景

構成：
- 半円形のゲージ（メーター）
- ラベル：「〇〇」（**太字**）
- 針が特定の位置を指す（具体的な数値を記載）
- スケール上に目標ラインと現在値を明記
- 下部に「目標：N」「現在：N」「達成率：N%」を表示
- 目標達成ラインは**緑で強調**

配色：低い値はグレー/赤、高い値は青/緑
アスペクト比：16:9
テキスト：日本語で記載

■ English prompt for AI tools
Consulting slide style, PowerPoint slide, information-dense, white background, gauge/meter diagram, semicircle shape with specific target and current values marked, blue and gray color scheme, green for success indicators, red for low values, target and achievement rate displayed below, Japanese text, aspect ratio 16:9
```

### 10. フロー図（詳細版）

用途：手順、意思決定フロー、ワークフロー

**ポイント：各ステップに担当者、所要時間、ツールを含める**

```
■ 画像生成プロンプト（日本語）

スタイル：コンサルティングスライド風、PowerPointスライド、情報密度高め、白背景

構成：
- 左から右へ流れるフロー図
- N個のボックス（各ステップ）が矢印でつながる
- ボックス内のラベル：
  - ステップ名
  - 担当者（人間/AI/ツール名）
  - 所要時間
- 分岐がある場合は菱形で表現、分岐条件を明記
- 重要なステップは**太字**、ゴールは**緑でハイライト**
- 各矢印に成果物やアウトプットを記載（オプション）

配色：ボックスは青、矢印はグレー、アクセントに緑
アスペクト比：16:9
テキスト：日本語で記載

■ English prompt for AI tools
Consulting slide style, PowerPoint slide, information-dense, white background, flow diagram from left to right, boxes containing step name owner and time estimate, connected by arrows labeled with outputs, blue boxes, gray arrows, green accents for goals, diamond shapes for decision points with conditions, Japanese text, aspect ratio 16:9
```

---

## 記事内での配置ガイドライン

| 画像の役割 | 配置位置 | 推奨パターン |
|-----------|---------|-------------|
| 現状と課題の提示 | 冒頭（導入直後） | 詳細比較図、Before/After時間配分図 |
| 概念・定義の説明 | 章の冒頭 | 対話フロー図、マトリクス |
| プロセスの解説 | 本文中 | Before/Afterワークフロー、フロー図、ファネル |
| 具体例の提示 | 本文中 | 対話フロー図（具体的な発話例入り） |
| 記事のまとめ | 最終章 | サイクル図、チェックリスト |

## 画像枚数の目安

- 1,500字以下：2〜3枚
- 2,000〜3,000字：3〜5枚
- 3,500字以上：5〜6枚

多すぎると読みにくくなるため、6枚を上限とする。

---

## チェックリスト：画像プロンプト作成時の確認事項

画像プロンプトを作成したら、以下を確認する：

- [ ] 具体的な数字（時間、割合、人数など）が含まれているか
- [ ] 具体的なツール名、手法名、事例名が含まれているか
- [ ] Before/After形式の場合、両方に同じレベルの詳細度があるか
- [ ] 対話形式の場合、実際に使えそうな発話例が含まれているか
- [ ] 読者が「自分の状況と比較できる」情報になっているか
- [ ] 抽象的な表現（「ポジティブ」「良い」など）を具体的な表現に置き換えたか
