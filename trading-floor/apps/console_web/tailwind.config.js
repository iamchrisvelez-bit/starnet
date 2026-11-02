/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#07080d",
        neon: "#3ec6ff",
        acid: "#f5e642",
      },
    },
  },
  plugins: [],
};
