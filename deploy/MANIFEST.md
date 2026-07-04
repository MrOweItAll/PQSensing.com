# Deployment Manifest — changes relative to live site (repo `main`)

Generated 2026-07-04 from `git diff --name-status main`. Upload = these 13 files only. No files need deleting on the host.

## Modified (7)
| File | Change |
|---|---|
| `index.html` | head metadata, JSON-LD, noscript, footer legal line, metrics-table labels, img lazy/dims |
| `modules.html` | head metadata, footer legal line, img lazy/dims |
| `metrology.html` | head metadata, h4→h3, img lazy/dims |
| `metrology201.html` | smart-quote markup fix, anchor fix, table scroll wrappers, head metadata |
| `about.html` | head metadata, footer legal line, img lazy/dims |
| `drafting/index.html` | completed OG tags, favicon links, footer © line, img lazy/dims |
| `styles.css` | +2 rules: `.footer-legal`, mobile metrics-table labels |

## New (6)
| File | Purpose |
|---|---|
| `404.html` | branded not-found page (needs ErrorDocument rule — see `htaccess.suggested`) |
| `favicon.ico` | 32px tab icon |
| `favicon.svg` | scalable tab icon |
| `apple-touch-icon.png` | 180px iOS/bookmark icon |
| `robots.txt` | crawl policy + sitemap pointer |
| `sitemap.xml` | six canonical URLs |

Not uploaded: `AUDIT.md`, `BACKLOG.md`, `CHANGELOG.md`, `REVIEW.md`, `REVIEW_FLAGS.md`, `CLAUDE.md`, `deploy/` (repo/working documents, not site content).
