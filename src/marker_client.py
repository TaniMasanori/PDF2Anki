import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests


@dataclass
class ConversionResultPaths:
    markdown_path: Path
    meta_path: Path


def compute_sha256(path: Path) -> str:
    sha256 = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def convert_pdf_to_markdown(
    pdf_path: Path,
    api_base_url: str,
    output_root: Path,
    timeout_seconds: int = 120,
    api_convert_path: str = "/convert",
) -> ConversionResultPaths:
    """
    Send a PDF file to Marker API and persist the returned markdown and metadata.

    - pdf_path: input PDF file path
    - api_base_url: e.g. "http://localhost:8000"
    - output_root: base directory to store conversion artifacts
    - api_convert_path: endpoint path (default: /convert)
    """
    pdf_path = pdf_path.resolve()
    output_root = output_root.resolve()

    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Invalid PDF path: {pdf_path}")

    source_sha256 = compute_sha256(pdf_path)
    conv_dir = output_root / "conversions" / source_sha256
    ensure_dir(conv_dir)

    # Copy source for reproducibility (optional: skip large copies if undesired)
    # (We only store hash; user may opt-in to copy the PDF.)

    url = api_base_url.rstrip("/") + api_convert_path
    with pdf_path.open('rb') as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        response = requests.post(url, files=files, timeout=timeout_seconds)

    response.raise_for_status()

    # Assume API returns raw markdown text; adapt if API returns JSON/zip
    markdown_text = response.text

    markdown_path = conv_dir / "marker.md"
    markdown_path.write_text(markdown_text, encoding="utf-8")

    meta = {
        "source_path": str(pdf_path),
        "source_sha256": source_sha256,
        "api_url": url,
        "status_code": response.status_code,
    }
    meta_path = conv_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return ConversionResultPaths(markdown_path=markdown_path, meta_path=meta_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Call Marker API to convert PDF to Markdown")
    parser.add_argument("pdf", type=str, help="Path to PDF file")
    parser.add_argument("--api", type=str, default=os.getenv("MARKER_API_BASE", "http://localhost:8000"), help="Marker API base URL")
    parser.add_argument("--out", type=str, default=str(Path("outputs")), help="Output root directory")
    parser.add_argument("--timeout", type=int, default=120, help="HTTP timeout seconds")
    args = parser.parse_args()

    result = convert_pdf_to_markdown(
        pdf_path=Path(args.pdf),
        api_base_url=args.api,
        output_root=Path(args.out),
        timeout_seconds=args.timeout,
    )
    print(json.dumps({
        "markdown_path": str(result.markdown_path),
        "meta_path": str(result.meta_path)
    }, ensure_ascii=False))


