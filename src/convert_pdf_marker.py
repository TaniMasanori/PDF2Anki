"""
Single CLI to convert a PDF to Markdown using marker-pdf, and write outputs that
align with the conceptual types in section 6.2:

Outputs layout (under --outdir):
  outputs/
    conversions/<pdf_sha256>/
      marker.md             # raw markdown from marker-pdf
      meta.json             # ConversionMeta
      conversion_result.json# ConversionResult

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
from typing import Dict, Iterable, List, Optional, Tuple

# External deps
from pypdf import PdfReader

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore

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



def convert_with_marker(pdf_path: Path) -> Tuple[str, Dict]:
    """
    Convert PDF to Markdown using marker-pdf.
    
    Returns:
        Tuple of (markdown_text, images_dict) where images_dict maps
        filename -> PIL.Image.Image
    """
    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(str(pdf_path))

    # Try common access paths to obtain markdown
    if hasattr(rendered, "markdown"):
        md_text = rendered.markdown  # type: ignore[attr-defined]
        images_dict = getattr(rendered, "images", {})
        return md_text, images_dict

    if 'text_from_rendered' in globals() and text_from_rendered:  # type: ignore
        text, _, images = text_from_rendered(rendered)  # type: ignore
        return text, images if isinstance(images, dict) else {}

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
    md_text, images_dict = convert_with_marker(input_pdf)
    elapsed = time.perf_counter() - t0

    # Write raw markdown
    marker_md_path = conv_dir / "marker.md"
    marker_md_path.write_text(md_text, encoding="utf-8")

    # Save images if any were extracted
    images_saved = 0
    if images_dict:
        for img_name, img_pil in images_dict.items():
            img_path = conv_dir / img_name
            try:
                # Save as JPEG or PNG depending on original name
                if img_name.lower().endswith(('.jpg', '.jpeg')):
                    img_pil.save(img_path, "JPEG")
                elif img_name.lower().endswith('.png'):
                    img_pil.save(img_path, "PNG")
                else:
                    # Default to JPEG for unknown extensions
                    img_pil.save(img_path, "JPEG")
                images_saved += 1
            except Exception as e:
                print(f"WARNING: Failed to save image {img_name}: {e}", file=sys.stderr)

    # cleaned.md generation removed per requirement

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

    # ConversionResult
    result_obj = ConversionResult(
        markdown_path=str(marker_md_path),
        meta_path=str(meta_path),
        images_dir=str(conv_dir) if images_saved > 0 else None,
    )
    result_path = conv_dir / "conversion_result.json"
    result_path.write_text(json.dumps(result_obj.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "markdown_path": str(marker_md_path),
        "meta_path": str(meta_path),
        "conversion_result": str(result_path),
        "images_saved": images_saved,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()


