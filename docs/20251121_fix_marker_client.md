# Fix Marker API Client Integration

## Date
2025-11-21

## Summary
Updated `src/marker_client.py` to work with the current version of `marker-api`.

## Changes
- **API Endpoint**: Changed default endpoint from `/convert` to `/marker/upload`.
- **Response Parsing**: Added support for the current API response format (`{"output": "...", "success": True}`).
- **Timeout**: Increased default timeout from 120s to 300s to handle larger files or first-time model loading.

## Context
The client was encountering `404 Not Found` errors because it was targeting an incorrect endpoint. Additionally, the response format expected by the client did not match the server's actual output.

## Verification
- Confirmed endpoint path in `marker-api/marker/scripts/server.py`.
- Confirmed response schema in `marker-api/marker/scripts/server.py`.

