---
title: Member 1 Implementation Plan & Design (PDF Conversion Pipeline and Integration)
date: 2025-10-02
owner: Member 1 (Alice)
scope: Marker API Setup, Conversion Output Processing, Data Integration to Card Generation, Anki Import Format Preparation, Windows/WSL Support
---

## 1. Purpose and Deliverables
This document outlines the detailed implementation plan and design for Member 1's area of responsibility (PDF conversion pipeline and system integration). The final goal is to complete the following:

- Establish stable operation of PDF→Markdown conversion (Marker API) as the preceding stage for Anki card generation
- Establish standard data models for normalization, chunking, and metadata annotation of conversion results
- Define I/O contracts and API/script interfaces that can be safely passed to the card generation process (LLM)
- Determine formatting and output specifications suitable for Anki import (TSV)
- Ensure stable operation in Windows/WSL environment

## 2. Task List (English/Japanese)
- Environment setup (Windows/WSL) / 実行環境準備（Windows/WSL）
- Install and run Marker API / Marker API の導入と起動方法確立
- Implement conversion HTTP client / 変換クライアント（HTTP）実装
- Normalize and clean conversion output / 出力正規化・クリーニング
- Chunking and metadata design / チャンク分割とメタ情報設計
- Define data contracts (types/JSON schema) / データ契約（型・JSON スキーマ）定義
- Define interface to card generation step / カード生成工程へのインターフェース定義
- Anki TSV spec and writer / Anki 取込フォーマット（TSV）仕様・整形実装
- Logging and reproducibility / ロギング/再現性（チェックポイント保存）
- Integration tests with sample PDFs / 統合テストとサンプル PDF での検証

## 3. Overall Architecture
```mermaid
flowchart LR
  A[PDF Input] --> B[Marker API (PDF->Markdown)]
  B --> C[Cleaner/Normalizer]
  C --> D[Chunker (by section/tokens)]
  D --> E[Card Generation Interface]
  E --> F[TSV Writer]
  F --> G[Anki Manual Import]
```

## 4. Runtime Environment Design (Windows/WSL Local Python Execution)
### 4.1 WSL (Recommended: Ubuntu)
1) Install and initialize Ubuntu WSL from Microsoft Store
2) Install required packages (Python/Build/Utilities)
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip git build-essential python3-dev poppler-utils
   ```
3) Create and update virtual environment
   ```bash
   python3 -m venv ~/.venvs/pdf2anki
   source ~/.venvs/pdf2anki/bin/activate
   python -m pip install --upgrade pip
   ```
4) Clone Marker API and install dependencies (follow repository README)
   ```bash
   git clone https://github.com/adithya-s-k/marker-api.git
   cd marker-api
   pip install -r requirements.txt || true
   pip install -e . || true
   ```
5) Start server (e.g., FastAPI/Uvicorn)
   ```bash
   export PORT=8000
   uvicorn marker_api.app:app --host 0.0.0.0 --port ${PORT}
   ```
6) Verify connectivity
   ```bash
   curl http://localhost:8000/docs || true
   ```
7) Access/share from Windows
   - Browser should open `http://localhost:8000/docs`
   - Windows `C:\Users\<user>\PDF2Anki` is `/mnt/c/Users/<user>/PDF2Anki` in WSL
8) Refer to `docs/20251002_marker_api_setup_wsl.md` for detailed procedures

### 4.2 Windows (Native execution also possible)
1) Install Python 3.10+ (register to PATH)
   - Get Windows installer from https://www.python.org and enable "Add python.exe to PATH"
   - Verify in PowerShell: `python --version` or `py -V`
2) (If needed) Prepare build/native dependencies
   - Some packages may require C/C++ compiler or tools
   - e.g., Install Microsoft C++ Build Tools, Poppler/Ghostscript, etc. (depending on features used)
3) Create and activate virtual environment
   - PowerShell: 
     ```powershell
     py -3.10 -m venv .venv
     .\.venv\Scripts\Activate.ps1
     python -m pip install --upgrade pip
     ```
   - If execution policy error occurs: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
4) Clone Marker API and install dependencies (follow official README)
   ```powershell
   git clone https://github.com/adithya-s-k/marker-api.git
   cd marker-api
   pip install -r requirements.txt
   pip install -e .
   ```
5) Start server (e.g., FastAPI/Uvicorn)
   - PowerShell:
     ```powershell
     $env:PORT=8000
     uvicorn marker_api.app:app --host 0.0.0.0 --port $env:PORT
     ```
   - cmd.exe:
     ```cmd
     set PORT=8000
     uvicorn marker_api.app:app --host 0.0.0.0 --port %PORT%
     ```
6) Verify connectivity (Windows side)
   - Browser: `http://localhost:8000/docs`
   - PowerShell: `curl http://localhost:8000/docs` or `Invoke-WebRequest http://localhost:8000/docs`
7) Note
   - Native Windows execution is possible, but may fail due to dependency build compatibility. Basically recommend WSL execution in 4.1.

(Docker is not used in this project per policy)

## 5. Marker API Usage Design
### 5.1 Endpoints (Assumed)
- POST `/convert` (multipart/form-data, field name `file`) → Markdown text or output archive
- GET `/healthz` or `/` → Health check
- Swagger: `/docs` (specification confirmation)

Note (operational assumptions)
- Actual parameters/responses will be confirmed via `/docs` (OpenAPI). This document assumes default operation (directly returns Markdown).

POST `/convert` Request Specification (Draft)
- Header: `Accept: text/markdown` (default operation to directly receive Markdown text)
- Body: `multipart/form-data`
  - `file`: PDF file (`application/pdf`)
  - Optional parameters (depends on API implementation):
    - `output`: `markdown` | `zip` | `json` (default assumes `markdown`)
    - `pages`: e.g., `1-10` (if page range specification is available)
    - `ocr`: `true|false` (if pre-OCR instruction for scanned PDFs is available)

Response (Draft)
- 200 OK
  - `text/markdown; charset=utf-8` (default)
  - Or `application/zip` / `application/json` (depending on `output`)
- Errors
  - 400 Bad Request (invalid file/missing)
  - 413 Payload Too Large (size exceeded)
  - 415 Unsupported Media Type (invalid content type)
  - 429 Too Many Requests (retry: exponential backoff)
  - 5xx Server Error (save log → abort)

curl execution example (save Markdown directly)
```bash
curl -fS -X POST "http://localhost:8000/convert" \
  -H "Accept: text/markdown" \
  -F "file=@/mnt/c/Users/<user>/PDF2Anki/sample.pdf;type=application/pdf" \
  --max-time 120 \
  -o marker.md
```

Python requests execution example (consistent with `src/marker_client.py`)
```python
import requests

url = "http://localhost:8000/convert"
with open("/mnt/c/Users/<user>/PDF2Anki/sample.pdf", "rb") as f:
    files = {"file": ("sample.pdf", f, "application/pdf")}
    resp = requests.post(url, files=files, headers={"Accept": "text/markdown"}, timeout=120)
resp.raise_for_status()
markdown_text = resp.text
```

Health Check
- Use `GET /healthz` or `GET /` returning 200 as the startup determination criterion.


Actual endpoint names and response formats should be confirmed via `/docs`, and types should be fixed on the client side.

### 5.2 Timeout and Retry Policy
- Initial timeout value: 120s (consideration for large PDFs)
- Retry up to 3 times with exponential backoff for 429/5xx
- On exception, save evidence (log/response) with hash name of input PDF

## 6. Data Flow and Data Contracts
### 6.1 Directory Structure (Proposal)
```
PDF2Anki/
  docs/
  src/               # Implementation (to be done later)
  outputs/
    conversions/<pdf_hash>/
      source.pdf
      marker.md            # Converted Markdown (UTF-8)
      meta.json            # Version/elapsed seconds/page count, etc.
      cleaned.md           # After cleaning
      chunks/
        chunk_0001.md
        ...
      cards.tsv            # Anki import file (after generation)
```

### 6.2 Types (Conceptual Design)
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
  id: str,                  # e.g., chunk_0001
  text: str,
  start_page?: int,
  end_page?: int,
  section_title?: str,
  token_count: int,
  source_ref: { pdf_sha256: str, chunk_id: str }
}

```

## 7. Cleaning and Chunking
### 7.1 Cleaning
- Format excess line breaks and consecutive whitespace
- Remove repetitive headers/footers (page numbers, etc.)
- Preserve mathematical expressions `$...$` / `$$...$$` (Anki MathJax assumption)
- Image references (`![]()`) are either retained or removed based on policy if unused in card generation

### 7.2 Chunking (Priority Order)
1) Split by section headings (`#`, `##`, etc.)
2) Split by token count limit (e.g., ~2k tokens)
3) Store chapter/section structure metadata in `Chunk.section_title`

## 8. Interface to Card Generation Process
The LLM side is handled by Member 2, but the handoff contract is defined:

- Input: Pass `chunks/*.md` one chunk at a time. Also provide `prompt_parameters.json` (e.g., number of cards to generate, style)
- Output: `cards.jsonl` (1 card per line, `Card` type) or `cards.tsv`
- On error: `errors.log` with chunk ID and message

Maintain abstraction for future expansion to AnkiConnect direct send or `.apkg` generation (genanki).

## 9. Anki Import Format Specification (TSV)
- Delimiter: Tab (`\t`)
- Encoding: UTF-8 (BOM-less recommended)
- 1 line = 1 card, columns: `Front\tBack`
- Normalize line breaks to `<br>` (don't leave LF directly in fields)
- Mathematical expressions enclosed with `$...$` / `$$...$$` (MathJax)
- Double quotes not mandatory (TSV)

Example:
```
What is Newton's first law of motion?	Every object remains at rest or in uniform motion unless acted upon by an external force.
What does $E=mc^2$ represent?	Mass–energy equivalence.
```

## 10. Logging and Reproducibility
- Save summary of conversion request/response in `meta.json`
- Store artifacts hierarchically keyed by input PDF's SHA-256
- On exception, leave `outputs/conversions/<hash>/error/*.log`

## 11. Error Handling Policy
- Input validation (non-PDF/corrupted/0 bytes)
- API failure (network, 5xx): Retry + explicitly abort on failure
- Conversion output is empty/extremely short: Detect with threshold and warn

## 12. Performance and Scalability
- Control parallelism according to CPU cores/IO bandwidth
- Reuse connections with `requests.Session`
- For large PDFs, use page range option (if API/CLI supports it)

## 13. Security and Confidential Information
- Read API keys and base URL from `.env` (not tracked in repository)
- Actual files (PDFs) are subject to `.gitignore`

## 14. Verification Plan (Minimum Execution)
1) Convert sample PDF (lecture slides, 5–10 page paper) → get `marker.md`
2) Clean → create `cleaned.md`
3) Chunk → `chunks/`
4) Generate `cards.tsv` from dummy Q/A (handwritten or small LLM output)
5) Verify import in Anki GUI (Front/Back mapping, mathematical expression display)

## 15. Milestones (Member 1)
- Day 1–2: Environment preparation (Windows/WSL) and Marker API connectivity
- Day 3–4: Conversion client + output save and metadata annotation
- Day 5–6: Cleaning/chunking and data contract finalization
- Day 7: TSV Writer and Anki import verification, integration testing

## 16. Definition of Done (DoD)
- Input any PDF and automatically generate from `marker.md → cleaned.md → chunks → cards.tsv`
- Manually import `cards.tsv` into Anki and verify that 2 types of cards (regular/mathematical) display correctly
- Failure logs and reproducible artifacts remain in `outputs/conversions/<hash>/`

## 17. Reference (Operational TIPS)
- Use `pathlib.Path` for Windows path separators
- Pay attention to WSL↔Windows localhost connectivity and file sharing (`/mnt/c/...`)
- For large PDFs, first limit page range to verify quality → process entire document if no issues


