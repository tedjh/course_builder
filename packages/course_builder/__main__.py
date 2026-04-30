"""Entry point for running course_builder as a module."""

import argparse
import os
import sys

from dotenv import load_dotenv

from course_builder.cli import run_course_builder

# Load .env file from current working directory
load_dotenv()


def main():
    """Main entry point for the course builder CLI."""
    parser = argparse.ArgumentParser(
        prog="course_builder",
        description="Build personalized learning courses from PDF source materials using Claude.",
    )

    parser.add_argument(
        "--model",
        default="claude-sonnet-4-5",
        help="Claude model to use (default: claude-sonnet-4-20250514)",
    )

    parser.add_argument(
        "--api-key",
        default=os.getenv("ANTHROPIC_API_KEY"),
        help="Anthropic API key (defaults to ANTHROPIC_API_KEY env variable)",
    )

    args = parser.parse_args()

    try:
        run_course_builder(api_key=args.api_key, model=args.model)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
