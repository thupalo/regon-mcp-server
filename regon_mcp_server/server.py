#!/usr/bin/env python3
"""
MCP Server for RegonAPI - Polish GUS REGON Database Client

This server provides tools to interact with the Polish REGON database
through the RegonAPI Python module.

Usage:
    python server.py [--production] [--log-level DEBUG|INFO|WARNING|ERROR]
    
Configuration:
    - Use --production flag to enable production mode
    - Set API_KEY and TEST_API_KEY in .env file
    - Logging level can be controlled via command line or LOG_LEVEL env var
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import signal
import traceback
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from RegonAPI import RegonAPI
from RegonAPI.exceptions import (
    ApiAuthenticationError, 
    ApiUnknownReportNameError, 
    ApiInvalidDateFormat,
    ApiError
)

# Try relative import first, fall back to direct import
try:
    from .tool_config import get_config_loader
    from .error_handling import (
        safe_execute, safe_async_execute, ServerError, ConfigurationError,
        APIError, ValidationError, NetworkError, create_error_response,
        setup_error_handling, retry_on_failure, retry_on_network_failure,
        health_checker, validate_input, sanitize_string, format_error_for_user
    )
except ImportError:
    from tool_config import get_config_loader
    from error_handling import (
        safe_execute, safe_async_execute, ServerError, ConfigurationError,
        APIError, ValidationError, NetworkError, create_error_response,
        setup_error_handling, retry_on_failure, retry_on_network_failure,
        health_checker, validate_input, sanitize_string, format_error_for_user
    )

# Configure UTF-8 encoding for proper Polish character handling
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception as e:
        # Fallback if reconfigure fails
        logging.warning(f"Could not reconfigure console encoding: {e}")

# Load environment variables with error handling
try:
    load_dotenv()
except Exception as e:
    logging.warning(f"Could not load .env file: {e}")

# Set up comprehensive error handling
setup_error_handling()

# Global configuration
config = {
    'production_mode': False,
    'log_level': 'INFO',
    'tools_config': None
}

# Global variables
regon_api = None
tool_config_loader = None
server_info = None

# Available report names for BIR 1.1
AVAILABLE_REPORTS = [
    "BIR11OsFizycznaDaneOgolne",
    "BIR11OsFizycznaDzialalnoscCeidg", 
    "BIR11OsFizycznaDzialalnoscRolnicza",
    "BIR11OsFizycznaDzialalnoscPozostala",
    "BIR11OsFizycznaListaJednLokalnych",
    "BIR11JednLokalnaOsFizycznej",
    "BIR11OsPrawna",
    "BIR11OsPrawnaDzialalnoscSkreslona",
    "BIR11OsPrawnaPkd",
    "BIR11OsPrawnaListaJednLokalnych",
    "BIR11JednLokalnaOsPrawnej",
    "BIR11TypPodmiotu"
]

@safe_execute
def parse_arguments():
    """Parse command line arguments with error handling."""
    try:
        parser = argparse.ArgumentParser(
            description='RegonAPI MCP Server',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python server.py                     # Run in test mode with INFO logging
  python server.py --production        # Run in production mode
  python server.py --log-level DEBUG   # Run with debug logging
  python server.py --production --log-level WARNING  # Production with warning logs
  python server.py --tools-config polish  # Use Polish tool descriptions
  
Environment Variables:
  TOOLS_CONFIG   - Tool configuration to use (default, polish, minimal, detailed)
  LOG_LEVEL      - Logging level (DEBUG, INFO, WARNING, ERROR)
  API_KEY        - Production API key
  TEST_API_KEY   - Test API key
            """
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
        
        return parser.parse_args()
    
    except SystemExit:
        # Handle help/version exits gracefully
        raise
    except Exception as e:
        # Return safe defaults if argument parsing fails
        logging.error(f"Argument parsing failed: {e}, using defaults")
        class DefaultArgs:
            production = False
            log_level = 'INFO'
            tools_config = None
        return DefaultArgs()

@safe_execute
def setup_logging(log_level: str):
    """Configure logging based on the specified level with error handling."""
    try:
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Create formatter with more detailed information
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(numeric_level)
        root_logger.addHandler(console_handler)
        
        # Create file handler for errors
        try:
            error_handler = logging.FileHandler('regon_mcp_server_errors.log', encoding='utf-8')
            error_handler.setFormatter(formatter)
            error_handler.setLevel(logging.ERROR)
            root_logger.addHandler(error_handler)
        except Exception as e:
            logging.warning(f"Could not create error log file: {e}")
        
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configured at level: {log_level}")
        
        return logger
        
    except Exception as e:
        # Fallback to basic logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        logger.error(f"Logging setup failed: {e}, using basic configuration")
        return logger

@safe_execute
def get_api_key(production_mode: bool) -> str:
    """Get appropriate API key based on mode with comprehensive error handling."""
    try:
        if production_mode:
            # Production mode: use API_KEY, fallback to TEST_API_KEY with warning
            api_key = os.getenv("API_KEY")
            if not api_key:
                test_key = os.getenv("TEST_API_KEY")
                if test_key:
                    logger.warning("Production mode requested but no API_KEY found. Using TEST_API_KEY.")
                    return sanitize_string(test_key, 100)
                else:
                    raise ConfigurationError(
                        "Production mode requires API_KEY in environment variables. "
                        "Please set API_KEY in your .env file."
                    )
            return sanitize_string(api_key, 100)
        else:
            # Test mode: use TEST_API_KEY, fallback to API_KEY, then default test key
            api_key = os.getenv("TEST_API_KEY")
            if not api_key:
                api_key = os.getenv("API_KEY")
                if api_key:
                    logger.info("TEST_API_KEY not found. Using API_KEY for testing.")
                else:
                    logger.warning("No API keys found in environment. Using default test key.")
                    return "abcde12345abcde12345"  # Default test key provided by GUS
            return sanitize_string(api_key, 100)
    
    except Exception as e:
        if production_mode:
            raise ConfigurationError(f"Failed to get production API key: {str(e)}")
        else:
            logger.warning(f"Failed to get API key: {e}, using default test key")
            return "abcde12345abcde12345"

@retry_on_network_failure.async_retry
async def initialize_regon_api_async(production_mode: bool) -> RegonAPI:
    """Initialize RegonAPI with async retry mechanism."""
    return initialize_regon_api(production_mode)

@safe_execute
def initialize_regon_api(production_mode: bool) -> RegonAPI:
    """Initialize and authenticate RegonAPI instance with comprehensive error handling."""
    global regon_api
    
    if regon_api is None:
        try:
            api_key = get_api_key(production_mode)
            
            logger.info(f"Initializing RegonAPI in {'production' if production_mode else 'test'} mode")
            
            # Initialize RegonAPI with appropriate environment
            regon_api = RegonAPI(
                bir_version="bir1.1",
                is_production=production_mode,
                timeout=30,
                operation_timeout=30
            )
            
            # Authenticate with retry mechanism
            @retry_on_network_failure
            def authenticate():
                regon_api.authenticate(key=api_key)
                return regon_api.get_service_status()
            
            status_code, status_message = authenticate()
            
            # Validate authentication
            if status_code != 1:
                raise APIError(f"RegonAPI authentication failed: {status_message}")
            
            mode_str = "production" if production_mode else "test"
            logger.info(f"RegonAPI initialized successfully in {mode_str} mode")
            logger.info(f"Service status: {status_message}")
            
            # Register health check
            health_checker.register_check("regon_api", lambda: regon_api.get_service_status())
            
        except (ApiAuthenticationError, ApiError) as e:
            error_msg = f"RegonAPI authentication failed: {str(e)}"
            logger.error(error_msg)
            raise APIError(error_msg, {"production_mode": production_mode})
        
        except Exception as e:
            error_msg = f"Failed to initialize RegonAPI: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise APIError(error_msg, {"production_mode": production_mode})
    
    return regon_api

@safe_execute
def initialize_tool_config():
    """Initialize tool configuration loader with comprehensive error handling."""
    global tool_config_loader, server_info
    
    # Get logger instance
    current_logger = logging.getLogger(__name__)
    
    try:
        current_logger.info("Initializing tool configuration...")
        
        tool_config_loader = get_config_loader()
        config_name = config.get('tools_config')
        
        # Validate config name if provided
        if config_name:
            config_name = sanitize_string(config_name, 50)
            available_configs = tool_config_loader.list_available_configs()
            if config_name not in available_configs:
                current_logger.warning(f"Invalid config '{config_name}', available: {available_configs}")
                config_name = None
        
        config_data = tool_config_loader.load_config(config_name)
        server_info = tool_config_loader.get_server_info()
        
        # Validate loaded configuration
        if not config_data or not isinstance(config_data, dict):
            raise ConfigurationError("Invalid configuration data format")
        
        tools = tool_config_loader.get_all_tools()
        if not tools or not isinstance(tools, list):
            raise ConfigurationError("Invalid tools configuration")
        
        # Validate each tool has required fields
        for i, tool in enumerate(tools):
            if not isinstance(tool, dict):
                raise ConfigurationError(f"Tool {i} is not a valid dictionary")
            
            required_fields = ['name', 'description', 'inputSchema']
            for field in required_fields:
                if field not in tool:
                    raise ConfigurationError(f"Tool {i} missing required field: {field}")
        
        current_logger.info(f"Loaded tool configuration: {server_info.get('name', 'Unknown')}")
        current_logger.info(f"Language: {server_info.get('language', 'unknown')}")
        current_logger.info(f"Tools available: {len(tools)}")
        
        # Register configuration health check
        health_checker.register_check("tool_config", lambda: {
            "config_name": config_name,
            "tool_count": len(tools),
            "language": server_info.get('language', 'unknown')
        })
        
    except Exception as e:
        current_logger.error(f"Failed to load tool configuration: {e}")
        current_logger.warning("Falling back to hardcoded tool definitions")
        
        tool_config_loader = None
        server_info = {
            'name': 'RegonAPI MCP Server (Fallback)',
            'version': '1.0.0',
            'description': 'Polish REGON database access (using fallback configuration)',
            'language': 'en'
        }
        
        # Register fallback health check
        health_checker.register_check("tool_config", lambda: {
            "status": "fallback",
            "error": str(e)
        })

# Initialize the MCP server
def create_server():
    """Create and configure the MCP server."""
    initialize_tool_config()
    
    server_name = server_info.get('name', 'regon-api') if server_info else 'regon-api'
    server_instance = Server(server_name)
    
    # Register handlers
    server_instance.list_tools()(handle_list_tools)
    server_instance.call_tool()(handle_call_tool)
    
    return server_instance

# Global server instance - will be created when needed
server = None

def get_server():
    """Get or create the server instance."""
    global server
    if server is None:
        server = create_server()
    return server

@safe_async_execute
async def handle_list_tools() -> List[Tool]:
    """List available tools based on configuration with comprehensive error handling."""
    try:
        if tool_config_loader:
            try:
                tools = []
                tool_configs = tool_config_loader.get_all_tools()
                
                if not tool_configs:
                    raise ConfigurationError("No tools found in configuration")
                
                for tool_config in tool_configs:
                    try:
                        # Validate tool configuration
                        if not isinstance(tool_config, dict):
                            logger.warning(f"Skipping invalid tool config: {tool_config}")
                            continue
                        
                        name = tool_config.get('name')
                        description = tool_config.get('description')
                        input_schema = tool_config.get('inputSchema')
                        
                        if not all([name, description, input_schema]):
                            logger.warning(f"Skipping incomplete tool config: {name}")
                            continue
                        
                        # Sanitize inputs
                        name = sanitize_string(name, 100)
                        description = sanitize_string(description, 1000)
                        
                        tool = Tool(
                            name=name,
                            description=description,
                            inputSchema=input_schema
                        )
                        tools.append(tool)
                        
                    except Exception as e:
                        logger.warning(f"Error processing tool config {tool_config.get('name', 'unknown')}: {e}")
                        continue
                
                if not tools:
                    raise ConfigurationError("No valid tools could be loaded from configuration")
                
                logger.info(f"Successfully loaded {len(tools)} tools from configuration")
                return tools
                
            except Exception as e:
                logger.error(f"Error loading tools from configuration: {e}")
                # Fall through to hardcoded tools
        
        # Fallback to hardcoded tools if configuration fails
        logger.warning("Using fallback hardcoded tool definitions")
        return get_fallback_tools()
        
    except Exception as e:
        logger.error(f"Critical error in handle_list_tools: {e}")
        return get_fallback_tools()

@safe_execute
def get_fallback_tools() -> List[Tool]:
    """Get hardcoded fallback tools in case configuration fails."""
    try:
        return [
            Tool(
                name="regon_search_by_nip",
                description="Search for Polish companies by NIP (tax number)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "nip": {
                            "type": "string",
                            "description": "10-digit NIP number (e.g., '7342867148')"
                        }
                    },
                    "required": ["nip"]
                }
            ),
            Tool(
                name="regon_search_by_regon",
                description="Search for Polish companies by REGON number",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "regon": {
                            "type": "string",
                            "description": "9-digit (main unit) or 14-digit (local unit) REGON number"
                        }
                    },
                    "required": ["regon"]
                }
            ),
            Tool(
                name="regon_search_by_krs",
                description="Search for Polish companies by KRS (court register) number",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "krs": {
                            "type": "string",
                            "description": "10-digit KRS number with leading zeros (e.g., '0000006865')"
                        }
                    },
                    "required": ["krs"]
                }
            ),
            Tool(
                name="regon_get_service_status",
                description="Check the status of the REGON service",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            )
        ]
    except Exception as e:
        logger.error(f"Error creating fallback tools: {e}")
        return []

@safe_async_execute
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls with comprehensive error handling and validation."""
    
    # Input validation and sanitization
    try:
        if not name or not isinstance(name, str):
            return create_error_response(ValidationError("Tool name must be a non-empty string"))
        
        name = sanitize_string(name, 100)
        
        if arguments is None or not isinstance(arguments, dict):
            return create_error_response(ValidationError("Arguments must be a dictionary"))
        
        # Sanitize all string arguments
        sanitized_args = {}
        for key, value in arguments.items():
            if isinstance(value, str):
                sanitized_args[key] = sanitize_string(value, 500)
            elif isinstance(value, list):
                sanitized_args[key] = [sanitize_string(str(item), 500) if isinstance(item, str) else item for item in value]
            else:
                sanitized_args[key] = value
        
        logger.info(f"Processing tool call: {name} with arguments: {list(sanitized_args.keys())}")
        
        # Initialize API with retry mechanism
        try:
            api = await initialize_regon_api_async(config['production_mode'])
        except Exception as e:
            return create_error_response(APIError(f"Failed to initialize RegonAPI: {str(e)}"))
        
        # Route to appropriate handler with validation
        result = await route_tool_call(name, sanitized_args, api)
        return result
        
    except Exception as e:
        logger.error(f"Critical error in handle_call_tool: {e}", exc_info=True)
        return create_error_response(e, f"Tool: {name}")

async def route_tool_call(name: str, arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Route tool calls to appropriate handlers with error handling."""
    
    try:
        if name == "regon_search_by_nip":
            return await handle_search_by_nip(arguments, api)
        elif name == "regon_search_by_regon":
            return await handle_search_by_regon(arguments, api)
        elif name == "regon_search_by_krs":
            return await handle_search_by_krs(arguments, api)
        elif name == "regon_search_multiple_nips":
            return await handle_search_multiple_nips(arguments, api)
        elif name == "regon_search_multiple_regons9":
            return await handle_search_multiple_regons9(arguments, api)
        elif name == "regon_search_multiple_krs":
            return await handle_search_multiple_krs(arguments, api)
        elif name == "regon_get_full_report":
            return await handle_get_full_report(arguments, api)
        elif name == "regon_get_service_status":
            return await handle_get_service_status(arguments, api)
        elif name == "regon_get_data_status":
            return await handle_get_data_status(arguments, api)
        elif name == "regon_get_last_error_code":
            return await handle_get_last_error_code(arguments, api)
        elif name == "regon_get_last_error_message":
            return await handle_get_last_error_message(arguments, api)
        elif name == "regon_get_session_status":
            return await handle_get_session_status(arguments, api)
        elif name == "regon_get_available_operations":
            return await handle_get_available_operations(arguments, api)
        else:
            return create_error_response(ValidationError(f"Unknown tool: {name}"))
            
    except Exception as e:
        logger.error(f"Error routing tool call {name}: {e}", exc_info=True)
        return create_error_response(e, f"Tool: {name}")

# Individual tool handlers with comprehensive error handling

@retry_on_network_failure.async_retry
async def handle_search_by_nip(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle NIP search with validation and error handling."""
    try:
        validate_input(arguments, ["nip"], {"nip": str})
        nip = arguments["nip"].strip()
        
        # Validate NIP format
        if not nip.isdigit() or len(nip) != 10:
            return create_error_response(ValidationError("NIP must be exactly 10 digits"))
        
        logger.debug(f"Searching by NIP: {nip}")
        result = api.searchData(nip=nip)
        
        if not result:
            return [TextContent(type="text", text="ℹ️ No data found for the specified NIP number.")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        return create_error_response(e, "NIP search")

@retry_on_network_failure.async_retry
async def handle_search_by_regon(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle REGON search with validation and error handling."""
    try:
        validate_input(arguments, ["regon"], {"regon": str})
        regon = arguments["regon"].strip()
        
        # Validate REGON format
        if not regon.isdigit() or len(regon) not in [9, 14]:
            return create_error_response(ValidationError("REGON must be 9 or 14 digits"))
        
        logger.debug(f"Searching by REGON: {regon}")
        result = api.searchData(regon=regon)
        
        if not result:
            return [TextContent(type="text", text="ℹ️ No data found for the specified REGON number.")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        return create_error_response(e, "REGON search")

@retry_on_network_failure.async_retry
async def handle_search_by_krs(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle KRS search with validation and error handling."""
    try:
        validate_input(arguments, ["krs"], {"krs": str})
        krs = arguments["krs"].strip()
        
        # Validate KRS format
        if not krs.isdigit() or len(krs) != 10:
            return create_error_response(ValidationError("KRS must be exactly 10 digits"))
        
        logger.debug(f"Searching by KRS: {krs}")
        result = api.searchData(krs=krs)
        
        if not result:
            return [TextContent(type="text", text="ℹ️ No data found for the specified KRS number.")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        return create_error_response(e, "KRS search")

@retry_on_network_failure.async_retry
async def handle_search_multiple_nips(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle multiple NIP search with validation and error handling."""
    try:
        validate_input(arguments, ["nips"], {"nips": list})
        nips = arguments["nips"]
        
        if len(nips) > 20:  # Limit to prevent abuse
            return create_error_response(ValidationError("Maximum 20 NIPs allowed per request"))
        
        # Validate each NIP
        valid_nips = []
        for nip in nips:
            nip = str(nip).strip()
            if nip.isdigit() and len(nip) == 10:
                valid_nips.append(nip)
            else:
                logger.warning(f"Skipping invalid NIP: {nip}")
        
        if not valid_nips:
            return create_error_response(ValidationError("No valid NIPs provided"))
        
        logger.debug(f"Searching multiple NIPs: {valid_nips}")
        result = api.searchData(nips=valid_nips)
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        return create_error_response(e, "Multiple NIP search")

@retry_on_network_failure.async_retry
async def handle_search_multiple_regons9(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle multiple REGON9 search with validation and error handling."""
    try:
        validate_input(arguments, ["regons"], {"regons": list})
        regons = arguments["regons"]
        
        if len(regons) > 20:  # Limit to prevent abuse
            return create_error_response(ValidationError("Maximum 20 REGONs allowed per request"))
        
        # Validate each REGON
        valid_regons = []
        for regon in regons:
            regon = str(regon).strip()
            if regon.isdigit() and len(regon) == 9:
                valid_regons.append(regon)
            else:
                logger.warning(f"Skipping invalid REGON: {regon}")
        
        if not valid_regons:
            return create_error_response(ValidationError("No valid 9-digit REGONs provided"))
        
        logger.debug(f"Searching multiple REGONs: {valid_regons}")
        result = api.searchData(regons9=valid_regons)
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        return create_error_response(e, "Multiple REGON search")

@retry_on_network_failure.async_retry
async def handle_search_multiple_krs(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle multiple KRS search with validation and error handling."""
    try:
        validate_input(arguments, ["krs_numbers"], {"krs_numbers": list})
        krs_numbers = arguments["krs_numbers"]
        
        if len(krs_numbers) > 20:  # Limit to prevent abuse
            return create_error_response(ValidationError("Maximum 20 KRS numbers allowed per request"))
        
        # Validate each KRS
        valid_krs = []
        for krs in krs_numbers:
            krs = str(krs).strip()
            if krs.isdigit() and len(krs) == 10:
                valid_krs.append(krs)
            else:
                logger.warning(f"Skipping invalid KRS: {krs}")
        
        if not valid_krs:
            return create_error_response(ValidationError("No valid KRS numbers provided"))
        
        logger.debug(f"Searching multiple KRS: {valid_krs}")
        result = api.searchData(krss=valid_krs)
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        return create_error_response(e, "Multiple KRS search")

@retry_on_network_failure.async_retry
async def handle_get_full_report(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle full report request with validation and error handling."""
    try:
        validate_input(arguments, ["regon", "report_name"], {"regon": str, "report_name": str})
        regon = arguments["regon"].strip()
        report_name = arguments["report_name"].strip()
        
        # Validate REGON format
        if not regon.isdigit() or len(regon) not in [9, 14]:
            return create_error_response(ValidationError("REGON must be 9 or 14 digits"))
        
        # Validate report name
        if report_name not in AVAILABLE_REPORTS:
            return create_error_response(ValidationError(f"Invalid report name. Available: {', '.join(AVAILABLE_REPORTS)}"))
        
        logger.debug(f"Getting full report for REGON {regon}, report: {report_name}")
        result = api.dataDownloadFullReport(regon, report_name)
        
        if not result:
            return [TextContent(type="text", text="ℹ️ No report data available for the specified parameters.")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        return create_error_response(e, "Full report request")

@retry_on_network_failure.async_retry
async def handle_get_service_status(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle service status request with error handling."""
    try:
        logger.debug("Getting service status")
        status_code, status_message = api.get_service_status()
        
        # Format status with emoji indicators
        status_emoji = "🟢" if status_code == 1 else "🔴"
        return [TextContent(type="text", text=f"{status_emoji} Service Status Code: {status_code}\nStatus Message: {status_message}")]
        
    except Exception as e:
        return create_error_response(e, "Service status request")

@retry_on_network_failure.async_retry
async def handle_get_data_status(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle data status request with error handling."""
    try:
        logger.debug("Getting data status")
        result = api.get_data_status()
        
        if not result:
            return [TextContent(type="text", text="ℹ️ No data status information available.")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        return create_error_response(e, "Data status request")

@retry_on_network_failure.async_retry
async def handle_get_last_error_code(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle last error code request with error handling."""
    try:
        logger.debug("Getting last error code")
        code, message = api.get_last_code()
        
        error_emoji = "🔴" if code != 0 else "🟢"
        return [TextContent(type="text", text=f"{error_emoji} Last Error Code: {code}\nMessage: {message}")]
        
    except Exception as e:
        return create_error_response(e, "Last error code request")

@retry_on_network_failure.async_retry
async def handle_get_last_error_message(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle last error message request with error handling."""
    try:
        logger.debug("Getting last error message")
        code, message = api.get_last_code()
        
        error_emoji = "🔴" if code != 0 else "🟢"
        return [TextContent(type="text", text=f"{error_emoji} Last Error Message: {message}")]
        
    except Exception as e:
        return create_error_response(e, "Last error message request")

@retry_on_network_failure.async_retry
async def handle_get_session_status(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle session status request with error handling."""
    try:
        logger.debug("Getting session status")
        status_code, status_message = api.get_service_status()
        
        status_emoji = "🟢" if status_code == 1 else "🔴"
        return [TextContent(type="text", text=f"{status_emoji} Session Status: {status_message} (Code: {status_code})")]
        
    except Exception as e:
        return create_error_response(e, "Session status request")

@retry_on_network_failure.async_retry
async def handle_get_available_operations(arguments: Dict[str, Any], api: RegonAPI) -> List[TextContent]:
    """Handle available operations request with error handling."""
    try:
        logger.debug("Getting available operations")
        operations = api.get_operations()
        
        if not operations:
            return [TextContent(type="text", text="ℹ️ No operations information available.")]
        
        return [TextContent(type="text", text=json.dumps(operations, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        return create_error_response(e, "Available operations request")

@safe_execute
def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        sys.exit(0)
    
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        if hasattr(signal, 'SIGBREAK'):  # Windows
            signal.signal(signal.SIGBREAK, signal_handler)
    except Exception as e:
        logger.warning(f"Could not set up signal handlers: {e}")

async def main():
    """Main entry point with comprehensive error handling and recovery."""
    global logger, config
    
    # Set up signal handlers for graceful shutdown
    setup_signal_handlers()
    
    # Initialize basic logging first (before argument parsing)
    logger = setup_logging('INFO')  # Default level until we parse args
    
    try:
        # Parse command line arguments with error handling
        args = parse_arguments()
        if args is None:
            if logger:
                logger.error("Failed to parse arguments, exiting")
            else:
                print("ERROR: Failed to parse arguments, exiting")
            return 1
        
        # Update global configuration with validation
        config['production_mode'] = bool(getattr(args, 'production', False))
        config['log_level'] = getattr(args, 'log_level', 'INFO')
        config['tools_config'] = getattr(args, 'tools_config', None)
        
        # Re-setup logging with the correct level from arguments
        logger = setup_logging(config['log_level'])
        if logger is None:
            print("ERROR: Failed to setup logging, exiting")
            return 1
        
        # Log startup information
        mode = "production" if config['production_mode'] else "test"
        tools_config = config['tools_config'] or 'default'
        
        logger.info("=" * 60)
        logger.info("🚀 Starting RegonAPI MCP Server")
        logger.info(f"   Mode: {mode}")
        logger.info(f"   Log Level: {config['log_level']}")
        logger.info(f"   Tools Config: {tools_config}")
        logger.info(f"   Python Version: {sys.version}")
        logger.info(f"   Platform: {sys.platform}")
        logger.info("=" * 60)
        
        # Pre-flight checks
        health_results = health_checker.run_checks()
        logger.info(f"Health checks: {len(health_results)} components checked")
        
        # Initialize server with comprehensive error handling
        try:
            server_instance = get_server()
            if server_instance is None:
                raise ServerError("Failed to create server instance")
            
            logger.info("✅ Server instance created successfully")
            
        except Exception as e:
            logger.error(f"Server initialization failed: {e}", exc_info=True)
            return 1
        
        # Test RegonAPI connection
        try:
            await initialize_regon_api_async(config['production_mode'])
            logger.info("✅ RegonAPI connection established")
        except Exception as e:
            logger.warning(f"RegonAPI connection failed during startup: {e}")
            logger.info("Server will continue, but RegonAPI calls may fail")
        
        logger.info("🎯 Server ready to accept connections")
        
        # Run the server with error recovery
        max_restarts = 3
        restart_count = 0
        
        while restart_count < max_restarts:
            try:
                async with stdio_server() as (read_stream, write_stream):
                    logger.info("📡 MCP Server running...")
                    await server_instance.run(
                        read_stream,
                        write_stream,
                        server_instance.create_initialization_options()
                    )
                # If we reach here, server shut down normally
                logger.info("🛑 Server shut down normally")
                break
                
            except (KeyboardInterrupt, SystemExit):
                logger.info("🛑 Server stopped by user")
                break
                
            except Exception as e:
                restart_count += 1
                logger.error(f"Server error (attempt {restart_count}/{max_restarts}): {e}", exc_info=True)
                
                if restart_count < max_restarts:
                    wait_time = min(5 * restart_count, 30)  # Exponential backoff, max 30s
                    logger.info(f"🔄 Restarting server in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("❌ Maximum restart attempts reached, exiting")
                    return 1
        
        return 0
        
    except KeyboardInterrupt:
        if logger:
            logger.info("🛑 Server interrupted by user")
        else:
            print("🛑 Server interrupted by user")
        return 0
    except SystemExit as e:
        # Handle --help and other argument parser exits gracefully
        if e.code == 0:  # Normal exit (like --help)
            return 0
        if logger:
            logger.info(f"🛑 Server exit requested: {e.code}")
        else:
            print(f"🛑 Server exit requested: {e.code}")
        return e.code or 0
    except Exception as e:
        if logger:
            logger.error(f"❌ Critical error in main: {e}", exc_info=True)
        else:
            print(f"CRITICAL ERROR: {e}")
            traceback.print_exc()
        return 1
    finally:
        # Cleanup
        if logger:
            logger.info("🧹 Cleaning up resources...")
            try:
                # Close RegonAPI connection if exists
                global regon_api
                if regon_api:
                    # RegonAPI doesn't have explicit close method, but we can clear it
                    regon_api = None
                    logger.info("✅ RegonAPI connection cleaned up")
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")
            
            logger.info("👋 Goodbye!")

if __name__ == "__main__":
    # Initialize global variables with safe defaults
    regon_api: Optional[RegonAPI] = None
    logger = None
    
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
