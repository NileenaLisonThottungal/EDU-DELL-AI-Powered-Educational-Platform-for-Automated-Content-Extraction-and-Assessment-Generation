export default function OptionButton({ label, selected, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`mb-2 block w-full rounded-lg border px-4 py-2 text-left text-sm transition-colors ${
        selected ? "border-brand-500 bg-brand-50 dark:bg-brand-900/40" : "hover:border-brand-300"
      }`}
      style={{
        borderColor: selected ? undefined : "var(--border)",
        background: selected ? undefined : "var(--surface-muted)",
      }}
    >
      {label}
    </button>
  );
}
