"""
Runner script for the stream processor.
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.processing.stream_processor.run_processor import main

if __name__ == "__main__":
    main() 