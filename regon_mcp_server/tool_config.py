#!/usr/bin/env python3
"""
Tool Configuration Loader for REGON MCP Server
Handles loading and managing customizable tool descriptions and configurations.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ToolConfigLoader:
    """Loads and manages tool configurations from JSON files."""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the tool configuration loader.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config = None
        self.available_configs = self._discover_configs()
        
    def _discover_configs(self) -> Dict[str, str]:
        """Discover available configuration files."""
        configs = {}
        
        if not self.config_dir.exists():
            logger.warning(f"Config directory {self.config_dir} does not exist")
            return configs
            
        for config_file in self.config_dir.glob("tools_*.json"):
            config_name = config_file.stem.replace("tools_", "")
            configs[config_name] = str(config_file)
            
        logger.info(f"Discovered tool configurations: {list(configs.keys())}")
        return configs
    
    def load_config(self, config_name: str = None) -> Dict[str, Any]:
        """
        Load a specific tool configuration.
        
        Args:
            config_name: Name of the configuration to load (e.g., 'default', 'polish', 'minimal')
                        If None, will use environment variable TOOLS_CONFIG or 'detailed'
        
        Returns:
            Loaded configuration dictionary
        """
        if config_name is None:
            config_name = os.getenv('TOOLS_CONFIG', 'detailed')
            
        # Try to load the requested config
        config_file = None
        
        if config_name in self.available_configs:
            config_file = self.available_configs[config_name]
        else:
            # Fallback to tools_{config_name}.json
            potential_file = self.config_dir / f"tools_{config_name}.json"
            if potential_file.exists():
                config_file = str(potential_file)
        
        if config_file is None:
            logger.warning(f"Config '{config_name}' not found, falling back to 'detailed'")
            # Fallback to detailed config
            if 'detailed' in self.available_configs:
                config_file = self.available_configs['detailed']
            else:
                # Ultimate fallback to the original file
                fallback_file = Path("regon_mcp_tools_ai_spec.json")
                if fallback_file.exists():
                    config_file = str(fallback_file)
                else:
                    raise FileNotFoundError(f"No tool configuration found for '{config_name}' and no fallback available")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            logger.info(f"Loaded tool configuration: {config_name} ({config_file})")
            logger.info(f"Configuration language: {self.config.get('language', 'unknown')}")
            logger.info(f"Number of tools: {len(self.config.get('tools', []))}")
            
            return self.config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Tool configuration file not found: {config_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in tool configuration file {config_file}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading tool configuration from {config_file}: {e}")
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool configuration dictionary or None if not found
        """
        if self.config is None:
            self.load_config()
            
        for tool in self.config.get('tools', []):
            if tool.get('name') == tool_name:
                return tool
                
        return None
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tool configurations.
        
        Returns:
            List of tool configuration dictionaries
        """
        if self.config is None:
            self.load_config()
            
        return self.config.get('tools', [])
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information from configuration.
        
        Returns:
            Server info dictionary
        """
        if self.config is None:
            self.load_config()
            
        return {
            'name': self.config.get('name', 'RegonAPI MCP Server'),
            'version': self.config.get('version', '1.0.0'),
            'description': self.config.get('description', 'Polish REGON database access'),
            'language': self.config.get('language', 'en'),
            'capabilities': self.config.get('capabilities', {}),
            'serverInfo': self.config.get('serverInfo', {})
        }
    
    def list_available_configs(self) -> List[str]:
        """
        List all available configuration names.
        
        Returns:
            List of configuration names
        """
        return list(self.available_configs.keys())
    
    def get_config_info(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Get basic information about a configuration without fully loading it.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Basic configuration info or None if not found
        """
        if config_name not in self.available_configs:
            return None
            
        config_file = self.available_configs[config_name]
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            return {
                'name': config.get('name', 'Unknown'),
                'version': config.get('version', 'Unknown'),
                'description': config.get('description', 'No description'),
                'language': config.get('language', 'unknown'),
                'tool_count': len(config.get('tools', [])),
                'file_path': config_file
            }
        except Exception as e:
            logger.error(f"Error reading config info for {config_name}: {e}")
            return None

# Global instance for the module
_config_loader = None

def get_config_loader(config_dir: str = "config") -> ToolConfigLoader:
    """
    Get the global configuration loader instance.
    
    Args:
        config_dir: Directory containing configuration files
        
    Returns:
        ToolConfigLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ToolConfigLoader(config_dir)
    return _config_loader

def load_tools_config(config_name: str = None) -> Dict[str, Any]:
    """
    Convenience function to load tools configuration.
    
    Args:
        config_name: Name of the configuration to load
        
    Returns:
        Loaded configuration dictionary
    """
    loader = get_config_loader()
    return loader.load_config(config_name)

def get_available_tool_configs() -> List[str]:
    """
    Get list of available tool configuration names.
    
    Returns:
        List of configuration names
    """
    loader = get_config_loader()
    return loader.list_available_configs()
