# pqsensing.com

Source for the Peterson Quantum Sensing public website.

PQSensing develops **Noise-Stationary Locking (NSL)** and **Phase-Controlled Dark-Mode Injection (DPI)**: a PDH-compatible measurement-performance layer for interferometric sensors. PDH locks the resonance; NSL locks measurement quality; DPI activates the dark port.

> Locked at the optical condition is not the same as locked at the measurement-optimal condition.

## Site map

| Page | Path | Purpose |
| --- | --- | --- |
| Home | `index.html` | Business-facing landing page with the collaboration ask, three-layer triad, interactive V<sub>norm</sub> slope-null demonstration, validation plan, prototype metrics, and $10K sprint. |
| Metrology 101 | `metrology.html` | Interactive primer on laser interferometric metrology. Mach–Zehnder with squeezed-vacuum injection, lock comparison, fiber-optic gyro, Thorlabs bench layout. Component hotspot tooltips and live mode-toggle visualizations. |
| Metrology 201 | `metrology201.html` | Extension to atomic interferometry and Information-Stationary Locking (ISL). |

## File layout

```
/
├── index.html                       # home page
├── metrology.html                   # interactive Metrology 101
├── metrology201.html                # Metrology 201 — ISL for atom interferometry
├── styles.css                       # shared stylesheet for index.html (metrology pages use scoped inline styles)
├── app.js                           # V_norm slope-null interactive demo (index.html exhibit)
├── mzi-thorlabs-layout.svg          # tabletop MZI bench layout (referenced from metrology.html)
├── technical_one_pager.md           # plain-text positioning copy (reuse in outreach)
├── README.md                        # this file (developer-facing)
├── README_UPLOAD.txt                # deploy guide for non-developer uploads
├── PQSensing_MZI_NSL_Pitch_Deck.pdf # validation-sprint pitch deck (linked from the site)
└── assets/
    ├── hero.jpg                     # hero background
    ├── dark_port.jpg                # DPI section illustration
    ├── mzi_bench.jpg                # validation section illustration
    ├── market_platforms.jpg         # market section background
    └── metrology-overview.m4a       # spoken metrology overview audio
```

## Deployment

The site is currently deployed via Namecheap shared hosting under `pqsensing.com`. There is no build step — the files are vanilla HTML / CSS / JS with no dependencies that need bundling.

To deploy, upload the contents of the repository root to your `public_html/` directory via SFTP (port **21098** on Namecheap), or via cPanel's Git Version Control feature pointed at this repository.

For local development, any static-file server works:

```bash
python3 -m http.server 8000
# then open http://localhost:8000/
```

## Editing conventions

- **Plain-text technical claims** live in `technical_one_pager.md`. Reuse this copy for emails and outreach so the language stays consistent across channels.
- **Email & phone** appear in multiple places. To change them, update every page footer and CTA — see `mailto:` and `tel:` links across all three HTML files.
- **The interactive V<sub>norm</sub> exhibit** in `index.html` uses a pedagogical analytic model (`app.js`), not bench data. Replace the curves in `app.js` once the validation sprint produces measured `P(δ)`, `N_band(δ)`, and `V_norm(δ)`.
- **Be sober.** Public-facing language emphasizes hypothesis and validation plan rather than claimed performance. Review technical claims with patent counsel before licensing discussions.

## Pre-launch checklist

- [ ] Email mroweitall@gmail.com — confirm this is the canonical contact (vs mroweitall@live.com)
- [ ] Phone 620-518-3686 — confirm this is the right number to publish
- [ ] Replace rendered concept images (hero.jpg, dark_port.jpg, mzi_bench.jpg) with real bench photos once the prototype is running
- [ ] Funding ask: $10K minimum data sprint plus 20–30 minute feasibility call. Update if it changes
- [ ] Pitch deck: refresh PQSensing_MZI_NSL_Pitch_Deck.pdf as the validation story evolves
- [ ] Patent counsel review of all technical claims before licensing conversations

## License & credits

Source code in this repository (HTML / CSS / JS) is provided for transparency about the site's structure. The PQSensing positioning, technical concepts (NSL, DPI, ISL), and intellectual property are the property of Peterson Quantum Sensing LLC, Hugoton, Kansas.

Website, patent drafting, research, and grant-writing support developed with AI tools at the direction of Peterson Quantum Sensing LLC. Original intellectual-property direction and publication decisions remain with Jon Peterson and Peterson Quantum Sensing LLC.

© 2026 Peterson Quantum Sensing LLC
