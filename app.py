#!/usr/bin/env python3
"""
AI Research Assistant - Main Application
"""

import streamlit as st
import logging
import sys
from pathlib import Path
import json
import tempfile
from typing import Optional, Dict, Any
from datetime import datetime

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

# Custom CSS with mobile responsiveness
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
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        border: 2px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .evidence-box {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffc107;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .success-metric {
        background: #d4edda;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 4px solid #28a745;
    }
    .warning-metric {
        background: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 4px solid #ffc107;
    }
    .error-metric {
        background: #f8d7da;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 4px solid #dc3545;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .section-header {
            font-size: 1.2rem;
        }
        .paper-card, .answer-box {
            margin: 0.5rem 0;
            padding: 1rem;
        }
    }
    
    /* Improved button styling */
    .stButton > button {
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2E86AB, #A23B72);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with lazy loading
if "assistant" not in st.session_state:
    st.session_state.assistant = None
    st.session_state.papers = {}
    st.session_state.assistant_initialized = False

def get_assistant():
    """Lazy load the research assistant only when needed."""
    if st.session_state.assistant is None:
        with st.spinner("🔬 Initializing AI Research Assistant..."):
            try:
                # Import only when needed to avoid loading heavy models on startup
                from src.research_assistant import ResearchAssistant
                st.session_state.assistant = ResearchAssistant()
                st.session_state.assistant_initialized = True
                st.success("✅ AI Research Assistant initialized successfully!")
            except Exception as e:
                st.error(f"❌ Failed to initialize assistant: {str(e)}")
                st.session_state.assistant_initialized = False
                return None
    return st.session_state.assistant


def main():
    """Main application function."""

    # Header
    st.markdown('<h1 class="main-header">🔬 AI Research Assistant</h1>',
                unsafe_allow_html=True)
    
    # Show initialization status
    if not st.session_state.assistant_initialized:
        st.markdown("**🚀 Fast-loading AI Research Assistant - Models load on-demand for instant startup!**")
        st.info("💡 The AI models will initialize automatically when you upload papers or ask questions.")
    else:
        st.markdown("**✅ AI Research Assistant - Ready for intelligent analysis!**")

    # Sidebar
    with st.sidebar:
        st.markdown("### 📚 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["📄 Upload Papers", "❓ Ask Questions", "📊 Paper Analysis", 
             "🔍 Search Papers", "📚 Q&A History", "⚙️ Settings"]
        )

        # Show uploaded papers with management options
        st.markdown("### 📑 Paper Library")
        
        # Check if assistant is initialized
        if not st.session_state.assistant_initialized:
            st.info("🔄 Assistant will initialize when you upload papers or ask questions")
            st.write("📊 0 papers")
        else:
            assistant = get_assistant()
            if assistant:
                papers = assistant.list_papers()
                
                if papers:
                    # Add search and filter options
                    search_term = st.text_input("🔍 Search papers:", placeholder="Search by title or author")
                    
                    # Filter papers based on search
                    filtered_papers = papers
                    if search_term:
                        filtered_papers = [
                            p for p in papers 
                            if search_term.lower() in p['title'].lower() or 
                            any(search_term.lower() in author.lower() for author in p['authors'])
                        ]
                    
                    st.write(f"📊 {len(filtered_papers)} of {len(papers)} papers")
                    
                    for paper in filtered_papers:
                        with st.expander(f"📄 {paper['title'][:40]}..."):
                            st.write(f"**Authors:** {', '.join(paper['authors'][:3])}...")
                            st.write(f"**Year:** {paper['year'] or 'Unknown'}")
                            st.write(f"**Pages:** {paper['page_count']}")
                            st.write(f"**ID:** `{paper['paper_id']}`")
                            
                            # Paper management buttons
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if st.button("📄 View Details", key=f"view_{paper['paper_id']}"):
                                    st.session_state.selected_paper = paper['paper_id']
                                    st.rerun()
                            with col2:
                                if st.button("📥 Export", key=f"export_{paper['paper_id']}"):
                                    export_paper_data(paper['paper_id'])
                            with col3:
                                if st.button("🗑️ Delete", key=f"delete_{paper['paper_id']}", type="secondary"):
                                    if st.session_state.get(f"confirm_delete_{paper['paper_id']}", False):
                                        delete_paper(paper['paper_id'])
                                        st.rerun()
                                    else:
                                        st.session_state[f"confirm_delete_{paper['paper_id']}"] = True
                                        st.warning("Click delete again to confirm")
                else:
                    st.info("No papers uploaded yet")
            else:
                st.error("❌ Assistant initialization failed")

    # Main content based on selected page
    if page == "📄 Upload Papers":
        upload_papers_page()
    elif page == "❓ Ask Questions":
        ask_questions_page()
    elif page == "📊 Paper Analysis":
        paper_analysis_page()
    elif page == "🔍 Search Papers":
        search_papers_page()
    elif page == "📚 Q&A History":
        qa_history_page()
    elif page == "⚙️ Settings":
        settings_page()


def upload_papers_page():
    """Paper upload page."""
    st.markdown('<h2 class="section-header">📄 Upload Research Papers</h2>',
                unsafe_allow_html=True)

    # Quick start info for new users
    if not st.session_state.assistant_initialized:
        st.info("🚀 **Quick Start**: Upload your first PDF to automatically initialize the AI assistant!")

    # File uploader with validation
    uploaded_files = st.file_uploader(
        "Upload PDF research papers",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF research papers for analysis (Max 50MB each)"
    )

    # Upload options
    col1, col2 = st.columns(2)
    with col1:
        extract_figures = st.checkbox("Extract figures and tables", value=True)
    with col2:
        auto_analyze = st.checkbox("Auto-analyze contributions", value=True)

    # File validation and processing
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Validate file
            validation_result = validate_uploaded_file(uploaded_file)
            
            with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                if not validation_result["valid"]:
                    st.error(f"❌ {validation_result['error']}")
                    continue
                    
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**File:** {uploaded_file.name}")
                    st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
                    if validation_result["valid"]:
                        st.success("✅ File validation passed")

                with col2:
                    if st.button(f"Process", key=f"process_{uploaded_file.name}"):
                        process_uploaded_paper(
                            uploaded_file, extract_figures, auto_analyze)


def validate_uploaded_file(uploaded_file) -> dict:
    """Validate uploaded file."""
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        return {
            "valid": False, 
            "error": f"File size ({uploaded_file.size / (1024*1024):.1f}MB) exceeds maximum allowed (50MB)"
        }
    
    # Check file type
    if not uploaded_file.name.lower().endswith('.pdf'):
        return {
            "valid": False,
            "error": "Only PDF files are supported"
        }
    
    # Check if file is empty
    if uploaded_file.size == 0:
        return {
            "valid": False,
            "error": "File appears to be empty"
        }
    
    return {"valid": True, "error": None}


def process_uploaded_paper(uploaded_file, extract_figures: bool, auto_analyze: bool):
    """Process an uploaded paper with comprehensive error handling."""
    tmp_path = None
    try:
        # Initialize assistant if needed
        assistant = get_assistant()
        if not assistant:
            st.error("❌ Failed to initialize AI assistant. Please refresh and try again.")
            return
            
        # Create progress bar
        progress_bar = st.progress(0, text="Starting processing...")
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        progress_bar.progress(20, text="File saved, starting analysis...")

        # Process paper with detailed progress
        with st.spinner(f"🔄 Processing {uploaded_file.name}..."):
            progress_bar.progress(40, text="Extracting text and structure...")
            
            # Upload and process paper
            paper_id = assistant.upload_paper(tmp_path)
            progress_bar.progress(60, text="Generating embeddings...")

            # Get paper info
            paper_info = assistant.get_paper_info(paper_id)
            progress_bar.progress(80, text="Finalizing processing...")

            # Store in session state
            st.session_state.papers[paper_id] = paper_info
            progress_bar.progress(100, text="Processing complete!")

            st.success(f"✅ Successfully processed: {paper_info['title']}")

            # Display paper info
            display_paper_info(paper_info)

            # Auto-analyze if requested
            if auto_analyze:
                with st.spinner("🧠 Analyzing contributions..."):
                    try:
                        analysis = assistant.analyze_contribution(paper_id)

                        st.markdown("### 🎯 Contribution Analysis")
                        st.markdown(f"**Main Contributions:** {analysis['main_contributions']}")
                        st.markdown(f"**Novelty:** {analysis['novelty']}")
                        st.markdown(f"**Significance:** {analysis['significance']}")
                    except Exception as analysis_error:
                        st.warning(f"⚠️ Could not analyze contributions: {str(analysis_error)}")

    except FileNotFoundError:
        st.error("❌ File could not be found or accessed")
        logger.error(f"File not found error processing: {uploaded_file.name}")
    except PermissionError:
        st.error("❌ Permission denied accessing file")
        logger.error(f"Permission error processing: {uploaded_file.name}")
    except Exception as e:
        st.error(f"❌ Error processing paper: {str(e)}")
        logger.error(f"Error processing paper {uploaded_file.name}: {e}")
        
        # Show detailed error information in expander
        with st.expander("🔍 Error Details"):
            st.code(str(e))
            st.write("**Troubleshooting tips:**")
            st.write("- Ensure the PDF is not corrupted")
            st.write("- Try a smaller file size")
            st.write("- Check if the PDF contains extractable text")
    
    finally:
        # Always clean up temporary file
        if tmp_path and Path(tmp_path).exists():
            try:
                Path(tmp_path).unlink()
            except Exception as cleanup_error:
                logger.warning(f"Could not clean up temp file {tmp_path}: {cleanup_error}")


def ask_questions_page():
    """Question asking page."""
    st.markdown('<h2 class="section-header">❓ Ask Research Questions</h2>',
                unsafe_allow_html=True)

    # Initialize assistant if needed
    assistant = get_assistant()
    if not assistant:
        st.error("❌ Failed to initialize AI assistant. Please refresh and try again.")
        return

    papers = assistant.list_papers()

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
    """Process a research question with enhanced features."""
    try:
        # Get assistant
        assistant = get_assistant()
        if not assistant:
            st.error("❌ Failed to initialize AI assistant. Please refresh and try again.")
            return
            
        with st.spinner("🤔 Thinking..."):
            # Determine paper ID
            paper_id = None
            if selected_paper != "All papers":
                # Extract paper ID from selection
                paper_id = selected_paper.split("(")[-1].rstrip(")")

            # Ask the question
            answer = assistant.ask_question(
                question=question,
                paper_id=paper_id,
                section=section if section else None
            )

            # Store Q&A in session state for history
            if "qa_history" not in st.session_state:
                st.session_state.qa_history = []
            
            qa_entry = {
                "question": question,
                "answer": answer,
                "paper_id": paper_id,
                "section": section,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.qa_history.insert(0, qa_entry)  # Most recent first
            
            # Keep only last 50 Q&As
            if len(st.session_state.qa_history) > 50:
                st.session_state.qa_history = st.session_state.qa_history[:50]

            # Display answer
            display_answer(answer, question)
            
            # Add export option for this Q&A
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 Export This Q&A", key="export_qa"):
                    export_qa_data(qa_entry)
            with col2:
                if st.button("📋 Copy Answer", key="copy_answer"):
                    st.code(answer.answer)
                    st.info("Answer copied to display above ⬆️")

    except Exception as e:
        st.error(f"❌ Error answering question: {str(e)}")
        logger.error(f"Error answering question '{question}': {e}")
        
        # Show troubleshooting
        with st.expander("🔧 Troubleshooting"):
            st.write("**Possible solutions:**")
            st.write("- Try rephrasing your question")
            st.write("- Make sure the paper is properly uploaded")
            st.write("- Try a more specific question")


def export_qa_data(qa_entry: dict):
    """Export a single Q&A interaction."""
    try:
        export_data = {
            "question_answer": qa_entry,
            "exported_at": datetime.now().isoformat(),
            "app_version": "AI Research Assistant v1.0"
        }
        
        json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="📥 Download Q&A",
            data=json_data,
            file_name=f"QA_{qa_entry['question'][:30].replace(' ', '_')}.json",
            mime="application/json",
            key="download_qa_unique"
        )
        
    except Exception as e:
        st.error(f"❌ Error exporting Q&A: {str(e)}")


def paper_analysis_page():
    """Paper analysis page."""
    st.markdown('<h2 class="section-header">📊 Paper Analysis</h2>',
                unsafe_allow_html=True)

    # Initialize assistant if needed
    assistant = get_assistant()
    if not assistant:
        st.error("❌ Failed to initialize AI assistant. Please refresh and try again.")
        return

    papers = assistant.list_papers()

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


def qa_history_page():
    """Q&A History page."""
    st.markdown('<h2 class="section-header">📚 Question & Answer History</h2>',
                unsafe_allow_html=True)

    if "qa_history" not in st.session_state or not st.session_state.qa_history:
        st.info("📝 No questions asked yet. Go to the 'Ask Questions' page to start!")
        return

    # Search and filter options
    col1, col2 = st.columns(2)
    with col1:
        search_query = st.text_input("🔍 Search Q&A history:", placeholder="Search questions or answers")
    with col2:
        show_count = st.selectbox("Show entries:", [10, 25, 50, "All"])

    # Filter Q&A history
    filtered_history = st.session_state.qa_history
    if search_query:
        filtered_history = [
            qa for qa in st.session_state.qa_history
            if search_query.lower() in qa['question'].lower() or 
               search_query.lower() in qa['answer'].answer.lower()
        ]

    # Limit results
    if show_count != "All":
        filtered_history = filtered_history[:show_count]

    st.write(f"📊 Showing {len(filtered_history)} of {len(st.session_state.qa_history)} Q&A entries")

    # Export all history
    if st.button("📥 Export All History"):
        export_all_history()

    # Display Q&A history
    for i, qa_entry in enumerate(filtered_history):
        timestamp = datetime.fromisoformat(qa_entry['timestamp']).strftime("%Y-%m-%d %H:%M")
        
        with st.expander(f"❓ {qa_entry['question'][:60]}... ({timestamp})"):
            st.markdown(f"**Question:** {qa_entry['question']}")
            st.markdown(f"**Answer:** {qa_entry['answer'].answer}")
            
            if qa_entry['answer'].confidence:
                confidence_color = "green" if qa_entry['answer'].confidence > 0.7 else "orange"
                st.markdown(f"**Confidence:** <span style='color: {confidence_color}'>{qa_entry['answer'].confidence:.2f}</span>", 
                           unsafe_allow_html=True)
            
            if qa_entry.get('paper_id'):
                st.markdown(f"**Paper ID:** `{qa_entry['paper_id']}`")
            
            if qa_entry.get('section'):
                st.markdown(f"**Section:** {qa_entry['section']}")
            
            if qa_entry['answer'].evidence_text:
                with st.expander("📋 Evidence"):
                    st.write(qa_entry['answer'].evidence_text)
            
            # Individual export
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 Export This Q&A", key=f"export_qa_{i}"):
                    export_qa_data(qa_entry)
            with col2:
                if st.button("🗑️ Remove", key=f"remove_qa_{i}", type="secondary"):
                    st.session_state.qa_history.remove(qa_entry)
                    st.rerun()


def export_all_history():
    """Export all Q&A history."""
    try:
        export_data = {
            "qa_history": st.session_state.qa_history,
            "total_entries": len(st.session_state.qa_history),
            "exported_at": datetime.now().isoformat(),
            "app_version": "AI Research Assistant v1.0"
        }
        
        json_data = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        
        st.download_button(
            label="📥 Download Complete History",
            data=json_data,
            file_name=f"qa_history_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            key="download_all_history"
        )
        
        st.success("✅ History export prepared!")
        
    except Exception as e:
        st.error(f"❌ Error exporting history: {str(e)}")


def search_papers_page():
    """Paper search page."""
    st.markdown('<h2 class="section-header">🔍 Search Papers</h2>',
                unsafe_allow_html=True)

    # Initialize assistant if needed
    assistant = get_assistant()
    if not assistant:
        st.error("❌ Failed to initialize AI assistant. Please refresh and try again.")
        return

    papers = assistant.list_papers()

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
            results = assistant.search_papers(
                search_query, max_results)

            if results:
                st.markdown(f"### 📊 Found {len(results)} relevant papers:")

                for i, result in enumerate(results, 1):
                    with st.expander(f"{i}. {result['title']} (Score: {result['similarity_score']:.3f})"):
                        display_paper_info(result)
            else:
                st.info("No papers found matching your search query.")


def settings_page():
    """Enhanced settings page with system management."""
    st.markdown('<h2 class="section-header">⚙️ Settings & System Management</h2>',
                unsafe_allow_html=True)

    # System status
    st.markdown("### 💻 System Status")
    col1, col2, col3 = st.columns(3)
    
    # Get counts safely
    if st.session_state.assistant_initialized and st.session_state.assistant:
        papers_count = len(st.session_state.assistant.list_papers())
    else:
        papers_count = 0
    qa_count = len(st.session_state.get('qa_history', []))
    
    with col1:
        st.metric("📄 Papers", papers_count)
    with col2:
        st.metric("❓ Q&A History", qa_count)
    with col3:
        # Estimate memory usage
        import sys
        memory_mb = sys.getsizeof(st.session_state) / (1024 * 1024)
        st.metric("💾 Memory", f"{memory_mb:.1f} MB")

    # Initialization status
    st.markdown("### 🤖 AI Assistant Status")
    if st.session_state.assistant_initialized:
        st.success("✅ AI Assistant initialized and ready")
        
        # Model settings
        st.markdown("### 🤖 AI Model Configuration")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Scientific Embeddings Model:**\nallenai/specter2")
            st.info("**Text Model:**\nallenai/scibert_scivocab_uncased")
        with col2:
            st.info("**QA Model:**\nmicrosoft/DialoGPT-medium")
            st.info("**Device:**\nAuto-detected (CPU/GPU)")
    else:
        st.info("🔄 AI Assistant will initialize when needed (lazy loading enabled for faster startup)")
        if st.button("🚀 Initialize AI Assistant Now"):
            get_assistant()
            st.rerun()

    # Processing settings
    st.markdown("### 🔧 Processing Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        extract_figures = st.checkbox("Extract figures and tables", value=True)
        extract_citations = st.checkbox("Extract citations and references", value=True)
        auto_analyze = st.checkbox("Auto-analyze contributions", value=True)
    
    with col2:
        max_context_length = st.slider("Max context length for QA:", 500, 3000, 2000)
        max_file_size = st.slider("Max file size (MB):", 10, 100, 50)
        qa_history_limit = st.slider("Q&A history limit:", 10, 200, 50)

    # Data management
    st.markdown("### �️ Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Clear Q&A History", type="secondary"):
            if st.session_state.get('confirm_clear_qa', False):
                st.session_state.qa_history = []
                st.session_state.confirm_clear_qa = False
                st.success("✅ Q&A history cleared!")
                st.rerun()
            else:
                st.session_state.confirm_clear_qa = True
                st.warning("⚠️ Click again to confirm")
    
    with col2:
        if st.button("🗑️ Clear All Papers", type="secondary"):
            if st.session_state.get('confirm_clear_papers', False):
                if st.session_state.assistant and st.session_state.assistant_initialized:
                    st.session_state.assistant.papers.clear()
                    st.session_state.assistant.paper_embeddings.clear()
                st.session_state.papers.clear()
                st.session_state.confirm_clear_papers = False
                st.success("✅ All papers cleared!")
                st.rerun()
            else:
                st.session_state.confirm_clear_papers = True
                st.warning("⚠️ Click again to confirm")
    
    with col3:
        if st.button("🔄 Reset All Data", type="secondary"):
            if st.session_state.get('confirm_reset_all', False):
                # Clear everything
                for key in list(st.session_state.keys()):
                    if key not in ['assistant']:  # Keep the assistant instance
                        del st.session_state[key]
                if st.session_state.assistant and st.session_state.assistant_initialized:
                    st.session_state.assistant.papers.clear()
                    st.session_state.assistant.paper_embeddings.clear()
                st.success("✅ All data reset!")
                st.rerun()
            else:
                st.session_state.confirm_reset_all = True
                st.warning("⚠️ This will delete EVERYTHING. Click again to confirm.")

    # Memory optimization
    st.markdown("### � Performance Optimization")
    
    if st.button("🧼 Optimize Memory"):
        optimize_memory()
    
    # Export/Import settings
    st.markdown("### 📦 Backup & Restore")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("� Export All Data"):
            export_complete_workspace()
    
    with col2:
        uploaded_backup = st.file_uploader("📤 Import Backup", type=['json'])
        if uploaded_backup and st.button("🔄 Restore Backup"):
            import_workspace_backup(uploaded_backup)

    # Advanced settings
    with st.expander("🔬 Advanced Settings"):
        st.markdown("**Experimental Features:**")
        enable_caching = st.checkbox("Enable response caching", value=True)
        debug_mode = st.checkbox("Debug mode", value=False)
        verbose_logging = st.checkbox("Verbose logging", value=False)
        
        if debug_mode:
            st.markdown("**Debug Information:**")
            st.json({
                "session_state_keys": list(st.session_state.keys()),
                "papers_count": papers_count,
                "qa_history_count": qa_count,
                "memory_usage_mb": f"{memory_mb:.1f}"
            })


def optimize_memory():
    """Optimize memory usage."""
    try:
        import gc
        
        # Run garbage collection
        gc.collect()
        
        # Limit Q&A history
        if "qa_history" in st.session_state and len(st.session_state.qa_history) > 50:
            st.session_state.qa_history = st.session_state.qa_history[:50]
        
        # Clear temporary data
        temp_keys = [k for k in st.session_state.keys() if k.startswith('temp_') or k.startswith('confirm_')]
        for key in temp_keys:
            del st.session_state[key]
        
        st.success("✅ Memory optimized!")
        
    except Exception as e:
        st.error(f"❌ Error optimizing memory: {str(e)}")


def export_complete_workspace():
    """Export complete workspace data."""
    try:
        papers_data = {}
        if st.session_state.assistant and st.session_state.assistant_initialized:
            papers_data = dict(st.session_state.assistant.papers)
            
        workspace_data = {
            "papers": papers_data,
            "qa_history": st.session_state.get('qa_history', []),
            "settings": {
                "papers_count": len(papers_data),
                "qa_count": len(st.session_state.get('qa_history', []))
            },
            "exported_at": datetime.now().isoformat(),
            "app_version": "AI Research Assistant v1.0"
        }
        
        json_data = json.dumps(workspace_data, indent=2, ensure_ascii=False, default=str)
        
        st.download_button(
            label="📥 Download Complete Workspace",
            data=json_data,
            file_name=f"ai_research_workspace_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            key="download_workspace"
        )
        
        st.success("✅ Workspace export prepared!")
        
    except Exception as e:
        st.error(f"❌ Error exporting workspace: {str(e)}")


def import_workspace_backup(uploaded_file):
    """Import workspace backup."""
    try:
        backup_data = json.load(uploaded_file)
        
        # Restore papers (basic info only - embeddings would need regeneration)
        if "papers" in backup_data:
            st.info("⚠️ Note: Paper embeddings will need to be regenerated after import")
        
        # Restore Q&A history
        if "qa_history" in backup_data:
            st.session_state.qa_history = backup_data["qa_history"]
        
        st.success("✅ Backup imported successfully!")
        st.info("💡 You may need to re-upload papers for full functionality")
        
    except Exception as e:
        st.error(f"❌ Error importing backup: {str(e)}")


def export_paper_data(paper_id: str):
    """Export paper data and analysis."""
    try:
        assistant = get_assistant()
        if not assistant:
            st.error("❌ Failed to initialize AI assistant")
            return
            
        paper_info = assistant.get_paper_info(paper_id)
        
        # Create export data
        export_data = {
            "paper_info": paper_info,
            "timestamp": datetime.now().isoformat(),
            "exported_by": "AI Research Assistant"
        }
        
        # Add recent questions and answers if available
        if hasattr(st.session_state, 'recent_qa') and paper_id in st.session_state.recent_qa:
            export_data["recent_qa"] = st.session_state.recent_qa[paper_id]
        
        # Convert to JSON
        json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Create download button
        st.download_button(
            label="📥 Download Paper Analysis",
            data=json_data,
            file_name=f"{paper_info['title'][:50]}_analysis.json",
            mime="application/json",
            key=f"download_{paper_id}"
        )
        
        st.success("✅ Export data prepared!")
        
    except Exception as e:
        st.error(f"❌ Error exporting paper data: {str(e)}")


def delete_paper(paper_id: str):
    """Delete a paper from the system."""
    try:
        assistant = get_assistant()
        
        # Remove from assistant if it exists
        if assistant:
            if paper_id in assistant.papers:
                del assistant.papers[paper_id]
            
            if paper_id in assistant.paper_embeddings:
                del assistant.paper_embeddings[paper_id]
        
        # Remove from session state
        if paper_id in st.session_state.papers:
            del st.session_state.papers[paper_id]
        
        # Clear confirmation flag
        confirm_key = f"confirm_delete_{paper_id}"
        if confirm_key in st.session_state:
            del st.session_state[confirm_key]
        
        st.success("✅ Paper deleted successfully!")
        
    except Exception as e:
        st.error(f"❌ Error deleting paper: {str(e)}")


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
    """Display a research answer with enhanced formatting."""
    st.markdown('<div class="answer-box">', unsafe_allow_html=True)

    st.markdown(f"**❓ Question:** {question}")
    
    # Enhanced answer display
    st.markdown("**💡 Answer:**")
    st.markdown(answer.answer)

    # Confidence indicator with better styling
    if hasattr(answer, 'confidence') and answer.confidence is not None:
        confidence = answer.confidence
        if confidence > 0.8:
            confidence_color = "#28a745"  # Green
            confidence_emoji = "🟢"
        elif confidence > 0.6:
            confidence_color = "#ffc107"  # Yellow
            confidence_emoji = "🟡"
        else:
            confidence_color = "#dc3545"  # Red
            confidence_emoji = "🔴"
            
        st.markdown(
            f"**🎯 Confidence:** {confidence_emoji} <span style='color: {confidence_color}; font-weight: bold;'>{confidence:.1%}</span>", 
            unsafe_allow_html=True
        )

    # Evidence section with better formatting
    if hasattr(answer, 'evidence_text') and answer.evidence_text:
        with st.expander("📋 Supporting Evidence", expanded=False):
            st.markdown('<div class="evidence-box">', unsafe_allow_html=True)
            st.markdown(answer.evidence_text)
            st.markdown('</div>', unsafe_allow_html=True)

    # Additional metadata
    col1, col2, col3 = st.columns(3)
    
    if hasattr(answer, 'source_section') and answer.source_section:
        with col1:
            st.info(f"📍 **Section:** {answer.source_section}")

    if hasattr(answer, 'page_number') and answer.page_number:
        with col2:
            st.info(f"📄 **Page:** {answer.page_number}")
    
    if hasattr(answer, 'paper_id') and answer.paper_id:
        with col3:
            st.info(f"🆔 **Paper ID:** `{answer.paper_id[:8]}...`")

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Copy Answer", key=f"copy_{hash(question)}"):
            st.code(answer.answer)
    with col2:
        if st.button("🔄 Ask Follow-up", key=f"followup_{hash(question)}"):
            st.session_state.followup_question = question
    with col3:
        if st.button("👍 Helpful", key=f"helpful_{hash(question)}"):
            st.success("Thanks for the feedback!")

    st.markdown('</div>', unsafe_allow_html=True)


def display_paper_overview(paper_id: str):
    """Display paper overview."""
    assistant = get_assistant()
    if not assistant:
        st.error("❌ Failed to initialize AI assistant")
        return
        
    paper_info = assistant.get_paper_info(paper_id)
    display_paper_info(paper_info)

    # Generate summary
    if st.button("📄 Generate Summary"):
        with st.spinner("Generating summary..."):
            summary = assistant.summarize_paper(paper_id)
            st.markdown("### 📝 Paper Summary")
            st.write(summary)


def display_contribution_analysis(paper_id: str):
    """Display contribution analysis."""
    if st.button("🎯 Analyze Contributions"):
        assistant = get_assistant()
        if not assistant:
            st.error("❌ Failed to initialize AI assistant")
            return
            
        with st.spinner("Analyzing contributions..."):
            analysis = assistant.analyze_contribution(paper_id)

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
        assistant = get_assistant()
        if not assistant:
            st.error("❌ Failed to initialize AI assistant")
            return
            
        with st.spinner("Analyzing methodology..."):
            analysis = assistant.analyze_methodology(paper_id)

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
        assistant = get_assistant()
        if not assistant:
            st.error("❌ Failed to initialize AI assistant")
            return
            
        with st.spinner("Analyzing results..."):
            # Ask results-related questions
            results_answer = assistant.ask_question(
                "What are the results?", paper_id)
            performance_answer = assistant.ask_question(
                "What is the performance?", paper_id)

            st.markdown("### 📈 Results Analysis")

            st.markdown("**Results:**")
            st.write(results_answer.answer)

            st.markdown("**Performance:**")
            st.write(performance_answer.answer)


if __name__ == "__main__":
    main()
