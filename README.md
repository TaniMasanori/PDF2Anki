# PDF2Anki

Convert PDF documents (lecture slides, academic papers) to Anki flashcards using AI.

## Features

- 📄 **PDF to Markdown conversion** using Marker API
- 🤖 **AI-powered flashcard generation** using GPT-4
- 🎴 **Anki-ready TSV export** for easy import
- 🌐 **Web interface** built with Streamlit
- 📐 **LaTeX support** for mathematical expressions
- 🏷️ **Automatic tagging** for card organization

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Marker API server running (see `marker-api/` directory)
- OpenAI API key

### 2. Setup

```bash
# Clone the repository
git clone <repository-url>
cd PDF2Anki

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
echo "MARKER_API_BASE=http://localhost:8000" >> .env
```

### 3. Start Marker API Server

```bash
cd marker-api
# Follow marker-api setup instructions
python server.py  # or use Docker
```

### 4. Launch Web Interface

```bash
# From project root
./run_streamlit.sh
```

Or manually:
```bash
streamlit run src/streamlit_app.py
```

## Usage

1. **Upload PDF**: Select your PDF file in the web interface
2. **Convert**: Click "Convert to Markdown" 
3. **Generate**: Click "Generate Anki Cards" with your desired settings
4. **Download**: Get the TSV file for Anki import
5. **Import**: Open Anki → File → Import → Select TSV file

## Project Structure

```
PDF2Anki/
├── src/
│   ├── streamlit_app.py    # Web interface
│   ├── marker_client.py    # PDF to Markdown conversion
│   └── pdf2anki_types.py   # Data structures
├── marker-api/             # Marker PDF conversion service
├── docs/                   # Documentation
├── outputs/                # Conversion outputs
├── requirements.txt        # Python dependencies
└── run_streamlit.sh        # Startup script
```

## Documentation

- [Streamlit Interface Guide](docs/streamlit_interface_guide.md)
- [Environment Setup](docs/env_setup.md)
- [Project Plan](Project_plan.md)

## Development

This project uses:
- **Streamlit** for the web interface
- **Marker PDF** for PDF to Markdown conversion
- **OpenAI GPT-4** for flashcard generation
- **Python** for scripting and integration

## License

See [LICENSE](LICENSE) file for details.
