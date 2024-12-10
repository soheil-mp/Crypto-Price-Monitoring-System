"""Technical analysis utilities for the Streamlit app."""

import pandas as pd

def calculate_technical_indicators(df, indicators):
    """Calculate technical indicators based on the selected options."""
    try:
        if df.empty:
            return df
            
        # SMA
        if indicators.get('sma'):
            period = indicators['sma_period']
            df[f'SMA_{period}'] = df['price'].rolling(window=period, min_periods=1).mean()

        # EMA
        if indicators.get('ema'):
            period = indicators['ema_period']
            df[f'EMA_{period}'] = df['price'].ewm(span=period, adjust=False, min_periods=1).mean()

        # Bollinger Bands
        if indicators.get('bb'):
            period = indicators['bb_period']
            std_dev = indicators['bb_std']
            df['BB_middle'] = df['price'].rolling(window=period, min_periods=1).mean()
            df['BB_std'] = df['price'].rolling(window=period, min_periods=1).std()
            df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * std_dev)
            df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * std_dev)

        # RSI
        if indicators.get('rsi'):
            period = indicators['rsi_period']
            delta = df['price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            df['RSI'] = df['RSI'].fillna(50)

        # MACD
        if indicators.get('macd'):
            exp1 = df['price'].ewm(span=12, adjust=False, min_periods=1).mean()
            exp2 = df['price'].ewm(span=26, adjust=False, min_periods=1).mean()
            df['MACD'] = exp1 - exp2
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False, min_periods=1).mean()
            df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']

        # VWAP
        if indicators.get('vwap'):
            df['VWAP'] = (df['price'] * df['volume_24h']).cumsum() / df['volume_24h'].cumsum()

        return df
    except Exception as e:
        print(f"Error calculating technical indicators: {str(e)}")
        return df 