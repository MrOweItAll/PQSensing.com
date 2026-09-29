# Reconciliation and site-validation report — 29 September 2026

**Production baseline is not accepted. Whole-site release remains blocked.**

This work reproduced the repository at
`44d5cf4d9934ca86f1ef650056cf5164e1888917`. No site source, pricing, scientific
copy, contact endpoint, package dependency, lockfile, or public asset was edited.
This is an infrastructure-only preservation reference, not permission to publish
that historical website over the current one.

## Evidence and known differences

A read-only public-web sample on 29 September 2026 confirmed material divergence:

| Surface | Repository build | Public sample | Resolution |
|---|---|---|---|
| Home `/` | Existing Astro homepage and earlier research presentation | New measurement-quality homepage and narrated interferometer film | Reconcile newer source and all associated assets from authenticated snapshot. |
| `/modules.html` | Existing supervisory modules page | New technology/application presentation and evidence boundaries | Review copy, navigation, metadata and assets. |
| `/evidence.html` | No generated route or corresponding source | Public electrical-test evidence page linked from home | Preserve and reconcile this route before any full release. |
| `/architecture.html` | 17 projects / 99 image records | Public page reports the same counts and service packages | Matching counts alone do not establish file hashes or behavioral parity. |

Sample URLs: <https://www.pqsensing.com/>,
<https://www.pqsensing.com/modules.html>,
<https://www.pqsensing.com/evidence.html>,
<https://www.pqsensing.com/architecture.html>.
The public-web retrieval of the last two research pages included cached crawls;
these are discovery signals, not timestamped host snapshots or a complete public
inventory. No full live file hashes, hidden files, server configuration, form
backend, redirects, permissions, or host-managed paths were available. No public
crawl can certify that unseen content is absent. The earlier architecture-only
patch likewise does not establish current whole-site parity.

## Repository inventory

`tests/site/repository-baseline.json` records 285 source/public/configuration and
lockfile SHA-256 values and explicitly marks live acceptance false. Generated
HTML routes are:

| Route | Purpose |
|---|---|
| `/index.html` (also local `/`) | Homepage |
| `/about.html` | Founder/company |
| `/architecture.html` | Media + Architecture |
| `/contact.html` | Contact form |
| `/drafting/index.html` | Compatibility page redirecting to architecture |
| `/metrology.html` | Metrology introduction |
| `/metrology201.html` | Advanced learning |
| `/modules.html` | Research modules |
| `/publications.html` | Papers/downloads |
| `/updates.html` | Updates |

Additional generated files include `/updates/rss.xml`, sitemap files and
`robots.txt`. Gallery counts come from the current repository data, not from a
hard-coded historical requirement. The contact page has its existing Formspree
action and mailto fallback, with name, email, inquiry type, package, message,
subject, and honeypot fields. The URL controls architecture/package prefills.
No form message was sent.

## Executed checks

| Check | Result | Qualification |
|---|---|---|
| Existing `npm test` | PASS: 14 tests in 1 file | Vitest 4.1.10 on Node 24.19.0. |
| Existing `npm run build` | PASS | Astro static build emitted 9 generated pages; public drafting page brings HTML total to 10. |
| Existing internal-link gate | PASS: 256 internal references / 10 HTML files | Filesystem existence, not external URL availability. |
| Source/public preservation | PASS: 285 protected files unchanged | Source-only manifest; live acceptance remains false. |
| Preservation negative tests | PASS: 5 tests | Modified copy, missing asset, and added file each fail; unmodified content and unrelated infrastructure pass. |
| New local HTTP/download checks | PASS: 23 assertions | Route inventory, document/metadata routes, a missing-route 404, and byte-identical local PDF/PPTX downloads. |
| Browser/viewport/gallery/contact execution | BLOCKED | Playwright 1.62.1 package exists, but no Chromium executable is installed. |
| Browser install | FAILED | Chromium download returned invalid/truncated ZIP payloads; no bypass or substitute rendering was used. |
| Live/source reconciliation, host behavior, visual approval | NOT DONE | Requires fresh authenticated private hosting snapshot and accepted differences. |

`scripts/test-site.mjs` fails closed when the real browser is unavailable. It
writes a JSON report containing partial checks and the blocking reason; it never
labels the viewport checks as passed in that condition. CI installs the pinned
browser separately from site dependencies and must execute the complete gate.
The script includes six required widths, menus, JavaScript/console checks,
canonical-origin metadata, gallery filters/full images, download integrity,
contact destination/prefill/validation checks, and network write prevention.
External font/service requests are stubbed in local browser checks, so external
availability remains separate. No screenshot reference set was created because
no browser ran.

## Hosted follow-up

GitHub subsequently installed Chromium successfully and ran the full browser gate.
Run [36551496861](https://github.com/MrOweItAll/PQSensing.com/actions/runs/36551496861)
recorded **307 passes and 23 responsive-width failures** in the unchanged source.
The 23 failures comprise tablet navigation overflow on the ten documents at 768
and 1024 px, plus the metrology201 comparison table at 320, 375 and 390 px. Gallery,
contact validation/prefill and console checks passed; no contact message was sent.
The local missing-Chromium result above remains accurate for this workspace but
is no longer the only browser evidence. See
[hosted-browser-results.md](automation/hosted-browser-results.md) for exact cases.
CI remains failed; candidate packaging was skipped after the browser gate.
No accepted visual baseline or authenticated preview has been established.

## Remaining baseline acceptance work

1. Freeze every active legacy publisher through the authorized administration
   interface and record pending runs before any main-branch change.
2. Capture the authenticated hosting tree including hidden files, active routing,
   ownership, permissions, forms and host-managed paths into private storage.
   Verify an encrypted off-host recovery copy and document restoration.
3. Classify every path and compare build routes, copy, assets, metadata, navigation,
   gallery, contact behavior and downloads with that snapshot. Bring the newer
   public content into editable source without silently replacing approved copy.
4. Run the full browser gate and inspect screenshots at all required widths;
   test server redirects, authentication, query strings and 404 behavior on the
   real protected staging host. Record all intentional differences for Jon.
5. Accept a complete baseline only after review, replace the source-only inventory
   with the accepted inventory/reference set, and recheck live hashes immediately
   before cutover so intervening edits cannot be overwritten.

A green source build does not resolve any of these missing baseline controls.
