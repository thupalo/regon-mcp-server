# REGON MCP Server Tests

This folder contains comprehensive tests for both the stdio and HTTP MCP servers using both traditional test scripts and modern pytest framework.

## 🧪 Test Framework

The project now supports **two testing approaches**:

1. **Pytest Framework** (recommended) - Modern, comprehensive testing with fixtures, markers, and coverage
2. **Traditional Scripts** - Legacy test scripts for manual testing and CI/CD

## ✅ Quick Start - Working Tests

For immediate testing with verified working tests:

```bash
# Run the simple test runner (15 passing tests)
python tests/run_simple_tests.py

# Or run specific working tests directly
python -m pytest tests/test_error_handling_simple.py -v
```

This will run **15 passing tests** covering:
- RetryMechanism functionality
- Input validation  
- String sanitization
- Custom exception classes

## 📁 Test Files

### Pytest Test Suites
- **`test_stdio_server_pytest.py`** - Comprehensive pytest tests for stdio MCP server
- **`test_http_server_pytest.py`** - Comprehensive pytest tests for HTTP server with fixtures
- **`test_error_handling_pytest.py`** - Unit tests for error handling and retry mechanisms
- **`conftest.py`** - Pytest configuration, fixtures, and test utilities

### Legacy Test Scripts
- **`test_stdio_server.py`** - Original stdio MCP server tests
- **`test_http_server.py`** - Original HTTP wrapper server tests  
- **`test_mcp_protocol.py`** - MCP protocol compliance tests

### Test Runners
- **`run_pytest.py`** - Advanced pytest runner with filtering and reporting options
- **`run_pytest.bat`** - Windows batch file for pytest execution
- **`run_all_tests.py`** - Legacy test runner for all tests
- **`run_all_tests.bat`** - Windows batch file for legacy tests
- **`run_simple_tests.py`** - **NEW** Simple runner for verified working tests

### Working Test Files ✅
- **`test_error_handling_simple.py`** - **15 passing tests** for error handling functionality
  - RetryMechanism class tests (4 tests)
  - Input validation tests (3 tests) 
  - String sanitization tests (3 tests)
  - Custom exception tests (5 tests)
  - **Coverage**: 37% of error_handling.py module

## 🚀 Quick Start with Pytest (Recommended)

### Prerequisites
Install pytest dependencies:
```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-xdist
```

### Basic Usage

```bash
# Run all tests
python tests\run_pytest.py

# Run only unit tests (fast)
python tests\run_pytest.py --unit

# Run only integration tests
python tests\run_pytest.py --integration

# Run HTTP server tests only
python tests\run_pytest.py --http

# Run stdio server tests only  
python tests\run_pytest.py --stdio

# Run with coverage report
python tests\run_pytest.py --coverage

# Run fast tests only (skip slow tests)
python tests\run_pytest.py --fast
```

### Windows Batch File Usage

```batch
# Run all tests
tests\run_pytest.bat

# Run specific test types
tests\run_pytest.bat unit
tests\run_pytest.bat integration
tests\run_pytest.bat http
tests\run_pytest.bat coverage
tests\run_pytest.bat fast
```

## 🎯 Test Categories and Markers

### Test Markers
- **`@pytest.mark.unit`** - Fast unit tests that don't require external dependencies
- **`@pytest.mark.integration`** - Integration tests that may require services
- **`@pytest.mark.http`** - HTTP server specific tests
- **`@pytest.mark.stdio`** - Stdio server specific tests
- **`@pytest.mark.slow`** - Tests that take longer to run
- **`@pytest.mark.network`** - Tests requiring network access
- **`@pytest.mark.api`** - Tests requiring REGON API access

### Running Specific Test Categories

```bash
# Run only fast unit tests
pytest -m "unit and not slow"

# Run integration tests for HTTP server
pytest -m "integration and http"

# Run all tests except network-dependent ones
pytest -m "not network"

# Run API tests (requires API key)
pytest -m "api"
```

## 📊 Coverage Reporting

Generate comprehensive coverage reports:

```bash
# HTML coverage report
python tests\run_pytest.py --coverage

# View coverage report
# Open htmlcov\index.html in browser

# Terminal coverage report only
pytest --cov=regon_mcp_server --cov-report=term-missing
```

## 🛠️ Advanced Pytest Usage

### Parallel Test Execution
```bash
# Run tests in parallel
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

### Verbose Output and Debugging
```bash
# Verbose output
pytest -v

# Show local variables in tracebacks
pytest --tb=long --showlocals

# Run specific test file
pytest tests/test_stdio_server_pytest.py

# Run specific test method
pytest tests/test_stdio_server_pytest.py::TestStdioMCPServer::test_server_startup
```

### Test Configuration
The project includes comprehensive pytest configuration in:
- **`pytest.ini`** - Main pytest configuration
- **`pyproject.toml`** - Alternative configuration format

## 🔧 Legacy Test Scripts

### Run All Legacy Tests

### Run All Tests
```bash
# Using Python directly (default port 8001)
.\.venv\Scripts\python.exe tests\run_all_tests.py

# Using Python with custom port
.\.venv\Scripts\python.exe tests\run_all_tests.py --port 8000

# Using batch file (Windows, default port 8001)
tests\run_all_tests.bat

# Using batch file with custom port
tests\run_all_tests.bat 8000
```

### Individual Tests

#### Stdio Server Test
```bash
.\.venv\Scripts\python.exe tests\test_stdio_server.py
```

#### MCP Protocol Test
```bash
.\.venv\Scripts\python.exe tests\test_mcp_protocol.py
```

#### HTTP Server Test
```bash
# Start HTTP server first (in another terminal)
.\.venv\Scripts\python.exe regon_mcp_server\server_http.py --port 8001

# Then run the test (default port 8001)
.\.venv\Scripts\python.exe tests\test_http_server.py

# Or test with custom port
.\.venv\Scripts\python.exe tests\test_http_server.py --port 8000

# Or use batch file with instructions (default port)
tests\test_http_server.bat

# Or use batch file with custom port
tests\test_http_server.bat 8000
```

## 📋 What Gets Tested

### Stdio MCP Server (`test_stdio_server.py`)
- ✅ Server startup in test mode
- ✅ Server startup in production mode (may require API_KEY)
- ✅ Tool listing functionality
- ✅ Tool calling with real API requests
- ✅ Polish character encoding verification

### HTTP Server (`test_http_server.py`)
- ✅ Server information endpoint (`/`)
- ✅ Health check endpoint (`/health`)
- ✅ Tool listing endpoint (`/tools`)
- ✅ Convenience search endpoints (`/search/nip/{nip}`)
- ✅ Direct tool calling endpoint (`/tools/call`)
- ✅ Polish character encoding in HTTP responses

### MCP Protocol (`test_mcp_protocol.py`)
- ✅ JSON-RPC 2.0 protocol compliance
- ✅ MCP initialization handshake
- ✅ Tool discovery via `tools/list`
- ✅ Tool execution via `tools/call`
- ✅ Error handling for invalid requests
- ✅ Proper response formatting

## 🔧 Prerequisites

### Environment Setup
1. **Virtual Environment**: Must have `.venv` directory with Python
2. **Dependencies**: All required packages installed via `pip install -r requirements.txt`
3. **Project Structure**: Must run from project root directory
4. **UTF-8 Encoding**: Proper Unicode handling for emojis and Polish characters

### UTF-8 Encoding Configuration
**Important**: All test scripts automatically configure UTF-8 encoding with:
```python
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
```

**Alternative Setup Methods**:
```powershell
# Method 1: Use UTF-8 activation script
.\.venv\Scripts\Activate-UTF8.ps1

# Method 2: Set environment variable manually
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\Activate.ps1

# Method 3: Use batch files (auto-configure UTF-8)
tests\run_all_tests.bat
```

### API Keys (Optional)
- **TEST_API_KEY**: For test mode (fallback to default test key)
- **API_KEY**: For production mode tests

## 📊 Test Results

Each test provides detailed output showing:
- ✅ **PASSED** - Test completed successfully
- ❌ **FAILED** - Test failed with error details
- ⚠️ **WARNING** - Test completed with warnings
- ℹ️ **INFO** - Informational messages

### Example Output
```
🚀 Testing HTTP MCP Server...
📡 Base URL: http://localhost:8001

✅ Test 1: Server Information
   Server: regon-api-http
   Version: 1.0.0
   Mode: test
   ✅ PASSED

✅ Test 2: Health Check
   Status: healthy
   Service: RegonAPI ready
   ✅ PASSED
```

## 🐛 Troubleshooting

### Common Issues

#### "UnicodeEncodeError: 'charmap' codec can't encode character"
This happens when UTF-8 encoding is not properly configured:
```bash
# Solution 1: Use UTF-8 activation script
.\.venv\Scripts\Activate-UTF8.ps1

# Solution 2: Set environment variable
set PYTHONIOENCODING=utf-8
# or in PowerShell:
$env:PYTHONIOENCODING = "utf-8"

# Solution 3: Use batch files (auto-configure)
tests\run_all_tests.bat
```

#### "HTTP server not running"
```bash
# Start HTTP server first
.\.venv\Scripts\python.exe regon_mcp_server\server_http.py --port 8001
```

#### "Not in project root directory"
```bash
# Make sure you're in the correct directory
cd C:\Users\YourUser\Documents\Projects\REGON_mcp_server
```

#### "Virtual environment not found"
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

#### "Missing required modules"
```bash
# Install dependencies
.\.venv\Scripts\pip.exe install -r requirements.txt
```

### Production Mode Tests
Production mode tests may fail if `API_KEY` is not set:
```bash
# Set API key in .env file
echo API_KEY=your_production_key >> .env
```

## 📚 Test Coverage

### Functional Coverage
- 🔍 **Search Operations**: NIP, REGON, KRS searches
- 📊 **Report Generation**: Full report downloads
- 🌐 **Service Status**: Health checks and error handling
- 🔧 **Protocol Compliance**: JSON-RPC 2.0 and MCP standards

### Technical Coverage
- 🔤 **Character Encoding**: Polish characters (ą, ć, ę, ł, ń, ó, ś, ź, ż)
- 🌍 **Environment Modes**: Test and production configurations
- 📡 **Communication**: Both stdio and HTTP protocols
- ⚠️ **Error Handling**: Invalid requests and API errors

## 🎯 Success Criteria

All tests should pass for a complete, working system:
- **Stdio Server**: 3/3 tests passing
- **HTTP Server**: 6/6 tests passing  
- **MCP Protocol**: 4/4 tests passing

Total: **13/13 individual test checks passing** across all test suites.
