interface SuggestedQuestionsProps {
  questions: string[];
  onSelect: (question: string) => void;
}

export default function SuggestedQuestions({
  questions,
  onSelect,
}: SuggestedQuestionsProps) {
  if (questions.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 px-4 pb-2">
      {questions.map((q, i) => (
        <button
          key={i}
          onClick={() => onSelect(q)}
          className="text-xs bg-pink-50 text-pink-700 hover:bg-pink-100 px-3 py-1.5 rounded-full border border-pink-200 transition-colors text-right"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
