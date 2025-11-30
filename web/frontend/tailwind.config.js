/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // DevBrain Futuristic Color Palette
        cyber: {
          50: '#e6f0ff',
          100: '#b3d9ff',
          200: '#80c2ff',
          300: '#4dabff',
          400: '#1a94ff',
          500: '#0080ff', // Primary cyber blue
          600: '#0066cc',
          700: '#004d99',
          800: '#003366',
          900: '#001a33',
          950: '#000d1a',
        },
        neon: {
          purple: '#a855f7',
          pink: '#ec4899',
          cyan: '#06b6d4',
          green: '#10b981',
          yellow: '#f59e0b',
          red: '#ef4444',
        },
        dark: {
          50: '#1a1a1a',
          100: '#141414',
          200: '#0f0f0f',
          300: '#0a0a0a',
          400: '#050505',
          500: '#000000',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-cyber': 'linear-gradient(135deg, #0080ff 0%, #a855f7 100%)',
        'gradient-neon': 'linear-gradient(90deg, #06b6d4 0%, #a855f7 50%, #ec4899 100%)',
        'gradient-dark': 'linear-gradient(180deg, #0a0a0a 0%, #000000 100%)',
      },
      boxShadow: {
        'neon-sm': '0 0 10px rgba(0, 128, 255, 0.3)',
        'neon-md': '0 0 20px rgba(0, 128, 255, 0.4)',
        'neon-lg': '0 0 30px rgba(0, 128, 255, 0.5)',
        'neon-xl': '0 0 40px rgba(0, 128, 255, 0.6)',
        'purple-glow': '0 0 20px rgba(168, 85, 247, 0.4)',
        'pink-glow': '0 0 20px rgba(236, 72, 153, 0.4)',
        'cyber-glow': '0 0 25px rgba(0, 128, 255, 0.5), 0 0 50px rgba(168, 85, 247, 0.3)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'fade-in': 'fadeIn 0.3s ease-in',
        'scan': 'scan 2s linear infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(0, 128, 255, 0.2), 0 0 10px rgba(0, 128, 255, 0.2)' },
          '100%': { boxShadow: '0 0 10px rgba(0, 128, 255, 0.6), 0 0 20px rgba(0, 128, 255, 0.4)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
