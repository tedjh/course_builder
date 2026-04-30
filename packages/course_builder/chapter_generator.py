"""Chapter content generation - reading materials, exercises, and solutions."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from anthropic import Anthropic

from .course_state import ChapterState, CourseState, save_course_state
from .source_document import SourceDocument
from .prompts.exercises import EXERCISES_PROMPT, SOLUTIONS_PROMPT
from .prompts.reading import FULL_READING_PROMPT
from .utils import validate_latex_formulas, write_markdown_file


@dataclass
class ChapterContent:
    """Generated content for a chapter."""

    reading: str
    exercises: str
    solutions: str
    key_concepts: list[str]
    summary: str


def parse_section_reference(section_ref: str, source_document: SourceDocument) -> tuple[int, int]:
    """
    Parse a section reference string into start and end indices.

    For PDFs: "1-25" or "pages 1-25" -> (0, 24)
    For webpages: "Sections: Intro, Getting Started" -> indices of those sections

    Args:
        section_ref: Section reference string from the plan
        source_document: The source document to look up sections in

    Returns:
        Tuple of (start_idx, end_idx) for 0-based indexing
    """
    if source_document.source_type == "pdf":
        # Extract page numbers
        numbers = re.findall(r"\d+", section_ref)
        if len(numbers) >= 2:
            return int(numbers[0]) - 1, int(numbers[1]) - 1
        elif len(numbers) == 1:
            page = int(numbers[0]) - 1
            return page, page
        else:
            return 0, min(9, source_document.total_sections - 1)
    else:
        # For webpages, try to find section indices by name
        # Default to first few sections if we can't parse
        return 0, min(4, source_document.total_sections - 1)


def generate_reading_material(
    client: Anthropic,
    chapter: ChapterState,
    chapter_info: dict,
    course_state: CourseState,
    source_document: SourceDocument,
    next_chapter_info: Optional[dict],
    model: str = "claude-sonnet-4-20250514",
) -> str:
    """
    Generate reading material for a chapter.

    Args:
        client: Anthropic API client
        chapter: Chapter state information
        chapter_info: Chapter details from the plan
        course_state: Overall course state
        source_document: Source document (PDF or webpage)
        next_chapter_info: Information about the next chapter (if any)
        model: Claude model to use

    Returns:
        Generated reading material markdown
    """
    # Get section reference for this chapter
    source_sections = chapter_info.get("source_sections", chapter_info.get("source_pages", "1-10"))
    start_idx, end_idx = parse_section_reference(source_sections, source_document)

    # Get source content for the relevant sections
    source_content = source_document.get_text_for_range(start_idx, end_idx)

    # Get context from previous chapters
    previous_context = course_state.get_context_for_chapter(chapter.number)

    # Format learning objectives
    objectives = chapter_info.get("learning_objectives", [])
    learning_objectives = "\n".join(f"- {obj}" for obj in objectives)

    # Next chapter info
    next_title = (
        next_chapter_info.get("title", "N/A")
        if next_chapter_info
        else "Course Conclusion"
    )
    next_desc = (
        next_chapter_info.get("description", "")
        if next_chapter_info
        else "This is the final chapter of the course."
    )

    prompt = FULL_READING_PROMPT.format(
        topic=course_state.topic,
        learning_purpose=course_state.learning_purpose,
        chapter_number=chapter.number,
        chapter_title=chapter.title,
        chapter_description=chapter_info.get("description", ""),
        learning_objectives=learning_objectives,
        source_name=source_document.source_name,
        source_sections=source_sections,
        previous_context=previous_context,
        source_content=source_content[:30000],  # Limit content length
        next_chapter_title=next_title,
        next_chapter_description=next_desc,
    )

    response = client.messages.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    assert response.content[0].type == "text"
    reading_content = response.content[0].text

    # Validate LaTeX formulas
    warnings = validate_latex_formulas(reading_content)
    if warnings:
        print(f"  LaTeX warnings for chapter {chapter.number}: {warnings}")

    return reading_content


def generate_exercises(
    client: Anthropic,
    chapter: ChapterState,
    chapter_info: dict,
    course_state: CourseState,
    source_document: SourceDocument,
    reading_content: str,
    model: str = "claude-sonnet-4-20250514",
) -> str:
    """
    Generate exercises for a chapter.

    Args:
        client: Anthropic API client
        chapter: Chapter state information
        chapter_info: Chapter details from the plan
        course_state: Overall course state
        source_document: Source document (PDF or webpage)
        reading_content: The generated reading material
        model: Claude model to use

    Returns:
        Generated exercises markdown
    """
    # Get section reference for this chapter
    source_sections = chapter_info.get("source_sections", chapter_info.get("source_pages", "1-10"))
    start_idx, end_idx = parse_section_reference(source_sections, source_document)

    # Get source content (for reference to existing exercises)
    source_content = source_document.get_text_for_range(start_idx, end_idx)

    # Format learning objectives
    objectives = chapter_info.get("learning_objectives", [])
    learning_objectives = "\n".join(f"- {obj}" for obj in objectives)

    prompt = EXERCISES_PROMPT.format(
        topic=course_state.topic,
        learning_purpose=course_state.learning_purpose,
        chapter_number=chapter.number,
        chapter_title=chapter.title,
        learning_objectives=learning_objectives,
        reading_content=reading_content[:15000],  # Limit content length
        source_content=source_content[:15000],
    )

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    assert response.content[0].type == "text"
    return response.content[0].text


def generate_solutions(
    client: Anthropic,
    chapter: ChapterState,
    course_state: CourseState,
    exercises_content: str,
    model: str = "claude-sonnet-4-20250514",
) -> str:
    """
    Generate solutions for Claude-generated exercises.

    Args:
        client: Anthropic API client
        chapter: Chapter state information
        course_state: Overall course state
        exercises_content: The generated exercises
        model: Claude model to use

    Returns:
        Generated solutions markdown
    """
    prompt = SOLUTIONS_PROMPT.format(
        topic=course_state.topic,
        chapter_number=chapter.number,
        chapter_title=chapter.title,
        exercises_content=exercises_content,
    )

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    assert response.content[0].type == "text"
    return response.content[0].text


def extract_key_concepts(
    client: Anthropic,
    reading_content: str,
    model: str = "claude-sonnet-4-20250514",
) -> list[str]:
    """
    Extract key concepts from reading material for course state tracking.

    Args:
        client: Anthropic API client
        reading_content: The generated reading material
        model: Claude model to use

    Returns:
        List of key concept strings
    """
    prompt = f"""Extract 5-7 key concepts from this chapter reading material.
Return only a JSON array of strings, no other text.

Reading Material:
{reading_content[:10000]}

Example output format:
["Concept 1", "Concept 2", "Concept 3"]
"""

    response = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    assert response.content[0].type == "text"
    response_text = response.content[0].text

    # Extract JSON array
    json_match = re.search(r"\[[\s\S]*?\]", response_text)
    if json_match:
        try:
            concepts = json.loads(json_match.group())
            return concepts
        except json.JSONDecodeError:
            pass

    return []


def generate_chapter_summary(
    client: Anthropic,
    reading_content: str,
    model: str = "claude-sonnet-4-20250514",
) -> str:
    """
    Generate a brief summary of the chapter for course state tracking.

    Args:
        client: Anthropic API client
        reading_content: The generated reading material
        model: Claude model to use

    Returns:
        Brief summary string
    """
    prompt = f"""Write a 2-3 sentence summary of this chapter's main content.
Be concise and focus on the core learning outcomes.

Reading Material:
{reading_content[:8000]}
"""

    response = client.messages.create(
        model=model,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    assert response.content[0].type == "text"
    return response.content[0].text.strip()


def generate_chapter(
    client: Anthropic,
    chapter_number: int,
    course_state: CourseState,
    plan_chapters: list[dict],
    source_document: SourceDocument,
    output_dir: Path,
    model: str = "claude-sonnet-4-20250514",
) -> ChapterContent:
    """
    Generate all content for a single chapter.

    Args:
        client: Anthropic API client
        chapter_number: Chapter number to generate
        course_state: Overall course state
        plan_chapters: List of chapter info from the plan
        source_document: Source document (PDF or webpage)
        output_dir: Output directory for the course
        model: Claude model to use

    Returns:
        ChapterContent with all generated materials
    """
    # Get chapter info
    chapter = course_state.get_chapter(chapter_number)
    if not chapter:
        raise ValueError(f"Chapter {chapter_number} not found in course state")

    chapter_info = None
    for info in plan_chapters:
        if info.get("number") == chapter_number:
            chapter_info = info
            break

    if not chapter_info:
        chapter_info = {
            "title": chapter.title,
            "source_sections": "1-10",
            "learning_objectives": [],
        }

    # Get next chapter info for preview
    next_chapter_info = None
    for info in plan_chapters:
        if info.get("number") == chapter_number + 1:
            next_chapter_info = info
            break

    # Mark chapter as in progress
    course_state.update_chapter(chapter_number, status="in_progress")
    save_course_state(course_state, output_dir)

    print("  Generating reading material...")
    reading = generate_reading_material(
        client,
        chapter,
        chapter_info,
        course_state,
        source_document,
        next_chapter_info,
        model,
    )

    print("  Generating exercises...")
    exercises = generate_exercises(
        client, chapter, chapter_info, course_state, source_document, reading, model
    )

    print("  Generating solutions...")
    solutions = generate_solutions(client, chapter, course_state, exercises, model)

    print("  Extracting key concepts...")
    key_concepts = extract_key_concepts(client, reading, model)

    print("  Generating summary...")
    summary = generate_chapter_summary(client, reading, model)

    # Write files
    chapter_dir = output_dir / f"chapter-{chapter_number}"
    chapter_dir.mkdir(parents=True, exist_ok=True)

    write_markdown_file(chapter_dir / "reading.md", reading)
    write_markdown_file(chapter_dir / "exercises.md", exercises)
    write_markdown_file(chapter_dir / "solutions.md", solutions)

    # Update course state
    course_state.update_chapter(
        chapter_number,
        status="completed",
        key_concepts=key_concepts,
        summary=summary,
    )
    save_course_state(course_state, output_dir)

    return ChapterContent(
        reading=reading,
        exercises=exercises,
        solutions=solutions,
        key_concepts=key_concepts,
        summary=summary,
    )


def generate_all_chapters(
    client: Anthropic,
    course_state: CourseState,
    plan_chapters: list[dict],
    source_document: SourceDocument,
    output_dir: Path,
    model: str = "claude-sonnet-4-20250514",
    progress_callback=None,
) -> list[ChapterContent]:
    """
    Generate content for all chapters in the course.

    Args:
        client: Anthropic API client
        course_state: Overall course state
        plan_chapters: List of chapter info from the plan
        source_document: Source document (PDF or webpage)
        output_dir: Output directory for the course
        model: Claude model to use
        progress_callback: Optional callback(chapter_number, total_chapters)

    Returns:
        List of ChapterContent for all chapters
    """
    results = []
    total_chapters = len(course_state.chapters)

    for chapter in course_state.chapters:
        if chapter.status == "completed":
            print(f"Skipping chapter {chapter.number} (already completed)")
            continue

        print(f"\nGenerating Chapter {chapter.number}: {chapter.title}")

        if progress_callback:
            progress_callback(chapter.number, total_chapters)

        content = generate_chapter(
            client,
            chapter.number,
            course_state,
            plan_chapters,
            source_document,
            output_dir,
            model,
        )
        results.append(content)

    return results
