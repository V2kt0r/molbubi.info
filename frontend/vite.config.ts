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
    port: 3080,
    proxy: {
      // Proxy API calls to avoid CORS issues when connecting to external APIs
      '/api/v1': {
        target: process.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8080',
        changeOrigin: true,
        secure: true,
        configure: (proxy, options) => {
          console.log('🔄 Vite Proxy configured - Target:', options.target);
        },
      },
    },
  },
  preview: {
    host: true,
    port: 3000,
    allowedHosts: ['dev.molbubi.info', 'molbubi.info'],
  },
})
