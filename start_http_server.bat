@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

echo 🚀 Starting HTTP MCP Server...
echo.
echo Server will start on http://localhost:8001
echo Press Ctrl+C to stop the server
echo UTF-8 encoding configured: %PYTHONIOENCODING%
echo.
.\.venv\Scripts\python.exe regon_mcp_server\server_http.py --port 8001
pause
