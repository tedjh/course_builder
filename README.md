# Course Builder

Generate personalised learning courses from a PDF or webpage using Claude, then study them in a local web viewer.

## Overview

The project has two packages that work together via a shared `results/` directory:

1. **`course_builder`** (Python CLI) — interactively consults you on a topic, ingests a source PDF or webpage, asks Claude to draft a chapter-by-chapter plan you can iterate on, and then generates each chapter as three markdown files: `reading.md`, `exercises.md`, and `solutions.md`.
2. **`course-viewer`** (Next.js app) — discovers every course in `results/` and renders it as a navigable web app with tabbed reading sections, collapsible exercise/solution pairs, syntax highlighting, and KaTeX-rendered LaTeX.

Generated courses live in [results/](results/), with one subdirectory per course (e.g. `results/mech_interp/`).

## Project structure

```
course_builder/
├── packages/
│   ├── course_builder/       # Python CLI — generates courses
│   │   ├── cli.py            # Interactive consultation + orchestration
│   │   ├── pdf_reader.py     # PDF ingestion (pdfplumber)
│   │   ├── web_reader.py     # Webpage ingestion (requests + BeautifulSoup)
│   │   ├── source_document.py# Abstract source interface
│   │   ├── planner.py        # Plan generation + revision loop
│   │   ├── chapter_generator.py # Reading / exercises / solutions generation
│   │   ├── course_state.py   # Persistent state (course_state.md)
│   │   └── prompts/          # Prompt templates for Claude
│   └── course-viewer/        # Next.js app — reads from results/
│       └── src/
│           ├── app/          # Routes (home, /course/[slug]/[chapter])
│           ├── components/   # Sidebar, MarkdownRenderer, ExerciseRenderer, ...
│           └── lib/courses.ts# Filesystem-based course discovery
├── results/                  # Generated course output (gitignored)
├── pyproject.toml
└── uv.lock
```

## Installation

### Course builder (Python)

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Set your Anthropic API key (the CLI reads from a `.env` in the working directory or from the environment):

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### Course viewer (Next.js)

Requires Node.js 18+.

```bash
cd packages/course-viewer
npm install
```

## Usage

### Generate a course

From the project root:

```bash
uv run course-builder
```

The CLI then walks you through:

1. **Consultation** — topic, learning purpose, source type (PDF or URL), and output directory (use a subdirectory of `results/` to make it visible to the viewer).
2. **Source ingestion** — extracts text from the PDF or webpage.
3. **Plan iteration** — Claude proposes a chapter outline; press Enter to accept, `e` to give feedback and regenerate, or `q` to quit.
4. **Chapter generation** — generates `reading.md`, `exercises.md`, and `solutions.md` for each chapter, with a progress bar.

Optional flags:

```bash
uv run course-builder --model claude-sonnet-4-5 --api-key sk-ant-...
```

If you re-run with the same output directory, the CLI detects the existing `course_state.md` and offers to resume from where it stopped.

### View courses in the browser

```bash
cd packages/course-viewer
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The viewer auto-discovers any course directory under `results/`, so newly generated courses appear after a refresh.

For a production build:

```bash
npm run build
npm run start
```

## Generated course layout

Each course directory under `results/` looks like:

```
results/<course-slug>/
├── README.md           # Course overview + chapter index
├── course_state.md     # Progress + chapter metadata (used to resume)
└── chapter-<n>/
    ├── reading.md
    ├── exercises.md
    └── solutions.md
```