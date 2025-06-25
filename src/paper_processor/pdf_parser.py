"""
Enhanced PDF parser specifically designed for academic papers.
Handles section extraction, figure/table detection, and academic formatting.
"""

import re
import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from PIL import Image
import io

logger = logging.getLogger(__name__)


@dataclass
class PaperSection:
    """Represents a section in an academic paper."""
    title: str
    content: str
    level: int  # 1 for main sections, 2 for subsections, etc.
    page_start: int
    page_end: int
    bbox: Optional[Tuple[float, float, float, float]] = None


@dataclass
class PaperFigure:
    """Represents a figure in an academic paper."""
    caption: str
    image_path: str
    page_number: int
    bbox: Tuple[float, float, float, float]
    figure_number: Optional[str] = None


@dataclass
class PaperTable:
    """Represents a table in an academic paper."""
    caption: str
    content: str  # Table content as text
    page_number: int
    bbox: Tuple[float, float, float, float]
    table_number: Optional[str] = None


@dataclass
class PaperMetadata:
    """Metadata extracted from academic paper."""
    title: str
    authors: List[str]
    abstract: str
    keywords: List[str]
    venue: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None


@dataclass
class ParsedPaper:
    """Complete parsed academic paper."""
    metadata: PaperMetadata
    sections: List[PaperSection]
    figures: List[PaperFigure]
    tables: List[PaperTable]
    references: List[str]
    full_text: str
    page_count: int


class AcademicPDFParser:
    """Enhanced PDF parser for academic papers."""

    def __init__(self, config: Any):
        self.config = config
        self.section_patterns = self._compile_section_patterns()

    def _compile_section_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for section identification."""
        patterns = {}

        # Common academic section patterns
        section_configs = self.config.research.section_patterns

        for section_type, keywords in section_configs.items():
            # Create pattern that matches section headers
            pattern_str = r'^\s*(?:\d+\.?\s*)?(?:' + \
                '|'.join(keywords) + r')\s*$'
            patterns[section_type] = re.compile(
                pattern_str, re.IGNORECASE | re.MULTILINE)

        return patterns

    def parse_paper(self, pdf_path: str) -> ParsedPaper:
        """Parse an academic paper PDF."""
        logger.info(f"Parsing academic paper: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)

            # Extract metadata
            metadata = self._extract_metadata(doc)

            # Extract text content
            full_text = self._extract_full_text(doc)

            # Extract sections
            sections = self._extract_sections(doc, full_text)

            # Extract figures
            figures = self._extract_figures(doc, pdf_path)

            # Extract tables
            tables = self._extract_tables(doc)

            # Extract references
            references = self._extract_references(doc, full_text)

            return ParsedPaper(
                metadata=metadata,
                sections=sections,
                figures=figures,
                tables=tables,
                references=references,
                full_text=full_text,
                page_count=len(doc)
            )

        except Exception as e:
            logger.error(f"Error parsing paper {pdf_path}: {e}")
            raise
        finally:
            if 'doc' in locals():
                doc.close()

    def _extract_metadata(self, doc: fitz.Document) -> PaperMetadata:
        """Extract paper metadata from PDF."""
        metadata = doc.metadata
        first_page_text = doc[0].get_text()

        # Extract title (usually the largest text on first page)
        title = self._extract_title(first_page_text, metadata)

        # Extract authors
        authors = self._extract_authors(first_page_text)

        # Extract abstract
        abstract = self._extract_abstract(first_page_text)

        # Extract keywords
        keywords = self._extract_keywords(first_page_text)

        # Extract venue/conference info
        venue = self._extract_venue(first_page_text)

        # Extract year
        year = self._extract_year(first_page_text, metadata)

        # Extract DOI
        doi = self._extract_doi(first_page_text)

        # Extract arXiv ID
        arxiv_id = self._extract_arxiv_id(first_page_text)

        return PaperMetadata(
            title=title,
            authors=authors,
            abstract=abstract,
            keywords=keywords,
            venue=venue,
            year=year,
            doi=doi,
            arxiv_id=arxiv_id
        )

    def _extract_title(self, text: str, metadata: Dict) -> str:
        """Extract paper title."""
        # Try metadata first
        if metadata.get('title'):
            return metadata['title'].strip()

        # Extract from text (usually in first few lines)
        lines = text.split('\n')[:10]

        # Find the longest line that looks like a title
        potential_titles = []
        for line in lines:
            line = line.strip()
            if len(line) > 20 and not line.lower().startswith(('abstract', 'introduction')):
                potential_titles.append(line)

        if potential_titles:
            return max(potential_titles, key=len)

        return "Unknown Title"

    def _extract_authors(self, text: str) -> List[str]:
        """Extract author names from paper."""
        authors = []

        # Look for author patterns
        author_patterns = [
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # First Last
            r'([A-Z]\.\s*[A-Z][a-z]+)',      # F. Last
            r'([A-Z][a-z]+\s+[A-Z]\.\s*[A-Z][a-z]+)',  # First F. Last
        ]

        for pattern in author_patterns:
            # Search in first 1000 chars
            matches = re.findall(pattern, text[:1000])
            authors.extend(matches)

        # Remove duplicates and clean
        authors = list(set(authors))
        return authors[:10]  # Limit to reasonable number

    def _extract_abstract(self, text: str) -> str:
        """Extract abstract from paper."""
        # Look for abstract section
        abstract_pattern = r'(?i)abstract[:\s]*(.*?)(?=\n\s*(?:keywords|introduction|\d+\.|$))'
        match = re.search(abstract_pattern, text, re.DOTALL)

        if match:
            abstract = match.group(1).strip()
            # Clean up the abstract
            abstract = re.sub(r'\s+', ' ', abstract)
            return abstract

        return ""

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from paper."""
        keywords = []

        # Look for keywords section
        keyword_pattern = r'(?i)keywords?[:\s]*(.*?)(?=\n\s*(?:introduction|\d+\.|$))'
        match = re.search(keyword_pattern, text, re.DOTALL)

        if match:
            keyword_text = match.group(1).strip()
            # Split by common separators
            keywords = re.split(r'[,;·•]', keyword_text)
            keywords = [k.strip() for k in keywords if k.strip()]

        return keywords

    def _extract_venue(self, text: str) -> Optional[str]:
        """Extract venue/conference information."""
        # Common conference/journal patterns
        venue_patterns = [
            r'(?i)(ICML|NeurIPS|ICLR|AAAI|IJCAI|ACL|EMNLP|NAACL|COLING)',
            r'(?i)(IEEE|ACM|Nature|Science|PNAS)',
            r'(?i)Proceedings of the.*?(\d{4})',
            r'(?i)Conference on.*?(\d{4})',
        ]

        for pattern in venue_patterns:
            match = re.search(pattern, text[:2000])
            if match:
                return match.group(0)

        return None

    def _extract_year(self, text: str, metadata: Dict) -> Optional[int]:
        """Extract publication year."""
        # Try metadata first
        if metadata.get('creationDate'):
            try:
                return int(str(metadata['creationDate'])[:4])
            except:
                pass

        # Look for year in text
        year_pattern = r'(?i)(?:20|19)\d{2}'
        matches = re.findall(year_pattern, text[:2000])

        if matches:
            years = [int(year)
                     for year in matches if 1990 <= int(year) <= 2030]
            if years:
                return max(years)  # Return most recent year

        return None

    def _extract_doi(self, text: str) -> Optional[str]:
        """Extract DOI from paper."""
        doi_pattern = r'(?i)doi[:\s]*(10\.\d+/[^\s]+)'
        match = re.search(doi_pattern, text)

        if match:
            return match.group(1)

        return None

    def _extract_arxiv_id(self, text: str) -> Optional[str]:
        """Extract arXiv ID from paper."""
        arxiv_pattern = r'(?i)arxiv[:\s]*(\d{4}\.\d{4,5})'
        match = re.search(arxiv_pattern, text)

        if match:
            return match.group(1)

        return None

    def _extract_full_text(self, doc: fitz.Document) -> str:
        """Extract full text from PDF."""
        full_text = ""

        for page in doc:
            text = page.get_text()
            full_text += text + "\n"

        return full_text

    def _extract_sections(self, doc: fitz.Document, full_text: str) -> List[PaperSection]:
        """Extract sections from the paper."""
        sections = []

        # Split text into lines with page information
        lines_with_pages = []
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            for line in page_text.split('\n'):
                lines_with_pages.append((line, page_num))

        # Identify section headers
        section_starts = []
        for i, (line, page_num) in enumerate(lines_with_pages):
            line_clean = line.strip()

            # Check if line matches any section pattern
            for section_type, pattern in self.section_patterns.items():
                if pattern.match(line_clean):
                    section_starts.append(
                        (i, section_type, line_clean, page_num))
                    break

        # Extract section content
        for i, (start_idx, section_type, title, start_page) in enumerate(section_starts):
            # Find end of section
            if i + 1 < len(section_starts):
                end_idx = section_starts[i + 1][0]
                end_page = section_starts[i + 1][3]
            else:
                end_idx = len(lines_with_pages)
                end_page = len(doc) - 1

            # Extract section content
            section_lines = lines_with_pages[start_idx:end_idx]
            content = '\n'.join(
                [line for line, _ in section_lines[1:]])  # Skip header

            if content.strip():
                sections.append(PaperSection(
                    title=title,
                    content=content.strip(),
                    level=1,  # Simplified for now
                    page_start=start_page,
                    page_end=end_page
                ))

        return sections

    def _extract_figures(self, doc: fitz.Document, pdf_path: str) -> List[PaperFigure]:
        """Extract figures from the paper."""
        figures = []
        base_path = Path(pdf_path).parent / "figures"
        base_path.mkdir(exist_ok=True)

        for page_num, page in enumerate(doc):
            # Get images from page
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                try:
                    # Extract image
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)

                    if pix.n - pix.alpha < 4:  # Skip if not RGB/RGBA
                        # Save image
                        image_name = f"page_{page_num+1}_fig_{img_index+1}.png"
                        image_path = base_path / image_name
                        pix.save(str(image_path))

                        # Find caption (look for "Figure" or "Fig" nearby)
                        caption = self._find_figure_caption(
                            page, img, page_num + 1)

                        figures.append(PaperFigure(
                            caption=caption,
                            image_path=str(image_path),
                            page_number=page_num + 1,
                            bbox=img[1:5],  # Bounding box
                            figure_number=self._extract_figure_number(caption)
                        ))

                    pix = None

                except Exception as e:
                    logger.warning(
                        f"Error extracting figure from page {page_num}: {e}")
                    continue

        return figures

    def _find_figure_caption(self, page: fitz.Page, img: tuple, page_num: int) -> str:
        """Find caption for a figure."""
        # Get text from page
        text = page.get_text()

        # Look for figure captions
        fig_patterns = [
            r'(?i)figure?\s*\d+[:\.]?\s*([^\n]+)',
            r'(?i)fig\.?\s*\d+[:\.]?\s*([^\n]+)',
        ]

        for pattern in fig_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()

        return f"Figure from page {page_num}"

    def _extract_figure_number(self, caption: str) -> Optional[str]:
        """Extract figure number from caption."""
        number_pattern = r'(?i)fig(?:ure)?\s*(\d+)'
        match = re.search(number_pattern, caption)

        if match:
            return match.group(1)

        return None

    def _extract_tables(self, doc: fitz.Document) -> List[PaperTable]:
        """Extract tables from the paper."""
        tables = []

        for page_num, page in enumerate(doc):
            # Find tables (simplified - look for table-like structures)
            tables_on_page = page.find_tables()

            for table_index, table in enumerate(tables_on_page):
                try:
                    # Extract table content
                    table_content = table.extract()
                    content_str = self._format_table_content(table_content)

                    # Find caption
                    caption = self._find_table_caption(
                        page, table, page_num + 1)

                    tables.append(PaperTable(
                        caption=caption,
                        content=content_str,
                        page_number=page_num + 1,
                        bbox=table.bbox,
                        table_number=self._extract_table_number(caption)
                    ))

                except Exception as e:
                    logger.warning(
                        f"Error extracting table from page {page_num}: {e}")
                    continue

        return tables

    def _format_table_content(self, table_data: List[List[str]]) -> str:
        """Format table data as readable text."""
        if not table_data:
            return ""

        # Simple formatting
        formatted_rows = []
        for row in table_data:
            formatted_rows.append(" | ".join(str(cell) for cell in row))

        return "\n".join(formatted_rows)

    def _find_table_caption(self, page: fitz.Page, table: Any, page_num: int) -> str:
        """Find caption for a table."""
        text = page.get_text()

        # Look for table captions
        table_patterns = [
            r'(?i)table\s*\d+[:\.]?\s*([^\n]+)',
            r'(?i)tab\.?\s*\d+[:\.]?\s*([^\n]+)',
        ]

        for pattern in table_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()

        return f"Table from page {page_num}"

    def _extract_table_number(self, caption: str) -> Optional[str]:
        """Extract table number from caption."""
        number_pattern = r'(?i)tab(?:le)?\s*(\d+)'
        match = re.search(number_pattern, caption)

        if match:
            return match.group(1)

        return None

    def _extract_references(self, doc: fitz.Document, full_text: str) -> List[str]:
        """Extract references from the paper."""
        references = []

        # Find references section
        ref_pattern = r'(?i)references?\s*\n(.*?)(?:\n\s*appendix|\n\s*$)'
        match = re.search(ref_pattern, full_text, re.DOTALL)

        if match:
            ref_text = match.group(1)

            # Split references (simple approach)
            # Look for numbered references or author patterns
            ref_lines = ref_text.split('\n')
            current_ref = ""

            for line in ref_lines:
                line = line.strip()

                # Check if line starts a new reference
                if re.match(r'^\[\d+\]|^\d+\.', line):
                    if current_ref:
                        references.append(current_ref.strip())
                    current_ref = line
                else:
                    current_ref += " " + line

            # Add last reference
            if current_ref:
                references.append(current_ref.strip())

        return references
