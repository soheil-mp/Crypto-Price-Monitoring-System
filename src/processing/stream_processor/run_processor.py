"""
Script to run the stream processor.
"""
import logging
import signal
import sys
from src.processing.stream_processor.price_processor import PriceProcessor

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
    
    # Create and start processor
    processor = PriceProcessor(
        bootstrap_servers="localhost:9092",
        input_topic_prefix="crypto_prices",
        alert_topic="crypto_alerts",
        analytics_topic="crypto_analytics",
        symbols=["btcusdt", "ethusdt", "solusdt", "adausdt"]
    )
    
    try:
        logger.info("Starting price processor...")
        processor.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        processor.stop()
        logger.info("Processor stopped")

if __name__ == "__main__":
    main() 