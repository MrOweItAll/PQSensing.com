# Changelog — site-improvements session (2026-08-02)

Branch: `claude/pqsensing-site-improvements-fs2onu` (based on latest `main`).
All changes are presentation/robustness only. No technical disclosure, claim
figures, dates, or filing references were added or altered (IP freeze respected).

## Site-wide / housekeeping

- **Add branded 404 page.** New `src/pages/404.astro` (builds to `/404.html`)
  using `BaseLayout`, marked `noindex, follow`, with suggested-page nav and a
  home button. *Why:* mistyped or stale URLs previously fell through to the
  host's default error page; a branded 404 keeps users oriented and preserves
  trust for lab/OEM/reviewer audiences.
- **Add `public/.htaccess`.** Single directive `ErrorDocument 404 /404.html`.
  *Why:* the static build emits `/404.html`, but Apache on Namecheap won't serve
  it as the error page without this. `.htaccess` is copied verbatim into `dist/`.

## Interactive demos (homepage exhibits)

- **`<noscript>` fallback for the NSL exhibit** (`src/components/NSLDemo.astro`).
  *Why:* the plot and readouts populate only after the JS island runs; with JS
  disabled the panel showed empty `—` values. The fallback states the takeaway
  in plain language (no new technical detail).
- **`<noscript>` fallback for the dark-port injection exhibit**
  (`src/components/DPIDemo.astro`). Same rationale.
- **`.exhibit-noscript` style** (`src/styles/global.css`) — shared styling so the
  fallback reads cleanly and spans the full panel width in the no-JS grid.

## Verification (this session)

- `npm test` → 12/12 pass.
- `npm run build` → succeeds; 11 pages; `check-links` reports 278 internal links
  OK, 0 broken.
- Confirmed: `/404.html` and `/.htaccess` present in `dist/`; both demo
  `<noscript>` blocks present in built `index.html`; `/404.html` carries
  `noindex` and is excluded from the sitemap.
