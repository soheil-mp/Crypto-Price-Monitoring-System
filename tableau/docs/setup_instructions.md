# Tableau Setup Instructions

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
