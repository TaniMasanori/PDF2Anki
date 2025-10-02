---
title: Member 1 実装計画・設計（PDF変換パイプラインと統合）
date: 2025-10-02
owner: Member 1 (Alice)
scope: Marker API セットアップ、変換出力処理、カード生成工程へのデータ連携、Anki 取込フォーマット整備、Windows/WSL 対応
---

## 1. 目的と成果物
この文書は Member 1 の担当範囲（PDF 変換パイプラインとシステム統合）の詳細な実装計画・設計を示す。最終的に以下を完了させる。

- Anki 用カード生成の前段となる PDF→Markdown 変換を安定運用できること（Marker API）
- 変換結果の正規化・チャンク分割・メタデータ付与の標準データモデルを確立
- カード生成工程（LLM）に安全に渡せる I/O 契約と API/スクリプト I/F を定義
- Anki 取込（TSV）に適した整形・書き出し仕様を決定
- Windows/WSL 環境での安定運用

## 2. タスクリスト（日本語/English）
- 実行環境準備（Windows/WSL） / Environment setup (Windows/WSL)
- Marker API の導入と起動方法確立 / Install and run Marker API
- 変換クライアント（HTTP）実装 / Implement conversion HTTP client
- 出力正規化・クリーニング / Normalize and clean conversion output
- チャンク分割とメタ情報設計 / Chunking and metadata design
- データ契約（型・JSON スキーマ）定義 / Define data contracts (types/JSON schema)
- カード生成工程へのインターフェース定義 / Define interface to card generation step
- Anki 取込フォーマット（TSV）仕様・整形実装 / Anki TSV spec and writer
- ロギング/再現性（チェックポイント保存） / Logging and reproducibility
- 統合テストとサンプル PDF での検証 / Integration tests with sample PDFs

## 3. 全体アーキテクチャ
```mermaid
flowchart LR
  A[PDF Input] --> B[Marker API (PDF->Markdown)]
  B --> C[Cleaner/Normalizer]
  C --> D[Chunker (by section/tokens)]
  D --> E[Card Generation Interface]
  E --> F[TSV Writer]
  F --> G[Anki Manual Import]
```

## 4. 実行環境設計（Windows/WSL ローカル Python 実行）
### 4.1 WSL（推奨: Ubuntu）
1) Microsoft Store から Ubuntu WSL を導入し初期化
2) 必要パッケージの導入（Python/ビルド/ユーティリティ）
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip git build-essential python3-dev poppler-utils
   ```
3) 仮想環境の作成と更新
   ```bash
   python3 -m venv ~/.venvs/pdf2anki
   source ~/.venvs/pdf2anki/bin/activate
   python -m pip install --upgrade pip
   ```
4) Marker API の取得と依存インストール（リポジトリ README に従う）
   ```bash
   git clone https://github.com/adithya-s-k/marker-api.git
   cd marker-api
   pip install -r requirements.txt || true
   pip install -e . || true
   ```
5) サーバ起動（例: FastAPI/Uvicorn）
   ```bash
   export PORT=8000
   uvicorn marker_api.app:app --host 0.0.0.0 --port ${PORT}
   ```
6) 疎通確認
   ```bash
   curl http://localhost:8000/docs || true
   ```
7) Windows からのアクセス/共有
   - ブラウザで `http://localhost:8000/docs` が開けること
   - Windows の `C:\\Users\\<user>\\PDF2Anki` は WSL では `/mnt/c/Users/<user>/PDF2Anki`
8) 詳細手順は `docs/20251002_marker_api_setup_wsl.md` を参照

### 4.2 Windows（ネイティブ実行も可能）
1) Python 3.10+ をインストール（PATH 登録）
2) 仮想環境作成: `python -m venv .venv` / 有効化
3) 依存関係（後日 `requirements.txt` 導入を想定）
4) CLI 単体検証（参考）: `marker_single <pdf> <outdir>`（Marker CLI がある場合）

（Docker は本プロジェクトでは使用しない方針）

## 5. Marker API 利用設計
### 5.1 エンドポイント（想定）
- POST `/convert`（multipart/form-data, フィールド名 `file`）→ Markdown テキスト or 出力アーカイブ
- GET `/healthz` or `/` → ヘルスチェック
- Swagger: `/docs`（仕様確認）

実際のエンドポイント名・レスポンス形は `/docs` で確認し、クライアント側で型を固定する。

### 5.2 タイムアウト・再試行方針
- タイムアウト初期値: 120s（大きめ PDF に配慮）
- 429/5xx は指数バックオフで最大 3 回再試行
- 例外時は入力 PDF のハッシュ名でエビデンス（ログ・レスポンス）を保存

## 6. データフローとデータ契約
### 6.1 ディレクトリ構成（提案）
```
PDF2Anki/
  docs/
  src/               # 実装（後日）
  outputs/
    conversions/<pdf_hash>/
      source.pdf
      marker.md            # 変換 Markdown（UTF-8）
      meta.json            # バージョン/所用秒数/ページ数 等
      cleaned.md           # クリーニング後
      chunks/
        chunk_0001.md
        ...
      cards.tsv            # Anki 取込ファイル（生成後）
```

### 6.2 型（概念設計）
```
ConversionMeta: {
  source_path: str,
  source_sha256: str,
  pages: int,
  engine: { name: str, version: str },
  elapsed_sec: float,
  created_at: str  # ISO 8601
}

ConversionResult: {
  markdown_path: str,
  meta_path: str,
  images_dir?: str
}

Chunk: {
  id: str,                  # chunk_0001 など
  text: str,
  start_page?: int,
  end_page?: int,
  section_title?: str,
  token_count: int,
  source_ref: { pdf_sha256: str, chunk_id: str }
}

Card: {
  question: str,
  answer: str,
  tags?: [str],
  source_ref?: { pdf_sha256: str, chunk_id?: str }
}
```

## 7. クリーニングとチャンク分割
### 7.1 クリーニング
- 余分な改行・連続空白の整形
- ヘッダ/フッタの反復除去（ページ番号等）
- 数式は `$...$` / `$$...$$` を保持（Anki MathJax 前提）
- 画像参照（`![]()`）はカード生成で未使用なら一旦残置または除去ポリシー化

### 7.2 チャンク分割（優先順）
1) セクション見出し（`#`, `##` 等）単位で分割
2) トークン数上限（例: ~2k tokens）で分割
3) 章・節の構造メタを `Chunk.section_title` に格納

## 8. カード生成工程へのインターフェース
LLM 側は Member 2 担当だが、受け渡し契約を定義：

- 入力: `chunks/*.md` を 1 チャンクずつ渡す。併せて `prompt_parameters.json`（例: 生成枚数, スタイル）
- 出力: `cards.jsonl`（1 行 1 カード, `Card` 型）または `cards.tsv`
- エラー時: `errors.log` にチャンク ID とメッセージ

将来拡張で AnkiConnect 直送や `.apkg` 生成（genanki）へ切替可能な抽象化を維持する。

## 9. Anki 取込フォーマット仕様（TSV）
- 区切り: タブ（`\t`）
- エンコーディング: UTF-8（BOM なし推奨）
- 1 行 = 1 カード、列: `Front\tBack`
- 改行は `<br>` へ正規化（フィールド内の LF を直接残さない）
- 数式は `$...$` / `$$...$$` で囲む（MathJax）
- ダブルクォートの必須なし（TSV）

例:
```
What is Newton's first law of motion?	Every object remains at rest or in uniform motion unless acted upon by an external force.
What does $E=mc^2$ represent?	Mass–energy equivalence.
```

## 10. ロギングと再現性
- 変換リクエスト/レスポンスの要約を `meta.json` に保存
- 入力 PDF の SHA-256 をキーに成果物を階層格納
- 例外時は `outputs/conversions/<hash>/error/*.log` を残置

## 11. エラーハンドリング方針
- 入力検証（非 PDF/破損/0 バイト）
- API 失敗（ネットワーク, 5xx）: 再試行 + 失敗時は明示的に中断
- 変換出力が空/極端に短い: しきい値で検知して警告

## 12. 性能・スケーラビリティ
- 並列度は CPU コア/IO 帯域に合わせて制御
- `requests.Session` でコネクション再利用
- 大型 PDF はページ範囲オプション（API/CLI が対応している場合）

## 13. セキュリティ・秘匿情報
- API キーやベース URL は `.env` から読み取り（リポジトリ非追跡）
- 実ファイル（PDF）は `.gitignore` 対象

## 14. 検証計画（最小実行）
1) サンプル PDF（講義スライド, 論文 5–10p）で変換→`marker.md` を得る
2) クリーニング→`cleaned.md` 作成
3) チャンク分割→`chunks/`
4) ダミーの Q/A（手書き or 小さな LLM 出力）から `cards.tsv` を生成
5) Anki の GUI でインポート確認（Front/Back マッピング, 数式表示）

## 15. マイルストーン（Member 1）
- Day 1–2: 環境準備（Windows/WSL）・Marker API の疎通
- Day 3–4: 変換クライアント + 出力保存・メタ付与
- Day 5–6: クリーニング/チャンク分割・データ契約確定
- Day 7: TSV Writer と Anki インポート検証・統合テスト

## 16. 完了の定義（DoD）
- 任意の PDF を投入し、`marker.md → cleaned.md → chunks → cards.tsv` まで自動生成
- `cards.tsv` を Anki に手動インポートし、2 種のカード（通常/数式）が正しく表示
- 失敗時ログと再現用アーティファクトが `outputs/conversions/<hash>/` に残る

## 17. 参考（運用 TIPS）
- Windows パス区切りは `pathlib.Path` を使用
- WSL↔Windows のローカルホスト疎通とファイル共有に留意（`/mnt/c/...`）
- 大型 PDF ではまずページ範囲を限定して品質確認→問題なければ全体処理


