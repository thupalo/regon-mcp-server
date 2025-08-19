#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'regon_mcp_server')

# Configure UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from regon_mcp_server.tool_config import get_config_loader

loader = get_config_loader()
config = loader.load_config('polish')
server_info = loader.get_server_info()
tools = loader.get_all_tools()

print('🇵🇱 Polish Configuration Test')
print(f'Nazwa serwera: {server_info["name"]}')
print(f'Język: {server_info["language"]}')
print(f'Liczba narzędzi: {len(tools)}')
print()
print('Pierwsze 3 narzędzia:')
for i, tool in enumerate(tools[:3]):
    print(f'{i+1}. {tool["name"]}')
    print(f'   {tool["description"]}')
    print()
