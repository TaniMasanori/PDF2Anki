## PDF2Anki プレゼン概要（Project_plan.md 紹介）

### 問題定義（Problem Definition）
- 大量のPDF（講義スライドや学術論文）から学習用のQ&Aカードを作成する作業は、手作業だと時間がかかり、網羅性や一貫性の担保が難しい。
- 図表や数式を含む資料では、適切なテキスト抽出や整形、要点抽出がさらに困難。
- 目標は、短時間で質の高いAnki用カードを生成し、学習効率を高めること。
- デモの対象範囲：講義スライド／学術論文（図・表・数式を含む）。

### 解決策（Solution）
- PDF → Markdown：Marker APIをWSL上でローカル実行し、高精度なMarkdownへ変換（構造、画像/表参照、LaTeX数式の保持）。
- Markdown → Q&A：LLM（GPT系API）にプロンプトテンプレートを用いて、指定枚数のBasic形式Q&Aを生成（長文はセクションごとに分割しトークン制約に対応）。
- Q&A → Importファイル：Ankiが読み込めるタブ区切り（TSV/CSV）に整形（Front/Backの2列、LaTeXは$...$等で保持）。
- Anki取り込み：デモではGUIから手動インポートでノート追加（最小実装）。
- ストレッチゴール：Ankiアドオン／AnkiConnectで自動取り込みを実装（最終発表までに検討）。
- 非目標（デモ外）：画像内容の自動理解による出題、独自モデル学習。

### システム構成（System Architecture）
- 実行環境
  - Windows + WSL(Ubuntu)：WSL側でMarker APIサーバを起動（Python環境、RESTエンドポイント）。
  - Pythonスクリプト：API呼び出し、テキスト分割、LLM応答解析、TSV生成を担当。
  - Anki Desktop（Windows）：生成TSVをGUIから手動インポート。
- コンポーネント概要
  1. PDF入力（ユーザが選択）
  2. Marker API（WSL, REST）：PDF→Markdown(+assets: 画像/表/数式)
  3. 変換結果管理：Markdown本文と関連ファイルを保存
  4. LLM呼び出し：GPT API＋プロンプトテンプレート、セクション分割・再結合
  5. 成形処理：Q&A抽出、整形、LaTeX保持、TSV生成
  6. Anki手動インポート：Basicノート型にFront/Backを割当
- データフロー（概念）
  - PDF → [Marker API] → Markdown(+assets)
  - Markdown(分割) → [LLM] → Q&Aテキスト
  - Q&A → TSV(Front/Back) → [Anki Import]
- 主要設計ポイント
  - セクション単位の分割生成で長文・トークン制約に対応。
  - 数式はLaTeX（$...$など）で保持し、AnkiのMathJax表示互換を確保。
  - デモ段階ではエラーハンドリングを最小限に留め、再現性重視（バックアップとして事前生成TSVも準備可能）。
  - セキュリティと運用：APIキーは環境変数で管理、機密情報はリポジトリに含めない。`.gitignore`で大容量生成物（assets等）を除外。


