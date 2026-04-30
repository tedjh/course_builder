"""Course plan generation and iteration."""

import json
import re
from dataclasses import dataclass
from typing import Optional

from anthropic import Anthropic

from .course_state import ChapterState, CourseState
from .prompts.planning import (
    PLAN_GENERATION_PROMPT,
    PLAN_REVISION_PROMPT,
    PLAN_TO_CHAPTERS_PROMPT,
)
from .source_document import SourceDocument


@dataclass
class CoursePlan:
    """Represents a generated course plan."""

    content: str  # Full markdown content of the plan
    chapters: list[dict]  # Parsed chapter information


def generate_plan(
    client: Anthropic,
    topic: str,
    learning_purpose: str,
    source_document: SourceDocument,
    model: str = "claude-sonnet-4-5",
) -> CoursePlan:
    """
    Generate an initial course plan based on the topic and source content.

    Args:
        client: Anthropic API client
        topic: The topic to learn about
        learning_purpose: Why the user is learning this topic
        source_document: The parsed source document (PDF or webpage)
        model: Claude model to use

    Returns:
        CoursePlan with the generated plan content and parsed chapters
    """
    # Get a summary of the source for planning
    source_summary = source_document.get_summary_text(max_sections=15)

    # Create source description based on type
    if source_document.source_type == "pdf":
        source_description = f"A PDF document ({source_document.source_name}) with {source_document.total_sections} pages"
    else:
        source_description = f"A webpage ({source_document.source_name}) with {source_document.total_sections} sections"

    prompt = PLAN_GENERATION_PROMPT.format(
        topic=topic,
        learning_purpose=learning_purpose,
        source_description=source_description,
        source_summary=source_summary,
    )

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    assert response.content[0].type == "text"
    plan_content = response.content[0].text

    # Parse chapters from the plan
    chapters = parse_chapters_from_plan(client, plan_content, model)

    return CoursePlan(content=plan_content, chapters=chapters)


def revise_plan(
    client: Anthropic,
    current_plan: str,
    user_feedback: str,
    learning_purpose: str,
    model: str = "claude-sonnet-4-5",
) -> CoursePlan:
    """
    Revise a course plan based on user feedback.

    Args:
        client: Anthropic API client
        current_plan: The current plan markdown content
        user_feedback: User's requested changes
        learning_purpose: Original learning purpose for context
        model: Claude model to use

    Returns:
        CoursePlan with the revised plan content and parsed chapters
    """
    prompt = PLAN_REVISION_PROMPT.format(
        current_plan=current_plan,
        user_feedback=user_feedback,
        learning_purpose=learning_purpose,
    )

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    assert response.content[0].type == "text"
    plan_content = response.content[0].text

    # Parse chapters from the revised plan
    chapters = parse_chapters_from_plan(client, plan_content, model)

    return CoursePlan(content=plan_content, chapters=chapters)


def parse_chapters_from_markdown(plan_content: str) -> list[dict]:
    """
    Fallback parser that extracts chapters directly from markdown using regex.

    Args:
        plan_content: The plan markdown content

    Returns:
        List of chapter dictionaries with basic information
    """
    chapters = []

    # Match chapter headers like "### Chapter 1: Title" or "### Chapter 1 - Title"
    chapter_pattern = r"###\s*Chapter\s+(\d+)[:\-\s]+([^\n]+)"
    matches = re.findall(chapter_pattern, plan_content, re.IGNORECASE)

    for number_str, title in matches:
        chapters.append(
            {
                "number": int(number_str),
                "title": title.strip(),
                "description": "",
                "source_sections": "1-10",
                "dependencies": [],
                "learning_objectives": [],
            }
        )

    return chapters


def parse_chapters_from_plan(
    client: Anthropic,
    plan_content: str,
    model: str = "claude-sonnet-4-5",
) -> list[dict]:
    """
    Parse chapter information from plan markdown using Claude.

    Args:
        client: Anthropic API client
        plan_content: The plan markdown content
        model: Claude model to use

    Returns:
        List of chapter dictionaries with structured information
    """
    prompt = PLAN_TO_CHAPTERS_PROMPT.format(plan_content=plan_content)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        assert response.content[0].type == "text"
        response_text = response.content[0].text

        # Extract JSON from the response
        json_match = re.search(r"\[[\s\S]*\]", response_text)
        if json_match:
            try:
                chapters = json.loads(json_match.group())
                if chapters:  # Only return if we got actual chapters
                    return chapters
            except json.JSONDecodeError:
                print("Warning: Failed to parse chapters JSON from Claude response")

        # Fallback: try to parse the whole response as JSON
        try:
            chapters = json.loads(response_text)
            if chapters:
                return chapters
        except json.JSONDecodeError:
            pass

    except Exception as e:
        print(f"Warning: Claude API call for chapter parsing failed: {e}")

    # Final fallback: parse chapters directly from markdown
    print("Using fallback markdown parser for chapters...")
    chapters = parse_chapters_from_markdown(plan_content)

    if not chapters:
        print("Warning: Could not extract any chapters from the plan!")

    return chapters


def plan_to_course_state(
    plan: CoursePlan,
    topic: str,
    learning_purpose: str,
    source_path: str,
    source_type: str = "pdf",
) -> CourseState:
    """
    Convert a course plan to an initial CourseState for tracking.

    Args:
        plan: The generated course plan
        topic: Course topic
        learning_purpose: Why the user is learning
        source_path: Path to the source PDF or URL
        source_type: Type of source ("pdf" or "webpage")

    Returns:
        CourseState initialized from the plan
    """
    state = CourseState(
        topic=topic,
        learning_purpose=learning_purpose,
        source_path=source_path,
        source_type=source_type,
    )

    for chapter_data in plan.chapters:
        # Parse dependencies
        deps = chapter_data.get("dependencies", [])
        if isinstance(deps, str):
            # Handle string like "Chapter 1, Chapter 2"
            deps = [int(d) for d in re.findall(r"\d+", deps)]

        chapter = ChapterState(
            number=chapter_data.get("number", len(state.chapters) + 1),
            title=chapter_data.get("title", f"Chapter {len(state.chapters) + 1}"),
            status="pending",
            dependencies=deps,
        )
        state.chapters.append(chapter)

    return state


def display_plan(plan: CoursePlan) -> str:
    """
    Format the plan for display to the user.

    Args:
        plan: The course plan to display

    Returns:
        Formatted string for console display
    """
    return plan.content


def get_chapter_info(plan: CoursePlan, chapter_number: int) -> Optional[dict]:
    """
    Get information for a specific chapter from the plan.

    Args:
        plan: The course plan
        chapter_number: Chapter number to retrieve

    Returns:
        Chapter dictionary or None if not found
    """
    for chapter in plan.chapters:
        if chapter.get("number") == chapter_number:
            return chapter
    return None
