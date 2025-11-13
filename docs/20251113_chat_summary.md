タイトル: 本チャットで実施した内容（2025-11-13）

本チャットでは、PDF2Anki の全体フローを把握し、Mermaid によるフローチャートを作成してドキュメント化しました。

実施内容:
- リポジトリの主要モジュール（`src/streamlit_app.py`, `src/marker_client.py`, `src/markdown_*`, `src/semantic_detector.py`, `src/anki_core.py`）を確認
- エンドツーエンド処理（PDFアップロード→Marker API 変換→Markdown整形/チャンク→LLMによるカード生成→TSV出力→ダウンロード）を整理
- Mermaid フローチャートを作成し、以下に保存
  - `docs/20251113_pdf2anki_flowchart.md`

変更点:
- 追加: `docs/20251113_pdf2anki_flowchart.md`
- 追加: 本記録 `docs/20251113_chat_summary.md`
- 既存コードへの変更は無し（既存挙動は維持）

閲覧方法:
- フローチャートは Mermaid 記法です。VSCode など Mermaid 対応プラグイン、あるいは Web 上の Mermaid Live Editor で可視化できます。

補足:
- 大容量ファイルはコミットせず、成果物は `docs/` 以下のテキストベースのみ追加しています。


