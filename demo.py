#!/usr/bin/env python3
"""
Demo script for AI Research Assistant
This script demonstrates key features of the application
"""

from src.config import Config
from src.research_assistant import ResearchAssistant
import sys
from pathlib import Path
import time

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


def print_banner():
    """Print a welcome banner"""
    print("=" * 60)
    print("🔬 AI RESEARCH ASSISTANT DEMO")
    print("=" * 60)
    print("This demo shows how to:")
    print("1. Upload and process academic papers")
    print("2. Ask research-specific questions")
    print("3. Generate summaries and analyses")
    print("4. Search across papers")
    print("=" * 60)
    print()


def demo_basic_functionality():
    """Demonstrate basic functionality with mock data"""
    print("📋 BASIC FUNCTIONALITY DEMO")
    print("-" * 30)

    # Initialize assistant
    print("🔧 Initializing AI Research Assistant...")
    assistant = ResearchAssistant()
    print("✅ Assistant initialized")

    # List current papers
    papers = assistant.list_papers()
    print(f"📚 Current papers in system: {len(papers)}")

    if papers:
        print("\\nPapers:")
        for i, paper in enumerate(papers, 1):
            print(f"  {i}. {paper.get('title', 'Unknown Title')[:50]}...")

    print()


def demo_questions():
    """Demonstrate common research questions"""
    print("❓ COMMON RESEARCH QUESTIONS DEMO")
    print("-" * 35)

    common_questions = [
        "What is the main contribution of this paper?",
        "What methodology does this paper use?",
        "What are the key results and findings?",
        "How does this work compare to previous research?",
        "What are the limitations of this study?",
        "What future work is suggested?",
        "Summarize the abstract",
        "What datasets were used?",
        "What evaluation metrics were used?",
        "What is the computational complexity?"
    ]

    print("These are common questions you can ask:")
    for i, question in enumerate(common_questions, 1):
        print(f"  {i:2d}. {question}")

    print()


def demo_features():
    """Demonstrate key features"""
    print("🌟 KEY FEATURES")
    print("-" * 15)

    features = [
        "📄 Academic PDF Processing",
        "  • Extracts sections, figures, tables, references",
        "  • Handles academic formatting and structure",
        "  • Preserves document hierarchy",
        "",
        "🧠 Research-Specific AI",
        "  • Uses scientific language models (SPECTER, SciBERT)",
        "  • Understands academic terminology",
        "  • Provides evidence-based answers",
        "",
        "❓ Intelligent Question Answering",
        "  • Section-specific queries",
        "  • Contribution analysis",
        "  • Methodology extraction",
        "  • Result summarization",
        "",
        "🔍 Advanced Search",
        "  • Semantic search across papers",
        "  • Cross-paper comparisons",
        "  • Citation network analysis",
        "",
        "📊 Research Analysis",
        "  • Contribution identification",
        "  • Methodology classification",
        "  • Impact assessment",
        "  • Gap analysis",
        "",
        "🌐 Multiple Interfaces",
        "  • Web UI (Streamlit)",
        "  • REST API (FastAPI)",
        "  • Command Line Interface",
        "  • Python SDK"
    ]

    for feature in features:
        print(feature)

    print()


def demo_usage_examples():
    """Show usage examples for different interfaces"""
    print("💻 USAGE EXAMPLES")
    print("-" * 17)

    print("1. Web Interface:")
    print("   streamlit run app.py")
    print("   → Open http://localhost:8501")
    print()

    print("2. Command Line:")
    print("   python cli.py upload paper.pdf")
    print("   python cli.py ask 'What is the main contribution?'")
    print("   python cli.py summarize --paper-id abc123")
    print()

    print("3. REST API:")
    print("   python api.py")
    print("   curl -X POST http://localhost:8000/papers/upload -F 'file=@paper.pdf'")
    print("   curl -X POST http://localhost:8000/papers/ask -d '...'")
    print()

    print("4. Python SDK:")
    print("   from src.research_assistant import ResearchAssistant")
    print("   assistant = ResearchAssistant()")
    print("   paper_id = assistant.upload_paper('paper.pdf')")
    print("   answer = assistant.ask_question('What is the contribution?', paper_id)")
    print()


def demo_file_support():
    """Show supported file types and formats"""
    print("📁 SUPPORTED FORMATS")
    print("-" * 19)

    formats = {
        "Input Formats": [
            "PDF (Adobe Portable Document Format)",
            "Academic papers with standard formatting",
            "Conference papers, journal articles, preprints",
            "Multi-column layouts with figures and tables"
        ],
        "Content Extraction": [
            "Title, authors, abstract, keywords",
            "Section headers and content",
            "Figures with captions",
            "Tables with captions",
            "References and citations",
            "Mathematical equations"
        ],
        "Output Formats": [
            "JSON (structured data)",
            "Plain text (human-readable)",
            "HTML (web display)",
            "Markdown (documentation)"
        ]
    }

    for category, items in formats.items():
        print(f"\\n{category}:")
        for item in items:
            print(f"  • {item}")

    print()


def main():
    """Main demo function"""
    print_banner()

    sections = [
        ("Basic Functionality", demo_basic_functionality),
        ("Research Questions", demo_questions),
        ("Key Features", demo_features),
        ("Usage Examples", demo_usage_examples),
        ("File Support", demo_file_support)
    ]

    for title, func in sections:
        func()

        # Add a small delay between sections
        time.sleep(1)

    print("🎯 GETTING STARTED")
    print("-" * 17)
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run web interface: streamlit run app.py")
    print("3. Upload a PDF paper")
    print("4. Ask questions about your research!")
    print()
    print("📚 For more help, check the README.md file")
    print("🔗 GitHub: https://github.com/your-org/ai-research-assistant")
    print()
    print("Happy researching! 🔬✨")


if __name__ == "__main__":
    main()
