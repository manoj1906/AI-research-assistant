#!/usr/bin/env python3
"""
Simple launcher for AI Research Assistant Web Interface
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit web interface"""
    print("🔬 AI Research Assistant - Starting Web Interface")
    print("=" * 50)
    print("🌐 Launching at: http://localhost:8501")
    print("📄 Upload PDFs and ask research questions!")
    print("=" * 50)

    # Get the path to app.py
    app_path = Path(__file__).parent / "app.py"

    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(app_path),
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down AI Research Assistant...")
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        print("💡 Try: streamlit run app.py")


if __name__ == "__main__":
    main()
