#!/usr/bin/env python3
"""
Quick demo of AI Research Assistant functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


def main():
    print("🔬 AI Research Assistant - Quick Demo")
    print("=" * 50)

    try:
        from src.research_assistant import ResearchAssistant
        print("✅ Successfully imported ResearchAssistant")

        # Initialize
        assistant = ResearchAssistant()
        print("✅ Research Assistant initialized")

        # Show available papers
        papers = assistant.list_papers()
        print(f"✅ Found {len(papers)} uploaded papers")

        if papers:
            print("\n📚 Uploaded Papers:")
            for paper in papers:
                print(f"  📄 {paper['title']}")
                print(f"     ID: {paper['id']}")

        print("\n🎯 Demo Questions You Can Ask:")
        demo_questions = [
            "What is the main contribution?",
            "Summarize the methodology",
            "What are the key findings?",
            "What datasets were used?",
            "What are the limitations?",
            "How does this compare to prior work?"
        ]

        for i, q in enumerate(demo_questions, 1):
            print(f"  {i}. {q}")

        print("\n🚀 How to Use:")
        print("1. Web Interface: streamlit run app.py")
        print("2. API Server: python api_server.py")
        print("3. CLI: python research_cli.py list-papers")

        print("\n✨ The AI Research Assistant is ready!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
