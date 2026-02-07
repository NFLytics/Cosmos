"""
Quick-start script to run the complete analysis

Place this in the project root directory and run:
    python run_analysis.py
"""

import os
import sys

# Ensure working directory is set correctly
if not os.path.exists('data'):
    print("ERROR: Please run this script from the project root directory")
    print("Current working directory:", os.getcwd())
    sys.exit(1)

# Run main analysis
from src.main import main

if __name__ == "__main__":
    main()