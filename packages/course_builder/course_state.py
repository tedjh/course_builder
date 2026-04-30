"""Course state management for tracking progress and chapter context."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .utils import read_markdown_file, write_markdown_file


@dataclass
class ChapterState:
    """State information for a single chapter."""

    number: int
    title: str
    status: str = "pending"  # pending, in_progress, completed
    key_concepts: list[str] = field(default_factory=list)
    dependencies: list[int] = field(default_factory=list)  # Chapter numbers this depends on
    summary: str = ""


@dataclass
class CourseState:
    """Overall course state tracking."""

    topic: str
    learning_purpose: str
    source_path: str  # File path or URL
    source_type: str = "pdf"  # "pdf" or "webpage"
    chapters: list[ChapterState] = field(default_factory=list)

    # Backward compatibility alias
    @property
    def source_pdf(self) -> str:
        """Alias for source_path for backward compatibility."""
        return self.source_path

    def get_chapter(self, chapter_number: int) -> Optional[ChapterState]:
        """Get state for a specific chapter."""
        for chapter in self.chapters:
            if chapter.number == chapter_number:
                return chapter
        return None

    def update_chapter(
        self,
        chapter_number: int,
        status: Optional[str] = None,
        key_concepts: Optional[list[str]] = None,
        summary: Optional[str] = None,
    ) -> None:
        """Update a chapter's state."""
        chapter = self.get_chapter(chapter_number)
        if chapter:
            if status is not None:
                chapter.status = status
            if key_concepts is not None:
                chapter.key_concepts = key_concepts
            if summary is not None:
                chapter.summary = summary

    def get_completed_chapters(self) -> list[ChapterState]:
        """Get all completed chapters."""
        return [c for c in self.chapters if c.status == "completed"]

    def get_next_pending_chapter(self) -> Optional[ChapterState]:
        """Get the next chapter to work on."""
        for chapter in self.chapters:
            if chapter.status == "pending":
                return chapter
        return None

    def get_context_for_chapter(self, chapter_number: int) -> str:
        """
        Get context string summarizing previous chapters for use when
        generating a new chapter.
        """
        completed = [c for c in self.chapters if c.number < chapter_number and c.status == "completed"]
        if not completed:
            return "This is the first chapter of the course."

        context_parts = ["Previous chapters covered:"]
        for chapter in completed:
            concepts = ", ".join(chapter.key_concepts) if chapter.key_concepts else "N/A"
            context_parts.append(
                f"\n## Chapter {chapter.number}: {chapter.title}\n"
                f"Key concepts: {concepts}\n"
                f"Summary: {chapter.summary}"
            )

        return "\n".join(context_parts)


def state_to_markdown(state: CourseState) -> str:
    """Convert course state to markdown format."""
    # Determine source label based on type
    source_label = "Source PDF" if state.source_type == "pdf" else "Source URL"

    lines = [
        "# Course State",
        "",
        f"**Topic:** {state.topic}",
        f"**Learning Purpose:** {state.learning_purpose}",
        f"**Source Type:** {state.source_type}",
        f"**{source_label}:** {state.source_path}",
        "",
        "---",
        "",
        "## Chapters",
        "",
    ]

    for chapter in state.chapters:
        status_emoji = {"pending": "\u23f3", "in_progress": "\ud83d\udd04", "completed": "\u2705"}.get(
            chapter.status, "\u2753"
        )

        lines.append(f"### Chapter {chapter.number}: {chapter.title}")
        lines.append(f"**Status:** {status_emoji} {chapter.status}")

        if chapter.dependencies:
            deps = ", ".join(f"Chapter {d}" for d in chapter.dependencies)
            lines.append(f"**Dependencies:** {deps}")

        if chapter.key_concepts:
            lines.append("**Key Concepts:**")
            for concept in chapter.key_concepts:
                lines.append(f"- {concept}")

        if chapter.summary:
            lines.append(f"**Summary:** {chapter.summary}")

        lines.append("")

    return "\n".join(lines)


def markdown_to_state(content: str) -> CourseState:
    """Parse markdown content back into CourseState."""
    # Extract header info
    topic_match = re.search(r"\*\*Topic:\*\*\s*(.+)", content)
    purpose_match = re.search(r"\*\*Learning Purpose:\*\*\s*(.+)", content)
    source_type_match = re.search(r"\*\*Source Type:\*\*\s*(.+)", content)

    # Try to match either "Source PDF" or "Source URL"
    source_path_match = re.search(r"\*\*Source (?:PDF|URL):\*\*\s*(.+)", content)

    topic = topic_match.group(1).strip() if topic_match else ""
    purpose = purpose_match.group(1).strip() if purpose_match else ""
    source_type = source_type_match.group(1).strip() if source_type_match else "pdf"
    source_path = source_path_match.group(1).strip() if source_path_match else ""

    state = CourseState(
        topic=topic,
        learning_purpose=purpose,
        source_path=source_path,
        source_type=source_type,
    )

    # Parse chapters
    chapter_pattern = r"### Chapter (\d+): (.+?)(?=\n)"
    status_pattern = r"\*\*Status:\*\*\s*[^\s]*\s*(\w+)"
    deps_pattern = r"\*\*Dependencies:\*\*\s*(.+)"
    summary_pattern = r"\*\*Summary:\*\*\s*(.+)"

    # Split by chapter headers
    chapter_sections = re.split(r"(?=### Chapter \d+:)", content)

    for section in chapter_sections:
        chapter_match = re.search(chapter_pattern, section)
        if chapter_match:
            number = int(chapter_match.group(1))
            title = chapter_match.group(2).strip()

            status = "pending"
            status_match = re.search(status_pattern, section)
            if status_match:
                status = status_match.group(1).strip()

            dependencies = []
            deps_match = re.search(deps_pattern, section)
            if deps_match:
                deps_str = deps_match.group(1)
                dependencies = [int(d) for d in re.findall(r"Chapter (\d+)", deps_str)]

            summary = ""
            summary_match = re.search(summary_pattern, section)
            if summary_match:
                summary = summary_match.group(1).strip()

            # Parse key concepts
            key_concepts = []
            concepts_section = re.search(
                r"\*\*Key Concepts:\*\*\n((?:- .+\n?)+)", section
            )
            if concepts_section:
                key_concepts = re.findall(r"- (.+)", concepts_section.group(1))

            state.chapters.append(
                ChapterState(
                    number=number,
                    title=title,
                    status=status,
                    key_concepts=key_concepts,
                    dependencies=dependencies,
                    summary=summary,
                )
            )

    return state


def save_course_state(state: CourseState, output_dir: Path) -> None:
    """Save course state to markdown file."""
    path = output_dir / "course_state.md"
    content = state_to_markdown(state)
    write_markdown_file(path, content)


def load_course_state(output_dir: Path) -> Optional[CourseState]:
    """Load course state from markdown file if it exists."""
    path = output_dir / "course_state.md"
    content = read_markdown_file(path)
    if content:
        return markdown_to_state(content)
    return None
