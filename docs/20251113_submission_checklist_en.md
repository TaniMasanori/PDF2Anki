Title: Final Submission Checklist and PDF Export Guide
Date: 2025-11-13
Repository: https://github.com/TaniMasanori/PDF2Anki
TA Email: samuel_reinehr@mines.edu
Deadline: 12/12 (PDF submission)

1) Report Requirements (PDF)
- At least 6 pages, single-spaced, 11-point font.
- Include a link to the GitHub repository: https://github.com/TaniMasanori/PDF2Anki
- Provide a technical deep dive: design trade-offs, debugging, vibe coding lessons.
- Be clear, engaging, and technically precise.

2) Repository Requirements
- README in repo root with detailed run instructions (present in this project).
- Codebase is complete and runnable (Streamlit UI + Marker API setup documented).
- Avoid large files in Git history (outputs/, *.pdf ignored by .gitignore).

3) Presentation and Live Demo
- Show end-to-end flow: upload PDF → convert → generate cards → download TSV.
- Discuss design decisions, error handling, and chunking rationale.
- Highlight limitations and future work.

4) Teamwork and Documentation
- Balanced contributions and clear division of responsibilities (UI, LLM, infra, QA/doc).
- Document vibe coding usage, including limitations and countermeasures.

5) PDF Export Instructions
Option A: Pandoc (recommended for consistent results)
- Install: pandoc and a LaTeX engine (e.g., TeX Live) if not already installed.
- Basic command:
  pandoc docs/20251113_project_report_en.md \
    -o docs/20251113_project_report_en.pdf \
    --from gfm \
    --pdf-engine=xelatex \
    -V mainfont='Times New Roman' \
    -V geometry:margin=1in \
    --metadata title='PDF2Anki Project Report'
- If your report embeds Mermaid diagrams, add a filter:
  pandoc docs/20251113_project_report_en.md \
    -o docs/20251113_project_report_en.pdf \
    --from gfm \
    --pdf-engine=xelatex \
    --filter pandoc-mermaid \
    -V mainfont='Times New Roman' \
    -V geometry:margin=1in

Option B: VS Code / Browser Print to PDF
- Open the Markdown file in VS Code with a Markdown PDF extension or use the built-in print.
- Set margins and font size to approximate 11-point, single-spaced.
- Verify pagination and link rendering.

6) Submission Steps
- [ ] Generate the final PDF from the report (>= 6 pages).
- [ ] Verify the GitHub link is present on the first page.
- [ ] Re-check README instructions (install, env, Marker API, Streamlit, usage).
- [ ] Test the live demo steps on a clean machine or fresh environment.
- [ ] Send the PDF via email to the TA by 12/12: samuel_reinehr@mines.edu.
- [ ] Keep the PDF out of git history (this repository ignores *.pdf by default).

7) Live Demo Prep Checklist
- [ ] Marker API runs (health check at http://localhost:8000/health).
- [ ] Streamlit runs at http://localhost:8501.
- [ ] .env has valid OpenAI or local LLM configuration.
- [ ] A small, representative PDF is prepared for upload.
- [ ] Fallback plan: upload an existing Markdown to skip conversion if needed.

Notes
- Git Large File Prevention: Large assets, outputs, and PDFs are ignored by .gitignore. Keep them out of Git or use external storage.
- Reproducibility: Each run writes to outputs/<timestamp>_<docname>/; do not commit this directory.
