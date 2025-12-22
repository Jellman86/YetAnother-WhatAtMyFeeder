import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [svelte()],
    server: {
        host: true,
        port: 3000,
        proxy: {
            '/api': {
                target: 'http://backend:8000',
                changeOrigin: true,
            }
        }
    }
})
