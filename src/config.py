"""
Configuration settings for AI Research Assistant.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
from pathlib import Path


@dataclass
class ModelConfig:
    """Configuration for AI models."""

    # Scientific text models
    # Reliable scientific embeddings
    scientific_embeddings: str = "sentence-transformers/all-mpnet-base-v2"
    text_model: str = "allenai/scibert_scivocab_uncased"  # Scientific BERT
    qa_model: str = "deepset/roberta-base-squad2"  # Question answering

    # Specialized models
    biomedical_model: str = "dmis-lab/biobert-base-cased-v1.1"  # Optional biomedical
    math_model: str = "facebook/nougat-base"  # Mathematical expressions

    # General models
    summarization_model: str = "facebook/bart-large-cnn"
    generation_model: str = "t5-base"

    # Model cache directory
    cache_dir: str = "./models"

    # Device settings
    device: str = "auto"  # auto, cpu, cuda

    # Model parameters
    max_length: int = 512
    batch_size: int = 16
    embedding_dim: int = 768


@dataclass
class ProcessingConfig:
    """Configuration for document processing."""

    # PDF processing
    pdf_dpi: int = 300
    extract_images: bool = True
    extract_tables: bool = True
    extract_equations: bool = True

    # Text processing
    min_section_length: int = 100
    max_chunk_size: int = 1000
    chunk_overlap: int = 100

    # Figure and table analysis
    figure_analysis: bool = True
    table_analysis: bool = True
    caption_extraction: bool = True

    # Citation processing
    extract_citations: bool = True
    parse_references: bool = True

    # File settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    supported_formats: List[str] = field(
        default_factory=lambda: ['.pdf', '.tex', '.txt'])

    # Temporary directories
    temp_dir: str = "./data/temp"
    upload_dir: str = "./data/uploads"
    processed_dir: str = "./data/processed"


@dataclass
class DatabaseConfig:
    """Configuration for data storage."""

    # Vector database
    vector_db_type: str = "chroma"  # chroma, faiss, pinecone
    vector_db_path: str = "./data/vectorstore"
    collection_name: str = "research_papers"

    # Metadata database
    metadata_db_type: str = "sqlite"  # sqlite, postgresql
    metadata_db_path: str = "./data/papers.db"

    # Search settings
    similarity_threshold: float = 0.7
    max_results: int = 20

    # Caching
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour


@dataclass
class APIConfig:
    """Configuration for API and web interface."""

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Web interface
    web_port: int = 8501
    web_host: str = "localhost"

    # API settings
    api_version: str = "v1"
    cors_enabled: bool = True

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour

    # Authentication (optional)
    auth_enabled: bool = False
    jwt_secret: Optional[str] = None


@dataclass
class ResearchConfig:
    """Configuration for research-specific features."""

    # Section identification
    section_patterns: Dict[str, List[str]] = field(default_factory=lambda: {
        'abstract': ['abstract', 'summary'],
        'introduction': ['introduction', 'intro'],
        'related_work': ['related work', 'background', 'literature review'],
        'methodology': ['methodology', 'methods', 'approach', 'model'],
        'experiments': ['experiments', 'evaluation', 'results'],
        'discussion': ['discussion', 'analysis'],
        'conclusion': ['conclusion', 'conclusions', 'summary'],
        'references': ['references', 'bibliography']
    })

    # Question answering
    qa_confidence_threshold: float = 0.5
    max_context_length: int = 2000

    # Analysis features
    contribution_analysis: bool = True
    methodology_analysis: bool = True
    result_analysis: bool = True
    citation_analysis: bool = True

    # Comparison features
    cross_paper_comparison: bool = True
    similarity_comparison: bool = True

    # Export features
    export_formats: List[str] = field(
        default_factory=lambda: ['txt', 'json', 'bibtex'])


@dataclass
class Config:
    """Main configuration class."""

    models: ModelConfig = field(default_factory=ModelConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    research: ResearchConfig = field(default_factory=ResearchConfig)

    # Environment-specific settings
    debug: bool = False
    log_level: str = "INFO"

    def __post_init__(self):
        """Create necessary directories."""
        directories = [
            self.models.cache_dir,
            self.processing.temp_dir,
            self.processing.upload_dir,
            self.processing.processed_dir,
            self.database.vector_db_path,
            Path(self.database.metadata_db_path).parent
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        config = cls()

        # Update from environment variables
        if os.getenv('RESEARCH_DEBUG'):
            config.debug = os.getenv('RESEARCH_DEBUG').lower() == 'true'

        if os.getenv('RESEARCH_LOG_LEVEL'):
            config.log_level = os.getenv('RESEARCH_LOG_LEVEL')

        if os.getenv('RESEARCH_API_PORT'):
            config.api.port = int(os.getenv('RESEARCH_API_PORT'))

        if os.getenv('RESEARCH_WEB_PORT'):
            config.api.web_port = int(os.getenv('RESEARCH_WEB_PORT'))

        # Model configurations
        if os.getenv('RESEARCH_SCIENTIFIC_MODEL'):
            config.models.scientific_embeddings = os.getenv(
                'RESEARCH_SCIENTIFIC_MODEL')

        if os.getenv('RESEARCH_TEXT_MODEL'):
            config.models.text_model = os.getenv('RESEARCH_TEXT_MODEL')

        return config


# Global configuration instance
config = Config.from_env()
