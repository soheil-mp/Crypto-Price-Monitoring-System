"""Metrics components for the Streamlit app."""

import streamlit as st
from src.visualization.streamlit.config.constants import COLORS

def inject_custom_css():
    """Inject custom CSS for metrics components."""
    st.markdown("""
        <style>
            @keyframes pulse {
                0% { transform: scale(1); opacity: 0.5; }
                50% { transform: scale(1.05); opacity: 0.7; }
                100% { transform: scale(1); opacity: 0.5; }
            }
            
            @keyframes blink {
                0% { opacity: 0.5; }
                50% { opacity: 1; }
                100% { opacity: 0.5; }
            }
            
            @keyframes shine {
                0% { transform: translateX(-100%); }
                50% { transform: translateX(100%); }
                100% { transform: translateX(-100%); }
            }
            
            .metric-card {
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
            }
            
            .pulse-effect {
                animation: pulse 2s ease-in-out infinite;
            }
            
            .blink-effect {
                animation: blink 2s ease-in-out infinite;
            }
            
            .shine-effect {
                animation: shine 3s ease-in-out infinite;
            }
        </style>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, prefix="$", suffix=""):
    """Create a styled metric card with gaming-inspired design."""
    return f"""
        <div class="metric-card" style='
            background: linear-gradient(145deg, {COLORS['card_bg']}, rgba(40, 40, 40, 0.4));
            padding: 1.2rem;
            border-radius: 16px;
            border: 1px solid {COLORS['border']};
            margin: 5px 0;
            box-shadow: 
                0 4px 20px rgba(0, 0, 0, 0.2),
                inset 0 0 20px rgba(0, 212, 255, 0.05);
            height: 100%;
            font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        '>
            <div class="shine-effect" style='
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg,
                    transparent 0%,
                    {COLORS['accent_secondary']}10 45%,
                    transparent 100%
                );
            '></div>
            <div style='position: relative; z-index: 1;'>
                <p style='
                    color: {COLORS['text_secondary']};
                    margin: 0;
                    font-size: 0.7rem;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                    opacity: 0.9;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                '>
                    <span class="blink-effect" style='
                        display: inline-block;
                        width: 6px;
                        height: 6px;
                        background: {COLORS['accent_secondary']};
                        border-radius: 50%;
                        box-shadow: 0 0 10px {COLORS['accent_secondary']};
                    '></span>
                    {title}
                </p>
                <h3 style='
                    margin: 0.4rem 0 0 0;
                    color: {COLORS['text']};
                    font-size: 1.1rem;
                    font-weight: 600;
                    letter-spacing: 0.02em;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    line-height: 1.4;
                    text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
                '>{prefix}{value:,.2f}{suffix}</h3>
            </div>
        </div>
    """

def display_key_metrics(stats):
    """Display the key metrics in the top row with enhanced styling."""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="metric-card" style='
                background: linear-gradient(145deg, {COLORS['card_bg']}, rgba(40, 40, 40, 0.4));
                padding: 1.8rem;
                border-radius: 20px;
                border: 1px solid {COLORS['border']};
                font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                box-shadow: 
                    0 4px 20px rgba(0, 0, 0, 0.2),
                    inset 0 0 20px rgba(0, 212, 255, 0.05);
                position: relative;
                overflow: hidden;
            '>
                <div class="pulse-effect" style='
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: radial-gradient(circle at center, 
                        {COLORS['info']}20 0%,
                        transparent 70%);
                    opacity: 0.5;
                '></div>
                <div style='position: relative; z-index: 1;'>
                    <div style='
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        margin-bottom: 0.8rem;
                    '>
                        <span class="blink-effect" style='
                            display: inline-block;
                            width: 8px;
                            height: 8px;
                            background: {COLORS['info']};
                            border-radius: 50%;
                            box-shadow: 0 0 10px {COLORS['info']};
                        '></span>
                        <h3 style='
                            margin: 0;
                            color: {COLORS['info']};
                            font-size: 0.85rem;
                            font-weight: 500;
                            letter-spacing: 0.08em;
                            text-transform: uppercase;
                            opacity: 0.9;
                        '>Current Price</h3>
                    </div>
                    <p style='
                        font-size: 1.75rem;
                        margin: 0;
                        font-weight: 600;
                        letter-spacing: -0.02em;
                        line-height: 1.2;
                        color: {COLORS['text']};
                        text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
                    '>${stats['current_price']:,.2f}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        color = COLORS['success'] if stats['price_change_pct'] >= 0 else COLORS['error']
        glow_color = COLORS['success'] if stats['price_change_pct'] >= 0 else COLORS['error']
        st.markdown(f"""
            <div class="metric-card" style='
                background: linear-gradient(145deg, {COLORS['card_bg']}, rgba(40, 40, 40, 0.4));
                padding: 1.8rem;
                border-radius: 20px;
                border: 1px solid {COLORS['border']};
                font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                box-shadow: 
                    0 4px 20px rgba(0, 0, 0, 0.2),
                    inset 0 0 20px {glow_color}10;
                position: relative;
                overflow: hidden;
            '>
                <div style='position: relative; z-index: 1;'>
                    <div style='
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        margin-bottom: 0.8rem;
                    '>
                        <span class="blink-effect" style='
                            display: inline-block;
                            width: 8px;
                            height: 8px;
                            background: {color};
                            border-radius: 50%;
                            box-shadow: 0 0 10px {color};
                        '></span>
                        <h3 style='
                            margin: 0;
                            color: {color};
                            font-size: 0.85rem;
                            font-weight: 500;
                            letter-spacing: 0.08em;
                            text-transform: uppercase;
                            opacity: 0.9;
                        '>Price Change</h3>
                    </div>
                    <p style='
                        font-size: 1.75rem;
                        margin: 0;
                        font-weight: 600;
                        letter-spacing: -0.02em;
                        line-height: 1.2;
                        color: {color};
                        text-shadow: 0 0 20px {color}50;
                    '>{stats['price_change_pct']:+.2f}%</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card" style='
                background: linear-gradient(145deg, {COLORS['card_bg']}, rgba(40, 40, 40, 0.4));
                padding: 1.8rem;
                border-radius: 20px;
                border: 1px solid {COLORS['border']};
                font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                box-shadow: 
                    0 4px 20px rgba(0, 0, 0, 0.2),
                    inset 0 0 20px rgba(0, 212, 255, 0.05);
                position: relative;
                overflow: hidden;
            '>
                <div class="shine-effect" style='
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(45deg,
                        transparent 0%,
                        {COLORS['accent_secondary']}10 45%,
                        transparent 100%
                    );
                '></div>
                <div style='position: relative; z-index: 1;'>
                    <div style='
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        margin-bottom: 0.8rem;
                    '>
                        <span class="blink-effect" style='
                            display: inline-block;
                            width: 8px;
                            height: 8px;
                            background: {COLORS['accent_secondary']};
                            border-radius: 50%;
                            box-shadow: 0 0 10px {COLORS['accent_secondary']};
                        '></span>
                        <h3 style='
                            margin: 0;
                            color: {COLORS['accent_secondary']};
                            font-size: 0.85rem;
                            font-weight: 500;
                            letter-spacing: 0.08em;
                            text-transform: uppercase;
                            opacity: 0.9;
                        '>24h Volume</h3>
                    </div>
                    <p style='
                        font-size: 1.75rem;
                        margin: 0;
                        font-weight: 600;
                        letter-spacing: -0.02em;
                        line-height: 1.2;
                        color: {COLORS['text']};
                        text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
                    '>${stats['avg_volume']:,.0f}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

def display_detailed_stats(stats, filtered_df, indicators):
    """Display detailed statistics in a single row layout with enhanced styling."""
    st.markdown(f"""
        <div style='
            padding: 1.5rem 0;
            border-top: 1px solid {COLORS['border']};
            border-bottom: 1px solid {COLORS['border']};
            margin: 2rem 0 1.5rem 0;
            background: linear-gradient(90deg,
                transparent 0%,
                {COLORS['accent_secondary']}05 50%,
                transparent 100%
            );
        '>
            <h2 style='
                font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 1.5rem;
                font-weight: 600;
                letter-spacing: -0.02em;
                margin: 0;
                color: {COLORS['text']};
                display: flex;
                align-items: center;
                gap: 0.8rem;
            '>
                <span style='
                    color: {COLORS['accent_secondary']};
                    text-shadow: 0 0 10px {COLORS['accent_secondary']};
                '>📊</span>
                <span style='
                    background: linear-gradient(90deg, {COLORS['text']}, {COLORS['accent_secondary']});
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    text-shadow: 0 0 20px {COLORS['accent_secondary']}30;
                '>Detailed Statistics</span>
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # Calculate the number of metrics to display
    num_metrics = 8  # Base metrics
    if indicators.get('rsi'): num_metrics += 1
    if indicators.get('macd'): num_metrics += 1
    if indicators.get('sma'): num_metrics += 1
    if indicators.get('ema'): num_metrics += 1

    cols = st.columns(num_metrics)
    current_idx = 0

    # Price metrics
    with cols[current_idx]:
        st.markdown(create_metric_card("High", stats['max_price']), unsafe_allow_html=True)
    current_idx += 1

    with cols[current_idx]:
        st.markdown(create_metric_card("Low", stats['min_price']), unsafe_allow_html=True)
    current_idx += 1

    with cols[current_idx]:
        st.markdown(create_metric_card("Average", stats['avg_price']), unsafe_allow_html=True)
    current_idx += 1

    with cols[current_idx]:
        st.markdown(create_metric_card("Range", stats['price_range']), unsafe_allow_html=True)
    current_idx += 1

    with cols[current_idx]:
        st.markdown(create_metric_card("Std Dev", stats['std_dev']), unsafe_allow_html=True)
    current_idx += 1

    with cols[current_idx]:
        st.markdown(create_metric_card("Volatility", stats['price_volatility'], prefix="", suffix="%"), unsafe_allow_html=True)
    current_idx += 1

    with cols[current_idx]:
        st.markdown(create_metric_card("Skewness", stats['skewness'], prefix=""), unsafe_allow_html=True)
    current_idx += 1

    with cols[current_idx]:
        st.markdown(create_metric_card("Kurtosis", stats['kurtosis'], prefix=""), unsafe_allow_html=True)
    current_idx += 1

    # Technical indicators
    if indicators.get('rsi'):
        with cols[current_idx]:
            st.markdown(create_metric_card("RSI", filtered_df['RSI'].iloc[-1], prefix=""), unsafe_allow_html=True)
        current_idx += 1

    if indicators.get('macd'):
        with cols[current_idx]:
            st.markdown(create_metric_card("MACD", filtered_df['MACD'].iloc[-1], prefix=""), unsafe_allow_html=True)
        current_idx += 1

    if indicators.get('sma'):
        with cols[current_idx]:
            st.markdown(create_metric_card(f"SMA{indicators['sma_period']}", filtered_df[f'SMA_{indicators["sma_period"]}'].iloc[-1]), unsafe_allow_html=True)
        current_idx += 1

    if indicators.get('ema'):
        with cols[current_idx]:
            st.markdown(create_metric_card(f"EMA{indicators['ema_period']}", filtered_df[f'EMA_{indicators["ema_period"]}'].iloc[-1]), unsafe_allow_html=True)