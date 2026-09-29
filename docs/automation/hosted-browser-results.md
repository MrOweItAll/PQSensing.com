# Hosted browser results — 29 September 2026

**CI failed: 307 checks passed; 23 responsive-width checks failed.**

[GitHub run 36551496861](https://github.com/MrOweItAll/PQSensing.com/actions/runs/36551496861)
executed Chromium 151.0.7922.34 with Playwright 1.62.1. Branch head was
`0b38ace6177a7672de8c57f2aa4bdcb3e08b8f20`; GitHub tested the synthetic PR merge
`99746b27f2babef9a6f6ce1fea227e43537662a1` against unchanged main. The report is
[artifact 11024696894](https://github.com/MrOweItAll/PQSensing.com/actions/runs/36551496861/artifacts/11024696894)
(retention expires 2026-10-13). The downloaded artifact ZIP SHA-256 is
`721aa460117cde9e62bc7d5485c663da488cd3de7711eaf571c48a2f63394637`.

The locked install, existing tests/build, source-preservation checks, and all
receiver/preservation unit tests also passed in this hosted run. The artifact
packaging step correctly did not run after browser failure. Local package
verification is separate and is not a successful hosted release candidate.

## Passing browser coverage

- 37 of 60 document/viewport width checks passed.
- 30 mobile menu opens and 30 closes after navigation passed.
- 10 page image checks, 10 console/runtime-error checks and document metadata passed.
- All 17 gallery projects opened, all 99 images loaded, all four filters worked,
  and Escape/focus restoration passed for each project.
- Contact destination, field mapping, architecture/package prefills, email/required
  validation and fallback address passed. Zero contact submissions occurred.
- Route inventory, 14 HTTP routes, local 404 and seven PDF/PPTX byte checks passed.

These are source-build checks, not live Namecheap behavior. External requests
were stubbed. Authentication, real message delivery, redirects and cached-asset
serving on the host remain untested. Screenshots were generated on the runner,
but only the JSON report was retained; no accepted visual baseline is claimed.

## Failing source-layout cases

| Route | Viewport px | Document width px |
|---|---:|---:|
| `/about.html` | 768 | 1268 |
| `/about.html` | 1024 | 1268 |
| `/architecture.html` | 768 | 1268 |
| `/architecture.html` | 1024 | 1268 |
| `/contact.html` | 768 | 1268 |
| `/contact.html` | 1024 | 1268 |
| `/drafting/index.html` | 768 | 1268 |
| `/drafting/index.html` | 1024 | 1268 |
| `/index.html` | 768 | 1268 |
| `/index.html` | 1024 | 1268 |
| `/metrology.html` | 768 | 1424 |
| `/metrology.html` | 1024 | 1424 |
| `/metrology201.html` | 320 | 496 |
| `/metrology201.html` | 375 | 496 |
| `/metrology201.html` | 390 | 496 |
| `/metrology201.html` | 768 | 1424 |
| `/metrology201.html` | 1024 | 1424 |
| `/modules.html` | 768 | 1268 |
| `/modules.html` | 1024 | 1268 |
| `/publications.html` | 768 | 1268 |
| `/publications.html` | 1024 | 1268 |
| `/updates.html` | 768 | 1268 |
| `/updates.html` | 1024 | 1268 |

The common tablet issue is the existing navigation extending beyond the viewport.
`metrology201.html` also has an existing comparison-table overflow on narrow phones.
The public live site has newer source and different navigation, so these failures
belong in the source/live reconciliation work. This draft has not rewritten the
historical theme or changed the preservation baseline to hide failures. CI stays
red and production stays blocked until the accepted source passes these checks.
