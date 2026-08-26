@echo off
echo =======================================================
echo   Installing InfinityScrape MCP Server (by VirajVerse)
echo =======================================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.10+ is not found in PATH. Please install Python.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [1/4] Creating isolated virtual environment...
    python -m venv .venv
)

echo [2/4] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3/4] Installing Python dependencies & local package...
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo [4/4] Installing Playwright Chromium browser...
playwright install chromium

echo.
echo =======================================================
echo   Installation Completed Successfully!
echo =======================================================
echo.
echo To start MCP Server:
echo   .\.venv\Scripts\python.exe -m infinity_scraper.server
echo.
echo To test CLI:
echo   .\.venv\Scripts\python.exe -m infinity_scraper.cli --help
echo.
pause
