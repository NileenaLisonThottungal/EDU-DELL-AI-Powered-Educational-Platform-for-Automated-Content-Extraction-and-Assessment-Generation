export default function ProgressBar({ current, total }) {
  const percentage = total ? Math.round((current / total) * 100) : 0;

  return (
    <div>
      <div className="mb-1 flex justify-between text-xs" style={{ color: "var(--text-muted)" }}>
        <span>Answered {current}/{total}</span>
        <span>{percentage}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full" style={{ background: "var(--surface-muted)" }}>
        <div
          className="h-full rounded-full bg-brand-500 transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
