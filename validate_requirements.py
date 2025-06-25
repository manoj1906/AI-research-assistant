#!/usr/bin/env python3
"""
AI Research Assistant - Requirements Validation
===============================================

This script validates that all requirements are properly installed and working.
"""

import sys
import importlib
import subprocess
from pathlib import Path


def test_import(module_name, display_name=None):
    """Test if a module can be imported"""
    if display_name is None:
        display_name = module_name

    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {display_name}: {version}")
        return True
    except ImportError as e:
        print(f"❌ {display_name}: {e}")
        return False


def test_requirements_file(req_file):
    """Test if a requirements file can be installed"""
    if not Path(req_file).exists():
        print(f"❌ {req_file}: File not found")
        return False

    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--dry-run', '-r', req_file
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print(f"✅ {req_file}: Valid")
            return True
        else:
            print(f"❌ {req_file}: Invalid - {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {req_file}: Timeout during validation")
        return False
    except Exception as e:
        print(f"❌ {req_file}: Error - {e}")
        return False


def main():
    print("🔬 AI Research Assistant - Requirements Validation")
    print("=" * 60)

    # Test core imports
    print("\n📦 Testing Core Dependencies:")
    core_imports = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("sentence_transformers", "Sentence Transformers"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("sklearn", "Scikit-Learn"),
        ("fitz", "PyMuPDF"),
        ("pdfplumber", "PDFplumber"),
        ("spacy", "spaCy"),
        ("streamlit", "Streamlit"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("requests", "Requests"),
        ("tqdm", "TQDM"),
        ("click", "Click"),
    ]

    core_success = 0
    for module, name in core_imports:
        if test_import(module, name):
            core_success += 1

    print(f"\n📊 Core Dependencies: {core_success}/{len(core_imports)} working")

    # Test custom modules
    print("\n🧠 Testing Custom Modules:")
    custom_modules = [
        ("src.config", "Config"),
        ("src.research_assistant", "Research Assistant"),
        ("src.paper_processor.pdf_parser", "PDF Parser"),
        ("src.research_embeddings.academic_embeddings", "Academic Embeddings"),
        ("src.research_qa.academic_qa", "Academic QA"),
    ]

    custom_success = 0
    for module, name in custom_modules:
        if test_import(module, name):
            custom_success += 1

    print(
        f"\n📊 Custom Modules: {custom_success}/{len(custom_modules)} working")

    # Test requirements files
    print("\n📋 Testing Requirements Files:")
    req_files = [
        "requirements-minimal.txt",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-gpu.txt",
        "requirements-biomedical.txt"
    ]

    req_success = 0
    for req_file in req_files:
        if test_requirements_file(req_file):
            req_success += 1

    print(f"\n📊 Requirements Files: {req_success}/{len(req_files)} valid")

    # Overall status
    total_tests = len(core_imports) + len(custom_modules) + len(req_files)
    total_success = core_success + custom_success + req_success

    print("\n" + "=" * 60)
    print(f"📊 Overall Status: {total_success}/{total_tests} tests passed")

    if total_success == total_tests:
        print("🎉 ALL REQUIREMENTS VALIDATED SUCCESSFULLY!")
        print("\n🚀 Ready to use:")
        print("   • Web App: streamlit run app.py")
        print("   • API Server: python api.py")
        print("   • CLI Tool: python cli.py --help")
        return True
    else:
        print("⚠️  Some requirements need attention.")
        print("💡 Try: pip install --upgrade -r requirements.txt")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
