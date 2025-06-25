#!/usr/bin/env python3
"""
Test script for the AI Research Assistant
"""

from src.config import Config
from src.research_assistant import ResearchAssistant
import sys
from pathlib import Path
import tempfile
import urllib.request

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


def download_sample_paper():
    """Download a sample academic paper for testing."""
    # Using a sample paper from arXiv (replace with actual paper if needed)
    sample_urls = [
        "https://arxiv.org/pdf/1706.03762.pdf",  # Attention is All You Need
        "https://arxiv.org/pdf/1810.04805.pdf",  # BERT
    ]

    for url in sample_urls:
        try:
            print(f"Downloading sample paper from {url}...")
            response = urllib.request.urlopen(url, timeout=30)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                f.write(response.read())
                return f.name
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            continue

    return None


def test_research_assistant():
    """Test the research assistant functionality."""
    print("🔬 Testing AI Research Assistant...")

    # Initialize the assistant
    config = Config()
    assistant = ResearchAssistant(config)

    # Try to download a sample paper
    paper_path = download_sample_paper()

    if paper_path:
        print(f"✅ Downloaded sample paper: {paper_path}")

        try:
            # Upload the paper
            print("📄 Processing paper...")
            paper_id = assistant.upload_paper(paper_path)
            print(f"✅ Paper uploaded with ID: {paper_id}")

            # Test questions
            test_questions = [
                "What is the main contribution of this paper?",
                "Summarize the abstract",
                "What methodology does this paper use?",
                "What are the key results?",
            ]

            print("\\n❓ Testing questions...")
            for question in test_questions:
                print(f"\\nQ: {question}")
                try:
                    answer = assistant.ask_question(question, paper_id)
                    print(f"A: {answer.answer[:200]}...")
                    if answer.evidence:
                        print(f"Evidence: {answer.evidence[:100]}...")
                except Exception as e:
                    print(f"Error answering question: {e}")

            # Test paper analysis
            print("\\n📊 Testing paper analysis...")
            try:
                analysis = assistant.analyze_contribution(paper_id)
                print(f"Contribution analysis: {analysis}")
            except Exception as e:
                print(f"Error in analysis: {e}")

        except Exception as e:
            print(f"❌ Error processing paper: {e}")

        finally:
            # Clean up
            Path(paper_path).unlink(missing_ok=True)
    else:
        print("❌ Could not download sample paper. Testing with mock data...")

        # Test with mock data (just to verify the system works)
        try:
            papers = assistant.list_papers()
            print(f"Current papers in system: {len(papers)}")
        except Exception as e:
            print(f"Error listing papers: {e}")


if __name__ == "__main__":
    test_research_assistant()
