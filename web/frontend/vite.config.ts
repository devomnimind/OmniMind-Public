import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Code splitting para chunks menores
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'chart-vendor': ['recharts'],
          'omnimind-core': [
            './src/services/api.ts',
            './src/store/daemonStore.ts',
            './src/services/robust-connection.ts'
          ],
          'components-dashboard': [
            './src/components/Dashboard.tsx',
            './src/components/HealthDashboard.tsx',
            './src/components/QuickStatsCards.tsx'
          ],
          'components-metrics': [
            './src/components/ConsciousnessMetrics.tsx',
            './src/components/AutopoieticMetrics.tsx',
            './src/components/AgentStatus.tsx'
          ]
        }
      }
    },
    // Aumentar limite de warning para chunks
    chunkSizeWarningLimit: 250
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/status': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/snapshot': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/plan': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/metrics': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/observability': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/daemon': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
})
