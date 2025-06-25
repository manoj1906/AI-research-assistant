"""
Main Research Assistant class that coordinates all components.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import json
import uuid
from datetime import datetime

from .config import Config
from .paper_processor.pdf_parser import AcademicPDFParser, ParsedPaper
from .research_embeddings.academic_embeddings import MultimodalResearchEmbeddings
from .research_qa.academic_qa import AcademicQuestionAnswering, ResearchAnswer

logger = logging.getLogger(__name__)


class ResearchAssistant:
    """Main AI Research Assistant for academic papers."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the research assistant."""
        self.config = config or Config()

        # Initialize components
        self.pdf_parser = AcademicPDFParser(self.config)
        self.embeddings = MultimodalResearchEmbeddings(self.config)
        self.qa_system = AcademicQuestionAnswering(self.config)

        # Paper storage
        self.papers: Dict[str, ParsedPaper] = {}
        self.paper_embeddings: Dict[str, Dict[str, Any]] = {}

        # Load existing papers if available
        self._load_existing_papers()

        logger.info("Research Assistant initialized successfully")

    def upload_paper(self, file_path: str, paper_id: Optional[str] = None) -> str:
        """
        Upload and process a research paper.

        Args:
            file_path: Path to the PDF file
            paper_id: Optional custom ID for the paper

        Returns:
            Paper ID for future reference
        """
        if paper_id is None:
            paper_id = str(uuid.uuid4())

        logger.info(f"Processing paper: {file_path}")

        try:
            # Parse the PDF
            parsed_paper = self.pdf_parser.parse_paper(file_path)

            # Generate embeddings
            embeddings = self._generate_paper_embeddings(parsed_paper)

            # Store paper and embeddings
            self.papers[paper_id] = parsed_paper
            self.paper_embeddings[paper_id] = embeddings

            # Save to disk
            self._save_paper_data(paper_id, parsed_paper, embeddings)

            logger.info(f"Successfully processed paper {paper_id}")
            return paper_id

        except Exception as e:
            logger.error(f"Error processing paper {file_path}: {e}")
            raise

    def ask_question(self,
                     question: str,
                     paper_id: Optional[str] = None,
                     section: Optional[str] = None) -> ResearchAnswer:
        """
        Ask a question about a research paper.

        Args:
            question: The research question
            paper_id: ID of the paper to query (if None, search all papers)
            section: Specific section to focus on

        Returns:
            Answer with evidence and context
        """
        logger.info(f"Answering question: {question}")

        if paper_id and paper_id not in self.papers:
            raise ValueError(f"Paper {paper_id} not found")

        if paper_id:
            # Answer question about specific paper
            paper = self.papers[paper_id]

            if section:
                return self.qa_system.answer_section_question(question, section, paper)
            else:
                return self.qa_system.answer_question(question, paper)
        else:
            # Search across all papers
            return self._answer_multi_paper_question(question)

    def summarize_paper(self, paper_id: str, section: Optional[str] = None) -> str:
        """
        Generate a summary of a paper or specific section.

        Args:
            paper_id: ID of the paper
            section: Specific section to summarize (optional)

        Returns:
            Summary text
        """
        if paper_id not in self.papers:
            raise ValueError(f"Paper {paper_id} not found")

        paper = self.papers[paper_id]

        if section:
            # Summarize specific section
            question = f"Summarize the {section} section"
            answer = self.qa_system.answer_section_question(
                question, section, paper)
            return answer.answer
        else:
            # Summarize entire paper
            summary_parts = []

            # Title and authors
            summary_parts.append(f"Title: {paper.metadata.title}")
            if paper.metadata.authors:
                summary_parts.append(
                    f"Authors: {', '.join(paper.metadata.authors)}")

            # Abstract
            if paper.metadata.abstract:
                summary_parts.append(f"Abstract: {paper.metadata.abstract}")

            # Main sections summary
            for section in paper.sections[:3]:  # First 3 sections
                if len(section.content) > 100:
                    summary_parts.append(
                        f"{section.title}: {section.content[:200]}...")

            return "\n\n".join(summary_parts)

    def analyze_contribution(self, paper_id: str) -> Dict[str, Any]:
        """
        Analyze the main contributions of a paper.

        Args:
            paper_id: ID of the paper

        Returns:
            Analysis of contributions
        """
        if paper_id not in self.papers:
            raise ValueError(f"Paper {paper_id} not found")

        paper = self.papers[paper_id]

        # Ask contribution-related questions
        contribution_answer = self.qa_system.answer_question(
            "What are the main contributions?", paper)
        novelty_answer = self.qa_system.answer_question(
            "What is novel about this work?", paper)
        significance_answer = self.qa_system.answer_question(
            "What is the significance of this research?", paper)

        return {
            "main_contributions": contribution_answer.answer,
            "novelty": novelty_answer.answer,
            "significance": significance_answer.answer,
            "confidence_scores": {
                "contributions": contribution_answer.confidence,
                "novelty": novelty_answer.confidence,
                "significance": significance_answer.confidence
            }
        }

    def analyze_methodology(self, paper_id: str) -> Dict[str, Any]:
        """
        Analyze the methodology of a paper.

        Args:
            paper_id: ID of the paper

        Returns:
            Analysis of methodology
        """
        if paper_id not in self.papers:
            raise ValueError(f"Paper {paper_id} not found")

        paper = self.papers[paper_id]

        # Ask methodology-related questions
        method_answer = self.qa_system.answer_question(
            "What is the methodology?", paper)
        approach_answer = self.qa_system.answer_question(
            "What approach was used?", paper)
        dataset_answer = self.qa_system.answer_question(
            "What datasets were used?", paper)

        return {
            "methodology": method_answer.answer,
            "approach": approach_answer.answer,
            "datasets": dataset_answer.answer,
            "confidence_scores": {
                "methodology": method_answer.confidence,
                "approach": approach_answer.confidence,
                "datasets": dataset_answer.confidence
            }
        }

    def compare_papers(self, paper_ids: List[str], aspect: str = "methodology") -> Dict[str, Any]:
        """
        Compare multiple papers on a specific aspect.

        Args:
            paper_ids: List of paper IDs to compare
            aspect: Aspect to compare (methodology, results, contributions)

        Returns:
            Comparison analysis
        """
        if len(paper_ids) < 2:
            raise ValueError("Need at least 2 papers to compare")

        comparisons = {}

        for paper_id in paper_ids:
            if paper_id not in self.papers:
                raise ValueError(f"Paper {paper_id} not found")

            paper = self.papers[paper_id]

            if aspect == "methodology":
                answer = self.qa_system.answer_question(
                    "What is the methodology?", paper)
            elif aspect == "contributions":
                answer = self.qa_system.answer_question(
                    "What are the main contributions?", paper)
            elif aspect == "results":
                answer = self.qa_system.answer_question(
                    "What are the results?", paper)
            else:
                answer = self.qa_system.answer_question(
                    f"What about {aspect}?", paper)

            comparisons[paper_id] = {
                "title": paper.metadata.title,
                "analysis": answer.answer,
                "confidence": answer.confidence
            }

        return {
            "aspect": aspect,
            "papers": comparisons,
            "comparison_summary": self._generate_comparison_summary(comparisons, aspect)
        }

    def get_paper_info(self, paper_id: str) -> Dict[str, Any]:
        """
        Get basic information about a paper.

        Args:
            paper_id: ID of the paper

        Returns:
            Paper information
        """
        if paper_id not in self.papers:
            raise ValueError(f"Paper {paper_id} not found")

        paper = self.papers[paper_id]

        return {
            "paper_id": paper_id,
            "title": paper.metadata.title,
            "authors": paper.metadata.authors,
            "abstract": paper.metadata.abstract,
            "keywords": paper.metadata.keywords,
            "venue": paper.metadata.venue,
            "year": paper.metadata.year,
            "page_count": paper.page_count,
            "sections": [{"title": s.title, "pages": f"{s.page_start}-{s.page_end}"} for s in paper.sections],
            "figures_count": len(paper.figures),
            "tables_count": len(paper.tables),
            "references_count": len(paper.references)
        }

    def list_papers(self) -> List[Dict[str, Any]]:
        """
        List all uploaded papers.

        Returns:
            List of paper information
        """
        papers_list = []

        for paper_id, paper in self.papers.items():
            papers_list.append({
                "paper_id": paper_id,
                "title": paper.metadata.title,
                "authors": paper.metadata.authors,
                "year": paper.metadata.year,
                "page_count": paper.page_count
            })

        return papers_list

    def search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search papers by content similarity.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of relevant papers with similarity scores
        """
        if not self.papers:
            return []

        # Generate query embedding
        query_embedding = self.embeddings.encode_research_question(query)

        # Calculate similarity with all papers
        similarities = []

        for paper_id, embeddings in self.paper_embeddings.items():
            # Use abstract embedding for similarity
            if 'abstract' in embeddings:
                abstract_embedding = embeddings['abstract']
                similarity = self._calculate_similarity(
                    query_embedding, abstract_embedding)
                similarities.append((paper_id, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top results
        results = []
        for paper_id, similarity in similarities[:max_results]:
            paper_info = self.get_paper_info(paper_id)
            paper_info['similarity_score'] = similarity
            results.append(paper_info)

        return results

    def _generate_paper_embeddings(self, paper: ParsedPaper) -> Dict[str, Any]:
        """Generate embeddings for a parsed paper."""
        embeddings = {}

        # Title embedding
        if paper.metadata.title:
            embeddings['title'] = self.embeddings.encode_for_search(
                paper.metadata.title,
                content_type="title"
            )

        # Abstract embedding
        if paper.metadata.abstract:
            embeddings['abstract'] = self.embeddings.encode_for_search(
                paper.metadata.abstract,
                content_type="abstract"
            )

        # Section embeddings
        section_embeddings = []
        for section in paper.sections:
            section_text = f"{section.title} {section.content}"
            section_emb = self.embeddings.encode_for_search(section_text)
            section_embeddings.append(section_emb)

        if section_embeddings:
            embeddings['sections'] = section_embeddings

        return embeddings

    def _answer_multi_paper_question(self, question: str) -> ResearchAnswer:
        """Answer a question across multiple papers."""
        if not self.papers:
            return ResearchAnswer(
                answer="No papers available to search.",
                confidence=0.0,
                evidence_text=""
            )

        # Search for most relevant papers
        relevant_papers = self.search_papers(question, max_results=3)

        if not relevant_papers:
            return ResearchAnswer(
                answer="No relevant papers found for this question.",
                confidence=0.0,
                evidence_text=""
            )

        # Answer question using the most relevant paper
        best_paper_id = relevant_papers[0]['paper_id']
        paper = self.papers[best_paper_id]

        answer = self.qa_system.answer_question(question, paper)
        answer.context = f"Based on analysis of: {paper.metadata.title}"

        return answer

    def _calculate_similarity(self, emb1, emb2):
        """Calculate cosine similarity between two embeddings."""
        import numpy as np

        # Ensure embeddings are 1D
        emb1 = emb1.flatten() if emb1.ndim > 1 else emb1
        emb2 = emb2.flatten() if emb2.ndim > 1 else emb2

        # Calculate cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _generate_comparison_summary(self, comparisons: Dict, aspect: str) -> str:
        """Generate a summary of paper comparisons."""
        summary = f"Comparison of {len(comparisons)} papers on {aspect}:\n\n"

        for paper_id, data in comparisons.items():
            summary += f"• {data['title'][:60]}...: {data['analysis'][:100]}...\n"

        return summary

    def _save_paper_data(self, paper_id: str, paper: ParsedPaper, embeddings: Dict):
        """Save paper data to disk."""
        # Create paper directory
        paper_dir = Path(self.config.processing.processed_dir) / paper_id
        paper_dir.mkdir(exist_ok=True)

        # Save paper metadata and structure
        paper_data = {
            "metadata": {
                "title": paper.metadata.title,
                "authors": paper.metadata.authors,
                "abstract": paper.metadata.abstract,
                "keywords": paper.metadata.keywords,
                "venue": paper.metadata.venue,
                "year": paper.metadata.year,
                "doi": paper.metadata.doi,
                "arxiv_id": paper.metadata.arxiv_id
            },
            "sections": [
                {
                    "title": s.title,
                    "content": s.content,
                    "level": s.level,
                    "page_start": s.page_start,
                    "page_end": s.page_end
                }
                for s in paper.sections
            ],
            "figures": [
                {
                    "caption": f.caption,
                    "image_path": f.image_path,
                    "page_number": f.page_number,
                    "figure_number": f.figure_number
                }
                for f in paper.figures
            ],
            "tables": [
                {
                    "caption": t.caption,
                    "content": t.content,
                    "page_number": t.page_number,
                    "table_number": t.table_number
                }
                for t in paper.tables
            ],
            "references": paper.references,
            "page_count": paper.page_count,
            "processed_at": datetime.now().isoformat()
        }

        # Save to JSON
        with open(paper_dir / "paper_data.json", "w") as f:
            json.dump(paper_data, f, indent=2)

        # Save embeddings (simplified - in production might use vector DB)
        embeddings_data = {}
        for key, emb in embeddings.items():
            if isinstance(emb, list):
                embeddings_data[key] = [e.tolist() if hasattr(
                    e, 'tolist') else e for e in emb]
            else:
                embeddings_data[key] = emb.tolist() if hasattr(
                    emb, 'tolist') else emb

        with open(paper_dir / "embeddings.json", "w") as f:
            json.dump(embeddings_data, f)

    def _load_existing_papers(self):
        """Load previously processed papers."""
        processed_dir = Path(self.config.processing.processed_dir)

        if not processed_dir.exists():
            return

        for paper_dir in processed_dir.iterdir():
            if paper_dir.is_dir():
                try:
                    # Load paper data
                    paper_data_file = paper_dir / "paper_data.json"
                    embeddings_file = paper_dir / "embeddings.json"

                    if paper_data_file.exists() and embeddings_file.exists():
                        with open(paper_data_file) as f:
                            paper_data = json.load(f)

                        with open(embeddings_file) as f:
                            embeddings_data = json.load(f)

                        # Reconstruct paper object (simplified)
                        paper_id = paper_dir.name

                        # Store in memory (in production, might load on demand)
                        # For now, just log that papers are available
                        logger.info(f"Found processed paper: {paper_id}")

                except Exception as e:
                    logger.warning(
                        f"Error loading paper {paper_dir.name}: {e}")
