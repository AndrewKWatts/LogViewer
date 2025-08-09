#!/usr/bin/env python3
#====== Log Viewer/debug_colors.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This code is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@gmail.com.
"""
Debug script to test color application in GUI
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from LogViewer import LogViewer

def debug_gui_colors():
    """Debug color application in GUI context"""
    print("Debugging GUI Color Application...")
    print("=" * 50)
    
    # Load with color configuration
    viewer = LogViewer(config_path="log_config.json")
    
    # Load sample logs
    count = viewer.load_file("sample_logs.txt")
    print(f"Loaded {count} log entries")
    
    # Test first few logs
    print("\nDebugging first 3 logs:")
    for i, log in enumerate(viewer.logs[:3], 1):
        print(f"\nLog {i}:")
        print(f"  Raw text: {log.raw_text[:100]}...")
        print(f"  Line number: {log.line_number}")
        
        # Check each color category
        for category in viewer.config_manager.categories:
            if category.has_color_config():
                field_value = log.get_field(category.name)
                color = category.get_color_for_value(field_value)
                print(f"  {category.name} ({category.ColourType}): '{field_value}' -> {color}")
    
    # Test GUI color tag creation
    print("\n" + "=" * 50)
    print("Testing GUI Color Tag Creation:")
    print("-" * 30)
    
    # Simulate GUI tag creation
    tag_counter = 0
    for category in viewer.config_manager.categories:
        if category.has_color_config():
            print(f"\nCategory: {category.name} ({category.ColourType})")
            for rgb_color in category.ColourMap.keys():
                hex_color = category._rgb_string_to_hex(rgb_color)
                tag_name = f"color_{tag_counter}"
                print(f"  RGB {rgb_color} -> Hex {hex_color} -> Tag {tag_name}")
                tag_counter += 1
    
    # Test actual GUI color application simulation
    print("\n" + "=" * 50)
    print("Simulating GUI Color Application:")
    print("-" * 30)
    
    for i, log in enumerate(viewer.logs[:3], 1):
        print(f"\nLog {i} Color Application:")
        
        # Check each category for color matches
        for category in viewer.config_manager.categories:
            if not category.has_color_config():
                continue
                
            field_value = log.get_field(category.name)
            if field_value is None:
                continue
            
            color = category.get_color_for_value(field_value)
            if not color:
                continue
            
            # Create tag name (simulate GUI logic)
            tag_name = f"{category.name}_{color.replace('#', '')}"
            
            print(f"  Would apply tag '{tag_name}' with color {color}")
            print(f"    Field: {category.name} = '{field_value}'")
            print(f"    Type: {category.ColourType}")

if __name__ == "__main__":
    debug_gui_colors()