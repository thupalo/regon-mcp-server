# REGON MCP Server Configuration Guide

This guide covers how to configure the REGON MCP Server for different environments and applications, including VS Code, LM Studio, and Claude.ai.

> **🆕 2025 Update**: VS Code MCP configuration now uses `.vscode/mcp.json` instead of `settings.json`. This guide has been updated to reflect the new format.

## 📋 Table of Contents

- [API Key Setup](#-api-key-setup)
- [MCP Configuration File](#-mcp-configuration-file)
- [Environment Variables](#-environment-variables)
- [VS Code Configuration](#-vs-code-configuration)
- [LM Studio Configuration](#-lm-studio-configuration)
- [Claude.ai Configuration](#-claudeai-configuration)
- [Protocol Options](#-protocol-options)
- [Testing Configuration](#-testing-configuration)
- [Troubleshooting](#-troubleshooting)

## 🔑 API Key Setup

### Getting Your API Key from GUS

1. **Visit the GUS RegonAPI Portal**: https://api.stat.gov.pl/Home/RegonApi
2. **Register for an account** or log in if you already have one
3. **Request API access**:
   - Fill out the application form
   - Specify your intended use case
   - Wait for approval (usually takes 1-3 business days)
4. **Receive your API key** via email
5. **Note the difference**:
   - **Test Key**: For development and testing (limited data)
   - **Production Key**: For production use (full access, rate limits apply)

### Setting Up Your API Key

Create a `.env` file in your project root:

```env
# Production API Key (from GUS)
API_KEY=your_production_api_key_here

# Test API Key (from GUS or default test key)
TEST_API_KEY=your_test_api_key_here

# Optional: Logging configuration
LOG_LEVEL=INFO
PYTHONIOENCODING=utf-8
```

**Security Note**: Never commit your `.env` file to version control. Add it to `.gitignore`.

## 📄 MCP Configuration File

The `mcp.json` file defines how MCP clients connect to the REGON server. Here are the main configuration options:

### Basic Configuration Structure

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["regon_mcp_server/server.py"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Pre-configured Server Options

#### 1. Test Mode (Default)
```json
{
  "mcpServers": {
    "regon-api-test": {
      "command": "python",
      "args": [
        "regon_mcp_server/server.py"
      ],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### 2. Production Mode
```json
{
  "mcpServers": {
    "regon-api-production": {
      "command": "python", 
      "args": [
        "regon_mcp_server/server.py",
        "--production",
        "--log-level",
        "WARNING"
      ],
      "env": {
        "LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

#### 3. Debug Mode
```json
{
  "mcpServers": {
    "regon-api-debug": {
      "command": "python",
      "args": [
        "regon_mcp_server/server.py",
        "--log-level",
        "DEBUG"
      ],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

#### 4. HTTP Server Mode
```json
{
  "mcpServers": {
    "regon-api-http": {
      "command": "python",
      "args": [
        "regon_mcp_server/server_http.py",
        "--port",
        "8001"
      ],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Virtual Environment Configuration

If using a virtual environment (recommended):

```json
{
  "mcpServers": {
    "regon-api-venv": {
      "command": ".venv/Scripts/python.exe",
      "args": [
        "regon_mcp_server/server.py",
        "--production"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## 🌍 Environment Variables

### Required Variables
- `API_KEY`: Your production API key from GUS
- `TEST_API_KEY`: Your test API key (optional, fallback available)

### Optional Variables
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `PYTHONIOENCODING`: Character encoding (set to `utf-8` for Polish characters)

### Setting Environment Variables

#### Windows (PowerShell)
```powershell
$env:API_KEY = "your_production_key"
$env:TEST_API_KEY = "your_test_key"
$env:PYTHONIOENCODING = "utf-8"
```

#### Windows (Command Prompt)
```cmd
set API_KEY=your_production_key
set TEST_API_KEY=your_test_key
set PYTHONIOENCODING=utf-8
```

#### Linux/macOS
```bash
export API_KEY="your_production_key"
export TEST_API_KEY="your_test_key"
export PYTHONIOENCODING="utf-8"
```

## 🛠️ Tool Configuration and Customization

The REGON MCP Server supports customizable tool descriptions and configurations through JSON files. This allows you to use the server with different languages, description styles, and tool sets.

### Available Tool Configurations

| Configuration | Language | Tools | Description |
|---------------|----------|-------|-------------|
| `default` | English | 13 | Complete tool set with clear English descriptions |
| `polish` | Polish | 13 | Comprehensive Polish descriptions and terminology |
| `minimal` | English | 4 | Essential tools only for basic usage |
| `detailed` | English | 12 | Original comprehensive configuration |

### Using Tool Configurations

#### Via Command Line Arguments
```bash
# Use Polish tool descriptions
python regon_mcp_server/server.py --tools-config polish

# Use minimal tool set
python regon_mcp_server/server.py --tools-config minimal --production

# HTTP server with Polish tools
python regon_mcp_server/server_http.py --tools-config polish --port 8080
```

#### Via Environment Variables
```bash
# Set default tool configuration
export TOOLS_CONFIG=polish

# Then run the server normally
python regon_mcp_server/server.py --production
```

#### Via .env File
```env
# Add to your .env file
TOOLS_CONFIG=polish
LOG_LEVEL=INFO
API_KEY=your_production_key
TEST_API_KEY=your_test_key
```

### MCP Client Configuration with Tool Customization

#### VS Code with Polish Tools (2025 Format)
Create `.vscode/mcp.json`:
```json
{
  "mcpServers": {
    "regon-api-polish": {
      "command": ".venv/Scripts/python.exe",
      "args": [
        "regon_mcp_server/server.py",
        "--tools-config", "polish",
        "--production"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "TOOLS_CONFIG": "polish"
      }
    }
  }
}
```

#### LM Studio with Minimal Tools
```json
{
  "mcpServers": {
    "regon-api-minimal": {
      "command": "python",
      "args": [
        "C:/path/to/regon_mcp_server/server.py",
        "--tools-config", "minimal"
      ],
      "env": {
        "TOOLS_CONFIG": "minimal",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Claude.ai with Custom Configuration
```json
{
  "mcpServers": {
    "regon-custom": {
      "command": "python",
      "args": ["C:/path/to/regon_mcp_server/server.py"],
      "env": {
        "TOOLS_CONFIG": "detailed",
        "TEST_API_KEY": "your_test_key"
      }
    }
  }
}
```

### Creating Custom Tool Configurations

1. **Copy an existing configuration** from `config/` directory:
   ```bash
   cp config/tools_default.json config/tools_custom.json
   ```

2. **Edit the configuration** with your preferred descriptions:
   ```json
   {
     "name": "Custom RegonAPI Server",
     "version": "1.0.0",
     "description": "Customized Polish business data server",
     "language": "en",
     "tools": [
       {
         "name": "regon_search_by_nip",
         "description": "Your custom description here",
         "inputSchema": { ... }
       }
     ]
   }
   ```

3. **Use your custom configuration**:
   ```bash
   python regon_mcp_server/server.py --tools-config custom
   ```

### Testing Tool Configurations

Validate your configuration setup:
```bash
python test_tool_config.py
```

This will show all available configurations and validate their structure.

For detailed information about tool customization, see: [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md)

## 💻 VS Code Configuration

### 1. Install MCP Extension
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "MCP" or "Model Context Protocol"
4. Install the official MCP extension

### 2. Workspace Configuration (2025 Format)

Create `.vscode/mcp.json` in your project workspace:

```json
{
  "mcpServers": {
    "regon-api": {
      "command": ".venv/Scripts/python.exe",
      "args": [
        "regon_mcp_server/server.py",
        "--production"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. Advanced Workspace Configurations

#### Production Setup
Create `.vscode/mcp.json` for production use:

```json
{
  "mcpServers": {
    "regon-api-production": {
      "command": ".venv/Scripts/python.exe",
      "args": [
        "regon_mcp_server/server.py",
        "--production",
        "--tools-config", "polish",
        "--log-level", "WARNING"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

#### Development Setup
Create `.vscode/mcp.json` for development:

```json
{
  "mcpServers": {
    "regon-api-dev": {
      "command": ".venv/Scripts/python.exe",
      "args": [
        "regon_mcp_server/server.py",
        "--tools-config", "default",
        "--log-level", "DEBUG"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

#### Multi-Server Setup
Configure multiple REGON servers for different purposes:

```json
{
  "mcpServers": {
    "regon-test": {
      "command": ".venv/Scripts/python.exe",
      "args": [
        "regon_mcp_server/server.py",
        "--tools-config", "minimal"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    },
    "regon-production": {
      "command": ".venv/Scripts/python.exe",
      "args": [
        "regon_mcp_server/server.py",
        "--production",
        "--tools-config", "polish"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    },
    "regon-http": {
      "command": ".venv/Scripts/python.exe",
      "args": [
        "regon_mcp_server/server_http.py",
        "--port", "8001",
        "--tools-config", "detailed"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### 4. Legacy Configuration (Pre-2025)

> **Note**: The following format is deprecated. Use `.vscode/mcp.json` instead.

<details>
<summary>Click to view legacy settings.json format</summary>

```json
{
  "mcp.servers": {
    "regon-api": {
      "command": "python",
      "args": [
        "regon_mcp_server/server.py",
        "--production"
      ],
      "cwd": "C:/path/to/your/REGON_mcp_server",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```
</details>
```

```
</details>

### 5. Validation and Testing

After creating your `.vscode/mcp.json` file, verify the configuration:

1. **Check file location**: Ensure `.vscode/mcp.json` is in your workspace root
2. **Validate JSON syntax**: Use VS Code's JSON validation or online JSON validators
3. **Test server startup**: Open VS Code command palette (Ctrl+Shift+P) and run "MCP: Restart Servers"
4. **Check MCP panel**: Look for the REGON server in VS Code's MCP panel
5. **Test functionality**: Try using REGON tools in your VS Code AI assistant

#### Quick Validation Example
Create a minimal `.vscode/mcp.json` for testing:
```json
{
  "mcpServers": {
    "regon-test": {
      "command": ".venv/Scripts/python.exe",
      "args": ["regon_mcp_server/server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

#### Troubleshooting VS Code MCP
- **Server not starting**: Check Python path and virtual environment activation
- **Import errors**: Verify dependencies are installed (`pip install -r requirements.txt`)
- **Encoding issues**: Ensure `PYTHONIOENCODING=utf-8` is set
- **Permission errors**: Check file permissions and virtual environment access

## 🎯 LM Studio Configuration

### 1. Install LM Studio
Download from: https://lmstudio.ai/

### 2. Enable MCP Plugin
1. Open LM Studio
2. Go to Settings → Plugins
3. Enable "Model Context Protocol (MCP)" plugin
4. Restart LM Studio

### 3. Configure REGON Server

Create MCP configuration file for LM Studio:

**Location**: `~/.config/lmstudio/mcp.json` (Linux/macOS) or `%APPDATA%\lmstudio\mcp.json` (Windows)

```json
{
  "mcpServers": {
    "regon-api": {
      "command": "python",
      "args": [
        "C:/path/to/REGON_mcp_server/regon_mcp_server/server.py",
        "--production"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 4. Virtual Environment Setup for LM Studio

```json
{
  "mcpServers": {
    "regon-api": {
      "command": "C:/path/to/REGON_mcp_server/.venv/Scripts/python.exe",
      "args": [
        "C:/path/to/REGON_mcp_server/regon_mcp_server/server.py",
        "--production"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

## 🤖 Claude.ai Configuration

### Desktop App Configuration

1. **Install Claude Desktop App**
2. **Locate configuration file**:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

3. **Add REGON MCP Server**:

```json
{
  "mcpServers": {
    "regon-api": {
      "command": "python",
      "args": [
        "C:/absolute/path/to/REGON_mcp_server/regon_mcp_server/server.py",
        "--production"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### Virtual Environment Configuration for Claude

```json
{
  "mcpServers": {
    "regon-api": {
      "command": "C:/absolute/path/to/REGON_mcp_server/.venv/Scripts/python.exe",
      "args": [
        "C:/absolute/path/to/REGON_mcp_server/regon_mcp_server/server.py",
        "--production",
        "--log-level",
        "WARNING"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### Multiple Server Configurations

You can configure multiple servers for different purposes:

```json
{
  "mcpServers": {
    "regon-test": {
      "command": "C:/path/to/.venv/Scripts/python.exe",
      "args": [
        "C:/path/to/regon_mcp_server/server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    },
    "regon-production": {
      "command": "C:/path/to/.venv/Scripts/python.exe",
      "args": [
        "C:/path/to/regon_mcp_server/server.py",
        "--production"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

## 🌐 Protocol Options

### STDIO Protocol (Default)
- **Use case**: Direct integration with MCP clients
- **Configuration**: Use `server.py`
- **Communication**: JSON-RPC over stdin/stdout
- **Performance**: Fastest, lowest overhead

```json
{
  "command": "python",
  "args": ["regon_mcp_server/server.py"]
}
```

### HTTP Protocol
- **Use case**: Web applications, REST API access
- **Configuration**: Use `server_http.py`
- **Communication**: HTTP REST endpoints
- **Performance**: Slightly higher overhead, more flexible

```json
{
  "command": "python",
  "args": [
    "regon_mcp_server/server_http.py",
    "--port", "8001"
  ]
}
```

### Production vs Test Mode

#### Test Mode (Default)
- Uses `TEST_API_KEY` or default test key
- Limited data access
- Suitable for development and testing

```json
{
  "args": ["regon_mcp_server/server.py"]
}
```

#### Production Mode
- Uses `API_KEY` (required)
- Full data access
- Rate limits apply

```json
{
  "args": [
    "regon_mcp_server/server.py",
    "--production"
  ]
}
```

### HTTP Port Configuration

For HTTP server, specify custom port:

```json
{
  "args": [
    "regon_mcp_server/server_http.py",
    "--port", "8080",
    "--host", "0.0.0.0"
  ]
}
```

Available HTTP endpoints:
- `GET /` - Server information
- `GET /health` - Health check
- `GET /tools` - List MCP tools
- `POST /tools/call` - Call MCP tool
- `GET /search/nip/{nip}` - Search by NIP
- `GET /search/krs/{krs}` - Search by KRS
- `GET /search/regon/{regon}` - Search by REGON
- `GET /docs` - API documentation

## 🧪 Testing Configuration

### Verify Configuration

1. **Test STDIO server**:
```bash
.\.venv\Scripts\python.exe tests\test_stdio_server.py
```

2. **Test HTTP server**:
```bash
# Start server
.\.venv\Scripts\python.exe regon_mcp_server\server_http.py --port 8001

# Test in another terminal
.\.venv\Scripts\python.exe tests\test_http_server.py --port 8001
```

3. **Test MCP protocol**:
```bash
.\.venv\Scripts\python.exe tests\test_mcp_protocol.py
```

4. **Run all tests**:
```bash
.\.venv\Scripts\python.exe tests\run_all_tests.py
```

### Configuration Validation

Test your configuration with:

```json
{
  "mcpServers": {
    "regon-config-test": {
      "command": "python",
      "args": [
        "regon_mcp_server/server.py",
        "--log-level", "DEBUG"
      ],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. "Module not found" Error
**Problem**: Python can't find the RegonAPI module
**Solution**: 
```bash
pip install -r requirements.txt
```

#### 2. "API Key not found" Error
**Problem**: Missing or invalid API key
**Solution**: Check your `.env` file and ensure API keys are correctly set

#### 3. "UnicodeEncodeError" 
**Problem**: Character encoding issues
**Solution**: Set `PYTHONIOENCODING=utf-8` in environment

#### 4. "Connection refused" (HTTP mode)
**Problem**: HTTP server not running
**Solution**: Start the HTTP server first:
```bash
.\.venv\Scripts\python.exe regon_mcp_server\server_http.py --port 8001
```

#### 5. "Invalid request parameters"
**Problem**: MCP protocol version mismatch
**Solution**: Ensure you're using a compatible MCP client version

### Debug Configuration

Enable debug logging for troubleshooting:

```json
{
  "mcpServers": {
    "regon-debug": {
      "command": "python",
      "args": [
        "regon_mcp_server/server.py",
        "--log-level", "DEBUG"
      ],
      "env": {
        "LOG_LEVEL": "DEBUG",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### Path Issues

Use absolute paths if relative paths don't work:

```json
{
  "command": "C:/absolute/path/to/.venv/Scripts/python.exe",
  "args": [
    "C:/absolute/path/to/regon_mcp_server/server.py"
  ]
}
```

### Environment Setup Script

Create a setup script for easy configuration:

**Windows (`setup.bat`):**
```batch
@echo off
set PYTHONIOENCODING=utf-8
set LOG_LEVEL=INFO
echo Environment configured for REGON MCP Server
python regon_mcp_server/server.py --production
```

**PowerShell (`setup.ps1`):**
```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:LOG_LEVEL = "INFO"
Write-Host "Environment configured for REGON MCP Server"
python regon_mcp_server/server.py --production
```

## 📚 Additional Resources

- **GUS RegonAPI Documentation**: https://api.stat.gov.pl/Home/RegonApi
- **MCP Protocol Specification**: https://modelcontextprotocol.io/
- **LM Studio MCP Plugin Docs**: https://lmstudio.ai/docs/app/plugins/mcp
- **VS Code MCP Extension**: Search "MCP" in VS Code Extensions
- **Claude Desktop App**: Available from Anthropic

## 🎯 Quick Start Checklist

- [ ] Obtain API key from GUS
- [ ] Create `.env` file with API keys
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Configure UTF-8 encoding (`PYTHONIOENCODING=utf-8`)
- [ ] Choose protocol (STDIO for MCP clients, HTTP for web apps)
- [ ] Configure your MCP client (VS Code, LM Studio, Claude)
- [ ] Test configuration with test scripts
- [ ] Switch to production mode when ready

Your REGON MCP Server is now ready to provide Polish business registry data to your AI applications! 🎉
