#!/usr/bin/env python3
#====== Log Viewer/test_gui.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This code is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@gmail.com.
"""
Test script for the Log Viewer GUI
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from LogViewerGUI import LogViewerGUI
import threading

def test_gui():
    """Test the GUI functionality"""
    print("Testing Log Viewer GUI...")
    
    # Create GUI instance
    app = LogViewerGUI()
    
    # Load sample logs automatically
    sample_file = Path(__file__).parent / "sample_logs.txt"
    if sample_file.exists():
        print(f"Loading sample file: {sample_file}")
        app.load_log_file(str(sample_file))
    
    print("GUI initialized successfully!")
    print("GUI should open in a new window.")
    print("Press Ctrl+C in terminal to close the GUI, or use File > Exit in the GUI.")
    
    # Start GUI
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nGUI closed by user.")

if __name__ == "__main__":
    test_gui()