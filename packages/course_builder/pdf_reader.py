"""PDF text extraction with page tracking capabilities."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pdfplumber

from .source_document import SectionContent, SourceDocument
from .utils import sanitize_text


@dataclass
class PDFDocument(SourceDocument):
    """Represents a parsed PDF document with page-level access."""

    path: Path
    _sections: list[SectionContent]
    _title: Optional[str] = None

    @property
    def source_type(self) -> str:
        return "pdf"

    @property
    def source_path(self) -> str:
        return str(self.path)

    @property
    def source_name(self) -> str:
        return self.path.name

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def total_sections(self) -> int:
        """Return total number of pages."""
        return len(self._sections)

    @property
    def total_pages(self) -> int:
        """Alias for total_sections for backward compatibility."""
        return self.total_sections

    @property
    def sections(self) -> list[SectionContent]:
        return self._sections

    @property
    def pages(self) -> list[SectionContent]:
        """Alias for sections for backward compatibility."""
        return self._sections

    def get_section(self, section_id: str) -> Optional[SectionContent]:
        """Get content for a specific page by ID (page number as string)."""
        for section in self._sections:
            if section.section_id == section_id:
                return section
        return None

    def get_page(self, page_number: int) -> Optional[SectionContent]:
        """Get content for a specific page (1-indexed)."""
        if 1 <= page_number <= len(self._sections):
            return self._sections[page_number - 1]
        return None

    def get_section_range(self, start_idx: int, end_idx: int) -> list[SectionContent]:
        """Get content for a range of sections by index (0-based, inclusive)."""
        start_idx = max(0, start_idx)
        end_idx = min(len(self._sections) - 1, end_idx)
        return self._sections[start_idx : end_idx + 1]

    def get_page_range(self, start: int, end: int) -> list[SectionContent]:
        """Get content for a range of pages (1-indexed, inclusive)."""
        return self.get_section_range(start - 1, end - 1)

    def get_full_text(self) -> str:
        """Get concatenated text from all pages."""
        return "\n\n".join(
            f"[Page {s.section_id}]\n{s.text}" for s in self._sections
        )

    def get_text_for_range(self, start_idx: int, end_idx: int) -> str:
        """Get concatenated text for a section range with page markers."""
        # For PDFs, convert to 1-indexed page numbers for the method
        sections = self.get_section_range(start_idx, end_idx)
        return "\n\n".join(
            f"[Page {s.section_id}]\n{s.text}" for s in sections
        )

    def get_text_for_page_range(self, start: int, end: int) -> str:
        """Get concatenated text for a page range (1-indexed) with page markers."""
        return self.get_text_for_range(start - 1, end - 1)

    def get_summary_text(self, max_sections: int = 10) -> str:
        """
        Get a summary of the document for planning purposes.
        Includes first few pages and table of contents if found.
        """
        summary_sections = self._sections[:max_sections]
        return "\n\n".join(
            f"[Page {s.section_id}]\n{s.text}" for s in summary_sections
        )

    def get_section_reference(self, section: SectionContent) -> str:
        """Get a reference string for a page."""
        return f"page {section.section_id}"

    def get_range_reference(self, start_idx: int, end_idx: int) -> str:
        """Get a reference string for a range of pages."""
        # Convert to 1-indexed page numbers
        start_page = start_idx + 1
        end_page = end_idx + 1
        if start_page == end_page:
            return f"page {start_page}"
        return f"pages {start_page}-{end_page}"


def extract_pdf(pdf_path: Path) -> PDFDocument:
    """
    Extract text content from a PDF file with page tracking.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        PDFDocument with extracted content

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If PDF cannot be parsed
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    sections = []
    title = None

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                # Sanitize text to remove invalid Unicode characters (surrogates)
                text = sanitize_text(text.strip())
                sections.append(SectionContent(
                    section_id=str(i),
                    section_label=f"Page {i}",
                    text=text,
                ))

            # Try to extract title from metadata
            if pdf.metadata and pdf.metadata.get("Title"):
                title = pdf.metadata["Title"]

    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {e}") from e

    return PDFDocument(path=pdf_path, _sections=sections, _title=title)


def find_content_by_keyword(
    document: PDFDocument, keyword: str, context_chars: int = 200
) -> list[tuple[int, str]]:
    """
    Find pages containing a keyword and return relevant snippets.

    Args:
        document: The PDF document to search
        keyword: Keyword to search for (case-insensitive)
        context_chars: Number of characters of context around match

    Returns:
        List of (page_number, snippet) tuples
    """
    results = []
    keyword_lower = keyword.lower()

    for section in document.sections:
        text_lower = section.text.lower()
        if keyword_lower in text_lower:
            # Find the position of the keyword
            pos = text_lower.find(keyword_lower)
            start = max(0, pos - context_chars)
            end = min(len(section.text), pos + len(keyword) + context_chars)
            snippet = section.text[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(section.text):
                snippet = snippet + "..."
            results.append((int(section.section_id), snippet))

    return results


def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Estimate reading time in minutes for a block of text."""
    word_count = len(text.split())
    return max(1, round(word_count / words_per_minute))
