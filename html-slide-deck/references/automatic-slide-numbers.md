# ページ番号の自動反映

今後の資料では、フッター右のページ番号を自動反映する。作成日は表示しない。既存の最終資料は依頼なしに変更しない。

## HTML テンプレート

`assets/template.dc.html` の `[data-page]` と末尾の runtime を保持する。番号は現在のページ番号だけを表示する。表紙を含めて順番を数え、表紙の番号を非表示にしても次のページは 2 とする。`data-deck-skip` は表示・出力から除く要素に限る。非表示スライドも PowerPoint ファイルに残す場合は番号に含まれるため、HTML と出力の対象を合わせる。

## PowerPoint 出力

HTML の数字を通常テキストでコピーしても自動番号にはならない。PowerPoint の標準スライド番号フィールド `a:fld type="slidenum"` を使う。テンプレートから新規スライドを作る場合も、番号フィールドを持つレイアウトや本文スライドを複製する。

- PowerPoint 上で編集するときは「挿入 → スライド番号」を使用し、マスター／レイアウトの番号欄をフッター右へ配置する。表紙の番号表示は指定されたデザインに合わせる。
- プログラムで生成する場合は、各ページの番号専用テキストボックスに `SlideNumber` と命名する。通常の数字や本文の参照番号を検索して一括置換しない。
- 使用する出力ライブラリがフィールドを保持できない場合は、PPTX の最終エクスポートと再掲ページの組み込みを終えてから次の変換を行う。数字だけの専用テキストボックスを対象とし、配置・段落書式・文字書式を維持する。

```bash
python3 ~/.claude/skills/html-slide-deck/scripts/pptx-slide-numbers.py draft.pptx --output final.pptx --skip-slide 1
python3 ~/.claude/skills/html-slide-deck/scripts/pptx-slide-numbers.py final.pptx --skip-slide 1
```

`--skip-slide 1` は表紙に番号欄を置かない場合だけ付ける。指定はスライド順での位置であり、枚数からは除かれない。出力先は新しいファイルにする。入力は変更しない。フィールド化のあとに別ライブラリで再エクスポートすると通常テキストに戻る場合があるため、納品する最終バイナリで再検査する。

再掲ページの古い固定番号は番号専用欄に統一し、同じ位置に固定番号と自動番号を重ねない。既存のレイアウトにネイティブ番号がある場合は追加せず活用する。この補助スクリプトは明示的な `SlideNumber` テキストボックス専用で、マスター由来の番号欄を推測して編集しない。

## 確認範囲

- 出力直後のキャッシュ値を実際のスライド順に合わせる。`--output` を省くと、固定文字が残っていないことと値の整合を検査する。
- PowerPoint 上での追加・削除・並べ替えに追従するのは標準フィールド。初めて使う変換経路では作業用コピーを PowerPoint で開き、削除・並べ替えと番号表示を確認する。プレビュー環境によっては保存時のキャッシュ値だけを表示する。
- 総ページ数は PowerPoint の標準機能では自動更新されないため、既定では付けない。本文の「○ページを参照」や表紙の流れは別途照合する。参照先は可能ならページ名でも示す。

根拠: [Microsoft のスライド番号フィールド仕様](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.drawing.field?view=openxml-3.0.1)、[スライド番号と総枚数の説明](https://support.microsoft.com/en-US/PowerPoint/show-the-slide-number-and-total-number-of-slides-on-every-slide)。
