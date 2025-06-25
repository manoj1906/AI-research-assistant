#!/usr/bin/env python3
"""
Complete Usage Guide for AI Research Assistant
"""

import os
from pathlib import Path


def print_banner():
    print("=" * 60)
    print("🔬 AI RESEARCH ASSISTANT - COMPLETE GUIDE")
    print("=" * 60)
    print()


def show_interfaces():
    print("🌟 AVAILABLE INTERFACES")
    print("-" * 25)
    print()

    print("1. 🌐 WEB INTERFACE (Recommended for beginners)")
    print("   • User-friendly Streamlit interface")
    print("   • Upload PDFs, ask questions, view results")
    print("   • Perfect for interactive research")
    print()
    print("   📍 How to start:")
    print("   streamlit run app.py")
    print("   → Open: http://localhost:8501")
    print()

    print("2. 🚀 REST API (For developers)")
    print("   • FastAPI server for programmatic access")
    print("   • JSON API endpoints")
    print("   • Perfect for integration with other tools")
    print()
    print("   📍 How to start:")
    print("   python api.py")
    print("   → API docs: http://localhost:8000/docs")
    print()

    print("3. 💻 COMMAND LINE (For batch processing)")
    print("   • CLI for scripting and automation")
    print("   • Batch processing multiple papers")
    print("   • Perfect for research workflows")
    print()
    print("   📍 How to use:")
    print("   python cli.py --help")
    print()

    print("4. 🐍 PYTHON SDK (For custom applications)")
    print("   • Direct Python API")
    print("   • Full programmatic control")
    print("   • Perfect for custom research tools")
    print()


def show_quick_start():
    print("🚀 QUICK START GUIDE")
    print("-" * 20)
    print()

    steps = [
        "1. 📦 Install Dependencies",
        "   pip install -r requirements.txt",
        "",
        "2. 🌐 Start Web Interface",
        "   streamlit run app.py",
        "   → Open http://localhost:8501",
        "",
        "3. 📄 Upload a Research Paper",
        "   • Click 'Browse files' or drag & drop",
        "   • Supported: PDF files",
        "   • Wait for processing to complete",
        "",
        "4. ❓ Ask Research Questions",
        "   • 'What is the main contribution?'",
        "   • 'Summarize the methodology'",
        "   • 'What are the key findings?'",
        "   • 'What datasets were used?'",
        "",
        "5. 📊 Explore Results",
        "   • View answers with evidence",
        "   • Check confidence scores",
        "   • Export summaries"
    ]

    for step in steps:
        print(step)
    print()


def show_sample_questions():
    print("❓ RESEARCH QUESTIONS YOU CAN ASK")
    print("-" * 35)
    print()

    categories = {
        "📋 General Analysis": [
            "What is the main contribution of this paper?",
            "What problem does this paper solve?",
            "What is novel about this research?",
            "How significant is this work?"
        ],
        "🔬 Methodology": [
            "What methodology does this paper use?",
            "Explain the experimental setup",
            "What are the key assumptions?",
            "How was the data collected?"
        ],
        "📈 Results & Findings": [
            "What are the main findings?",
            "What do the results show?",
            "How do results compare to baselines?",
            "What are the performance metrics?"
        ],
        "📚 Literature & Context": [
            "How does this relate to previous work?",
            "What datasets were used?",
            "What are the limitations?",
            "What future work is suggested?"
        ],
        "📖 Section-Specific": [
            "Summarize the abstract",
            "Explain the introduction",
            "Describe the methodology section",
            "What does the conclusion say?"
        ]
    }

    for category, questions in categories.items():
        print(f"{category}:")
        for question in questions:
            print(f"  • {question}")
        print()


def show_api_examples():
    print("🔗 API USAGE EXAMPLES")
    print("-" * 21)
    print()

    print("📤 Upload Paper:")
    print("curl -X POST http://localhost:8000/papers/upload \\")
    print("     -F 'file=@research_paper.pdf'")
    print()

    print("❓ Ask Question:")
    print("curl -X POST http://localhost:8000/papers/ask \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print("       \"question\": \"What is the main contribution?\",")
    print("       \"paper_id\": \"your-paper-id\"")
    print("     }'")
    print()

    print("📋 List Papers:")
    print("curl http://localhost:8000/papers")
    print()


def show_python_examples():
    print("🐍 PYTHON SDK EXAMPLES")
    print("-" * 23)
    print()

    code = '''
# Import the research assistant
from src.research_assistant import ResearchAssistant

# Initialize
assistant = ResearchAssistant()

# Upload a paper
paper_id = assistant.upload_paper("research_paper.pdf")

# Ask questions
answer = assistant.ask_question(
    "What is the main contribution?", 
    paper_id=paper_id
)
print(f"Answer: {answer.answer}")
print(f"Confidence: {answer.confidence}")

# Generate summary
summary = assistant.summarize_paper(paper_id)
print(f"Summary: {summary}")

# Analyze contribution
analysis = assistant.analyze_contribution(paper_id)
print(f"Analysis: {analysis}")
'''

    print(code.strip())
    print()


def show_tips_and_tricks():
    print("💡 TIPS & TRICKS")
    print("-" * 16)
    print()

    tips = [
        "📄 Upload Quality: Use high-quality PDFs with selectable text",
        "❓ Question Types: Ask specific, focused questions for best results",
        "📊 Section Focus: Target specific sections for detailed analysis",
        "🔄 Multiple Questions: Ask follow-up questions to dive deeper",
        "💾 Save Results: Export summaries and answers for later use",
        "🔍 Search Feature: Use semantic search to find relevant content",
        "⚡ Performance: CPU processing may be slower than GPU",
        "🔧 Configuration: Adjust model settings in src/config.py"
    ]

    for tip in tips:
        print(f"  • {tip}")
    print()


def show_troubleshooting():
    print("🔧 TROUBLESHOOTING")
    print("-" * 18)
    print()

    issues = {
        "❌ Import Errors": [
            "Run: pip install -r requirements.txt",
            "Check Python version (3.8+ required)"
        ],
        "🐌 Slow Processing": [
            "Normal on CPU - GPU recommended for production",
            "Reduce model size in config if needed"
        ],
        "📄 PDF Issues": [
            "Ensure PDF has selectable text (not scanned images)",
            "Try different PDF if processing fails"
        ],
        "🤖 Model Loading": [
            "First run downloads models (may take time)",
            "Check internet connection for model downloads"
        ]
    }

    for issue, solutions in issues.items():
        print(f"{issue}:")
        for solution in solutions:
            print(f"  → {solution}")
        print()


def show_project_structure():
    print("📁 PROJECT STRUCTURE")
    print("-" * 20)
    print()

    structure = """
ai-research-assistant/
├── 📱 app.py                    # Streamlit web interface
├── 🚀 api.py                    # FastAPI REST API
├── 💻 cli.py                    # Command line interface
├── 📋 requirements.txt          # Python dependencies
├── 📖 README.md                 # Documentation
├── 🎯 demo.py                   # Demo script
├── src/                         # Core source code
│   ├── 🎛️ config.py              # Configuration
│   ├── 🧠 research_assistant.py  # Main coordinator
│   ├── paper_processor/         # PDF parsing
│   ├── research_embeddings/     # AI embeddings
│   ├── research_qa/             # Question answering
│   └── analysis/               # Advanced analysis
├── data/                       # Uploaded papers storage
└── web/                        # Additional web assets
"""

    print(structure)


def main():
    print_banner()
    show_interfaces()
    show_quick_start()
    show_sample_questions()
    show_api_examples()
    show_python_examples()
    show_tips_and_tricks()
    show_troubleshooting()
    show_project_structure()

    print("🎉 CONGRATULATIONS!")
    print("-" * 17)
    print("Your AI Research Assistant is ready to use!")
    print()
    print("🚀 Next Steps:")
    print("1. Start the web interface: streamlit run app.py")
    print("2. Upload your first research paper")
    print("3. Ask questions and explore the results")
    print()
    print("📚 Need help? Check the README.md or run the demo")
    print("✨ Happy researching!")


if __name__ == "__main__":
    main()
