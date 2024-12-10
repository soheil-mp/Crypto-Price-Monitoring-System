"""
Runner script for the storage consumer.
"""
import os
import sys
import signal
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.storage.time_series.price_store import PriceStore
from src.storage.time_series.storage_consumer import StorageConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("Received shutdown signal")
    sys.exit(0)

def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create data directory in project root
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Initialize components
    price_store = PriceStore(data_dir)
    consumer = StorageConsumer(
        price_store=price_store,
        bootstrap_servers="localhost:9092",
        price_topics=[
            "crypto_prices.btcusdt",
            "crypto_prices.ethusdt",
            "crypto_prices.solusdt",
            "crypto_prices.adausdt"
        ],
        analytics_topic="crypto_analytics",
        alerts_topic="crypto_alerts"
    )
    
    try:
        logger.info("Starting storage consumer...")
        consumer.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        consumer.stop()
        logger.info("Storage consumer stopped")

if __name__ == "__main__":
    main() 