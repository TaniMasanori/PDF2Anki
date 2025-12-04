# Marker API Endpoint Fix - 2024/12/04

## Overview / 概要

This document describes the fixes applied to resolve the 404 error when connecting to the Marker API server.

このドキュメントは、Marker APIサーバーへの接続時に発生した404エラーを解決するために適用された修正について説明します。

## Problem / 問題

When attempting to convert PDFs using the Streamlit app, the following errors occurred:

PDFをStreamlitアプリで変換しようとした際、以下のエラーが発生しました：

1. `404 Client Error: Not Found for url: http://localhost:8000/marker/upload`
2. `404 Client Error: Not Found for url: http://localhost:8080/marker/upload`
3. `404 Client Error: Not Found for url: http://localhost:8080/convert`

## Root Causes / 原因

### 1. Incorrect API Endpoint / 不正なAPIエンドポイント

The `marker_client.py` was using `/marker/upload` as the endpoint, but the marker-api server uses `/convert`.

`marker_client.py`は`/marker/upload`をエンドポイントとして使用していましたが、marker-apiサーバーは`/convert`を使用しています。

### 2. Incorrect Parameter Name / 不正なパラメータ名

The file upload parameter was named `file`, but the API expects `pdf_file`.

ファイルアップロードのパラメータ名が`file`でしたが、APIは`pdf_file`を期待しています。

### 3. Gradio App Overriding Routes / GradioアプリによるルートのOverride

The Gradio demo UI was mounted at root path `""`, which intercepted all FastAPI routes including `/convert` and `/health`.

GradioデモUIがルートパス`""`にマウントされており、`/convert`や`/health`を含むすべてのFastAPIルートをインターセプトしていました。

## Fixes Applied / 適用された修正

### 1. `src/marker_client.py`

```python
# Changed endpoint from /marker/upload to /convert
api_convert_path: str = "/convert"  # was "/marker/upload"

# Changed parameter name from file to pdf_file
files = {"pdf_file": (pdf_path.name, f, "application/pdf")}  # was "file"

# Changed default port from 8000 to 8080
default=os.getenv("MARKER_API_BASE", "http://localhost:8080")  # was 8000
```

### 2. `src/streamlit_app.py`

```python
# Changed default port from 8000 to 8080
value=os.getenv("MARKER_API_BASE", "http://localhost:8080")  # was 8000
```

### 3. `marker-api/server.py`

```python
# Changed Gradio mount path from "" to "/gradio"
app = gr.mount_gradio_app(app, demo_ui, path="/gradio")  # was path=""
```

## Verification / 検証

After applying these fixes:

これらの修正を適用後：

1. Health endpoint works: `curl http://localhost:8080/health`
   - Returns: `{"message":"Welcome to Marker-api","type":"simple","workers":null}`

2. PDF conversion works through Streamlit app at `http://localhost:8501` or `http://localhost:8503`

3. Gradio demo UI is accessible at `http://localhost:8080/gradio`

## Notes / 備考

- The marker-api submodule was modified locally. If updating the submodule, this fix may need to be reapplied.
- marker-apiサブモジュールはローカルで修正されました。サブモジュールを更新する場合、この修正を再適用する必要がある可能性があります。

