import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/api/v1/stations': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/api/v1/bikes': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/api/v1/distribution': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
  preview: {
    host: true,
    port: 3000,
    proxy: {
      '/api/v1/stations': {
        target: 'http://api:8000',
        changeOrigin: true,
      },
      '/api/v1/bikes': {
        target: 'http://api:8000',
        changeOrigin: true,
      },
      '/api/v1/distribution': {
        target: 'http://api:8000',
        changeOrigin: true,
      },
      '/api/v1/health': {
        target: 'http://api:8000',
        changeOrigin: true,
      },
    },
  },
  define: {
    // Make env variables available at build time
    __API_BASE_URL__: JSON.stringify(process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080/api/v1'),
    __ENVIRONMENT__: JSON.stringify(process.env.REACT_APP_ENVIRONMENT || 'development'),
  },
})
