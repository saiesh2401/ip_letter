#!/bin/bash

# CDR Analyzer Launcher Script
# Run this script to start the CDR Analyzer application

echo "🔍 Starting CDR Analyzer - Law Enforcement Edition..."
echo "=================================================="
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit is not installed."
    echo "Installing required dependencies..."
    pip3 install -r requirements_cdr.txt
fi

echo "✅ Launching CDR Analyzer..."
echo ""
echo "📍 The application will open in your browser at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

# Run the Streamlit app
streamlit run cdr_app.py
