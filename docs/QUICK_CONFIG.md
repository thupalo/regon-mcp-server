# REGON MCP Server - Quick Configuration Reference

## 🚀 Quick Setup

### 1. Get API Key
Visit: https://api.stat.gov.pl/Home/RegonApi

### 2. Create .env file
```env
API_KEY=your_production_key
TEST_API_KEY=your_test_key
PYTHONIOENCODING=utf-8
```

### 3. Choose Configuration

#### VS Code
```json
{
  "mcp.servers": {
    "regon-api": {
      "command": ".venv/Scripts/python.exe",
      "args": ["regon_mcp_server/server.py", "--production"],
      "env": {"PYTHONIOENCODING": "utf-8"}
    }
  }
}
```

#### LM Studio
Location: `%APPDATA%\lmstudio\mcp.json`
```json
{
  "mcpServers": {
    "regon-api": {
      "command": "C:/path/to/.venv/Scripts/python.exe",
      "args": ["C:/path/to/regon_mcp_server/server.py", "--production"],
      "env": {"PYTHONIOENCODING": "utf-8"}
    }
  }
}
```

#### Claude Desktop
Location: `%APPDATA%\Claude\claude_desktop_config.json`
```json
{
  "mcpServers": {
    "regon-api": {
      "command": "C:/absolute/path/.venv/Scripts/python.exe",
      "args": ["C:/absolute/path/regon_mcp_server/server.py", "--production"],
      "env": {"PYTHONIOENCODING": "utf-8"}
    }
  }
}
```

## 🌐 Protocol Options

| Protocol | Use Case | Configuration |
|----------|----------|---------------|
| STDIO | MCP Clients | `server.py` |
| HTTP | Web Apps | `server_http.py --port 8001` |

## 🔧 Mode Options

| Mode | API Key | Use Case |
|------|---------|----------|
| Test | `TEST_API_KEY` | Development |
| Production | `API_KEY` | Live data |

## 📊 Port Configuration

Default HTTP port: `8001`
Custom port: `--port 8080`

## ✅ Test Configuration

```bash
.\.venv\Scripts\python.exe tests\run_all_tests.py
```

See [CONFIGURATION.md](CONFIGURATION.md) for detailed setup instructions.
