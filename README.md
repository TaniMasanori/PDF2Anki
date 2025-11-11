# PDF2Anki

Convert PDF documents (lecture slides, academic papers) to Anki flashcards using AI.

## Features

- **PDF to Markdown conversion** using Marker API
- **AI-powered flashcard generation** using OpenAI GPT models or compatible LLMs
- **Anki-ready TSV export** for easy import
- **Web interface** built with Streamlit
- **MathJax/LaTeX support** for mathematical expressions
- **Automatic tagging** for card organization
- **Intelligent chunking** for better card generation from long documents

## Installation Guide

### Step 1: Prerequisites

Before you begin, make sure you have:

1. **Python 3.8 or higher** installed
   - Check your Python version: `python3 --version` or `python --version`
   - Download from [python.org](https://www.python.org/downloads/) if needed

2. **OpenAI API key** (for AI card generation)
   - Sign up at [platform.openai.com](https://platform.openai.com/)
   - Get your API key from [API Keys page](https://platform.openai.com/api-keys)
   - You'll need a paid account or credits

3. **Marker API server** (for PDF to Markdown conversion)
   - This will be set up in Step 3
   - Requires Python 3.10+ for the Marker API server

### Step 2: Clone and Setup the Repository

```bash
# Clone the repository
git clone <repository-url>
cd PDF2Anki

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Verify installation**: Run `pip list` to confirm packages are installed.

### Step 3: Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
# Create .env file
touch .env  # On Windows: type nul > .env
```

Edit the `.env` file with your preferred text editor and add the following:

#### Option A: Using OpenAI (Recommended for beginners)

```bash
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-turbo
MARKER_API_BASE=http://localhost:8000
```

**Getting your OpenAI API key**:
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key and paste it in your `.env` file

**Available OpenAI models**:
- `gpt-4-turbo` (default, recommended)
- `gpt-5-mini` (cost-effective)
- `gpt-4o` (latest)
- Note: `gpt-4-turbo-preview` is deprecated

#### Option B: Using Local LLM (Advanced)

If you have a local LLM server running (e.g., llama.cpp, vLLM, LM Studio):

```bash
LLM_API_BASE=http://localhost:8080/v1
LLM_MODEL=llama-3.1-8b-instruct
LLM_API_KEY=no-key-required
MARKER_API_BASE=http://localhost:8000
```

**Important**: Make sure `.env` is in `.gitignore` (it should be by default) to keep your API keys secure.

### Step 4: Setup Marker API Server

The Marker API server converts PDFs to Markdown. You need to set it up separately.

#### 4.1 Clone Marker API Repository

```bash
# Navigate to project root (if not already there)
cd PDF2Anki

# Clone Marker API repository
git clone https://github.com/VikParuchuri/marker.git marker-api
cd marker-api
```

#### 4.2 Install Marker API Dependencies

```bash
# Create virtual environment for Marker API
python3 -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Upgrade pip
python -m pip install -U pip

# Install Marker API
pip install -e .
```

**Note**: Marker API requires Python 3.10 or higher. Installation may take several minutes as it downloads models.

#### 4.3 Start Marker API Server

**Important**: Keep this terminal window open while using PDF2Anki.

```bash
# Make sure you're in the marker-api directory
cd marker-api

# Activate virtual environment (if not already activated)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start the server
python server.py --host 0.0.0.0 --port 8000
```

**What to expect**:
- First startup will download models (this can take 5-10 minutes)
- You'll see "Application startup complete" when ready
- The server will keep running until you stop it (Ctrl+C)

**Verify the server is running**:
1. Open your browser and go to: `http://localhost:8000/health`
2. You should see `{"status":"ok"}` or similar
3. API documentation: `http://localhost:8000/docs`
4. Optional Gradio UI: `http://localhost:8000/gradio`

**Troubleshooting**:
- If port 8000 is in use, change the port: `python server.py --host 0.0.0.0 --port 8888`
- Update `MARKER_API_BASE` in your `.env` file to match the port you're using

### Step 5: Launch Streamlit Web Interface

**Important**: Make sure the Marker API server is running (Step 4) before starting Streamlit.

Open a **new terminal window** (keep the Marker API server terminal open) and run:

```bash
# Navigate to project root
cd PDF2Anki

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Start Streamlit app
streamlit run src/streamlit_app.py
```

**Alternative**: Use the provided script:
```bash
./run_streamlit.sh  # On Linux/Mac
```

The Streamlit app will automatically open in your browser at `http://localhost:8501`

If it doesn't open automatically, manually navigate to: `http://localhost:8501`

### Step 6: Configure Settings in Web Interface

When the Streamlit app opens:

1. **Check the left sidebar** - you'll see "Settings" section
2. **Marker API URL**: Verify it matches your Marker API server port
   - Default: `http://localhost:8000`
   - If you changed the port, update this field
3. **LLM API**: Check that your LLM configuration is detected
   - Should show "Using OpenAI (model: gpt-4-turbo)" or similar
   - If not, verify your `.env` file is correct and restart Streamlit

**Quick verification**:
- Check the terminal where Marker API is running - it should show: `INFO: Uvicorn running on http://0.0.0.0:8000`
- The port number in Streamlit must match this port

## Usage Guide

### First Time Setup Checklist

Before using the app, verify:

- [ ] Marker API server is running (Step 4)
- [ ] Streamlit app is running (Step 5)
- [ ] `.env` file is configured with your API key (Step 3)
- [ ] Marker API URL in Streamlit sidebar matches your server port (Step 6)

### Creating Your First Anki Cards

1. **Upload PDF**
   - Click "Choose a PDF file" button
   - Select your PDF document (lecture slides, papers, etc.)
   - File will be uploaded and displayed

2. **Convert PDF to Markdown**
   - Click "Convert to Markdown" button
   - Wait for conversion to complete (may take 30 seconds to a few minutes)
   - You'll see a success message when done
   - Optionally preview the markdown in the expandable section

3. **Configure Card Generation Settings** (in sidebar)
   - **Number of cards**: How many flashcards to generate (default: 10)
   - **Content focus**: Choose what to focus on (mixed, definitions, concepts, facts)
   - **Anki note type**: Basic (Front/Back) or Cloze deletion
   - **Use intelligent chunking**: Recommended for better results (enabled by default)
   - **Max tokens per chunk**: Adjust if needed (default: 2000)

4. **Generate Anki Cards**
   - Click "Generate Anki Cards" button
   - Processing may take 1-5 minutes depending on document size
   - You can click "Stop Generation" to cancel if needed
   - Cards will appear below when generation completes

5. **Review Generated Cards**
   - Expand each card to review the content
   - Cards include mathematical expressions in MathJax format
   - Tags are automatically added for organization

6. **Download Results**
   - **Markdown file**: Download the converted markdown (optional)
   - **TSV file**: Download the Anki-ready TSV file

7. **Import into Anki**
   - Open Anki Desktop application
   - Go to **File → Import**
   - Select the downloaded TSV file
   - Configure import settings:
     - **Field separator**: Tab
     - **Note type**: 
       - For Basic: Choose "Basic" and map Field 1 → Front, Field 2 → Back
       - For Cloze: Choose "Cloze" and map Field 1 → Text, Field 2 → Extra
   - Click **Import**
   - Your cards will appear in Anki!

### Tips for Best Results

- **Mathematical expressions**: Automatically converted to MathJax format (`\(...\)` for inline, `\[...\]` for display)
- **Long documents**: Use chunking for better card quality
- **Card count**: Start with 10-20 cards, then adjust based on results
- **Content focus**: Use "definitions" for terminology-heavy documents, "concepts" for conceptual material

## Troubleshooting

### Common Issues and Solutions

#### Issue: "404 Client Error: Not Found for url: http://localhost:XXXX/convert"

**Cause**: Marker API server is not running or URL is incorrect.

**Solution**:
1. Check if Marker API server is running in its terminal window
2. Look for "Application startup complete" message
3. Verify the port number in the terminal (e.g., `INFO: Uvicorn running on http://0.0.0.0:8000`)
4. Update "Marker API URL" in Streamlit sidebar to match the port
5. Test the server: Open `http://localhost:8000/health` in your browser (should show `{"status":"ok"}`)

#### Issue: "Connection refused" or "Connection error"

**Cause**: Marker API server is not accessible.

**Solution**:
1. Make sure Marker API server is running (check the terminal)
2. Wait for models to load on first startup (can take 5-10 minutes)
3. Check firewall settings if using a different machine
4. Verify you're using the correct port number
5. Try restarting the Marker API server

#### Issue: Streamlit can't connect to Marker API

**Cause**: Server startup order or configuration issue.

**Solution**:
1. **Always start Marker API server FIRST**, then Streamlit
2. Check both are running in separate terminal windows
3. Verify Marker API URL in Streamlit sidebar matches the server port
4. Restart both servers if needed
5. Check for port conflicts (another application using port 8000)

#### Issue: "No LLM configured. Set LLM_API_BASE for Llama or OPENAI_API_KEY for OpenAI."

**Cause**: Missing or incorrect `.env` file configuration.

**Solution**:
1. Check that `.env` file exists in the project root directory
2. Verify `.env` contains `OPENAI_API_KEY=sk-...` (with your actual key)
3. Make sure there are no extra spaces or quotes around the API key
4. Restart Streamlit after updating `.env`
5. Check the sidebar shows "Using OpenAI (model: ...)" when configured correctly

#### Issue: "API Quota Exceeded" or Error code: 429

**Cause**: OpenAI API quota or billing limit reached.

**Solution**:
1. Check your OpenAI account usage: https://platform.openai.com/usage
2. Verify payment method: https://platform.openai.com/account/billing
3. Add credits or upgrade your plan if needed
4. Wait for monthly quota reset
5. Consider using a local LLM server (set `LLM_API_BASE` in `.env`) to avoid API costs

#### Issue: "Model Not Found" error

**Cause**: Invalid or unsupported model name.

**Solution**:
1. Check your `OPENAI_MODEL` setting in `.env`
2. Use a valid model name: `gpt-4-turbo`, `gpt-5-mini`, `gpt-4o`
3. Note: `gpt-4-turbo-preview` is deprecated
4. Verify you have access to the model in your OpenAI account

#### Issue: Cards not generating or empty results

**Cause**: Various possible issues.

**Solution**:
1. Check that PDF conversion completed successfully
2. Verify markdown content is visible in preview
3. Try reducing the number of cards requested
4. Check for error messages in the Streamlit interface
5. Verify your API key is valid and has credits
6. Try with a simpler PDF document first

#### Issue: Mathematical expressions not rendering in Anki

**Cause**: Anki not configured for MathJax.

**Solution**:
1. Cards are generated with MathJax format (`\(...\)` and `\[...\]`)
2. Anki should render these automatically
3. If not working, check Anki's MathJax settings
4. Ensure you're using a recent version of Anki Desktop

### Getting Help

If you encounter issues not covered here:

1. Check the terminal output for both Marker API and Streamlit servers
2. Review error messages in the Streamlit interface
3. Verify all prerequisites are met (Python version, API keys, etc.)
4. Check the [documentation](docs/) folder for detailed guides

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

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

See [LICENSE](LICENSE) file for details.

### Why GPL v3?

This project uses GPL-3.0-licensed dependencies (marker-api and marker-pdf), which require the entire project to be licensed under GPL v3 to maintain license compatibility.
