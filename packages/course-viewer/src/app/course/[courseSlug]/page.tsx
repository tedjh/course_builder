import { getCourseInfo, getCourseReadme } from '@/lib/courses';
import MarkdownRenderer from '@/components/MarkdownRenderer';
import { notFound } from 'next/navigation';
import Link from 'next/link';

interface PageProps {
  params: Promise<{ courseSlug: string }>;
}

export default async function CourseOverviewPage({ params }: PageProps) {
  const { courseSlug } = await params;
  const course = getCourseInfo(courseSlug);
  const readme = getCourseReadme(courseSlug);

  if (!course || !readme) {
    notFound();
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {course.topic}
        </h1>
        <p className="text-gray-600">
          Learning Purpose: {course.learningPurpose}
        </p>
        {course.sourceUrl && (
          <p className="text-sm text-gray-500 mt-2">
            Source:{' '}
            <a
              href={course.sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              {course.sourceUrl}
            </a>
          </p>
        )}
      </div>

      {/* Quick start */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
        <h2 className="text-lg font-semibold text-blue-900 mb-3">Get Started</h2>
        <p className="text-blue-800 mb-4">
          This course has {course.chapters.length} chapters. Start with Chapter 1 or browse the sidebar to jump to any chapter.
        </p>
        {course.chapters.length > 0 && (
          <Link
            href={`/course/${course.slug}/${course.chapters[0].slug}/reading`}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Start Chapter 1
            <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        )}
      </div>

      {/* Chapters list */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Chapters</h2>
        <div className="space-y-3">
          {course.chapters.map((chapter) => (
            <div
              key={chapter.slug}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="w-8 h-8 flex items-center justify-center bg-gray-100 rounded-full text-sm font-medium mr-3">
                    {chapter.number}
                  </span>
                  <span className="font-medium text-gray-900">
                    {chapter.title}
                  </span>
                </div>
                <div className="flex gap-2">
                  {chapter.hasReading && (
                    <Link
                      href={`/course/${course.slug}/${chapter.slug}/reading`}
                      className="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      Reading
                    </Link>
                  )}
                  {chapter.hasExercises && (
                    <Link
                      href={`/course/${course.slug}/${chapter.slug}/exercises`}
                      className="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      Exercises
                    </Link>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Full README content */}
      <div className="border-t border-gray-200 pt-8">
        <MarkdownRenderer content={readme} />
      </div>
    </div>
  );
}
