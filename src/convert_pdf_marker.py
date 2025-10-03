"""
Single CLI to convert a PDF to Markdown using marker-pdf, and write outputs that
align with the conceptual types in section 6.2:

ConversionMeta, ConversionResult, and Chunk (chunked markdown files + jsonl).

Outputs layout (under --outdir):
  outputs/
    conversions/<pdf_sha256>/
      marker.md             # raw markdown from marker-pdf
      cleaned.md            # cleaned markdown
      meta.json             # ConversionMeta
      conversion_result.json# ConversionResult
      chunks/
        chunk_0001.md
        ...
      chunks.jsonl          # one JSON object per line for Chunk

Usage:
  python src/convert_pdf_marker.py --input /path/to/input.pdf --outdir outputs
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

# External deps
from pypdf import PdfReader

try:
    # marker-pdf API (commonly imported as "marker")
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    # Some versions expose text via rendered.markdown; others via output utils
    try:
        from marker.output import text_from_rendered  # type: ignore
    except Exception:  # pragma: no cover
        text_from_rendered = None  # type: ignore
except Exception as exc:  # pragma: no cover
    print("ERROR: marker-pdf is required. Please `pip install marker-pdf`.", file=sys.stderr)
    raise


@dataclass
class ConversionMeta:
    source_path: str
    source_sha256: str
    pages: int
    engine: dict
    elapsed_sec: float
    created_at: str  # ISO 8601


@dataclass
class ConversionResult:
    markdown_path: str
    meta_path: str
    images_dir: Optional[str] = None


def compute_sha256(path: Path) -> str:
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def read_pdf_pages(path: Path) -> int:
    try:
        reader = PdfReader(str(path))
        return len(reader.pages)
    except Exception:
        return 0


def clean_markdown(md: str) -> str:
    # Minimal cleanup: normalize line endings, collapse 3+ newlines to 2, trim trailing spaces
    text = md.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def split_by_headings(md: str) -> List[Tuple[str, str]]:
    """
    Split markdown by top-level headings (#..######). Returns list of (title, body).
    If no headings, return single chunk.
    """
    lines = md.splitlines()
    chunks: List[Tuple[str, List[str]]] = []
    current_title = ""
    current_body: List[str] = []

    heading_re = re.compile(r"^(#{1,6})\s+(.*)")
    for line in lines:
        m = heading_re.match(line)
        if m:
            # flush previous
            if current_title or current_body:
                chunks.append((current_title, current_body))
                current_body = []
            current_title = m.group(2).strip()
        else:
            current_body.append(line)
    # flush last
    if current_title or current_body:
        chunks.append((current_title, current_body))

    if not chunks:
        return [("", md)]
    return [(title, "\n".join(body).strip() + "\n") for title, body in chunks]


def count_tokens_approx(text: str) -> int:
    # Simple approximation: count word-like tokens
    return len(re.findall(r"\w+", text))


def write_chunks(
    base_dir: Path,
    pdf_sha256: str,
    cleaned_md: str,
) -> None:
    chunks_dir = base_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    pieces = split_by_headings(cleaned_md)
    jsonl_path = base_dir / "chunks.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as jf:
        for idx, (title, body) in enumerate(pieces, start=1):
            chunk_id = f"chunk_{idx:04d}"
            chunk_path = chunks_dir / f"{chunk_id}.md"
            chunk_path.write_text(body, encoding="utf-8")

            chunk_obj = {
                "id": chunk_id,
                "text": body,
                "start_page": None,
                "end_page": None,
                "section_title": title or None,
                "token_count": count_tokens_approx(body),
                "source_ref": {"pdf_sha256": pdf_sha256, "chunk_id": chunk_id},
            }
            jf.write(json.dumps(chunk_obj, ensure_ascii=False) + "\n")


def convert_with_marker(pdf_path: Path) -> Tuple[str, Optional[str]]:
    """Return (markdown_text, images_dir?)."""
    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(str(pdf_path))

    # Try common access paths to obtain markdown
    if hasattr(rendered, "markdown"):
        md_text = rendered.markdown  # type: ignore[attr-defined]
        images_dir = getattr(rendered, "images_dir", None)
        return md_text, images_dir

    if 'text_from_rendered' in globals() and text_from_rendered:  # type: ignore
        text, _, images = text_from_rendered(rendered)  # type: ignore
        return text, images

    raise RuntimeError("Unsupported marker-pdf output structure; please update code for your version.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown with marker-pdf and write meta/chunks")
    parser.add_argument("--input", required=True, help="Path to input PDF")
    parser.add_argument("--outdir", default="outputs", help="Root output directory (default: outputs)")
    args = parser.parse_args()

    input_pdf = Path(args.input).expanduser().resolve()
    if not input_pdf.exists() or input_pdf.suffix.lower() != ".pdf":
        print(f"ERROR: invalid input PDF: {input_pdf}", file=sys.stderr)
        sys.exit(2)

    out_root = Path(args.outdir).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    pdf_sha256 = compute_sha256(input_pdf)
    pages = read_pdf_pages(input_pdf)

    conv_dir = out_root / "conversions" / pdf_sha256
    conv_dir.mkdir(parents=True, exist_ok=True)

    # Convert
    engine_name = "marker-pdf"
    try:
        engine_version = metadata.version("marker-pdf")
    except Exception:
        # Fallback to try alternative dist name
        try:
            engine_version = metadata.version("marker")
        except Exception:
            engine_version = "unknown"

    t0 = time.perf_counter()
    md_text, images_dir = convert_with_marker(input_pdf)
    elapsed = time.perf_counter() - t0

    # Write raw markdown
    marker_md_path = conv_dir / "marker.md"
    marker_md_path.write_text(md_text, encoding="utf-8")

    # Clean and write cleaned markdown
    cleaned = clean_markdown(md_text)
    cleaned_md_path = conv_dir / "cleaned.md"
    cleaned_md_path.write_text(cleaned, encoding="utf-8")

    # Meta (ConversionMeta)
    meta_obj = ConversionMeta(
        source_path=str(input_pdf),
        source_sha256=pdf_sha256,
        pages=pages,
        engine={"name": engine_name, "version": engine_version},
        elapsed_sec=elapsed,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    meta_path = conv_dir / "meta.json"
    meta_path.write_text(json.dumps(meta_obj.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write chunks and chunk jsonl
    write_chunks(conv_dir, pdf_sha256, cleaned)

    # ConversionResult
    result_obj = ConversionResult(
        markdown_path=str(marker_md_path),
        meta_path=str(meta_path),
        images_dir=images_dir,
    )
    result_path = conv_dir / "conversion_result.json"
    result_path.write_text(json.dumps(result_obj.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "markdown_path": str(marker_md_path),
        "cleaned_markdown_path": str(cleaned_md_path),
        "meta_path": str(meta_path),
        "chunks_dir": str(conv_dir / "chunks"),
        "chunks_index": str(conv_dir / "chunks.jsonl"),
        "conversion_result": str(result_path),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()


