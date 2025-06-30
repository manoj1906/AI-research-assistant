"""
Academic question answering system specialized for research papers.
"""

import re
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import torch

from ..paper_processor.pdf_parser import ParsedPaper, PaperSection
from ..research_embeddings.academic_embeddings import MultimodalResearchEmbeddings

logger = logging.getLogger(__name__)


@dataclass
class ResearchAnswer:
    """Answer to a research question with evidence."""
    answer: str
    confidence: float
    evidence_text: str
    source_section: Optional[str] = None
    page_number: Optional[int] = None
    context: Optional[str] = None
    # contribution, methodology, results, etc.
    answer_type: Optional[str] = None


@dataclass
class QuestionContext:
    """Context for answering questions."""
    question: str
    question_type: str
    target_sections: List[str]
    max_context_length: int = 2000


class AcademicQuestionAnswering:
    """Question answering system for academic papers."""

    def __init__(self, config: Any):
        self.config = config
        self.embeddings = MultimodalResearchEmbeddings(config)

        # Load QA model
        self._load_qa_model()

        # Question type patterns
        self.question_patterns = self._compile_question_patterns()

        # Section priorities for different question types
        self.section_priorities = {
            'contribution': ['abstract', 'introduction', 'conclusion'],
            'methodology': ['methodology', 'methods', 'approach', 'model'],
            'results': ['results', 'experiments', 'evaluation'],
            'limitations': ['discussion', 'limitations', 'conclusion'],
            'related_work': ['related_work', 'background', 'literature_review'],
            'summary': ['abstract', 'conclusion'],
            'dataset': ['experiments', 'evaluation', 'methodology'],
            'performance': ['results', 'experiments', 'evaluation']
        }

    def _load_qa_model(self):
        """Load question answering model."""
        try:
            logger.info("Loading question answering model")

            # Use a scientific QA model if available, otherwise use general
            qa_model_name = getattr(
                self.config.models, 'qa_model', 'distilbert-base-cased-distilled-squad')

            self.qa_pipeline = pipeline(
                "question-answering",
                model=qa_model_name,
                tokenizer=qa_model_name,
                device=0 if torch.cuda.is_available() and self.config.models.device == "auto" else -1
            )

            logger.info("Question answering model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load QA model: {e}")
            # Fallback to a simpler approach
            self.qa_pipeline = None

    def _compile_question_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for question type detection."""
        patterns = {
            'contribution': [
                re.compile(
                    r'(?i)(main|key|primary|novel|new)\s*(contribution|novelty)', re.IGNORECASE),
                re.compile(
                    r'(?i)what.*?(novel|new|contribution|significance)', re.IGNORECASE),
                re.compile(
                    r'(?i)(significance|importance).*?(work|research|paper)', re.IGNORECASE),
            ],
            'methodology': [
                re.compile(
                    r'(?i)(method|approach|algorithm|technique|procedure)', re.IGNORECASE),
                re.compile(
                    r'(?i)how.*?(implement|design|build|create|develop)', re.IGNORECASE),
                re.compile(
                    r'(?i)(experimental|evaluation)\s*(setup|design|protocol)', re.IGNORECASE),
            ],
            'results': [
                re.compile(
                    r'(?i)(result|finding|outcome|performance|accuracy)', re.IGNORECASE),
                re.compile(
                    r'(?i)what.*?(achieve|obtain|find|discover)', re.IGNORECASE),
                re.compile(
                    r'(?i)(evaluation|experiment).*?(result|outcome)', re.IGNORECASE),
            ],
            'limitations': [
                re.compile(
                    r'(?i)(limitation|weakness|constraint|problem)', re.IGNORECASE),
                re.compile(
                    r'(?i)what.*?(limit|constrain|prevent|issue)', re.IGNORECASE),
                re.compile(r'(?i)(challenge|difficulty|drawback)',
                           re.IGNORECASE),
            ],
            'summary': [
                re.compile(
                    r'(?i)(summarize|summary|overview|abstract)', re.IGNORECASE),
                re.compile(r'(?i)what.*?(about|discuss|cover)', re.IGNORECASE),
                re.compile(
                    r'(?i)(explain|describe).*?(paper|work|research)', re.IGNORECASE),
            ],
            'dataset': [
                re.compile(r'(?i)(dataset|data|corpus|benchmark)',
                           re.IGNORECASE),
                re.compile(r'(?i)what.*?(data|dataset|corpus)', re.IGNORECASE),
                re.compile(
                    r'(?i)(evaluation|experiment).*?(data|dataset)', re.IGNORECASE),
            ],
            'comparison': [
                re.compile(
                    r'(?i)(compare|comparison|versus|vs|differ)', re.IGNORECASE),
                re.compile(r'(?i)how.*?(different|similar|compare)',
                           re.IGNORECASE),
                re.compile(
                    r'(?i)(baseline|previous|prior).*?(work|method)', re.IGNORECASE),
            ]
        }

        return patterns

    def detect_question_type(self, question: str) -> str:
        """Detect the type of research question with improved general question handling."""
        question_lower = question.lower().strip()
        
        # Handle very short/generic questions explicitly
        very_generic = [
            'what is this',
            'what is that',
            'what is it',
            'describe this',
            'tell me about this',
            'what does this say',
            'what is the content',
            'what is in this',
            'explain this',
            'summarize this'
        ]
        
        if any(generic in question_lower for generic in very_generic):
            return 'summary'  # Treat as summary rather than general for better handling
        
        # Check patterns for each question type
        for question_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if pattern.search(question_lower):
                    return question_type

        # Better classification for borderline cases
        # If question contains "what" and is short, likely wants summary
        if 'what' in question_lower and len(question.split()) <= 5:
            return 'summary'
        
        # If question asks about "how", likely methodology
        if any(word in question_lower for word in ['how', 'method', 'approach', 'technique']):
            return 'methodology'
            
        # Default to general if no specific type detected
        return 'general'

    def answer_question(self, question: str, paper: ParsedPaper) -> ResearchAnswer:
        """Answer a question about a research paper."""
        logger.info(f"Answering question: {question}")

        # Detect question type
        question_type = self.detect_question_type(question)
        logger.info(f"Detected question type: {question_type}")

        # Get relevant sections
        relevant_sections = self._get_relevant_sections(question_type, paper)

        # Build context
        context = self._build_context(relevant_sections, question)

        # Generate answer
        if self.qa_pipeline and context:
            answer = self._generate_answer_with_model(question, context)
        else:
            answer = self._generate_answer_with_rules(
                question, question_type, relevant_sections)

        return answer

    def _get_relevant_sections(self, question_type: str, paper: ParsedPaper) -> List[PaperSection]:
        """Get sections most relevant to the question type."""
        relevant_sections = []

        # Get priority sections for this question type
        priority_sections = self.section_priorities.get(
            question_type, ['abstract'])

        # Find matching sections
        for section in paper.sections:
            section_title_lower = section.title.lower()

            # Check if section matches priority keywords
            for priority in priority_sections:
                if priority.replace('_', ' ') in section_title_lower:
                    relevant_sections.append(section)
                    break

        # If no specific sections found, use abstract and introduction
        if not relevant_sections:
            for section in paper.sections:
                section_title_lower = section.title.lower()
                if any(keyword in section_title_lower for keyword in ['abstract', 'introduction']):
                    relevant_sections.append(section)

        # Sort by relevance (priority sections first)
        def section_priority_score(section):
            section_title_lower = section.title.lower()
            for i, priority in enumerate(priority_sections):
                if priority.replace('_', ' ') in section_title_lower:
                    return i
            return len(priority_sections)

        relevant_sections.sort(key=section_priority_score)

        return relevant_sections[:3]  # Limit to top 3 sections

    def _build_context(self, sections: List[PaperSection], question: str) -> str:
        """Build context for question answering."""
        context_parts = []
        max_length = self.config.research.max_context_length
        current_length = 0

        for section in sections:
            section_text = f"{section.title}\n{section.content}"

            if current_length + len(section_text) <= max_length:
                context_parts.append(section_text)
                current_length += len(section_text)
            else:
                # Truncate to fit
                remaining_length = max_length - current_length
                if remaining_length > 100:  # Only add if significant space remains
                    truncated_text = section_text[:remaining_length] + "..."
                    context_parts.append(truncated_text)
                break

        return "\n\n".join(context_parts)

    def _generate_answer_with_model(self, question: str, context: str) -> ResearchAnswer:
        """Generate answer using the QA model."""
        try:
            result = self.qa_pipeline(question=question, context=context)

            answer_text = result['answer']
            confidence = result['score']

            # Extract source information
            start = result['start']
            end = result['end']
            evidence_text = context[max(
                0, start-100):min(len(context), end+100)]

            return ResearchAnswer(
                answer=answer_text,
                confidence=confidence,
                evidence_text=evidence_text,
                context=context[:500] +
                "..." if len(context) > 500 else context
            )

        except Exception as e:
            logger.error(f"Error generating answer with model: {e}")
            # Fallback to rule-based approach
            return self._generate_answer_with_rules(question, "general", [])

    def _generate_answer_with_rules(self, question: str, question_type: str, sections: List[PaperSection]) -> ResearchAnswer:
        """Generate answer using rule-based approach."""

        if question_type == 'contribution':
            return self._answer_contribution_question(sections)
        elif question_type == 'methodology':
            return self._answer_methodology_question(sections)
        elif question_type == 'results':
            return self._answer_results_question(sections)
        elif question_type == 'summary':
            return self._answer_summary_question(sections)
        elif question_type == 'limitations':
            return self._answer_limitations_question(sections)
        else:
            return self._answer_general_question(question, sections)

    def _answer_contribution_question(self, sections: List[PaperSection]) -> ResearchAnswer:
        """Answer questions about paper contributions."""
        contribution_text = ""

        for section in sections:
            content = section.content.lower()

            # Look for contribution indicators
            contribution_patterns = [
                r'contribution[s]?\s*(?:of this work|include|are|is)',
                r'we\s*(?:propose|introduce|present|develop|contribute)',
                r'(?:main|key|primary|novel)\s*(?:contribution|novelty|innovation)',
                r'our\s*(?:approach|method|work|contribution)',
                r'(?:significance|importance).*?(?:work|research)'
            ]

            for pattern in contribution_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Extract surrounding context
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 200)
                    context = content[start:end]
                    contribution_text += context + " "

        if contribution_text:
            answer = contribution_text.strip()[:500]
        else:
            answer = "The main contributions are not explicitly stated in the available sections."

        return ResearchAnswer(
            answer=answer,
            confidence=0.7,
            evidence_text=contribution_text[:300] if contribution_text else "",
            answer_type="contribution"
        )

    def _answer_methodology_question(self, sections: List[PaperSection]) -> ResearchAnswer:
        """Answer questions about methodology."""
        method_text = ""

        for section in sections:
            if any(keyword in section.title.lower() for keyword in ['method', 'approach', 'model']):
                method_text = section.content[:500]
                break

        if not method_text:
            # Look for methodology descriptions in any section
            for section in sections:
                content = section.content.lower()
                if any(keyword in content for keyword in ['algorithm', 'approach', 'method', 'technique']):
                    method_text = section.content[:500]
                    break

        if method_text:
            answer = method_text
        else:
            answer = "The methodology is not clearly described in the available sections."

        return ResearchAnswer(
            answer=answer,
            confidence=0.7,
            evidence_text=method_text[:300] if method_text else "",
            answer_type="methodology"
        )

    def _answer_results_question(self, sections: List[PaperSection]) -> ResearchAnswer:
        """Answer questions about results."""
        results_text = ""

        for section in sections:
            if any(keyword in section.title.lower() for keyword in ['result', 'experiment', 'evaluation']):
                results_text = section.content[:500]
                break

        if results_text:
            answer = results_text
        else:
            answer = "The results are not available in the provided sections."

        return ResearchAnswer(
            answer=answer,
            confidence=0.6,
            evidence_text=results_text[:300] if results_text else "",
            answer_type="results"
        )

    def _answer_summary_question(self, sections: List[PaperSection]) -> ResearchAnswer:
        """Answer summary questions with improved content extraction."""
        # Use abstract if available, otherwise combine introduction and conclusion
        summary_text = ""
        source_section = None

        # First, try to find abstract
        for section in sections:
            if 'abstract' in section.title.lower():
                summary_text = section.content.strip()
                source_section = section.title
                break

        # If no abstract, look for introduction or first substantial section
        if not summary_text:
            for section in sections:
                if any(keyword in section.title.lower() for keyword in ['introduction', 'intro', 'background']):
                    # Take first part of introduction
                    summary_text = section.content[:800].strip()
                    source_section = section.title
                    break
            
            # If still no summary, use first section with substantial content
            if not summary_text:
                for section in sections:
                    if len(section.content.strip()) > 200:
                        summary_text = section.content[:600].strip()
                        source_section = section.title
                        break

        # Final fallback: combine multiple sections
        if not summary_text and sections:
            combined_text = " ".join([s.content for s in sections[:3] if len(s.content.strip()) > 50])
            summary_text = combined_text[:700].strip()
            source_section = "Multiple sections"

        # Ensure we have something to return
        if not summary_text:
            summary_text = "This appears to be a research paper, but I couldn't extract a clear summary from the available content. Please try asking about specific aspects like methodology, results, or contributions."

        return ResearchAnswer(
            answer=summary_text,
            confidence=0.8 if source_section else 0.4,
            evidence_text=summary_text[:300],
            source_section=source_section,
            answer_type="summary"
        )

    def _answer_limitations_question(self, sections: List[PaperSection]) -> ResearchAnswer:
        """Answer questions about limitations."""
        limitations_text = ""

        for section in sections:
            content = section.content.lower()

            # Look for limitation indicators
            limitation_patterns = [
                r'limitation[s]?\s*(?:of|include|are|is)',
                r'(?:however|but|although).*?(?:limitation|constraint|issue)',
                r'(?:weakness|drawback|shortcoming)',
                r'future\s*work',
                r'(?:cannot|unable to|difficult to)'
            ]

            for pattern in limitation_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 150)
                    context = content[start:end]
                    limitations_text += context + " "

        if limitations_text:
            answer = limitations_text.strip()[:500]
        else:
            answer = "Limitations are not explicitly discussed in the available sections."

        return ResearchAnswer(
            answer=answer,
            confidence=0.6,
            evidence_text=limitations_text[:300] if limitations_text else "",
            answer_type="limitations"
        )

    def _answer_general_question(self, question: str, sections: List[PaperSection]) -> ResearchAnswer:
        """Answer general questions using improved keyword matching and fallback strategies."""
        logger.info(f"Processing general question: {question}")
        
        # Handle very generic questions
        if len(question.split()) <= 3 and any(word in question.lower() for word in ['what', 'this', 'that', 'it']):
            # For generic questions like "what is this?", provide a general paper overview
            if sections:
                # Try to find title/abstract first
                title_abstract = ""
                for section in sections:
                    if any(keyword in section.title.lower() for keyword in ['title', 'abstract', 'summary']):
                        title_abstract = section.content[:800]
                        break
                
                if not title_abstract and sections:
                    # Fallback to first section
                    title_abstract = sections[0].content[:800]
                
                if title_abstract:
                    return ResearchAnswer(
                        answer=f"This appears to be a research paper. {title_abstract}",
                        confidence=0.7,
                        evidence_text=title_abstract[:300],
                        answer_type="general"
                    )
        
        # Extract keywords from question
        question_words = set(re.findall(r'\b\w+\b', question.lower()))
        question_words = {word for word in question_words if len(word) > 2}  # Include 3+ char words
        
        # Remove common stop words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'to', 'are', 'as', 'was', 'for', 'with', 'by'}
        question_words = question_words - stop_words

        best_match = ""
        best_score = 0
        best_section = None

        # Search through sections for relevant content
        for section in sections:
            content = section.content.lower()
            content_words = set(re.findall(r'\b\w+\b', content))

            # Calculate similarity
            if question_words:
                overlap = len(question_words.intersection(content_words))
                score = overlap / len(question_words)
            else:
                score = 0

            if score > best_score:
                best_score = score
                best_section = section
                
                # Find the most relevant paragraph
                paragraphs = content.split('\n\n')
                best_paragraph = ""
                best_paragraph_score = 0

                for paragraph in paragraphs:
                    if len(paragraph.strip()) < 50:  # Skip very short paragraphs
                        continue
                        
                    paragraph_words = set(re.findall(r'\b\w+\b', paragraph.lower()))
                    if question_words:
                        paragraph_overlap = len(question_words.intersection(paragraph_words))
                        paragraph_score = paragraph_overlap / len(question_words)
                    else:
                        paragraph_score = 0

                    if paragraph_score > best_paragraph_score:
                        best_paragraph_score = paragraph_score
                        best_paragraph = paragraph

                best_match = best_paragraph[:600] if best_paragraph else content[:600]

        # Provide fallback answer if no good match found
        if best_match and best_score > 0.1:
            answer = best_match.strip()
            confidence = min(best_score * 0.8, 0.8)  # Cap confidence at 0.8
        else:
            # Fallback strategy: provide paper overview
            if sections:
                # Get the first substantial section (likely abstract or introduction)
                fallback_content = ""
                for section in sections:
                    if len(section.content.strip()) > 100:
                        fallback_content = section.content[:500]
                        break
                
                if fallback_content:
                    answer = f"Based on the available content: {fallback_content.strip()}"
                    confidence = 0.4
                else:
                    answer = "I have access to this paper but couldn't find content specifically relevant to your question. Please try asking a more specific question about the paper's methodology, results, or contributions."
                    confidence = 0.2
            else:
                answer = "I don't have access to the paper content to answer your question. Please ensure the paper was properly uploaded and processed."
                confidence = 0.1

        return ResearchAnswer(
            answer=answer,
            confidence=confidence,
            evidence_text=best_match[:300] if best_match else "",
            source_section=best_section.title if best_section else None,
            answer_type="general"
        )

    def answer_section_question(self, question: str, section_name: str, paper: ParsedPaper) -> ResearchAnswer:
        """Answer a question about a specific section."""
        # Find the requested section
        target_section = None
        for section in paper.sections:
            if section_name.lower() in section.title.lower():
                target_section = section
                break

        if not target_section:
            return ResearchAnswer(
                answer=f"Section '{section_name}' not found in the paper.",
                confidence=0.0,
                evidence_text="",
                source_section=section_name
            )

        # Answer question in context of specific section
        context = f"{target_section.title}\n{target_section.content}"

        if self.qa_pipeline:
            try:
                result = self.qa_pipeline(question=question, context=context)
                return ResearchAnswer(
                    answer=result['answer'],
                    confidence=result['score'],
                    evidence_text=context[max(
                        0, result['start']-50):result['end']+50],
                    source_section=target_section.title,
                    page_number=target_section.page_start
                )
            except:
                pass

        # Fallback: return section content summary
        return ResearchAnswer(
            answer=target_section.content[:500],
            confidence=0.6,
            evidence_text=target_section.content[:300],
            source_section=target_section.title,
            page_number=target_section.page_start
        )
