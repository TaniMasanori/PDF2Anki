# Markdownアップロード機能の追加（PDF変換スキップ対応）

本日の変更では、既存のPDFアップロードと変換フローに加えて、既にMarkdownファイルがある場合にそれを直接アップロードしてPDF→Markdown変換をスキップできる機能を追加しました。

## 変更点
- `src/streamlit_app.py`
  - 「Upload Markdown」セクションを追加し、`.md`/`.markdown`をアップロード可能にしました。
  - アップロードしたMarkdownを`outputs/<timestamp>_<basename>/converted.md`として保存し、以降のカード生成フローでそのまま利用します。
  - PDF未使用時でもダウンロードファイル名生成でエラーにならないよう、ファイル名のフォールバック（`converted.md`, `anki_cards.tsv`）を追加しました。
  - 「How to use」にMarkdownアップロードの手順を追記しました。

## 使い方
1. PDFから始める場合  
   - 「Choose a PDF file」でPDFを選択  
   - 「Convert to Markdown」をクリック  
   - 「Generate Anki Cards」でカード生成  
   - ダウンロード欄からMarkdownまたはTSVを保存
2. 既存のMarkdownから始める場合（PDF変換スキップ）  
   - 「Upload Markdown」で`.md`または`.markdown`を選択  
   - そのまま「Generate Anki Cards」でカード生成  
   - ダウンロード欄からMarkdownまたはTSVを保存

## 保存場所
- セッションごとに`outputs/<timestamp>_<basename>/`ディレクトリを作成し、以下を保存します。
  - `converted.md`（アップロードされたMarkdown、またはPDF変換後のMarkdown）
  - `anki_cards.tsv`（カード生成後に出力）
  - `prompt_script.sh`（カード生成に用いるスクリプト）
  - `meta.json`（Markdownアップロード時は簡易メタを出力、PDF変換時は変換結果のメタをコピー）

## 互換性・注意点
- 既存のPDF→Markdown変換フローには影響しません（最小限の改修）。
- Markdownのみで開始した場合はPDFのハッシュ（`pdf_sha256`）は存在しないため、チャンク処理の拡張情報はPDF由来のメタが無い状態で実行されます。必要に応じて`Processing Options`の設定を調整してください。

## 今後の拡張候補
- Markdownアップロード時の追加バリデーション（Front Matterや特定フォーマットの検証）。
- 既存の`meta.json`を伴うMarkdown一式のドラッグ&ドロップ対応（フォルダアップロード）。


