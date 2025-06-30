# 🚀 AI Research Assistant - Installation Guide

## Prerequisites

Before installing, make sure you have:
- **Python 3.8+** (recommended: Python 3.9 or 3.10)
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **8GB+ RAM** (recommended)
- **Internet connection** (for downloading AI models)

## Quick Installation (Recommended)

### Step 1: Navigate to the Project Directory
```bash
cd ~/ai-research-assistant
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv ai_research_env

# Activate virtual environment
source ai_research_env/bin/activate  # On Linux/Mac
# or
ai_research_env\Scripts\activate     # On Windows
```

### Step 3: Upgrade pip
```bash
pip install --upgrade pip
```

### Step 4: Install Requirements
```bash
# Install all requirements
pip install -r requirements.txt
```

## Alternative Installation Methods

### Method 1: Smart Setup (Automated)
```bash
# Run the automated setup script
python3 setup.py
```

### Method 2: Step-by-Step Installation
If the automatic installation fails, install components step by step:

```bash
# Core dependencies first
pip install torch>=1.9.0
pip install transformers>=4.20.0
pip install sentence-transformers>=2.2.0

# Scientific libraries
pip install numpy>=1.21.0 scipy>=1.7.0 scikit-learn>=1.0.0 pandas>=1.3.0

# PDF processing
pip install PyMuPDF>=1.20.0 pdfplumber>=0.7.0 pypdf>=3.0.0

# Web framework
pip install streamlit>=1.25.0 fastapi>=0.95.0 uvicorn>=0.20.0

# Vector database
pip install chromadb>=0.4.0

# Utilities
pip install requests>=2.28.0 tqdm>=4.64.0 click>=8.1.0
```

### Method 3: Minimal Installation (Fastest)
For a lightweight installation with core features only:
```bash
pip install -r requirements-minimal.txt
```

## Installation Verification

After installation, verify everything works:

```bash
# Quick verification
python -c "
import torch, transformers, streamlit, fastapi, fitz
from src.research_assistant import ResearchAssistant
print('✅ All core components installed successfully!')
"

# Or run the comprehensive test
python validate_requirements.py
```

## Launch the Application

Once installed, start the application:

```bash
# Start the web interface
streamlit run app.py

# Or start the API server
python api.py

# Or use the CLI
python cli.py --help
```

## Troubleshooting Common Issues

### Issue 1: PyTorch Installation
If PyTorch fails to install:
```bash
# For CPU-only version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# For CUDA (if you have NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue 2: Permission Errors
If you get permission errors:
```bash
# Install with user flag
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

### Issue 3: Package Conflicts
If you encounter package conflicts:
```bash
# Create a fresh virtual environment
rm -rf ai_research_env
python3 -m venv ai_research_env
source ai_research_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue 4: Memory Issues During Installation
If installation fails due to memory issues:
```bash
# Install with no cache
pip install --no-cache-dir -r requirements.txt

# Or install packages one by one
pip install torch
pip install transformers
# ... continue with individual packages
```

### Issue 5: Streamlit Import Errors
If Streamlit has import issues:
```bash
# Reinstall Streamlit
pip uninstall streamlit
pip install streamlit>=1.25.0

# Clear Streamlit cache
streamlit cache clear
```

## System-Specific Instructions

### Ubuntu/Debian
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv python3-dev build-essential

# For PDF processing (if needed)
sudo apt install poppler-utils

# Then proceed with pip installation
pip install -r requirements.txt
```

### CentOS/RHEL/Fedora
```bash
# Install system dependencies
sudo yum install python3-pip python3-devel gcc

# Or for newer versions
sudo dnf install python3-pip python3-devel gcc

# Then proceed with pip installation
pip install -r requirements.txt
```

### macOS
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Then proceed with pip installation
pip install -r requirements.txt
```

## GPU Support (Optional)

If you have an NVIDIA GPU and want to use GPU acceleration:

```bash
# Install CUDA-enabled PyTorch
pip install -r requirements-gpu.txt

# Verify GPU support
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Development Installation

If you want to contribute or develop:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

## Docker Installation (Alternative)

If you prefer Docker:

```bash
# Build the Docker image
docker build -t ai-research-assistant .

# Run the container
docker run -p 8501:8501 ai-research-assistant

# Or use docker-compose
docker-compose up
```

## Environment Variables (Optional)

Create a `.env` file for optional configurations:

```bash
# Create .env file
cat > .env << EOF
# Optional: Set custom paths
DATA_DIR=./data
MODELS_DIR=./models

# Optional: API keys (if using external services)
OPENAI_API_KEY=your_key_here
HUGGINGFACE_API_KEY=your_key_here

# Optional: Performance settings
MAX_WORKERS=4
CACHE_SIZE=1000
EOF
```

## Final Verification

Run the complete test suite to ensure everything is working:

```bash
# Run improvement tests
python test_improvements.py

# Or run the main application
streamlit run app.py
```

## Getting Help

If you encounter issues:

1. **Check the logs**: Look at the terminal output for specific error messages
2. **Update packages**: `pip install --upgrade -r requirements.txt`
3. **Clear cache**: `pip cache purge`
4. **Fresh install**: Delete virtual environment and recreate
5. **System requirements**: Ensure you have Python 3.8+ and sufficient RAM

## Success! 🎉

Once installed successfully, you should see:
```
✅ All core components installed successfully!
🚀 AI Research Assistant ready to use!
🌐 Web interface: http://localhost:8501
```

Happy researching! 📚🔬
