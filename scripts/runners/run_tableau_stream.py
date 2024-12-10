"""
Script to run real-time data streaming for Tableau.
"""
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.storage.time_series.tableau_streamer import TableauStreamer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the Tableau streaming service."""
    # Initialize streamer
    export_dir = project_root / "tableau" / "realtime"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure topics
    price_topics = [
        "crypto_prices.btcusdt",
        "crypto_prices.ethusdt",
        "crypto_prices.solusdt",
        "crypto_prices.adausdt"
    ]
    
    # Create and start streamer
    streamer = TableauStreamer(
        export_dir=export_dir,
        price_topics=price_topics,
        max_buffer_size=5000,  # Keep more data in memory
        export_interval=5      # Export more frequently
    )
    
    try:
        logger.info("""
Starting Tableau real-time streaming service...

Data will be exported to: tableau/realtime/
Files are updated every 5 seconds and include:
- realtime_prices_*.csv: Latest price data
- realtime_analytics_*.csv: Latest analytics
- realtime_alerts_*.csv: Latest alerts

To use in Tableau:
1. Create a new data source
2. Connect to Text File (CSV)
3. Select the realtime_*.csv files
4. Enable automatic refresh (5-10 seconds)
5. Use "Union" to combine multiple time periods
""")
        
        streamer.start()
        
        # Keep running until interrupted
        try:
            while True:
                input()  # Wait for Ctrl+C
        except KeyboardInterrupt:
            pass
            
    finally:
        streamer.stop()
        logger.info("Streaming service stopped")

if __name__ == "__main__":
    main() 