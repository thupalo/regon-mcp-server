# RegonAPI HTTP MCP Server

This is a transparent HTTP wrapper around the original stdio MCP server, providing the same functionality via HTTP endpoints while preserving all features and avoiding code redundancy.

## 🚀 Quick Start

### Prerequisites

Install HTTP server dependencies:
```bash
pip install fastapi uvicorn requests
```

**UTF-8 Encoding**: For Windows users, ensure proper Unicode handling:
```powershell
# Use UTF-8 activation script
.\.venv\Scripts\Activate-UTF8.ps1

# Or set manually
$env:PYTHONIOENCODING = "utf-8"
```

### Starting the Server

```bash
# Virtual Environment (Recommended)
.\.venv\Scripts\python.exe regon_mcp_server/server_http.py --port 8001

# Or activate virtual environment first
.\.venv\Scripts\Activate.ps1
python regon_mcp_server/server_http.py --port 8001

# Basic usage (test mode, localhost:8000)
python regon_mcp_server/server_http.py

# Custom port
python regon_mcp_server/server_http.py --port 8001

# Production mode
python regon_mcp_server/server_http.py --production

# Custom host and port
python regon_mcp_server/server_http.py --host 0.0.0.0 --port 8080

# Debug logging
python regon_mcp_server/server_http.py --log-level DEBUG
```

## 📡 API Endpoints

### Server Information
- `GET /` - Server information and capabilities
- `GET /health` - Health check and RegonAPI status
- `GET /docs` - Interactive API documentation (Swagger UI)

### MCP Protocol Endpoints
- `GET /tools` - List all available MCP tools
- `POST /tools/call` - Call a specific MCP tool

### Convenience Endpoints
- `GET /search/nip/{nip}` - Search company by NIP
- `GET /search/krs/{krs}` - Search company by KRS  
- `GET /search/regon/{regon}` - Search company by REGON

## 🔧 Usage Examples

### Using curl

```bash
# Server info
curl http://localhost:8001/

# Health check
curl http://localhost:8001/health

# Search by NIP
curl http://localhost:8001/search/nip/7342867148

# Search by KRS
curl http://localhost:8001/search/krs/0000006865

# List available tools
curl http://localhost:8001/tools

# Call a tool directly
curl -X POST http://localhost:8001/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "regon_search_by_nip",
    "arguments": {"nip": "7342867148"}
  }'
```

### Using Python requests

```python
import requests

# Server info
response = requests.get("http://localhost:8001/")
print(response.json())

# Search by NIP
nip_response = requests.get("http://localhost:8001/search/nip/7342867148")
company_data = nip_response.json()
print(f"Company: {company_data['result'][0]['Nazwa']}")

# Call tool directly
tool_response = requests.post("http://localhost:8001/tools/call", json={
    "name": "regon_search_by_nip",
    "arguments": {"nip": "7342867148"}
})
result = tool_response.json()
```

### Using JavaScript/Browser

```javascript
// Fetch company data
fetch('http://localhost:8001/search/nip/7342867148')
  .then(response => response.json())
  .then(data => {
    console.log('Company:', data.result[0].Nazwa);
    console.log('Location:', data.result[0].Gmina);
  });
```

## 🌐 Web Interface

Open your browser and navigate to:
- `http://localhost:8001/` - Server information
- `http://localhost:8001/docs` - Interactive API documentation
- `http://localhost:8001/health` - Health status

## ✅ Features

### Complete Functionality Preservation
- ✅ All 13 MCP tools from stdio server
- ✅ Production and test modes
- ✅ Proper error handling
- ✅ UTF-8 encoding for Polish characters
- ✅ Same authentication and configuration

### HTTP-Specific Features
- ✅ RESTful API endpoints
- ✅ Interactive API documentation
- ✅ CORS support for web clients
- ✅ Health check endpoint
- ✅ Convenience endpoints for common operations

### Polish Character Support
- ✅ Proper UTF-8 encoding: `SPÓŁKA`, `Północ`
- ✅ All Polish characters display correctly
- ✅ JSON responses preserve Unicode

## 🔧 Configuration

### Environment Variables
Same as stdio server:
- `API_KEY` - Production API key
- `TEST_API_KEY` - Test API key  
- `LOG_LEVEL` - Logging level
- `PYTHONIOENCODING=utf-8` - Automatic UTF-8 encoding

### Command Line Options
```
--host HOST          Host to bind to (default: localhost)
--port PORT          Port to bind to (default: 8000)
--production         Use production mode
--log-level LEVEL    Set logging level (DEBUG|INFO|WARNING|ERROR)
```

## 🧪 Testing

Test the HTTP server using virtual environment:
```bash
# Start server in one terminal
.\.venv\Scripts\python.exe regon_mcp_server/server_http.py --port 8001

# Test in another terminal  
.\.venv\Scripts\python.exe tests\test_http_server.py
```

Test in browser:
```bash
# Terminal 1: Start server
.\.venv\Scripts\python.exe regon_mcp_server/server_http.py --port 8001

# Terminal 2: Test with PowerShell
Invoke-RestMethod -Uri "http://localhost:8001/search/nip/7342867148"
```

Run all tests:
```bash
.\.venv\Scripts\python.exe tests\run_all_tests.py
```

## 🏗️ Architecture

The HTTP server is a transparent wrapper that:
1. **Imports** the original stdio server module
2. **Reuses** all existing handlers and logic
3. **Wraps** functionality in FastAPI endpoints
4. **Preserves** all features without code duplication

```
stdio_server.py ←── server_http.py (imports and wraps)
      ↓                    ↓
   MCP Tools         HTTP Endpoints
   handlers      →   /tools/call
   functions     →   /search/nip/{nip}
   config        →   Same configuration
```

## 🔄 Compatibility

- **Full MCP compatibility**: All stdio server features work identically
- **Zero code duplication**: HTTP server imports and reuses stdio logic
- **Same configuration**: Environment variables and settings work identically
- **Unicode support**: Polish characters work perfectly in HTTP responses

## 🐛 Troubleshooting

### Port already in use
```bash
# Try different port
python regon_mcp_server/server_http.py --port 8001
```

### Module import error
```bash
# Run from project root directory
cd /path/to/REGON_mcp_server
python regon_mcp_server/server_http.py
```

### FastAPI not installed
```bash
pip install fastapi uvicorn
```

## 📚 Related Files

- `regon_mcp_server/server.py` - Original stdio MCP server
- `regon_mcp_server/server_http.py` - HTTP wrapper server
- `test_http_simple.py` - HTTP server test script
- `examples/` - Usage examples (work with both servers)
