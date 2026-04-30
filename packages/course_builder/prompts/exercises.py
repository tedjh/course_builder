"""Prompts for generating exercises and solutions."""

EXERCISES_PROMPT = """You are an expert educator creating exercises for a learning chapter.

## Context
- **Course Topic:** {topic}
- **Learning Purpose:** {learning_purpose}
- **Chapter {chapter_number}:** {chapter_title}
- **Learning Objectives:**
{learning_objectives}

## Chapter Reading Material
{reading_content}

## Source Content (for reference to existing exercises)
{source_content}

## Your Task
Create a comprehensive set of exercises that test whether the learner has mastered this chapter's material, tailored to their learning purpose: "{learning_purpose}"

### Exercise Requirements

#### Theoretical Exercises (up to 10)
Create exercises that test understanding of key concepts. Include a mix of:
- **Conceptual questions** (explain, compare, analyze)
- **Calculation problems** (apply formulas, work through examples)
- **True/False with justification**
- **Short answer** questions

For each exercise:
- Clearly number it (Exercise 1, Exercise 2, etc.)
- Indicate difficulty level: [Basic], [Intermediate], or [Advanced]
- If referencing a source PDF exercise, note: "See Exercise X.Y on page Z of the source PDF"
- For Claude-generated exercises, mark with: [Solution provided]

#### Practical Projects (1-3, optional)
If appropriate for this chapter's content, suggest hands-on projects that:
- Apply the concepts in a practical context
- Are scoped for approximately 2-4 hours of work
- Align with the learner's purpose: "{learning_purpose}"

### Output Format

# Chapter {chapter_number} Exercises

## Theoretical Exercises

### Exercise 1 [Basic] [Solution provided]
[Exercise description]

### Exercise 2 [Intermediate]
See Exercise 3.2 on page 47 of the source PDF.
[Optional: Brief note about what this exercise covers]

### Exercise 3 [Advanced] [Solution provided]
[Exercise description]

...

## Practical Projects

### Project 1: [Project Title]
**Objective:** [What they will build/do]
**Skills Applied:** [List of concepts from chapter]
**Suggested Approach:**
1. [Step 1]
2. [Step 2]
...

---

## Formatting Requirements
- Use proper markdown formatting
- ALL mathematical formulas must use LaTeX notation:
  - Inline: $formula$
  - Display: $$formula$$
- Clearly distinguish between source PDF exercises and Claude-generated ones
- Number all exercises sequentially

## Output
Write the exercises directly in markdown format.
"""

SOLUTIONS_PROMPT = """You are an expert educator providing solutions for exercises.

## Context
- **Course Topic:** {topic}
- **Chapter {chapter_number}:** {chapter_title}

## Exercises (Claude-generated ones that need solutions)
{exercises_content}

## Your Task
Provide detailed solutions ONLY for exercises marked with [Solution provided].
Do NOT provide solutions for exercises that reference the source PDF.

For each solution:
1. **Restate the problem briefly**
2. **Provide step-by-step solution**
3. **Explain the reasoning** at each step
4. **Highlight key insights** or common mistakes

### Output Format

# Chapter {chapter_number} Solutions

## Exercise 1 Solution

**Problem:** [Brief restatement]

**Solution:**
[Detailed step-by-step solution]

**Key Insight:** [Important takeaway or common mistake to avoid]

---

## Exercise 3 Solution

**Problem:** [Brief restatement]

**Solution:**
[Detailed step-by-step solution]

**Key Insight:** [Important takeaway or common mistake to avoid]

---

[Continue for all exercises marked with [Solution provided]]

---

## Formatting Requirements
- Use proper markdown formatting
- ALL mathematical formulas must use LaTeX notation:
  - Inline: $formula$
  - Display: $$formula$$
- Show all work clearly
- Use numbered steps for multi-step solutions

## Output
Write the solutions directly in markdown format.
"""

EXERCISE_QUALITY_CHECK_PROMPT = """Review these exercises for quality and alignment.

## Learning Objectives
{learning_objectives}

## Learning Purpose
{learning_purpose}

## Exercises to Review
{exercises_content}

## Check For:
1. Do exercises cover all learning objectives?
2. Is there appropriate difficulty progression?
3. Are exercises aligned with the stated learning purpose?
4. Are there any unclear or ambiguous questions?
5. Is the mix of exercise types appropriate?

## Output
Provide a brief assessment and any suggested improvements.
"""
