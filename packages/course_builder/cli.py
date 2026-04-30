"""Command-line interface for user consultation and course building."""

import os
import re
from pathlib import Path
from typing import Optional

from anthropic import Anthropic
from tqdm import tqdm

from .chapter_generator import generate_all_chapters
from .course_state import CourseState, load_course_state, save_course_state
from .pdf_reader import extract_pdf
from .planner import (
    CoursePlan,
    display_plan,
    generate_plan,
    plan_to_course_state,
    revise_plan,
)
from .source_document import SourceDocument
from .utils import write_markdown_file
from .web_reader import extract_webpage


def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    """Get input from user with optional default value."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    response = input(prompt).strip()
    if not response and default:
        return default
    return response


def get_path_input(prompt: str, must_exist: bool = False) -> Path:
    """Get a file/directory path from user with validation."""
    while True:
        path_str = get_user_input(prompt)
        path = Path(path_str).expanduser().resolve()

        if must_exist and not path.exists():
            print(f"Error: Path does not exist: {path}")
            continue

        return path


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def get_url_input(prompt: str) -> str:
    """Get a URL from user with validation."""
    while True:
        url = get_user_input(prompt)
        if is_valid_url(url):
            return url
        print("Error: Please enter a valid URL (starting with http:// or https://)")


def confirm(prompt: str, default: bool = True) -> bool:
    """Get yes/no confirmation from user."""
    suffix = " [Y/n]: " if default else " [y/N]: "
    response = input(prompt + suffix).strip().lower()

    if not response:
        return default
    return response in ("y", "yes")


def print_header(text: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")


def print_step(step_num: int, text: str) -> None:
    """Print a step indicator."""
    print(f"\n[Step {step_num}] {text}")
    print("-" * 40)


def initial_consultation() -> dict:
    """
    Conduct initial consultation with user to gather course requirements.

    Returns:
        Dictionary with topic, learning_purpose, source_type, source_path, output_dir
    """
    print_header("Course Builder - Initial Consultation")

    print("Welcome! I'll help you create a personalized learning course.")
    print("Please provide the following information:\n")

    # Topic
    topic = get_user_input("What topic would you like to learn about?")
    while not topic:
        print("Topic is required.")
        topic = get_user_input("What topic would you like to learn about?")

    # Learning purpose
    print("\nWhy are you learning about this topic?")
    print("(e.g., for an interview, certification, academic course, personal interest)")
    learning_purpose = get_user_input("Your purpose")
    while not learning_purpose:
        print("Learning purpose is required.")
        learning_purpose = get_user_input("Your purpose")

    # Source type selection
    print("\nWhat type of source material will you use?")
    print("  [1] PDF file")
    print("  [2] Webpage URL")
    source_choice = get_user_input("Enter choice (1 or 2)", default="1")

    if source_choice == "2":
        # Webpage source
        print("\nPlease provide the URL of your source webpage.")
        print("This webpage will be the primary reference for the course content.")
        source_url = get_url_input("Webpage URL")

        source_type = "webpage"
        source_path = source_url
    else:
        # PDF source (default)
        print("\nPlease provide the path to your source PDF file.")
        print("This PDF will be the primary reference for the course content.")
        pdf_path = get_path_input("PDF file path", must_exist=True)
        while not pdf_path.suffix.lower() == ".pdf":
            print("Error: File must be a PDF.")
            pdf_path = get_path_input("PDF file path", must_exist=True)

        source_type = "pdf"
        source_path = str(pdf_path)

    # Output directory
    print("\nWhere should the course content be saved?")
    output_dir = get_path_input("Output directory")
    if not output_dir.exists():
        if confirm(f"Directory {output_dir} does not exist. Create it?"):
            output_dir.mkdir(parents=True)
        else:
            print("Cannot proceed without output directory.")
            raise SystemExit(1)

    return {
        "topic": topic,
        "learning_purpose": learning_purpose,
        "source_type": source_type,
        "source_path": source_path,
        "output_dir": output_dir,
    }


def load_source_document(source_type: str, source_path: str) -> SourceDocument:
    """
    Load source document based on type.

    Args:
        source_type: "pdf" or "webpage"
        source_path: File path or URL

    Returns:
        SourceDocument instance
    """
    if source_type == "webpage":
        print(f"Fetching webpage: {source_path}")
        return extract_webpage(source_path)
    else:
        print(f"Loading PDF: {source_path}")
        return extract_pdf(Path(source_path))


def plan_iteration_loop(
    client: Anthropic,
    plan: CoursePlan,
    learning_purpose: str,
    model: str = "claude-sonnet-4-20250514",
) -> CoursePlan:
    """
    Allow user to iterate on the course plan until satisfied.

    Args:
        client: Anthropic API client
        plan: Initial course plan
        learning_purpose: User's learning purpose
        model: Claude model to use

    Returns:
        Final approved course plan
    """
    while True:
        print("\n" + display_plan(plan))

        print("\n" + "-" * 40)
        print("Options:")
        print("  [Enter] - Accept this plan and proceed")
        print("  [e] - Edit: Provide feedback to revise the plan")
        print("  [q] - Quit without saving")

        choice = input("\nYour choice: ").strip().lower()

        if choice == "":
            print("\nPlan approved! Proceeding to chapter generation...")
            return plan

        elif choice == "e":
            print("\nWhat changes would you like to make to the plan?")
            print("(Describe your requested changes in detail)")
            feedback = []
            print("Enter your feedback (empty line to finish):")
            while True:
                line = input()
                if not line:
                    break
                feedback.append(line)

            feedback_text = "\n".join(feedback)
            if feedback_text:
                print("\nRevising plan based on your feedback...")
                plan = revise_plan(
                    client, plan.content, feedback_text, learning_purpose, model
                )
            else:
                print("No feedback provided. Showing current plan again.")

        elif choice == "q":
            if confirm("Are you sure you want to quit?", default=False):
                print("Exiting...")
                raise SystemExit(0)


def generate_master_readme(
    course_state: CourseState,
    plan: CoursePlan,
    output_dir: Path,
) -> None:
    """
    Generate the master README.md with course overview and chapter index.

    Args:
        course_state: Course state with chapter information
        plan: Course plan with overview content
        output_dir: Output directory
    """
    # Extract course title from plan if available
    lines = plan.content.split("\n")
    title = f"Course: {course_state.topic}"
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Determine source label based on type
    source_label = "Source Material"
    if course_state.source_type == "pdf":
        source_display = Path(course_state.source_path).name
    else:
        source_display = course_state.source_path

    readme_parts = [
        f"# {title}",
        "",
        f"**Topic:** {course_state.topic}",
        f"**Learning Purpose:** {course_state.learning_purpose}",
        f"**{source_label}:** {source_display}",
        "",
        "---",
        "",
        "## Course Overview",
        "",
    ]

    # Extract overview from plan if available
    in_overview = False
    overview_lines = []
    for line in lines:
        if "## Course Overview" in line or "## Overview" in line:
            in_overview = True
            continue
        if in_overview:
            if line.startswith("## "):
                break
            overview_lines.append(line)

    if overview_lines:
        readme_parts.extend(overview_lines)
    else:
        readme_parts.append(f"A personalized course on {course_state.topic}.")

    readme_parts.extend(
        [
            "",
            "---",
            "",
            "## Chapters",
            "",
        ]
    )

    # Add chapter links
    for chapter in course_state.chapters:
        status = {
            "pending": "\u23f3",
            "in_progress": "\ud83d\udd04",
            "completed": "\u2705",
        }.get(chapter.status, "\u2753")

        readme_parts.append(
            f"{status} **[Chapter {chapter.number}: {chapter.title}](chapter-{chapter.number}/reading.md)**"
        )
        if chapter.summary:
            readme_parts.append(f"   {chapter.summary[:100]}...")
        readme_parts.append("")

    readme_parts.extend(
        [
            "---",
            "",
            "## How to Use This Course",
            "",
            "1. Read through each chapter's `reading.md` file",
            "2. Complete the exercises in `exercises.md`",
            "3. Check your answers against `solutions.md`",
            "4. Progress to the next chapter once you feel comfortable with the material",
            "",
            "---",
            "",
            "*Generated with Course Builder*",
        ]
    )

    content = "\n".join(readme_parts)
    write_markdown_file(output_dir / "README.md", content)


def run_course_builder(
    api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-20250514",
) -> None:
    """
    Main entry point for the course builder CLI.

    Args:
        api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
        model: Claude model to use
    """
    # Initialize API client
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is required.")
        print("Please set it with: export ANTHROPIC_API_KEY=your-key-here")
        raise SystemExit(1)

    client = Anthropic(api_key=api_key)

    # Step 1: Initial consultation
    print_step(1, "Initial Consultation")
    consultation = initial_consultation()

    topic = consultation["topic"]
    learning_purpose = consultation["learning_purpose"]
    source_type = consultation["source_type"]
    source_path = consultation["source_path"]
    output_dir = consultation["output_dir"]

    # Check for existing course state
    existing_state = load_course_state(output_dir)
    if existing_state:
        print(f"\nFound existing course in {output_dir}")
        if confirm("Would you like to resume the existing course?"):
            # Resume existing course
            print("Resuming existing course...")
            course_state = existing_state

            # Load source document
            print("\nLoading source material...")
            source_document = load_source_document(
                course_state.source_type,
                course_state.source_path
            )
            print(f"Loaded: {source_document.total_sections} sections")

            # We need to regenerate plan chapters from state for generation
            plan_chapters = [
                {"number": c.number, "title": c.title, "source_sections": "1-10"}
                for c in course_state.chapters
            ]

            print_step(4, "Chapter Generation (Resuming)")
            generate_all_chapters(
                client, course_state, plan_chapters, source_document, output_dir, model
            )

            print_header("Course Complete!")
            print(f"Course content saved to: {output_dir}")
            return

    # Step 2: Load and analyze source document
    print_step(2, "Loading Source Material")
    source_document = load_source_document(source_type, source_path)
    print(f"Loaded {source_document.total_sections} sections")

    # Step 3: Generate and iterate on plan
    print_step(3, "Course Plan Generation")
    print("Generating initial course plan...")
    plan = generate_plan(client, topic, learning_purpose, source_document, model)

    plan = plan_iteration_loop(client, plan, learning_purpose, model)

    # Create course state from plan
    course_state = plan_to_course_state(
        plan, topic, learning_purpose, source_path, source_type
    )
    save_course_state(course_state, output_dir)

    # Step 4: Generate chapters
    print_step(4, "Chapter Generation")
    print(f"Generating {len(course_state.chapters)} chapters...")
    print("This may take a while. Progress will be shown below.\n")

    with tqdm(total=len(course_state.chapters), desc="Chapters") as pbar:

        def update_progress(chapter_num: int, total: int):
            pbar.update(1)
            pbar.set_description(f"Chapter {chapter_num}/{total}")

        generate_all_chapters(
            client,
            course_state,
            plan.chapters,
            source_document,
            output_dir,
            model,
            progress_callback=update_progress,
        )

    # Generate master README
    print("\nGenerating course overview...")
    generate_master_readme(course_state, plan, output_dir)

    print_header("Course Complete!")
    print(f"Course content saved to: {output_dir}")
    print("\nGenerated files:")
    print("  - README.md (course overview)")
    print("  - course_state.md (progress tracking)")
    for chapter in course_state.chapters:
        print(f"  - chapter-{chapter.number}/ (reading.md, exercises.md, solutions.md)")
