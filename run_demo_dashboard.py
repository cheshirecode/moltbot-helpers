#!/usr/bin/env python3
"""
Standalone script to run the demo dashboard server.
"""

import sys
import os

# Add the current directory to the path so we can import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from demo_dashboard import main

if __name__ == '__main__':
    main()