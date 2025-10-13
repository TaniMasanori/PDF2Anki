## PDF2Anki Presentation Overview (Introducing Project_plan.md)

### Problem Definition
- Creating study Q&A cards from large PDFs (lecture slides and academic papers) is time-consuming and hard to keep comprehensive and consistent when done manually.
- Documents containing figures, tables, and equations make text extraction, formatting, and key-point selection even harder.
- Goal: generate high-quality Anki cards quickly to improve study efficiency.
- Demo scope: lecture slides and academic papers (including figures/tables/equations).

### Solution
- PDF → Markdown: Run Marker API locally on WSL to convert PDFs into high-fidelity Markdown (preserve structure, references to images/tables, and LaTeX equations).
- Markdown → Q&A: Use an LLM (GPT API) with a prompt template to generate a specified number of Basic-format Q&A pairs (chunk long content by section to handle token limits).
- Q&A → Import file: Normalize into Anki-importable tab-separated (TSV/CSV) with two fields (Front/Back); keep LaTeX as $...$ for MathJax rendering.
- Anki import: For the demo, add notes via the Anki GUI (minimum implementation).
- Stretch goal: Automate import via an Anki add-on or AnkiConnect by the final presentation.
- Out of scope (for the demo): image-understanding questions and training custom models.

### System Architecture
- Runtime environment
  - Windows + WSL (Ubuntu): run the Marker API server in WSL (Python environment, REST endpoint).
  - Python scripts: handle API calls, text chunking, LLM response parsing, and TSV generation.
  - Anki Desktop (Windows): manually import the generated TSV via the GUI.
- Component overview
  1. PDF input (user-selected)
  2. Marker API (WSL, REST): PDF → Markdown (+assets: images/tables/equations)
  3. Conversion output management: store Markdown and related assets
  4. LLM invocation: GPT API with a prompt template; section chunking and result merging
  5. Formatting: extract Q&A, normalize, preserve LaTeX, generate TSV
  6. Manual Anki import: map to the Basic note type (Front/Back)
- Data flow (conceptual)
  - PDF → [Marker API] → Markdown (+assets)
  - Markdown (chunked) → [LLM] → Q&A text
  - Q&A → TSV (Front/Back) → [Anki Import]
- Key design points
  - Section-level chunking to handle long documents and token limits.
  - Preserve LaTeX ($...$) to ensure compatibility with Anki's MathJax rendering.
  - Keep error handling minimal for the demo and prioritize reproducibility (optionally prepare a pre-generated TSV as backup).
  - Security and operations: manage API keys via environment variables, exclude large generated artifacts (e.g., assets) using `.gitignore`.


