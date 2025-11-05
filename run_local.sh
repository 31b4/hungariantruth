#!/bin/bash
# Hungarian Truth News - Local Runner
# Run this script to test the full system locally

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Hungarian Truth News - Local Test                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Set your API key here
export GEMINI_API_KEY="AIzaSyDW9LlCfH82IoX1QbDe7r2DmA2BNCPVnqI"

# Navigate to scraper directory
cd scraper

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

echo "🚀 Running news scraper and AI synthesis..."
echo ""

# Run the daily script
python3 run_daily.py

if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    ✅ SUCCESS!                                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📁 Check the output:"
    echo "   • data/$(date +%Y-%m-%d).json - Today's AI-synthesized news"
    echo ""
    echo "🌐 To view the website locally:"
    echo "   $ cd .."
    echo "   $ python3 -m http.server 8000"
    echo "   → Then open: http://localhost:8000"
    echo ""
else
    echo ""
    echo "❌ Something went wrong. Check the logs above."
fi

