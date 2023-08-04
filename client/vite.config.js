import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    strictPort: true,
    proxy: {
      '/api': 'http://127.0.0.1:5001'
    }
  },
  plugins: [svelte()],
})
