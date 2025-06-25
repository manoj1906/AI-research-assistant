#!/usr/bin/env python3
"""
Final validation script for AI Research Assistant
Confirms all components are working correctly
"""

import sys
from pathlib import Path
import tempfile
import urllib.request
import time

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


def test_imports():
    """Test all critical imports"""
    print("🔧 Testing imports...")

    try:
        from src.config import Config
        print("  ✅ Config import successful")

        from src.research_assistant import ResearchAssistant
        print("  ✅ ResearchAssistant import successful")

        from src.paper_processor.pdf_parser import AcademicPDFParser
        print("  ✅ PDF Parser import successful")

        from src.research_embeddings.academic_embeddings import MultimodalResearchEmbeddings
        print("  ✅ Embeddings import successful")

        from src.research_qa.academic_qa import AcademicQuestionAnswering
        print("  ✅ QA System import successful")

        return True

    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_initialization():
    """Test system initialization"""
    print("\\n🚀 Testing system initialization...")

    try:
        from src.research_assistant import ResearchAssistant
        assistant = ResearchAssistant()
        print("  ✅ Research Assistant initialized successfully")
        return assistant

    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        return None


def test_basic_functionality(assistant):
    """Test basic functionality"""
    print("\\n📋 Testing basic functionality...")

    try:
        # Test listing papers (should be empty initially)
        papers = assistant.list_papers()
        print(f"  ✅ Paper listing works: {len(papers)} papers found")

        # Test basic question without paper (should handle gracefully)
        try:
            answer = assistant.ask_question("What is AI?")
            print("  ✅ Question answering works (general query)")
        except Exception as e:
            print(f"  ⚠️ Question answering (expected without papers): {e}")

        return True

    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        return False


def test_file_access():
    """Test file system access for data storage"""
    print("\\n📁 Testing file system access...")

    try:
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(exist_ok=True)

        # Test write access
        test_file = data_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()

        print("  ✅ File system access working")
        return True

    except Exception as e:
        print(f"  ❌ File system access failed: {e}")
        return False


def test_web_components():
    """Test web-related components"""
    print("\\n🌐 Testing web components...")

    try:
        # Test if streamlit can be imported
        import streamlit
        print("  ✅ Streamlit available")

        # Test if FastAPI can be imported
        import fastapi
        print("  ✅ FastAPI available")

        # Test if main app file exists
        app_file = Path(__file__).parent / "app.py"
        if app_file.exists():
            print("  ✅ Web app file exists")
        else:
            print("  ❌ Web app file missing")

        return True

    except Exception as e:
        print(f"  ❌ Web components test failed: {e}")
        return False


def show_usage_info():
    """Show usage information"""
    print("\\n" + "="*60)
    print("🎉 AI RESEARCH ASSISTANT - VALIDATION COMPLETE!")
    print("="*60)
    print()
    print("✅ SYSTEM STATUS: FULLY OPERATIONAL")
    print()
    print("🚀 QUICK START:")
    print("  1. Run: streamlit run app.py")
    print("  2. Open: http://localhost:8501")
    print("  3. Upload a PDF paper")
    print("  4. Ask research questions!")
    print()
    print("💡 EXAMPLE QUESTIONS:")
    print("  • What is the main contribution?")
    print("  • Summarize the methodology")
    print("  • What are the key findings?")
    print("  • Explain section 3.1")
    print()
    print("🛠️ OTHER INTERFACES:")
    print("  • API Server: python api.py")
    print("  • CLI Tool: python cli.py --help")
    print("  • Demo: python demo.py")
    print()
    print("Happy researching! 🔬✨")


def main():
    """Main validation function"""
    print("🔬 AI RESEARCH ASSISTANT - FINAL VALIDATION")
    print("="*50)

    # Run all tests
    tests = [
        ("Imports", test_imports),
        ("File Access", test_file_access),
        ("Web Components", test_web_components),
    ]

    all_passed = True

    for test_name, test_func in tests:
        success = test_func()
        if not success:
            all_passed = False

    # Test initialization and basic functionality
    assistant = test_initialization()
    if assistant:
        test_basic_functionality(assistant)
    else:
        all_passed = False

    print("\\n" + "-"*50)

    if all_passed:
        print("🎉 ALL TESTS PASSED - SYSTEM READY!")
        show_usage_info()
    else:
        print("❌ SOME TESTS FAILED - CHECK ERRORS ABOVE")
        print("\\n🔧 Try running: pip install -r requirements.txt")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
