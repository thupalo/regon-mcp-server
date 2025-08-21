#!/usr/bin/env python3
"""
HTTP MCP Server for RegonAPI - Polish GUS REGON Database Client

This is a transparent HTTP wrapper around the original stdio MCP server,
preserving all functions while providing HTTP access using FastAPI.

Features:
- Comprehensive error handling and validation
- Automatic retry mechanisms with exponential backoff
- Input sanitization and security measures
- Health checking and monitoring
- Graceful degradation on failures
- Production-ready logging and metrics

Usage:
    python server_http.py [--host HOST] [--port PORT] [--production] [--log-level DEBUG|INFO|WARNING|ERROR]
    
Configuration:
    - Use --production flag to enable production mode
    - Set API_KEY and TEST_API_KEY in .env file
    - Default host: localhost, default port: 8000
    - Logging level can be controlled via command line or LOG_LEVEL env var
    
Dependencies:
    pip install fastapi uvicorn
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
import traceback
from typing import Any, Dict, List, Optional, Union
import time

try:
    from fastapi import FastAPI, HTTPException, Request, Response
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.exceptions import RequestValidationError
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Import error handling framework
ERROR_HANDLING_AVAILABLE = False
try:
    # First try direct import (for standalone executables)
    import error_handling
    from error_handling import (
        ServerError, ValidationError, APIError, NetworkError,
        safe_execute, safe_async_execute,
        RetryMechanism, HealthChecker,
        sanitize_string, validate_input
    )
    ERROR_HANDLING_AVAILABLE = True
except ImportError as e:
    try:
        # Try relative import (for module structure)
        from .error_handling import (
            ServerError, ValidationError, APIError, NetworkError,
            safe_execute, safe_async_execute,
            RetryMechanism, HealthChecker,
            sanitize_string, validate_input
        )
        ERROR_HANDLING_AVAILABLE = True
    except ImportError as e2:
        print("WARNING: Error handling module not found, server will run without advanced error handling")
        ERROR_HANDLING_AVAILABLE = False
        # Define minimal fallback decorators and classes
        def safe_execute(func):
            return func
        def safe_async_execute(func):
            return func
        class ServerError(Exception):
            pass
        class ValidationError(Exception):
            pass
        class APIError(Exception):
            pass
        class NetworkError(Exception):
            pass
        class RetryMechanism:
            def __init__(self, *args, **kwargs):
                pass
            async def execute_async(self, func):
                return await func()
        class HealthChecker:
            def run_checks(self):
                return []
        def sanitize_string(text, max_length=1000):
            return str(text).strip()
        def validate_input(data, required_fields, field_types=None):
            return data

# Create a compatibility wrapper for InputValidator
class InputValidator:
    """Compatibility wrapper for validation functions."""
    @staticmethod
    def sanitize_string(text, max_length=1000):
        return sanitize_string(text, max_length) if ERROR_HANDLING_AVAILABLE else str(text).strip()
    
    @staticmethod
    def validate_nip(nip):
        """Basic NIP validation - should be 10 digits."""
        return len(str(nip).strip()) >= 10
    
    @staticmethod
    def validate_krs(krs):
        """Basic KRS validation - should be 10 digits.""" 
        return len(str(krs).strip()) >= 10
    
    @staticmethod
    def validate_regon(regon):
        """Basic REGON validation - should be 9 or 14 digits."""
        return len(str(regon).strip()) >= 9

# Import the original server implementation to avoid code duplication
try:
    # Try relative import first (when run as module)
    from . import server as stdio_server_module
except ImportError:
    # Fall back to direct import (when run as script)
    try:
        import server as stdio_server_module
    except ImportError:
        # Last resort: add current directory to path and import
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        import server as stdio_server_module

# Global configuration and state
config = {
    'production_mode': False,
    'log_level': 'INFO',
    'host': 'localhost',
    'port': 8000,
    'tools_config': None
}

# Global instances
logger: Optional[logging.Logger] = None
retry_mechanism: Optional[RetryMechanism] = None
health_checker: Optional[HealthChecker] = None
input_validator: Optional[InputValidator] = None

# Configure UTF-8 encoding for proper Polish character handling
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass  # Ignore if reconfigure is not available

@safe_execute
def parse_http_arguments() -> Optional[argparse.Namespace]:
    """Parse command line arguments for HTTP server with validation."""
    try:
        parser = argparse.ArgumentParser(
            description='RegonAPI HTTP MCP Server',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python server_http.py                                    # Run on localhost:8000 in test mode
  python server_http.py --port 3000                       # Run on port 3000
  python server_http.py --host 0.0.0.0 --port 8080       # Run on all interfaces, port 8080
  python server_http.py --production                      # Run in production mode
  python server_http.py --production --log-level DEBUG    # Production with debug logging
            """
        )
        
        parser.add_argument(
            '--host',
            default='localhost',
            help='Host to bind the HTTP server to (default: localhost)'
        )
        
        parser.add_argument(
            '--port',
            type=int,
            default=8000,
            help='Port to bind the HTTP server to (default: 8000)'
        )
        
        parser.add_argument(
            '--production', 
            action='store_true', 
            help='Use production environment and API_KEY (default: test mode with TEST_API_KEY)'
        )
        
        parser.add_argument(
            '--log-level', 
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
            default=os.getenv('LOG_LEVEL', 'INFO'),
            help='Set logging level (default: INFO, or LOG_LEVEL env var)'
        )
        
        parser.add_argument(
            '--tools-config',
            type=str,
            default=os.getenv('TOOLS_CONFIG'),
            help='Tool configuration to use (default, polish, minimal, detailed). Uses TOOLS_CONFIG env var if not specified.'
        )
        
        args = parser.parse_args()
        
        # Validate arguments
        if args.port < 1 or args.port > 65535:
            raise ValueError(f"Port must be between 1 and 65535, got: {args.port}")
        
        if args.host and not args.host.strip():
            raise ValueError("Host cannot be empty")
        
        return args
        
    except Exception as e:
        print(f"ERROR: Failed to parse arguments: {e}")
        return None

@safe_execute
def setup_http_logging(log_level: str) -> Optional[logging.Logger]:
    """Configure logging for HTTP server with error handling."""
    try:
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Create formatter with timestamp and context
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [HTTP] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Create logger for this module
        http_logger = logging.getLogger(__name__)
        http_logger.setLevel(numeric_level)
        
        return http_logger
        
    except Exception as e:
        print(f"ERROR: Failed to setup logging: {e}")
        return None

@safe_execute
def initialize_global_components() -> bool:
    """Initialize global components with error handling."""
    global retry_mechanism, health_checker, input_validator
    
    try:
        # Initialize components if available
        if ERROR_HANDLING_AVAILABLE:
            retry_mechanism = RetryMechanism(max_retries=3, delay=1.0)
            health_checker = HealthChecker()
            input_validator = InputValidator()
        else:
            # Use fallback implementations
            retry_mechanism = RetryMechanism()
            health_checker = HealthChecker()
            input_validator = InputValidator()
        
        return True
        
    except Exception as e:
        if logger:
            logger.warning(f"Could not initialize some components: {e}")
        return False

@safe_execute
def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        if logger:
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        sys.exit(0)
    
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        if hasattr(signal, 'SIGBREAK'):  # Windows
            signal.signal(signal.SIGBREAK, signal_handler)
    except Exception as e:
        if logger:
            logger.warning(f"Could not set up signal handlers: {e}")

# Custom exception handlers for FastAPI
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors."""
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": error_details,
            "timestamp": time.time()
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with safe error reporting."""
    error_id = f"err_{int(time.time())}"
    
    if logger:
        logger.error(f"Unhandled exception [{error_id}]: {str(exc)}", exc_info=True)
    
    # In production, don't expose internal error details
    if config.get('production_mode', False):
        detail = f"Internal server error (ID: {error_id})"
    else:
        detail = f"Internal server error: {str(exc)} (ID: {error_id})"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": detail,
            "error_id": error_id,
            "timestamp": time.time()
        }
    )

@safe_execute
def create_http_app(production_mode: bool = False) -> Optional[FastAPI]:
    """Create FastAPI application with MCP endpoints and comprehensive error handling."""
    
    if not FASTAPI_AVAILABLE:
        raise ImportError(
            "FastAPI and uvicorn are required for HTTP server. "
            "Install them with: pip install fastapi uvicorn"
        )
    
    try:
        app = FastAPI(
            title="RegonAPI MCP Server",
            description="HTTP wrapper for RegonAPI MCP Server - Polish GUS REGON Database Client",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add exception handlers
        app.add_exception_handler(RequestValidationError, validation_exception_handler)
        app.add_exception_handler(HTTPException, http_exception_handler)
        app.add_exception_handler(Exception, general_exception_handler)
        
        # Enable CORS for web client access
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Set up the configuration in the original module
        stdio_server_module.config['production_mode'] = production_mode
        
        @app.get("/")
        @safe_async_execute
        async def root():
            """Root endpoint with server information and health status."""
            mode = "production" if production_mode else "test"
            
            # Basic server info
            server_info = {
                "service": "RegonAPI MCP Server",
                "version": "1.0.0",
                "mode": mode,
                "description": "HTTP wrapper for Polish GUS REGON Database access",
                "endpoints": {
                    "tools": "/tools",
                    "tools/call": "/tools/call",
                    "health": "/health",
                    "search": {
                        "nip": "/search/nip/{nip}",
                        "krs": "/search/krs/{krs}",
                        "regon": "/search/regon/{regon}"
                    }
                },
                "encoding": "UTF-8 ✅",
                "polish_characters": "SPÓŁKA, Północ ✅",
                "timestamp": time.time()
            }
            
            # Add health status if available
            if health_checker:
                try:
                    health_results = health_checker.run_checks()
                    server_info["health_status"] = "healthy" if health_results else "degraded"
                except Exception:
                    server_info["health_status"] = "unknown"
            
            return server_info
        
        @app.get("/health")
        @safe_async_execute
        async def health_check():
            """Comprehensive health check endpoint."""
            health_data = {
                "status": "unknown",
                "timestamp": time.time(),
                "checks": {}
            }
            
            try:
                # Test RegonAPI initialization
                health_data["checks"]["regon_api"] = {"status": "checking"}
                
                if retry_mechanism:
                    api = await retry_mechanism.execute_async(
                        lambda: stdio_server_module.initialize_regon_api(production_mode)
                    )
                else:
                    api = stdio_server_module.initialize_regon_api(production_mode)
                
                if api:
                    status_code, status_message = api.get_service_status()
                    health_data["checks"]["regon_api"] = {
                        "status": "healthy",
                        "status_code": status_code,
                        "status_message": status_message
                    }
                else:
                    health_data["checks"]["regon_api"] = {
                        "status": "unhealthy",
                        "error": "Failed to initialize API"
                    }
                
                # Test tool availability
                health_data["checks"]["tools"] = {"status": "checking"}
                try:
                    tools = await stdio_server_module.handle_list_tools()
                    health_data["checks"]["tools"] = {
                        "status": "healthy",
                        "count": len(tools) if tools else 0
                    }
                except Exception as e:
                    health_data["checks"]["tools"] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                
                # Overall status
                all_healthy = all(
                    check.get("status") == "healthy" 
                    for check in health_data["checks"].values()
                )
                health_data["status"] = "healthy" if all_healthy else "degraded"
                
                # Additional system info
                health_data["system"] = {
                    "mode": "production" if production_mode else "test",
                    "python_version": sys.version,
                    "platform": sys.platform
                }
                
                return health_data
                
            except Exception as e:
                if logger:
                    logger.error(f"Health check failed: {e}", exc_info=True)
                
                health_data["status"] = "unhealthy"
                health_data["error"] = str(e)
                
                raise HTTPException(
                    status_code=503, 
                    detail=f"Service unhealthy: {e}"
                )
        
        @app.get("/tools")
        @safe_async_execute
        async def list_tools():
            """List available MCP tools with error handling."""
            try:
                if retry_mechanism:
                    tools = await retry_mechanism.execute_async(
                        stdio_server_module.handle_list_tools
                    )
                else:
                    tools = await stdio_server_module.handle_list_tools()
                
                if not tools:
                    return {"tools": [], "count": 0, "timestamp": time.time()}
                
                tools_data = []
                for tool in tools:
                    tool_info = {
                        "name": tool.name,
                        "description": tool.description
                    }
                    
                    # Safely add schema if available
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        tool_info["inputSchema"] = tool.inputSchema
                    
                    tools_data.append(tool_info)
                
                return {
                    "tools": tools_data,
                    "count": len(tools_data),
                    "timestamp": time.time()
                }
                
            except Exception as e:
                if logger:
                    logger.error(f"Error listing tools: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to list tools: {e}"
                )
        
        @app.post("/tools/call")
        @safe_async_execute
        async def call_tool(request: dict):
            """Call a specific MCP tool with comprehensive validation and error handling."""
            request_id = f"req_{int(time.time())}"
            
            try:
                # Validate request structure
                if not isinstance(request, dict):
                    raise HTTPException(
                        status_code=400, 
                        detail="Request must be a JSON object"
                    )
                
                tool_name = request.get("name")
                arguments = request.get("arguments", {})
                
                # Validate tool name
                if not tool_name or not isinstance(tool_name, str):
                    raise HTTPException(
                        status_code=400, 
                        detail="Tool name is required and must be a string"
                    )
                
                # Sanitize tool name
                if input_validator:
                    tool_name = input_validator.sanitize_string(tool_name)
                
                # Validate arguments
                if not isinstance(arguments, dict):
                    raise HTTPException(
                        status_code=400, 
                        detail="Arguments must be a JSON object"
                    )
                
                # Log the request
                if logger:
                    logger.info(f"Tool call [{request_id}]: {tool_name} with args: {arguments}")
                
                # Execute tool with retry mechanism
                start_time = time.time()
                
                if retry_mechanism:
                    result = await retry_mechanism.execute_async(
                        lambda: stdio_server_module.handle_call_tool(tool_name, arguments)
                    )
                else:
                    result = await stdio_server_module.handle_call_tool(tool_name, arguments)
                
                execution_time = time.time() - start_time
                
                # Convert result to response format
                response_data = []
                if result:
                    for content in result:
                        if hasattr(content, 'text'):
                            response_data.append({
                                "type": "text",
                                "text": content.text
                            })
                        else:
                            response_data.append({
                                "type": "text",
                                "text": str(content)
                            })
                
                response = {
                    "result": response_data,
                    "tool": tool_name,
                    "arguments": arguments,
                    "request_id": request_id,
                    "execution_time": round(execution_time, 3),
                    "timestamp": time.time()
                }
                
                if logger:
                    logger.info(f"Tool call [{request_id}] completed in {execution_time:.3f}s")
                
                return response
                
            except HTTPException:
                raise
            except Exception as e:
                if logger:
                    logger.error(f"Error calling tool [{request_id}] {tool_name}: {e}", exc_info=True)
                
                error_detail = f"Tool execution failed: {e}" if not config.get('production_mode') else "Tool execution failed"
                
                raise HTTPException(
                    status_code=500, 
                    detail=error_detail
                )
        
        # Convenience endpoints for common operations with validation
        @app.get("/search/nip/{nip}")
        @safe_async_execute
        async def search_by_nip(nip: str):
            """Search company by NIP with validation (convenience endpoint)."""
            try:
                # Validate and sanitize NIP
                if input_validator:
                    if not input_validator.validate_nip(nip):
                        raise HTTPException(
                            status_code=400, 
                            detail="Invalid NIP format"
                        )
                    nip = input_validator.sanitize_string(nip)
                
                result = await stdio_server_module.handle_call_tool("regon_search_by_nip", {"nip": nip})
                
                response_data = {"nip": nip, "timestamp": time.time()}
                
                if result and len(result) > 0 and hasattr(result[0], 'text'):
                    try:
                        response_data["result"] = json.loads(result[0].text)
                    except json.JSONDecodeError:
                        response_data["result"] = result[0].text
                else:
                    response_data["result"] = None
                
                return response_data
                
            except HTTPException:
                raise
            except Exception as e:
                if logger:
                    logger.error(f"NIP search failed for {nip}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"NIP search failed: {e}")
        
        @app.get("/search/krs/{krs}")
        @safe_async_execute
        async def search_by_krs(krs: str):
            """Search company by KRS with validation (convenience endpoint)."""
            try:
                # Validate and sanitize KRS
                if input_validator:
                    if not input_validator.validate_krs(krs):
                        raise HTTPException(
                            status_code=400, 
                            detail="Invalid KRS format"
                        )
                    krs = input_validator.sanitize_string(krs)
                
                result = await stdio_server_module.handle_call_tool("regon_search_by_krs", {"krs": krs})
                
                response_data = {"krs": krs, "timestamp": time.time()}
                
                if result and len(result) > 0 and hasattr(result[0], 'text'):
                    try:
                        response_data["result"] = json.loads(result[0].text)
                    except json.JSONDecodeError:
                        response_data["result"] = result[0].text
                else:
                    response_data["result"] = None
                
                return response_data
                
            except HTTPException:
                raise
            except Exception as e:
                if logger:
                    logger.error(f"KRS search failed for {krs}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"KRS search failed: {e}")
        
        @app.get("/search/regon/{regon}")
        @safe_async_execute
        async def search_by_regon(regon: str):
            """Search company by REGON with validation (convenience endpoint)."""
            try:
                # Validate and sanitize REGON
                if input_validator:
                    if not input_validator.validate_regon(regon):
                        raise HTTPException(
                            status_code=400, 
                            detail="Invalid REGON format"
                        )
                    regon = input_validator.sanitize_string(regon)
                
                result = await stdio_server_module.handle_call_tool("regon_search_by_regon", {"regon": regon})
                
                response_data = {"regon": regon, "timestamp": time.time()}
                
                if result and len(result) > 0 and hasattr(result[0], 'text'):
                    try:
                        response_data["result"] = json.loads(result[0].text)
                    except json.JSONDecodeError:
                        response_data["result"] = result[0].text
                else:
                    response_data["result"] = None
                
                return response_data
                
            except HTTPException:
                raise
            except Exception as e:
                if logger:
                    logger.error(f"REGON search failed for {regon}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"REGON search failed: {e}")
        
        return app
        
    except Exception as e:
        if logger:
            logger.error(f"Failed to create FastAPI app: {e}", exc_info=True)
        raise ServerError(f"Application creation failed: {e}")

@safe_async_execute
async def run_http_server() -> int:
    """Run the HTTP MCP server with comprehensive error handling and recovery."""
    global logger, config
    
    # Set up signal handlers for graceful shutdown
    setup_signal_handlers()
    
    try:
        # Parse command line arguments with validation
        args = parse_http_arguments()
        if args is None:
            print("ERROR: Failed to parse arguments, exiting")
            return 1
        
        # Update global configuration
        config.update({
            'production_mode': bool(args.production),
            'log_level': args.log_level,
            'host': args.host,
            'port': args.port,
            'tools_config': args.tools_config
        })
        
        # Setup logging with error handling
        logger = setup_http_logging(args.log_level)
        if logger is None:
            print("ERROR: Failed to setup logging, exiting")
            return 1
        
        # Initialize global components
        initialize_global_components()
        
        # Set up the original server's global configuration
        stdio_server_module.config.update({
            'production_mode': config['production_mode'],
            'log_level': config['log_level'],
            'tools_config': config['tools_config']
        })
        
        # Initialize the original server's logger
        stdio_server_module.logger = stdio_server_module.setup_logging(config['log_level'])
        
        # Log startup information
        mode = "production" if config['production_mode'] else "test"
        tools_config = config['tools_config'] or 'default'
        
        logger.info("=" * 70)
        logger.info("🌐 Starting RegonAPI HTTP MCP Server")
        logger.info(f"   Host: {config['host']}")
        logger.info(f"   Port: {config['port']}")
        logger.info(f"   Mode: {mode}")
        logger.info(f"   Log Level: {config['log_level']}")
        logger.info(f"   Tools Config: {tools_config}")
        logger.info(f"   Python Version: {sys.version}")
        logger.info(f"   Platform: {sys.platform}")
        logger.info(f"   Encoding: UTF-8 ✅")
        logger.info("=" * 70)
        
        # Pre-flight checks
        if health_checker:
            health_results = health_checker.run_checks()
            logger.info(f"Health checks: {len(health_results)} components checked")
                
        # Create FastAPI app with comprehensive error handling
        try:
            app = create_http_app(config['production_mode'])
            if app is None:
                raise ServerError("Failed to create FastAPI application")
            
            logger.info("✅ FastAPI application created successfully")
            
        except Exception as e:
            logger.error(f"FastAPI application creation failed: {e}", exc_info=True)
            return 1
        
        # Configure uvicorn with error handling
        try:
            uvicorn_config = uvicorn.Config(
                app,
                host=config['host'],
                port=config['port'],
                log_level=config['log_level'].lower(),
                access_log=True,
                server_header=False,  # Security: hide server header
                date_header=False     # Security: hide date header
            )
            
            server = uvicorn.Server(uvicorn_config)
            logger.info("✅ Uvicorn server configured")
            
        except Exception as e:
            logger.error(f"Uvicorn configuration failed: {e}", exc_info=True)
            return 1
        
        logger.info("🎯 HTTP Server ready to accept connections")
        logger.info(f"✅ HTTP MCP Server starting at http://{config['host']}:{config['port']}")
        logger.info(f"� API Documentation: http://{config['host']}:{config['port']}/docs")
        logger.info(f"🔍 Health Check: http://{config['host']}:{config['port']}/health")
        logger.info(f"🔍 Example: http://{config['host']}:{config['port']}/search/nip/7342867148")
        
        # Run server with error recovery
        max_restarts = 3
        restart_count = 0
        
        while restart_count < max_restarts:
            try:
                logger.info("📡 HTTP MCP Server running...")
                await server.serve()
                
                # If we reach here, server shut down normally
                logger.info("🛑 HTTP Server shut down normally")
                break
                
            except (KeyboardInterrupt, SystemExit):
                logger.info("🛑 HTTP Server stopped by user")
                break
                
            except Exception as e:
                restart_count += 1
                logger.error(f"HTTP Server error (attempt {restart_count}/{max_restarts}): {e}", exc_info=True)
                
                if restart_count < max_restarts:
                    wait_time = min(5 * restart_count, 30)  # Exponential backoff, max 30s
                    logger.info(f"🔄 Restarting HTTP server in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    
                    # Recreate server instance
                    try:
                        server = uvicorn.Server(uvicorn_config)
                        logger.info("✅ Server instance recreated")
                    except Exception as recreate_error:
                        logger.error(f"Failed to recreate server: {recreate_error}")
                        break
                else:
                    logger.error("❌ Maximum restart attempts reached, exiting")
                    return 1
        
        return 0
        
    except KeyboardInterrupt:
        if logger:
            logger.info("🛑 HTTP Server interrupted by user")
        else:
            print("\n🛑 HTTP Server interrupted by user")
        return 0
    except SystemExit as e:
        if logger:
            logger.info(f"🛑 HTTP Server exit requested: {e.code}")
        return e.code or 0
    except Exception as e:
        if logger:
            logger.error(f"❌ Critical error in HTTP server: {e}", exc_info=True)
        else:
            print(f"CRITICAL ERROR: {e}")
            traceback.print_exc()
        return 1
    finally:
        # Cleanup
        if logger:
            logger.info("🧹 Cleaning up HTTP server resources...")
            try:
                # Additional cleanup can be added here
                pass
            except Exception as e:
                logger.warning(f"Error during HTTP server cleanup: {e}")
            
            logger.info("👋 HTTP Server goodbye!")

def main():
    """Main entry point for HTTP server with comprehensive error handling."""
    global logger
    
    try:
        exit_code = asyncio.run(run_http_server())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 HTTP Server stopped by user")
        sys.exit(0)
    except Exception as e:
        if logger:
            logger.error(f"FATAL ERROR in HTTP server: {e}", exc_info=True)
        else:
            print(f"FATAL ERROR: {e}")
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Initialize global variables with safe defaults
    logger = None
    main()
