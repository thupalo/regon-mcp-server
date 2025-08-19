@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

set PORT=%1
if "%PORT%"=="" set PORT=8001

echo 🚀 Testing HTTP MCP Server
echo.
echo Instructions:
echo 1. Start HTTP server first in another terminal:
echo    .\.venv\Scripts\python.exe regon_mcp_server\server_http.py --port %PORT%
echo.
echo 2. Then press any key to run the HTTP tests
echo.
echo UTF-8 encoding configured: %PYTHONIOENCODING%
echo Port: %PORT%
echo.
pause

echo Running HTTP server tests...
.\.venv\Scripts\python.exe tests\test_http_server.py --port %PORT%

echo.
echo HTTP test completed. Check output above for results.
pause
