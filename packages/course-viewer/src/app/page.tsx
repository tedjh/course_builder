import Link from 'next/link';
import { getCourses, getCourseInfo } from '@/lib/courses';

export default function HomePage() {
  const courseIds = getCourses();
  const courses = courseIds
    .map(id => getCourseInfo(id))
    .filter((c): c is NonNullable<typeof c> => c !== null);

  return (
    <main className="min-h-screen py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Course Viewer</h1>
        <p className="text-lg text-gray-600 mb-8">
          Select a course to begin studying
        </p>

        {courses.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <p className="text-gray-500">No courses found.</p>
            <p className="text-sm text-gray-400 mt-2">
              Generate a course using the course builder CLI, then refresh this page.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {courses.map((course) => (
              <Link
                key={course.slug}
                href={`/course/${course.slug}`}
                className="block bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-gray-300 transition-all"
              >
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  {course.topic}
                </h2>
                <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    {course.chapters.length} chapters
                  </span>
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {course.learningPurpose}
                  </span>
                </div>
                {course.overview && (
                  <p className="text-gray-600 text-sm line-clamp-2">
                    {course.overview}
                  </p>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
