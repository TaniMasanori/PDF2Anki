# README.md修正と環境セットアップガイド

日付: 2024-12-04

## 概要

このセッションでは、README.mdの問題点を修正し、プロジェクトのセットアップ手順を検証しました。

## 修正内容

### 1. サーバーファイル名の修正
- **変更前**: `marker_server.py`
- **変更後**: `server.py`
- marker-apiの実際のファイル名に合わせて修正

### 2. デフォルトポートの統一
- **変更前**: 8000, 8888（混在）
- **変更後**: 8080（marker-apiのデフォルト）
- `.env`ファイル、起動コマンド、トラブルシューティングセクション全てを統一

### 3. OpenAIモデル名の修正
- **変更前**: `gpt-5-mini`（存在しないモデル）
- **変更後**: `gpt-4o-mini`（正しいモデル名）

### 4. Conda環境のインストール手順追加
- venvに加えて、Condaを使用したインストール方法を推奨オプションとして追加
- WSL環境での互換性問題を回避するため

### 5. transformersバージョン互換性の修正
- `KeyError: 'sdpa'`エラーの解決方法を追加
- `pip install transformers==4.41.0`の実行が必要

### 6. トラブルシューティングセクションの追加
- `KeyError: 'sdpa'`エラーの解決方法を新規追加

## 環境セットアップ手順（検証済み）

### 1. Conda環境の作成
```bash
conda create -n pdf2anki python=3.11 -y
conda activate pdf2anki
```

### 2. marker-apiのインストール
```bash
cd marker-api
pip install -e .
pip install transformers==4.41.0  # 重要！
```

### 3. marker-apiサーバーの起動
```bash
cd marker-api
conda activate pdf2anki
python server.py --host 0.0.0.0 --port 8080
```

### 4. Streamlitアプリの起動（別ターミナル）
```bash
cd PDF2Anki
conda activate pdf2anki
streamlit run src/streamlit_app.py
```

## アクセスURL
- Marker API: http://localhost:8080
- Marker API Health Check: http://localhost:8080/health
- Streamlit App: http://localhost:8501

## 発見された問題と解決策

| 問題 | 原因 | 解決策 |
|------|------|--------|
| `KeyError: 'sdpa'` | transformers 4.48.xとsurya-ocr 0.5.0の互換性問題 | `pip install transformers==4.41.0` |
| WSLでvenv作成失敗 | Windowsマウントポイントでの制限 | Condaを使用 |
| `ModuleNotFoundError: No module named 'marker'` | marker-pdfがインストールされていない | `pip install -e .`をmarker-apiディレクトリで実行 |

## コミット情報

```
ea6c7f3 fix: Update README.md with correct server file name, port, and model names
```

