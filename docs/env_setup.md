# Environment Setup

Create a `.env` file in the project root with the following variables:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Marker API Configuration
MARKER_API_BASE=http://localhost:8000
```

## Getting an OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API keys section
4. Create a new API key
5. Copy the key and paste it in your `.env` file

## Marker API Setup

The Marker API should be running locally at the specified URL (default: http://localhost:8000).
You can change this URL in the `.env` file if your Marker API is running on a different port or host.
