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
from types import Card

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


def generate_anki_cards(markdown_content: str, num_cards: int = 10, card_type: str = "mixed") -> List[Card]:
    """
    Generate Anki cards from markdown content using OpenAI API.
    
    Args:
        markdown_content: The markdown content to generate cards from
        num_cards: Number of cards to generate
        card_type: Type of cards to generate (definitions, concepts, mixed)
    
    Returns:
        List of Card objects
    """
    # Get OpenAI API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
        return []
    
    openai.api_key = api_key
    
    # Prepare the prompt
    prompt_template = f"""You are an assistant that creates flashcards. Given the following content extracted from a PDF document, generate exactly {num_cards} flashcards in Q&A format suitable for Anki (basic card).

Focus on {card_type if card_type != 'mixed' else 'key concepts, definitions, and important details'}.

IMPORTANT: 
- Provide output ONLY as a numbered list of questions and answers.
- Format EXACTLY as shown below:
1. Question: [question text]
   Answer: [answer text]

2. Question: [question text]
   Answer: [answer text]

- Do not include any other text, explanations, or formatting.
- Ensure mathematical expressions are wrapped in $...$ for inline math or $$...$$ for display math.
- Keep questions clear and concise.
- Keep answers comprehensive but not overly verbose.

Content:
{markdown_content[:4000]}  # Limit content to avoid token limits
"""

    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
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
        pattern = r'\d+\.\s*Question:\s*(.*?)\n\s*Answer:\s*(.*?)(?=\n\d+\.|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for i, (question, answer) in enumerate(matches):
            # Clean up the text
            question = question.strip()
            answer = answer.strip()
            
            if question and answer:
                card = Card(
                    question=question,
                    answer=answer,
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
            "Card type focus",
            ["mixed", "definitions", "concepts", "facts"],
            help="What type of content to focus on when generating cards"
        )
        
        # OpenAI API key check
        st.subheader("OpenAI API")
        if os.getenv("OPENAI_API_KEY"):
            st.success("✅ API key configured")
        else:
            st.warning("⚠️ Please set OPENAI_API_KEY environment variable")
    
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
            
            # Generate cards button
            if st.button("🎴 Generate Anki Cards", type="primary"):
                with st.spinner(f"Generating {num_cards} Anki cards..."):
                    cards = generate_anki_cards(
                        st.session_state.markdown_content,
                        num_cards=num_cards,
                        card_type=card_type
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
           - Map fields: Field 1 → Front, Field 2 → Back
           - Click Import
        
        **Note**: Make sure the Marker API server is running at the specified URL (default: http://localhost:8000)
        """)


if __name__ == "__main__":
    main()
