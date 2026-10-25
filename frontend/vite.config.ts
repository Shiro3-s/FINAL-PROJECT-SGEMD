import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

/**
 * Desarrollo: Vite en :5173 con proxy `/api` al backend en :3000, de modo que el
 * navegador ve un solo origen (la cookie `SameSite=Strict` funciona igual que en Caddy).
 */
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
