#!/bin/bash
# Quick start script for development

set -e

echo "===== Textile Pattern Generator - Quick Start ====="
echo ""

# Check Python
echo "[1/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.9+"
    exit 1
fi
python_version=$(python3 -V | cut -d' ' -f2)
echo "✓ Python $python_version found"

# Check PostgreSQL
echo "[2/6] Checking PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "WARNING: PostgreSQL not found. Make sure PostgreSQL is running separately"
else
    echo "✓ PostgreSQL found"
fi

# Create venv
echo "[3/6] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate venv
echo "[4/6] Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Setup environment
echo "[5/6] Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env from template (update with your settings)"
else
    echo "✓ .env already exists"
fi

# Initialize database
echo "[6/6] Initializing database..."
python init_db.py --init > /dev/null 2>&1
echo "✓ Database initialized"

echo ""
echo "===== Setup Complete! ====="
echo ""
echo "Next steps:"
echo "1. Make sure PostgreSQL is running"
echo "2. Update .env if needed (DB credentials, model path)"
echo "3. Run: source venv/bin/activate && python app.py"
echo "4. Visit: http://localhost:5000"
echo ""
echo "First API call to generate:"
echo "curl -X POST http://localhost:5000/api/generate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"geometric pattern\", \"style\": \"block_print\"}'"
echo ""
