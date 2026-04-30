"""Utility functions for file I/O, markdown formatting, and LaTeX helpers."""

import re
from pathlib import Path
from typing import Optional


def ensure_directory(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def sanitize_text(text: str) -> str:
    """
    Remove invalid Unicode characters (surrogates) from text.

    Surrogates are code points in the range U+D800 to U+DFFF that are
    invalid in UTF-8 and can cause encoding errors.
    """
    # Remove surrogate characters (U+D800 to U+DFFF)
    return text.encode("utf-8", errors="surrogatepass").decode("utf-8", errors="replace")


def write_markdown_file(path: Path, content: str) -> None:
    """Write content to a markdown file, sanitizing invalid characters."""
    ensure_directory(path.parent)
    sanitized_content = sanitize_text(content)
    path.write_text(sanitized_content, encoding="utf-8")


def read_markdown_file(path: Path) -> Optional[str]:
    """Read content from a markdown file if it exists."""
    if path.exists():
        try:
            # Try UTF-8 first (most common)
            return path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            # Fall back to Latin-1 with replacement for bad chars
            return path.read_text(encoding="latin-1", errors="replace")
    return None


def validate_latex_formulas(content: str) -> list[str]:
    """
    Check for potential plain-text formulas that should be LaTeX.
    Returns a list of warnings for suspicious patterns.
    """
    warnings = []

    # Patterns that suggest plain-text math that should be LaTeX
    plain_math_patterns = [
        (r"(?<!\$)\b\w+\^[0-9]+(?!\$)", "Possible plain-text exponent"),
        (r"(?<!\$)\b\w+_[0-9]+(?!\$)", "Possible plain-text subscript"),
        (r"(?<!\$)sqrt\([^)]+\)(?!\$)", "Possible plain-text square root"),
        (r"(?<!\$)\bsum\s*\(", "Possible plain-text summation"),
        (r"(?<!\$)\bintegral\b", "Possible plain-text integral"),
    ]

    for pattern, message in plain_math_patterns:
        matches = re.findall(pattern, content)
        if matches:
            warnings.append(f"{message}: {matches[:3]}")  # Show first 3 matches

    return warnings


def format_chapter_directory_name(chapter_number: int) -> str:
    """Format chapter directory name consistently."""
    return f"chapter-{chapter_number}"


def create_course_directory_structure(
    output_dir: Path, num_chapters: int
) -> dict[int, Path]:
    """
    Create the full course directory structure.
    Returns a mapping of chapter numbers to their directories.
    """
    ensure_directory(output_dir)

    chapter_dirs = {}
    for i in range(1, num_chapters + 1):
        chapter_path = output_dir / format_chapter_directory_name(i)
        ensure_directory(chapter_path)
        chapter_dirs[i] = chapter_path

    return chapter_dirs


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "", name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")
    # Limit length
    return sanitized[:100]


def format_page_reference(start_page: int, end_page: Optional[int] = None) -> str:
    """Format a page reference string."""
    if end_page is None or start_page == end_page:
        return f"page {start_page}"
    return f"pages {start_page}-{end_page}"


def wrap_in_latex_inline(formula: str) -> str:
    """Wrap a formula in inline LaTeX delimiters."""
    return f"${formula}$"


def wrap_in_latex_display(formula: str) -> str:
    """Wrap a formula in display LaTeX delimiters."""
    return f"$${formula}$$"
