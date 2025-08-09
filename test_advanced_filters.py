#!/usr/bin/env python3
#====== Log Viewer/test_advanced_filters.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This code is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@gmail.com.
"""
Test script for advanced filtering functionality
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from LogViewer import LogViewer

def test_enhanced_filters():
    """Test the enhanced filtering capabilities"""
    print("Testing Advanced Filtering...")
    print("=" * 50)
    
    # Create log viewer with correct config
    config = {
        "logViewerConfig": {
            "delimiters": {
                "logStartDelimiter": "[",
                "logEndDelimiter": "]###",
                "categorySeparator": "|",
                "keyValuePairsSeparator": ";",
                "keyValueSeparator": "=",
                "arrayElementSeparator": ","
            },
            "categories": [
                {"name": "Timestamp", "type": "datetime", "order": 1},
                {"name": "LogLevel", "type": "string", "order": 2},
                {"name": "Component", "type": "string", "order": 3},
                {"name": "Details", "type": "structured_string", "order": 4},
                {"name": "Tags", "type": "array_string", "order": 5},
                {"name": "ErrorCode", "type": "number", "order": 6}
            ]
        }
    }
    
    viewer = LogViewer(config_dict=config)
    
    # Load sample logs
    sample_file = Path(__file__).parent / "sample_logs.txt"
    if not sample_file.exists():
        print("ERROR: sample_logs.txt not found!")
        return
    
    count = viewer.load_file(str(sample_file))
    print(f"Loaded {count} log entries\n")
    
    # Test 1: Basic string filtering
    print("Test 1: String filtering (LogLevel = ERROR)")
    print("-" * 30)
    error_count = viewer.filter_by_field('LogLevel', 'ERROR', 'equals')
    print(f"Found {error_count} ERROR logs")
    if error_count > 0:
        print("First ERROR log:")
        print(f"  {viewer.filtered_logs[0]}")
    print()
    
    # Test 2: Structured string filtering (Details field)
    print("Test 2: Structured string filtering (Details contains 'action=query')")
    print("-" * 50)
    viewer.reset_filters()
    query_logs = []
    for log in viewer.logs:
        details = log.get_field('Details')
        if isinstance(details, dict) and 'action' in details and details['action'] == 'query':
            query_logs.append(log)
    
    print(f"Found {len(query_logs)} logs with action=query")
    for i, log in enumerate(query_logs[:2], 1):
        print(f"  {i}. {log.get_field('Component')}: {log.get_field('Details')}")
    print()
    
    # Test 3: Array string filtering (Tags field)
    print("Test 3: Array string filtering (Tags contains 'critical')")
    print("-" * 45)
    viewer.reset_filters()
    critical_logs = []
    for log in viewer.logs:
        tags = log.get_field('Tags')
        if isinstance(tags, list) and any('critical' in str(tag).lower() for tag in tags):
            critical_logs.append(log)
    
    print(f"Found {len(critical_logs)} logs with 'critical' tag")
    for i, log in enumerate(critical_logs[:2], 1):
        print(f"  {i}. {log.get_field('Component')}: {log.get_field('Tags')}")
    print()
    
    # Test 4: Number range filtering (ErrorCode)
    print("Test 4: Number range filtering (ErrorCode > 1000)")
    print("-" * 40)
    viewer.reset_filters()
    high_error_logs = []
    for log in viewer.logs:
        error_code = log.get_field('ErrorCode')
        if error_code is not None and error_code > 1000:
            high_error_logs.append(log)
    
    print(f"Found {len(high_error_logs)} logs with ErrorCode > 1000")
    for i, log in enumerate(high_error_logs[:3], 1):
        print(f"  {i}. Code {log.get_field('ErrorCode')}: {log.get_field('Component')}")
    print()
    
    # Test 5: Time filtering (partial match)
    print("Test 5: Time filtering (Timestamp contains '06:50')")
    print("-" * 42)
    viewer.reset_filters()
    morning_logs = []
    for log in viewer.logs:
        timestamp = log.get_field('Timestamp')
        if timestamp and '06:50' in str(timestamp):
            morning_logs.append(log)
    
    print(f"Found {len(morning_logs)} logs from 06:50 period")
    for i, log in enumerate(morning_logs[:2], 1):
        print(f"  {i}. {log.get_field('Timestamp')}: {log.get_field('Component')}")
    print()
    
    # Test 6: Multiple filters combination
    print("Test 6: Multiple filters (ERROR logs with critical tags)")
    print("-" * 48)
    viewer.reset_filters()
    combined_logs = []
    for log in viewer.logs:
        log_level = log.get_field('LogLevel')
        tags = log.get_field('Tags')
        if (log_level == 'ERROR' and 
            isinstance(tags, list) and 
            any('critical' in str(tag).lower() for tag in tags)):
            combined_logs.append(log)
    
    print(f"Found {len(combined_logs)} ERROR logs with critical tags")
    for i, log in enumerate(combined_logs, 1):
        print(f"  {i}. {log.get_field('Component')}: {log.get_field('Details')}")
    print()
    
    print("=" * 50)
    print("Advanced filtering test completed!")
    print("\nGUI Features now include:")
    print("✓ Dropdown operators for each field type")
    print("✓ Range inputs for numbers and dates")
    print("✓ Special operators for structured/array strings")
    print("✓ Multiple simultaneous filters")
    print("✓ Scrollable filter panel")
    print("✓ Help text for each filter type")

if __name__ == "__main__":
    test_enhanced_filters()