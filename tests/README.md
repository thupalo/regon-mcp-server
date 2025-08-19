# REGON MCP Server Tests

This folder contains comprehensive tests for both the stdio and HTTP MCP servers.

## 🧪 Test Scripts

### Core Tests
- **`test_stdio_server.py`** - Tests the main stdio MCP server functionality
- **`test_http_server.py`** - Tests the HTTP wrapper server (requires server to be running)
- **`test_mcp_protocol.py`** - Tests MCP protocol compliance with JSON-RPC messages

### Test Runners
- **`run_all_tests.py`** - Runs all available tests in sequence
- **`run_all_tests.bat`** - Windows batch file to run all tests
- **`test_http_server.bat`** - Windows batch file to run HTTP tests with instructions

## 🚀 Quick Start

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
