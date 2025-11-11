"""
Core logic for prompt construction, parsing model outputs, and script generation.

This module contains pure functions that can be unit-tested without importing
the Streamlit UI layer.

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

from __future__ import annotations

from typing import List
import re

from pdf2anki_types import Card


def build_output_instructions(note_type: str, num_cards: int) -> str:
    """
    Return instruction block describing the exact output format expected from the model.
    """
    note = (note_type or "basic").lower()
    if note == "cloze":
        return (
            "Generate exactly {num_cards} cloze deletions. Output ONLY a numbered list with this exact format:\n"
            "1. Cloze: [Text containing {{c1::...}} or {{cN::...}}]\n   Extra: [optional extra]\n\n"
            "2. Cloze: [Text]\n   Extra: [optional extra]"
        ).format(num_cards=num_cards)
    return (
        "Generate exactly {num_cards} flashcards. Output ONLY a numbered list with this exact format:\n"
        "1. Question: [question text]\n   Answer: [answer text]\n\n"
        "2. Question: [question text]\n   Answer: [answer text]"
    ).format(num_cards=num_cards)


def build_prompt(note_type: str, num_cards: int, content_focus: str, markdown_content: str) -> str:
    """
    Build the full user prompt for the chat completion request.
    Note: System message should be set separately (e.g., "You are a helpful assistant that creates educational flashcards.")
    """
    focus = content_focus if content_focus and content_focus != "mixed" else "key concepts, definitions, and important details"
    instructions = build_output_instructions(note_type, num_cards)
    content = (markdown_content or "")[:4000]
    return (
        f"Create Anki flashcards from the following content. Focus on {focus}.\n\n"
        "IMPORTANT:\n"
        f"- {instructions}\n"
        "- Do not include any other text, explanations, headings, or formatting.\n"
        "- Ensure mathematical expressions are wrapped in $...$ for inline math or $$...$$ for display math.\n"
        "- Keep each item concise but informative.\n\n"
        f"Content:\n{content}\n"
    )


def parse_cards_from_output(model_output: str, note_type: str) -> List[Card]:
    """
    Parse model output into a list of Card objects according to note_type.
    """
    text = model_output or ""
    note = (note_type or "basic").lower()

    if note == "cloze":
        pattern = r"\d+\.\s*Cloze:\s*(.*?)\n\s*Extra:\s*(.*?)(?=\n\d+\.|$)"
    else:
        pattern = r"\d+\.\s*Question:\s*(.*?)\n\s*Answer:\s*(.*?)(?=\n\d+\.|$)"

    matches = re.findall(pattern, text, re.DOTALL)
    cards: List[Card] = []
    for front, back in matches:
        front = front.strip()
        back = back.strip()
        if not front:
            continue
        if note == "cloze":
            cards.append(
                Card(
                    question=front,
                    answer="",
                    note_type="cloze",
                    extra=back,
                    tags=["PDF2Anki", "auto-generated", "cloze"],
                )
            )
        else:
            cards.append(
                Card(
                    question=front,
                    answer=back,
                    note_type="basic",
                    tags=["PDF2Anki", "auto-generated"],
                )
            )
    return cards


def build_llm_prompt_script(md_path: str, num_cards: int, note_type: str, content_focus: str) -> str:
    """
    Build a Bash script that calls an OpenAI-compatible endpoint to generate cards.
    """
    # Build prompt header without content (remove trailing "Content:\n" line)
    prompt_with_empty = build_prompt(note_type=note_type, num_cards=num_cards, content_focus=content_focus, markdown_content="")
    # Remove the trailing "Content:\n" line since we'll add it in the script
    prompt_header = prompt_with_empty.rstrip().rsplit("Content:", 1)[0].rstrip()
    
    script = f"""#!/usr/bin/env bash
set -euo pipefail

# OpenAI-compatible endpoint (e.g., llama.cpp server, vLLM, LM Studio)
LLM_API_BASE="${{LLM_API_BASE:-http://localhost:8080/v1}}"
LLM_MODEL="${{LLM_MODEL:-llama-3.1-8b-instruct}}"
LLM_API_KEY="${{LLM_API_KEY:-no-key-required}}"

CONTENT_FILE="{md_path}"
CONTENT=$(cat "$CONTENT_FILE")

read -r -d '' PROMPT <<'EOF'
{prompt_header}

Content:
EOF

USER_INPUT="$PROMPT$CONTENT"

DATA=$(jq -n --arg model "$LLM_MODEL" --arg sys "You are a helpful assistant that creates educational flashcards." --arg prompt "$USER_INPUT" '{{model:$model, messages:[{{"role":"system", "content":$sys}},{{"role":"user", "content":$prompt}}], temperature:0.2, max_completion_tokens:2000}}')

echo "Requesting LLM at $LLM_API_BASE with model $LLM_MODEL..." 1>&2
curl -sS -X POST "$LLM_API_BASE/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer '$LLM_API_KEY'" \
  -d "$DATA" | jq -r '.choices[0].message.content'
"""
    return script







