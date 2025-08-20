# 📚 RegonAPI MCP Server Documentation

Welcome to the comprehensive documentation for the RegonAPI MCP Server - a robust, production-ready Model Context Protocol server for accessing Polish business registry data.

## 📋 Documentation Index

### 🚀 Getting Started
- **[README.md](../README.md)** - Main project overview and quick start guide
- **[QUICK_CONFIG.md](QUICK_CONFIG.md)** - Fast configuration guide for common setups

### ⚙️ Configuration Guides
- **[CONFIGURATION.md](CONFIGURATION.md)** - Complete configuration guide for all MCP clients
- **[TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md)** - Tool customization and JSON configuration reference

### 🌐 Server Deployment
- **[HTTP_SERVER_README.md](HTTP_SERVER_README.md)** - HTTP REST API server documentation
- **[SERVER_HARDENING_SUMMARY.md](SERVER_HARDENING_SUMMARY.md)** - Production hardening and error handling

### 🔧 Implementation Details
- **[TOOLS_CONFIG_IMPLEMENTATION.md](TOOLS_CONFIG_IMPLEMENTATION.md)** - Technical implementation of tool customization
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview and architecture

### 🧪 Development & Testing
- **[EXAMPLES_COMPLETION.md](EXAMPLES_COMPLETION.md)** - Example scripts and usage patterns

## 🎯 Quick Navigation

### For First-Time Users
1. Start with [README.md](../README.md) for project overview
2. Use [QUICK_CONFIG.md](QUICK_CONFIG.md) for fast setup
3. Check [CONFIGURATION.md](CONFIGURATION.md) for your specific MCP client

### For Advanced Configuration
1. Review [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md) for customization options
2. Check [HTTP_SERVER_README.md](HTTP_SERVER_README.md) for REST API deployment
3. See [SERVER_HARDENING_SUMMARY.md](SERVER_HARDENING_SUMMARY.md) for production deployment

### For Developers
1. Study [TOOLS_CONFIG_IMPLEMENTATION.md](TOOLS_CONFIG_IMPLEMENTATION.md) for technical details
2. Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for architecture overview
3. Check examples/ folder for usage patterns and testing

## 🌟 Key Features Documented

### 🛠️ Tool Customization System
- **4 Pre-configured tool sets**: default, polish, minimal, detailed
- **Multi-language support**: English and Polish descriptions
- **Custom JSON configurations**: Create your own tool descriptions
- **Runtime configuration**: Switch tool sets via command line or environment variables

### 🌐 Dual Protocol Support
- **Stdio MCP Protocol**: For VS Code, Claude.ai, and other MCP clients
- **HTTP REST API**: For web applications and direct API access
- **Unified functionality**: Same tools available via both protocols

### 🛡️ Production-Ready Features
- **Comprehensive error handling**: Bullet-proof against runtime errors
- **Automatic retry mechanisms**: Network resilience and recovery
- **Input validation**: Sanitization of all user inputs
- **Graceful degradation**: Continues running despite component failures
- **Security features**: Production-ready hardening

### 🌍 UTF-8 & Polish Character Support
- **Native Polish character handling**: SPÓŁKA, Północ, etc.
- **Windows compatibility**: Proper console encoding
- **Cross-platform support**: Linux, macOS, Windows

## 📁 File Structure

```
docs/
├── README.md                        # This index file
├── CONFIGURATION.md                 # Complete configuration guide
├── QUICK_CONFIG.md                  # Fast setup guide
├── TOOL_CONFIGURATION.md            # Tool customization reference
├── HTTP_SERVER_README.md            # HTTP server documentation
├── SERVER_HARDENING_SUMMARY.md     # Production hardening guide
├── TOOLS_CONFIG_IMPLEMENTATION.md  # Technical implementation details
├── PROJECT_SUMMARY.md              # Project architecture overview
└── EXAMPLES_COMPLETION.md          # Usage examples and patterns

```

## 🔗 Related Resources

### Configuration Files
- **`config/`** - Tool configuration JSON files
- **`mcp.json`** - MCP client configuration template
- **`.env.example`** - Environment variables template

### Example Scripts
- **`examples/`** - Usage examples and demonstration scripts
- **`tests/`** - Test suite and validation scripts

### Core Implementation
- **`regon_mcp_server/`** - Main server implementation
- **`regon_mcp_server/server.py`** - Stdio MCP server
- **`regon_mcp_server/server_http.py`** - HTTP REST API server
- **`regon_mcp_server/error_handling.py`** - Error handling framework

## 🆘 Getting Help

1. **Configuration Issues**: Check [CONFIGURATION.md](CONFIGURATION.md) and [QUICK_CONFIG.md](QUICK_CONFIG.md)
2. **Tool Customization**: See [TOOL_CONFIGURATION.md](TOOL_CONFIGURATION.md)
3. **HTTP API**: Review [HTTP_SERVER_README.md](HTTP_SERVER_README.md)
4. **Production Deployment**: Follow [SERVER_HARDENING_SUMMARY.md](SERVER_HARDENING_SUMMARY.md)

## 📝 Documentation Updates

This documentation was last updated: **August 19, 2025**

All guides include the latest features:
- ✅ Server hardening and error handling
- ✅ Tool JSON customization system
- ✅ HTTP REST API wrapper
- ✅ Multi-language support (English/Polish)
- ✅ Production-ready configuration options

---

**📍 Start Here**: New users should begin with [README.md](../README.md) and [QUICK_CONFIG.md](QUICK_CONFIG.md) for the fastest setup experience.
