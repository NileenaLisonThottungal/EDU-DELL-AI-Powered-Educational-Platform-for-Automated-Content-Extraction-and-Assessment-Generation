/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eefaf9",
          100: "#d3f1ee",
          200: "#a8e3dd",
          300: "#72cfc5",
          400: "#43b3a8",
          500: "#2b6777", // primary accent, matches the reference UI's teal
          600: "#235462",
          700: "#1d4450",
          800: "#193740",
          900: "#152d34",
        },
        surface: {
          light: "#ffffff",
          dark: "#111827",
        },
      },
    },
  },
  plugins: [],
};
