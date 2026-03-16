/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        pizza: {
          red: "#DC2626",
          orange: "#EA580C",
          yellow: "#F59E0B",
          cream: "#FEF3C7",
          dark: "#1C1917",
        },
      },
    },
  },
  plugins: [],
};
