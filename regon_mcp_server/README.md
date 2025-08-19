# RegonAPI MCP Server - Clean Version

This is the consolidated, production-ready version of the RegonAPI MCP Server with configurable environment support.

## Project Structure

```
REGON_mcp_server/
├── regon_mcp_server/           # Clean server package
│   ├── __init__.py
│   └── server.py               # Main consolidated server
├── examples/                   # Example usage (updated to use new server)
├── mcp.json                    # MCP host configuration examples
├── .env                        # Environment variables (API keys)
├── .env.example               # Environment template
└── requirements.txt           # Python dependencies
```

## Configuration

### Environment Variables (.env file)

```bash
# Test environment API key (default provided by GUS)
TEST_API_KEY=abcde12345abcde12345

# Production API key (obtain from GUS)
API_KEY=your_production_api_key_here

# Optional: Logging level
LOG_LEVEL=INFO
```

### Command Line Usage

```bash
# Test mode (default) with INFO logging
python regon_mcp_server/server.py

# Production mode with production API key
python regon_mcp_server/server.py --production

# Debug mode with detailed logging
python regon_mcp_server/server.py --log-level DEBUG

# Production mode with warning-level logging
python regon_mcp_server/server.py --production --log-level WARNING
```

### MCP Host Configuration

The `mcp.json` file provides three pre-configured server instances:

1. **regon-api-test** - Test mode with INFO logging
2. **regon-api-production** - Production mode with WARNING logging  
3. **regon-api-debug** - Test mode with DEBUG logging

## API Key Selection Logic

### Test Mode (default)
1. Uses `TEST_API_KEY` from .env
2. Falls back to `API_KEY` if TEST_API_KEY not found
3. Uses default test key `abcde12345abcde12345` as last resort

### Production Mode (--production flag)
1. Uses `API_KEY` from .env (required for production)
2. Falls back to `TEST_API_KEY` with warning if API_KEY not found
3. Raises error if no keys are available

## Usage Examples

### From Command Line
```bash
# Start in test mode
python regon_mcp_server/server.py

# Start in production mode
python regon_mcp_server/server.py --production --log-level WARNING
```

### From MCP Host (Claude Desktop, etc.)
Configure your MCP host to use one of the configurations from `mcp.json`:

```json
{
  "mcpServers": {
    "regon-api": {
      "command": "python",
      "args": ["regon_mcp_server/server.py", "--production"],
      "cwd": "/path/to/REGON_mcp_server"
    }
  }
}
```

## Available Tools

- `regon_search_by_nip` - Search by tax number (NIP)
- `regon_search_by_regon` - Search by business registry number (REGON)
- `regon_search_by_krs` - Search by court register number (KRS)
- `regon_search_multiple_nips` - Bulk search by multiple NIPs
- `regon_search_multiple_regons9` - Bulk search by multiple REGONs
- `regon_search_multiple_krs` - Bulk search by multiple KRS numbers
- `regon_get_full_report` - Get detailed business reports
- `regon_get_service_status` - Check service availability
- `regon_get_data_status` - Get data status information
- `regon_get_last_error_code` - Get last error code
- `regon_get_last_error_message` - Get last error message
- `regon_get_session_status` - Check session status

## Testing

Run the updated examples to verify functionality:

```bash
cd examples
python run_all_examples.py
```

All examples now use the consolidated server and should work identically to the previous versions.

## Migration from Old Versions

The old server files have been consolidated:
- `regon_mcp_server.py` → Replaced by `regon_mcp_server/server.py`
- `regon_mcp_server_fixed.py` → Replaced by `regon_mcp_server/server.py`
- `regon_mcp_server_prod.py` → Replaced by `regon_mcp_server/server.py --production`

The new server includes all fixes and improvements from the previous versions while adding configurable environment support.
