@echo off
setlocal

echo ==========================================
echo PDF2Anki Setup and Run Script
echo ==========================================

REM 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.10+.
    pause
    exit /b 1
)

REM 2. Initialize Submodules
echo.
echo [1/6] Updating git submodules...
git submodule update --init --recursive
if %errorlevel% neq 0 (
    echo Failed to update submodules.
    pause
    exit /b 1
)

REM 3. Setup Virtual Environment
if not exist venv (
    echo.
    echo [2/6] Creating virtual environment...
    python -m venv venv
) else (
    echo.
    echo [2/6] Virtual environment already exists.
)

REM Activate venv
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

REM 4. Install Dependencies
echo.
echo [3/6] Installing dependencies...
echo Installing root requirements...
pip install -r requirements.txt

echo Installing marker-api dependencies...
cd marker-api
pip install -e .
echo Fixing transformers version...
pip install transformers==4.41.0
cd ..

REM 5. Environment Configuration
echo.
echo [4/6] Checking configuration...
if not exist .env (
    echo Creating .env file...
    (
        echo OPENAI_API_KEY=
        echo OPENAI_MODEL=gpt-5-mini
        echo MARKER_API_BASE=http://localhost:8080
    ) > .env
    echo.
    echo ***************************************************************
    echo WARNING: .env file was created but API keys are missing.
    echo Please open .env file and add your OPENAI_API_KEY.
    echo ***************************************************************
    echo.
    echo Press any key to continue after you have added the key...
    echo (Or continue to run and configure later, but card generation will fail)
    pause
) else (
    echo .env file exists.
)

REM 6. Launch Servers
echo.
echo [5/6] Starting Marker API Server...
start "Marker API Server" cmd /k "call venv\Scripts\activate && cd marker-api && python server.py --port 8080"

echo.
echo Waiting for Marker API to initialize (5 seconds)...
timeout /t 5 /nobreak >nul

echo.
echo [6/6] Starting Streamlit App...
echo Opening browser...
streamlit run src\streamlit_app.py

pause
