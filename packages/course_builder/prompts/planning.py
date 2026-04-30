"""Prompts for course plan generation and revision."""

PLAN_GENERATION_PROMPT = """You are an expert course designer creating a personalized learning curriculum.

## Context
- **Topic:** {topic}
- **Learning Purpose:** {learning_purpose}
- **Source Material:** {source_description}

## Source Material Overview
The following is an excerpt from the beginning of the source material to help you understand its structure and content:

{source_summary}

## Your Task
Create a high-level course plan with the following requirements:

1. **Course Length:** Design a semester-length course with up to 10 chapters. Each chapter should take approximately one week to complete.

2. **Chapter Structure:** For each chapter, provide:
   - A clear, descriptive title
   - A brief description (2-3 sentences) of what the chapter covers
   - The relevant sections from the source material (for PDFs: page ranges like "1-25"; for webpages: section names like "Introduction, Getting Started")
   - Key learning objectives (3-5 bullet points)
   - Any dependencies on previous chapters

3. **Progression:** Ensure logical progression from foundational concepts to advanced topics.

4. **Alignment:** Tailor the depth and focus of each chapter to the learner's stated purpose: "{learning_purpose}"

## Output Format
Provide the course plan in the following markdown format:

# Course Plan: [Course Title]

## Course Overview
[2-3 paragraph overview of the course, what the learner will achieve, and how it aligns with their purpose]

## Chapters

### Chapter 1: [Title]
**Description:** [2-3 sentences]
**Source Sections:** [section reference - for PDF: "pages 1-25", for webpage: "Sections: Introduction, Getting Started"]
**Dependencies:** None
**Learning Objectives:**
- [Objective 1]
- [Objective 2]
- [Objective 3]

### Chapter 2: [Title]
...

[Continue for all chapters]

## Course Summary
[Brief summary of the complete learning journey]
"""

PLAN_REVISION_PROMPT = """You are an expert course designer revising a learning curriculum based on user feedback.

## Original Plan
{current_plan}

## User Feedback
{user_feedback}

## Your Task
Revise the course plan based on the user's feedback. Maintain the same output format as the original plan.

Key considerations:
- Address all specific points raised in the feedback
- Maintain logical progression and dependencies between chapters
- Keep the course length appropriate (up to 10 chapters, semester-length)
- Ensure the revisions still align with the learning purpose: "{learning_purpose}"

Provide the complete revised plan in the same markdown format.
"""

PLAN_TO_CHAPTERS_PROMPT = """Extract the chapter information from this course plan as a structured list.

## Course Plan
{plan_content}

## Output Format
Return a JSON array with each chapter's details:
```json
[
  {{
    "number": 1,
    "title": "Chapter Title",
    "description": "Brief description",
    "source_sections": "pages 1-25 OR Sections: Intro, Getting Started",
    "dependencies": [],
    "learning_objectives": ["obj1", "obj2", "obj3"]
  }},
  ...
]
```

Only output the JSON array, no additional text.
"""
