import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
    proxy: {
      // Forward /api requests to the FastAPI backend in development
      '/api': 'http://localhost:8000',
    },
  },
})
