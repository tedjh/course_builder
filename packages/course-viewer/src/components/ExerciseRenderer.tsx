'use client';

import { useState, useMemo } from 'react';
import MarkdownRenderer from './MarkdownRenderer';

interface ExerciseRendererProps {
  content: string;
}

interface Exercise {
  id: string;
  header: string;
  content: string;
  solution: string | null;
}

export default function ExerciseRenderer({ content }: ExerciseRendererProps) {
  const [showAllSolutions, setShowAllSolutions] = useState(false);
  const [visibleSolutions, setVisibleSolutions] = useState<Set<string>>(new Set());

  // Parse exercises and solutions from the content
  const { introContent, exercises, hasAnySolutions } = useMemo(() => {
    const lines = content.split('\n');
    const exercises: Exercise[] = [];
    let currentExercise: Exercise | null = null;
    let inSolutionSection = false;
    let solutionStartIndex = -1;

    // Find where the solutions section starts
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].match(/^##\s*(Solutions|Solutions to)/i)) {
        solutionStartIndex = i;
        break;
      }
    }

    // Extract intro content (everything before first exercise)
    let introEndIndex = 0;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].match(/^###\s*Exercise\s+\d+/i)) {
        introEndIndex = i;
        break;
      }
    }
    const introContent = lines.slice(0, introEndIndex).join('\n').trim();

    // Parse exercises
    let exerciseContent: string[] = [];
    let exerciseId = '';
    let exerciseHeader = '';

    for (let i = introEndIndex; i < lines.length; i++) {
      const line = lines[i];

      // Check for solution section start
      if (line.match(/^##\s*(Solutions|Solutions to)/i)) {
        // Save current exercise if any
        if (currentExercise) {
          currentExercise.content = exerciseContent.join('\n').trim();
          exercises.push(currentExercise);
        }
        inSolutionSection = true;
        currentExercise = null;
        exerciseContent = [];
        continue;
      }

      // Check for exercise header (in exercises section)
      const exerciseMatch = line.match(/^###\s*(Exercise\s+(\d+).*)/i);
      if (exerciseMatch && !inSolutionSection) {
        // Save previous exercise
        if (currentExercise) {
          currentExercise.content = exerciseContent.join('\n').trim();
          exercises.push(currentExercise);
        }

        exerciseId = `exercise-${exerciseMatch[2]}`;
        exerciseHeader = exerciseMatch[1];
        currentExercise = {
          id: exerciseId,
          header: exerciseHeader,
          content: '',
          solution: null,
        };
        exerciseContent = [];
        continue;
      }

      // Check for solution header (in solutions section)
      const solutionMatch = line.match(/^###\s*(Solution to Exercise\s+(\d+)|Solution\s+(\d+))/i);
      if (solutionMatch && inSolutionSection) {
        const solutionNum = solutionMatch[2] || solutionMatch[3];
        const exercise = exercises.find(e => e.id === `exercise-${solutionNum}`);

        if (exercise) {
          // Collect solution content until next solution header
          let solutionContent: string[] = [];
          i++;
          while (i < lines.length) {
            if (lines[i].match(/^###\s*(Solution|Exercise)/i)) {
              i--;
              break;
            }
            solutionContent.push(lines[i]);
            i++;
          }
          exercise.solution = solutionContent.join('\n').trim();
        }
        continue;
      }

      // Add to current exercise content
      if (currentExercise && !inSolutionSection) {
        exerciseContent.push(line);
      }
    }

    // Save last exercise if in exercises section
    if (currentExercise && !inSolutionSection) {
      currentExercise.content = exerciseContent.join('\n').trim();
      exercises.push(currentExercise);
    }

    const hasAnySolutions = exercises.some(e => e.solution !== null);

    return { introContent, exercises, hasAnySolutions };
  }, [content]);

  const toggleSolution = (id: string) => {
    setVisibleSolutions(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const toggleAllSolutions = () => {
    if (showAllSolutions) {
      setVisibleSolutions(new Set());
    } else {
      setVisibleSolutions(new Set(exercises.filter(e => e.solution).map(e => e.id)));
    }
    setShowAllSolutions(!showAllSolutions);
  };

  const isSolutionVisible = (id: string) => visibleSolutions.has(id);

  // If no exercises were parsed, just render the content as-is
  if (exercises.length === 0) {
    return <MarkdownRenderer content={content} />;
  }

  return (
    <div>
      {/* Intro content */}
      {introContent && (
        <div className="mb-8">
          <MarkdownRenderer content={introContent} />
        </div>
      )}

      {/* Show all toggle */}
      {hasAnySolutions && (
        <div className="flex justify-end mb-6">
          <button
            onClick={toggleAllSolutions}
            className="flex items-center text-sm px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <svg
              className={`w-4 h-4 mr-2 transition-transform ${showAllSolutions ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            {showAllSolutions ? 'Hide all solutions' : 'Show all solutions'}
          </button>
        </div>
      )}

      {/* Exercises */}
      <div className="space-y-8">
        {exercises.map((exercise) => (
          <div
            key={exercise.id}
            id={exercise.id}
            className="border border-gray-200 rounded-lg overflow-hidden"
          >
            {/* Exercise header */}
            <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {exercise.header}
              </h3>
            </div>

            {/* Exercise content */}
            <div className="p-6">
              <MarkdownRenderer content={exercise.content} />
            </div>

            {/* Solution toggle and content */}
            {exercise.solution && (
              <div className="border-t border-gray-200">
                <button
                  onClick={() => toggleSolution(exercise.id)}
                  className="w-full px-6 py-3 flex items-center justify-between text-left bg-blue-50 hover:bg-blue-100 transition-colors"
                >
                  <span className="font-medium text-blue-700">
                    {isSolutionVisible(exercise.id) ? 'Hide Solution' : 'Show Solution'}
                  </span>
                  <svg
                    className={`w-5 h-5 text-blue-600 transform transition-transform ${
                      isSolutionVisible(exercise.id) ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {isSolutionVisible(exercise.id) && (
                  <div className="p-6 bg-blue-50 border-t border-blue-100">
                    <MarkdownRenderer content={exercise.solution} />
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
