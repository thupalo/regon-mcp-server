# Tool Configuration Quick Reference

The REGON MCP Server supports customizable tool descriptions and configurations through JSON files. This allows you to use the server with different languages, description styles, and tool sets.

## Available Configurations

| Configuration | Name | Language | Tools | Description |
|---------------|------|----------|-------|-------------|
| `default` | RegonAPI MCP Server | English | 13 | Complete tool set with clear English descriptions |
| `polish` | Serwer MCP RegonAPI | Polish | 13 | Comprehensive Polish descriptions and terminology |
| `minimal` | RegonAPI MCP Server - Minimal | English | 4 | Essential tools only for basic usage |
| `detailed` | RegonAPI MCP Server | English | 12 | Original comprehensive configuration |

## Usage Examples

### Environment Variable
```bash
# Use Polish configuration
set TOOLS_CONFIG=polish
python regon_mcp_server/server.py

# Use minimal configuration
set TOOLS_CONFIG=minimal
python regon_mcp_server/server.py
```

### Command Line
```bash
# Use Polish configuration
python regon_mcp_server/server.py --tools-config polish

# Use minimal configuration with production mode
python regon_mcp_server/server.py --tools-config minimal --production

# HTTP server with Polish tools
python regon_mcp_server/server_http.py --tools-config polish --port 8080
```

### .env File Configuration
```
# Add to your .env file
TOOLS_CONFIG=polish
LOG_LEVEL=INFO
API_KEY=your_production_key
TEST_API_KEY=your_test_key
```

## Configuration Files

All configuration files are located in the `config/` directory:

- `tools_default.json` - English descriptions, complete tool set
- `tools_polish.json` - Polish descriptions, complete tool set  
- `tools_minimal.json` - English descriptions, essential tools only
- `tools_detailed.json` - Original comprehensive configuration

## Tool Configuration Format

Each JSON configuration file contains:

```json
{
  "name": "Server Name",
  "version": "1.0.0", 
  "description": "Server description",
  "language": "en",
  "tools": [
    {
      "name": "tool_name",
      "description": "Tool description",
      "inputSchema": {
        "type": "object",
        "properties": { ... },
        "required": [...]
      }
    }
  ]
}
```

## Creating Custom Configurations

1. Copy an existing configuration file from `config/`
2. Modify the descriptions, tool names, or add/remove tools
3. Save with a new name (e.g., `tools_custom.json`)
4. Use with `--tools-config custom` or `TOOLS_CONFIG=custom`

## Validation

Test your configuration setup:

```bash
python test_tool_config.py
```

This will validate all configurations and show available options.

## MCP Client Integration

### VS Code Settings
```json
{
  "mcpServers": {
    "regon": {
      "command": "python",
      "args": [
        "C:/path/to/regon_mcp_server/server.py",
        "--tools-config", "polish"
      ],
      "env": {
        "TOOLS_CONFIG": "polish"
      }
    }
  }
}
```

### Claude.ai Desktop
When using Claude Desktop, add the tools configuration to your environment:

```json
{
  "mcpServers": {
    "regon": {
      "command": "python",
      "args": ["C:/path/to/regon_mcp_server/server.py"],
      "env": {
        "TOOLS_CONFIG": "polish",
        "TEST_API_KEY": "your_test_key"
      }
    }
  }
}
```

## Language Support

- **English (`en`)**: Default technical descriptions
- **Polish (`pl`)**: Native Polish terminology and descriptions
- Custom languages can be added by creating new configuration files

The Polish configuration includes proper Polish business terminology:
- "Wyszukiwanie podmiotów gospodarczych" (Business entity search)
- "Numer identyfikacji podatkowej NIP" (Tax identification number)
- "Krajowy Rejestr Sądowy KRS" (National Court Register)
- And more...
