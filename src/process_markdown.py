"""
Main CLI for processing markdown files from PDF conversion.

This module provides the command-line interface for cleaning and chunking
markdown files produced by Member 1's PDF conversion pipeline.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from domain_types import ConversionMeta
from markdown_chunker import chunk_markdown
from markdown_cleaner import clean_markdown
from semantic_detector import identify_semantic_structures


def load_meta(meta_path: Path) -> Optional[dict]:
    """
    Load metadata from meta.json file.
    
    Args:
        meta_path: Path to meta.json file
    
    Returns:
        Dictionary with metadata, or None if file doesn't exist or is invalid
    """
    if not meta_path.exists():
        return None
    
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"WARNING: Failed to load meta.json: {e}", file=sys.stderr)
        return None


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Process markdown from PDF conversion: clean and chunk for flashcard generation"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input marker.md file (or directory containing marker.md)"
    )
    parser.add_argument(
        "--outdir",
        help="Output directory (default: same as input directory)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2000,
        help="Maximum tokens per chunk (default: 2000)"
    )
    parser.add_argument(
        "--remove-images",
        action="store_true",
        help="Remove image references from markdown"
    )
    parser.add_argument(
        "--save-chunk-files",
        action="store_true",
        help="Save individual chunk files in chunks/ directory"
    )
    
    args = parser.parse_args()
    
    # Resolve input path
    input_path = Path(args.input).expanduser().resolve()
    
    # Determine marker.md path
    if input_path.is_file() and input_path.name == "marker.md":
        marker_md_path = input_path
        conv_dir = input_path.parent
    elif input_path.is_dir():
        marker_md_path = input_path / "marker.md"
        conv_dir = input_path
    else:
        print(f"ERROR: Invalid input path: {input_path}", file=sys.stderr)
        print("Expected: path to marker.md file or directory containing marker.md", file=sys.stderr)
        sys.exit(1)
    
    if not marker_md_path.exists():
        print(f"ERROR: marker.md not found: {marker_md_path}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output directory
    if args.outdir:
        out_dir = Path(args.outdir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = conv_dir
    
    # Load metadata
    meta_path = conv_dir / "meta.json"
    meta = load_meta(meta_path)
    pdf_sha256 = meta.get("source_sha256") if meta else None
    
    if not pdf_sha256:
        # Try to extract from directory name (conversions/<sha256>/)
        if "conversions" in conv_dir.parts:
            try:
                sha256_idx = conv_dir.parts.index("conversions")
                if sha256_idx + 1 < len(conv_dir.parts):
                    pdf_sha256 = conv_dir.parts[sha256_idx + 1]
            except (ValueError, IndexError):
                pass
        
        if not pdf_sha256:
            print("WARNING: Could not determine PDF SHA256. Using placeholder.", file=sys.stderr)
            pdf_sha256 = "unknown"
    
    # Read markdown
    print(f"Reading markdown from: {marker_md_path}", file=sys.stderr)
    try:
        raw_markdown = marker_md_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR: Failed to read markdown file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Step 1: Clean markdown
    print("Cleaning markdown...", file=sys.stderr)
    cleaning_result = clean_markdown(raw_markdown, remove_images=args.remove_images)
    
    # Save cleaned markdown
    cleaned_md_path = out_dir / "cleaned.md"
    cleaned_md_path.write_text(cleaning_result.cleaned_text, encoding='utf-8')
    print(f"Saved cleaned markdown to: {cleaned_md_path}", file=sys.stderr)
    
    # Step 2: Chunk markdown
    print(f"Chunking markdown (max_tokens={args.max_tokens})...", file=sys.stderr)
    chunking_result = chunk_markdown(
        cleaning_result.cleaned_text,
        pdf_sha256=pdf_sha256,
        max_tokens=args.max_tokens
    )
    
    # Save chunks.jsonl
    chunks_jsonl_path = out_dir / "chunks.jsonl"
    with open(chunks_jsonl_path, 'w', encoding='utf-8') as f:
        for chunk in chunking_result.chunks:
            # Convert Chunk to dict for JSON serialization
            chunk_dict = {
                "id": chunk.id,
                "text": chunk.text,
                "token_count": chunk.token_count,
                "source_ref": {
                    "pdf_sha256": chunk.source_ref.pdf_sha256,
                    "chunk_id": chunk.source_ref.chunk_id
                },
                "start_page": chunk.start_page,
                "end_page": chunk.end_page,
                "section_title": chunk.section_title
            }
            f.write(json.dumps(chunk_dict, ensure_ascii=False) + "\n")
    
    print(f"Saved {chunking_result.total_chunks} chunks to: {chunks_jsonl_path}", file=sys.stderr)
    
    # Step 3: Optionally save individual chunk files
    if args.save_chunk_files:
        chunks_dir = out_dir / "chunks"
        chunks_dir.mkdir(exist_ok=True)
        for chunk in chunking_result.chunks:
            chunk_file_path = chunks_dir / f"{chunk.id}.md"
            chunk_file_path.write_text(chunk.text, encoding='utf-8')
        print(f"Saved individual chunk files to: {chunks_dir}", file=sys.stderr)
    
    # Step 4: Identify semantic structures (optional, for metadata)
    semantic_data = {}
    for chunk in chunking_result.chunks[:10]:  # Limit to first 10 chunks for performance
        semantic_data[chunk.id] = identify_semantic_structures(chunk)
    
    # Step 5: Create processing result summary
    processing_result = {
        "cleaned_md_path": str(cleaned_md_path),
        "chunks_jsonl_path": str(chunks_jsonl_path),
        "total_chunks": chunking_result.total_chunks,
        "total_tokens": chunking_result.total_tokens,
        "avg_tokens_per_chunk": round(chunking_result.total_tokens / chunking_result.total_chunks, 2) if chunking_result.total_chunks > 0 else 0,
        "cleaning_stats": cleaning_result.stats,
        "semantic_structures_sample": semantic_data  # Sample from first 10 chunks
    }
    
    result_path = out_dir / "processing_result.json"
    result_path.write_text(
        json.dumps(processing_result, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"Saved processing result to: {result_path}", file=sys.stderr)
    
    # Print summary to stdout (JSON for programmatic use)
    print(json.dumps({
        "cleaned_md_path": str(cleaned_md_path),
        "chunks_jsonl_path": str(chunks_jsonl_path),
        "processing_result_path": str(result_path),
        "total_chunks": chunking_result.total_chunks,
        "total_tokens": chunking_result.total_tokens
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

