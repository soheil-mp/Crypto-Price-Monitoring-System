"""
Runner script for the crypto feed example.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.data_ingestion.crypto_feeds.example import main

if __name__ == "__main__":
    main() 