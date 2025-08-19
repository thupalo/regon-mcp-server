@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

set PORT=%1
if "%PORT%"=="" set PORT=8001

echo 🧪 Running All REGON MCP Server Tests
echo.
echo This will test both stdio and HTTP MCP servers
echo Make sure you're in the project root directory
echo.
echo UTF-8 encoding configured: %PYTHONIOENCODING%
echo HTTP Port: %PORT%
echo.
pause

echo Starting comprehensive test suite...
.\.venv\Scripts\python.exe tests\run_all_tests.py --port %PORT%

echo.
echo Test completed. Check output above for results.
pause
