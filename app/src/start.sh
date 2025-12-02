#!/bin/bash

# Run the main crew AI workflow
echo "Starting CrewAI workflow..."
python main_crewai.py

# Check if crew completed successfully
if [ $? -eq 0 ]; then
    echo "CrewAI workflow completed successfully. Starting Streamlit display..."
    # Start Streamlit server
    streamlit run display_results.py
else
    echo "CrewAI workflow failed. Exiting..."
    exit 1
fi
