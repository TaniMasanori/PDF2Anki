"""
Data type definitions for PDF2Anki conversion pipeline.

This module defines the core data structures used throughout the conversion process,
from PDF input to Anki card generation.

Copyright (C) 2025  Masanori Tani

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class EngineInfo:
    """Information about the conversion engine."""
    name: str
    version: str


@dataclass
class ConversionMeta:
    """
    Metadata about a PDF conversion operation.
    
    Attributes:
        source_path: Path to the original PDF file
        source_sha256: SHA256 hash of the source PDF
        pages: Number of pages in the PDF
        engine: Information about the conversion engine used
        elapsed_sec: Time taken for conversion in seconds
        created_at: ISO 8601 timestamp of conversion
    """
    source_path: str
    source_sha256: str
    pages: int
    engine: EngineInfo
    elapsed_sec: float
    created_at: str  # ISO 8601 format
    
    @classmethod
    def create_now(cls, source_path: str, source_sha256: str, pages: int,
                   engine: EngineInfo, elapsed_sec: float) -> 'ConversionMeta':
        """Create a ConversionMeta with current timestamp."""
        return cls(
            source_path=source_path,
            source_sha256=source_sha256,
            pages=pages,
            engine=engine,
            elapsed_sec=elapsed_sec,
            created_at=datetime.utcnow().isoformat() + 'Z'
        )


@dataclass
class ConversionResult:
    """
    Result of a PDF to Markdown conversion.
    
    Attributes:
        markdown_path: Path to the generated Markdown file
        meta_path: Path to the metadata JSON file
        images_dir: Optional path to directory containing extracted images
    """
    markdown_path: str
    meta_path: str
    images_dir: Optional[str] = None


@dataclass
class SourceReference:
    """Reference to the source PDF and location within it."""
    pdf_sha256: str
    chunk_id: Optional[str] = None


@dataclass
class Chunk:
    """
    A chunk of text extracted from a PDF, suitable for LLM processing.
    
    Attributes:
        id: Unique identifier for the chunk (e.g., "chunk_0001")
        text: The actual text content of the chunk
        start_page: Starting page number (optional)
        end_page: Ending page number (optional)
        section_title: Title of the section this chunk belongs to (optional)
        token_count: Approximate token count for LLM context management
        source_ref: Reference back to the source PDF
    """
    id: str
    text: str
    token_count: int
    source_ref: SourceReference
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    section_title: Optional[str] = None


@dataclass
class Card:
    """
    An Anki flashcard generated from PDF content.
    
    Attributes:
        question: The front of the flashcard (question/prompt)
        answer: The back of the flashcard (answer/explanation)
        tags: Optional list of tags for organizing cards in Anki
        source_ref: Optional reference to source PDF and chunk
    """
    question: str
    answer: str
    tags: List[str] = field(default_factory=list)
    source_ref: Optional[SourceReference] = None
    
    def to_tsv_row(self) -> str:
        """
        Convert card to TSV format for Anki import.
        
        Returns:
            Tab-separated string: question, answer, tags (semicolon-separated)
        """
        tags_str = ';'.join(self.tags) if self.tags else ''
        return f"{self.question}\t{self.answer}\t{tags_str}"


@dataclass
class CleaningResult:
    """
    Result of markdown cleaning operation.
    
    Attributes:
        cleaned_text: The cleaned markdown text
        removed_patterns: List of patterns that were removed
        stats: Optional statistics about the cleaning operation
    """
    cleaned_text: str
    removed_patterns: List[str] = field(default_factory=list)
    stats: Optional[dict] = None


@dataclass
class ChunkingResult:
    """
    Result of text chunking operation.
    
    Attributes:
        chunks: List of text chunks
        total_chunks: Total number of chunks created
        total_tokens: Total token count across all chunks
    """
    chunks: List[Chunk]
    total_chunks: int
    total_tokens: int

