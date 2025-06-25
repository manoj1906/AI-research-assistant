#!/usr/bin/env python3
"""
AI Research Assistant - Smart Setup Script
Automatically installs the right dependencies based on your needs
"""

import subprocess
import sys
import platform
from pathlib import Path


def print_banner():
    """Print setup banner"""
    print("=" * 70)
    print("🔬 AI RESEARCH ASSISTANT - SMART SETUP")
    print("=" * 70)
    print("This script will help you install the right dependencies")
    print("for your specific use case and system configuration.")
    print()


def detect_system():
    """Detect system configuration"""
    print("🔍 Detecting system configuration...")

    system_info = {
        'os': platform.system(),
        'arch': platform.machine(),
        'python': sys.version_info,
        'has_cuda': False,
        'is_gpu': False
    }

    # Check for CUDA availability
    try:
        import torch
        system_info['has_cuda'] = torch.cuda.is_available()
        system_info['is_gpu'] = torch.cuda.device_count() > 0
    except ImportError:
        pass

    print(f"   OS: {system_info['os']} ({system_info['arch']})")
    print(
        f"   Python: {system_info['python'].major}.{system_info['python'].minor}.{system_info['python'].micro}")
    print(f"   CUDA Available: {system_info['has_cuda']}")
    print(f"   GPU Detected: {system_info['is_gpu']}")

    return system_info


def get_user_preferences():
    """Get user installation preferences"""
    print("\\n🎯 What would you like to install?")
    print("1. 🚀 Minimal (Basic functionality only)")
    print("2. 📦 Standard (Recommended for most users)")
    print("3. 🔬 Full (All features including development tools)")
    print("4. 🎮 GPU (GPU acceleration support)")
    print("5. 🧬 Biomedical (Specialized for biomedical papers)")

    while True:
        try:
            choice = input("\\nEnter your choice (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            else:
                print("Please enter a number between 1 and 5.")
        except KeyboardInterrupt:
            print("\\nSetup cancelled.")
            sys.exit(0)


def install_requirements(choice, system_info):
    """Install the appropriate requirements"""
    print("\\n📦 Installing dependencies...")

    requirements_map = {
        1: "requirements-minimal.txt",
        2: "requirements.txt",
        3: ["requirements.txt", "requirements-dev.txt"],
        4: "requirements-gpu.txt",
        5: "requirements-biomedical.txt"
    }

    req_files = requirements_map[choice]
    if isinstance(req_files, str):
        req_files = [req_files]

    for req_file in req_files:
        if not Path(req_file).exists():
            print(f"❌ Requirements file {req_file} not found!")
            continue

        print(f"📥 Installing from {req_file}...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", req_file
            ], check=True)
            print(f"✅ Successfully installed {req_file}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {req_file}: {e}")
            return False

    return True


def verify_installation():
    """Verify the installation works"""
    print("\\n🔧 Verifying installation...")

    try:
        # Test core imports
        sys.path.append(str(Path(__file__).parent / "src"))
        from src.research_assistant import ResearchAssistant

        # Test initialization
        assistant = ResearchAssistant()
        print("✅ Core system working")

        # Test basic functionality
        papers = assistant.list_papers()
        print("✅ Paper management working")

        return True

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        print("💡 Try running: python status_check.py")
        return False


def show_next_steps(choice):
    """Show next steps after installation"""
    print("\\n🎉 INSTALLATION COMPLETE!")
    print("=" * 30)

    if choice == 1:  # Minimal
        print("🚀 Quick Start:")
        print("   streamlit run app.py")

    elif choice == 2:  # Standard
        print("🌐 Web Interface:")
        print("   streamlit run app.py")
        print("🚀 API Server:")
        print("   python api.py")

    elif choice == 3:  # Full
        print("🛠️ Development Setup Complete!")
        print("🌐 Web: streamlit run app.py")
        print("🚀 API: python api.py")
        print("💻 CLI: python cli.py --help")
        print("🧪 Tests: python -m pytest")

    elif choice == 4:  # GPU
        print("🎮 GPU Setup Complete!")
        print("🌐 Web: streamlit run app.py")
        print("⚡ GPU acceleration will be used automatically")

    elif choice == 5:  # Biomedical
        print("🧬 Biomedical Setup Complete!")
        print("🌐 Web: streamlit run app.py")
        print("🔬 Specialized for biomedical paper analysis")

    print()
    print("📖 Documentation: README.md")
    print("🔧 Status Check: python status_check.py")
    print("🎯 Quick Demo: python success.py")


def main():
    """Main setup function"""
    print_banner()

    # Detect system
    system_info = detect_system()

    # Get user preferences
    choice = get_user_preferences()

    # Install requirements
    if not install_requirements(choice, system_info):
        print("\\n❌ Installation failed!")
        print("💡 Try manually running: pip install -r requirements.txt")
        sys.exit(1)

    # Verify installation
    if not verify_installation():
        print("\\n⚠️ Installation completed but verification failed.")
        print("💡 The system might still work. Try: streamlit run app.py")

    # Show next steps
    show_next_steps(choice)


if __name__ == "__main__":
    main()
