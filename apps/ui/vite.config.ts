import { defineConfig } from 'vite'
import theSveltePlugin from '@sveltejs/vite-plugin-svelte'
// Workaround for import issue with default export in some environments
const svelte = theSveltePlugin.svelte || theSveltePlugin

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
