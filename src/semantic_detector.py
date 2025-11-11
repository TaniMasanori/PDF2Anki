"""
Semantic structure detection for markdown content.

This module identifies definitions, key terms, and concept boundaries
in markdown chunks to enrich metadata for flashcard generation.
"""

import re
from typing import Dict, List

from domain_types import Chunk


def identify_definitions(text: str) -> List[Dict[str, str]]:
    """
    Identify definition patterns in text.
    
    Patterns:
    - "X is Y" or "X is a Y"
    - "X: Y" (colon definition)
    - "X - Y" (dash definition)
    - "X (definition)" (parenthetical)
    
    Args:
        text: Text to analyze
    
    Returns:
        List of dicts with 'term' and 'definition' keys
    """
    definitions: List[Dict[str, str]] = []
    
    # Pattern 1: "X is Y" or "X is a/an/the Y"
    pattern1 = r'\*\*([^*]+)\*\*\s+is\s+(?:a|an|the)?\s*(.+?)(?:\.|$|,|;)'
    for match in re.finditer(pattern1, text, re.IGNORECASE):
        definitions.append({
            'term': match.group(1).strip(),
            'definition': match.group(2).strip()
        })
    
    # Pattern 2: "X: Y" (colon definition, often in lists)
    pattern2 = r'^\s*\*\*([^*]+)\*\*\s*:\s*(.+?)(?:\.|$|,|;)'
    for match in re.finditer(pattern2, text, re.MULTILINE):
        definitions.append({
            'term': match.group(1).strip(),
            'definition': match.group(2).strip()
        })
    
    # Pattern 3: "X - Y" (dash definition)
    pattern3 = r'^\s*\*\*([^*]+)\*\*\s*-\s*(.+?)(?:\.|$|,|;)'
    for match in re.finditer(pattern3, text, re.MULTILINE):
        definitions.append({
            'term': match.group(1).strip(),
            'definition': match.group(2).strip()
        })
    
    return definitions


def identify_key_terms(text: str) -> List[str]:
    """
    Identify key terms in text.
    
    Looks for:
    - Bold text (**term**)
    - Italic text (*term*)
    - Terms in quotes ("term")
    - Capitalized phrases (likely proper nouns or acronyms)
    
    Args:
        text: Text to analyze
    
    Returns:
        List of identified key terms
    """
    terms: List[str] = []
    
    # Bold text
    bold_pattern = r'\*\*([^*]+)\*\*'
    for match in re.finditer(bold_pattern, text):
        term = match.group(1).strip()
        if len(term) > 2 and len(term) < 50:  # Reasonable length
            terms.append(term)
    
    # Italic text (but not math expressions)
    italic_pattern = r'(?<!\$)\*([^*]+)\*(?!\$)'
    for match in re.finditer(italic_pattern, text):
        term = match.group(1).strip()
        if len(term) > 2 and len(term) < 50:
            terms.append(term)
    
    # Terms in quotes
    quote_pattern = r'"([^"]{3,50})"'
    for match in re.finditer(quote_pattern, text):
        terms.append(match.group(1).strip())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_terms = []
    for term in terms:
        term_lower = term.lower()
        if term_lower not in seen:
            seen.add(term_lower)
            unique_terms.append(term)
    
    return unique_terms


def identify_concept_boundaries(text: str) -> List[Dict[str, str]]:
    """
    Identify concept boundaries in text.
    
    Looks for:
    - Section transitions (headings)
    - Bullet lists (likely concept lists)
    - Numbered lists (likely concept lists)
    
    Args:
        text: Text to analyze
    
    Returns:
        List of dicts with concept boundary information
    """
    boundaries: List[Dict[str, str]] = []
    
    lines = text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check for headings
        if re.match(r'^#{1,6}\s+', stripped):
            boundaries.append({
                'type': 'heading',
                'text': stripped,
                'line': i
            })
        
        # Check for bullet lists
        if re.match(r'^[-*+]\s+', stripped):
            boundaries.append({
                'type': 'bullet_list',
                'text': stripped[:100],  # First 100 chars
                'line': i
            })
        
        # Check for numbered lists
        if re.match(r'^\d+[.)]\s+', stripped):
            boundaries.append({
                'type': 'numbered_list',
                'text': stripped[:100],
                'line': i
            })
    
    return boundaries


def identify_semantic_structures(chunk: Chunk) -> Dict:
    """
    Identify semantic structures in a chunk.
    
    Args:
        chunk: Chunk to analyze
    
    Returns:
        Dictionary with semantic structure information:
        - definitions: List of term/definition pairs
        - key_terms: List of key terms
        - concept_boundaries: List of concept boundaries
    """
    return {
        'definitions': identify_definitions(chunk.text),
        'key_terms': identify_key_terms(chunk.text),
        'concept_boundaries': identify_concept_boundaries(chunk.text)
    }

