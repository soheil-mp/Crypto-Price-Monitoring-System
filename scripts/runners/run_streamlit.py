"""
Runner script for the Streamlit visualization app.
"""
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Run the Streamlit app
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    sys.argv = ["streamlit", "run", 
                str(project_root / "src/visualization/streamlit/streamlit_app.py"),
                "--server.port=8501",
                "--server.address=localhost"]
    sys.exit(stcli.main()) 