#!/usr/bin/env python3
"""
Restore Unicode Icons Script - Reverse of fix_unicode.py

Now that we have proper UTF-8 encoding configured, we can restore
the beautiful Unicode icons in all example files!
"""

import os
import sys

# Configure UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# ASCII to Unicode mappings (reverse of fix_unicode.py)
ICON_REPLACEMENTS = {
    "[STARTED]": "🚀",
    "[STOPPED]": "⏹️", 
    "[ERROR]": "❌",
    "[OK]": "✅",
    "[STATS]": "📊",
    "[CONFIG]": "🔧",
    "[INFO]": "📝",
    "[LIST]": "📋",
    "[WARN]": "⚠️",
    "[TIP]": "💡",
    "[SEARCH]": "🔍",
    "[REPORT]": "📈",
    "[API]": "🌐",
    "[TIME]": "⏰",
    "[CALL]": "📞",
    "[FILE]": "📁",
    "[TARGET]": "🎯",
    "[SAVE]": "💾",
    "[REFRESH]": "🔄",
    "[READ]": "📖",
    "[NEW]": "✨",
    "[LINK]": "🔗",
    "[OUTPUT]": "📤",
    "[CRASH]": "💥",
    "[SUCCESS]": "🎉",
    "[PASS]": "🟢",
    "[FAIL]": "🔴",
    "[PAUSE]": "⏸️",
    "[DOCUMENT]": "📄",
    "[ENTITY]": "🏢",
    "[SETTINGS]": "⚙️",
    "[TIMER]": "⏱️",
}

def restore_icons_in_file(filepath):
    """Restore Unicode icons in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        for ascii_text, unicode_icon in ICON_REPLACEMENTS.items():
            if ascii_text in content:
                content = content.replace(ascii_text, unicode_icon)
                changes_made.append(f"{ascii_text} → {unicode_icon}")
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✨ Restored icons in: {filepath}")
            for change in changes_made:
                print(f"   {change}")
            return True, len(changes_made)
        else:
            print(f"📄 No icons to restore in: {filepath}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False, 0

def main():
    """Restore Unicode icons in all Python files in the examples directory."""
    example_files = [
        "basic_usage_example.py",
        "bulk_search_example.py",
        "reports_example.py", 
        "monitoring_example.py",
        "advanced_example.py",
        "run_all_examples.py"
    ]
    
    print("🎨 Restoring Unicode Icons in Example Files")
    print("=" * 50)
    print("Now that we have proper UTF-8 encoding, let's bring back the beautiful icons!")
    print()
    
    total_files_changed = 0
    total_replacements = 0
    
    for filename in example_files:
        if os.path.exists(filename):
            changed, count = restore_icons_in_file(filename)
            if changed:
                total_files_changed += 1
                total_replacements += count
        else:
            print(f"❌ File not found: {filename}")
    
    print()
    print("=" * 50)
    print(f"🎉 Restoration complete!")
    print(f"   📁 Files updated: {total_files_changed}")
    print(f"   🔄 Total replacements: {total_replacements}")
    
    if total_files_changed > 0:
        print()
        print("💡 The examples now use beautiful Unicode icons!")
        print("   Run an example to see the icons in action:")
        print("   python basic_usage_example.py")

if __name__ == "__main__":
    main()
