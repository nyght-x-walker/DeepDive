import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://example.github.io',
  base: '/',
  integrations: [react()],
  output: 'static',
  server: { host: true },
  vite: { server: { host: true } }
});
