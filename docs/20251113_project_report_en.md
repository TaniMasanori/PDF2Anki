Title: PDF2Anki – Final Project Report
Date: 2025-11-13
Repository: https://github.com/TaniMasanori/PDF2Anki

Abstract
This report presents PDF2Anki, a system that converts PDF documents (lecture slides, academic papers) into high‑quality Anki flashcards using AI. The system integrates a Streamlit web interface, a PDF→Markdown pipeline powered by Marker API, and an AI card generation component using OpenAI or OpenAI‑compatible LLMs. We detail the system design, technical trade‑offs, debugging challenges, and lessons learned from vibe coding. We include a live demo runbook, evaluation against the course rubric, and directions to reproduce results.


1. Introduction and Problem Statement
Students and professionals often study from PDFs that are dense and time‑consuming to parse. Converting key ideas into spaced‑repetition flashcards can accelerate learning, but manual card creation is tedious. PDF2Anki automates this process:
- Converts PDFs to Markdown while preserving essential structure and math.
- Generates Anki‑ready flashcards (Basic or Cloze) with automatic tagging.
- Exports a TSV file compatible with Anki import.
- Offers a simple web UI for end‑to‑end operation.

Scope and Goals
- Support robust PDF→Markdown conversion via Marker API.
- Maintain mathematical expressions (MathJax/LaTeX) in the pipeline.
- Produce intelligible, accurate flashcards with minimal user friction.
- Enable local LLMs (OpenAI‑compatible) or OpenAI APIs for flexibility.


2. System Overview
User‑facing Features
- PDF to Markdown conversion using Marker API.
- AI‑powered flashcard generation (OpenAI GPT family or OpenAI‑compatible endpoint).
- Anki‑ready TSV export and optional Markdown download.
- Streamlit‑based web interface and configuration sidebar.
- Intelligent chunking for long documents with semantic signals (definitions, key terms, conceptual boundaries).
- Automatic tagging and MathJax formatting.

High‑Level Architecture
- Frontend/UI: Streamlit app (`src/streamlit_app.py`).
- PDF Conversion Service: Marker API server (separate process).
- AI Generation: OpenAI Chat Completions or OpenAI‑compatible endpoints (e.g., llama.cpp, vLLM).
- Outputs: Session directory under `outputs/<timestamp>_<docname>/` containing `converted.md`, `meta.json`, `anki_cards.tsv`, and a generated prompt script.


3. Architecture and Data Flow
Step‑by‑step flow (end‑to‑end):
1) Upload PDF in Streamlit UI.
2) Compute SHA256 for deduplication and create a session directory under `outputs/`.
3) Call Marker API `/convert/` to produce Markdown and metadata in a temporary directory.
4) Copy `marker.md` and `meta.json` to the session directory as `converted.md` and `meta.json`.
5) Preview Markdown in the UI.
6) Generate Cards:
   - If intelligent chunking is enabled:
     a. Clean and chunk Markdown within a token budget.
     b. Extract semantic signals (key terms, definitions, boundaries).
     c. Build prompts per chunk; call LLM; parse card outputs.
     d. Aggregate cards across chunks; enforce count target.
   - Otherwise, build a single prompt from the full text; call LLM; parse cards.
7) Persist `anki_cards.tsv` and optional prompt script in the session directory.
8) Download results and import into Anki.

Design Rationale for Chunking
- Long documents exceed prompt and output limits; chunking ensures coverage.
- Semantic hints guide LLM extraction toward definitions/concepts, improving precision.
- Even card allocation per chunk prevents early truncation bias.


4. Core Components
4.1 Streamlit Web UI (`src/streamlit_app.py`)
- Upload handling, progress feedback, session output folder creation.
- Sidebar for configuration: Marker API URL, number of cards, content focus, note type, chunking settings, LLM mode (OpenAI vs local).
- Markdown preview and generated card viewer.
- Download buttons for `converted.md` and `anki_cards.tsv`.

4.2 Marker API (External Service)
- Converts PDF to Markdown (supports 3.10+ Python environment for the service).
- Offers `/health` and OpenAPI docs for verification.
- We allow an optimized startup script for faster conversion and GPU enablement.

4.3 AI Generation
- OpenAI or OpenAI‑compatible endpoints; auto‑selects based on environment variables:
  - Local endpoint: `LLM_API_BASE`, `LLM_MODEL`, `LLM_API_KEY`.
  - OpenAI: `OPENAI_API_KEY`, `OPENAI_MODEL` (default sensible fallback).
- Prompts are built according to desired note type (Basic/Cloze), content focus (mixed/definitions/concepts/facts), and target card counts.
- Parsing returns structured `Card` objects; TSV rows are serialized for Anki import.


5. Live Demo Runbook
Prerequisites
- Python 3.8+ for the app; Python 3.10+ for Marker API service.
- `.env` configured (see README) with either OpenAI or local LLM settings.

Step A. Start Marker API
1) Open terminal A:
   - cd PDF2Anki/marker-api
   - source .venv/bin/activate
   - python server.py --host 0.0.0.0 --port 8000
2) Verify: open http://localhost:8000/health (expect status ok).

Step B. Launch Streamlit UI
1) Open terminal B:
   - cd PDF2Anki
   - source venv/bin/activate
   - streamlit run src/streamlit_app.py
2) Open http://localhost:8501 in the browser.

Step C. Demo Script
1) Upload a representative PDF (lecture slides or a short paper).
2) Click “Convert to Markdown”. Confirm success; preview Markdown.
3) In sidebar: set Number of cards (e.g., 12), Content focus (e.g., definitions), Note type (Basic or Cloze), ensure “Use intelligent chunking” is enabled.
4) Click “Generate Anki Cards” and show progress.
5) Review a few generated cards; highlight MathJax retention and tags.
6) Download TSV; briefly show Anki import mapping (Front/Back or Cloze).

Failure Demonstration and Recovery (if time allows)
- Stop/restart Marker API to show graceful Streamlit warnings.
- Enter an invalid model to trigger validation and show troubleshooting guidance.


6. Design Decisions and Trade‑offs
LLM Integration
- Trade‑off: Simplicity (OpenAI) vs Cost/Control (local LLM). We support both; OpenAI is the default for ease, local LLM reduces cost and adds privacy but may require tuning.

Chunking and Semantics
- Chunk‑aware prompting improves coverage and specificity but adds complexity and latency. Balanced via a tokens‑per‑chunk parameter and even allocation of card counts per chunk.

Sessionized Outputs
- Storing all artifacts under `outputs/<timestamp>_<docname>/` improves reproducibility and auditing. We intentionally `.gitignore` this directory to avoid bloating the repository.

Error Handling and UX
- Streamlit uses clear status messages, progress bars, and actionable error copy (e.g., quota exceeded, model not found, connection errors). Design favors transparency over silent failures.

Licensing
- GPL‑3.0 to remain compatible with Marker dependencies and preserve copyleft requirements for downstream users.


7. Debugging Challenges and Solutions
API Parameter Changes
- Some Chat Completions models require `max_completion_tokens` instead of `max_tokens`. We detect and report misconfiguration in UI with guidance to switch or update code.

Quota and Rate Limits
- OpenAI 429s surfaced frequently under load. We added targeted warnings, links to usage/billing pages, and a local LLM fallback path in `.env`.

Connectivity and Startup Order
- Frequent user error: launching Streamlit before Marker API. We added explicit startup order checks, sidebar URL validation, and a health page verification step in README.

Large Document Stability
- Token overflows and poor coverage without chunking. Intelligent chunking plus semantic hints stabilized card quality across long documents while controlling latency.

Markdown Encoding
- Uploading an existing Markdown (UTF‑8 with replacement) allows skipping PDF conversion; we write minimal `meta.json` to retain provenance.


8. Use of Vibe Coding Tools and Lessons Learned
Approach
- We practiced iterative “vibe coding” with an AI assistant for rapid prototyping, refactoring, and documentation scaffolding, while validating outputs with small, frequent runs.

What Worked Well
- High‑level intent prompts yielded boilerplate reliably (Streamlit forms, file IO, error scaffolding).
- Semantic search and iterative patching accelerated cross‑file coordination.

Limitations Observed
- LLMs can hallucinate parameter names or endpoint details—guarded with runtime checks, explicit exceptions, and UI warnings.
- Over‑eager refactors can obscure minimal‑change constraints; we prioritized small edits and diff‑friendly updates.

Key Takeaways
- Keep prompts grounded in concrete artifacts (file paths, env vars).
- Add UX affordances that surface misconfigurations quickly.
- Preserve reproducibility through sessionized outputs and explicit runbooks.


9. Evaluation Against Criteria
System Design and Correctness
- Architecture separates concerns (UI, conversion service, LLM integration). Robust error paths and reproducible outputs improve correctness.

Creativity in Problem‑Solving
- Semantic‑guided chunking and prompt construction improved card quality on long/technical PDFs, including math‑heavy content.

Thoughtful Use of Vibe Coding Tools
- Documented assistant‑aided flows, controlled scope, and validated with working demos; we highlight limitations and compensating controls.

Clarity of Presentation
- Demo runbook, troubleshooting, and README quick‑start aim for crisp delivery.

Teamwork
- Roles can split naturally: infra (Marker), UI/UX (Streamlit), prompts/LLMs, QA and documentation.


10. Reproducibility and Setup
Quick Start (summary; see README for details)
1) Clone repo and install Python dependencies.
2) Configure `.env` with either OpenAI or local LLM endpoint.
3) Start Marker API (separate environment, Python 3.10+).
4) Run Streamlit app; access at http://localhost:8501.
5) Upload a PDF, convert, generate cards, and download TSV for Anki.

Environment Variables
- OPENAI_API_KEY, OPENAI_MODEL, MARKER_API_BASE.
- or LLM_API_BASE, LLM_MODEL, LLM_API_KEY for local endpoints.

Artifacts
- outputs/<timestamp>_<docname>/: converted.md, meta.json, anki_cards.tsv, prompt_script.sh.


11. Limitations and Future Work
Limitations
- Card quality depends on source structure and model capability.
- Marker conversion may misplace complex layouts; images are currently embedded as base64 and not deeply leveraged in card generation.
- Performance dependence on hardware and LLM endpoint speed.

Future Work
- Add image‑aware card generation and figure caption extraction.
- Fine‑tune semantic detectors and note‑type selection via heuristics.
- Support batch PDFs and background job queues.
- Add evaluation harness for card quality (e.g., human‑in‑the‑loop rating UI).


12. Ethics, Privacy, and Licensing
- Respect document licenses when converting and sharing outputs.
- Support local LLMs for privacy‑sensitive documents.
- GPL‑3.0 licensing with clear dependency notices in README and LICENSE.


13. Submission Notes
- Submit PDF (exported from this report; see checklist) to TA at samuel_reinehr@mines.edu by 12/12.
- Include the GitHub repository link in the PDF: https://github.com/TaniMasanori/PDF2Anki
- Ensure the repository README contains detailed run instructions (present).


Appendix A. Commands
Start Marker API
  cd marker-api && source .venv/bin/activate && python server.py --host 0.0.0.0 --port 8000

Start Streamlit
  source venv/bin/activate && streamlit run src/streamlit_app.py

Optional: Local LLM
  export LLM_API_BASE=http://localhost:8080/v1
  export LLM_MODEL=llama-3.1-8b-instruct
  export LLM_API_KEY=no-key-required

Note: outputs/ is git‑ignored by design to prevent large files in history.
*** End Patch

