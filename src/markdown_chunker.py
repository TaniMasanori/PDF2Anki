"""
Markdown chunking module for splitting content into LLM-processable chunks.

This module provides functions to intelligently split markdown content by
section headings and token limits, preserving semantic structure.
"""

import re
from typing import List, Optional, Tuple

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False

from domain_types import Chunk, ChunkingResult, SourceReference


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.
    
    Uses tiktoken if available (cl100k_base encoding for GPT models),
    otherwise falls back to a simple approximation (4 chars per token).
    
    Args:
        text: Text to count tokens for
    
    Returns:
        Estimated token count
    """
    if HAS_TIKTOKEN:
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            pass
    
    # Fallback: approximate 4 characters per token
    return len(text) // 4


def extract_section_title(line: str) -> Optional[str]:
    """
    Extract section title from a markdown heading line.
    
    Args:
        line: A markdown heading line (e.g., "# Title" or "## Subtitle")
    
    Returns:
        The title text without the heading markers, or None if not a heading
    """
    match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
    if match:
        return match.group(2).strip()
    return None


def split_by_headings(md: str) -> List[Tuple[Optional[str], str]]:
    """
    Split markdown into sections based on headings.
    
    Args:
        md: Markdown text to split
    
    Returns:
        List of tuples (section_title, content) where section_title can be None
        for content before the first heading
    """
    sections: List[Tuple[Optional[str], str]] = []
    lines = md.split("\n")
    
    current_section_title: Optional[str] = None
    current_content: List[str] = []
    
    for line in lines:
        title = extract_section_title(line)
        if title is not None:
            # Save previous section if it has content
            if current_content:
                sections.append((current_section_title, "\n".join(current_content)))
            # Start new section
            current_section_title = title
            current_content = [line]  # Include the heading line
        else:
            current_content.append(line)
    
    # Add final section
    if current_content:
        sections.append((current_section_title, "\n".join(current_content)))
    
    return sections


def split_large_chunk(text: str, max_tokens: int, section_title: Optional[str]) -> List[str]:
    """
    Split a chunk that exceeds max_tokens into smaller chunks.
    
    Splits by paragraphs first, then by sentences if still too large.
    
    Args:
        text: Text content to split
        max_tokens: Maximum tokens per chunk
        section_title: Title of the section (will be prepended to all sub-chunks)
    
    Returns:
        List of text chunks
    """
    chunks: List[str] = []
    
    # Try splitting by paragraphs first
    paragraphs = re.split(r'\n\n+', text)
    current_chunk: List[str] = []
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        
        if para_tokens > max_tokens:
            # Paragraph itself is too large, split by sentences
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sentence in sentences:
                sent_tokens = estimate_tokens(sentence)
                if current_tokens + sent_tokens > max_tokens and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                current_chunk.append(sentence)
                current_tokens += sent_tokens
        else:
            if current_tokens + para_tokens > max_tokens and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_tokens = 0
            current_chunk.append(para)
            current_tokens += para_tokens
    
    # Add remaining content
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    
    return chunks


def chunk_markdown(md: str, pdf_sha256: str, max_tokens: int = 2000) -> ChunkingResult:
    """
    Split markdown into semantically meaningful chunks.
    
    Strategy:
    1. Split by section headings (#, ##, ###, etc.)
    2. If any chunk exceeds max_tokens, split further by paragraphs/sentences
    3. Assign sequential IDs and calculate token counts
    
    Args:
        md: Markdown text to chunk
        pdf_sha256: SHA256 hash of the source PDF
        max_tokens: Maximum tokens per chunk (default: 2000)
    
    Returns:
        ChunkingResult with list of Chunk objects
    """
    chunks: List[Chunk] = []
    chunk_counter = 1
    
    # Step 1: Split by headings
    sections = split_by_headings(md)
    
    for section_title, section_content in sections:
        section_tokens = estimate_tokens(section_content)
        
        if section_tokens <= max_tokens:
            # Section fits in one chunk
            chunk_id = f"chunk_{chunk_counter:04d}"
            chunks.append(Chunk(
                id=chunk_id,
                text=section_content.strip(),
                token_count=section_tokens,
                source_ref=SourceReference(
                    pdf_sha256=pdf_sha256,
                    chunk_id=chunk_id
                ),
                section_title=section_title
            ))
            chunk_counter += 1
        else:
            # Section is too large, split it
            sub_chunks = split_large_chunk(section_content, max_tokens, section_title)
            for sub_chunk_text in sub_chunks:
                chunk_id = f"chunk_{chunk_counter:04d}"
                sub_tokens = estimate_tokens(sub_chunk_text)
                chunks.append(Chunk(
                    id=chunk_id,
                    text=sub_chunk_text.strip(),
                    token_count=sub_tokens,
                    source_ref=SourceReference(
                        pdf_sha256=pdf_sha256,
                        chunk_id=chunk_id
                    ),
                    section_title=section_title
                ))
                chunk_counter += 1
    
    # Calculate totals
    total_tokens = sum(chunk.token_count for chunk in chunks)
    
    return ChunkingResult(
        chunks=chunks,
        total_chunks=len(chunks),
        total_tokens=total_tokens
    )

