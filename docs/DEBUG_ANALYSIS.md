# MCP Server Parameter Mapping Error Investigation

## Issue Summary

The original error message:
```
Error: {'code': -32602, 'message': 'Invalid request parameters', 'data': ''}
```

This error was occurring when the example test scripts attempted to call any MCP tools.

## Root Cause Analysis

### Primary Issues Identified:

1. **Missing MCP Protocol Initialization Step**
   - The MCP protocol requires sending a `notifications/initialized` message after the initial `initialize` request
   - Without this step, the server rejects all subsequent requests with "Received request before initialization was complete"

2. **Incorrect Response Format Handling**
   - The MCP framework returns tool results in a different format than expected
   - Expected: `response["result"][0]["text"]`
   - Actual: `response["result"]["content"][0]["text"]`

3. **Server Reference Issue**
   - Examples were pointing to `regon_mcp_server.py` instead of the fixed version

## Detailed Debugging Process

### Direct RegonAPI Testing
First, I verified that the RegonAPI library itself works correctly:

```python
# Direct API calls work perfectly
api = RegonAPI(bir_version="bir1.1", is_production=False)
api.authenticate(key=api_key)
status = api.get_service_status()  # Returns: ('1', 'Available')
results = api.searchData(nip="7342867148")  # Returns search results
```

### MCP Communication Analysis
Using a debug client, I discovered the communication flow issues:

1. **Initialize Request**: ✅ Working
2. **Tools List Request**: ❌ Failing with -32602 error
3. **Tool Call Request**: ❌ Failing with -32602 error

### Manual JSON-RPC Testing
Created a manual test to send raw JSON-RPC messages and discovered:

- The server was rejecting requests due to incomplete initialization
- After adding the `notifications/initialized` message, tools/list worked correctly
- Tool calls then worked but returned data in a different format

## Solutions Implemented

### 1. Fixed MCP Client Initialization
```python
async def initialize(self):
    # Send initialize request
    response = await self.send_request("initialize", {...})
    
    # CRITICAL: Send initialized notification
    initialized_msg = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    message = json.dumps(initialized_msg) + "\n"
    self.process.stdin.write(message.encode())
    await self.process.stdin.drain()
    
    return response
```

### 2. Updated Response Format Handling
```python
async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
    response = await self.send_request("tools/call", {
        "name": tool_name,
        "arguments": arguments or {}
    })
    
    if "result" in response and response["result"]:
        result = response["result"]
        # Handle the correct MCP response format
        if "content" in result and result["content"]:
            return result["content"][0]["text"]
    # ... error handling
```

### 3. Created Fixed Server Version
- Created `regon_mcp_server_fixed.py` with enhanced logging and error handling
- Updated examples to use the fixed server

## Verification Results

After implementing the fixes, all functionality works correctly:

### Service Status
```
Service Status Code: 1
Status Message: Available
```

### NIP Search
```
--- Result 1 ---
Regon: 492707333
Nip: 7342867148
Nazwa: CD PROJEKT SPÓŁKA AKCYJNA
Wojewodztwo: MAZOWIECKIE
...
```

### Full Reports
All report types (BIR11OsPrawna, BIR11OsPrawnaPkd, etc.) now work correctly.

## Key Takeaways

1. **MCP Protocol Compliance**: The MCP specification requires the `notifications/initialized` message - this is not optional
2. **Response Format**: MCP servers return structured responses with `content` arrays, not direct text
3. **Error Codes**: JSON-RPC error -32602 typically indicates parameter validation issues or protocol violations
4. **Debug Approach**: Direct API testing first, then protocol-level debugging helps isolate issues

## Files Modified

- `regon_mcp_server_fixed.py` - Fixed server with enhanced logging
- `examples/basic_usage_example.py` - Updated client with correct initialization
- `debug_example.py` - Comprehensive debugging tool
- `manual_test.py` - Raw JSON-RPC testing utility

## Recommended Next Steps

1. Update all example files to use the fixed initialization pattern
2. Replace the original server with the fixed version
3. Add proper error handling for common MCP protocol issues
4. Consider adding automated tests to catch similar issues early
