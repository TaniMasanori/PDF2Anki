import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    max_retries: int = 3,
) -> ConversionResultPaths:
    """
    Send a PDF file to Marker API and persist the returned markdown and metadata.

    - pdf_path: input PDF file path
    - api_base_url: e.g. "http://localhost:8000"
    - output_root: base directory to store conversion artifacts
    - api_convert_path: endpoint path (default: /convert)
    - max_retries: maximum number of retry attempts for 429/5xx errors
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
    logger.info(f"Converting PDF: {pdf_path.name} (SHA256: {source_sha256})")
    
    # Retry logic with exponential backoff
    retry_count = 0
    last_exception = None
    
    while retry_count <= max_retries:
        try:
            with pdf_path.open('rb') as f:
                files = {"file": (pdf_path.name, f, "application/pdf")}
                headers = {"Accept": "application/json"}
                
                logger.info(f"Sending request to {url} (attempt {retry_count + 1}/{max_retries + 1})")
                response = requests.post(
                    url, 
                    files=files, 
                    headers=headers,
                    timeout=timeout_seconds
                )

            # Check for retriable status codes
            if response.status_code in [429, 500, 502, 503, 504]:
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"Received status {response.status_code}. "
                        f"Retrying in {wait_time}s... (attempt {retry_count + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                    retry_count += 1
                    continue
                else:
                    # Save error evidence
                    error_path = conv_dir / "error.log"
                    error_data = {
                        "status_code": response.status_code,
                        "response_text": response.text[:1000],  # First 1000 chars
                        "attempts": retry_count + 1,
                    }
                    error_path.write_text(json.dumps(error_data, ensure_ascii=False, indent=2), encoding="utf-8")
                    logger.error(f"Max retries exceeded. Error log saved to {error_path}")
                    response.raise_for_status()

            # Success case
            response.raise_for_status()
            break

        except requests.exceptions.RequestException as e:
            last_exception = e
            if retry_count < max_retries:
                wait_time = 2 ** retry_count
                logger.warning(f"Request failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                retry_count += 1
            else:
                # Save error evidence
                error_path = conv_dir / "error.log"
                error_data = {
                    "error": str(e),
                    "exception_type": type(e).__name__,
                    "attempts": retry_count + 1,
                }
                error_path.write_text(json.dumps(error_data, ensure_ascii=False, indent=2), encoding="utf-8")
                logger.error(f"Max retries exceeded. Error log saved to {error_path}")
                raise

    # API returns JSON with structure: {"status": "Success", "result": {"markdown": "...", ...}}
    try:
        response_json = response.json()
        if response_json.get("status") == "Success" and "result" in response_json:
            markdown_text = response_json["result"].get("markdown", "")
        else:
            # Fallback: try to use response text directly
            markdown_text = response.text
            logger.warning(f"Unexpected API response format: {response_json}")
    except (json.JSONDecodeError, KeyError) as e:
        # Fallback: use response text if JSON parsing fails
        logger.warning(f"Failed to parse JSON response: {e}. Using response text.")
        markdown_text = response.text

    markdown_path = conv_dir / "marker.md"
    markdown_path.write_text(markdown_text, encoding="utf-8")
    logger.info(f"Markdown saved to {markdown_path}")

    meta = {
        "source_path": str(pdf_path),
        "source_sha256": source_sha256,
        "api_url": url,
        "status_code": response.status_code,
        "retry_count": retry_count,
    }
    meta_path = conv_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Metadata saved to {meta_path}")

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


