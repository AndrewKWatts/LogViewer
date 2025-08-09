#!/usr/bin/env python3
#====== Log Viewer/verify_parsing.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This code is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@gmail.com.
"""
Verify that the log parsing works correctly with the sample logs
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from LogViewer import LogViewer

def test_parsing():
    """Test log parsing functionality"""
    print("Testing log parsing...")
    
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
    print(f"Loaded {count} log entries")
    
    # Display first few logs in detail
    print("\nFirst 3 logs (detailed view):")
    viewer.display_logs(limit=3, detailed=True)
    
    # Test filtering
    print(f"\nFiltering for ERROR logs...")
    error_count = viewer.filter_by_field('LogLevel', 'ERROR')
    print(f"Found {error_count} ERROR logs")
    
    if error_count > 0:
        print("\nERROR logs:")
        viewer.display_logs(limit=2, detailed=False)
    
    # Show stats
    stats = viewer.get_stats()
    print(f"\nStatistics:")
    print(f"  Total logs: {stats['total_logs']}")
    print(f"  Filtered logs: {stats['filtered_logs']}")
    if 'log_levels' in stats:
        print(f"  Log levels breakdown:")
        for level, count in stats['log_levels'].items():
            print(f"    {level}: {count}")

if __name__ == "__main__":
    test_parsing()