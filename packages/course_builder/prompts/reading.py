"""Prompts for generating chapter reading materials."""

READING_INTRO_PROMPT = """You are an expert educator writing an introduction for a learning chapter.

## Context
- **Course Topic:** {topic}
- **Learning Purpose:** {learning_purpose}
- **Chapter {chapter_number}:** {chapter_title}
- **Chapter Description:** {chapter_description}
- **Learning Objectives:**
{learning_objectives}

## Previous Chapter Context
{previous_context}

## Your Task
Write a compelling 1-2 page introduction for this chapter that includes:

1. **High-Level Overview** (2-3 paragraphs)
   - What the learner will discover in this chapter
   - Why this topic matters, especially for their purpose: "{learning_purpose}"
   - How this connects to what they've learned before (if applicable)

2. **Key Terminology**
   - Define 3-7 essential terms they'll encounter
   - Use clear, accessible language
   - Include any mathematical notation with proper LaTeX formatting

3. **Conceptual Overview** (2-3 paragraphs)
   - Explain the core concepts in accessible language
   - Use analogies or examples where helpful
   - Build intuition before they dive into the detailed source material

## Formatting Requirements
- Use proper markdown formatting
- ALL mathematical formulas must use LaTeX notation:
  - Inline: $formula$
  - Display: $$formula$$
- Never use plain text for mathematical expressions
- Use clear headings and bullet points for readability

## Output
Write the introduction directly in markdown format.
"""

READING_GUIDE_PROMPT = """You are an expert educator creating a guided reading assignment.

## Context
- **Course Topic:** {topic}
- **Learning Purpose:** {learning_purpose}
- **Chapter {chapter_number}:** {chapter_title}
- **Source Material:** {source_name}
- **Relevant Sections:** {source_sections}

## Source Content from Relevant Sections
{source_content}

## Your Task
Create a guided reading assignment that helps the learner navigate the source material effectively.

Structure your guide as follows:

### Reading Assignment

**Sections to Study:** {source_sections}

**Reading Approach:**
[Suggest how to approach this reading - skim first? Read carefully? Take notes on specific items?]

### Section-by-Section Guide

For each major section in the assigned material, provide:

#### [Section/Topic Name]
- **Focus:** What to pay attention to
- **Key Figures/Tables:** Highlight important visual elements with specific references
- **Annotations:** Your notes to help them understand difficult passages
- **For Your Purpose:** How this relates to "{learning_purpose}"

### What to Skip or Skim
[Identify any sections that are:
- Too advanced for current level
- Not relevant to their learning purpose
- Optional/supplementary]

### Must-Know Items
[List the absolute essential concepts, formulas, or facts they must understand from this reading]

## Formatting Requirements
- Use proper markdown formatting
- Reference specific sections throughout
- ALL mathematical formulas must use LaTeX notation
- Be specific and actionable in your guidance

## Output
Write the guided reading assignment directly in markdown format.
"""

READING_SYNTHESIS_PROMPT = """You are an expert educator writing a synthesis section for a learning chapter.

## Context
- **Course Topic:** {topic}
- **Learning Purpose:** {learning_purpose}
- **Chapter {chapter_number}:** {chapter_title}
- **Learning Objectives:**
{learning_objectives}

## Chapter Introduction (already written)
{introduction}

## Reading Assignment (already created)
{reading_guide}

## Next Chapter Preview
{next_chapter_info}

## Your Task
Write a 1-page synthesis section that:

1. **Key Takeaways** (5-7 bullet points)
   - Summarize the most important concepts in your own words
   - Emphasize what matters most for their purpose: "{learning_purpose}"

2. **Connections to Previous Chapters**
   - How does this build on earlier material?
   - What concepts from before are now clearer or more complete?

3. **Common Misconceptions** (2-4 items)
   - Address typical confusions or mistakes
   - Clarify subtle but important distinctions

4. **Looking Ahead**
   - How does this chapter prepare them for what's next?
   - What concepts will be built upon in future chapters?

## Formatting Requirements
- Use proper markdown formatting
- ALL mathematical formulas must use LaTeX notation:
  - Inline: $formula$
  - Display: $$formula$$
- Keep it concise - approximately 1 page

## Output
Write the synthesis section directly in markdown format.
"""

FULL_READING_PROMPT = """You are an expert educator creating the complete reading material for a learning chapter.

## Context
- **Course Topic:** {topic}
- **Learning Purpose:** {learning_purpose}
- **Chapter {chapter_number}:** {chapter_title}
- **Chapter Description:** {chapter_description}
- **Learning Objectives:**
{learning_objectives}
- **Source Material:** {source_name} ({source_sections})

## Previous Chapter Context
{previous_context}

## Source Content from Relevant Sections
{source_content}

## Next Chapter Preview
**Next Chapter:** {next_chapter_title}
**Description:** {next_chapter_description}

## Your Task
Create the complete reading material for this chapter with the following structure:

---

# Chapter {chapter_number}: {chapter_title}

## Introduction
[1-2 pages covering:
- High-level overview of the chapter
- Why this matters for the learner's purpose
- Key terminology (3-7 terms defined)
- Conceptual overview in accessible language]

## Guided Reading

### Reading Assignment
**Sections to Study:** [specific sections from source]
**Suggested Approach:** [how to approach the reading]

### Section-by-Section Guide
[For each major section:
- Focus points
- Key figures/tables with references
- Annotations for difficult passages
- Relevance to learning purpose]

### What to Skip or Skim
[Optional/supplementary sections]

### Must-Know Items
[Essential concepts, formulas, facts]

## Synthesis

### Key Takeaways
[5-7 bullet points summarizing core concepts]

### Connections
[How this builds on previous material]

### Common Misconceptions
[2-4 typical confusions clarified]

### Looking Ahead
[Preview of how this connects to next chapter]

---

## Formatting Requirements
- Use proper markdown formatting with clear headings
- ALL mathematical formulas MUST use LaTeX notation:
  - Inline: $formula$ (e.g., $x^2 + y^2 = z^2$)
  - Display: $$formula$$ (e.g., $$\\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}}$$)
- NEVER use plain text for formulas (no "x^2", always "$x^2$")
- Reference specific sections from source material
- Attribute source material appropriately

## Output
Write the complete reading material directly in markdown format.
"""
