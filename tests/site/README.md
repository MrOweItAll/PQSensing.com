# Site regression evidence

`repository-baseline.json` is a source/public inventory at repository commit
`44d5cf4d9934ca86f1ef650056cf5164e1888917`. It is **not an accepted live baseline**.
There are 285 protected files, 10 built HTML routes, 17 portfolio projects, and
99 portfolio images. The public website already contains newer pages absent from
this checkout; see `docs/reconciliation.md`.

Run from the repository root:

```sh
npm ci
npm test
npm run build
python3 scripts/check-preservation.py --root .
python3 -m unittest discover -s tests/site -p 'test_*.py'
PLAYWRIGHT_MODULE_PATH=/absolute/path/to/playwright/index.mjs node scripts/test-site.mjs --dist dist --report verification/browser.json
```

The browser script starts a read-only loopback server and requires pinned
Playwright plus an installed Chromium binary. It performs 60 route/viewport
checks (10 documents at 320, 375, 390, 768, 1024, 1440 pixels), tests mobile menu
navigation, metadata, browser errors, downloads, gallery filters and all 99
images, and contact field/prefill/validation behavior. Contact is never submitted;
all non-GET/HEAD network requests are blocked and fail the test. External browser
requests are stubbed, so external font/service availability is not certified.
Local HTTP checks are not evidence of production Apache redirects, authentication,
certificate paths, canonical-domain redirects, or custom 404 behavior.

`verification/browser.json` is written on success, failures, and missing-browser
errors. A browser unavailable in the runtime is a failing exit, never a pass.
Screenshots are produced for home, architecture, and contact at 375 and 1440 pixels
when browser execution is available. A full site screenshot review remains part
of approving a reconciled baseline. Do not commit machine-specific verification
outputs or screenshots as a substitute for approved baseline references.

The preservation manifest catches accidental content changes in this infrastructure
change. Later requested content changes require a deliberate reviewed manifest
update and must preserve the accepted live inventory. Never regenerate it merely
to make CI green. Do not set production acceptance from this source-only manifest.
