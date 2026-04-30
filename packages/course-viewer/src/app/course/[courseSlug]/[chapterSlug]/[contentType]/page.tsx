import { getCourseInfo, getChapterContent, getAllChapterPaths, splitReadingSections } from '@/lib/courses';
import MarkdownRenderer from '@/components/MarkdownRenderer';
import ExerciseRenderer from '@/components/ExerciseRenderer';
import ReadingTabs from '@/components/ReadingTabs';
import { notFound } from 'next/navigation';
import Link from 'next/link';

interface PageProps {
  params: Promise<{
    courseSlug: string;
    chapterSlug: string;
    contentType: 'reading' | 'exercises' | 'solutions';
  }>;
}

export async function generateStaticParams() {
  const paths = getAllChapterPaths();
  const allParams: { courseSlug: string; chapterSlug: string; contentType: string }[] = [];

  for (const { course, chapter } of paths) {
    for (const contentType of ['reading', 'exercises', 'solutions']) {
      allParams.push({
        courseSlug: course,
        chapterSlug: chapter,
        contentType,
      });
    }
  }

  return allParams;
}

export default async function ChapterContentPage({ params }: PageProps) {
  const { courseSlug, chapterSlug, contentType } = await params;

  const course = getCourseInfo(courseSlug);
  const content = getChapterContent(courseSlug, chapterSlug, contentType);

  if (!course || !content) {
    notFound();
  }

  // Find current chapter info
  const currentChapter = course.chapters.find(c => c.slug === chapterSlug);
  if (!currentChapter) {
    notFound();
  }

  // Find previous and next chapters
  const currentIndex = course.chapters.findIndex(c => c.slug === chapterSlug);
  const prevChapter = currentIndex > 0 ? course.chapters[currentIndex - 1] : null;
  const nextChapter = currentIndex < course.chapters.length - 1 ? course.chapters[currentIndex + 1] : null;

  // Content type tabs
  const tabs = [
    { key: 'reading', label: 'Reading', available: currentChapter.hasReading },
    { key: 'exercises', label: 'Exercises', available: currentChapter.hasExercises },
    { key: 'solutions', label: 'Solutions', available: currentChapter.hasSolutions },
  ].filter(tab => tab.available);

  return (
    <div>
      {/* Breadcrumb */}
      <nav className="text-sm text-gray-500 mb-4">
        <Link href={`/course/${courseSlug}`} className="hover:text-gray-700">
          {course.topic}
        </Link>
        <span className="mx-2">/</span>
        <span className="text-gray-900">Chapter {currentChapter.number}</span>
      </nav>

      {/* Chapter header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {currentChapter.title}
        </h1>

        {/* Content type tabs */}
        <div className="flex gap-2 mt-4 border-b border-gray-200 pb-4">
          {tabs.map((tab) => (
            <Link
              key={tab.key}
              href={`/course/${courseSlug}/${chapterSlug}/${tab.key}`}
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${contentType === tab.key
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
                }
              `}
            >
              {tab.label}
            </Link>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 lg:p-8 shadow-sm">
        {contentType === 'reading' ? (
          <ReadingTabs sections={splitReadingSections(content.content)} />
        ) : contentType === 'exercises' ? (
          <ExerciseRenderer content={content.content} />
        ) : (
          <MarkdownRenderer content={content.content} />
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
        {prevChapter ? (
          <Link
            href={`/course/${courseSlug}/${prevChapter.slug}/reading`}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>
              <span className="block text-xs text-gray-400">Previous</span>
              <span className="font-medium">Chapter {prevChapter.number}</span>
            </span>
          </Link>
        ) : (
          <div />
        )}

        {nextChapter ? (
          <Link
            href={`/course/${courseSlug}/${nextChapter.slug}/reading`}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <span className="text-right">
              <span className="block text-xs text-gray-400">Next</span>
              <span className="font-medium">Chapter {nextChapter.number}</span>
            </span>
            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        ) : (
          <div />
        )}
      </div>
    </div>
  );
}
