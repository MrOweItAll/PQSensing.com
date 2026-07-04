# REVIEW_FLAGS — Items Requiring Founder Judgment

Nothing below was changed in code. Each needs Jon's explicit decision.

## 1. Contact email is a personal Gmail (site-wide)
`mroweitall@gmail.com` appears in every Collaborate/Funding CTA, footers, and drafting contact block. Recommend a domain address (e.g. `contact@pqsensing.com`) for credibility with OEMs and SBIR/STTR reviewers — **but only after the mailbox/forwarding exists in cPanel**. Once routing works, this is a safe find-and-replace across all six pages (≈12 occurrences incl. `mailto:` subjects).

## 2. Personal phone number published on metrology201.html
The footer there exposes `620-518-3686` (also on the drafting page, where phone-first contact is intentional). Decide whether the PQS-branded page should carry a personal cell.

## 3. metrology201.html disclosure-reduction candidates (IP freeze — flag only)
The page currently discloses, at a level of detail beyond the rest of the site:
- the explicit ISL objective `V_ISL(θ) = N_band(θ) / I(θ)^k` and the slope-null lock condition;
- candidate information functionals (fringe contrast, atom number × contrast², classical/quantum Fisher information, signal-response gain);
- the three-loop architecture (primary lock / ISL outer loop with dither-gradient extraction / safety supervisor with contrast, atom-number, and deviation bounds, confidence-weighted freezing);
- a per-application table naming ISL control variables (chirp rate, Raman phase/detuning, pulse timing, ensemble preparation parameters);
- the claim "provably not equivalent to contrast maximization" with the asymmetric-noise reasoning.

If ISL/atom-interferometry embodiments are **not yet filed**, consider trimming the page to the level of `modules.html` ("what it achieves, where it runs — not how"). **No deletion was made.** Patent counsel should review before any public change *or continued publication*.

## 4. metrology.html bench-concept wording (awareness only)
The interactive MZI section says the layout "reflects the current benchtop NSL test concept and working optical drawing," including OPO/squeezed-vacuum injection and control-hardware roles. This looks consistent with the already-public validation plan, but confirm it matches what counsel has cleared.

## 5. Audio transcript (accessibility gap)
`metrology-overview.m4a` (index + metrology pages) has no text alternative. A transcript is required for WCAG conformance, but the narration text must come from you — I did not fabricate one. If you supply/approve a transcript, it can be added as a collapsible section or linked page.

## 6. 23 MB WAV on about.html
`a-real-charmer-ai-gentle-remaster.wav` — anyone pressing play downloads 23 MB. Converting to AAC/MP3 (~2 MB) is lossy re-encoding of a music release, so it's your call. `preload="metadata"` already prevents auto-download.

## 7. Optional image recompression
Several lightbox full-size JPGs are 300–560 KB. They load only on click, so gains are modest; recompression risks visible artifacts on drawing linework. Recommend leaving unless page-weight becomes a concern.

## 8. Custom 404 requires a hosting rule
`404.html` is ready, but Namecheap/Apache serves it only with `ErrorDocument 404 /404.html` in `.htaccess`. I did **not** add an `.htaccess` to the site root, since the live server may already have one that the repo doesn't track (overwriting it via FTP could break existing hosting behavior). A suggested snippet is in `deploy/htaccess.suggested` — merge it by hand in cPanel's file manager after checking the live file.

## 9. `.ftpquota` committed in the repo
A host-generated artifact; harmless but could be removed from version control and gitignored. Left untouched.

## 10. Wording I was tempted to change but did not
- "Liquid Instruments Mako class" in the two instrument-figure captions (index + modules): the vendor's product line is **Moku** (the body copy says Moku correctly). "Mako" may be intentional wordplay or a typo — vendor-name accuracy matters to OEM readers, so please confirm; it's a 2-character fix ×4 if unintended.
- metrology201 footer says "PQSENSING.COM" in caps while other footers use "PQSensing" — left alone as a stylistic choice.
- metrology.html footer says "Kansas, USA" where newer footers say "Hugoton, Kansas" — left alone to avoid touching a page that already had legal identity.
