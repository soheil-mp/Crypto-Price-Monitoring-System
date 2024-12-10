"""
Runner script for the alert processor.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.alerting.alert_processor import AlertProcessor

def main():
    # Initialize alert processor with price topics
    price_topics = [
        'crypto_prices.btcusdt',
        'crypto_prices.ethusdt',
        'crypto_prices.solusdt',
        'crypto_prices.adausdt'
    ]
    
    processor = AlertProcessor(price_topics=price_topics)
    
    # Connect to Kafka
    if processor.connect():
        # Run the processor
        processor.run()
    
if __name__ == "__main__":
    main() 