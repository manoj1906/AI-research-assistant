"""
Research-specific embeddings for academic papers using scientific models.
"""

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from typing import List, Union, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ScientificEmbeddings:
    """Scientific text embeddings using specialized models like SciBERT or SPECTER."""

    def __init__(self, config: Any):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available(
        ) and config.models.device == "auto" else "cpu")

        logger.info(f"Using device: {self.device}")

        # Load scientific embeddings model
        self._load_model()

    def _load_model(self):
        """Load the scientific embeddings model."""
        model_name = self.config.models.scientific_embeddings

        try:
            logger.info(f"Loading scientific embeddings model: {model_name}")

            if "specter" in model_name.lower():
                # SPECTER models are specialized for scientific papers
                self.model = SentenceTransformer(
                    model_name, cache_folder=self.config.models.cache_dir)
                self.tokenizer = None
                self.model_type = "specter"

            elif "scibert" in model_name.lower():
                # SciBERT models
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=self.config.models.cache_dir
                )
                self.model = AutoModel.from_pretrained(
                    model_name,
                    cache_dir=self.config.models.cache_dir
                ).to(self.device)
                self.model_type = "bert"

            else:
                # Default to sentence transformers
                self.model = SentenceTransformer(
                    model_name, cache_folder=self.config.models.cache_dir)
                self.tokenizer = None
                self.model_type = "sentence_transformer"

            logger.info("Scientific embeddings model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load scientific embeddings model: {e}")
            # Fallback to a general model
            logger.info("Falling back to general sentence transformer model")
            self.model = SentenceTransformer(
                'all-MiniLM-L6-v2', cache_folder=self.config.models.cache_dir)
            self.tokenizer = None
            self.model_type = "sentence_transformer"

    def encode_text(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """Encode text using scientific embeddings."""
        if isinstance(texts, str):
            texts = [texts]

        try:
            if self.model_type == "bert":
                return self._encode_with_bert(texts, **kwargs)
            else:
                return self._encode_with_sentence_transformer(texts, **kwargs)

        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            raise

    def _encode_with_bert(self, texts: List[str], **kwargs) -> np.ndarray:
        """Encode texts using BERT-style models."""
        embeddings = []
        batch_size = kwargs.get('batch_size', self.config.models.batch_size)

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # Tokenize
            inputs = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=self.config.models.max_length,
                return_tensors="pt"
            ).to(self.device)

            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use CLS token embedding or mean pooling
                if hasattr(outputs, 'pooler_output') and outputs.pooler_output is not None:
                    batch_embeddings = outputs.pooler_output
                else:
                    # Mean pooling
                    attention_mask = inputs['attention_mask']
                    token_embeddings = outputs.last_hidden_state
                    input_mask_expanded = attention_mask.unsqueeze(
                        -1).expand(token_embeddings.size()).float()
                    batch_embeddings = torch.sum(
                        token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

                embeddings.append(batch_embeddings.cpu().numpy())

        return np.vstack(embeddings)

    def _encode_with_sentence_transformer(self, texts: List[str], **kwargs) -> np.ndarray:
        """Encode texts using sentence transformer models."""
        batch_size = kwargs.get('batch_size', self.config.models.batch_size)

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 10,
            convert_to_numpy=True,
            device=str(self.device)
        )

        return embeddings

    def encode_paper_abstract(self, abstract: str) -> np.ndarray:
        """Specialized encoding for paper abstracts."""
        # Abstracts often contain the most important information
        # We can add special preprocessing here
        if not abstract.strip():
            return self.encode_text(["[EMPTY ABSTRACT]"])

        # Add special tokens for abstract
        processed_abstract = f"[ABSTRACT] {abstract}"
        return self.encode_text(processed_abstract)

    def encode_paper_section(self, section_title: str, section_content: str) -> np.ndarray:
        """Specialized encoding for paper sections."""
        # Combine title and content with special formatting
        section_text = f"[SECTION: {section_title}] {section_content}"
        return self.encode_text(section_text)

    def encode_paper_title(self, title: str) -> np.ndarray:
        """Specialized encoding for paper titles."""
        processed_title = f"[TITLE] {title}"
        return self.encode_text(processed_title)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if self.model_type == "bert":
            return self.model.config.hidden_size
        else:
            # Get dimension from model
            test_embedding = self.model.encode(["test"], convert_to_numpy=True)
            return test_embedding.shape[1]


class AcademicQuestionEmbeddings:
    """Specialized embeddings for academic questions and queries."""

    def __init__(self, config: Any):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available(
        ) and config.models.device == "auto" else "cpu")

        # Load question answering model
        self._load_model()

    def _load_model(self):
        """Load question answering embeddings model."""
        try:
            logger.info("Loading academic question embeddings model")

            # Use the same model as scientific embeddings for consistency
            self.scientific_embeddings = ScientificEmbeddings(self.config)

            # Academic question templates
            self.question_templates = {
                'contribution': [
                    "What is the main contribution?",
                    "What are the key contributions?",
                    "What is novel about this work?",
                    "What is the significance of this research?"
                ],
                'methodology': [
                    "What is the methodology?",
                    "How was the experiment conducted?",
                    "What approach was used?",
                    "Describe the method"
                ],
                'results': [
                    "What are the results?",
                    "What were the findings?",
                    "What did the authors discover?",
                    "What are the experimental results?"
                ],
                'limitations': [
                    "What are the limitations?",
                    "What are the weaknesses?",
                    "What are the constraints?",
                    "What issues does this approach have?"
                ]
            }

            logger.info("Academic question embeddings loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load question embeddings: {e}")
            raise

    def encode_question(self, question: str) -> np.ndarray:
        """Encode academic question with special formatting."""
        # Detect question type and add context
        question_type = self._detect_question_type(question)

        if question_type:
            formatted_question = f"[ACADEMIC QUESTION: {question_type.upper()}] {question}"
        else:
            formatted_question = f"[ACADEMIC QUESTION] {question}"

        return self.scientific_embeddings.encode_text(formatted_question)

    def _detect_question_type(self, question: str) -> Optional[str]:
        """Detect the type of academic question."""
        question_lower = question.lower()

        # Check for different question types
        if any(word in question_lower for word in ['contribution', 'novel', 'significance', 'main']):
            return 'contribution'
        elif any(word in question_lower for word in ['method', 'approach', 'algorithm', 'technique']):
            return 'methodology'
        elif any(word in question_lower for word in ['result', 'finding', 'outcome', 'performance']):
            return 'results'
        elif any(word in question_lower for word in ['limitation', 'weakness', 'problem', 'issue']):
            return 'limitations'

        return None

    def get_similar_questions(self, question: str, question_type: Optional[str] = None) -> List[str]:
        """Get similar academic questions for better matching."""
        if question_type and question_type in self.question_templates:
            return self.question_templates[question_type]

        # Auto-detect type
        detected_type = self._detect_question_type(question)
        if detected_type and detected_type in self.question_templates:
            return self.question_templates[detected_type]

        return []


class MultimodalResearchEmbeddings:
    """Combined embeddings for text, figures, and tables in research papers."""

    def __init__(self, config: Any):
        self.config = config

        # Initialize components
        self.text_embeddings = ScientificEmbeddings(config)
        self.question_embeddings = AcademicQuestionEmbeddings(config)

        # TODO: Add vision embeddings for figures/tables when needed
        self.vision_embeddings = None

        logger.info("Multimodal research embeddings initialized")

    def encode_paper_content(self,
                             title: str = "",
                             abstract: str = "",
                             sections: List[Dict[str, str]] = None,
                             **kwargs) -> Dict[str, np.ndarray]:
        """Encode different parts of a research paper."""
        embeddings = {}

        # Encode title
        if title:
            embeddings['title'] = self.text_embeddings.encode_paper_title(
                title)

        # Encode abstract
        if abstract:
            embeddings['abstract'] = self.text_embeddings.encode_paper_abstract(
                abstract)

        # Encode sections
        if sections:
            section_embeddings = []
            for section in sections:
                section_emb = self.text_embeddings.encode_paper_section(
                    section.get('title', ''),
                    section.get('content', '')
                )
                section_embeddings.append(section_emb)

            if section_embeddings:
                embeddings['sections'] = np.vstack(section_embeddings)

        return embeddings

    def encode_research_question(self, question: str) -> np.ndarray:
        """Encode research question with academic context."""
        return self.question_embeddings.encode_question(question)

    def get_unified_dimension(self) -> int:
        """Get unified embedding dimension."""
        return self.text_embeddings.get_dimension()

    def encode_for_search(self, content: str, content_type: str = "general") -> np.ndarray:
        """Encode content for search with type-specific processing."""
        if content_type == "title":
            return self.text_embeddings.encode_paper_title(content)
        elif content_type == "abstract":
            return self.text_embeddings.encode_paper_abstract(content)
        elif content_type == "question":
            return self.question_embeddings.encode_question(content)
        else:
            return self.text_embeddings.encode_text(content)
