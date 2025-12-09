# PDF2Anki Streamlit Interface Guide

This guide explains how to use the PDF2Anki web interface built with Streamlit.

## Prerequisites

1. **Marker API Server**: Make sure the Marker API server is running at http://localhost:8000
   - Navigate to the `marker-api` directory
   - Run the server with appropriate setup (see marker-api documentation)

2. **OpenAI API Key**: You need an OpenAI API key for card generation
   - Create a `.env` file in the project root
   - Add your API key: `OPENAI_API_KEY=your_key_here`
   - See `docs/env_setup.md` for detailed instructions

## Starting the Interface

### Option 1: Using the startup script (Recommended)
```bash
./run_streamlit.sh
```

### Option 2: Manual startup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run src/streamlit_app.py
```

The interface will open in your default web browser at http://localhost:8501

## Using the Interface

### 1. Upload PDF
- Click "Browse files" in the upload section
- Select your PDF file (lecture slides, academic papers, etc.)
- The file details will be displayed

### 2. Convert to Markdown
- Click the "Convert to Markdown" button
- Wait for the conversion to complete
- A success message will appear when done

### 3. Generate Anki Cards
- Configure settings in the sidebar:
  - Number of cards to generate (1-50)
  - Card type focus (mixed, definitions, concepts, facts)
- Click "Generate Anki Cards"
- The AI will create flashcards based on the content

### 4. Review Generated Cards
- Cards are displayed in expandable sections
- Each card shows:
  - Question (front of card)
  - Answer (back of card)
  - Tags for organization

### 5. Download Results
- **Download Markdown**: Get the converted markdown file
- **Download TSV for Anki**: Get the cards in Anki-importable format

## Importing Cards to Anki

1. Open Anki Desktop
2. Go to **File → Import**
3. Select the downloaded TSV file
4. Configure import settings:
   - Field separator: Tab
   - Allow HTML in fields: Yes (for LaTeX support)
   - Field mapping:
     - Field 1 → Front
     - Field 2 → Back
     - Field 3 → Tags (if present)
5. Click Import

## Features

- **Real-time conversion**: See your PDF converted to Markdown instantly
- **AI-powered card generation**: Uses GPT-4 to create meaningful flashcards
- **LaTeX support**: Mathematical expressions are preserved with $ delimiters
- **Customizable generation**: Choose number of cards and focus type
- **Preview before download**: Review all cards before importing to Anki

## Troubleshooting

### "Marker API connection failed"
- Ensure Marker API server is running at the specified URL
- Check the URL in the sidebar settings
- Verify no firewall is blocking the connection

### "OpenAI API key not found"
- Create a `.env` file in the project root
- Add: `OPENAI_API_KEY=your_api_key_here`
- Restart the Streamlit app

### "Error generating cards"
- Check your OpenAI API key is valid
- Ensure you have API credits available
- Try reducing the number of cards requested
- Check if the PDF content is readable (not scanned images)

### Cards not displaying properly in Anki
- Ensure Anki has LaTeX support enabled
- Check that mathematical expressions are wrapped in $ symbols
- Verify the TSV file is properly formatted (tab-separated)

## Tips for Best Results

1. **PDF Quality**: Use text-based PDFs rather than scanned images
2. **Content Length**: For very long PDFs, the system uses the first ~4000 characters
3. **Card Focus**: Select appropriate card type based on your content:
   - "definitions" for term-heavy content
   - "concepts" for theoretical material
   - "facts" for data and statistics
   - "mixed" for general content
4. **Review Cards**: Always review generated cards before importing
5. **Batch Processing**: Process multiple PDFs sequentially for large study sets
