# REVIEW.md — Local Review Instructions

## Serve the site locally

From the repo root:

```
python -m http.server 8000
```

Then open <http://localhost:8000/> in a browser. (Any static server works; root-absolute favicon/404 links assume the repo root is the web root, exactly as on the live host.)

## Review checklist

### Every page (index, modules.html, metrology.html, metrology201.html, about.html, drafting/)
- [ ] Page renders identically to the live site apart from the changes listed in `CHANGELOG.md`.
- [ ] Favicon appears in the browser tab.
- [ ] Footer shows the legal line (entity · Hugoton, Kansas · © 2026).
- [ ] View source: canonical / og: / twitter: tags present in `<head>` and the description text matches the page.

### index.html specifically
- [ ] Interactive demo populates immediately on load (readouts show numbers, not "—"); drag all three sliders, including k slider to both extremes — no NaN/Infinity readouts.
- [ ] Narrow the window below ~980px: Prototype Metrics table stacks and each cell shows its TARGET / EVIDENCE OUTPUT label.
- [ ] Disable JavaScript (DevTools → Settings → Debugger → Disable JavaScript), reload: a sentence explains the demo needs JS.

### metrology201.html specifically (biggest visual change)
- [ ] The ISL sections ("Information-Stationary Locking — the generalization", "The three-loop architecture", "Why ISL changes the strategic picture") now render with full styling: large section headings, purple-tinted callout boxes, mono-font formula blocks, three numbered cards. Before the fix these were plain unstyled text.
- [ ] On a phone (or narrow window): both comparison tables scroll horizontally inside their box instead of being cut off.
- [ ] "contact Peterson Quantum Sensing" link in the Navigate box lands on the Collaborate section of the homepage.
- [ ] **Confirm no technical content changed** — only markup/quoting. `git diff main -- metrology201.html` shows the exact edits.

### about.html / drafting/
- [ ] Lightbox galleries still open, navigate (arrows/Escape), and download correctly (lazy-loading touched every `<img>` tag).
- [ ] Founder portrait still appears (it uses an onload swap — verify it wasn't affected).

### 404 page
- [ ] Open <http://localhost:8000/404.html> directly — renders branded page. (On the live host it only triggers automatically after the `.htaccess` rule in `deploy/htaccess.suggested` is merged — see REVIEW_FLAGS #8.)

### New files
- [ ] `sitemap.xml`, `robots.txt` — check URLs.
- [ ] `favicon.svg` / `apple-touch-icon.png` — icon style acceptable.

## After review

1. Work through `REVIEW_FLAGS.md` decisions.
2. Follow `deploy/README.md` to stage the FTP upload. **Nothing has been deployed; the FTP script is prepared but must not be run until you approve.**
