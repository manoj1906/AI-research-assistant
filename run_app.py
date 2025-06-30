#!/usr/bin/env python3
"""
Launch script for AI Research Assistant
Handles environment setup and graceful error handling
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import streamlit
        import torch
        import numpy
        import pandas
        logger.info("✅ Core dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def run_app():
    """Run the Streamlit app with proper error handling"""
    if not check_dependencies():
        logger.error("Dependencies missing. Please run: pip install -r requirements.txt")
        return False
    
    try:
        # Change to app directory
        app_dir = Path(__file__).parent
        os.chdir(app_dir)
        
        # Run streamlit app
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"]
        logger.info("🚀 Starting AI Research Assistant...")
        logger.info("📊 App will be available at: http://localhost:8501")
        
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
        
    except KeyboardInterrupt:
        logger.info("🛑 App stopped by user")
        return True
    except Exception as e:
        logger.error(f"❌ Error running app: {e}")
        return False

if __name__ == "__main__":
    success = run_app()
    sys.exit(0 if success else 1)
