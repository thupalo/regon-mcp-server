# 🔧 Development Tools

This directory contains development and build tools for the REGON MCP Server project.

## Available Tools

### 🏗️ Professional Executable Builder

**File**: `make_exe_professional.py`

A sophisticated executable builder that creates production-ready standalone applications for the REGON MCP Server.

#### Key Features
- **Multi-target builds**: HTTP server, STDIO server, and standalone versions
- **Professional UX**: Color-coded output, progress bars, and status indicators
- **Comprehensive error handling**: Detailed error messages with actionable solutions
- **Automated configuration**: API key detection and environment validation
- **Build optimization**: Optimized PyInstaller settings for maximum compatibility
- **Detailed reporting**: File sizes, build times, and success status

#### Quick Usage

```powershell
# Build all executables
python tools\make_exe_professional.py

# Build specific target
python tools\make_exe_professional.py --target http

# Custom output directory
python tools\make_exe_professional.py --output-dir custom_dist\

# Verbose output for debugging
python tools\make_exe_professional.py --verbose
```

#### Requirements
- Python 3.11+
- PyInstaller (automatically installed if missing)
- Virtual environment (recommended)
- REGON API key (for functional executables)

#### Output
Creates standalone `.exe` files in the `production_deployment/regon_mcp/` directory:
- `regon_mcp_server_http.exe` - HTTP REST API server
- `regon_mcp_server_stdio.exe` - MCP protocol server

The output directory also includes configuration files and templates for easy deployment.

#### Documentation
Complete documentation available at: [docs/PROFESSIONAL_BUILD_TOOL.md](../docs/PROFESSIONAL_BUILD_TOOL.md)

## Tool Philosophy

The tools in this directory follow these principles:

1. **Professional Quality**: Production-ready tools with comprehensive error handling
2. **User Experience**: Clear progress indicators, helpful error messages, and intuitive interfaces
3. **Automation**: Minimal manual intervention required for common tasks
4. **Documentation**: Comprehensive documentation with examples and troubleshooting
5. **Maintainability**: Clean, well-structured code that's easy to extend and modify

## Adding New Tools

When adding new development tools to this directory:

1. **Follow naming convention**: Use descriptive names with underscores
2. **Include documentation**: Add comprehensive docstrings and comments
3. **Error handling**: Implement proper error handling with helpful messages
4. **Progress indicators**: For long-running operations, show progress
5. **Update this README**: Document the new tool and its purpose
6. **Create documentation**: Add detailed documentation in the `docs/` folder

## Integration

These tools are designed to integrate with the overall project workflow:

- **Build process**: Executable generation for distribution
- **Development**: Support for common development tasks
- **CI/CD**: Automation-friendly for continuous integration
- **Documentation**: Comprehensive guides in the `docs/` folder

## Support

For issues with development tools:

1. Check the specific tool's documentation in `docs/`
2. Review the tool's help output (`python tool_name.py --help`)
3. Enable verbose mode for debugging information
4. Check the project's main documentation for related guides

---

**Note**: These tools are designed for developers and advanced users. For basic usage of the REGON MCP Server, see the main project documentation in the `docs/` folder.
