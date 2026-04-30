'use client';

import { useState } from 'react';
import MarkdownRenderer from './MarkdownRenderer';

interface CollapsibleSectionProps {
  heading: string;
  content: string;
  defaultOpen?: boolean;
}

export default function CollapsibleSection({ heading, content, defaultOpen = false }: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-5 py-3.5 text-left bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <h3 className="text-lg font-semibold text-gray-900">{heading}</h3>
        <svg
          className={`w-5 h-5 text-gray-500 shrink-0 ml-4 transform transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {isOpen && (
        <div className="px-5 py-4">
          <MarkdownRenderer content={content} />
        </div>
      )}
    </div>
  );
}
