import { Link } from "react-router";
import { useTheme } from "../context/ThemeContext.jsx";

export default function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="flex items-center justify-between px-6 py-4 text-white">
      <Link to="/" className="flex items-center gap-2 text-lg font-semibold tracking-wide">
        <span aria-hidden="true">📘</span> EDU-DELL
      </Link>

      <nav className="flex items-center gap-4 text-sm">
        <Link to="/" className="opacity-90 hover:opacity-100">
          Upload
        </Link>
        <Link to="/history" className="opacity-90 hover:opacity-100">
          History
        </Link>
        <button
          type="button"
          onClick={toggleTheme}
          aria-label="Toggle light/dark theme"
          className="rounded-full bg-white/15 px-3 py-1 hover:bg-white/25"
        >
          {theme === "light" ? "🌙 Dark" : "☀️ Light"}
        </button>
      </nav>
    </header>
  );
}
