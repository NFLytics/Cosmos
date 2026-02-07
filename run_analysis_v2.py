"""
Quick-start script for Phase 1B - Expanded Analysis with Quality Levels

Run with:
    python run_analysis_v2.py
"""

import os
import sys

if not os.path.exists('data'):
    print("ERROR: Please run this script from the project root directory")
    print("Current working directory:", os.getcwd())
    sys.exit(1)

from src.main_v2 import main

if __name__ == "__main__":
    main()