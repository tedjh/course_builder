import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

// Path to the results directory containing generated courses
const RESULTS_DIR = path.join(process.cwd(), '..', '..', 'results');

export interface ChapterInfo {
  number: number;
  slug: string;
  title: string;
  hasReading: boolean;
  hasExercises: boolean;
  hasSolutions: boolean;
}

export interface CourseInfo {
  slug: string;
  title: string;
  topic: string;
  learningPurpose: string;
  sourceUrl?: string;
  overview: string;
  chapters: ChapterInfo[];
}

export interface ContentFile {
  content: string;
  title: string;
}

export interface ReadingSection {
  heading: string;
  content: string;
}

/**
 * Get all available courses from the results directory
 */
export function getCourses(): string[] {
  if (!fs.existsSync(RESULTS_DIR)) {
    return [];
  }

  return fs.readdirSync(RESULTS_DIR, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name);
}

/**
 * Parse the README.md to extract course information
 */
export function getCourseInfo(courseSlug: string): CourseInfo | null {
  const coursePath = path.join(RESULTS_DIR, courseSlug);
  const readmePath = path.join(coursePath, 'README.md');

  if (!fs.existsSync(readmePath)) {
    return null;
  }

  const readmeContent = fs.readFileSync(readmePath, 'utf-8');

  // Parse the README to extract info
  const titleMatch = readmeContent.match(/^# (.+)$/m);
  const topicMatch = readmeContent.match(/\*\*Topic:\*\* (.+)$/m);
  const purposeMatch = readmeContent.match(/\*\*Learning Purpose:\*\* (.+)$/m);
  const sourceMatch = readmeContent.match(/\*\*Source Material:\*\* (.+)$/m);

  // Extract overview (text between "## Course Overview" and the next ##)
  const overviewMatch = readmeContent.match(/## Course Overview\s+([\s\S]+?)(?=\n---|\n##)/);

  // Get chapters
  const chapters = getChapters(coursePath);

  return {
    slug: courseSlug,
    title: titleMatch?.[1] || courseSlug,
    topic: topicMatch?.[1] || '',
    learningPurpose: purposeMatch?.[1] || '',
    sourceUrl: sourceMatch?.[1],
    overview: overviewMatch?.[1]?.trim() || '',
    chapters,
  };
}

/**
 * Get all chapters for a course
 */
function getChapters(coursePath: string): ChapterInfo[] {
  const chapters: ChapterInfo[] = [];

  // Find all chapter directories
  const entries = fs.readdirSync(coursePath, { withFileTypes: true });

  for (const entry of entries) {
    if (!entry.isDirectory() || !entry.name.startsWith('chapter-')) {
      continue;
    }

    const chapterNum = parseInt(entry.name.replace('chapter-', ''), 10);
    const chapterPath = path.join(coursePath, entry.name);

    // Check which files exist
    const hasReading = fs.existsSync(path.join(chapterPath, 'reading.md'));
    const hasExercises = fs.existsSync(path.join(chapterPath, 'exercises.md'));
    const hasSolutions = fs.existsSync(path.join(chapterPath, 'solutions.md'));

    // Try to get chapter title from reading.md
    let title = `Chapter ${chapterNum}`;
    if (hasReading) {
      const readingContent = fs.readFileSync(path.join(chapterPath, 'reading.md'), 'utf-8');
      const titleMatch = readingContent.match(/^# (.+)$/m);
      if (titleMatch) {
        title = titleMatch[1];
      }
    }

    chapters.push({
      number: chapterNum,
      slug: entry.name,
      title,
      hasReading,
      hasExercises,
      hasSolutions,
    });
  }

  // Sort by chapter number
  chapters.sort((a, b) => a.number - b.number);

  return chapters;
}

/**
 * Get content for a specific chapter file
 */
export function getChapterContent(
  courseSlug: string,
  chapterSlug: string,
  fileType: 'reading' | 'exercises' | 'solutions'
): ContentFile | null {
  const filePath = path.join(RESULTS_DIR, courseSlug, chapterSlug, `${fileType}.md`);

  if (!fs.existsSync(filePath)) {
    return null;
  }

  const content = fs.readFileSync(filePath, 'utf-8');

  // Extract title from first heading
  const titleMatch = content.match(/^# (.+)$/m);
  const title = titleMatch?.[1] || `${chapterSlug} - ${fileType}`;

  return {
    content,
    title,
  };
}

/**
 * Get the course README content
 */
export function getCourseReadme(courseSlug: string): string | null {
  const readmePath = path.join(RESULTS_DIR, courseSlug, 'README.md');

  if (!fs.existsSync(readmePath)) {
    return null;
  }

  return fs.readFileSync(readmePath, 'utf-8');
}

/**
 * Split reading markdown into sections based on ## headings.
 * The content before the first ## (typically the # title) is discarded.
 */
export function splitReadingSections(markdown: string): ReadingSection[] {
  // Normalize Windows line endings
  const normalized = markdown.replace(/\r\n/g, '\n');

  // Split on ## headings, keeping the delimiter
  const parts = normalized.split(/^(?=## )/m);
  const sections: ReadingSection[] = [];

  for (const part of parts) {
    const match = part.match(/^## (.+)\n([\s\S]*)$/);
    if (match) {
      sections.push({
        heading: match[1].trim(),
        content: match[2].trim(),
      });
    }
  }

  return sections;
}

/**
 * Get all static paths for chapters
 */
export function getAllChapterPaths(): { course: string; chapter: string }[] {
  const paths: { course: string; chapter: string }[] = [];

  for (const courseSlug of getCourses()) {
    const courseInfo = getCourseInfo(courseSlug);
    if (!courseInfo) continue;

    for (const chapter of courseInfo.chapters) {
      paths.push({
        course: courseSlug,
        chapter: chapter.slug,
      });
    }
  }

  return paths;
}
