# Streamlit Web Interface Implementation for PDF2Anki

Date: 2025-10-23

## Overview

In this session, we implemented a complete web-based user interface for the PDF2Anki project using Streamlit. This interface allows users to easily upload PDF files, convert them to Markdown using marker-pdf, generate Anki flashcards using AI, and download the results.

## What We Accomplished

### 1. Created Streamlit Web Application (`src/streamlit_app.py`)

The main application provides:
- **PDF Upload Interface**: Simple drag-and-drop or file browser upload
- **Marker API Integration**: Converts PDFs to Markdown using the existing `marker_client.py`
- **AI-Powered Card Generation**: Uses OpenAI GPT-4 to generate flashcards from Markdown content
- **TSV Export**: Formats cards for Anki import using the `Card.to_tsv_row()` method
- **Download Functionality**: Users can download both Markdown and TSV files

Key features implemented:
- Session state management for smooth user experience
- Real-time conversion status updates
- Preview of generated cards before download
- Configurable settings (number of cards, card type focus)
- Error handling and user feedback

### 2. Updated Dependencies

Added to `requirements.txt`:
- `streamlit>=1.29.0` - Web framework
- `openai>=1.3.0` - For GPT-4 API access
- `python-dotenv>=1.0.0` - Environment variable management

### 3. Created Supporting Documentation

- **`docs/env_setup.md`**: Instructions for setting up environment variables, particularly the OpenAI API key
- **`docs/streamlit_interface_guide.md`**: Comprehensive user guide including:
  - Prerequisites and setup instructions
  - Step-by-step usage guide
  - Troubleshooting common issues
  - Tips for best results
- **`README.md`**: Project overview with quick start guide

### 4. Created Startup Script

- **`run_streamlit.sh`**: Bash script that:
  - Creates/activates virtual environment
  - Installs dependencies
  - Checks for `.env` file
  - Launches Streamlit app

### 5. Integration with Existing Code

Successfully integrated with:
- `src/marker_client.py`: For PDF to Markdown conversion
- `src/pdf2anki_types.py`: Using the `Card` class and its `to_tsv_row()` method (renamed from types.py to avoid conflict with Python's built-in types module)
- Marker API server: Communicates via HTTP requests

## Technical Implementation Details

### PDF to Markdown Conversion
- Uses the existing `convert_pdf_to_markdown()` function
- Handles temporary file storage for uploaded PDFs
- Manages conversion results in session state

### AI Card Generation
- Implements prompt engineering for consistent output format
- Handles token limits by truncating content to 4000 characters
- Parses GPT-4 responses using regex to extract Q&A pairs
- Preserves LaTeX formatting with $ delimiters

### User Interface Design
- Two-column layout for upload and results
- Sidebar for configuration settings
- Expandable sections for card preview
- Clear visual feedback with success/error messages

## Usage Workflow

1. Start Marker API server
2. Set OpenAI API key in `.env` file
3. Run `./run_streamlit.sh`
4. Upload PDF through web interface
5. Convert to Markdown
6. Generate Anki cards with AI
7. Download TSV file
8. Import to Anki Desktop

## Future Enhancements

Potential improvements identified:
- Support for batch PDF processing
- Advanced chunking for very large PDFs
- Custom prompt templates
- Direct Anki integration via AnkiConnect
- Image-based question generation
- Progress bars for long operations
- Card editing before export

## Files Modified/Created

- Created: `src/streamlit_app.py`
- Created: `run_streamlit.sh`
- Created: `docs/env_setup.md`
- Created: `docs/streamlit_interface_guide.md`
- Created: `README.md`
- Modified: `requirements.txt`

## Testing Notes

The complete workflow was tested and verified to work:
1. PDF upload ✓
2. Markdown conversion via Marker API ✓
3. AI card generation ✓
4. TSV export with proper formatting ✓
5. Download functionality ✓

## Conclusion

Successfully delivered a fully functional web interface that meets all requirements:
- ✅ Browser-based UI using Streamlit
- ✅ PDF upload functionality
- ✅ PDF to MD conversion using marker-pdf
- ✅ MD to TSV conversion for Anki import
- ✅ Download capability for both MD and TSV files

The implementation provides a user-friendly way to convert educational PDFs into Anki flashcards, significantly streamlining the study material preparation process.

## Post-Implementation Fix

After initial implementation, encountered an import error where Python was trying to import from the built-in `types` module instead of our local module. Fixed by:
- Renaming `src/types.py` to `src/pdf2anki_types.py`
- Updating import statement in `streamlit_app.py`
- This is a common Python issue when naming modules the same as built-in modules


## 2025-10-28 Additions

### Llama Prompt Command Generation

After converting a PDF to Markdown, the UI now provides a ready-to-run Bash script that posts the markdown content to an OpenAI-compatible LLM endpoint (e.g., llama.cpp server, vLLM) to generate cards. The script uses environment variables:

- `LLM_API_BASE` (default: `http://localhost:8080/v1`)
- `LLM_MODEL` (default: `llama-3.1-8b-instruct`)
- `LLM_API_KEY` (default: `no-key-required`)

Copy or download the script from the UI under “Generate LLM Prompt Command”. It reads the generated `.md` file and requests the LLM to output a numbered list of cards.

### Basic and Cloze Note Types

The UI supports selecting the Anki note type:
- Basic: Front/Back fields → TSV columns: `Question` and `Answer`
- Cloze: Cloze deletion with `{{c1::...}}` syntax → TSV columns: `Text` and optional `Extra`

When importing into Anki:
- Basic: Map Field 1 → Front, Field 2 → Back
- Cloze: Choose note type “Cloze”, map Field 1 → Text, Field 2 → Extra

Implementation touches:
- `src/pdf2anki_types.py`: `Card` now has `note_type` and `extra`, and `to_tsv_row()` adapts layout for Basic/Cloze.
- `src/streamlit_app.py`: Sidebar options for note type, LLM API configuration, and prompt command generation section.
