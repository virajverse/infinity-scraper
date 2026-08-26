#!/usr/bin/env bash
set -e

echo "======================================================="
echo "   Installing InfinityScrape MCP Server (by VirajVerse)"
echo "======================================================="

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.10+."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "[1/4] Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "[2/4] Activating virtual environment..."
source .venv/bin/activate

echo "[3/4] Installing Python requirements & local package..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo "[4/4] Installing Playwright Chromium browser..."
playwright install chromium

echo ""
echo "======================================================="
echo "   Installation Completed Successfully!                "
echo "======================================================="
echo ""
echo "To run MCP server:"
echo "  ./.venv/bin/python -m infinity_scraper.server"
echo ""
