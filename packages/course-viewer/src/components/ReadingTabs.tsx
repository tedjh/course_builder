'use client';

import { useState, useMemo } from 'react';
import MarkdownRenderer from './MarkdownRenderer';
import CollapsibleSection from './CollapsibleSection';
import type { ReadingSection } from '@/lib/courses';

interface Subsection {
  heading: string;
  content: string;
}

interface ParsedContent {
  intro: string;
  subsections: Subsection[];
}

function parseSubsections(markdown: string): ParsedContent {
  const parts = markdown.split(/^(?=### )/m);
  const subsections: Subsection[] = [];
  let intro = '';

  for (const part of parts) {
    const match = part.match(/^### (.+)\n([\s\S]*)$/);
    if (match) {
      subsections.push({
        heading: match[1].trim(),
        content: match[2].trim(),
      });
    } else {
      intro += part;
    }
  }

  return { intro: intro.trim(), subsections };
}

interface ReadingTabsProps {
  sections: ReadingSection[];
}

export default function ReadingTabs({ sections }: ReadingTabsProps) {
  const [activeIndex, setActiveIndex] = useState(0);

  const parsed = useMemo(
    () => sections.map(s => parseSubsections(s.content)),
    [sections],
  );

  if (sections.length === 0) {
    return null;
  }

  const active = parsed[activeIndex];

  return (
    <div>
      {/* Section tabs */}
      <div className="flex gap-1 mb-6 border-b border-gray-200">
        {sections.map((section, i) => (
          <button
            key={i}
            onClick={() => setActiveIndex(i)}
            className={`
              px-4 py-2.5 text-sm font-medium transition-colors relative
              ${activeIndex === i
                ? 'text-blue-700'
                : 'text-gray-500 hover:text-gray-700'
              }
            `}
          >
            {section.heading}
            {activeIndex === i && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />
            )}
          </button>
        ))}
      </div>

      {/* Section content */}
      {active.intro && (
        <div className="mb-6">
          <MarkdownRenderer content={active.intro} />
        </div>
      )}

      {active.subsections.length > 0 ? (
        <div className="space-y-3">
          {active.subsections.map((sub, i) => (
            <CollapsibleSection
              key={`${activeIndex}-${i}`}
              heading={sub.heading}
              content={sub.content}
              defaultOpen={i === 0}
            />
          ))}
        </div>
      ) : (
        <MarkdownRenderer content={sections[activeIndex].content} />
      )}
    </div>
  );
}
