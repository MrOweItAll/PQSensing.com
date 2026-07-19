# PQSensing.com — Astro migration

This branch (`astro-migration`) restructures the site from hand-maintained,
duplicated HTML files into an [Astro](https://astro.build) static site while
**preserving every page's exact appearance and URL**. Nothing on the live site
changes until you deploy this branch.

## What changed

**Structure**
- Shared `Header` and `Footer` are now single components (`src/components/`).
  Editing the nav once updates every page. A new **Publications** link was added
  to the nav.
- `src/layouts/BaseLayout.astro` — the shell for `index`, `modules`, `about`,
  `publications`. Adds SEO: canonical URLs, Open Graph + Twitter cards, and
  JSON-LD (`Organization` / `TechArticle`) structured data.
- The two metrology pages keep their bespoke inline designs (moved to
  page-scoped stylesheets) and are served through `RawLayout.astro`, so they
  look identical but now share the site header and SEO head.
- Original page HTML/CSS/JS was ported faithfully; the old root files
  (`index.html`, `about.html`, `styles.css`, `app.js`, etc.) are removed in
  favor of `src/`.

**Interactive demos**
- The NSL exhibit (`src/components/NSLDemo.astro`) keeps its live SVG curves and
  gains: a **"Copy shareable link"** button that encodes the slider regime in the
  URL hash, and a **CSV bench-trace loader** — drop a measured `delta, P, N_band`
  file and the same UI re-plots your data and marks both lock points.
- New **DPI demo** (`src/components/DPIDemo.astro`): injects a known phase code,
  buries it in noise, and recovers it with a matched filter — making the
  dark-port processing-gain claim tangible.

**Rigor / SEO**
- Equations are typeset at build time with **KaTeX** (`MathEquation.astro`) — no
  runtime math JS shipped.
- **Publications index** (`/publications.html`) is driven by
  `src/data/publications.json`; each paper gets a PDF link and a copy-paste
  BibTeX citation. Add a paper by appending one JSON entry.
- **Vitest** suite (`src/lib/nsl-model.test.js`) locks the demo's math
  invariants so future edits can't silently break the pedagogical claims.
- `sitemap-index.xml` and `robots.txt` are generated/added automatically.

## Local commands

```bash
npm install     # once
npm run dev      # local preview at http://localhost:4321
npm test         # run the Vitest math suite
npm run build    # produce the deployable site in dist/
npm run preview  # serve the built dist/ locally
```

## ⚠️ The one deploy change you must make

Previously, Namecheap served the **repository root** as your web root. After this
migration the servable site is the **built `dist/` folder**, not the repo root.
So whatever currently publishes the repo to `public_html` must be pointed at the
build output instead. Two options:

1. **GitHub Actions (included).** `.github/workflows/deploy.yml` builds the site
   and uploads `dist/` to Namecheap over FTP on every push to `main`. Add the
   `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD` repo secrets and confirm
   `server-dir` matches your web root. If you use cPanel's "Git Version Control"
   auto-deploy today, disable it (or repoint it) so it doesn't publish the repo
   root over the built output.

2. **Manual / local.** Run `npm run build` and upload the contents of `dist/` to
   `public_html` yourself (FTP, cPanel File Manager, or `.cpanel.yml`).

Until you make this change, **do not merge `astro-migration` into `main`** if
your host auto-publishes the repo root — it would serve the un-built source.
Deploy the built `dist/` instead.
