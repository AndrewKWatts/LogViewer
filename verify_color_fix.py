#!/usr/bin/env python3
#====== Log Viewer/verify_color_fix.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This code is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@gmail.com.
"""
Verify that the color fix is working by simulating GUI startup
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from LogViewer import LogViewer

def verify_gui_color_fix():
    """Verify the GUI will now load colors correctly"""
    print("Verifying Color Fix...")
    print("=" * 50)
    
    # Test 1: Check if log_config.json exists
    config_path = Path("log_config.json")
    if config_path.exists():
        print("✓ log_config.json found")
    else:
        print("✗ log_config.json NOT found!")
        return False
    
    # Test 2: Load config like GUI does
    try:
        viewer = LogViewer(config_path="log_config.json")
        print("✓ Config loaded successfully")
    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        return False
    
    # Test 3: Check if color configuration is present
    has_colors = False
    for category in viewer.config_manager.categories:
        if category.has_color_config():
            has_colors = True
            print(f"✓ Color config found for: {category.name} ({category.ColourType})")
    
    if not has_colors:
        print("✗ No color configuration found!")
        return False
    
    # Test 4: Load sample logs
    try:
        count = viewer.load_file("sample_logs.txt")
        print(f"✓ Loaded {count} sample logs")
    except Exception as e:
        print(f"✗ Failed to load sample logs: {e}")
        return False
    
    # Test 5: Verify colors will be applied
    color_matches = 0
    for log in viewer.logs[:5]:
        for category in viewer.config_manager.categories:
            if category.has_color_config():
                field_value = log.get_field(category.name)
                if field_value is not None:
                    color = category.get_color_for_value(field_value)
                    if color:
                        color_matches += 1
                        print(f"✓ Color match: {category.name}={field_value} -> {color}")
    
    if color_matches == 0:
        print("✗ No color matches found!")
        return False
    else:
        print(f"✓ Found {color_matches} color matches in first 5 logs")
    
    print("\n" + "=" * 50)
    print("COLOR FIX VERIFICATION: ✓ PASSED")
    print("=" * 50)
    print("\nThe GUI should now display colors correctly!")
    print("Expected colors:")
    print("  - ERROR logs: Red entire lines")
    print("  - WARNING logs: Orange entire lines") 
    print("  - INFO logs: Green entire lines")
    print("  - DEBUG logs: Gray entire lines")
    print("  - Various components: Colored line numbers")
    print("  - Error codes: Colored based on value ranges")
    
    return True

if __name__ == "__main__":
    verify_gui_color_fix()