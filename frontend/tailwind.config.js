/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#e94560',
        secondary: '#1a1a2e',
        accent: '#0f3460',
        dark: '#16213e',
      },
    },
  },
  plugins: [],
}
