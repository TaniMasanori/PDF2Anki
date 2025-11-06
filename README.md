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

**Important**: You need to run Marker API server in a **separate terminal** before starting Streamlit.

Open a new terminal and run:

```bash
# Navigate to marker-api directory
cd marker-api

# (Optional) Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (first time only)
python -m pip install -U pip
pip install -e .

# Start the server (default port: 8000)
python server.py --host 0.0.0.0 --port 8000
```

**Note**: 
- Marker API requires Python 3.10+
- The server will take some time to load models on first startup
- Keep this terminal open while using the application

**Verify the server is running**:
- Health check: Open `http://localhost:8000/health` in your browser
- API docs: Open `http://localhost:8000/docs` in your browser
- Gradio UI: Open `http://localhost:8000/gradio` in your browser (optional)

### 4. Launch Streamlit Web Interface

Open a **new terminal** (keep the Marker API server running in the first terminal) and run:

```bash
# Navigate to project root
cd PDF2Anki

# Activate virtual environment (if not already activated)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start Streamlit app
./run_streamlit.sh
```

Or manually:
```bash
streamlit run src/streamlit_app.py
```

The Streamlit app will open automatically in your browser at `http://localhost:8501`

### 5. Configure Marker API URL in Browser

After the Streamlit app opens in your browser:

1. **Look at the left sidebar** - you'll see "⚙️ Settings" section
2. **Find "Marker API" subsection**
3. **In the "Marker API URL" text field**, enter:
   - `http://localhost:8000` (if Marker API is running on port 8000)
   - `http://localhost:8888` (if Marker API is running on port 8888)
   - Or any other port where your Marker API server is running

**Important**: The Marker API URL in Streamlit must match the port where your Marker API server is actually running. The default is port 8000, but you can use any available port.

**Quick check**: If you're not sure which port Marker API is using, check the terminal where you started the server - it will show something like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Usage

Once both servers are running and the Marker API URL is configured:

1. **Upload PDF**: Select your PDF file in the web interface
2. **Convert**: Click "🔄 Convert to Markdown" button
   - Make sure the Marker API URL in the sidebar matches your running server
3. **Generate**: Click "🎴 Generate Anki Cards" with your desired settings
4. **Download**: Get the TSV file for Anki import
5. **Import**: Open Anki → File → Import → Select TSV file

## Troubleshooting

### "404 Client Error: Not Found for url: http://localhost:XXXX/convert"

This error means the Marker API server is not running or the URL is incorrect.

**Solution**:
1. Make sure Marker API server is running (check the terminal where you started it)
2. Verify the port number in the terminal output
3. Update the "Marker API URL" in Streamlit sidebar to match the correct port
4. Try accessing `http://localhost:XXXX/health` in your browser to verify the server is accessible

### "Connection refused" or "Connection error"

**Solution**:
1. Check if Marker API server is actually running
2. Verify the server started successfully (look for "Application startup complete" message)
3. Make sure you're using the correct port number
4. On first startup, wait for models to load (this can take several minutes)

### Streamlit can't connect to Marker API

**Solution**:
1. Ensure Marker API server is running **before** starting Streamlit
2. Check that both servers are running in separate terminals
3. Verify the Marker API URL in Streamlit sidebar matches the server port
4. Try restarting both servers

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
- [Marker API Setup (JP)](docs/20251104_marker_api_setup.md)
- [Project Plan](Project_plan.md)

## Development

This project uses:
- **Streamlit** for the web interface
- **Marker PDF** for PDF to Markdown conversion
- **OpenAI GPT-4** for flashcard generation
- **Python** for scripting and integration

## License

See [LICENSE](LICENSE) file for details.
