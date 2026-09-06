# Review Flags — founder judgment required

These items were identified but **intentionally not changed** this session. Each
needs Jon's decision. Nothing here was auto-edited.

## 1. Contact email is a personal Gmail address

`mroweitall@gmail.com` appears as the public contact address in:

- `src/data/site.json` (`contactEmail`)
- the contact page mailto fallback (`src/pages/contact.astro`)
- the Organization JSON-LD in `src/layouts/BaseLayout.astro` (`email`)

**Recommendation:** move to a domain address (e.g. `contact@pqsensing.com`) for
credibility with lab partners, OEMs, and SBIR/STTR reviewers. **Not changed** —
mail routing for the domain address must exist first, or inbound mail breaks.
Confirm the mailbox, then update those three locations together.

## 2. Audio overview has no text transcript

The spoken overviews (`/assets/metrology-overview.m4a`, and the About-page audio)
have in-element fallback text and a download link, but no full text transcript.

**Recommendation:** add a transcript for accessibility. **Not auto-authored** —
transcribing the audio would (a) require content I cannot verify by ear against
the founder's intent and (b) risk restating technical material under the IP
freeze. Provide an approved transcript and it can be added behind a
`<details>` disclosure next to each player.

## 3. metrology201.html technical content (IP-sensitive)

Per the hard constraints, `metrology201.astro` is treated as known-sensitive
(enabling disclosure of unfiled concepts) and was **not expanded, reduced, or
edited**. No reduction candidates were removed. If a disclosure review is
desired, that is a deliberate, separate, founder-approved pass — flagging here
only so it isn't forgotten.

## 4. Live Formspree endpoint committed in `site.json`

`formspreeEndpoint` is set to a real-looking value (`https://formspree.io/f/xqerbarl`).
Confirm this is the intended production form and that it routes to the desired
inbox. (Informational — not a defect; noted because it's a live integration.)

## 5. Merging this PR to `main` auto-deploys to Namecheap

`.github/workflows/deploy.yml` ("Build & Deploy to Namecheap") runs on **push to
`main`** and builds + FTP-uploads `dist/` to the live web root (when the
`FTP_SERVER` / `FTP_USERNAME` / `FTP_PASSWORD` secrets are set). It does **not**
run on this PR or feature branch — nothing was deployed by this session.

**Implication:** merging PR #4 = a live deployment. This is the founder's call,
not the agent's. Complete local review (`npm run dev` / `npm run build` +
`npm run preview`) before merging. Note: there are no PR-triggered CI checks, so
a "green" status won't appear on the PR itself — the build/test/deploy runs only
after merge to `main`.

## 6. Wording not changed

No claim figures, dates, or filing references (e.g. the ≥6 dB target, the
validation-sprint figure, patent 19/535,045) were altered. None were edited even
where phrasing could be tightened — any such change is deferred to founder review
per the no-substantive-claim-changes constraint.
