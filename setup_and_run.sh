#!/bin/bash

echo "=========================================="
echo "PDF2Anki Setup and Run Script"
echo "=========================================="

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH. Please install Python 3.10+."
    exit 1
fi

# 2. Initialize Submodules
echo ""
echo "[1/6] Updating git submodules..."
git submodule update --init --recursive
if [ $? -ne 0 ]; then
    echo "Failed to update submodules."
    exit 1
fi

# 3. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo ""
    echo "[2/6] Creating virtual environment..."
    python3 -m venv venv
else
    echo ""
    echo "[2/6] Virtual environment already exists."
fi

# Activate venv
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# 4. Install Dependencies
echo ""
echo "[3/6] Installing dependencies..."
echo "Installing root requirements..."
pip install -r requirements.txt

echo "Installing marker-api dependencies..."
cd marker-api
pip install -e .
echo "Fixing transformers version..."
pip install transformers==4.41.0
cd ..

# 5. Environment Configuration
echo ""
echo "[4/6] Checking configuration..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
MARKER_API_BASE=http://localhost:8080
EOL
    echo ""
    echo "***************************************************************"
    echo "WARNING: .env file was created but API keys are missing."
    echo "Please open .env file and add your OPENAI_API_KEY."
    echo "***************************************************************"
    echo ""
    read -p "Press Enter to continue after you have added the key..."
else
    echo ".env file exists."
fi

# 6. Launch Servers
echo ""
echo "[5/6] Starting Marker API Server..."

# Check OS to determine how to open new terminal
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e 'tell app "Terminal" to do script "cd \"'"$(pwd)"'\" && source venv/bin/activate && cd marker-api && python server.py --port 8080"'
elif command -v gnome-terminal &> /dev/null; then
    # Linux (GNOME)
    gnome-terminal -- bash -c "source venv/bin/activate && cd marker-api && python server.py --port 8080; exec bash"
elif command -v xterm &> /dev/null; then
    # Linux (xterm)
    xterm -e "source venv/bin/activate && cd marker-api && python server.py --port 8080" &
else
    echo "Could not detect terminal emulator. Please run Marker API manually in another terminal:"
    echo "cd marker-api && python server.py --port 8080"
fi

echo ""
echo "Waiting for Marker API to initialize (5 seconds)..."
sleep 5

echo ""
echo "[6/6] Starting Streamlit App..."
echo "Opening browser..."
streamlit run src/streamlit_app.py
