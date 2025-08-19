# RegonAPI MCP Server - Examples

This folder contains comprehensive examples demonstrating how to use the RegonAPI MCP Server. These examples are based on the original RegonAPI examples but adapted for the MCP (Model Context Protocol) interface.

## 📁 Example Files

### 1. `basic_usage_example.py`
**Based on**: `RegonAPI/examples/bir11_examples.py`

Demonstrates basic usage patterns equivalent to the original RegonAPI examples:
- Service status checking
- Searching by NIP, KRS, and REGON numbers
- Fetching basic reports
- Error handling

**Run with**: `python basic_usage_example.py`

### 2. `bulk_search_example.py`
Demonstrates bulk search capabilities for improved performance:
- Multiple NIP searches
- Multiple REGON searches (9 and 14 digit)
- Multiple KRS searches
- Performance comparison with individual searches

**Run with**: `python bulk_search_example.py`

### 3. `reports_example.py`
Comprehensive demonstration of report generation:
- Legal entity reports
- Natural person reports (reference)
- Local unit reports
- Partnership reports
- Report validation and error handling

**Run with**: `python reports_example.py`

### 4. `monitoring_example.py`
Error handling and service monitoring:
- Service health checks
- Error code interpretation
- Debugging techniques
- Production monitoring best practices

**Run with**: `python monitoring_example.py`

### 5. `advanced_example.py`
Advanced usage patterns for production applications:
- Complex business workflows
- Entity cross-referencing
- Performance monitoring
- Business intelligence generation
- Data analysis patterns

**Run with**: `python advanced_example.py`

## 🚀 Quick Start

### Prerequisites
1. Make sure the MCP server is properly configured:
   ```bash
   cd ..
   # Check that .env file exists with API key
   python test_server.py
   ```

2. All examples run from the examples directory and reference the parent directory for the server script.

### Running Examples

#### Basic Example (Recommended to start)
```bash
cd examples
python basic_usage_example.py
```

#### All Examples
```bash
# Run all examples in sequence
python run_all_examples.py
```

#### Individual Examples
```bash
python bulk_search_example.py
python reports_example.py
python monitoring_example.py
python advanced_example.py
```

## 📊 Example Comparison with Original RegonAPI

| Original RegonAPI Code | MCP Server Equivalent |
|------------------------|----------------------|
| `api.searchData(nip="123")` | `call_tool("regon_search_by_nip", {"nip": "123"})` |
| `api.searchData(regon="456")` | `call_tool("regon_search_by_regon", {"regon": "456"})` |
| `api.dataDownloadFullReport(regon, report)` | `call_tool("regon_get_full_report", {"regon": regon, "report_name": report})` |
| `api.get_service_status()` | `call_tool("regon_get_service_status")` |

## 🔧 Customizing Examples

### Using Your Own Data
Replace the sample company identifiers in the examples:

```python
# Change these in any example
CD_PROJEKT_NIP = "7342867148"     # Your company NIP
CD_PROJEKT_KRS = "0000006865"     # Your company KRS  
CD_PROJEKT_REGON9 = "492707333"   # Your company REGON
```

### Adding New Report Types
Add report names to the report lists:

```python
# In reports_example.py
custom_reports = [
    ("BIR11CustomReport", "Your custom report description")
]
```

### Error Handling Patterns
All examples include comprehensive error handling:

```python
try:
    result = await client.call_tool("tool_name", arguments)
    # Process successful result
except Exception as e:
    # Handle errors gracefully
    print(f"Error: {e}")
```

## 📋 Example Output

Each example provides detailed output showing:
- ✅ Successful operations
- ❌ Error conditions
- 📊 Data analysis results
- 💡 Best practice recommendations
- ⏱️ Performance metrics

## 🔍 Understanding the Output

### Search Results
```
--- Result 1 ---
Nazwa: CD PROJEKT SPÓŁKA AKCYJNA
Nip: 7342867148
Regon: 492707333
Krs: 0000006865
...
```

### Report Data
```
--- Record 1 ---
praw_nazwa: CD PROJEKT SPÓŁKA AKCYJNA
praw_nip: 7342867148
praw_regon: 492707333
...
```

### Error Messages
```
Error: No results found for NIP: 1234567890
Authentication error: Authentication failed with key: "invalid_key"
```

## 🎯 Learning Path

1. **Start with**: `basic_usage_example.py` - Learn core concepts
2. **Next**: `bulk_search_example.py` - Understand performance optimization
3. **Then**: `reports_example.py` - Explore different data types
4. **Follow with**: `monitoring_example.py` - Learn error handling
5. **Finish with**: `advanced_example.py` - See production patterns

## 🔧 Troubleshooting

### Common Issues

#### Server Not Starting
```bash
# Check if server script exists
ls -la ../regon_mcp_server.py

# Check Python environment
python --version
pip list | grep mcp
```

#### Authentication Errors
```bash
# Check API key in .env file
cat ../.env

# Test authentication
cd ..
python test_server.py
```

#### Import Errors
```bash
# Install dependencies
cd ..
pip install -r requirements.txt
```

## 💡 Tips for Production Use

1. **Error Handling**: Always implement proper error handling
2. **Rate Limiting**: Respect API rate limits
3. **Caching**: Cache results for frequently accessed data
4. **Monitoring**: Monitor service status regularly
5. **Logging**: Implement comprehensive logging
6. **Async Operations**: Use async patterns for better performance

## 📚 Additional Resources

- [RegonAPI Documentation](https://github.com/rolzwy7/RegonAPI)
- [GUS REGON API Official Docs](https://api.stat.gov.pl/Home/RegonApi)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Main Project README](../README.md)

## 🤝 Contributing

To add new examples:
1. Follow the existing pattern and naming convention
2. Include comprehensive documentation
3. Add error handling and progress indicators
4. Update this README with the new example

## ⚖️ License

These examples are provided as educational material. Please refer to the RegonAPI license for usage terms.
