#!/usr/bin/env python3
"""
Production launcher for AI Research Assistant
Optimized for reliability and performance
"""

import os
import sys
import subprocess
from pathlib import Path
import logging

# Suppress warnings for cleaner output
logging.basicConfig(level=logging.ERROR)
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'


def print_banner():
    """Print startup banner"""
    print("=" * 80)
    print("🔬 AI RESEARCH ASSISTANT - PRODUCTION LAUNCHER")
    print("=" * 80)
    print("🚀 Starting optimized research assistant...")
    print()


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'streamlit': 'streamlit',
        'torch': 'torch',
        'transformers': 'transformers',
        'sentence-transformers': 'sentence_transformers',
        'PyMuPDF': 'fitz',  # PyMuPDF imports as fitz
        'pandas': 'pandas'
    }

    missing = []
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)

    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("💡 Run: pip install -r requirements.txt")
        return False

    return True


def launch_web_app():
    """Launch the Streamlit web application"""
    print("🌐 Launching web interface...")
    print("📱 Access URL: http://localhost:8501")
    print("🔗 The app will open automatically in your browser")
    print()
    print("✨ Features ready:")
    print("   📄 Upload academic PDF papers")
    print("   ❓ Ask intelligent research questions")
    print("   📊 Get evidence-based answers")
    print("   🔍 Search across multiple papers")
    print()
    print("⏳ Starting application... (this may take a moment)")
    print("-" * 40)

    try:
        # Launch streamlit with optimized settings
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false",
            "--logger.level", "error"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Application stopped")
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        return False

    return True


def launch_api_server():
    """Launch the FastAPI server"""
    print("🚀 Launching API server...")
    print("🔗 API URL: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print()

    try:
        subprocess.run([
            sys.executable, "api.py"
        ])
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")
    except Exception as e:
        print(f"❌ Error launching API: {e}")
        return False

    return True


def show_options():
    """Show available options"""
    print("🎯 Choose launch option:")
    print("  1. 🌐 Web Interface (Recommended)")
    print("  2. 🚀 API Server")
    print("  3. 💻 CLI Help")
    print("  4. 📊 System Info")
    print("  5. 🧪 Run Tests")
    print("  0. ❌ Exit")
    print()


def show_cli_help():
    """Show CLI usage help"""
    print("💻 COMMAND LINE INTERFACE")
    print("-" * 30)
    print("Usage: python cli.py [command] [options]")
    print()
    print("Commands:")
    print("  upload    Upload and process a paper")
    print("  ask       Ask a question about papers")
    print("  list      List uploaded papers")
    print("  analyze   Analyze paper contributions")
    print("  web       Launch web interface")
    print()
    print("Examples:")
    print("  python cli.py upload paper.pdf")
    print("  python cli.py ask 'What is the main contribution?'")
    print("  python cli.py list")
    print()


def show_system_info():
    """Show system information"""
    print("📊 SYSTEM INFORMATION")
    print("-" * 25)

    # Python version
    print(f"🐍 Python: {sys.version.split()[0]}")

    # Key packages
    packages = ['torch', 'transformers', 'streamlit', 'sentence_transformers']
    for pkg in packages:
        try:
            module = __import__(pkg.replace('-', '_'))
            version = getattr(module, '__version__', 'unknown')
            print(f"📦 {pkg}: {version}")
        except ImportError:
            print(f"❌ {pkg}: not installed")

    # System resources
    import psutil
    print(f"💾 RAM: {psutil.virtual_memory().total // (1024**3)} GB")
    print(f"🖥️  CPU: {psutil.cpu_count()} cores")

    # GPU info
    try:
        import torch
        if torch.cuda.is_available():
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("🖥️  GPU: Not available (using CPU)")
    except:
        print("🖥️  GPU: Cannot detect")


def run_tests():
    """Run system tests"""
    print("🧪 RUNNING SYSTEM TESTS")
    print("-" * 25)

    try:
        result = subprocess.run([
            sys.executable, "test_robust.py"
        ], capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main launcher function"""
    print_banner()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    while True:
        show_options()

        try:
            choice = input("👉 Enter your choice (0-5): ").strip()

            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                launch_web_app()
            elif choice == '2':
                launch_api_server()
            elif choice == '3':
                show_cli_help()
            elif choice == '4':
                show_system_info()
            elif choice == '5':
                run_tests()
            else:
                print("❌ Invalid choice. Please enter 0-5.")

            print()

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
