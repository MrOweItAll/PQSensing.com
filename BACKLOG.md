# PQSensing.com — Prioritized Improvement Backlog

Ordering: (a) credibility impact for lab partners, instrument OEMs, and SBIR/STTR reviewers; (b) implementation risk, lowest first. Items marked ⚑ require founder approval and live in `REVIEW_FLAGS.md`.

## P0 — Defects (fix first)

1. **metrology201.html smart-quote attributes** — 26 curly-quote attribute delimiters break class/style application on the ISL sections. Pure markup repair; zero content change. *(Risk: none)*
2. **metrology201.html dead anchor** — `index.html#contact` → point to `index.html#collaborate`. *(Risk: none)*

## P1 — Credibility & discoverability infrastructure

3. **Canonical + Open Graph + Twitter Card tags on all six pages** — link previews in email/Slack/LinkedIn are how reviewers first see the site. *(Risk: low, head-only)*
4. **JSON-LD Organization + WebSite schema on index** — Peterson Quantum Sensing LLC, Hugoton, Kansas. *(Risk: low)*
5. **sitemap.xml + robots.txt** — standard crawl infrastructure. *(Risk: none)*
6. **Favicon (SVG + ICO fallback + apple-touch-icon)** — a 404ing favicon and blank tab icon read as unfinished. Derive mark from the existing `.brand-mark` gradient. *(Risk: low)*
7. **Consistent legal footer** — add "Peterson Quantum Sensing LLC · Hugoton, Kansas · © 2026" to index/modules/about (metrology pages already carry it); add © line to drafting footer for Media+Architecture. *(Risk: low, no claim changes)*
8. **404.html** — branded, links home. *(Risk: none)*

## P2 — Accessibility & robustness

9. **`<noscript>` fallback for the interactive demo** — one sentence explaining the demo needs JS; placeholders otherwise look broken. *(Risk: none)*
10. **Heading fix** — `metrology.html` lone `<h4>` → `<h3>`. *(Risk: none)*
11. **`loading="lazy"` + explicit `width`/`height` on below-fold images** — avoids layout shift and wasted bytes. Keep hero eager. *(Risk: low)*
12. ⚑ **Audio transcript for metrology-overview.m4a** — required for accessibility, but the transcript text must come from/be approved by the founder (cannot invent technical narration). Structure can be added once text exists.

## P3 — Polish (do if session allows)

13. **Stacked metrics-table cells lose column labels on mobile** — inject per-cell labels via CSS `::before` or small markup change. *(Risk: medium — shared CSS)*
14. **`.ftpquota` host artifact in repo** — harmless; could be removed/gitignored. *(Risk: none, cosmetic)*
15. ⚑ **Compress/convert 23 MB WAV** (about.html music card) to AAC/MP3 — ~90% smaller; artistic asset, founder call.
16. ⚑ **Optional JPG recompression** of >300 KB lightbox images — modest gain, quality risk on portfolio drawings; founder call.
17. ⚑ **Domain email** — replace personal Gmail with e.g. contact@pqsensing.com once mailbox/routing exists; touches every CTA.

## Deliberately not doing

- **CSS/JS minification** — repo is the deployment source; savings ≈ few KB vs. real maintainability cost.
- **Any technical content changes** on metrology201.html or elsewhere (IP disclosure freeze).
- **Any change to dates, filing references, ≥6 dB target, $10K figure, or validation wording.**
- **News/Updates page** — cannot be populated without new disclosure decisions; revisit with founder.
