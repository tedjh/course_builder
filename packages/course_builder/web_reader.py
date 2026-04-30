"""Webpage text extraction with section tracking capabilities."""

from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

from .source_document import SectionContent, SourceDocument
from .utils import sanitize_text


@dataclass
class WebDocument(SourceDocument):
    """Represents a parsed webpage with section-level access."""

    url: str
    _sections: list[SectionContent]
    page_title: Optional[str] = None
    _fetched_urls: list[str] = field(default_factory=list)

    @property
    def source_type(self) -> str:
        return "webpage"

    @property
    def source_path(self) -> str:
        return self.url

    @property
    def source_name(self) -> str:
        if self.page_title:
            return self.page_title
        # Extract domain from URL
        parsed = urlparse(self.url)
        return parsed.netloc

    @property
    def title(self) -> Optional[str]:
        return self.page_title

    @property
    def total_sections(self) -> int:
        return len(self._sections)

    @property
    def sections(self) -> list[SectionContent]:
        return self._sections

    def get_section(self, section_id: str) -> Optional[SectionContent]:
        """Get content for a specific section by ID."""
        for section in self._sections:
            if section.section_id == section_id:
                return section
        return None

    def get_section_by_index(self, index: int) -> Optional[SectionContent]:
        """Get content for a specific section by index (0-based)."""
        if 0 <= index < len(self._sections):
            return self._sections[index]
        return None

    def get_section_range(self, start_idx: int, end_idx: int) -> list[SectionContent]:
        """Get content for a range of sections by index (0-based, inclusive)."""
        start_idx = max(0, start_idx)
        end_idx = min(len(self._sections) - 1, end_idx)
        return self._sections[start_idx : end_idx + 1]

    def get_full_text(self) -> str:
        """Get concatenated text from all sections."""
        return "\n\n".join(f"[{s.section_label}]\n{s.text}" for s in self._sections)

    def get_text_for_range(self, start_idx: int, end_idx: int) -> str:
        """Get concatenated text for a section range with markers."""
        sections = self.get_section_range(start_idx, end_idx)
        return "\n\n".join(f"[{s.section_label}]\n{s.text}" for s in sections)

    def get_summary_text(self, max_sections: int = 10) -> str:
        """Get a summary of the document for planning purposes."""
        summary_sections = self._sections[:max_sections]
        return "\n\n".join(f"[{s.section_label}]\n{s.text}" for s in summary_sections)

    def get_section_reference(self, section: SectionContent) -> str:
        """Get a reference string for a section."""
        return f"Section: {section.section_label}"

    def get_range_reference(self, start_idx: int, end_idx: int) -> str:
        """Get a reference string for a range of sections."""
        if start_idx == end_idx:
            section = self.get_section_by_index(start_idx)
            if section:
                return f"Section: {section.section_label}"
            return f"Section {start_idx + 1}"

        start_section = self.get_section_by_index(start_idx)
        end_section = self.get_section_by_index(end_idx)

        if start_section and end_section:
            return f"Sections: {start_section.section_label} to {end_section.section_label}"
        return f"Sections {start_idx + 1}-{end_idx + 1}"


def _extract_text_from_element(element: Tag) -> str:
    """Extract clean text from an HTML element."""
    # Get text, preserving some structure
    texts = []
    for child in element.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                texts.append(text)
        elif isinstance(child, Tag):
            if child.name in ("script", "style", "nav", "footer", "header", "aside"):
                continue
            if child.name == "br":
                texts.append("\n")
            elif child.name in ("p", "div", "li", "tr"):
                child_text = _extract_text_from_element(child)
                if child_text:
                    texts.append(child_text + "\n")
            elif child.name == "pre" or child.name == "code":
                # Preserve code blocks
                code_text = child.get_text()
                if code_text.strip():
                    texts.append(f"\n```\n{code_text}\n```\n")
            else:
                child_text = _extract_text_from_element(child)
                if child_text:
                    texts.append(child_text)

    return " ".join(texts).strip()


def _find_main_content(soup: BeautifulSoup) -> Tag:
    """Find the main content area of a webpage."""
    # Try common main content selectors
    main_selectors = [
        "main",
        "article",
        '[role="main"]',
        "#content",
        "#main-content",
        ".content",
        ".main-content",
        ".post-content",
        ".article-content",
        ".documentation",
        ".docs-content",
    ]

    for selector in main_selectors:
        main = soup.select_one(selector)
        if main and len(main.get_text(strip=True)) > 200:
            return main

    # Fallback to body
    body = soup.find("body")
    if body:
        return body

    return soup


def _split_into_sections(content: Tag) -> list[tuple[str, str, str]]:
    """
    Split content into sections based on headings.

    Returns list of (section_id, heading_text, content_text) tuples.
    """
    sections = []
    current_heading = "Introduction"
    current_content = []
    section_count = 0

    def flush_section():
        nonlocal section_count
        if current_content:
            content_text = "\n".join(current_content).strip()
            if content_text:
                section_id = f"section-{section_count}"
                sections.append((section_id, current_heading, content_text))
                section_count += 1

    for element in content.children:
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                current_content.append(text)
        elif isinstance(element, Tag):
            if element.name in ("h1", "h2", "h3"):
                # Flush previous section
                flush_section()
                # Start new section
                current_heading = element.get_text(strip=True)
                current_content = []
            elif element.name in ("script", "style", "nav", "footer", "aside"):
                continue
            else:
                text = _extract_text_from_element(element)
                if text:
                    current_content.append(text)

    # Flush final section
    flush_section()

    return sections


def extract_webpage(url: str, timeout: int = 30) -> WebDocument:
    """
    Extract text content from a webpage with section tracking.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        WebDocument with extracted content

    Raises:
        ValueError: If webpage cannot be fetched or parsed
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch webpage: {e}") from e

    try:
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        raise ValueError(f"Failed to parse webpage: {e}") from e

    # Extract title
    page_title = None
    title_tag = soup.find("title")
    if title_tag:
        page_title = title_tag.get_text(strip=True)

    # Find main content
    main_content = _find_main_content(soup)

    # Split into sections
    raw_sections = _split_into_sections(main_content)

    # Convert to SectionContent objects
    sections = []
    for section_id, heading, content in raw_sections:
        # Sanitize text to remove invalid Unicode characters
        sections.append(
            SectionContent(
                section_id=section_id,
                section_label=sanitize_text(heading),
                text=sanitize_text(content),
            )
        )

    # If no sections found, create one from all content
    if not sections:
        all_text = main_content.get_text(separator="\n", strip=True)
        if all_text:
            sections.append(
                SectionContent(
                    section_id="section-0",
                    section_label="Content",
                    text=sanitize_text(all_text),
                )
            )

    return WebDocument(
        url=url,
        _sections=sections,
        page_title=page_title,
        _fetched_urls=[url],
    )


def extract_multiple_pages(
    urls: list[str],
    timeout: int = 30,
) -> WebDocument:
    """
    Fetch multiple related pages and combine them into one document.

    Args:
        urls: List of URLs to fetch
        timeout: Request timeout in seconds per page

    Returns:
        WebDocument with combined content from all pages
    """
    all_sections = []
    page_titles = []
    fetched_urls = []

    for url in urls:
        try:
            doc = extract_webpage(url, timeout=timeout)
            # Prefix section IDs with page index to avoid collisions
            page_idx = len(fetched_urls)
            for section in doc.sections:
                new_section = SectionContent(
                    section_id=f"page{page_idx}-{section.section_id}",
                    section_label=f"[{doc.source_name}] {section.section_label}",
                    text=section.text,
                )
                all_sections.append(new_section)

            if doc.page_title:
                page_titles.append(doc.page_title)
            fetched_urls.append(url)

        except ValueError as e:
            print(f"Warning: Failed to fetch {url}: {e}")
            continue

    if not all_sections:
        raise ValueError("Failed to fetch any pages")

    # Use first page's title or combine them
    combined_title = page_titles[0] if page_titles else None

    return WebDocument(
        url=urls[0],  # Primary URL
        _sections=all_sections,
        page_title=combined_title,
        _fetched_urls=fetched_urls,
    )


def find_content_by_keyword(
    document: WebDocument,
    keyword: str,
    context_chars: int = 200,
) -> list[tuple[str, str]]:
    """
    Find sections containing a keyword and return relevant snippets.

    Args:
        document: The web document to search
        keyword: Keyword to search for (case-insensitive)
        context_chars: Number of characters of context around match

    Returns:
        List of (section_label, snippet) tuples
    """
    results = []
    keyword_lower = keyword.lower()

    for section in document.sections:
        text_lower = section.text.lower()
        if keyword_lower in text_lower:
            pos = text_lower.find(keyword_lower)
            start = max(0, pos - context_chars)
            end = min(len(section.text), pos + len(keyword) + context_chars)
            snippet = section.text[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(section.text):
                snippet = snippet + "..."
            results.append((section.section_label, snippet))

    return results
