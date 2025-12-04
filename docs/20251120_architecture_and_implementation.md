# Architecture and Implementation

This document details the technical architecture and implementation of the PDF2Anki system.

## 1. Streamlit UI

The user interface is built with Streamlit (`src/streamlit_app.py`), serving as the orchestration layer for the entire pipeline.

### 1.1. Core Components
- **Session State Management**: Streamlit's `session_state` is extensively used to persist data across re-runs (which happen on every user interaction). Key state variables include:
    - `conversion_done`: Tracks if PDF processing is complete.
    - `markdown_content`: Stores the converted text.
    - `cards`: Holds the generated list of `Card` objects.
    - `pdf_sha256`: Ensures content integrity and prevents duplicate processing.
- **Sidebar Configuration**: Allows users to configure:
    - **Marker API URL**: Endpoint for the PDF conversion service.
    - **Card Generation Settings**: Number of cards, content focus (definitions/concepts), and note type (Basic/Cloze).
    - **LLM Settings**: Model selection (OpenAI or Local LLM) and chunking parameters.

### 1.2. Workflow Logic
1.  **Upload**: Accepts PDF files and calculates SHA256 hash.
2.  **Conversion**: Triggers `marker_client` to send the file to the backend API.
3.  **Preview**: Displays the converted Markdown for user verification.
4.  **Generation**: Batches text chunks to the LLM and parses responses.
5.  **Export**: Generates TSV files and Markdown downloads.

## 2. Marker API and Services

The PDF conversion backend uses a microservices architecture defined in `marker-api/docker-compose.cpu.yml` (or `.gpu.yml`).

### 2.1. Service Architecture
- **App Service (`marker-api`)**: The entry point (Python server) running on port 8080. It accepts HTTP POST requests with PDF files.
- **Celery Worker**: Handles the heavy lifting of PDF processing asynchronously. It consumes tasks from the Redis queue.
- **Redis**: Acts as the message broker between the API server and the Celery workers.
- **Flower**: Provides a dashboard to monitor Celery tasks (port 5556).

### 2.2. Interface
- **Client**: `src/marker_client.py` implements a robust client with retry logic (exponential backoff).
- **Endpoint**: `POST /convert`
- **Payload**: Multipart/form-data containing the PDF file.
- **Response**: JSON containing the full Markdown text and metadata.

## 3. Flashcard Generation (TSV)

The core logic for transforming text into flashcards resides in `src/anki_core.py` and `src/pdf2anki_types.py`.

### 3.1. Data Structures
The system uses strongly typed data classes (`src/pdf2anki_types.py`):
- **`Chunk`**: Represents a segment of text with token counts and source references.
- **`Card`**: Represents a single flashcard with fields:
    - `question`: Front text (or Cloze text).
    - `answer`: Back text.
    - `extra`: Additional context (specifically for Cloze notes).
    - `tags`: Auto-generated tags.

### 3.2. Generation Process
1.  **Prompt Construction**: `anki_core.build_prompt` creates a strict system prompt instructing the LLM to output a specific numbered list format.
2.  **LLM Interaction**: `streamlit_app.py` iterates through text chunks, sending them to the configured LLM (OpenAI or OpenAI-compatible local endpoint).
3.  **Parsing**: `anki_core.parse_cards_from_output` uses Regular Expressions (Regex) to extract cards from the LLM's natural language response.
    - *Basic Pattern*: `Question: (.*?) \n Answer: (.*?)`
    - *Cloze Pattern*: `Cloze: (.*?) \n Extra: (.*?)`
4.  **TSV Formatting**: The `Card.to_tsv_row()` method formats the data into tab-separated values suitable for Anki import, handling HTML line breaks and field mapping.

## 4. Configuration and Environment

The system is configured via Environment Variables and Docker.

### 4.1. Environment Variables (.env)
- **LLM Configuration**:
    - `LLM_API_BASE`: URL for local LLM (e.g., `http://localhost:8080/v1`).
    - `LLM_MODEL`: Model name to request (e.g., `llama-3.1-8b-instruct`).
    - `OPENAI_API_KEY`: API key for OpenAI (if not using local LLM).
- **Marker API**:
    - `MARKER_API_BASE`: URL of the conversion server (default: `http://localhost:8000`).

### 4.2. Deployment
- **Docker**: The `marker-api` folder contains Dockerfiles for both CPU and GPU environments.
- **Local Execution**: The Streamlit app runs natively in the local Python environment (managed via `venv` and `requirements.txt`).

