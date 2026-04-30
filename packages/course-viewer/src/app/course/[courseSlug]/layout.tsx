import { getCourseInfo, getCourses } from '@/lib/courses';
import Sidebar from '@/components/Sidebar';
import { notFound } from 'next/navigation';

export async function generateStaticParams() {
  const courses = getCourses();
  return courses.map((slug) => ({ courseSlug: slug }));
}

export default async function CourseLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ courseSlug: string }>;
}) {
  const { courseSlug } = await params;
  const course = getCourseInfo(courseSlug);

  if (!course) {
    notFound();
  }

  return (
    <div className="min-h-screen">
      <Sidebar course={course} />
      <main className="lg:ml-72 min-h-screen">
        <div className="max-w-4xl mx-auto px-4 py-8 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  );
}
