@echo off
echo RegonAPI MCP Server - Examples Runner
echo ====================================

cd /d "%~dp0"

if not exist "..\regon_mcp_server\server.py" (
    echo Error: MCP server script not found!
    echo Please make sure you're running this from the examples folder.
    pause
    exit /b 1
)

if not exist "..\.venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat from the parent directory first.
    pause
    exit /b 1
)

echo.
echo Available examples:
echo 1. Basic Usage Example
echo 2. Bulk Search Example
echo 3. Reports Example
echo 4. Monitoring Example
echo 5. Advanced Example
echo 6. Run All Examples
echo.

set /p choice="Choose an example (1-6): "

if "%choice%"=="1" (
    echo Running Basic Usage Example...
    ..\.venv\Scripts\python.exe basic_usage_example.py
) else if "%choice%"=="2" (
    echo Running Bulk Search Example...
    ..\.venv\Scripts\python.exe bulk_search_example.py
) else if "%choice%"=="3" (
    echo Running Reports Example...
    ..\.venv\Scripts\python.exe reports_example.py
) else if "%choice%"=="4" (
    echo Running Monitoring Example...
    ..\.venv\Scripts\python.exe monitoring_example.py
) else if "%choice%"=="5" (
    echo Running Advanced Example...
    ..\.venv\Scripts\python.exe advanced_example.py
) else if "%choice%"=="6" (
    echo Running All Examples...
    ..\.venv\Scripts\python.exe run_all_examples.py
) else (
    echo Invalid choice: %choice%
    echo Please choose a number between 1 and 6.
)

echo.
echo Examples completed!
pause
