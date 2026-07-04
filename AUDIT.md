# PQSensing.com — Site Audit (Phase 0)

Date: 2026-07-04 · Branch: `claude/pqsensing-site-improvements-2q6kwp` · Audited against repo `main` (live-site mirror).

Page inventory: `index.html`, `modules.html`, `metrology.html`, `metrology201.html`, `about.html`, `drafting/index.html`, plus `assets/` (SVG, JPG, audio, white papers), pitch deck PDF/PPTX, résumé PDF.

## 1. HTML validity

| Finding | Severity | Location |
|---|---|---|
| **Curly "smart quotes" used as attribute delimiters** (`class=”section-title”`, 26 occurrences). Browsers do not treat `”` as a quote character, so those class/style attributes fail to apply — several ISL sections render unstyled. | **High** | `metrology201.html` (source lines 23–29 region) |
| Broken in-page anchor: link to `index.html#contact` — `index.html` has no `id="contact"` (nearest equivalents: `#collaborate`, `#fund`). | Medium | `metrology201.html` ("Navigate" callout) |
| Heading-level skip: single `<h4>` under `<h2>` sections (no `<h3>` ancestor). | Low | `metrology.html:463` |
| All pages have `<!doctype html>`, `lang="en"`, UTF-8 charset, viewport meta. | OK | all |
| One `<h1>` per page on all six pages. | OK | all |

## 2. Links

- **Internal file links:** all `href`/`src` targets resolve (checked every page). No broken file links.
- **Internal anchors:** one broken (`index.html#contact`, above). All others resolve.
- **External links:** Google Fonts (2 hosts + CSS), 4× loc.gov, 3× nist.gov, 1× science.nasa.gov. All use `target="_blank" rel="noopener"` where new-tab. (Not fetched from this environment; spot-check during founder review.)
- Pitch deck PDF/PPTX and résumé PDF links resolve to committed files.

## 3. SEO / metadata

| Item | Status |
|---|---|
| Page titles | Present and descriptive on all pages |
| Meta descriptions | Present on all pages |
| Canonical URLs | **Missing on all pages** |
| Open Graph tags | Missing everywhere except partial set on `drafting/` (no `og:url`, `og:image`) |
| Twitter Card tags | **Missing on all pages** |
| `sitemap.xml` | **Missing** |
| `robots.txt` | **Missing** |
| Favicon / apple-touch-icon | **Missing** (browsers request `/favicon.ico` → 404) |
| JSON-LD Organization/WebSite schema | **Missing** |
| 404 page | **Missing** (Namecheap default will show) |

## 4. Accessibility

- **Audio transcript:** none for `assets/metrology-overview.m4a` (used on `index.html` and `metrology.html`). Needs a founder-supplied or founder-approved transcript — content cannot be invented. → REVIEW_FLAGS.
- **Alt text:** present on all meaningful images, and generally high quality. The empty-`src`/empty-`alt` hits in scans are the lightbox `<img>` shells (populated by JS) — acceptable.
- **Demo controls:** sliders are wrapped in `<label>` elements with visible text + hints — good. `<output>` elements mirror values. Keyboard-operable natively.
- **No `<noscript>` fallback** anywhere; with JS disabled the demo panel shows "V<sub>norm</sub> there = —" placeholders with no explanation.
- **Heading hierarchy:** good except the `metrology.html` h4 skip noted above.
- **Contrast:** footer text `--muted2 (#7aa4bc)` on `#030b14` ≈ 7.4:1 — passes AA. Demo hint text (11.5px muted) is small but passes. No blockers found.
- `aria-label`s present on nav, demo panel, lightbox controls, metrics table (`role="table"`).

## 5. Performance

- **`assets/audio/a-real-charmer-ai-gentle-remaster.wav` is 23 MB** (about.html music card). `preload="metadata"` avoids auto-download, but any play costs 23 MB. Converting WAV→AAC/MP3 would cut ~90% — requires founder approval (artistic asset). → REVIEW_FLAGS.
- `PQSensing_MZI_NSL_Pitch_Deck.pptx` is 8.9 MB — download-only link, acceptable.
- Raster images: hero-class JPGs 136–250 KB at 1672×941 — reasonable. Portfolio/HABS full-size JPGs (up to 556 KB) load only on lightbox click; thumbs are small. **No recompression performed** (quality risk on portfolio drawings outweighs gain); flagged as optional.
- **`loading="lazy"` and `width`/`height` attributes missing on all `<img>`** — below-fold images should lazy-load; missing dimensions cause layout shift.
- CSS/JS unminified: `styles.css` ~13 KB, `app.js` ~10 KB. Minification savings ≈ a few KB and would make the repo (which is the deployment source) harder to maintain. Deliberately **not** minified; noted as a conscious decision.
- Google Fonts CSS is render-blocking on every page (standard pattern, `preconnect` already present). Left as-is.
- `index.html` preloads `assets/hero.jpg` — good.

## 6. Mobile responsiveness

- Viewport meta on all pages; shared nav collapses to a Menu toggle ≤740px; `metrology201.html` nav scrolls horizontally ≤980px on its own header variant — usable.
- **Prototype Metrics table** (`index.html`): at ≤980px each row stacks to one column and the header row is hidden — no horizontal overflow. Acceptable, though the stacked cells lose their column labels (candidate polish, low priority).
- Tap targets (buttons, nav links ≥44px effective) look adequate.
- No horizontal-overflow sources found (`overflow-x:hidden` on body as backstop).

## 7. Interactive demo (`app.js`) health

- `update()` **is called on load** — the "—" placeholders in the HTML are replaced immediately when JS runs. Placeholders persist only when JS is disabled/fails → the `<noscript>` gap above is the real issue.
- Divide-by-zero guarded: `P(δ)` clamped to `EPS = 0.01` before `pow(p,k)`; gain readout guards non-finite values. k-extremes safe.
- No console errors found by inspection; DOM lookups null-guarded at entry (`if (!plotEl) return`).
- Resize handled with debounce.

## 8. Consistency & trust signals

- **Footers are inconsistent:**
  - `index.html`, `modules.html`: brand blurb only — **no legal entity, no location, no copyright**.
  - `about.html`: adds contact line, no copyright.
  - `metrology.html`: `© 2026 Peterson Quantum Sensing LLC · Kansas, USA` + email.
  - `metrology201.html`: full legal footer with phone + AI-assistance disclosure.
  - `drafting/`: Media+Architecture footer (separate brand, reasonable) — no copyright line.
- Brand naming: "PQSensing" (nav/brand) vs "Peterson Quantum Sensing" (titles of metrology pages) — coexistence is fine, but the legal name should appear in every footer.
- Nav is identical across the five PQS pages (drafting has its own — intentional).
- **Contact email is a personal Gmail** (`mroweitall@gmail.com`) in all CTAs and footers → REVIEW_FLAGS (do not change without mail routing).
- `metrology201.html` footer exposes a personal phone number — founder may want that; flagged for awareness.
- `.ftpquota` file committed to repo (host artifact, harmless but noise).

## 9. IP-sensitivity observations (no action taken)

- `metrology201.html` contains enabling-level discussion of ISL (objective formula, three-loop architecture, control variables per application). Per the disclosure freeze, **nothing was added, expanded, or removed**. Reduction candidates listed in `REVIEW_FLAGS.md` only.
- `metrology.html` describes the NSL/DPI concept at a level already public on `index.html`; the "current benchtop test concept" diagram wording is noted in REVIEW_FLAGS for founder awareness.
