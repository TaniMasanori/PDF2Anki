# Llama Prompt Command and Cloze Support

Date: 2025-10-28

## Overview

This update adds two capabilities to the Streamlit UI:
- A copyable/downloadable Bash script that posts the converted Markdown to an OpenAI-compatible LLM endpoint (e.g., llama.cpp server, vLLM) to generate cards.
- Anki note type selection (Basic or Cloze) with proper TSV export layout.

## How It Works

After converting a PDF to Markdown, open the “Generate LLM Prompt Command (Llama/OpenAI-compatible)” section. The UI shows a ready-to-run Bash script that:
- Reads the generated Markdown file
- Constructs an instruction prompt tailored to the selected note type and content focus
- Calls the Chat Completions endpoint
- Prints the model’s numbered list output to stdout

You can save the output to a file and optionally convert it to TSV if needed.

## Environment Variables

- `LLM_API_BASE` (default: `http://localhost:8080/v1`)
- `LLM_MODEL` (default: `llama-3.1-8b-instruct`)
- `LLM_API_KEY` (default: `no-key-required`)

These allow you to point the script at your local/remote Llama server or any OpenAI-compatible endpoint.

## Note Types and TSV

- Basic
  - UI generation: Front/Back
  - TSV columns: `Question` (Field 1), `Answer` (Field 2), `Tags`
  - Import mapping in Anki: Field 1 → Front, Field 2 → Back

- Cloze
  - UI generation: `{{c1::...}}` or `{{cN::...}}` in Text, optional Extra
  - TSV columns: `Text` (Field 1), `Extra` (Field 2), `Tags`
  - Import mapping in Anki: Choose note type “Cloze”, Field 1 → Text, Field 2 → Extra

## Implementation Notes

- `src/pdf2anki_types.py`
  - `Card` now includes `note_type` and `extra`
  - `to_tsv_row()` adapts output for Basic vs Cloze
- `src/streamlit_app.py`
  - Sidebar now includes “Anki note type”
  - LLM configuration section (detects `LLM_API_BASE` or OpenAI)
  - New section to display and download the LLM prompt script
  - Card generation supports Basic/Cloze prompts and parsing

## Example Script (shown in UI)

The UI generates and displays a script similar to this (paths and values are filled automatically):

```bash
#!/usr/bin/env bash
set -euo pipefail

LLM_API_BASE="${LLM_API_BASE:-http://localhost:8080/v1}"
LLM_MODEL="${LLM_MODEL:-llama-3.1-8b-instruct}"
LLM_API_KEY="${LLM_API_KEY:-no-key-required}"

CONTENT_FILE="/absolute/path/to/marker.md"
CONTENT=$(cat "$CONTENT_FILE")

read -r -d '' PROMPT <<'EOF'
You are an assistant that creates Anki flashcards.
IMPORTANT:
- Generate exactly N cards in the specified format (Basic or Cloze)
- Output ONLY the numbered list items; no extra text
- Keep items concise; preserve math using $...$ / $$...$$
EOF

USER_INPUT="$PROMPT\n\nContent:\n$CONTENT"

DATA=$(jq -n --arg model "$LLM_MODEL" --arg sys "You are a helpful assistant that creates educational flashcards." --arg prompt "$USER_INPUT" '{model:$model, messages:[{role:"system", content:$sys},{role:"user", content:$prompt}], temperature:0.2, max_tokens:2000}')

curl -sS -X POST "$LLM_API_BASE/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer '$LLM_API_KEY'" \
  -d "$DATA" | jq -r '.choices[0].message.content'
```

> Tip: Pipe the output to a file, review it, and then convert to TSV as needed.

## Importing to Anki

- Basic: Choose “Tab” as the field separator; map Field 1 → Front, Field 2 → Back
- Cloze: Choose note type “Cloze”; map Field 1 → Text, Field 2 → Extra

## Testing

- Verified UI generation for Basic and Cloze
- Verified TSV export aligns with Anki field mappings
- Verified script generation and environment variable overrides
