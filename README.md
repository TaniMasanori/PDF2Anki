# PDF2Anki

Convert PDF documents (lecture slides, academic papers) to Anki flashcards using AI.

## Quick Start for Reviewers (One-Click Setup)

We have provided automated scripts to handle all setup, dependency installation, and server launching.

### Prerequisites

1.  **Python 3.10+** installed.
2.  **OpenAI API Key**: You will be prompted to enter this in the generated `.env` file.
    *   *Note*: If obtaining an API key is difficult, please email `samuel_reinehr_sw@mines.edu` to schedule a demo/discussion as per the submission guidelines.

### How to Run

**Windows**:
Double-click `setup_and_run.bat` or run it from Command Prompt:
```cmd
setup_and_run.bat
```

**Mac / Linux**:
Run the shell script:
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

**What the script does**:
1.  Updates git submodules (`marker-api`).
2.  Creates a virtual environment (`venv`).
3.  Installs all dependencies (and fixes version conflicts).
4.  Creates a `.env` file (you will need to add your API key).
5.  Launches the **Marker API Server** (in a separate terminal).
6.  Launches the **Streamlit Web App** (opens in your default browser).

---

## Manual Installation Guide (Legacy)

If the automated scripts above do not work for your environment, please follow these manual steps.

### Step 1: Prerequisites

Before you begin, make sure you have:

1. **Python 3.10 or higher** installed (Python 3.11 recommended)
   - Check your Python version: `python3 --version` or `python --version`
   - Download from [python.org](https://www.python.org/downloads/) if needed
   - **Recommended**: Use [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for easier dependency management

2. **OpenAI API key** (for AI card generation)
   - Sign up at [platform.openai.com](https://platform.openai.com/)
   - Get your API key from [API Keys page](https://platform.openai.com/api-keys)
   - You'll need a paid account or credits

3. **Marker API server** (for PDF to Markdown conversion)
   - This will be set up in Step 4
   - Requires Python 3.10+ (included in marker-api submodule)

### Step 2: Clone and Setup the Repository

```bash
# Clone the repository (include submodules)
git clone --recurse-submodules <repository-url>
cd PDF2Anki

# If you already cloned without submodules, run:
git submodule update --init --recursive
```

#### Option A: Using Conda (Recommended)

```bash
# Create and activate conda environment
conda create -n pdf2anki python=3.11 -y
conda activate pdf2anki

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using venv

```bash
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

**Verify installation**: 
```bash
pip list | grep -E "streamlit|openai"
# Should show: streamlit and openai packages
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
# Create .env file (make sure you're in PDF2Anki directory)
cd PDF2Anki

# Option 1: Create with echo commands
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
echo "OPENAI_MODEL=gpt-4o-mini" >> .env
echo "MARKER_API_BASE=http://localhost:8080" >> .env

# Option 2: Or create manually
touch .env  # On Windows: type nul > .env
# Then edit with your text editor
```

#### Option A: Using OpenAI (Recommended for beginners)

Edit `.env` file to contain:

```bash
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini
MARKER_API_BASE=http://localhost:8080
```

**Important**: Replace `sk-your-api-key-here` with your actual OpenAI API key!

**Getting your OpenAI API key**:
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key and paste it in your `.env` file

**Available OpenAI models**:
- `gpt-4o-mini` (cost-effective, recommended)
- `gpt-4o` (more powerful)
- `gpt-4-turbo` (legacy)

#### Option B: Using Local LLM (Advanced)

If you have a local LLM server running (e.g., llama.cpp, vLLM, LM Studio):

```bash
LLM_API_BASE=http://localhost:8081/v1
LLM_MODEL=llama-3.1-8b-instruct
LLM_API_KEY=no-key-required
MARKER_API_BASE=http://localhost:8080
```

**Important**: Make sure `.env` is in `.gitignore` (it should be by default) to keep your API keys secure.

### Step 4: Setup Marker API Server

The Marker API server converts PDFs to Markdown. You need to set it up separately.

#### 4.1 Initialize Marker API submodule

```bash
# From the project root (if not already there)
cd PDF2Anki

# Ensure the submodule is initialized and up-to-date
git submodule update --init --recursive

# Enter the submodule directory
cd marker-api
```

Note: To update the submodule to a newer version later:

```bash
cd marker-api
git fetch origin
git checkout <tag-or-commit>
cd ..
git add marker-api
git commit -m "chore: bump marker-api submodule"
```

#### 4.2 Install Marker API Dependencies

Use the **same environment** you created in Step 2:

```bash
# Make sure you're in the project root
cd PDF2Anki

# Activate the environment you created in Step 2
# For Conda:
conda activate pdf2anki
# For venv:
# source venv/bin/activate

# Navigate to marker-api directory
cd marker-api

# Install Marker API and all dependencies (this may take 5-10 minutes)
pip install -e .

# Fix transformers version compatibility (Important!)
pip install transformers==4.41.0

# Go back to project root
cd ..
```

**Verify installation**:
```bash
python -c "import marker; print('Marker installed successfully')"
```

**Note**: 
- Installation downloads large packages (PyTorch ~2GB, etc.) - this may take 5-10 minutes
- The `transformers==4.41.0` fix is **required** to avoid `KeyError: 'sdpa'` error
- If you see import errors, ensure you're in the correct conda/venv environment

#### 4.3 Start Marker API Server

**Important**: Keep this terminal window open while using PDF2Anki.

**Option A: Standard startup (recommended for first-time users)**

```bash
# Make sure you're in the marker-api directory
cd marker-api

# Activate environment
# For Conda:
conda activate pdf2anki
# For venv:
# source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the server (default port is 8080)
python server.py --host 0.0.0.0 --port 8080
```

**Option B: Optimized startup (for faster conversion)**

If you want to speed up PDF conversion, use the optimized startup script:

```bash
# Make sure you're in the marker-api directory
cd marker-api

# Use the optimized startup script (automatically detects GPU and optimizes settings)
./run_optimized.sh
```

The optimized script will:
- Automatically detect and enable GPU if available
- Set optimal memory settings based on your hardware
- Provide better performance for PDF conversion

**For more optimization options**, see [PDF Conversion Optimization Guide](docs/20251113_pdf_conversion_optimization.md).

**What to expect**:
- First startup will download models (this can take 5-10 minutes)
- You'll see output like:
  ```
  Loaded detection model vikp/surya_det3 on device cpu...
  Loaded detection model vikp/surya_layout3 on device cpu...
  Loaded reading order model vikp/surya_order on device cpu...
  Loaded recognition model vikp/surya_rec2 on device cpu...
  INFO:     Uvicorn running on http://0.0.0.0:8080
  ```
- The server will keep running until you stop it (Ctrl+C)

**Verify the server is running** (in a new terminal):
```bash
curl http://localhost:8080/health
# Expected output: {"message":"Welcome to Marker-api","type":"simple"}
```

Or open in browser: `http://localhost:8080/health`

**Troubleshooting**:
- Update `MARKER_API_BASE` in your `.env` file to match the port you're using
- If you see `KeyError: 'sdpa'` error, run: `pip install transformers==4.41.0`
- For performance issues, see the [optimization guide](docs/20251113_pdf_conversion_optimization.md)

### Step 5: Launch Streamlit Web Interface

**Important**: Make sure the Marker API server is running (Step 4) before starting Streamlit.

Open a **new terminal window** (keep the Marker API server terminal open) and run:

```bash
# Navigate to project root
cd PDF2Anki

# Activate environment
# For Conda:
conda activate pdf2anki
# For venv:
# source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start Streamlit app
streamlit run src/streamlit_app.py
```

**Alternative**: Use the provided script:
```bash
./run_streamlit.sh  # On Linux/Mac
```

**What to expect**:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

The Streamlit app will automatically open in your browser at `http://localhost:8501`

If it doesn't open automatically, manually navigate to: `http://localhost:8501`

**Verify both servers are running**:
- Marker API: `http://localhost:8080/health` should return JSON
- Streamlit: `http://localhost:8501` should show the web interface

### Step 6: Configure Settings in Web Interface

When the Streamlit app opens:

1. **Check the left sidebar** - you'll see "Settings" section
2. **Marker API URL**: Verify it matches your Marker API server port
   - Default: `http://localhost:8080`
   - If you changed the port, update this field
3. **LLM API**: Check that your LLM configuration is detected
   - Should show "Using OpenAI (model: gpt-4o-mini)" or similar
   - If not, verify your `.env` file is correct and restart Streamlit

**Quick verification**:
- Check the terminal where Marker API is running - it should show: `INFO: Uvicorn running on http://0.0.0.0:8080`
- The port number in Streamlit must match this port

## Usage Guide

### Installation Verification Checklist

After completing all installation steps, verify everything is working:

| Check | Command/Action | Expected Result |
|-------|---------------|-----------------|
| Python version | `python --version` | 3.10 or higher |
| Conda env active | `conda info --envs` | `pdf2anki` with `*` |
| Marker installed | `python -c "import marker"` | No error |
| .env file exists | `cat .env` | Shows API key config |
| Marker API running | `curl localhost:8080/health` | JSON response |
| Streamlit running | Open `localhost:8501` | Web interface |

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
3. Verify the port number in the terminal (e.g., `INFO: Uvicorn running on http://0.0.0.0:8080`)
4. Update "Marker API URL" in Streamlit sidebar to match the port
5. Test the server: Open `http://localhost:8080/health` in your browser

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
5. Check for port conflicts (another application using port 8080)

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
2. Use a valid model name: `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`
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

#### Issue: `KeyError: 'sdpa'` when starting Marker API server

**Cause**: Incompatibility between transformers and surya-ocr versions.

**Solution**:
1. This is automatically handled by the setup scripts. If running manually:
```bash
conda activate pdf2anki  # or activate your venv
pip install transformers==4.41.0
```
Then restart the server.

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
├── marker-api/             # Marker API (git submodule)
├── docs/                   # Documentation
├── outputs/                # Conversion outputs
├── requirements.txt        # Python dependencies
├── setup_and_run.bat       # Windows setup script
├── setup_and_run.sh        # Mac/Linux setup script
└── run_streamlit.sh        # Startup script
```

## Architecture Flowchart

```mermaid
flowchart TD
    U[User (Browser/Streamlit UI)] -->|Upload PDF| A[streamlit_app.py\nUpload handling]
    A --> B[Compute SHA256 and create session dir\noutputs/<timestamp>_<pdf_name>/]
    A -->|Click Convert to Markdown| C[marker_client.convert_pdf_to_markdown]
    
    subgraph Marker API Service
        MAPI[/POST /convert/]
    end
    C -->|Send PDF| MAPI
    MAPI -->|Receive markdown, meta| D[Save marker.md, meta.json\n(temp conv_dir)]
    D --> E[Copy to session output:\nconverted.md, meta.json]
    E --> F[Show Markdown preview]
    
    F -->|Generate Anki Cards| G[Select LLM config\n(LLM_API_BASE or OPENAI)]
    G --> H{Use intelligent chunking?}
    
    subgraph Chunking Path
        direction TB
        I[markdown_processor_wrapper\n.clean_markdown] --> J[.chunk_markdown\n(max_tokens)]
        J --> K[semantic_detector:\ndefinitions/key terms/concept boundaries]
        K --> L[anki_core.build_prompt\n(chunk + semantics)]
        L --> LL[LLM call\nopenai.chat.completions.create]
        LL --> LM[anki_core.parse_cards_from_output\n→ Cards]
    end
    
    subgraph Non-chunking Path
        direction TB
        N[anki_core.build_prompt\n(full text)] --> NL[LLM call]
        NL --> NM[parse_cards_from_output\n→ Cards]
    end
    
    H -- yes --> I
    H -- no --> N
    
    I & J & K & L & LL & LM --> O[Aggregate cards]
    N & NL & NM --> O
    O --> P[Generate TSV\noutputs/<session>/anki_cards.tsv]
    P --> Q[Download buttons\n(Markdown / TSV)]
    Q --> R[Import into Anki]
```

See also: `docs/20251113_pdf2anki_flowchart.md` for the Japanese-annotated version.

## Documentation

- [Streamlit Interface Guide](docs/streamlit_interface_guide.md)
- [Environment Setup](docs/env_setup.md)
- [Marker API Setup (JP)](docs/20251104_marker_api_setup.md)
- [PDF Conversion Optimization Guide](docs/20251113_pdf_conversion_optimization.md) - Speed up PDF conversion
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
