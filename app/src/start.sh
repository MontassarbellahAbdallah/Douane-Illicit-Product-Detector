#!/bin/bash

# Set error handling
set -e

# Check required environment variables
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "ERROR: GOOGLE_API_KEY environment variable is required"
    exit 1
fi

# Create necessary directories
mkdir -p ai-agent-output
mkdir -p fallback

echo "Starting Streamlit server..."
# Start Streamlit with proper signal handling
streamlit run display_results.py --server.port=8501 --server.headless=true
