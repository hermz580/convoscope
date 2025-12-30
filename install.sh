#!/bin/bash
# ConvoScope Quick Start Installation Script

set -e

echo "🔍 ConvoScope Installation"
echo "=========================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
    echo "✓ Python $python_version detected"
else
    echo "❌ Python 3.8+ required. You have: $python_version"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Installing optional visualization libraries..."
pip3 install matplotlib seaborn scikit-learn || echo "⚠️  Optional viz libs skipped"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Quick Start:"
echo "  1. Get your data: claude.ai → Settings → Privacy → Download my data"
echo "  2. Run analysis: python3 src/advanced_analyzer.py your_export.json"
echo ""
echo "Documentation: ./docs/USAGE.md"
echo "Examples: ./examples/"
echo ""
