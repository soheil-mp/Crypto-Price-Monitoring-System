"""
Time series storage for cryptocurrency price data.
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceStore:
    """Store for cryptocurrency price data."""
    
    def __init__(self, base_path: Union[str, Path]):
        """
        Initialize the price store.
        
        Args:
            base_path: Base directory for storing data files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different data types
        self.raw_dir = self.base_path / "raw"
        self.analytics_dir = self.base_path / "analytics"
        self.alerts_dir = self.base_path / "alerts"
        
        for directory in [self.raw_dir, self.analytics_dir, self.alerts_dir]:
            directory.mkdir(exist_ok=True)
            
    def _get_date_partition(self, timestamp: datetime) -> str:
        """Get partition path based on date."""
        return timestamp.strftime("%Y/%m/%d")
        
    def _get_hour_partition(self, timestamp: datetime) -> str:
        """Get partition path including hour."""
        return timestamp.strftime("%Y/%m/%d/%H")
        
    def store_raw_price(self, symbol: str, price_data: Dict) -> bool:
        """
        Store raw price data.
        
        Args:
            symbol: Trading pair symbol
            price_data: Price data dictionary
            
        Returns:
            bool: True if storage successful
        """
        try:
            timestamp = datetime.fromisoformat(price_data['timestamp'])
            partition = self._get_hour_partition(timestamp)
            
            # Create partition directory
            partition_dir = self.raw_dir / symbol.lower() / partition
            partition_dir.mkdir(parents=True, exist_ok=True)
            
            # Store data in JSON file
            filename = f"{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
            file_path = partition_dir / filename
            
            with open(file_path, 'w') as f:
                json.dump(price_data, f)
                
            logger.debug(f"Stored raw price data: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store raw price data: {e}")
            return False
            
    def store_analytics(self, symbol: str, analytics_data: Dict) -> bool:
        """
        Store price analytics data.
        
        Args:
            symbol: Trading pair symbol
            analytics_data: Analytics data dictionary
            
        Returns:
            bool: True if storage successful
        """
        try:
            timestamp = datetime.fromisoformat(analytics_data['timestamp'])
            partition = self._get_hour_partition(timestamp)
            
            # Create partition directory
            partition_dir = self.analytics_dir / symbol.lower() / partition
            partition_dir.mkdir(parents=True, exist_ok=True)
            
            # Store data in JSON file
            filename = f"{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
            file_path = partition_dir / filename
            
            with open(file_path, 'w') as f:
                json.dump(analytics_data, f)
                
            logger.debug(f"Stored analytics data: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store analytics data: {e}")
            return False
            
    def store_alert(self, symbol: str, alert_data: Dict) -> bool:
        """
        Store price alert data.
        
        Args:
            symbol: Trading pair symbol
            alert_data: Alert data dictionary
            
        Returns:
            bool: True if storage successful
        """
        try:
            timestamp = datetime.fromisoformat(alert_data['timestamp'])
            partition = self._get_date_partition(timestamp)
            
            # Create partition directory
            partition_dir = self.alerts_dir / symbol.lower() / partition
            partition_dir.mkdir(parents=True, exist_ok=True)
            
            # Store data in JSON file
            filename = f"{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
            file_path = partition_dir / filename
            
            with open(file_path, 'w') as f:
                json.dump(alert_data, f)
                
            logger.debug(f"Stored alert data: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store alert data: {e}")
            return False
            
    def get_price_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        as_dataframe: bool = True
    ) -> Union[List[Dict], pd.DataFrame]:
        """
        Retrieve price data for a given time range.
        
        Args:
            symbol: Trading pair symbol
            start_time: Start of time range
            end_time: End of time range (defaults to now)
            as_dataframe: Return as pandas DataFrame if True, else list of dicts
            
        Returns:
            Price data as DataFrame or list
        """
        end_time = end_time or datetime.now()
        data = []
        
        try:
            # Get all relevant partition directories
            current = start_time
            while current <= end_time:
                partition = self._get_hour_partition(current)
                partition_dir = self.raw_dir / symbol.lower() / partition
                
                if partition_dir.exists():
                    # Read all JSON files in partition
                    for file_path in partition_dir.glob("*.json"):
                        with open(file_path, 'r') as f:
                            price_data = json.load(f)
                            timestamp = datetime.fromisoformat(price_data['timestamp'])
                            
                            if start_time <= timestamp <= end_time:
                                data.append(price_data)
                                
                current += timedelta(hours=1)
                
            if not data:
                logger.warning(f"No data found for {symbol} between {start_time} and {end_time}")
                return pd.DataFrame() if as_dataframe else []
                
            # Sort by timestamp
            data.sort(key=lambda x: x['timestamp'])
            
            if as_dataframe:
                return pd.DataFrame(data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve price data: {e}")
            return pd.DataFrame() if as_dataframe else []
            
    def get_analytics_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        as_dataframe: bool = True
    ) -> Union[List[Dict], pd.DataFrame]:
        """
        Retrieve analytics data for a given time range.
        
        Args:
            symbol: Trading pair symbol
            start_time: Start of time range
            end_time: End of time range (defaults to now)
            as_dataframe: Return as pandas DataFrame if True, else list of dicts
            
        Returns:
            Analytics data as DataFrame or list
        """
        end_time = end_time or datetime.now()
        data = []
        
        try:
            # Get all relevant partition directories
            current = start_time
            while current <= end_time:
                partition = self._get_hour_partition(current)
                partition_dir = self.analytics_dir / symbol.lower() / partition
                
                if partition_dir.exists():
                    # Read all JSON files in partition
                    for file_path in partition_dir.glob("*.json"):
                        with open(file_path, 'r') as f:
                            analytics_data = json.load(f)
                            timestamp = datetime.fromisoformat(analytics_data['timestamp'])
                            
                            if start_time <= timestamp <= end_time:
                                data.append(analytics_data)
                                
                current += timedelta(hours=1)
                
            if not data:
                logger.warning(f"No analytics data found for {symbol} between {start_time} and {end_time}")
                return pd.DataFrame() if as_dataframe else []
                
            # Sort by timestamp
            data.sort(key=lambda x: x['timestamp'])
            
            if as_dataframe:
                return pd.DataFrame(data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve analytics data: {e}")
            return pd.DataFrame() if as_dataframe else []
            
    def get_alerts(
        self,
        symbol: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        as_dataframe: bool = True
    ) -> Union[List[Dict], pd.DataFrame]:
        """
        Retrieve alerts for a given time range.
        
        Args:
            symbol: Trading pair symbol
            start_time: Start of time range
            end_time: End of time range (defaults to now)
            as_dataframe: Return as pandas DataFrame if True, else list of dicts
            
        Returns:
            Alert data as DataFrame or list
        """
        end_time = end_time or datetime.now()
        data = []
        
        try:
            # Get all relevant partition directories
            current = start_time
            while current <= end_time:
                partition = self._get_date_partition(current)
                partition_dir = self.alerts_dir / symbol.lower() / partition
                
                if partition_dir.exists():
                    # Read all JSON files in partition
                    for file_path in partition_dir.glob("*.json"):
                        with open(file_path, 'r') as f:
                            alert_data = json.load(f)
                            timestamp = datetime.fromisoformat(alert_data['timestamp'])
                            
                            if start_time <= timestamp <= end_time:
                                data.append(alert_data)
                                
                current += timedelta(days=1)
                
            if not data:
                logger.warning(f"No alerts found for {symbol} between {start_time} and {end_time}")
                return pd.DataFrame() if as_dataframe else []
                
            # Sort by timestamp
            data.sort(key=lambda x: x['timestamp'])
            
            if as_dataframe:
                return pd.DataFrame(data)
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve alerts: {e}")
            return pd.DataFrame() if as_dataframe else [] 