# プロジェクト開発におけるバグと困難 / Bugs and Difficulties in Development

日付: 2025-11-20

## 概要 / Overview

本プロジェクト（PDF2Anki）の開発プロセスにおいて遭遇した主要なバグ、技術的な困難、およびそれらの解決策についてまとめました。

## 1. バグとエラー / Bugs and Errors

### 1.1 Streamlit IndentationError
- **現象**: `src/streamlit_app.py` の実行時に `IndentationError` が発生し、アプリが起動しない。
- **原因**: コード内の意図しない場所（`generate_anki_cards` 関数の直前）に閉じていないトリプルクォート（`"""`）が残っていたため、Pythonパーサーが構文エラーを起こした。
- **解決策**: 該当のトリプルクォートを削除。

### 1.2 Marker API 404 エラー
- **現象**: StreamlitアプリからPDF変換を実行すると `404 Client Error: Not Found` が発生する。
- **原因**:
  1. **ルーティング順序**: `marker-api/server.py` で Gradio アプリをルートパス (`/`) にマウントした後に FastAPI エンドポイントを定義していたため、Gradio が全てのリクエストを捕捉していた。
  2. **レスポンス形式**: クライアント側 (`marker_client.py`) がテキストレスポンスを期待していたが、API は JSON を返していた。
- **解決策**:
  1. FastAPI エンドポイントを Gradio マウントの**前**に定義し、Gradio のマウントパスを `/gradio` に変更。
  2. クライアント側で JSON レスポンスを適切にパースするように修正。

## 2. 環境構築と設定の困難 / Environment and Setup Difficulties

### 2.1 WSL環境でのMarker APIセットアップ
- **困難**: Windows 11 + WSL (Ubuntu) 環境での Marker API のセットアップにおいて、システム依存関係の不足やポート競合が発生。
- **詳細**: `poppler-utils` や `build-essential` などのネイティブライブラリが必要であった。また、ポート 8000 が他のプロセスと競合することがあった。
- **解決策**:
  - 必要な `apt` パッケージのインストール手順を文書化。
  - ポート確認手順 (`lsof`) と環境変数によるポート変更のサポート。

### 2.2 PDF変換のパフォーマンス
- **困難**: CPUのみの環境では、特に OCR (`surya`) を使用する場合、PDF変換に非常に時間がかかる。
- **解決策**:
  - **GPU利用**: CUDA 対応 GPU が利用可能な場合の環境変数設定 (`TORCH_DEVICE=cuda` 等) を整備。
  - **OCRエンジンの選択**: テキストベースのPDFに対しては OCR を無効化 (`OCR_ENGINE=None`) するか、軽量な `ocrmypdf` を選択可能にするオプションを検討。
  - **バッチ処理**: 並列処理数 (`max_workers`) の調整。

## 3. アーキテクチャと統合の課題 / Architecture and Integration Challenges

### 3.1 ライセンスの互換性 (MIT vs GPL v3)
- **課題**: プロジェクト本体は MIT ライセンスだが、依存する `marker-api` や `marker-pdf` が GPL v3 (または GPL-3.0-or-later) であり、リポジトリに含めるとプロジェクト全体が GPL の影響を受けるリスクがあった。
- **解決策**:
  - **分離**: `marker-api` を HTTP API サーバーとして別プロセスで実行し、疎結合にするアーキテクチャを採用。
  - **推奨構成**: 将来的には `marker-api` を別リポジトリまたはサブモジュールとして管理することを推奨。
  - **ドキュメント**: ライセンスの法的リスクと対応策を `docs/20251106_license_analysis.md` に明記。

### 3.2 新旧モジュールの統合と型システム
- **課題**: 新しく導入したマークダウン処理モジュール（`markdown_chunker.py` 等）が独自の型定義 (`domain_types.py`) を持っており、既存の Streamlit アプリの型 (`pdf2anki_types.py`) と不整合があった。
- **解決策**:
  - **Wrapper パターン**: `markdown_processor_wrapper.py` を作成し、型変換と処理のオーケストレーションを担当させることで、既存コードへの影響を最小限に抑えて統合。

### 3.3 出力ファイルの管理
- **課題**: 変換結果や生成されたカード、プロンプトの履歴管理ができず、再実行やデバッグが困難だった。
- **解決策**: `outputs/` ディレクトリ配下にタイムスタンプ付きのセッションフォルダ (`YYYYMMDD_HHMMSS_pdfname`) を自動生成し、関連ファイル一式（MD, JSON, TSV, Script）を保存する仕組みを実装。

## まとめ / Summary

初期の構文エラーや設定ミスから、パフォーマンス最適化、ライセンスコンプライアンス、アーキテクチャ統合といったより高度な課題へとシフトしてきました。特に Marker API との連携部分（通信、ライセンス、パフォーマンス）が開発の主要なハードルとなりましたが、API化による疎結合アーキテクチャと適切なラッパーの実装により解決されました。

