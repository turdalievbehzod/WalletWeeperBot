/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        blue: {
          50:  '#EEF2FF',
          100: '#DCE6FF',
          400: '#7B9FF5',
          500: '#5C7EFF',
          600: '#3B5FD9',
        },
        orange: {
          50:  '#FFF5E6',
          100: '#FFE9C7',
          400: '#FFBA5A',
          500: '#FF9F43',
          600: '#E07B20',
        },
        cream: '#FAF5EC',
        yellow: '#FFF5C4',
      },
    },
  },
  plugins: [],
}
