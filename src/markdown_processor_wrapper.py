"""
Wrapper module to integrate newly ingested markdown processing scripts
into the Streamlit application without modifying the original scripts.

This module provides functions that bridge domain_types and pdf2anki_types,
and wraps the markdown cleaning, chunking, and semantic detection functions.
"""

from typing import List, Optional
from pathlib import Path
import json

# Import new scripts (they use domain_types)
from markdown_cleaner import clean_markdown as _clean_markdown
from markdown_chunker import chunk_markdown as _chunk_markdown
from semantic_detector import identify_semantic_structures as _identify_semantic_structures

# Import existing types (pdf2anki_types)
from pdf2anki_types import Chunk as PdfAnkiChunk, ChunkingResult as PdfAnkiChunkingResult, SourceReference as PdfAnkiSourceReference, Card as PdfAnkiCard

# Import domain_types for conversion
from domain_types import Chunk as DomainChunk, ChunkingResult as DomainChunkingResult, SourceReference as DomainSourceReference


def convert_domain_chunk_to_pdfanki(domain_chunk: DomainChunk) -> PdfAnkiChunk:
    """Convert a domain_types.Chunk to pdf2anki_types.Chunk."""
    return PdfAnkiChunk(
        id=domain_chunk.id,
        text=domain_chunk.text,
        token_count=domain_chunk.token_count,
        source_ref=PdfAnkiSourceReference(
            pdf_sha256=domain_chunk.source_ref.pdf_sha256,
            chunk_id=domain_chunk.source_ref.chunk_id
        ),
        start_page=domain_chunk.start_page,
        end_page=domain_chunk.end_page,
        section_title=domain_chunk.section_title
    )


def convert_domain_chunking_result_to_pdfanki(domain_result: DomainChunkingResult) -> PdfAnkiChunkingResult:
    """Convert a domain_types.ChunkingResult to pdf2anki_types.ChunkingResult."""
    pdfanki_chunks = [convert_domain_chunk_to_pdfanki(chunk) for chunk in domain_result.chunks]
    return PdfAnkiChunkingResult(
        chunks=pdfanki_chunks,
        total_chunks=domain_result.total_chunks,
        total_tokens=domain_result.total_tokens
    )


def process_markdown_for_streamlit(
    markdown_content: str,
    pdf_sha256: str,
    max_tokens: int = 2000,
    remove_images: bool = False
) -> tuple[str, PdfAnkiChunkingResult]:
    """
    Process markdown content: clean and chunk it for LLM-based card generation.
    
    Args:
        markdown_content: Raw markdown content from PDF conversion
        pdf_sha256: SHA256 hash of the source PDF
        max_tokens: Maximum tokens per chunk (default: 2000)
        remove_images: Whether to remove image references (default: False)
    
    Returns:
        Tuple of (cleaned_markdown, chunking_result) where chunking_result uses pdf2anki_types
    """
    # Step 1: Clean markdown
    cleaning_result = _clean_markdown(markdown_content, remove_images=remove_images)
    cleaned_markdown = cleaning_result.cleaned_text
    
    # Step 2: Chunk markdown
    domain_chunking_result = _chunk_markdown(
        cleaned_markdown,
        pdf_sha256=pdf_sha256,
        max_tokens=max_tokens
    )
    
    # Step 3: Convert to pdf2anki_types
    pdfanki_chunking_result = convert_domain_chunking_result_to_pdfanki(domain_chunking_result)
    
    return cleaned_markdown, pdfanki_chunking_result


def get_semantic_info_for_chunk(chunk: PdfAnkiChunk) -> dict:
    """
    Get semantic structure information for a chunk.
    
    Args:
        chunk: A pdf2anki_types.Chunk object
    
    Returns:
        Dictionary with semantic structure information
    """
    # Convert to domain_types.Chunk for semantic detection
    domain_chunk = DomainChunk(
        id=chunk.id,
        text=chunk.text,
        token_count=chunk.token_count,
        source_ref=DomainSourceReference(
            pdf_sha256=chunk.source_ref.pdf_sha256,
            chunk_id=chunk.source_ref.chunk_id
        ),
        start_page=chunk.start_page,
        end_page=chunk.end_page,
        section_title=chunk.section_title
    )
    
    return _identify_semantic_structures(domain_chunk)


def load_pdf_sha256_from_meta(meta_path: Path) -> Optional[str]:
    """
    Load PDF SHA256 from meta.json file.
    
    Args:
        meta_path: Path to meta.json file
    
    Returns:
        SHA256 hash string or None if not found
    """
    if not meta_path.exists():
        return None
    
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            return meta.get("source_sha256")
    except Exception:
        return None

