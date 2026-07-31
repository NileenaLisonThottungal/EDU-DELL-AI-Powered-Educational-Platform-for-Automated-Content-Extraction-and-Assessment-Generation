export default function QuestionCard({ index, question, answered, children }) {
  return (
    <div
      className="border-b pb-5 mb-5 last:border-b-0 last:mb-0 last:pb-0"
      style={{ borderColor: "var(--border)" }}
    >
      <h3 className="mb-3 font-semibold">
        {index}. {question}
        {answered && <span className="ml-2 text-xs font-normal text-brand-500">✓ answered</span>}
      </h3>
      {children}
    </div>
  );
}
