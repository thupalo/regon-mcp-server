# RegonAPI MCP Server

[![GitHub license](https://img.shields.io/github/license/thupalo/regon-mcp-server)](https://github.com/thupalo/regon-mcp-server/blob/main/LICENSE)
[![Python version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green)](https://modelcontextprotocol.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-HTTP%20API-red)](https://fastapi.tiangolo.com/)

An MCP (Model Context Protocol) server that provides access to the Polish GUS REGON Database through the RegonAPI Python module. This server allows you to search for business entity information and download detailed reports.

> 🇵🇱 **Polish Business Data**: Access official Polish business registry data with UTF-8 support for Polish characters (ą, ć, ę, ł, ń, ó, ś, ź, ż)

## ✨ Features

- 🔍 **Search business entities** by NIP (Tax Identification Number)
- 📋 **Search business entities** by REGON number (9 or 14 digits)  
- 🏢 **Search business entities** by KRS (National Court Register) number
- 📊 **Support for bulk searches** (multiple entities at once)
- 📈 **Download full reports** with detailed business information
- 💚 **Service status monitoring** and health checks
- 🛡️ **Comprehensive error handling** and logging
- 🌐 **Dual protocol support**: Stdio MCP + HTTP REST API
- 🔧 **Tool customization** with JSON configurations
- 🇵🇱 **UTF-8 encoding** for Polish characters

## 📚 Documentation

**Complete documentation is available in the [`docs/`](docs/) folder:**

- **[docs/README.md](docs/README.md)** - 📚 Documentation index and navigation guide
- **[docs/QUICK_CONFIG.md](docs/QUICK_CONFIG.md)** - ⚡ Fast setup for common configurations
- **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - ⚙️ Complete configuration guide for all MCP clients
- **[docs/TOOL_CONFIGURATION.md](docs/TOOL_CONFIGURATION.md)** - 🛠️ Tool customization and JSON configuration
- **[docs/HTTP_SERVER_README.md](docs/HTTP_SERVER_README.md)** - 🌐 HTTP REST API server documentation
- **[docs/SERVER_HARDENING_SUMMARY.md](docs/SERVER_HARDENING_SUMMARY.md)** - 🛡️ Production hardening guide

**👉 For first-time setup, start with [docs/QUICK_CONFIG.md](docs/QUICK_CONFIG.md)**

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/thupalo/regon-mcp-server.git
   cd regon-mcp-server
   ```

2. **Setup environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Configure API key:**
   ```bash
   cp .env.example .env
   # Edit .env file with your GUS API key
   ```

4. **Start the server:**
   ```bash
   # MCP Stdio server
   python regon_mcp_server/server.py
   
   # HTTP REST API server  
   python regon_mcp_server/server_http.py --port 8000
   ```

## 📁 Project Structure

```
regon-mcp-server/
├── 📦 regon_mcp_server/     # Core server implementation
│   ├── server.py            # Main MCP stdio server
│   ├── server_http.py       # HTTP REST API wrapper
│   ├── error_handling.py    # Comprehensive error handling
│   └── tool_config.py       # Tool configuration loader
├── ⚙️ config/               # Tool customization files
│   ├── tools_default.json   # Default tool set
│   ├── tools_polish.json    # Polish language tools
│   ├── tools_minimal.json   # Minimal tool set
│   └── tools_detailed.json  # Detailed tool descriptions
├── 📚 docs/                 # Complete documentation
├── 🧪 tests/                # Comprehensive test suite
├── 📝 examples/             # Usage examples and utilities
└── 🚀 start_*.bat          # Quick start scripts
```

## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## UTF-8 Encoding Configuration

**Important for Windows users**: To properly display Polish characters and emojis, configure UTF-8 encoding:

### Automatic Configuration
All servers and scripts automatically configure UTF-8 encoding with:
```python
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
```

### Manual Configuration (if needed)
```powershell
# Use the UTF-8 activation script
.\.venv\Scripts\Activate-UTF8.ps1

# Or set manually before activation
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\Activate.ps1

# Or use batch files (auto-configure UTF-8)
start_http_server.bat
tests\run_all_tests.bat
```

## Configuration

Create a `.env` file in the project root with your API key:

```env
TEST_API_KEY=your_test_api_key_here
# or for production:
# API_KEY=your_production_api_key_here
```

**📋 For comprehensive configuration guides:**
- **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - Complete setup for VS Code, LM Studio, Claude.ai
- **[docs/QUICK_CONFIG.md](docs/QUICK_CONFIG.md)** - Fast configuration reference
- **[docs/TOOL_CONFIGURATION.md](docs/TOOL_CONFIGURATION.md)** - Tool customization and language options

### Getting API Keys
Visit https://api.stat.gov.pl/Home/RegonApi to register and obtain your API keys from the Polish GUS organization.

### Tool Configuration

The server supports customizable tool descriptions and multiple languages:

- **English** (default): Technical descriptions in English
- **Polish** (polski): Native Polish terminology and descriptions  
- **Minimal**: Essential tools only for basic usage
- **Detailed**: Comprehensive tool set with full descriptions

```bash
# Use Polish configuration
python regon_mcp_server/server.py --tools-config polish

# Use minimal tool set
python regon_mcp_server/server.py --tools-config minimal

# Set via environment variable
set TOOLS_CONFIG=polish
python regon_mcp_server/server.py
```

Available configurations: `default`, `polish`, `minimal`, `detailed`

## Usage

### Running the Server

Run the MCP server using:

```bash
python regon_mcp_server.py
```

The server uses stdio for communication, making it compatible with MCP clients.

### Available Tools

#### Search Tools

1. **regon_search_by_nip** - Search by NIP number
   - Input: `nip` (string) - 10-digit NIP number
   
2. **regon_search_by_regon** - Search by REGON number  
   - Input: `regon` (string) - 9 or 14-digit REGON number
   
3. **regon_search_by_krs** - Search by KRS number
   - Input: `krs` (string) - 10-digit KRS number

4. **regon_search_multiple_nips** - Search multiple entities by NIP
   - Input: `nips` (array of strings) - List of NIP numbers

5. **regon_search_multiple_regons9** - Search multiple entities by 9-digit REGON
   - Input: `regons9` (array of strings) - List of 9-digit REGON numbers

6. **regon_search_multiple_regons14** - Search multiple entities by 14-digit REGON
   - Input: `regons14` (array of strings) - List of 14-digit REGON numbers

7. **regon_search_multiple_krs** - Search multiple entities by KRS
   - Input: `krss` (array of strings) - List of KRS numbers

#### Report Tools

8. **regon_get_full_report** - Download detailed report
   - Input: 
     - `regon` (string) - REGON number
     - `report_name` (string) - Report type (see available reports below)
     - `strict` (boolean, optional) - Validate report name strictly (default: true)

#### Status Tools

9. **regon_get_service_status** - Get API service status
10. **regon_get_data_status** - Get database last update date
11. **regon_get_available_operations** - List all WSDL operations
12. **regon_get_last_error_code** - Get last API error information

### Available Report Types

For natural persons (physical entities):
- `BIR11OsFizycznaDaneOgolne` - General data
- `BIR11OsFizycznaDzialalnoscCeidg` - CEIDG activity
- `BIR11OsFizycznaDzialalnoscRolnicza` - Agricultural activity
- `BIR11OsFizycznaDzialalnoscPozostala` - Other activities
- `BIR11OsFizycznaDzialalnoscSkreslonaDo20141108` - Deleted activities (until 2014-11-08)
- `BIR11OsFizycznaPkd` - PKD (Polish Activity Classification)
- `BIR11OsFizycznaListaJednLokalnych` - List of local units
- `BIR11JednLokalnaOsFizycznej` - Local unit of natural person
- `BIR11JednLokalnaOsFizycznejPkd` - Local unit PKD

For legal entities:
- `BIR11OsPrawna` - Legal entity basic data
- `BIR11OsPrawnaPkd` - Legal entity PKD
- `BIR11OsPrawnaListaJednLokalnych` - List of local units
- `BIR11JednLokalnaOsPrawnej` - Local unit of legal entity
- `BIR11JednLokalnaOsPrawnejPkd` - Local unit PKD
- `BIR11OsPrawnaSpCywilnaWspolnicy` - Civil partnership participants

General:
- `BIR11TypPodmiotu` - Entity type

## API Key Information

### Test Environment
- The server is configured to use the test environment by default
- Test API key: `abcde12345abcde12345` (official test key)
- You can use your own test key in the `.env` file

### Production Environment
To use the production environment:
1. Set `is_production=True` in the `regon_mcp_server.py` file
2. Use a production API key in your `.env` file as `API_KEY`

### Obtaining an API Key
To get a production API key, visit: [GUS REGON API](https://api.stat.gov.pl/Home/RegonApi)

## Example Usage with MCP Client

```json
{
  "method": "tools/call",
  "params": {
    "name": "regon_search_by_nip", 
    "arguments": {
      "nip": "7342867148"
    }
  }
}
```

## Error Handling

The server includes comprehensive error handling for:
- Authentication failures
- Invalid parameters
- Network timeouts
- API rate limits
- Unknown report names
- Invalid data formats

## Logging

The server logs important events and errors. Check the console output for diagnostic information.

## Testing

The `tests/` folder contains comprehensive test suites for both stdio and HTTP servers:

### Quick Test Run
```bash
# Run all tests (default port 8001)
.\.venv\Scripts\python.exe tests\run_all_tests.py

# Run all tests with custom HTTP port
.\.venv\Scripts\python.exe tests\run_all_tests.py --port 8000

# Or use batch file (default port 8001)
tests\run_all_tests.bat

# Or use batch file with custom port
tests\run_all_tests.bat 8000
```

### Individual Tests
```bash
# Test stdio MCP server
.\.venv\Scripts\python.exe tests\test_stdio_server.py

# Test HTTP server (requires server running, default port 8001)
.\.venv\Scripts\python.exe tests\test_http_server.py

# Test HTTP server on custom port
.\.venv\Scripts\python.exe tests\test_http_server.py --port 8000

# Test MCP protocol compliance
.\.venv\Scripts\python.exe tests\test_mcp_protocol.py
```

See `tests/README.md` for detailed testing documentation.

## Examples

The `examples/` folder contains comprehensive usage examples:

- **`basic_usage_example.py`** - Introduction to MCP server usage (based on original RegonAPI examples)
- **`bulk_search_example.py`** - Performance optimization through bulk operations
- **`reports_example.py`** - Comprehensive report generation for all entity types
- **`monitoring_example.py`** - Error handling and service monitoring best practices
- **`advanced_example.py`** - Complex business workflows and data analysis

### Quick Example Run
```bash
cd examples
python basic_usage_example.py
# or run all examples
python run_all_examples.py
```

See [examples/README.md](examples/README.md) for detailed documentation.

## Technical Details

- Built using the MCP (Model Context Protocol) framework
- Uses the RegonAPI Python library for REGON database access
- Supports stdio communication for MCP clients
- Implements proper error handling and logging
- Uses environment variables for configuration

## License

This project is provided as-is. Please check the RegonAPI library license for usage terms.

## Support

For issues related to:
- The RegonAPI library: Check the [RegonAPI GitHub repository](https://github.com/rolzwy7/RegonAPI)
- The REGON database: Visit [GUS REGON API documentation](https://api.stat.gov.pl/Home/RegonApi)
- MCP protocol: Check the [Model Context Protocol documentation](https://spec.modelcontextprotocol.io/)
