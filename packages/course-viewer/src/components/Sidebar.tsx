'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChapterInfo, CourseInfo } from '@/lib/courses';

interface SidebarProps {
  course: CourseInfo;
}

export default function Sidebar({ course }: SidebarProps) {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [expandedChapters, setExpandedChapters] = useState<Set<string>>(new Set());

  const toggleChapter = (slug: string) => {
    setExpandedChapters(prev =>
      prev.has(slug) ? new Set() : new Set([slug])
    );
  };

  const isChapterActive = (chapter: ChapterInfo) => {
    return pathname.includes(`/${chapter.slug}`);
  };

  const isSubItemActive = (chapter: ChapterInfo, type: string) => {
    return pathname === `/course/${course.slug}/${chapter.slug}/${type}`;
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md border border-gray-200"
        aria-label="Toggle menu"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          {isOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-full w-72 bg-white border-r border-gray-200 z-40
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 overflow-y-auto
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="p-6">
          {/* Course title */}
          <Link href={`/course/${course.slug}`} className="block mb-6">
            <h1 className="text-lg font-bold text-gray-900 hover:text-blue-600 transition-colors">
              {course.topic}
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              {course.learningPurpose}
            </p>
          </Link>

          {/* Navigation */}
          <nav className="space-y-1">
            {/* Overview link */}
            <Link
              href={`/course/${course.slug}`}
              className={`
                flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors
                ${pathname === `/course/${course.slug}`
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }
              `}
              onClick={() => setIsOpen(false)}
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Overview
            </Link>

            {/* Chapters */}
            <div className="pt-4">
              <h2 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Chapters
              </h2>
              {course.chapters.map((chapter) => (
                <div key={chapter.slug} className="mb-1">
                  {/* Chapter header */}
                  <button
                    onClick={() => toggleChapter(chapter.slug)}
                    className={`
                      w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors
                      ${isChapterActive(chapter)
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                      }
                    `}
                  >
                    <span className="flex items-start">
                      <span className="w-6 h-6 flex items-center justify-center bg-gray-100 rounded text-xs font-medium mr-2 shrink-0 mt-0.5">
                        {chapter.number}
                      </span>
                      <span className="line-clamp-3 text-left">
                        {chapter.title.replace(/^Chapter \d+:\s*/, '')}
                      </span>
                    </span>
                    <svg
                      className={`w-4 h-4 transform transition-transform ${
                        expandedChapters.has(chapter.slug) ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {/* Chapter sub-items */}
                  {expandedChapters.has(chapter.slug) && (
                    <div className="ml-8 mt-1 space-y-1">
                      {chapter.hasReading && (
                        <Link
                          href={`/course/${course.slug}/${chapter.slug}/reading`}
                          className={`
                            block px-3 py-1.5 rounded text-sm transition-colors
                            ${isSubItemActive(chapter, 'reading')
                              ? 'bg-blue-100 text-blue-700'
                              : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700'
                            }
                          `}
                          onClick={() => setIsOpen(false)}
                        >
                          Reading
                        </Link>
                      )}
                      {chapter.hasExercises && (
                        <Link
                          href={`/course/${course.slug}/${chapter.slug}/exercises`}
                          className={`
                            block px-3 py-1.5 rounded text-sm transition-colors
                            ${isSubItemActive(chapter, 'exercises')
                              ? 'bg-blue-100 text-blue-700'
                              : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700'
                            }
                          `}
                          onClick={() => setIsOpen(false)}
                        >
                          Exercises
                        </Link>
                      )}
                      {chapter.hasSolutions && (
                        <Link
                          href={`/course/${course.slug}/${chapter.slug}/solutions`}
                          className={`
                            block px-3 py-1.5 rounded text-sm transition-colors
                            ${isSubItemActive(chapter, 'solutions')
                              ? 'bg-blue-100 text-blue-700'
                              : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700'
                            }
                          `}
                          onClick={() => setIsOpen(false)}
                        >
                          Solutions
                        </Link>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </nav>
        </div>
      </aside>
    </>
  );
}
