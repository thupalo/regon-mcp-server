@echo off
REM Pytest runner for REGON MCP Server tests
REM This script provides easy access to pytest functionality on Windows

REM Configure UTF-8 encoding
set PYTHONIOENCODING=utf-8

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ❌ Failed to activate virtual environment
        echo Please ensure .venv exists and try again
        pause
        exit /b 1
    )
)

REM Change to project root
pushd "%~dp0\.."

echo 🧪 REGON MCP Server - Pytest Test Runner
echo ==========================================

REM Parse command line arguments for common scenarios
if "%1"=="unit" (
    echo Running unit tests only...
    python tests\run_pytest.py --unit
    goto :end
)

if "%1"=="integration" (
    echo Running integration tests only...
    python tests\run_pytest.py --integration
    goto :end
)

if "%1"=="http" (
    echo Running HTTP server tests only...
    python tests\run_pytest.py --http
    goto :end
)

if "%1"=="stdio" (
    echo Running stdio server tests only...
    python tests\run_pytest.py --stdio
    goto :end
)

if "%1"=="coverage" (
    echo Running all tests with coverage report...
    python tests\run_pytest.py --coverage
    goto :end
)

if "%1"=="fast" (
    echo Running fast tests only (excluding slow tests)...
    python tests\run_pytest.py --fast
    goto :end
)

if "%1"=="help" (
    echo.
    echo Usage: run_pytest.bat [option]
    echo.
    echo Options:
    echo   unit         - Run only unit tests
    echo   integration  - Run only integration tests  
    echo   http         - Run only HTTP server tests
    echo   stdio        - Run only stdio server tests
    echo   coverage     - Run all tests with coverage report
    echo   fast         - Run tests excluding slow ones
    echo   help         - Show this help message
    echo.
    echo If no option is provided, all tests will be run.
    echo.
    goto :end
)

REM Default: run all tests
echo Running all tests...
python tests\run_pytest.py

:end
popd

REM Check exit code and provide feedback
if errorlevel 1 (
    echo.
    echo ❌ Tests failed. Check the output above for details.
    echo.
) else (
    echo.
    echo ✅ All tests passed successfully!
    echo.
)

if "%1"=="coverage" (
    echo 📊 Coverage report generated in htmlcov\index.html
    echo.
)

pause
