---
title: Marker API 404エラー修正
date: 2025-11-06
---

# Marker API 404エラー修正

## 問題

StreamlitアプリからPDFをMarkdownに変換しようとした際に、以下のエラーが発生していました：

```
❌ Error converting PDF: 404 Client Error: Not Found for url: http://localhost:8888/convert
```

## 原因

1. **ルーティングの順序問題**: `marker-api/server.py`で、Gradioアプリをルートパス（`path=""`）にマウントした後にFastAPIエンドポイントを定義していたため、Gradioがすべてのルートをキャッチしていました。

2. **レスポンス形式の不一致**: `marker_client.py`がAPIレスポンスをテキストとして扱っていましたが、実際のAPIはJSON形式（`{"status": "Success", "result": {"markdown": "...", ...}}`）を返していました。

## 修正内容

### 1. `marker-api/server.py`の修正

- FastAPIエンドポイント（`/health`, `/convert`, `/batch_convert`）をGradioマウントの**前に**定義
- Gradioアプリのマウントパスを`path=""`から`path="/gradio"`に変更して、FastAPIルートとの競合を回避

```python
# FastAPIエンドポイントを先に定義
@app.get("/health", ...)
@app.post("/convert", ...)
@app.post("/batch_convert", ...)

# その後でGradioをマウント
app = gr.mount_gradio_app(app, demo_ui, path="/gradio")
```

### 2. `src/marker_client.py`の修正

- JSONレスポンスを正しく解析するように変更
- `response.json()`を使用してJSONを解析し、`result.markdown`を取得
- フォールバック処理を追加（JSON解析に失敗した場合はテキストを使用）
- Acceptヘッダーを`text/markdown`から`application/json`に変更

```python
# JSONレスポンスを解析
response_json = response.json()
if response_json.get("status") == "Success" and "result" in response_json:
    markdown_text = response_json["result"].get("markdown", "")
```

## 動作確認

修正後、以下の手順で動作確認してください：

1. Marker APIサーバーを起動（ポート8888で起動している場合）:
   ```bash
   cd /home/masan/PDF2Anki/marker-api
   source .venv/bin/activate
   python server.py --host 0.0.0.0 --port 8888
   ```

2. Streamlitアプリを起動:
   ```bash
   cd /home/masan/PDF2Anki
   ./run_streamlit.sh
   ```

3. Streamlit UIのサイドバーで、Marker API URLを`http://localhost:8888`に設定

4. PDFをアップロードして「Convert to Markdown」ボタンをクリック

## 注意事項

- Marker APIサーバーはポート8888で起動している場合、Streamlitアプリの設定も`http://localhost:8888`に合わせる必要があります
- デフォルトのポート8000を使用する場合は、`.env`ファイルに`MARKER_API_BASE=http://localhost:8000`を設定してください
- Gradio UIは`http://localhost:8888/gradio`でアクセス可能です

## 関連ファイル

- `marker-api/server.py`: FastAPIサーバーのルーティング設定
- `src/marker_client.py`: Marker APIクライアントの実装
- `src/streamlit_app.py`: Streamlit UIの実装

