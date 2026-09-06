# Site Audit — PQSensing.com

**Date:** 2026-08-02 · **Branch:** `claude/pqsensing-site-improvements-fs2onu`
**Basis:** Astro static site (`output: 'static'`, `build.format: 'file'`), latest `main`.

> **Context correction.** The improvement task was written against an assumed
> raw static-HTML site missing basic SEO/accessibility/perf infrastructure. The
> actual repository is a mature Astro v2 migration where most of that
> infrastructure already exists. This audit reflects the *real* state, so the
> work done this session is narrow and surgical rather than a rebuild.

## Baseline health (verified)

- `npm test` → **12/12 pass** (vitest; `nsl-model` unit tests).
- `npm run build` → **succeeds**, 11 pages generated.
- `scripts/check-links.mjs` → **278 internal links OK across 11 pages**, 0 broken.

## Already in place (no action needed)

| Area | Status |
|---|---|
| Per-page `<title>` + meta description | ✅ via `BaseLayout` props on every page |
| Canonical URLs | ✅ `BaseLayout` (`<link rel="canonical">`) |
| Open Graph + Twitter Card tags | ✅ `BaseLayout` |
| JSON-LD structured data | ✅ Organization schema site-wide; TechArticle on article pages |
| `sitemap.xml` | ✅ `@astrojs/sitemap` (`sitemap-index.xml` + `sitemap-0.xml`) |
| `robots.txt` | ✅ `public/robots.txt` |
| Favicons | ✅ `favicon.ico`, `favicon.svg`, `apple-touch-icon.png` |
| `lang` + `charset` + viewport | ✅ `BaseLayout` (`<html lang="en">`, UTF-8, responsive viewport) |
| Consistent nav + footer across pages | ✅ shared `Header.astro` / `Footer.astro` |
| Interactive demos self-initialize on load | ✅ `NSLDemo` calls `update()` at load; no lingering "—" when JS runs |
| Audio elements have in-element fallback text + download link | ✅ (see flag re: transcript) |
| Build-time broken-link gate | ✅ `scripts/check-links.mjs` runs in `build` |
| Deploy/launch instructions (Formspree + Namecheap FTP) | ✅ `LAUNCH.md` (do not duplicate) |

## Gaps found and fixed this session

1. **No custom 404 page.** → Added `src/pages/404.astro` (emits `/404.html`,
   `noindex, follow`, full nav) + `public/.htaccess` with
   `ErrorDocument 404 /404.html` so Apache/Namecheap actually serves it. The
   file-format build emits `/404.html`, which Apache ignores without this line.
2. **No `<noscript>` fallback on the interactive demos.** → Added a plain-language
   `<noscript>` sentence to both exhibits (NSL, dark-port injection) plus a shared
   `.exhibit-noscript` style. With JS disabled, users previously saw dangling
   `—` readouts. No new technical detail was introduced.

## Remaining opportunities (deferred — see REVIEW_FLAGS.md)

- **Audio transcript** for the spoken overview: not present. Not auto-authored —
  producing a transcript risks IP disclosure and must be founder-supplied.
- **Contact email is a personal Gmail** across `site.json`, the contact page, and
  the Organization JSON-LD. Left unchanged pending a domain mailbox.
- **Image performance pass**: not all below-fold `<img>` carry `loading="lazy"`
  and explicit `width`/`height`. Low priority; requires per-image judgment about
  which are above the fold. No layout-shift problems were observed in the build.

## Explicitly left alone (IP freeze)

- `metrology201.astro` technical content — untouched, not reduced. Any reduction
  is a founder decision (see REVIEW_FLAGS.md).
- No mathematical detail, algorithm steps, parameters, or claim figures were
  added or altered anywhere.
