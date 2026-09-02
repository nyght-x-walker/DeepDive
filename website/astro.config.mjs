import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://nyght-x-walker.github.io',
  base: '/DeepDive/',
  integrations: [react()],
  output: 'static',
  server: { host: true },
  vite: { server: { host: true } }
});
