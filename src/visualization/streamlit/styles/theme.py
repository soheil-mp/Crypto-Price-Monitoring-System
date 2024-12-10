"""Theme and styling for the Streamlit app."""

from src.visualization.streamlit.config.constants import COLORS

def get_css_style():
    """Returns the CSS styling for the app."""
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Main app styling with enhanced cosmic background */
        .stApp {{
            font-family: 'Inter', sans-serif;
            background: radial-gradient(circle at top right, 
                {COLORS['background_gradient_start']} 0%,
                {COLORS['background_gradient_middle']} 35%,
                {COLORS['background_gradient_end']} 70%,
                {COLORS['background']} 100%
            );
            position: relative;
            overflow: hidden;
        }}
        
        /* Enhanced cosmic particles with better visibility */
        .stApp::before {{
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            top: -50%;
            left: -50%;
            z-index: 0;
            background-image: 
                radial-gradient(circle at center, {COLORS['primary_glow']} 0.05%, transparent 0.3%),
                radial-gradient(circle at center, {COLORS['accent']} 0.05%, transparent 0.2%),
                radial-gradient(circle at center, {COLORS['accent_secondary']} 0.05%, transparent 0.25%);
            background-size: 150px 150px, 200px 200px, 120px 120px;
            animation: particles 30s linear infinite;
            opacity: 0.15;
        }}

        @keyframes particles {{
            0% {{ transform: rotate(0deg) scale(1); }}
            50% {{ transform: rotate(180deg) scale(1.1); }}
            100% {{ transform: rotate(360deg) scale(1); }}
        }}
        
        /* Enhanced gradient overlay */
        .stApp::after {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                125deg,
                transparent 0%,
                rgba(107, 62, 239, 0.015) 25%,
                transparent 50%,
                rgba(224, 30, 219, 0.015) 75%,
                transparent 100%
            );
            z-index: 1;
            pointer-events: none;
            animation: gradient-shift 25s ease infinite;
            backdrop-filter: blur(150px);
        }}

        @keyframes gradient-shift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        /* Ensure content stays above effects */
        .stApp > * {{
            position: relative;
            z-index: 2;
        }}
        
        /* Ultra-modern card styling with advanced glassmorphism */
        .css-1kyxreq, .css-1adrfps {{
            background: linear-gradient(135deg, 
                rgba(8, 12, 28, 0.4),
                rgba(12, 18, 40, 0.2)
            );
            border-radius: 24px;
            padding: 1.5rem;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(107, 62, 239, 0.08);
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.3),
                inset 0 0 32px rgba(107, 62, 239, 0.03);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}

        /* Card hover effects */
        .css-1kyxreq::before, .css-1adrfps::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(107, 62, 239, 0.1),
                transparent
            );
            transition: 0.5s;
        }}

        .css-1kyxreq:hover::before, .css-1adrfps:hover::before {{
            left: 100%;
        }}
        
        /* Enhanced metric cards with dramatic effects */
        .stMetric {{
            background: linear-gradient(135deg,
                rgba(8, 12, 28, 0.4),
                rgba(12, 18, 40, 0.2)
            );
            border-radius: 24px;
            padding: 1.5rem;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(107, 62, 239, 0.08);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.3),
                inset 0 0 32px rgba(107, 62, 239, 0.03);
            position: relative;
            overflow: hidden;
        }}

        /* Metric card hover effects */
        .stMetric:hover {{
            transform: translateY(-4px) scale(1.02);
            box-shadow: 
                0 12px 40px rgba(107, 62, 239, 0.1),
                inset 0 0 32px rgba(107, 62, 239, 0.05);
            border-color: {COLORS['primary']};
        }}
        
        /* Text styling */
        h1, h2, h3 {{
            background: linear-gradient(135deg, 
                {COLORS['text']} 0%, 
                {COLORS['text_secondary']} 50%,
                {COLORS['accent_secondary']} 100%
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-shadow: 
                0 0 20px rgba(107, 62, 239, 0.2),
                0 0 40px rgba(107, 62, 239, 0.1),
                0 0 60px rgba(107, 62, 239, 0.05);
            position: relative;
        }}

        /* Tab styling */
        .stTabs [data-baseweb="tab"] {{
            background: linear-gradient(135deg,
                rgba(8, 12, 28, 0.3),
                rgba(12, 18, 40, 0.2)
            );
            border-radius: 12px;
            padding: 12px 24px;
            color: {COLORS['text_secondary']};
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid transparent;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background: linear-gradient(135deg,
                rgba(12, 18, 40, 0.4),
                rgba(16, 24, 50, 0.3)
            );
            border-color: rgba(107, 62, 239, 0.1);
            color: {COLORS['text']};
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg,
                rgba(107, 62, 239, 0.1),
                rgba(107, 62, 239, 0.05)
            ) !important;
            border-color: rgba(107, 62, 239, 0.2) !important;
            color: {COLORS['primary']} !important;
        }}

        /* Button styling */
        .stButton button {{
            background: linear-gradient(135deg,
                {COLORS['primary']},
                {COLORS['accent']}
            );
            color: {COLORS['text']};
            border: none;
            border-radius: 12px;
            padding: 0.8rem 1.6rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
            box-shadow: 
                0 4px 20px rgba(107, 62, 239, 0.2),
                inset 0 0 20px rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
        }}

        .stButton button:hover {{
            transform: translateY(-2px);
            box-shadow: 
                0 8px 25px rgba(107, 62, 239, 0.3),
                inset 0 0 20px rgba(255, 255, 255, 0.2);
        }}

        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: {COLORS['background']};
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg,
                {COLORS['primary']},
                {COLORS['accent']}
            );
            border-radius: 4px;
            border: 2px solid {COLORS['background']};
        }}

        /* Loading animation */
        .stProgress > div > div > div > div {{
            background: linear-gradient(135deg,
                {COLORS['primary']},
                {COLORS['accent']},
                {COLORS['accent_secondary']}
            ) !important;
            background-size: 200% 200% !important;
            animation: loading 2s ease infinite !important;
        }}

        @keyframes loading {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        /* Selectbox styling */
        .stSelectbox [data-baseweb="select"] {{
            background: linear-gradient(135deg,
                rgba(8, 12, 28, 0.4),
                rgba(12, 18, 40, 0.2)
            );
            border-radius: 12px;
            border: 1px solid rgba(107, 62, 239, 0.08);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }}

        .stSelectbox [data-baseweb="select"]:hover {{
            border-color: rgba(107, 62, 239, 0.2);
            box-shadow: 0 4px 20px rgba(107, 62, 239, 0.1);
        }}

        /* Radio buttons */
        .stRadio [data-baseweb="radio"] {{
            color: {COLORS['text_secondary']};
        }}

        .stRadio [data-baseweb="radio"]:hover {{
            color: {COLORS['text']};
        }}

        /* Checkbox */
        .stCheckbox [data-baseweb="checkbox"] {{
            color: {COLORS['text_secondary']};
        }}

        .stCheckbox [data-baseweb="checkbox"]:hover {{
            color: {COLORS['text']};
        }}
    </style>
    """ 