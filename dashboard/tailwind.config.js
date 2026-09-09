/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          blue: "#1a73e8",
          dark: "#202124",
          gray: "#5f6368",
          green: "#1e8e3e",
          amber: "#e37400",
          red: "#d93025",
        }
      }
    },
  },
  plugins: [],
}
