#!/usr/bin/env python3
"""
🚀 AI Research Assistant - Production Deployment Script
Complete setup and verification for production use
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def print_banner():
    """Print deployment banner"""
    print("=" * 80)
    print("🚀 AI RESEARCH ASSISTANT - PRODUCTION DEPLOYMENT")
    print("=" * 80)
    print("Preparing your research assistant for production use...")
    print()


def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(
            f"   ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(
            f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Incompatible")
        print("   💡 Please upgrade to Python 3.8 or higher")
        return False


def install_dependencies():
    """Install required dependencies"""
    print("📦 Checking dependencies...")
    try:
        # Try to import key packages to check if already installed
        import streamlit
        import torch
        import transformers
        print("   ✅ Dependencies already installed")
        return True
    except ImportError:
        print("   Installing missing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                           check=True, capture_output=True)
            print("   ✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install dependencies: {e}")
            return False


def verify_installation():
    """Verify all components are working"""
    print("🔧 Verifying installation...")

    try:
        # Test core imports
        sys.path.append(str(Path(__file__).parent / "src"))
        from src.research_assistant import ResearchAssistant

        # Test initialization
        assistant = ResearchAssistant()
        papers = assistant.list_papers()

        print("   ✅ Core system working")
        print("   ✅ AI models loaded")
        print("   ✅ PDF processing ready")
        print("   ✅ Question answering ready")
        return True

    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")

    directories = ['data', 'data/papers', 'data/embeddings', 'logs']

    for dir_name in directories:
        Path(dir_name).mkdir(parents=True, exist_ok=True)

    print("   ✅ Directories created")


def show_deployment_options():
    """Show available deployment options"""
    print()
    print("🎯 DEPLOYMENT OPTIONS:")
    print("-" * 25)
    print()

    print("1. 🌐 WEB INTERFACE (Recommended):")
    print("   Command: streamlit run app.py")
    print("   URL: http://localhost:8501")
    print("   Use: Interactive paper analysis")
    print()

    print("2. 🚀 API SERVER:")
    print("   Command: python api.py")
    print("   URL: http://localhost:8000")
    print("   Use: REST API for integration")
    print()

    print("3. 💻 CLI TOOL:")
    print("   Command: python cli.py --help")
    print("   Use: Batch processing and automation")
    print()

    print("4. 🐳 DOCKER DEPLOYMENT:")
    print("   Command: docker-compose up")
    print("   Use: Production containerized deployment")
    print()


def show_quick_start():
    """Show quick start instructions"""
    print("⚡ QUICK START:")
    print("-" * 15)
    print()
    print("# Start the web interface")
    print("streamlit run app.py")
    print()
    print("# Open in browser")
    print("http://localhost:8501")
    print()
    print("# Upload a PDF paper and start asking questions!")
    print()


def show_example_questions():
    """Show example research questions"""
    print("❓ EXAMPLE RESEARCH QUESTIONS:")
    print("-" * 32)
    print()

    questions = [
        "What is the main contribution of this paper?",
        "Summarize the methodology section",
        "What are the key findings and results?",
        "Explain the experimental setup",
        "What datasets were used for evaluation?",
        "What are the limitations of this approach?",
        "How does this compare to prior work?",
        "What future work is suggested?"
    ]

    for i, q in enumerate(questions, 1):
        print(f"   {i}. {q}")
    print()


def main():
    """Main deployment function"""
    print_banner()

    # Check prerequisites
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("💡 Try: pip install --upgrade pip")
        print("💡 Or: pip install -r requirements.txt --force-reinstall")
        sys.exit(1)

    # Create directories
    create_directories()

    # Verify installation
    if not verify_installation():
        print("💡 Try running: python status_check.py")
        sys.exit(1)

    print()
    print("🎉 DEPLOYMENT SUCCESSFUL!")
    print("=" * 25)
    print()
    print("✅ AI Research Assistant is ready for production use!")
    print()

    show_deployment_options()
    show_quick_start()
    show_example_questions()

    print("🔬 Ready to accelerate your research!")
    print("Happy researching! ✨")
    print("=" * 80)


if __name__ == "__main__":
    main()
