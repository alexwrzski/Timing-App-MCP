#!/bin/bash

# Timing App MCP Server Installation Script

echo "🚀 Installing Timing App MCP Server..."
echo "======================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Make scripts executable
echo "🔨 Making scripts executable..."
chmod +x mcp_timing_server.py
chmod +x example_usage.py
chmod +x test_server.py

echo ""
echo "✅ Installation completed!"
echo ""
echo "Next steps:"
echo "1. Get your API token from: https://web.timingapp.com/integrations/tokens"
echo "2. Update config.json with your token"
echo "3. Run the server: python mcp_timing_server.py"
echo "4. Test the server: python test_server.py"
echo ""
echo "For more information, see README.md" 