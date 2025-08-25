#!/bin/bash

echo "Starting HealthAra..."

# Install dependencies
pip install -r requirements.txt

# Start Streamlit
streamlit run health_assistant.py --server.port=${PORT:-8000} --server.address=0.0.0.0
