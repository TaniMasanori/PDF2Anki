#!/bin/bash

# Script to run the PDF2Anki Streamlit app

echo "Starting PDF2Anki Streamlit app..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please create one based on docs/env_setup.md"
    echo "You'll need to set OPENAI_API_KEY for card generation to work."
fi

# Run Streamlit app
echo "Starting Streamlit app..."
streamlit run src/streamlit_app.py --server.port 8501 --server.address localhost
