#!/usr/bin/env python3
"""
Quick fix script to replace Unicode characters in all example files
"""

import os
import re

# Unicode to ASCII mappings
REPLACEMENTS = {
    "🚀": "[STARTED]",
    "⏹️": "[STOPPED]", 
    "❌": "[ERROR]",
    "✅": "[OK]",
    "📊": "[STATS]",
    "🔧": "[CONFIG]",
    "📝": "[INFO]",
    "📋": "[LIST]",
    "⚠️": "[WARN]",
    "💡": "[TIP]",
    "🔍": "[SEARCH]",
    "📈": "[REPORT]",
    "🌐": "[API]",
    "⏰": "[TIME]",
    "📞": "[CALL]",
    "📁": "[FILE]",
    "🎯": "[TARGET]",
    "💾": "[SAVE]",
    "🔄": "[REFRESH]",
    "📖": "[READ]",
    "✨": "[NEW]",
    "🔗": "[LINK]",
    "📤": "[OUTPUT]",
    "💥": "[CRASH]",
    "🎉": "[SUCCESS]",
    "🟢": "[PASS]",
    "🔴": "[FAIL]",
    "🔹": "[INFO]",
    "⏸️": "[PAUSE]",
    "📄": "[DOCUMENT]",
    "🏢": "[ENTITY]",
    "⚙️": "[SETTINGS]",
    "⏱️": "[TIMER]",
    "•": "*",  # bullet point
}

def fix_file(filepath):
    """Fix Unicode characters in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for unicode_char, replacement in REPLACEMENTS.items():
            content = content.replace(unicode_char, replacement)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath}")
            return True
        else:
            print(f"No changes needed: {filepath}")
            return False
            
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """Fix all Python files in the examples directory."""
    example_files = [
        "basic_usage_example.py",
        "bulk_search_example.py",
        "reports_example.py", 
        "monitoring_example.py",
        "advanced_example.py",
        "run_all_examples.py"
    ]
    
    fixed_count = 0
    
    for filename in example_files:
        if os.path.exists(filename):
            if fix_file(filename):
                fixed_count += 1
        else:
            print(f"File not found: {filename}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()
