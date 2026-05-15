PQSensing — redesigned website package (v2)
============================================

Upload the entire pqsensing/ folder contents to your hosting root
(Cloudflare Pages, Namecheap public_html, etc.).

Files
-----
index.html                          One-page redesigned site (11 numbered sections)
styles.css                          Editorial-technical stylesheet
app.js                              Interactive demonstration logic
assets/hero.jpg                     Hero background
assets/dark_port.jpg                DPI section image
assets/mzi_bench.jpg                Sprint section image
assets/market_platforms.jpg         (kept available — currently unused; reusable for future sections)
assets/metrology-overview.m4a       Embedded audio overview
PQSensing_MZI_NSL_Pitch_Deck.pdf    Linked deck (PDF)
PQSensing_MZI_NSL_Pitch_Deck.pptx   Linked deck (editable PPTX)

What changed from v1
--------------------
1. New centerpiece: an interactive SVG demonstration in §02 where the
   visitor manipulates noise parameters and watches the V_norm slope-null
   diverge from the power extremum. Live readouts show δ_PDH, δ_NSL,
   and the dB advantage in the current regime. The page's central thesis
   is now visible, not just stated.

2. DPI subordinated. v1 framed DPI as a parallel offering alongside NSL.
   v2 frames DPI as the channel through which NSL reaches the quantum
   domain. The licensing wedge is clearer.

3. Explicit kill criteria added to §08. Three concrete falsification
   conditions. Sophisticated readers (SBIR reviewers, technical due-
   diligence, partner physicists) read this as scientific maturity.

4. Funding ladder added (§09). Four rungs: $10K sprint → $50–80K
   extended bench → ~$275K SBIR Phase I → $1–2M Phase II. Each rung
   is a defined deliverable. The previous version stopped at the $10K
   ask, which left readers asking "and then what?"

5. Founder section added (§10). Closes the credibility gap. References
   the planned advisor relationship with Dr. Rongqing Hui.

6. Typography upgrade. Fraunces (variable serif display) + IBM Plex Sans
   (body) + IBM Plex Mono (equations and technical labels). Replaces
   Inter, which the frontend-design conventions explicitly flag as a
   generic AI default.

7. Palette refined to deep navy ink with a single warm-cream "exhibit"
   surface that breaks the dark flow at the centerpiece moment, plus
   brass amber accents for emphasis and a muted rose for the kill-criteria
   block.

Pre-launch checklist
--------------------
- Replace contact@pqsensing.com if a different email should be used.
- Confirm Dr. Rongqing Hui mention is appropriate before publish; soften
  the "planned" language if not yet confirmed in writing.
- Replace rendered concept images with real bench photos once available.
- Review all technical claims with patent counsel before licensing
  conversations.

Browser support
---------------
Tested in Chromium-based browsers at 1440px desktop and 414px mobile.
Uses standard CSS Grid, IntersectionObserver, and SVG — all of which
are supported in every browser shipped in the past five years.
