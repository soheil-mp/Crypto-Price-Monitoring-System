"""Main Streamlit application file."""

import streamlit as st
import pandas as pd

# Set page config first
st.set_page_config(layout="wide", page_title="Crypto Analytics", page_icon="📈")

# Import local modules
from src.visualization.streamlit.config.constants import RESAMPLE_INTERVALS, TIME_RANGES, COLORS
from src.visualization.streamlit.styles.theme import get_css_style
from src.visualization.streamlit.utils.data_processing import load_data, process_data, calculate_statistics
from src.visualization.streamlit.utils.technical_analysis import calculate_technical_indicators
from src.visualization.streamlit.components.charts import (
    create_price_chart,
    create_rsi_chart,
    create_macd_chart,
    create_volume_chart
)
from src.visualization.streamlit.components.metrics import display_key_metrics, display_detailed_stats, inject_custom_css

# Apply custom styling
st.markdown(get_css_style(), unsafe_allow_html=True)
inject_custom_css()

# Load initial data
df = load_data()

# Verify we have data
if df.empty:
    st.error("No data available for analysis.")
    st.stop()

# Sidebar
with st.sidebar:
    st.title('💹 Trading Dashboard')
    st.markdown("---")
    
    # Cryptocurrency selection
    st.subheader('🎯 Select Asset')
    try:
        available_cryptos = sorted(df['symbol'].unique())
        if not available_cryptos:
            st.error("No cryptocurrencies found in the data.")
            st.stop()
    except KeyError:
        st.error("Error: 'symbol' column not found in the data.")
        st.stop()
        
    selected_crypto = st.selectbox(
        'Choose Cryptocurrency',
        available_cryptos,
        index=0,
        format_func=lambda x: f"📊 {x}"
    )
    
    st.markdown("---")
    
    # Time range selection
    st.subheader('⏰ Time Frame')
    selected_time_range = st.radio(
        'Select Time Range',
        list(TIME_RANGES.keys()),
        format_func=lambda x: f"🕒 {x}"
    )
    
    # Add resampling interval selection
    st.markdown("---")
    st.subheader('📊 Data Resolution')
    selected_interval = st.select_slider(
        'Select Data Interval',
        options=list(RESAMPLE_INTERVALS.keys()),
        value='5 Minutes'
    )
    
    st.markdown("---")
    
    # Technical Analysis section with tabs
    st.subheader('📊 Technical Analysis')
    indicator_tabs = st.tabs([
        "📈 Trend", 
        "🔄 Momentum", 
        "📊 Volatility",
        "💹 Volume"
    ])

    # Collect all indicator settings
    indicators = {}
    
    # Trend Indicators Tab
    with indicator_tabs[0]:
        st.caption("Trend Following Indicators")
        indicators['sma'] = st.checkbox('SMA', value=False)
        if indicators['sma']:
            indicators['sma_period'] = st.slider('Period', 5, 200, 50)
        
        indicators['ema'] = st.checkbox('EMA', value=False)
        if indicators['ema']:
            indicators['ema_period'] = st.slider('Period', 5, 200, 20)

    # Momentum Indicators Tab
    with indicator_tabs[1]:
        st.caption("Momentum Indicators")
        indicators['rsi'] = st.checkbox('RSI', value=False)
        if indicators['rsi']:
            indicators['rsi_period'] = st.slider('Period', 5, 50, 14)
        
        indicators['macd'] = st.checkbox('MACD', value=False)
        if indicators['macd']:
            st.info('Using (12, 26, 9)')

    # Volatility Indicators Tab
    with indicator_tabs[2]:
        st.caption("Volatility Indicators")
        indicators['bb'] = st.checkbox('Bollinger Bands', value=False)
        if indicators['bb']:
            indicators['bb_period'] = st.slider('Period', 5, 50, 20)
            indicators['bb_std'] = st.slider('Std Dev', 1, 4, 2)

    # Volume Analysis Tab
    with indicator_tabs[3]:
        st.caption("Volume Analysis")
        indicators['volume'] = st.checkbox('Volume', value=False)
        indicators['vwap'] = st.checkbox('VWAP', value=False)

    # Add scale selector
    st.markdown("---")
    st.subheader('📊 Chart Settings')
    scale_type = st.radio(
        'Price Scale',
        ['Linear', 'Logarithmic'],
        format_func=lambda x: f"📐 {x}",
        help="Logarithmic scale helps visualize price changes when values are close together"
    )

# Process the data
filtered_df = process_data(df, selected_crypto, selected_time_range, selected_interval)

# Calculate technical indicators
filtered_df = calculate_technical_indicators(filtered_df, indicators)

# Calculate statistics
stats = calculate_statistics(filtered_df)

# Main content area
st.title(f'📈 {selected_crypto} Analytics')

# Display key metrics
display_key_metrics(stats)

# Add spacing
st.markdown("<br>", unsafe_allow_html=True)

# Create tabs for different chart views
chart_tabs = st.tabs(["📊 Price", "📈 Technical", "📉 Analysis"])

with chart_tabs[0]:
    # Create and display main price chart
    fig = create_price_chart(filtered_df, indicators, selected_crypto, scale_type)
    st.plotly_chart(fig, use_container_width=True)

with chart_tabs[1]:
    if indicators.get('rsi') or indicators.get('macd'):
        if indicators.get('rsi'):
            rsi_fig = create_rsi_chart(filtered_df, indicators['rsi_period'])
            st.plotly_chart(rsi_fig, use_container_width=True)
        
        if indicators.get('macd'):
            macd_fig = create_macd_chart(filtered_df)
            st.plotly_chart(macd_fig, use_container_width=True)
    else:
        st.info("Select technical indicators from the sidebar to display analysis charts.")

with chart_tabs[2]:
    if indicators.get('volume'):
        volume_fig = create_volume_chart(filtered_df, selected_crypto)
        st.plotly_chart(volume_fig, use_container_width=True)

# Display detailed statistics
display_detailed_stats(stats, filtered_df, indicators)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Made with ❤️ by Your Crypto Assistant | Data updates every minute</p>
    </div>
""", unsafe_allow_html=True)
