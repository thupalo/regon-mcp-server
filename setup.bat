@echo off
echo RegonAPI MCP Server Setup
echo =========================

cd /d "%~dp0"

echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Create a .env file with your API key:
echo    TEST_API_KEY=your_api_key_here
echo 2. Run the test: .venv\Scripts\python.exe test_server.py
echo 3. Start the server: start_server.bat
echo.

pause
