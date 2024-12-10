"""
Script to run scheduled data exports for Tableau.
"""
import os
import sys
import time
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.storage.time_series.price_store import PriceStore
from src.storage.time_series.tableau_export import TableauExporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def copy_to_tableau_dir(source_path: Path, tableau_dir: Path):
    """Copy exported file to Tableau directory."""
    if source_path and source_path.exists():
        # Create same filename in tableau directory
        dest_path = tableau_dir / source_path.name
        shutil.copy2(source_path, dest_path)
        logger.info(f"Copied {source_path.name} to Tableau directory")
        return dest_path
    return None

def main():
    """Run scheduled data exports."""
    # Initialize components
    data_dir = project_root / "data"
    export_dir = data_dir / "tableau_exports"
    tableau_dir = project_root / "tableau" / "data"
    
    # Ensure directories exist
    export_dir.mkdir(parents=True, exist_ok=True)
    tableau_dir.mkdir(parents=True, exist_ok=True)
    
    price_store = PriceStore(data_dir)
    exporter = TableauExporter(price_store, export_dir)
    
    # Cryptocurrency symbols to export
    symbols = ["btcusdt", "ethusdt", "solusdt", "adausdt"]
    
    # Export interval (10 seconds for testing)
    export_interval = 10
    
    logger.info("Starting Tableau data export service")
    logger.info(f"Export directory: {export_dir}")
    logger.info(f"Tableau directory: {tableau_dir}")
    logger.info(f"Export interval: {export_interval} seconds")
    
    try:
        while True:
            try:
                now = datetime.now()
                start_time = now - timedelta(days=1)  # Last 24 hours
                
                # Export price data
                price_path = exporter.export_price_data(
                    symbols=symbols,
                    start_time=start_time,
                    end_time=now,
                    file_format='csv'
                )
                
                # Copy to Tableau directory
                if price_path:
                    tableau_path = copy_to_tableau_dir(price_path, tableau_dir)
                    if tableau_path:
                        logger.info(f"Price data available at: {tableau_path}")
                
                # Export analytics data
                analytics_path = exporter.export_analytics_data(
                    symbols=symbols,
                    start_time=start_time,
                    end_time=now,
                    file_format='csv'
                )
                
                # Copy to Tableau directory
                if analytics_path:
                    tableau_path = copy_to_tableau_dir(analytics_path, tableau_dir)
                    if tableau_path:
                        logger.info(f"Analytics data available at: {tableau_path}")
                
                # Clean up old files (keep last 7 days)
                cleanup_threshold = now - timedelta(days=7)
                
                # Clean export directory
                for file_path in export_dir.glob("*.csv"):
                    if file_path.stat().st_mtime < cleanup_threshold.timestamp():
                        file_path.unlink()
                        logger.debug(f"Cleaned up old export: {file_path}")
                
                # Clean tableau directory
                for file_path in tableau_dir.glob("*.csv"):
                    if file_path.stat().st_mtime < cleanup_threshold.timestamp():
                        file_path.unlink()
                        logger.debug(f"Cleaned up old tableau file: {file_path}")
                
            except Exception as e:
                logger.error(f"Error during export: {e}")
            
            # Wait for next export
            logger.info(f"Next export in {export_interval} seconds")
            time.sleep(export_interval)
            
    except KeyboardInterrupt:
        logger.info("Export service stopped")

if __name__ == "__main__":
    main() 