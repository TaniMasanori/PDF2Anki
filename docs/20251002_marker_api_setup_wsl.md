---
title: Marker API セットアップ手順（WSL）
date: 2025-10-02
---

本ドキュメントは WSL (Ubuntu) 上で Marker API をローカルサービスとして実行するための最小ステップを示す。コードコメント等は英語で記載する前提。

## 1. 前提
- Windows 11 + WSL (Ubuntu)
- Anki Desktop は Windows 側にインストール

## 2. WSL 初期化と Python 環境
```bash
wsl --install -d Ubuntu   # 既に導入済みなら不要
# Ubuntu ターミナル内
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git
python3 --version
python3 -m venv ~/.venvs/pdf2anki
source ~/.venvs/pdf2anki/bin/activate
python -m pip install --upgrade pip
```

## 3. Marker API の取得とインストール
Marker API の最新版手順に従う（リポジトリ README を参照）。以下は一般的な例。
```bash
# 例: リポジトリを取得
git clone https://github.com/adithya-s-k/marker-api.git
cd marker-api

# 依存インストール（プロジェクト推奨の方法に従う）
pip install -r requirements.txt || true
pip install -e . || true
```

注意: 実際の依存名や起動方法は upstream の README に従うこと。PyMuPDF などのネイティブ依存が必要な場合がある。

## 4. サーバ起動（例）
FastAPI/Uvicorn ベースの場合の一般例。実際のエントリポイントはリポジトリに従う。
```bash
export PORT=8000
uvicorn marker_api.app:app --host 0.0.0.0 --port ${PORT}
# 別ターミナルで動作確認
curl http://localhost:${PORT}/docs || true
```

## 5. Windows からのアクセス
- Windows 側ブラウザで `http://localhost:8000/docs` にアクセス可能なこと
- ファイル共有: Windows の `C:\Users\<user>\PDF2Anki` は WSL では `/mnt/c/Users/<user>/PDF2Anki`

## 6. トラブルシュート
- ポートが占有: `lsof -i :8000`（WSL）で確認しプロセス停止
- 依存のビルド失敗: `build-essential`, `python3-dev`, `poppler-utils` 等を追加
  ```bash
  sudo apt install -y build-essential python3-dev poppler-utils
  ```
- 変換が失敗: PDF がスキャン画像の場合 OCR が必要。別途 OCR 前処理を検討

## 7. 次のステップ
- クライアントスクリプトから `/convert` にファイル送信
- 出力の保存・正規化・チャンク分割に進む


