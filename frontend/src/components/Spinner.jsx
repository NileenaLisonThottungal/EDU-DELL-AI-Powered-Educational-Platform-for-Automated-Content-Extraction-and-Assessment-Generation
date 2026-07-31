export default function Spinner({ label = "Loading..." }) {
  return (
    <div className="flex items-center justify-center gap-3 py-6 text-sm" style={{ color: "var(--text-muted)" }}>
      <span
        className="h-4 w-4 animate-spin rounded-full border-2 border-brand-400 border-t-transparent"
        role="status"
        aria-label={label}
      />
      {label}
    </div>
  );
}
