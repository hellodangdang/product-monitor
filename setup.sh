#!/bin/bash

# Setup script for Product Monitor

echo "Setting up Product Monitor..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Create config file if it doesn't exist
if [ ! -f config.json ]; then
    echo "Creating config.json from template..."
    cp config.json.example config.json
    echo ""
    echo "⚠️  IMPORTANT: Please edit config.json with your shipping information!"
    echo "   Open config.json and fill in your details before running the monitor."
else
    echo "config.json already exists, skipping..."
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.json with your shipping information"
echo "2. Run: python3 product_monitor.py"
echo ""

