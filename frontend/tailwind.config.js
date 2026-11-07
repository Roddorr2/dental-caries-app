/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"IBM Plex Sans"', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      colors: {
        // Epic/Athena clinical palette: Slate foundation with restrained clinical semantic accents
        clinical: {
          canvas: '#f8fafc', // slate-50
          surface: '#ffffff',
          border: '#e2e8f0', // slate-200
          borderSubtle: '#cbd5e1', // slate-300
          textPrimary: '#0f172a', // slate-900
          textSecondary: '#475569', // slate-600
          textMuted: '#64748b', // slate-500
          
          // Semantic clinical status only
          valid: {
            bg: '#f0fdf4',
            border: '#86efac',
            text: '#166534',
            dot: '#16a34a',
          },
          review: {
            bg: '#fffbeb',
            border: '#fde68a',
            text: '#92400e',
            dot: '#d97706',
          },
          alert: {
            bg: '#fff1f2',
            border: '#fecdd3',
            text: '#9f1239',
            dot: '#e11d48',
          },
        }
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.07), 0 1px 2px -1px rgba(0, 0, 0, 0.05)',
      },
      borderRadius: {
        'DEFAULT': '0.375rem',
        'sm': '0.25rem',
        'md': '0.375rem',
        'lg': '0.5rem',
      }
    },
  },
  plugins: [],
}
