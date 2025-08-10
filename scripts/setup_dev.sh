#!/bin/bash

# Multi-Document Fraud Detection Agent - Development Setup Script

set -e

echo "🔍 Setting up Multi-Document Fraud Detection Agent - Development Environment"
echo "============================================================================"

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install build tools first
echo "🔧 Installing build tools..."
pip install setuptools>=68.0.0 wheel>=0.41.0

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from .env.example"
    echo "⚠️  Please edit .env file and add your OpenAI API key"
else
    echo "✅ .env file already exists"
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs
echo "✅ Logs directory created"

# Check if OpenAI API key is set
echo "🔑 Checking OpenAI API key..."
if [ -f ".env" ]; then
    if grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env; then
        echo "⚠️  WARNING: Please update your OpenAI API key in .env file"
    else
        echo "✅ OpenAI API key appears to be configured"
    fi
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Start the backend: python -m src.main"
echo "4. Start the frontend (in another terminal): streamlit run frontend/app.py"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Frontend will be available at: http://localhost:8501"
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "Happy fraud detecting! 🕵️‍♂️" 