"""
PDF2Anki Streamlit Web Interface
Allows users to upload PDF files, convert them to Markdown using marker-pdf,
generate Anki cards, and download the results.

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

import streamlit as st
import tempfile
import os
from pathlib import Path
import json
import time
from datetime import datetime
import shutil
import hashlib
from typing import List, Optional
import openai
from openai import APIError, RateLimitError, APIConnectionError, APITimeoutError
from dotenv import load_dotenv

# Import our local modules
from marker_client import convert_pdf_to_markdown
from pdf2anki_types import Card, SourceReference
from anki_core import build_llm_prompt_script, build_prompt, parse_cards_from_output
from markdown_processor_wrapper import (
    process_markdown_for_streamlit,
    get_semantic_info_for_chunk,
    load_pdf_sha256_from_meta
)

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
if 'meta_path' not in st.session_state:
    st.session_state.meta_path = None
if 'pdf_sha256' not in st.session_state:
    st.session_state.pdf_sha256 = None
if 'cancel_generation' not in st.session_state:
    st.session_state.cancel_generation = False
if 'generating' not in st.session_state:
    st.session_state.generating = False
if 'converting' not in st.session_state:
    st.session_state.converting = False
if 'converting_pdf_hash' not in st.session_state:
    st.session_state.converting_pdf_hash = None
if 'session_output_dir' not in st.session_state:
    st.session_state.session_output_dir = None



def generate_cards_from_chunk(
    chunk_text: str,
    chunk_id: str,
    num_cards_per_chunk: int,
    card_type: str,
    note_type: str,
    model_name: str,
    pdf_sha256: Optional[str] = None,
    semantic_info: Optional[dict] = None
) -> List[Card]:
    """
    Generate Anki cards from a single chunk using OpenAI API.
    
    Args:
        chunk_text: The chunk text content
        chunk_id: ID of the chunk
        num_cards_per_chunk: Number of cards to generate from this chunk
        card_type: Type of cards to generate
        note_type: Note type (basic or cloze)
        model_name: LLM model name
        semantic_info: Optional semantic structure information
    
    Returns:
        List of Card objects
    """
    # Enhance prompt with semantic information if available
    enhanced_content = chunk_text
    if semantic_info:
        key_terms = semantic_info.get("key_terms", [])
        definitions = semantic_info.get("definitions", [])
        if key_terms:
            enhanced_content += f"\n\nKey terms in this section: {', '.join(key_terms[:10])}"
        if definitions:
            enhanced_content += "\n\nImportant definitions:\n"
            for def_item in definitions[:5]:
                enhanced_content += f"- {def_item.get('term', '')}: {def_item.get('definition', '')}\n"
    
    # Prepare the prompt
    prompt_template = build_prompt(
        note_type=note_type,
        num_cards=num_cards_per_chunk,
        content_focus=card_type,
        markdown_content=enhanced_content,
    )

    try:
        # Call OpenAI API (without temperature parameter as default)
        response = openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates educational flashcards."},
                {"role": "user", "content": prompt_template}
            ],
            max_completion_tokens=2000
        )
        
        # Parse the response
        content = response.choices[0].message.content
        cards = parse_cards_from_output(content, note_type)
        
        # Add chunk reference to cards
        for card in cards:
            if card.source_ref is None:
                card.source_ref = SourceReference(
                    pdf_sha256=pdf_sha256 or "",
                    chunk_id=chunk_id
                )
            else:
                if pdf_sha256:
                    card.source_ref.pdf_sha256 = pdf_sha256
                card.source_ref.chunk_id = chunk_id
        
        return cards
        
    except RateLimitError as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
            st.error(f"**API Quota Exceeded** (chunk {chunk_id})\n\n"
                    f"You have exceeded your OpenAI API quota. Please check your billing and plan details.\n\n"
                    f"For more information: https://platform.openai.com/docs/guides/error-codes/api-errors")
        else:
            st.warning(f"**Rate Limit Error** (chunk {chunk_id})\n\n"
                      f"Too many requests. Please wait a moment and try again.\n\n"
                      f"Error: {error_msg}")
        return []
    except APIError as e:
        error_msg = str(e)
        if "model_not_found" in error_msg.lower():
            st.error(f"**Model Not Found** (chunk {chunk_id})\n\n"
                    f"The specified model does not exist or you don't have access to it.\n\n"
                    f"Error: {error_msg}\n\n"
                    f"Please check your OPENAI_MODEL setting in .env file.")
        elif "max_tokens" in error_msg.lower() or ("unsupported_parameter" in error_msg.lower() and "max_tokens" in error_msg.lower()):
            st.error(f"**Unsupported Parameter** (chunk {chunk_id})\n\n"
                    f"This model requires 'max_completion_tokens' instead of 'max_tokens'.\n\n"
                    f"Error: {error_msg}\n\n"
                    f"Please update the code or use a different model.")
        else:
            st.error(f"**API Error** (chunk {chunk_id})\n\n"
                    f"Error: {error_msg}")
        return []
    except (APIConnectionError, APITimeoutError) as e:
        st.warning(f"**Connection Error** (chunk {chunk_id})\n\n"
                  f"Failed to connect to the API. Please check your internet connection and try again.\n\n"
                  f"Error: {str(e)}")
        return []
    except Exception as e:
        st.warning(f"**Error generating cards from chunk {chunk_id}**: {str(e)}")
        return []


def generate_anki_cards(
    markdown_content: str,
    num_cards: int = 10,
    card_type: str = "mixed",
    note_type: str = "basic",
    use_chunking: bool = True,
    pdf_sha256: Optional[str] = None,
    max_tokens_per_chunk: int = 2000,
) -> List[Card]:
    """
    Generate Anki cards from markdown content using OpenAI API.
    
    Args:
        markdown_content: The markdown content to generate cards from
        num_cards: Number of cards to generate
        card_type: Type of cards to generate (definitions, concepts, mixed)
        note_type: Note type (basic or cloze)
        use_chunking: Whether to use chunking-based processing (default: True)
        pdf_sha256: SHA256 hash of the source PDF (required if use_chunking=True)
        max_tokens_per_chunk: Maximum tokens per chunk (default: 2000)
    
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
        # Use OPENAI_MODEL env var if set, otherwise default to gpt-5
        model_name = os.getenv("OPENAI_MODEL", "gpt-5")
    
    # Use chunking-based approach if enabled
    if use_chunking:
        if not pdf_sha256:
            st.warning("PDF SHA256 not provided. Falling back to non-chunking mode.")
            use_chunking = False
    
    if use_chunking:
        # Process markdown: clean and chunk
        cleaned_markdown, chunking_result = process_markdown_for_streamlit(
            markdown_content,
            pdf_sha256=pdf_sha256,
            max_tokens=max_tokens_per_chunk,
            remove_images=False
        )
        
        # Calculate cards per chunk
        total_chunks = chunking_result.total_chunks
        if total_chunks == 0:
            st.warning("No chunks created from markdown content.")
            return []
        
        cards_per_chunk = max(1, num_cards // total_chunks)
        remaining_cards = num_cards
        
        all_cards: List[Card] = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process each chunk
        for i, chunk in enumerate(chunking_result.chunks):
            if remaining_cards <= 0:
                break
            
            # Check if generation was cancelled
            if st.session_state.cancel_generation:
                st.warning("Card generation cancelled by user.")
                progress_bar.empty()
                status_text.empty()
                st.session_state.cancel_generation = False
                st.session_state.generating = False
                return all_cards[:num_cards] if all_cards else []
            
            status_text.text(f"Processing chunk {i+1}/{total_chunks}...")
            progress_bar.progress((i + 1) / total_chunks)
            
            # Get semantic info for the chunk
            semantic_info = get_semantic_info_for_chunk(chunk)
            
            # Generate cards from this chunk
            chunk_cards = generate_cards_from_chunk(
                chunk_text=chunk.text,
                chunk_id=chunk.id,
                num_cards_per_chunk=min(cards_per_chunk, remaining_cards),
                card_type=card_type,
                note_type=note_type,
                model_name=model_name,
                pdf_sha256=pdf_sha256,
                semantic_info=semantic_info
            )
            
            all_cards.extend(chunk_cards)
            remaining_cards -= len(chunk_cards)
        
        progress_bar.empty()
        status_text.empty()
        
        return all_cards[:num_cards]  # Limit to requested number
    
    else:
        # Original non-chunking approach
        prompt_template = build_prompt(
            note_type=note_type,
            num_cards=num_cards,
            content_focus=card_type,
            markdown_content=markdown_content,
        )

        try:
            # Call OpenAI API (without temperature parameter as default)
            response = openai.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates educational flashcards."},
                    {"role": "user", "content": prompt_template}
                ],
                max_completion_tokens=2000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            cards = parse_cards_from_output(content, note_type)
            
            return cards
            
        except RateLimitError as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
                st.error("**API Quota Exceeded**\n\n"
                        "You have exceeded your OpenAI API quota. Please check your billing and plan details.\n\n"
                        "For more information: https://platform.openai.com/docs/guides/error-codes/api-errors")
            else:
                st.warning("**Rate Limit Error**\n\n"
                          "Too many requests. Please wait a moment and try again.\n\n"
                          f"Error: {error_msg}")
            return []
        except APIError as e:
            error_msg = str(e)
            if "model_not_found" in error_msg.lower():
                st.error("**Model Not Found**\n\n"
                        "The specified model does not exist or you don't have access to it.\n\n"
                        f"Error: {error_msg}\n\n"
                        "Please check your OPENAI_MODEL setting in .env file.")
            elif "max_tokens" in error_msg.lower() or ("unsupported_parameter" in error_msg.lower() and "max_tokens" in error_msg.lower()):
                st.error("**Unsupported Parameter**\n\n"
                        "This model requires 'max_completion_tokens' instead of 'max_tokens'.\n\n"
                        f"Error: {error_msg}\n\n"
                        "Please update the code or use a different model.")
            else:
                st.error(f"**API Error**: {error_msg}")
            return []
        except (APIConnectionError, APITimeoutError) as e:
            st.warning("**Connection Error**\n\n"
                      "Failed to connect to the API. Please check your internet connection and try again.\n\n"
                      f"Error: {str(e)}")
            return []
        except Exception as e:
            st.error(f"**Error generating cards**: {str(e)}")
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
        
        # Chunking settings
        st.subheader("Processing Options")
        use_chunking = st.checkbox(
            "Use intelligent chunking",
            value=True,
            help="Enable markdown cleaning and chunking for better card generation"
        )
        max_tokens_per_chunk = st.number_input(
            "Max tokens per chunk",
            min_value=500,
            max_value=4000,
            value=2000,
            help="Maximum tokens per chunk (affects chunk size)"
        )
        
        # LLM configuration (OpenAI-compatible or OpenAI)
        st.subheader("LLM API")
        llm_base = os.getenv("LLM_API_BASE")
        llm_model = os.getenv("LLM_MODEL", "llama-3.1-8b-instruct")
        if llm_base:
            st.info(f"Using OpenAI-compatible endpoint: {llm_base} (model: {llm_model})")
        elif os.getenv("OPENAI_API_KEY"):
            openai_model = os.getenv("OPENAI_MODEL", "gpt-5")
            st.success(f"Using OpenAI (model: {openai_model})")
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
            # Compute PDF hash to prevent duplicate conversions
            uploaded_file.seek(0)  # Reset file pointer
            pdf_content = uploaded_file.read()
            pdf_hash = hashlib.sha256(pdf_content).hexdigest()
            uploaded_file.seek(0)  # Reset again for later use
            
            # Check if this PDF is already being converted
            is_same_pdf_converting = (
                st.session_state.get('converting', False) and 
                st.session_state.get('converting_pdf_hash') == pdf_hash
            )
            
            convert_button_disabled = st.session_state.get('converting', False)
            if st.button("🔄 Convert to Markdown", type="primary", disabled=convert_button_disabled):
                if is_same_pdf_converting:
                    st.warning("⚠️ This PDF is already being converted. Please wait for the current conversion to complete.")
                    st.stop()
                
                if st.session_state.get('converting', False):
                    st.warning("⚠️ Another PDF conversion is in progress. Please wait...")
                    st.stop()
                
                st.session_state.converting = True
                st.session_state.converting_pdf_hash = pdf_hash
                
                with st.spinner("Converting PDF to Markdown..."):
                    try:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(pdf_content)
                            tmp_path = Path(tmp_file.name)
                        
                        # Create session output directory in outputs folder
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        pdf_name_safe = Path(uploaded_file.name).stem.replace(" ", "_")
                        session_dir_name = f"{timestamp}_{pdf_name_safe}"
                        outputs_root = Path("outputs")
                        session_output_dir = outputs_root / session_dir_name
                        session_output_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Convert PDF to Markdown (using temporary directory first)
                        temp_output_root = Path(tempfile.mkdtemp())
                        result = convert_pdf_to_markdown(
                            pdf_path=tmp_path,
                            api_base_url=marker_api_url,
                            output_root=temp_output_root
                        )
                        
                        # Copy conversion results to session output directory
                        final_markdown_path = session_output_dir / "converted.md"
                        final_meta_path = session_output_dir / "meta.json"
                        
                        shutil.copy2(result.markdown_path, final_markdown_path)
                        shutil.copy2(result.meta_path, final_meta_path)
                        
                        # Note: Images are embedded in markdown as base64 data
                        # If needed, images can be extracted from the API response separately
                        
                        # Read the markdown content
                        with open(final_markdown_path, 'r', encoding='utf-8') as f:
                            markdown_content = f.read()
                        
                        # Load PDF SHA256 from metadata
                        pdf_sha256 = load_pdf_sha256_from_meta(final_meta_path)
                        if not pdf_sha256:
                            # Try to extract from meta.json directly
                            try:
                                with open(final_meta_path, 'r', encoding='utf-8') as meta_file:
                                    meta_data = json.load(meta_file)
                                    pdf_sha256 = meta_data.get("source_sha256")
                            except Exception:
                                pass
                        
                        # Store in session state
                        st.session_state.markdown_content = markdown_content
                        st.session_state.markdown_path = str(final_markdown_path)
                        st.session_state.meta_path = str(final_meta_path)
                        st.session_state.pdf_sha256 = pdf_sha256
                        st.session_state.session_output_dir = session_output_dir
                        st.session_state.conversion_done = True
                        
                        # Clean up temp PDF and temp output directory
                        os.unlink(tmp_path)
                        shutil.rmtree(temp_output_root, ignore_errors=True)
                        
                        st.success("✅ PDF converted successfully!")
                        if pdf_sha256:
                            st.info(f"PDF SHA256: {pdf_sha256[:16]}...")
                        st.info(f"Results saved to: {session_output_dir}")
                        
                    except Exception as e:
                        st.error(f"❌ Error converting PDF: {str(e)}")
                        st.session_state.conversion_done = False
                    finally:
                        st.session_state.converting = False
                        st.session_state.converting_pdf_hash = None
    
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
            
            # Generate cards button and stop button
            col_gen, col_stop = st.columns([1, 1])
            with col_gen:
                generate_clicked = st.button("Generate Anki Cards", type="primary")
            with col_stop:
                stop_clicked = st.button("Stop Generation", disabled=not st.session_state.get('generating', False))
            
            if stop_clicked:
                st.session_state.cancel_generation = True
                st.session_state.generating = False
                st.warning("Stopping card generation...")
                st.rerun()
            
            if generate_clicked:
                # Reset cancel flag and set generating flag
                st.session_state.cancel_generation = False
                st.session_state.generating = True
                
                with st.spinner(f"Generating {num_cards} Anki cards..."):
                    cards = generate_anki_cards(
                        st.session_state.markdown_content,
                        num_cards=num_cards,
                        card_type=card_type,
                        note_type=note_type,
                        use_chunking=use_chunking,
                        pdf_sha256=st.session_state.pdf_sha256,
                        max_tokens_per_chunk=max_tokens_per_chunk,
                    )
                    
                    # Reset generating flag
                    st.session_state.generating = False
                    
                    if cards:
                        st.session_state.cards = cards
                        
                        # Generate TSV content
                        tsv_lines = []
                        for card in cards:
                            tsv_lines.append(card.to_tsv_row())
                        st.session_state.tsv_content = "\n".join(tsv_lines)
                        
                        # Save TSV file to session output directory
                        if st.session_state.session_output_dir:
                            tsv_path = st.session_state.session_output_dir / "anki_cards.tsv"
                            with open(tsv_path, 'w', encoding='utf-8') as f:
                                f.write(st.session_state.tsv_content)
                        
                        # Generate and save prompt script to session output directory
                        if st.session_state.session_output_dir and st.session_state.markdown_path:
                            script_text = build_llm_prompt_script(
                                md_path=str(st.session_state.markdown_path),
                                num_cards=num_cards,
                                note_type=note_type,
                                content_focus=card_type,
                            )
                            prompt_script_path = st.session_state.session_output_dir / "prompt_script.sh"
                            with open(prompt_script_path, 'w', encoding='utf-8') as f:
                                f.write(script_text)
                            os.chmod(prompt_script_path, 0o755)  # Make executable
                        
                        st.success(f"✅ Generated {len(cards)} cards successfully!")
                        if st.session_state.session_output_dir:
                            st.info(f"Files saved to: {st.session_state.session_output_dir}")
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
