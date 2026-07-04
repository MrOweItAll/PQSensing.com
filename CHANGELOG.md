# CHANGELOG — Site Improvement Session 2026-07-04

Branch: `claude/pqsensing-site-improvements-2q6kwp`. Nothing deployed; all changes staged for founder review (see `REVIEW.md`).

## metrology201.html
- **Fixed broken markup:** 26 attributes used typographic curly quotes (`class=”…”`) which browsers don't parse, so the entire ISL block (headings, callouts, formulas, three-loop cards) rendered unstyled. Replaced with straight quotes; prose punctuation untouched. *Rationale: rendering defect on the page most likely to be read by technical reviewers.*
- **Fixed dead link:** "contact Peterson Quantum Sensing" pointed to `index.html#contact`, which doesn't exist → now `index.html#collaborate`. *Rationale: broken CTA.*
- **Mobile tables:** both comparison tables were clipped at phone widths (body hides overflow). Wrapped in horizontal-scroll containers. *Rationale: content was unreadable on phones; no content change.*
- No technical/IP content was added, expanded, or removed on this page.

## All six pages (index, modules, metrology, metrology201, about, drafting/)
- Added canonical URL tag.
- Added Open Graph and Twitter Card metadata, reusing each page's existing title and meta description verbatim (drafting page kept its existing partial OG set; only missing tags added). *Rationale: link previews are the first impression when the site is shared with partners/reviewers.*
- Added favicon links (`favicon.ico`, `favicon.svg`, `apple-touch-icon.png`) — new icon files generated from the existing brand-mark gradient. *Rationale: missing favicon 404s and blank tab icons read as unfinished.*

## index.html
- Added JSON-LD `Organization` (Peterson Quantum Sensing LLC, Hugoton KS, founder Jon Peterson) + `WebSite` schema.
- Added `<noscript>` sentence inside the demo panel explaining the demo requires JavaScript (the "—" placeholders otherwise look broken).
- Footer: added legal line "© 2026 Peterson Quantum Sensing LLC · Hugoton, Kansas · email".
- Prototype Metrics table: restored "Target"/"Evidence output" labels on stacked mobile rows via `data-label` + CSS (header row is hidden at phone widths). No cell text changed.

## modules.html
- Footer legal line (same as index).

## about.html
- Footer legal line (© + location; contact line already present).

## metrology.html
- Promoted the lone `<h4>` ("Noise lock — dark-port residual SNR vs drive amplitude") to `<h3>` to fix a heading-level skip. No text change.

## drafting/index.html
- Footer: added "© 2026 Media+Architecture · Jon Peterson · Hugoton, Kansas".
- Completed OG tags (`og:url`, `og:image`, `og:site_name`).

## Images (all pages)
- `loading="lazy"` on below-fold local images; explicit `width`/`height` on all local images (prevents layout shift). Above-fold images (founder portrait with its onload swap, drafting hero logo) kept eager.

## New files
- `sitemap.xml` — six canonical URLs.
- `robots.txt` — allow all, sitemap pointer.
- `404.html` — branded not-found page (noindex, root-absolute links). Note: Namecheap needs an `ErrorDocument` rule to serve it — see `deploy/htaccess.suggested` and `REVIEW.md`.
- `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`.
- `styles.css` — two additions only: `.footer-legal` styles and the mobile metrics-table label rule.

## Verification performed
- All six pages + 404 rendered in headless Chromium (desktop 1280px and mobile 375px): zero console errors (excluding sandbox-blocked Google Fonts), zero horizontal overflow, demo readouts populate on load (e.g. "+5.65 dB"), ISL sections now styled.
- JSON-LD validated as JSON; head tags machine-checked on every page; all internal links/anchors re-verified.

## Deliberately NOT changed (see REVIEW_FLAGS.md)
- Contact email (personal Gmail), phone number in metrology201 footer.
- All dates, the ≥6 dB target, the $10K sprint figure, validation wording.
- metrology201.html technical content (IP disclosure freeze).
- CSS/JS minification, WAV/JPG recompression, audio transcript (needs founder input).
