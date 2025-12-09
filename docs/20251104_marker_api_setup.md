---
title: Marker API 起動と URL 設定ガイド
date: 2025-11-04
---

# Marker API 起動と URL 設定ガイド

本書は PDF2Anki から利用する Marker API の「ローカル起動手順」と「URL 設定方法」をまとめたものです。WSL2（Ubuntu）環境を前提にしています。

## 前提条件

- Python 3.10 以上
- 本リポジトリをクローン済み（`/home/masan/PDF2Anki`）
- WSL2 上で実行（Windows からは `http://localhost:<port>` でアクセス可能）

## 起動方法（シンプルサーバ）

最も簡単な構成です。単一プロセスで `/convert` を提供します。

1. ディレクトリ移動と（任意で）仮想環境作成

```bash
cd /home/masan/PDF2Anki/marker-api
python3 -m venv .venv && source .venv/bin/activate  # 任意
python -m pip install -U pip
```

2. 依存関係インストール（開発インストール）

```bash
pip install -e .
```

3. サーバ起動（例: ポート 8000）

```bash
python server.py --host 0.0.0.0 --port 8000
```

4. 動作確認

- ヘルスチェック: `http://localhost:8000/health`
- API ドキュメント: `http://localhost:8000/docs`
- cURL テスト（JSON 返却。`/convert` は multipart/form-data の `file` フィールドで PDF を送信）:

```bash
curl -s -X POST \
  http://localhost:8000/convert \
  -F "file=@/absolute/path/to/sample.pdf" | jq . | head
```

> 初回実行時はモデル類のダウンロードで時間がかかる場合があります。

## PDF2Anki 側の URL 設定

どちらか一方で設定してください。

- `.env` に記載（推奨）:

```bash
echo "MARKER_API_BASE=http://localhost:8000" >> /home/masan/PDF2Anki/.env
```

- Streamlit UI 側バーで設定: アプリ起動後、`Marker API URL` に `http://localhost:8000` を入力

コード上の参照箇所:

```124:131:/home/masan/PDF2Anki/src/streamlit_app.py
        st.subheader("Marker API")
        marker_api_url = st.text_input(
            "Marker API URL",
            value=os.getenv("MARKER_API_BASE", "http://localhost:8000"),
            help="URL of the Marker API server"
        )
```

```158:163:/home/masan/PDF2Anki/src/marker_client.py
    parser.add_argument("--api", type=str, default=os.getenv("MARKER_API_BASE", "http://localhost:8000"), help="Marker API base URL")
    parser.add_argument("--out", type=str, default=str(Path("outputs")), help="Output root directory")
    parser.add_argument("--timeout", type=int, default=120, help="HTTP timeout seconds")
    args = parser.parse_args()
```

> 注意: `marker-api/server.py` のデフォルトポートは 8080 です。本ガイドでは PDF2Anki のデフォルト（8000）に合わせ、起動引数 `--port 8000` を指定しています。8080 で起動したい場合は `.env` の `MARKER_API_BASE` を `http://localhost:8080` に変更してください。

## 既知の挙動とヒント

- `/convert` のレスポンスは JSON（`{"status": "Success", "result": {...}}`）です。将来的に `text/markdown` 返却へ切替える場合はクライアント側も合わせて更新してください。
- 初回起動時はモデルのダウンロードに時間がかかります。ネットワーク環境に応じて時間とディスク容量に余裕を持って実行してください。
- エラー時は以下を確認:
  - サーバが起動しているか（ポート・プロセス）
  - `MARKER_API_BASE` と実サーバのポートが一致しているか
  - WSL/Windows 間のファイアウォール設定

## 参考情報

- 詳細なオプションや分散構成（Celery/Redis）は `marker-api/README.md` を参照してください。
- 本プロジェクトの環境変数全般は `docs/env_setup.md` を参照してください。


