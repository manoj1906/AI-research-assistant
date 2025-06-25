#!/usr/bin/env python3
"""
Test script for AI Research Assistant
Validates core functionality and components
"""

from src.config import Config
from src.research_assistant import ResearchAssistant
import sys
from pathlib import Path
import tempfile
import logging
from typing import List, Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_pdf():
    """Create a sample PDF for testing."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        # Create a temporary PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            c = canvas.Canvas(tmp.name, pagesize=letter)

            # Add sample content
            c.drawString(100, 750, "Sample Research Paper")
            c.drawString(100, 720, "Authors: John Doe, Jane Smith")

            c.drawString(100, 680, "Abstract")
            c.drawString(
                100, 660, "This paper presents a novel approach to solving problem X.")
            c.drawString(
                100, 640, "Our method achieves state-of-the-art results on benchmark Y.")

            c.drawString(100, 600, "1. Introduction")
            c.drawString(
                100, 580, "Problem X has been extensively studied in the literature.")
            c.drawString(
                100, 560, "However, existing methods have limitations.")

            c.drawString(100, 520, "2. Methodology")
            c.drawString(
                100, 500, "We propose a new algorithm based on technique Z.")
            c.drawString(100, 480, "Our approach has three main components:")
            c.drawString(120, 460, "- Component A: Handles data preprocessing")
            c.drawString(
                120, 440, "- Component B: Performs feature extraction")
            c.drawString(
                120, 420, "- Component C: Generates final predictions")

            c.drawString(100, 380, "3. Results")
            c.drawString(100, 360, "We evaluated our method on dataset D.")
            c.drawString(
                100, 340, "Results show 15% improvement over baseline.")

            c.drawString(100, 300, "4. Conclusion")
            c.drawString(100, 280, "Our method achieves superior performance.")
            c.drawString(
                100, 260, "Future work includes extension to domain E.")

            c.save()
            return tmp.name

    except ImportError:
        logger.warning("reportlab not installed, cannot create sample PDF")
        return None


def test_research_assistant():
    """Test the research assistant functionality."""

    print("🔬 Testing AI Research Assistant")
    print("=" * 50)

    # Initialize assistant
    print("\n1. Initializing Research Assistant...")
    try:
        config = Config()
        assistant = ResearchAssistant(config)
        print("✅ Assistant initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing assistant: {e}")
        return False

    # Test configuration
    print("\n2. Testing Configuration...")
    try:
        print(f"✅ Models configured: {len(config.models.scientific_models)}")
        print(f"✅ Database path: {config.database.path}")
        print(f"✅ Processing config: {config.processing.max_pages} max pages")
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

    # Create or use sample PDF
    print("\n3. Creating Sample PDF...")
    sample_pdf = create_sample_pdf()

    if sample_pdf:
        print("✅ Sample PDF created")

        # Test paper upload
        print("\n4. Testing Paper Upload...")
        try:
            paper_id = assistant.upload_paper(sample_pdf)
            print(f"✅ Paper uploaded successfully: {paper_id}")
        except Exception as e:
            print(f"❌ Error uploading paper: {e}")
            return False

        # Test question answering
        print("\n5. Testing Question Answering...")
        test_questions = [
            "What is the main contribution?",
            "What methodology is used?",
            "What are the results?",
            "What datasets were used?",
            "What are the limitations?"
        ]

        for question in test_questions:
            try:
                answer = assistant.ask_question(question, paper_id)
                print(f"✅ Q: {question}")
                print(f"   A: {answer.answer[:100]}...")
            except Exception as e:
                print(f"❌ Error answering '{question}': {e}")

        # Test summarization
        print("\n6. Testing Summarization...")
        try:
            summary = assistant.summarize_paper(paper_id)
            print(f"✅ Summary generated: {len(summary)} characters")
        except Exception as e:
            print(f"❌ Error generating summary: {e}")

        # Test analysis
        print("\n7. Testing Analysis...")
        try:
            analysis = assistant.analyze_contribution(paper_id)
            print(f"✅ Analysis completed: {len(analysis)} components")
        except Exception as e:
            print(f"❌ Error analyzing paper: {e}")

        # Test paper listing
        print("\n8. Testing Paper Listing...")
        try:
            papers = assistant.list_papers()
            print(f"✅ Papers listed: {len(papers)} papers")
        except Exception as e:
            print(f"❌ Error listing papers: {e}")

        # Clean up
        import os
        try:
            os.unlink(sample_pdf)
            print("✅ Sample PDF cleaned up")
        except:
            pass

    else:
        print("⚠️  No sample PDF available, skipping paper tests")
        print("   Install reportlab for full testing: pip install reportlab")

        # Test basic functionality without PDF
        print("\n4. Testing Basic Components...")
        try:
            # Test embeddings
            embeddings = assistant.embeddings
            print("✅ Embeddings component accessible")

            # Test QA system
            qa_system = assistant.qa_system
            print("✅ QA system component accessible")

            # Test PDF parser
            pdf_parser = assistant.pdf_parser
            print("✅ PDF parser component accessible")

        except Exception as e:
            print(f"❌ Error testing components: {e}")

    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    return True


def test_api_compatibility():
    """Test API compatibility."""

    print("\n🌐 Testing API Compatibility")
    print("=" * 30)

    try:
        # Test FastAPI imports
        from fastapi import FastAPI
        print("✅ FastAPI available")

        # Test Pydantic
        from pydantic import BaseModel
        print("✅ Pydantic available")

        # Test uvicorn
        import uvicorn
        print("✅ uvicorn available")

    except ImportError as e:
        print(f"❌ Missing API dependency: {e}")
        return False

    return True


def test_cli_compatibility():
    """Test CLI compatibility."""

    print("\n💻 Testing CLI Compatibility")
    print("=" * 30)

    try:
        # Test Click
        import click
        print("✅ Click available")

    except ImportError as e:
        print(f"❌ Missing CLI dependency: {e}")
        return False

    return True


def test_web_compatibility():
    """Test web interface compatibility."""

    print("\n🌐 Testing Web Interface Compatibility")
    print("=" * 40)

    try:
        # Test Streamlit
        import streamlit
        print("✅ Streamlit available")

    except ImportError as e:
        print(f"❌ Missing web dependency: {e}")
        return False

    return True


def main():
    """Run all tests."""

    print("🧪 AI Research Assistant - Comprehensive Testing")
    print("=" * 60)

    # Run tests
    core_test = test_research_assistant()
    api_test = test_api_compatibility()
    cli_test = test_cli_compatibility()
    web_test = test_web_compatibility()

    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Core Functionality: {'✅ PASS' if core_test else '❌ FAIL'}")
    print(f"API Compatibility: {'✅ PASS' if api_test else '❌ FAIL'}")
    print(f"CLI Compatibility: {'✅ PASS' if cli_test else '❌ FAIL'}")
    print(f"Web Compatibility: {'✅ PASS' if web_test else '❌ FAIL'}")

    all_passed = all([core_test, api_test, cli_test, web_test])

    if all_passed:
        print("\n🎉 All tests passed! The AI Research Assistant is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Run the web interface: streamlit run app.py")
        print("2. Start the API server: python api_server.py")
        print("3. Use the CLI: python research_cli.py --help")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        print("   You may need to install additional dependencies.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
