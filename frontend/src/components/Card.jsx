export default function Card({ children, className = "" }) {
  return (
    <div
      className={`rounded-2xl border shadow-xl ${className}`}
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      {children}
    </div>
  );
}
