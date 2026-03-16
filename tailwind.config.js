/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#f0f4ff',
          500: '#4f6ef7',
          600: '#3b55e6',
          700: '#2d42cc',
        }
      }
    },
  },
  plugins: [],
}
