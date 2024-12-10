"""Constants for the Streamlit app."""

# Deep Space Theme Colors
COLORS = {
    'background': '#0E1117',  # Dark background
    'background_gradient_start': '#0E1117',  # Dark background start
    'background_gradient_middle': '#161B22',  # Slightly lighter
    'background_gradient_end': '#1F2937',  # Grid color
    'card_bg': 'rgba(30, 30, 30, 0.7)',  # Card background
    'card_bg_hover': 'rgba(40, 40, 40, 0.8)',  # Card hover state
    'primary': '#00D4FF',  # Info/Primary color
    'primary_glow': 'rgba(0, 212, 255, 0.4)',  # Primary glow
    'secondary': '#1F2937',  # Grid color
    'accent': '#FF4B4B',  # Accent color
    'accent_secondary': '#00D4FF',  # Secondary accent
    'accent_tertiary': '#FFA500',  # Warning color
    'price_up': '#00CC96',  # Success color
    'price_down': '#FF4B4B',  # Accent/Error color
    'text': '#FFFFFF',  # White text
    'text_secondary': '#A1A1AA',  # Secondary text
    'grid': '#1F2937',  # Grid lines
    'border': 'rgba(255, 255, 255, 0.1)',  # Border color
    'chart_gradient': 'rgba(0, 212, 255, 0.05)',  # Chart gradient
    'success': '#00CC96',  # Success state
    'warning': '#FFA500',  # Warning state
    'error': '#FF4B4B',  # Error state
    'info': '#00D4FF'  # Info state
}

# Time intervals for data resampling
RESAMPLE_INTERVALS = {
    '1 Minute': '1min',
    '5 Minutes': '5min',
    '15 Minutes': '15min',
    '30 Minutes': '30min',
    '1 Hour': '1H',
    '4 Hours': '4H'
}

# Time range options
TIME_RANGES = {
    'Last Hour': '1H',
    'Last 4 Hours': '4H',
    'Last 12 Hours': '12H',
    'Last 24 Hours': '24H',
    'All Data': 'ALL'
} 