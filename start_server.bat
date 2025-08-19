@echo off
echo Starting RegonAPI MCP Server...
echo ==============================

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

if not exist ".env" (
    echo Warning: .env file not found!
    echo Please create a .env file with your API key.
    echo Example:
    echo TEST_API_KEY=your_api_key_here
    echo.
    pause
)

echo Starting server...
.venv\Scripts\python.exe regon_mcp_server.py

pause
