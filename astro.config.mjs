// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // Absolute base for canonical links, Open Graph URLs, and the XML sitemap.
  site: 'https://www.pqsensing.com',

  // Fully static output — pure HTML/CSS/JS that drops straight onto the
  // Namecheap web root (no Node server required at runtime).
  output: 'static',

  // 'file' format preserves the existing URL scheme exactly:
  //   src/pages/metrology.astro  ->  /metrology.html   (not /metrology/)
  // so every current inbound link and nav href keeps working after deploy.
  build: {
    format: 'file',
  },

  integrations: [
    sitemap({
      changefreq: 'weekly',
      priority: 0.8,
    }),
  ],

  vite: {
    build: {
      cssMinify: true,
      sourcemap: false,
    },
  },
});
