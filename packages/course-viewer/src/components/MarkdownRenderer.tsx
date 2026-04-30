'use client';

import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
import { Components } from 'react-markdown';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

const components: Components = {
  // Custom heading rendering with anchor links
  h1: ({ children, ...props }) => (
    <h1 className="text-3xl font-bold mt-8 mb-4 pb-2 border-b border-gray-200" {...props}>
      {children}
    </h1>
  ),
  h2: ({ children, ...props }) => (
    <h2 className="text-2xl font-semibold mt-8 mb-3" {...props}>
      {children}
    </h2>
  ),
  h3: ({ children, ...props }) => (
    <h3 className="text-xl font-semibold mt-6 mb-2" {...props}>
      {children}
    </h3>
  ),
  h4: ({ children, ...props }) => (
    <h4 className="text-lg font-semibold mt-4 mb-2" {...props}>
      {children}
    </h4>
  ),

  // Custom table styling
  table: ({ children, ...props }) => (
    <div className="overflow-x-auto my-6">
      <table className="min-w-full border-collapse" {...props}>
        {children}
      </table>
    </div>
  ),

  // Custom blockquote styling
  blockquote: ({ children, ...props }) => (
    <blockquote
      className="border-l-4 border-blue-500 pl-4 py-2 my-4 bg-blue-50 italic"
      {...props}
    >
      {children}
    </blockquote>
  ),

  // Custom link styling
  a: ({ children, href, ...props }) => (
    <a
      href={href}
      className="text-blue-600 hover:text-blue-800 underline"
      target={href?.startsWith('http') ? '_blank' : undefined}
      rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
      {...props}
    >
      {children}
    </a>
  ),

  // Custom list styling
  ul: ({ children, ...props }) => (
    <ul className="list-disc list-outside ml-6 my-4 space-y-1" {...props}>
      {children}
    </ul>
  ),
  ol: ({ children, ...props }) => (
    <ol className="list-decimal list-outside ml-6 my-4 space-y-1" {...props}>
      {children}
    </ol>
  ),

  // Custom code block styling
  pre: ({ children, ...props }) => (
    <pre
      className="bg-gray-900 text-gray-100 rounded-lg p-4 my-4 overflow-x-auto text-sm"
      {...props}
    >
      {children}
    </pre>
  ),

  // Inline code styling
  code: ({ children, className, ...props }) => {
    // Check if this is a code block (has language class) or inline code
    const isCodeBlock = className?.includes('language-');

    if (isCodeBlock) {
      return (
        <code className={className} {...props}>
          {children}
        </code>
      );
    }

    return (
      <code
        className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono"
        {...props}
      >
        {children}
      </code>
    );
  },

  // Horizontal rule styling
  hr: () => <hr className="my-8 border-t border-gray-300" />,

  // Paragraph styling
  p: ({ children, ...props }) => (
    <p className="my-4 leading-7" {...props}>
      {children}
    </p>
  ),
};

export default function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div className={`prose prose-slate max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkMath, remarkGfm]}
        rehypePlugins={[rehypeKatex, rehypeHighlight]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
