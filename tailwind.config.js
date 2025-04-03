/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/src/**/*.js"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#121212',
        surface: '#1E1E1E',
        primary: '#BB86FC',
        error: '#CF6679',
        'text-primary': '#FFFFFF',
        'text-secondary': '#B3B3B3',
        'graph-temp': '#FF4B4B',
        'graph-humidity': '#4B9EFF'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      fontSize: {
        'card-title': '1.25rem',
        'main-value': '2.5rem',
        'label': '0.875rem'
      },
      borderRadius: {
        'card': '12px'
      },
      spacing: {
        'card-padding': '1.5rem'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms')
  ]
} 