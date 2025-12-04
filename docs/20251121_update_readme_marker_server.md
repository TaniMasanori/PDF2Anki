# Update README for Marker API Server Setup

## Date
2025-11-21

## Summary
Updated `README.md` to reflect the correct setup and startup instructions for the Marker API server.

## Changes
- **Dependency Installation**: Added `fastapi uvicorn python-multipart starlette` to the installation steps for `marker-api`.
- **Startup Command**: Corrected the server startup command from `python server.py ...` to `python marker_server.py ...`.

## Context
The previous instructions referenced `server.py` which is not the entry point for the API server in the current version of `marker-api`. Additionally, required dependencies for running the server were missing from the guide.

## Verification
- Confirmed `marker_server.py` is the correct entry point.
- Verified dependencies required for `uvicorn` and `fastapi`.

