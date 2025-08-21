# RegonAPI MCP Server PowerShell Launcher
# Run this script to start the MCP server

Write-Host "Starting RegonAPI MCP Server..." -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

# Change to script directory
Set-Location $PSScriptRoot

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create a .env file with your API key." -ForegroundColor Yellow
    Write-Host "Example:" -ForegroundColor Cyan
    Write-Host "TEST_API_KEY=your_api_key_here" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to continue anyway"
}

Write-Host "Starting server..." -ForegroundColor Cyan
& ".venv\Scripts\python.exe" "regon_mcp_server\server_http.py"

Read-Host "Press Enter to exit"
