"""
Enhanced markdown cleaning module for PDF conversion artifacts.

This module provides functions to clean markdown output from PDF converters,
removing OCR artifacts, repetitive headers/footers, and normalizing formatting
while preserving important content like LaTeX math expressions.
"""

import re
from typing import List

from domain_types import CleaningResult


def clean_markdown(md: str, remove_images: bool = False) -> CleaningResult:
    """
    Clean markdown text by removing artifacts and normalizing formatting.
    
    Args:
        md: Raw markdown text from PDF conversion
        remove_images: If True, remove image references. If False, keep them.
    
    Returns:
        CleaningResult with cleaned text and statistics
    """
    removed_patterns: List[str] = []
    stats: dict = {
        "original_length": len(md),
        "lines_removed": 0,
        "artifacts_removed": 0,
    }
    
    text = md
    
    # Step 1: Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Step 2: Remove trailing whitespace from lines
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    
    # Step 3: Collapse excessive newlines (3+ to 2)
    original_lines = len(text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    stats["lines_removed"] = original_lines - len(text.split("\n"))
    
    # Step 4: Remove common OCR artifacts (isolated punctuation, excessive punctuation)
    # Remove lines that are just punctuation or symbols
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that are just punctuation/symbols (but preserve math expressions)
        if stripped and not re.match(r'^[|\\/_\-\+\*\^~`]+$', stripped):
            # Check if it's a valid line (has alphanumeric content or is a heading/list)
            if re.search(r'[a-zA-Z0-9]', stripped) or stripped.startswith('#') or stripped.startswith('-') or stripped.startswith('*'):
                cleaned_lines.append(line)
            elif re.search(r'\$.*\$', stripped):  # Preserve lines with math
                cleaned_lines.append(line)
            else:
                stats["artifacts_removed"] += 1
                removed_patterns.append(f"OCR artifact: {stripped[:50]}")
        elif not stripped:  # Preserve empty lines (for paragraph breaks)
            cleaned_lines.append(line)
    
    text = "\n".join(cleaned_lines)
    
    # Step 5: Remove repetitive headers/footers (page numbers, document titles)
    # Detect lines that appear multiple times and are likely headers/footers
    lines = text.split("\n")
    line_counts: dict[str, int] = {}
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped) < 100:  # Short lines are more likely headers/footers
            line_counts[stripped] = line_counts.get(stripped, 0) + 1
    
    # Remove lines that appear 3+ times and are likely headers/footers
    repetitive_patterns = [line for line, count in line_counts.items() 
                          if count >= 3 and not line.startswith('#') 
                          and not re.search(r'\$.*\$', line)]  # Don't remove math
    
    if repetitive_patterns:
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped not in repetitive_patterns:
                cleaned_lines.append(line)
            else:
                stats["artifacts_removed"] += 1
                removed_patterns.append(f"Repetitive header/footer: {stripped[:50]}")
        text = "\n".join(cleaned_lines)
    
    # Step 6: Remove image references if requested
    if remove_images:
        image_pattern = r'!\[.*?\]\(.*?\)'
        image_matches = re.findall(image_pattern, text)
        if image_matches:
            text = re.sub(image_pattern, '', text)
            stats["artifacts_removed"] += len(image_matches)
            removed_patterns.extend([f"Image reference: {img[:50]}" for img in image_matches])
    
    # Step 7: Clean up any remaining excessive whitespace
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines to double
    
    # Step 8: Final trim
    text = text.strip() + "\n"
    
    stats["final_length"] = len(text)
    stats["reduction_percent"] = round((1 - len(text) / len(md)) * 100, 2) if md else 0
    
    return CleaningResult(
        cleaned_text=text,
        removed_patterns=removed_patterns[:50],  # Limit to first 50 for readability
        stats=stats
    )

