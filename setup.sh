#!/bin/bash

# Hungarian Truth News - Setup Script
# This script helps set up the development environment

echo "🚀 Setting up Hungarian Truth News..."
echo ""

# Check Python version
echo "📌 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
cd scraper
python3 -m venv venv

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and add your Gemini API key"
echo "2. Activate the virtual environment: source scraper/venv/bin/activate"
echo "3. Run the scraper: cd scraper && python run_daily.py"
echo ""
echo "For website development:"
echo "1. Start a local server: python3 -m http.server 8000"
echo "2. Open http://localhost:8000 in your browser"
echo ""

