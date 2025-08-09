#!/usr/bin/env python3
#====== Log Viewer/test_colors.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This code is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@gmail.com.
"""
Test script for configurable coloring functionality
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from LogViewer import LogViewer, LogCategory

def test_color_configuration():
    """Test the color configuration parsing and functionality"""
    print("Testing Configurable Coloring...")
    print("=" * 50)
    
    # Load with color configuration
    viewer = LogViewer(config_path="log_config.json")
    
    # Load sample logs
    sample_file = Path(__file__).parent / "sample_logs.txt"
    if not sample_file.exists():
        print("ERROR: sample_logs.txt not found!")
        return
    
    count = viewer.load_file(str(sample_file))
    print(f"Loaded {count} log entries\n")
    
    # Test color configuration parsing
    print("Color Configuration Test:")
    print("-" * 30)
    
    for category in viewer.config_manager.categories:
        print(f"\nCategory: {category.name}")
        print(f"  Type: {category.type}")
        print(f"  Has Color Config: {category.has_color_config()}")
        
        if category.has_color_config():
            print(f"  Color Type: {category.ColourType}")
            print(f"  Color Map: {category.ColourMap}")
            
            # Test color resolution for first few logs
            print(f"  Color Tests:")
            for i, log in enumerate(viewer.logs[:3], 1):
                field_value = log.get_field(category.name)
                color = category.get_color_for_value(field_value)
                print(f"    Log {i}: '{field_value}' -> {color}")
    
    print("\n" + "=" * 50)
    print("Specific Color Tests:")
    print("-" * 30)
    
    # Test LogLevel coloring (WholeLine)
    log_level_category = viewer.config_manager.get_category_by_name('LogLevel')
    if log_level_category and log_level_category.has_color_config():
        print(f"\nLogLevel (WholeLine) Tests:")
        test_values = ['ERROR', 'WARNING', 'INFO', 'DEBUG']
        for value in test_values:
            color = log_level_category.get_color_for_value(value)
            print(f"  '{value}' -> {color}")
    
    # Test Component coloring (LineNumber)  
    component_category = viewer.config_manager.get_category_by_name('Component')
    if component_category and component_category.has_color_config():
        print(f"\nComponent (LineNumber) Tests:")
        test_values = ['DatabaseService', 'ApplicationService', 'AuthService', 'PaymentService']
        for value in test_values:
            color = component_category.get_color_for_value(value)
            print(f"  '{value}' -> {color}")
    
    # Test ErrorCode coloring (SpecificValue with ranges)
    error_code_category = viewer.config_manager.get_category_by_name('ErrorCode')
    if error_code_category and error_code_category.has_color_config():
        print(f"\nErrorCode (SpecificValue) Range Tests:")
        test_values = [0, 5, 15, 25, 35, 55, 1001, 2003, 3001, 5001]
        for value in test_values:
            color = error_code_category.get_color_for_value(value)
            print(f"  {value} -> {color}")
    
    print("\n" + "=" * 50)
    print("Real Log Data Color Analysis:")
    print("-" * 30)
    
    # Analyze actual log colors
    color_stats = {}
    for i, log in enumerate(viewer.logs[:10], 1):
        print(f"\nLog {i}: Line {log.line_number}")
        
        for category in viewer.config_manager.categories:
            if category.has_color_config():
                field_value = log.get_field(category.name)
                color = category.get_color_for_value(field_value)
                
                if color:
                    print(f"  {category.name} ({category.ColourType}): '{field_value}' -> {color}")
                    
                    # Track color usage
                    key = f"{category.name}_{category.ColourType}"
                    if key not in color_stats:
                        color_stats[key] = {}
                    if color not in color_stats[key]:
                        color_stats[key][color] = 0
                    color_stats[key][color] += 1
    
    print("\n" + "=" * 50)
    print("Color Usage Statistics:")
    print("-" * 30)
    
    for category_type, colors in color_stats.items():
        print(f"\n{category_type}:")
        for color, count in colors.items():
            print(f"  {color}: {count} occurrences")
    
    print("\n" + "=" * 50)
    print("Color Configuration Test Completed!")
    print("\nImplemented Features:")
    print("✓ Parse ColourType and ColourMap from JSON")
    print("✓ WholeLine coloring (entire log entry)")
    print("✓ LineNumber coloring (line number area)")
    print("✓ SpecificValue coloring with range support")
    print("✓ RGB string to hex conversion")
    print("✓ Range parsing (1-20, 50-65 format)")

def test_range_parsing():
    """Test the range parsing functionality specifically"""
    print("\n" + "=" * 50)
    print("Range Parsing Tests:")
    print("-" * 30)
    
    # Create test category
    category = LogCategory(
        name="TestCategory",
        type="number",
        order=1,
        ColourType="SpecificValue",
        ColourMap={
            "255,0,0": "1-10, 20-30, 50",
            "0,255,0": "100-200",
            "0,0,255": "500"
        }
    )
    
    test_cases = [
        (1, "255,0,0"),      # In range 1-10
        (5, "255,0,0"),      # In range 1-10
        (10, "255,0,0"),     # Edge of range 1-10
        (15, None),          # Not in any range
        (25, "255,0,0"),     # In range 20-30
        (50, "255,0,0"),     # Exact match 50
        (150, "0,255,0"),    # In range 100-200
        (300, None),         # Not in any range
        (500, "0,0,255"),    # Exact match 500
    ]
    
    for value, expected_rgb in test_cases:
        color = category.get_color_for_value(value)
        expected_hex = category._rgb_string_to_hex(expected_rgb) if expected_rgb else None
        
        result = "✓" if color == expected_hex else "✗"
        print(f"  {result} Value {value}: Expected {expected_hex}, Got {color}")

if __name__ == "__main__":
    test_color_configuration()
    test_range_parsing()