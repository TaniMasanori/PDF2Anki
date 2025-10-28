"""
PDF2Anki Streamlit Web Interface
Allows users to upload PDF files, convert them to Markdown using marker-pdf,
generate Anki cards, and download the results.
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
import json
import time
from typing import List, Optional
import openai
from dotenv import load_dotenv

# Import our local modules
from marker_client import convert_pdf_to_markdown
from pdf2anki_types import Card

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="PDF2Anki Converter",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'conversion_done' not in st.session_state:
    st.session_state.conversion_done = False
if 'markdown_content' not in st.session_state:
    st.session_state.markdown_content = None
if 'markdown_path' not in st.session_state:
    st.session_state.markdown_path = None
if 'cards' not in st.session_state:
    st.session_state.cards = []
if 'tsv_content' not in st.session_state:
    st.session_state.tsv_content = None


def build_llm_prompt_script(md_path: str, num_cards: int, note_type: str, content_focus: str) -> str:
    """
    Build a Bash script that calls an OpenAI-compatible LLM endpoint (e.g., Llama)
    to generate Anki cards directly from the markdown file content.
    """
    note_type = (note_type or "basic").lower()
    content_focus = content_focus or "mixed"

    if note_type == "cloze":
        output_block = (
            "Generate exactly {num_cards} cloze deletions. Output ONLY a numbered list with this exact format:\n"
            "1. Cloze: [Text containing {{c1::...}} or {{cN::...}}]\n   Extra: [optional extra]\n\n"
            "2. Cloze: [Text]\n   Extra: [optional extra]"
        )
        tsv_hint = "Cloze TSV: cloze_text\textra"
    else:
        output_block = (
            "Generate exactly {num_cards} flashcards. Output ONLY a numbered list with this exact format:\n"
            "1. Question: [question text]\n   Answer: [answer text]\n\n"
            "2. Question: [question text]\n   Answer: [answer text]"
        )
        tsv_hint = "Basic TSV: question\tanswer"

    prompt_header = (
        "You are an assistant that creates Anki flashcards.\n\n"
        f"Focus on {content_focus if content_focus != 'mixed' else 'key concepts, definitions, and important details'}.\n\n"
        "IMPORTANT:\n"
        f"- {output_block}\n"
        "- Do not include any other text, explanations, headings, or formatting.\n"
        "- Ensure mathematical expressions are wrapped in $...$ for inline math or $$...$$ for display math.\n"
        "- Keep each item concise but informative.\n"
    )

    script = f"""#!/usr/bin/env bash
set -euo pipefail

# OpenAI-compatible endpoint (e.g., llama.cpp server, vLLM, LM Studio)
LLM_API_BASE="${{LLM_API_BASE:-http://localhost:8080/v1}}"
LLM_MODEL="${{LLM_MODEL:-llama-3.1-8b-instruct}}"
LLM_API_KEY="${{LLM_API_KEY:-no-key-required}}"

CONTENT_FILE="{md_path}"
CONTENT=$(cat "$CONTENT_FILE")

# Build user prompt
read -r -d '' PROMPT <<'EOF'
{prompt_header}
EOF

USER_INPUT="$PROMPT\n\nContent:\n$CONTENT"

# Build JSON payload using jq to escape safely
DATA=$(jq -n --arg model "$LLM_MODEL" --arg sys "You are a helpful assistant that creates educational flashcards." --arg prompt "$USER_INPUT" '{model:$model, messages:[{role:"system", content:$sys},{role:"user", content:$prompt}], temperature:0.2, max_tokens:2000}')

echo "Requesting LLM at $LLM_API_BASE with model $LLM_MODEL..." 1>&2
curl -sS -X POST "$LLM_API_BASE/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer '$LLM_API_KEY'" \
  -d "$DATA" | jq -r '.choices[0].message.content'

# Hint: The output is a numbered list; you can post-process to TSV if desired.
# {tsv_hint}
"""
    return script


def generate_anki_cards(
    markdown_content: str,
    num_cards: int = 10,
    card_type: str = "mixed",
    note_type: str = "basic",
) -> List[Card]:
    """
    Generate Anki cards from markdown content using OpenAI API.
    
    Args:
        markdown_content: The markdown content to generate cards from
        num_cards: Number of cards to generate
        card_type: Type of cards to generate (definitions, concepts, mixed)
    
    Returns:
        List of Card objects
    """
    # Configure LLM endpoint
    llm_base = os.getenv("LLM_API_BASE")
    llm_model = os.getenv("LLM_MODEL", "llama-3.1-8b-instruct")
    if llm_base:
        # Use OpenAI-compatible endpoint (e.g., llama.cpp, vLLM)
        openai.base_url = llm_base.rstrip("/")
        openai.api_key = os.getenv("LLM_API_KEY", "no-key-required")
        model_name = llm_model
    else:
        # Fallback to OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("No LLM configured. Set LLM_API_BASE (for Llama) or OPENAI_API_KEY.")
            return []
        openai.api_key = api_key
        model_name = "gpt-4-turbo-preview"
    
    # Prepare the prompt
    if (note_type or "basic").lower() == "cloze":
        output_instructions = (
            "Generate exactly {num_cards} cloze deletions. Output ONLY a numbered list with this exact format:\n"
            "1. Cloze: [Text containing {{c1::...}} or {{cN::...}}]\n   Extra: [optional extra]\n\n"
            "2. Cloze: [Text]\n   Extra: [optional extra]"
        )
    else:
        output_instructions = (
            "Generate exactly {num_cards} flashcards. Output ONLY a numbered list with this exact format:\n"
            "1. Question: [question text]\n   Answer: [answer text]\n\n"
            "2. Question: [question text]\n   Answer: [answer text]"
        )

    prompt_template = f"""You are an assistant that creates Anki flashcards.

Focus on {card_type if card_type != 'mixed' else 'key concepts, definitions, and important details'}.

IMPORTANT:
- {output_instructions.format(num_cards=num_cards)}
- Do not include any other text, explanations, headings, or formatting.
- Ensure mathematical expressions are wrapped in $...$ for inline math or $$...$$ for display math.
- Keep each item concise but informative.

Content:
{markdown_content[:4000]}
"""

    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates educational flashcards."},
                {"role": "user", "content": prompt_template}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse the response
        content = response.choices[0].message.content
        cards = []
        
        # Split by numbered items
        import re
        if (note_type or "basic").lower() == "cloze":
            pattern = r'\d+\.\s*Cloze:\s*(.*?)\n\s*Extra:\s*(.*?)(?=\n\d+\.|$)'
        else:
            pattern = r'\d+\.\s*Question:\s*(.*?)\n\s*Answer:\s*(.*?)(?=\n\d+\.|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for i, (front, back_or_extra) in enumerate(matches):
            # Clean up the text
            front = front.strip()
            back_or_extra = back_or_extra.strip()
            
            if front:
                if (note_type or "basic").lower() == "cloze":
                    card = Card(
                        question=front,
                        answer="",
                        note_type="cloze",
                        extra=back_or_extra,
                        tags=["PDF2Anki", "auto-generated", "cloze"]
                    )
                else:
                    card = Card(
                        question=front,
                        answer=back_or_extra,
                        note_type="basic",
                        tags=["PDF2Anki", "auto-generated"]
                    )
                cards.append(card)
        
        return cards
        
    except Exception as e:
        st.error(f"Error generating cards: {str(e)}")
        return []


def main():
    # Header
    st.title("📚 PDF2Anki Converter")
    st.markdown("Convert PDF documents to Anki flashcards with AI")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Marker API settings
        st.subheader("Marker API")
        marker_api_url = st.text_input(
            "Marker API URL",
            value=os.getenv("MARKER_API_BASE", "http://localhost:8000"),
            help="URL of the Marker API server"
        )
        
        # Card generation settings
        st.subheader("Card Generation")
        num_cards = st.number_input(
            "Number of cards to generate",
            min_value=1,
            max_value=50,
            value=10,
            help="How many flashcards to generate from the PDF"
        )
        
        card_type = st.selectbox(
            "Content focus",
            ["mixed", "definitions", "concepts", "facts"],
            help="What type of content to focus on when generating cards"
        )

        note_type = st.selectbox(
            "Anki note type",
            ["basic", "cloze"],
            help="Choose 'basic' (Front/Back) or 'cloze' ({{c1::...}} with Extra)"
        )
        
        # LLM configuration (OpenAI-compatible or OpenAI)
        st.subheader("LLM API")
        llm_base = os.getenv("LLM_API_BASE")
        llm_model = os.getenv("LLM_MODEL", "llama-3.1-8b-instruct")
        if llm_base:
            st.info(f"Using OpenAI-compatible endpoint: {llm_base} (model: {llm_model})")
        elif os.getenv("OPENAI_API_KEY"):
            st.success("Using OpenAI (OPENAI_API_KEY configured)")
        else:
            st.warning("No LLM configured. Set LLM_API_BASE for Llama or OPENAI_API_KEY for OpenAI.")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Upload PDF")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF document to convert to Anki cards"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            
            # Display file info
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB",
                "File type": uploaded_file.type
            }
            st.json(file_details)
            
            # Convert button
            if st.button("🔄 Convert to Markdown", type="primary"):
                with st.spinner("Converting PDF to Markdown..."):
                    try:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_path = Path(tmp_file.name)
                        
                        # Convert PDF to Markdown
                        output_root = Path(tempfile.mkdtemp())
                        result = convert_pdf_to_markdown(
                            pdf_path=tmp_path,
                            api_base_url=marker_api_url,
                            output_root=output_root
                        )
                        
                        # Read the markdown content
                        with open(result.markdown_path, 'r', encoding='utf-8') as f:
                            markdown_content = f.read()
                        
                        # Store in session state
                        st.session_state.markdown_content = markdown_content
                        st.session_state.markdown_path = result.markdown_path
                        st.session_state.conversion_done = True
                        
                        # Clean up temp PDF
                        os.unlink(tmp_path)
                        
                        st.success("✅ PDF converted successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error converting PDF: {str(e)}")
                        st.session_state.conversion_done = False
    
    with col2:
        st.header("📝 Results")
        
        if st.session_state.conversion_done and st.session_state.markdown_content:
            # Show markdown preview
            with st.expander("📄 Markdown Preview", expanded=False):
                st.text_area(
                    "Markdown content",
                    st.session_state.markdown_content[:2000] + "...",
                    height=300,
                    disabled=True
                )

            # Prompt command/script for Llama (OpenAI-compatible) generation
            with st.expander("🧩 Generate LLM Prompt Command (Llama/OpenAI-compatible)", expanded=False):
                script_text = build_llm_prompt_script(
                    md_path=str(st.session_state.markdown_path),
                    num_cards=num_cards,
                    note_type=note_type,
                    content_focus=card_type,
                )
                st.markdown("Environment: set LLM_API_BASE / LLM_MODEL / LLM_API_KEY as needed. The script reads the converted markdown file and posts it to the LLM.")
                st.code(script_text, language="bash")
                st.download_button(
                    label="⬇️ Download prompt script",
                    data=script_text,
                    file_name="generate_cards_llama.sh",
                    mime="text/x-shellscript"
                )
            
            # Generate cards button
            if st.button("🎴 Generate Anki Cards", type="primary"):
                with st.spinner(f"Generating {num_cards} Anki cards..."):
                    cards = generate_anki_cards(
                        st.session_state.markdown_content,
                        num_cards=num_cards,
                        card_type=card_type,
                        note_type=note_type,
                    )
                    
                    if cards:
                        st.session_state.cards = cards
                        
                        # Generate TSV content
                        tsv_lines = []
                        for card in cards:
                            tsv_lines.append(card.to_tsv_row())
                        st.session_state.tsv_content = "\n".join(tsv_lines)
                        
                        st.success(f"✅ Generated {len(cards)} cards successfully!")
                    else:
                        st.error("❌ Failed to generate cards")
            
            # Display generated cards
            if st.session_state.cards:
                st.subheader(f"Generated Cards ({len(st.session_state.cards)})")
                
                # Show cards in an expandable section
                for i, card in enumerate(st.session_state.cards, 1):
                    with st.expander(f"Card {i}: {card.question[:50]}..."):
                        if card.note_type == "cloze":
                            st.markdown(f"**Cloze:** {card.question}")
                            if card.extra:
                                st.markdown(f"**Extra:** {card.extra}")
                        else:
                            st.markdown(f"**Question:** {card.question}")
                            st.markdown(f"**Answer:** {card.answer}")
                        if card.tags:
                            st.markdown(f"**Tags:** {', '.join(card.tags)}")
    
    # Download section
    if st.session_state.conversion_done:
        st.header("💾 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.markdown_content:
                st.download_button(
                    label="📄 Download Markdown",
                    data=st.session_state.markdown_content,
                    file_name=f"converted_{uploaded_file.name.replace('.pdf', '.md')}",
                    mime="text/markdown"
                )
        
        with col2:
            if st.session_state.tsv_content:
                st.download_button(
                    label="📊 Download TSV for Anki",
                    data=st.session_state.tsv_content,
                    file_name=f"anki_cards_{uploaded_file.name.replace('.pdf', '.tsv')}",
                    mime="text/tab-separated-values"
                )
    
    # Instructions
    with st.expander("📖 How to use"):
        st.markdown("""
        1. **Upload a PDF**: Click the file uploader and select your PDF document
        2. **Convert to Markdown**: Click the "Convert to Markdown" button
        3. **Generate Cards**: Once converted, click "Generate Anki Cards"
        4. **Download Results**: Download the Markdown file and/or TSV file
        5. **Import to Anki**:
           - Open Anki Desktop
           - Go to File → Import
           - Select the downloaded TSV file
           - Choose "Tab" as the field separator
           - For Basic: map fields → Field 1: Front, Field 2: Back
           - For Cloze: choose note type "Cloze", map fields → Field 1: Text, Field 2: Extra
           - Click Import
        
        **Note**: Make sure the Marker API server is running at the specified URL (default: http://localhost:8000)
        """)


if __name__ == "__main__":
    main()
