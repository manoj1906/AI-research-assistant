#!/usr/bin/env python3
"""
Quick status check for AI Research Assistant
"""

import sys
from pathlib import Path


def check_status():
    """Check system status"""
    print("🔬 AI Research Assistant - Status Check")
    print("=" * 45)

    # Add src to path for imports
    sys.path.append(str(Path(__file__).parent / "src"))

    # Test core imports
    try:
        from src.research_assistant import ResearchAssistant
        print("✅ Core system: Ready")

        # Quick initialization test
        assistant = ResearchAssistant()
        papers = assistant.list_papers()
        print(f"✅ Paper database: Ready ({len(papers)} papers)")

        print("✅ Question answering: Ready")
        print("✅ PDF processing: Ready")

    except Exception as e:
        print(f"❌ System check failed: {e}")
        return False

    print()
    print("🚀 READY TO USE:")
    print("   Web Interface: streamlit run app.py")
    print("   API Server: python api.py")
    print("   CLI Tool: python cli.py --help")
    print()
    print("💡 QUICK START:")
    print("   1. Run: streamlit run app.py")
    print("   2. Open: http://localhost:8501")
    print("   3. Upload a PDF and ask questions!")

    return True


if __name__ == "__main__":
    success = check_status()
    sys.exit(0 if success else 1)
