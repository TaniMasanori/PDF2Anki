# Fix Filename Length Issue in Streamlit App

## Date
2025-11-21

## Summary
Updated `src/streamlit_app.py` to truncate generated directory names derived from uploaded files.

## Changes
- **Directory Naming**: Truncated the sanitized filename to 50 characters when creating session output directories (`outputs/YYYYMMDD_HHMMSS_<filename>`).

## Context
The user encountered an `[Errno 2] No such file or directory` error when processing a PDF with a very long filename. This is likely due to filesystem limitations on path or filename lengths (e.g., on encrypted filesystems like eCryptfs, filenames are limited to ~143 characters). Truncating the name prevents this issue while keeping the directory identifiable.

## Verification
- Applied truncation logic to both PDF upload and Markdown upload flows.

