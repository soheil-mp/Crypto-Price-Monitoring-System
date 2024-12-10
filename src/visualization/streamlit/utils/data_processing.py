"""Data processing utilities for the Streamlit app."""

import pandas as pd
import streamlit as st
from src.visualization.streamlit.config.constants import TIME_RANGES, RESAMPLE_INTERVALS

@st.cache_data
def load_data():
    """Load and preprocess the cryptocurrency data."""
    try:
        with st.spinner('Loading data...'):
            df = pd.read_csv('tableau/data/crypto_prices_20241208_215932.csv')
            
            # Verify required columns exist
            required_columns = ['symbol', 'price', 'timestamp', 'volume_24h']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
                st.stop()
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
            
            return df
    except FileNotFoundError:
        st.error("Data file not found. Please check the file path.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

def process_data(df, symbol, time_range, interval):
    """Process and filter the data based on selected parameters."""
    try:
        # Filter by symbol
        df = df[df['symbol'] == symbol].copy()
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Apply time range filter
        if time_range != 'All Data':
            hours = int(TIME_RANGES[time_range].replace('H', ''))
            last_timestamp = df['timestamp'].max()
            df = df[df['timestamp'] >= last_timestamp - pd.Timedelta(hours=hours)]
        
        # Resample data
        df = df.set_index('timestamp')
        resampled = df.resample(RESAMPLE_INTERVALS[interval]).agg({
            'price': 'last',
            'volume_24h': 'sum'
        }).reset_index()
        
        # Forward fill missing values
        resampled = resampled.fillna(method='ffill')
        
        return resampled
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return pd.DataFrame()

def calculate_statistics(df):
    """Calculate various statistics from the data."""
    try:
        if df.empty:
            raise ValueError("No data available for statistics calculation")
            
        stats = {
            'current_price': df['price'].iloc[-1],
            'min_price': df['price'].min(),
            'max_price': df['price'].max(),
            'avg_price': df['price'].mean(),
            'std_dev': df['price'].std(),
            'price_change': df['price'].iloc[-1] - df['price'].iloc[0],
            'avg_volume': df['volume_24h'].mean(),
            'skewness': df['price'].skew(),
            'kurtosis': df['price'].kurtosis()
        }
        
        # Calculate derived statistics
        stats['price_change_pct'] = (stats['price_change'] / df['price'].iloc[0]) * 100
        stats['price_range'] = stats['max_price'] - stats['min_price']
        stats['price_volatility'] = (stats['std_dev'] / stats['avg_price']) * 100
        
        return stats
    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")
        return {k: 0 for k in ['current_price', 'min_price', 'max_price', 'avg_price', 
                              'std_dev', 'price_change', 'avg_volume', 'skewness', 
                              'kurtosis', 'price_change_pct', 'price_range', 'price_volatility']} 