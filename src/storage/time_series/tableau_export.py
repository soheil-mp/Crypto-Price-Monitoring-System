"""
Data export module for Tableau integration.
"""
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Union
from .price_store import PriceStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TableauExporter:
    """Export data in Tableau-compatible format."""
    
    def __init__(self, price_store: PriceStore, export_dir: Union[str, Path]):
        """
        Initialize the Tableau exporter.
        
        Args:
            price_store: PriceStore instance for data access
            export_dir: Directory for exported files
        """
        self.price_store = price_store
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized TableauExporter with export directory: {self.export_dir}")
        
    def _add_time_dimensions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based dimensions for Tableau analysis."""
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        df['year'] = df['timestamp'].dt.year
        df['month'] = df['timestamp'].dt.month
        df['month_name'] = df['timestamp'].dt.month_name()
        df['day'] = df['timestamp'].dt.day
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['week_of_year'] = df['timestamp'].dt.isocalendar().week
        df['is_weekend'] = df['timestamp'].dt.weekday.isin([5, 6])
        df['trading_session'] = pd.cut(
            df['hour'],
            bins=[-1, 6, 12, 18, 24],
            labels=['Night', 'Morning', 'Afternoon', 'Evening']
        )
        return df
        
    def _calculate_moving_averages(self, prices: pd.Series) -> dict:
        """Calculate various moving averages."""
        return {
            'ma_5min': prices.rolling('5min').mean(),
            'ma_15min': prices.rolling('15min').mean(),
            'ma_1hour': prices.rolling('1H').mean(),
            'ema_5min': prices.ewm(span=5, adjust=False).mean(),
            'ema_15min': prices.ewm(span=15, adjust=False).mean(),
            'ema_1hour': prices.ewm(span=60, adjust=False).mean(),
        }
        
    def _calculate_bollinger_bands(self, prices: pd.Series, window: str = '15min', num_std: float = 2.0) -> dict:
        """Calculate Bollinger Bands."""
        rolling = prices.rolling(window)
        middle_band = rolling.mean()
        std = rolling.std()
        return {
            'bb_middle': middle_band,
            'bb_upper': middle_band + (std * num_std),
            'bb_lower': middle_band - (std * num_std),
            'bb_width': ((middle_band + (std * num_std)) - (middle_band - (std * num_std))) / middle_band
        }
        
    def _calculate_macd(self, prices: pd.Series) -> dict:
        """Calculate MACD indicator."""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return {
            'macd': macd,
            'macd_signal': signal,
            'macd_histogram': macd - signal
        }
        
    def _calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> dict:
        """Calculate Stochastic Oscillator."""
        lowest_low = low.rolling(window=window).min()
        highest_high = high.rolling(window=window).max()
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=3).mean()
        return {
            'stoch_k': k,
            'stoch_d': d
        }
        
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high_low = high - low
        high_close = (high - close.shift()).abs()
        low_close = (low - close.shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=window).mean()
        
    def _calculate_rsi(self, prices: pd.Series, periods: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    def _calculate_price_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate additional price metrics for analysis."""
        # Group by symbol for calculations
        for symbol in df['symbol'].unique():
            mask = df['symbol'] == symbol
            symbol_data = df[mask].copy()
            
            # Sort by timestamp
            symbol_data = symbol_data.sort_values('timestamp')
            
            # Basic price changes
            df.loc[mask, 'price_change'] = symbol_data['price'].diff()
            df.loc[mask, 'price_change_pct'] = symbol_data['price'].pct_change() * 100
            
            # Moving averages and EMAs
            mas = self._calculate_moving_averages(symbol_data['price'])
            for name, values in mas.items():
                df.loc[mask, name] = values
            
            # Bollinger Bands
            bbs = self._calculate_bollinger_bands(symbol_data['price'])
            for name, values in bbs.items():
                df.loc[mask, name] = values
            
            # MACD
            macd = self._calculate_macd(symbol_data['price'])
            for name, values in macd.items():
                df.loc[mask, name] = values
            
            # Stochastic Oscillator
            stoch = self._calculate_stochastic(
                symbol_data['price'],  # Using price as high/low/close for now
                symbol_data['price'],
                symbol_data['price']
            )
            for name, values in stoch.items():
                df.loc[mask, name] = values
            
            # ATR
            df.loc[mask, 'atr'] = self._calculate_atr(
                symbol_data['price'],  # Using price as high/low/close for now
                symbol_data['price'],
                symbol_data['price']
            )
            
            # RSI
            df.loc[mask, 'rsi'] = self._calculate_rsi(symbol_data['price'])
            
            # Trend indicators
            df.loc[mask, 'trend_ema'] = np.where(
                symbol_data['price'] > mas['ema_15min'],
                'Uptrend',
                'Downtrend'
            )
            
            df.loc[mask, 'volatility_regime'] = pd.qcut(
                df.loc[mask, 'atr'],
                q=5,
                labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
            )
            
            # Support and resistance levels
            price_std = symbol_data['price'].std()
            pivot = symbol_data['price'].mean()
            df.loc[mask, 'pivot'] = pivot
            df.loc[mask, 'r1'] = pivot + price_std
            df.loc[mask, 's1'] = pivot - price_std
            df.loc[mask, 'r2'] = pivot + (2 * price_std)
            df.loc[mask, 's2'] = pivot - (2 * price_std)
        
        return df
        
    def export_price_data(
        self,
        symbols: list[str],
        start_time: datetime,
        end_time: Optional[datetime] = None,
        file_format: str = 'csv'
    ) -> Optional[Path]:
        """
        Export price data for Tableau.
        
        Args:
            symbols: List of cryptocurrency symbols
            start_time: Start of time range
            end_time: End of time range (defaults to now)
            file_format: Export format ('csv' or 'parquet')
            
        Returns:
            Path: Path to exported file
        """
        end_time = end_time or datetime.now()
        
        # Collect data for all symbols
        all_data = []
        for symbol in symbols:
            try:
                df = self.price_store.get_price_data(
                    symbol=symbol,
                    start_time=start_time,
                    end_time=end_time,
                    as_dataframe=True
                )
                if not df.empty:
                    all_data.append(df)
                    logger.debug(f"Collected {len(df)} records for {symbol}")
            except Exception as e:
                logger.error(f"Error collecting data for {symbol}: {e}")
        
        if not all_data:
            logger.warning("No data to export")
            return None
            
        try:
            # Combine all data
            combined_df = pd.concat(all_data, ignore_index=True)
            logger.info(f"Combined {len(combined_df)} total records")
            
            # Generate export path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"crypto_prices_{timestamp}.{file_format}"
            export_path = self.export_dir / filename
            
            # Export data
            if file_format == 'csv':
                combined_df.to_csv(export_path, index=False)
            elif file_format == 'parquet':
                combined_df.to_parquet(export_path, index=False)
            else:
                raise ValueError(f"Unsupported format: {file_format}")
                
            logger.info(f"Exported data to {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return None
            
    def export_analytics_data(
        self,
        symbols: list[str],
        start_time: datetime,
        end_time: Optional[datetime] = None,
        file_format: str = 'csv'
    ) -> Optional[Path]:
        """
        Export analytics data for Tableau.
        
        Args:
            symbols: List of cryptocurrency symbols
            start_time: Start of time range
            end_time: End of time range (defaults to now)
            file_format: Export format ('csv' or 'parquet')
            
        Returns:
            Path: Path to exported file
        """
        end_time = end_time or datetime.now()
        
        # Collect analytics data for all symbols
        all_data = []
        for symbol in symbols:
            try:
                df = self.price_store.get_analytics_data(
                    symbol=symbol,
                    start_time=start_time,
                    end_time=end_time,
                    as_dataframe=True
                )
                if not df.empty:
                    all_data.append(df)
                    logger.debug(f"Collected {len(df)} analytics records for {symbol}")
            except Exception as e:
                logger.error(f"Error collecting analytics data for {symbol}: {e}")
        
        if not all_data:
            logger.warning("No analytics data to export")
            return None
            
        try:
            # Combine all data
            combined_df = pd.concat(all_data, ignore_index=True)
            logger.info(f"Combined {len(combined_df)} total analytics records")
            
            # Generate export path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"crypto_analytics_{timestamp}.{file_format}"
            export_path = self.export_dir / filename
            
            # Export data
            if file_format == 'csv':
                combined_df.to_csv(export_path, index=False)
            elif file_format == 'parquet':
                combined_df.to_parquet(export_path, index=False)
            else:
                raise ValueError(f"Unsupported format: {file_format}")
                
            logger.info(f"Exported analytics data to {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Error exporting analytics data: {e}")
            return None