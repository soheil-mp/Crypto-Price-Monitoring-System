"""
Script to help set up Tableau environment for cryptocurrency data visualization.
"""
import os
import sys
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.storage.time_series.price_store import PriceStore
from src.storage.time_series.tableau_export import TableauExporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_tableau_environment():
    """Set up the Tableau environment with sample data and documentation."""
    try:
        # Create directory structure
        tableau_dir = project_root / "tableau"
        tableau_dir.mkdir(exist_ok=True)
        
        data_dir = tableau_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        docs_dir = tableau_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Copy documentation
        templates_src = project_root / "scripts" / "tableau" / "tableau_templates.md"
        if templates_src.exists():
            shutil.copy(templates_src, docs_dir / "templates.md")
            logger.info(f"Copied templates to {docs_dir / 'templates.md'}")
        else:
            logger.warning(f"Templates file not found at {templates_src}")
        
        # Create sample data directory if it doesn't exist
        data_store_dir = project_root / "data"
        data_store_dir.mkdir(exist_ok=True)
        
        # Create placeholder files to indicate directory structure
        placeholder_content = """# This is a placeholder file
# Real data will be populated when the system is running
# Files in this directory:
# - crypto_prices_*.csv: Historical price data
# - crypto_analytics_*.csv: Technical analysis data
# - realtime_*.csv: Real-time streaming data
"""
        
        # Create placeholder files
        (data_dir / "PLACEHOLDER.md").write_text(placeholder_content)
        logger.info("Created placeholder file in data directory")
        
        # Create Tableau instructions
        with open(docs_dir / "setup_instructions.md", "w") as f:
            f.write("""# Tableau Setup Instructions

> ⚠️ Important: Before connecting Tableau, ensure the data pipeline is running:
> 1. Start the crypto feed: `python scripts/runners/run_crypto_feed.py`
> 2. Start the processor: `python scripts/runners/run_processor.py`
> 3. Start the storage service: `python scripts/runners/run_storage.py`
> 4. Start Tableau services:
>    - For historical data: `python scripts/runners/run_tableau_export.py`
>    - For real-time data: `python scripts/runners/run_tableau_stream.py`

1. **Data Connection**
   - Open Tableau Desktop
   - Connect to Text File (CSV)
   - Navigate to `tableau/data` directory
   - Select the latest `crypto_prices_*.csv` and `crypto_analytics_*.csv` files
   - Set up relationships between the data sources

2. **Template Setup**
   - Follow the templates in `docs/templates.md`
   - Create calculated fields as specified
   - Set up parameters and filters
   - Configure refresh schedules

3. **Best Practices**
   - Use extracts for better performance
   - Set up incremental refreshes
   - Follow the visual design guidelines
   - Implement security measures as needed

4. **Maintenance**
   - Data is refreshed every 15 minutes
   - Keep workbooks version controlled
   - Test calculations regularly
   - Update documentation as needed

5. **Support**
   - Check `docs/templates.md` for detailed guidance
   - Contact system administrator for access issues
   - Report bugs and feature requests through appropriate channels

6. **Troubleshooting**
   - If no data appears, ensure the data pipeline is running
   - Check the logs in `logs/` directory
   - Verify Kafka and other services are running
   - Ensure proper network connectivity
""")
        
        logger.info(f"""
Tableau environment setup complete! Directory structure created:

{tableau_dir}/
├── data/               # Data exports directory
│   └── PLACEHOLDER.md  # Placeholder for data files
├── docs/               # Documentation
│   ├── templates.md    # Dashboard templates
│   └── setup_instructions.md
└── realtime/          # Real-time data directory

Note: Actual data files will be created when you run:
1. python scripts/runners/run_tableau_export.py  (for historical data)
2. python scripts/runners/run_tableau_stream.py  (for real-time data)
""")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to set up Tableau environment: {e}")
        return False

def main():
    """Main entry point."""
    if setup_tableau_environment():
        logger.info("""
Next steps:
1. Start the data pipeline (crypto feed, processor, storage)
2. Run the Tableau export service: python scripts/runners/run_tableau_export.py
3. Run the streaming service: python scripts/runners/run_tableau_stream.py
4. Open Tableau Desktop and connect to the CSV files in tableau/data
5. Follow the templates in tableau/docs/templates.md
6. Start building your dashboards!
""")
    else:
        logger.error("Failed to set up Tableau environment")

if __name__ == "__main__":
    main() 