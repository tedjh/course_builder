"""Abstract base class for source documents (PDF or webpage)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class SectionContent:
    """Content from a document section (page for PDF, section for web)."""

    section_id: str  # "1" for page 1, or "section-intro" for web
    section_label: str  # "Page 1" or "Introduction"
    text: str


class SourceDocument(ABC):
    """Abstract base class for source documents (PDF or webpage)."""

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Return 'pdf' or 'webpage'."""

    @property
    @abstractmethod
    def source_path(self) -> str:
        """Return file path or URL."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return a display name for the source (filename or page title)."""

    @property
    @abstractmethod
    def title(self) -> Optional[str]:
        """Return document title if available."""

    @property
    @abstractmethod
    def total_sections(self) -> int:
        """Return total number of sections."""

    @property
    @abstractmethod
    def sections(self) -> list[SectionContent]:
        """Return all sections."""

    @abstractmethod
    def get_section(self, section_id: str) -> Optional[SectionContent]:
        """Get content for a specific section by ID."""

    @abstractmethod
    def get_section_range(self, start_idx: int, end_idx: int) -> list[SectionContent]:
        """Get content for a range of sections by index (0-based, inclusive)."""

    @abstractmethod
    def get_full_text(self) -> str:
        """Get all text with section markers."""

    @abstractmethod
    def get_text_for_range(self, start_idx: int, end_idx: int) -> str:
        """Get concatenated text for a section range with markers."""

    @abstractmethod
    def get_summary_text(self, max_sections: int = 10) -> str:
        """Get summary for planning purposes."""

    @abstractmethod
    def get_section_reference(self, section: SectionContent) -> str:
        """Get a reference string for a section (e.g., 'page 5' or 'Section: Intro')."""

    @abstractmethod
    def get_range_reference(self, start_idx: int, end_idx: int) -> str:
        """Get a reference string for a range (e.g., 'pages 5-10' or 'Sections 1-3')."""
