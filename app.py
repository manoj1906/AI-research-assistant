#!/usr/bin/env python3
"""
AI Research Assistant - Main Application
"""

from src.research_assistant import ResearchAssistant
from src.config import Config
import streamlit as st
import logging
import sys
from pathlib import Path
import json
import tempfile
from typing import Optional, Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🔬 AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin: 1rem 0;
        border-bottom: 2px solid #F18F01;
        padding-bottom: 0.5rem;
    }
    .paper-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
    .answer-box {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #28a745;
        margin: 1rem 0;
    }
    .evidence-box {
        background: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border: 1px solid #ffc107;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "assistant" not in st.session_state:
    with st.spinner("🔬 Initializing AI Research Assistant..."):
        st.session_state.assistant = ResearchAssistant()
        st.session_state.papers = {}


def main():
    """Main application function."""

    # Header
    st.markdown('<h1 class="main-header">🔬 AI Research Assistant</h1>',
                unsafe_allow_html=True)
    st.markdown(
        "**Intelligent analysis of academic papers and research documents**")

    # Sidebar
    with st.sidebar:
        st.markdown("### 📚 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["📄 Upload Papers", "❓ Ask Questions",
                "📊 Paper Analysis", "🔍 Search Papers", "⚙️ Settings"]
        )

        # Show uploaded papers
        st.markdown("### 📑 Uploaded Papers")
        papers = st.session_state.assistant.list_papers()

        if papers:
            for paper in papers:
                with st.expander(f"📄 {paper['title'][:40]}..."):
                    st.write(
                        f"**Authors:** {', '.join(paper['authors'][:3])}...")
                    st.write(f"**Year:** {paper['year'] or 'Unknown'}")
                    st.write(f"**Pages:** {paper['page_count']}")
                    st.write(f"**ID:** `{paper['paper_id']}`")
        else:
            st.info("No papers uploaded yet")

    # Main content based on selected page
    if page == "📄 Upload Papers":
        upload_papers_page()
    elif page == "❓ Ask Questions":
        ask_questions_page()
    elif page == "📊 Paper Analysis":
        paper_analysis_page()
    elif page == "🔍 Search Papers":
        search_papers_page()
    elif page == "⚙️ Settings":
        settings_page()


def upload_papers_page():
    """Paper upload page."""
    st.markdown('<h2 class="section-header">📄 Upload Research Papers</h2>',
                unsafe_allow_html=True)

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload PDF research papers",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF research papers for analysis"
    )

    # Upload options
    col1, col2 = st.columns(2)
    with col1:
        extract_figures = st.checkbox("Extract figures and tables", value=True)
    with col2:
        auto_analyze = st.checkbox("Auto-analyze contributions", value=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**File:** {uploaded_file.name}")
                    st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")

                with col2:
                    if st.button(f"Process", key=f"process_{uploaded_file.name}"):
                        process_uploaded_paper(
                            uploaded_file, extract_figures, auto_analyze)


def process_uploaded_paper(uploaded_file, extract_figures: bool, auto_analyze: bool):
    """Process an uploaded paper."""
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        with st.spinner(f"🔄 Processing {uploaded_file.name}..."):
            # Upload and process paper
            paper_id = st.session_state.assistant.upload_paper(tmp_path)

            # Get paper info
            paper_info = st.session_state.assistant.get_paper_info(paper_id)

            # Store in session state
            st.session_state.papers[paper_id] = paper_info

            st.success(f"✅ Successfully processed: {paper_info['title']}")

            # Display paper info
            display_paper_info(paper_info)

            # Auto-analyze if requested
            if auto_analyze:
                with st.spinner("🧠 Analyzing contributions..."):
                    analysis = st.session_state.assistant.analyze_contribution(
                        paper_id)

                    st.markdown("### 🎯 Contribution Analysis")
                    st.markdown(
                        f"**Main Contributions:** {analysis['main_contributions']}")
                    st.markdown(f"**Novelty:** {analysis['novelty']}")
                    st.markdown(
                        f"**Significance:** {analysis['significance']}")

        # Clean up temporary file
        Path(tmp_path).unlink()

    except Exception as e:
        st.error(f"❌ Error processing paper: {str(e)}")
        logger.error(f"Error processing paper: {e}")


def ask_questions_page():
    """Question asking page."""
    st.markdown('<h2 class="section-header">❓ Ask Research Questions</h2>',
                unsafe_allow_html=True)

    papers = st.session_state.assistant.list_papers()

    if not papers:
        st.warning("📝 Please upload some papers first!")
        return

    # Question input
    st.markdown("### 💭 Ask a Question")
    question = st.text_input(
        "Enter your research question:",
        placeholder="What is the main contribution of this paper?",
        help="Ask questions like: 'What is the methodology?', 'Summarize section 3', 'What are the limitations?'"
    )

    # Paper selection
    col1, col2 = st.columns(2)
    with col1:
        paper_options = ["All papers"] + \
            [f"{p['title'][:50]}... ({p['paper_id']})" for p in papers]
        selected_paper = st.selectbox("Select paper:", paper_options)

    with col2:
        section = st.text_input(
            "Specific section (optional):",
            placeholder="e.g., methodology, results, conclusion",
            help="Leave empty to search entire paper"
        )

    # Common questions
    st.markdown("### 🔥 Common Questions")
    common_questions = [
        "What is the main contribution?",
        "What is the methodology?",
        "What are the results?",
        "What are the limitations?",
        "Summarize the abstract",
        "What datasets were used?",
        "How does this compare to related work?"
    ]

    selected_common = st.selectbox(
        "Or choose a common question:", [""] + common_questions)

    if selected_common:
        question = selected_common

    # Ask question button
    if st.button("🧠 Ask Question", disabled=not question):
        ask_question(question, selected_paper, section, papers)


def ask_question(question: str, selected_paper: str, section: str, papers: list):
    """Process a research question."""
    try:
        with st.spinner("🤔 Thinking..."):
            # Determine paper ID
            paper_id = None
            if selected_paper != "All papers":
                # Extract paper ID from selection
                paper_id = selected_paper.split("(")[-1].rstrip(")")

            # Ask the question
            answer = st.session_state.assistant.ask_question(
                question=question,
                paper_id=paper_id,
                section=section if section else None
            )

            # Display answer
            display_answer(answer, question)

    except Exception as e:
        st.error(f"❌ Error answering question: {str(e)}")
        logger.error(f"Error answering question: {e}")


def paper_analysis_page():
    """Paper analysis page."""
    st.markdown('<h2 class="section-header">📊 Paper Analysis</h2>',
                unsafe_allow_html=True)

    papers = st.session_state.assistant.list_papers()

    if not papers:
        st.warning("📝 Please upload some papers first!")
        return

    # Paper selection
    paper_options = [f"{p['title'][:50]}... ({p['paper_id']})" for p in papers]
    selected_paper = st.selectbox("Select paper for analysis:", paper_options)

    if selected_paper:
        paper_id = selected_paper.split("(")[-1].rstrip(")")

        # Analysis tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📋 Overview", "🎯 Contributions", "🔬 Methodology", "📈 Results"])

        with tab1:
            display_paper_overview(paper_id)

        with tab2:
            display_contribution_analysis(paper_id)

        with tab3:
            display_methodology_analysis(paper_id)

        with tab4:
            display_results_analysis(paper_id)


def search_papers_page():
    """Paper search page."""
    st.markdown('<h2 class="section-header">🔍 Search Papers</h2>',
                unsafe_allow_html=True)

    papers = st.session_state.assistant.list_papers()

    if not papers:
        st.warning("📝 Please upload some papers first!")
        return

    # Search input
    search_query = st.text_input(
        "Search papers by content:",
        placeholder="machine learning transformers attention mechanism",
        help="Enter keywords or concepts to find relevant papers"
    )

    max_results = st.slider("Max results:", 1, 10, 5)

    if st.button("🔍 Search") and search_query:
        with st.spinner("🔎 Searching papers..."):
            results = st.session_state.assistant.search_papers(
                search_query, max_results)

            if results:
                st.markdown(f"### 📊 Found {len(results)} relevant papers:")

                for i, result in enumerate(results, 1):
                    with st.expander(f"{i}. {result['title']} (Score: {result['similarity_score']:.3f})"):
                        display_paper_info(result)
            else:
                st.info("No papers found matching your search query.")


def settings_page():
    """Settings page."""
    st.markdown('<h2 class="section-header">⚙️ Settings</h2>',
                unsafe_allow_html=True)

    # Model settings
    st.markdown("### 🤖 Model Configuration")

    col1, col2 = st.columns(2)
    with col1:
        st.info("**Scientific Embeddings Model:**\nallenai/specter2")
        st.info("**Text Model:**\nallenai/scibert_scivocab_uncased")

    with col2:
        st.info("**QA Model:**\nmicrosoft/DialoGPT-medium")
        st.info("**Device:**\nAuto-detected (CPU/GPU)")

    # Processing settings
    st.markdown("### 🔧 Processing Settings")

    extract_figures = st.checkbox("Extract figures and tables", value=True)
    extract_citations = st.checkbox(
        "Extract citations and references", value=True)
    max_context_length = st.slider(
        "Max context length for QA:", 500, 3000, 2000)

    # System information
    st.markdown("### 💻 System Information")

    papers_count = len(st.session_state.assistant.list_papers())
    st.metric("Uploaded Papers", papers_count)

    # Clear data
    st.markdown("### 🗑️ Data Management")
    if st.button("🗑️ Clear All Papers", type="secondary"):
        if st.confirm("Are you sure you want to clear all papers?"):
            st.session_state.assistant.papers.clear()
            st.session_state.assistant.paper_embeddings.clear()
            st.session_state.papers.clear()
            st.success("All papers cleared!")
            st.rerun()


def display_paper_info(paper_info: Dict[str, Any]):
    """Display paper information."""
    st.markdown('<div class="paper-card">', unsafe_allow_html=True)

    st.markdown(f"**Title:** {paper_info['title']}")

    if paper_info['authors']:
        st.markdown(f"**Authors:** {', '.join(paper_info['authors'])}")

    if paper_info.get('abstract'):
        with st.expander("📄 Abstract"):
            st.write(paper_info['abstract'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pages", paper_info['page_count'])
    with col2:
        st.metric("Figures", paper_info['figures_count'])
    with col3:
        st.metric("Tables", paper_info['tables_count'])

    if paper_info.get('sections'):
        with st.expander("📑 Sections"):
            for section in paper_info['sections']:
                st.write(f"• {section['title']} (Pages {section['pages']})")

    st.markdown('</div>', unsafe_allow_html=True)


def display_answer(answer, question: str):
    """Display a research answer."""
    st.markdown('<div class="answer-box">', unsafe_allow_html=True)

    st.markdown(f"**Question:** {question}")
    st.markdown(f"**Answer:** {answer.answer}")

    # Confidence indicator
    confidence_color = "green" if answer.confidence > 0.7 else "orange" if answer.confidence > 0.4 else "red"
    st.markdown(
        f"**Confidence:** <span style='color: {confidence_color}'>{answer.confidence:.2f}</span>", unsafe_allow_html=True)

    if answer.evidence_text:
        with st.expander("📋 Evidence"):
            st.markdown('<div class="evidence-box">', unsafe_allow_html=True)
            st.write(answer.evidence_text)
            st.markdown('</div>', unsafe_allow_html=True)

    if answer.source_section:
        st.markdown(f"**Source Section:** {answer.source_section}")

    if answer.page_number:
        st.markdown(f"**Page:** {answer.page_number}")

    st.markdown('</div>', unsafe_allow_html=True)


def display_paper_overview(paper_id: str):
    """Display paper overview."""
    paper_info = st.session_state.assistant.get_paper_info(paper_id)
    display_paper_info(paper_info)

    # Generate summary
    if st.button("📄 Generate Summary"):
        with st.spinner("Generating summary..."):
            summary = st.session_state.assistant.summarize_paper(paper_id)
            st.markdown("### 📝 Paper Summary")
            st.write(summary)


def display_contribution_analysis(paper_id: str):
    """Display contribution analysis."""
    if st.button("🎯 Analyze Contributions"):
        with st.spinner("Analyzing contributions..."):
            analysis = st.session_state.assistant.analyze_contribution(
                paper_id)

            st.markdown("### 🎯 Contribution Analysis")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Main Contributions:**")
                st.write(analysis['main_contributions'])

                st.markdown("**Novelty:**")
                st.write(analysis['novelty'])

            with col2:
                st.markdown("**Significance:**")
                st.write(analysis['significance'])

                # Confidence scores
                st.markdown("**Confidence Scores:**")
                for aspect, score in analysis['confidence_scores'].items():
                    st.progress(score, text=f"{aspect}: {score:.2f}")


def display_methodology_analysis(paper_id: str):
    """Display methodology analysis."""
    if st.button("🔬 Analyze Methodology"):
        with st.spinner("Analyzing methodology..."):
            analysis = st.session_state.assistant.analyze_methodology(paper_id)

            st.markdown("### 🔬 Methodology Analysis")

            st.markdown("**Methodology:**")
            st.write(analysis['methodology'])

            st.markdown("**Approach:**")
            st.write(analysis['approach'])

            st.markdown("**Datasets:**")
            st.write(analysis['datasets'])


def display_results_analysis(paper_id: str):
    """Display results analysis."""
    if st.button("📈 Analyze Results"):
        with st.spinner("Analyzing results..."):
            # Ask results-related questions
            results_answer = st.session_state.assistant.ask_question(
                "What are the results?", paper_id)
            performance_answer = st.session_state.assistant.ask_question(
                "What is the performance?", paper_id)

            st.markdown("### 📈 Results Analysis")

            st.markdown("**Results:**")
            st.write(results_answer.answer)

            st.markdown("**Performance:**")
            st.write(performance_answer.answer)


if __name__ == "__main__":
    main()
