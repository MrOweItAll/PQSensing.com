# PQSensing — Launch checklist

Everything below is a one-time setup to take the `astro-migration` branch live.
There are two pieces of information to gather (a Formspree endpoint and your FTP
login), then it's push → merge → done. Estimated time: ~20 minutes.

Prerequisite: Node.js installed on your PC (check with `node -v`; if missing, get
the LTS from nodejs.org).

---

## Part A — Formspree endpoint (activates the contact form)

This is what makes `/contact` actually email you. It's free and takes 3 minutes.

1. Go to **https://formspree.io** and click **Sign up** (use `mroweitall@gmail.com`).
2. Verify the sign-up email Formspree sends you.
3. In the dashboard: **+ New Form** → name it `PQSensing site` → set the
   "Send emails to" address to `mroweitall@gmail.com` → **Create Form**.
4. On the form's page, copy its **endpoint URL**. It looks like:
   `https://formspree.io/f/abcdwxyz` (an 8-character code after `/f/`).
5. Give that URL to me and I'll drop it into `src/data/site.json` and re-bundle —
   or edit it yourself: open `src/data/site.json`, replace
   `"https://formspree.io/f/YOUR_FORM_ID"` with your URL, save.
6. After the site is live, submit the form once. Formspree emails you a one-time
   **"Confirm your email"** link for the first submission — click it, and all
   future submissions flow straight to your inbox.

Notes: the free plan allows 50 submissions/month. Until you set this, the form
still works — it falls back to opening a pre-filled email. So this step is
"nice to have before launch," not a blocker.

---

## Part B — Your FTP login (so GitHub can deploy to Namecheap)

You already have these three values, because Codex uses them to FTP the site
today. The fastest path is to **reuse the exact same host / username / password**.
If you don't have them written down, here's where to find them in Namecheap:

1. Sign in at **namecheap.com** → top-right **Account** → **Dashboard**.
2. Left menu → **Hosting List** → find your hosting plan → **Manage**.
3. Click **Go to cPanel** (may ask you to log in again).
4. In cPanel, under the **Files** section, click **FTP Accounts**.
5. Scroll to **"Special FTP Accounts"** (or your existing account) and click
   **Configure FTP Client** next to it. That panel shows exactly:
   - **FTP Server** → this is your `FTP_SERVER` (e.g. `ftp.pqsensing.com` or a
     host like `serverNNN.web-hosting.com`).
   - **FTP Username** → this is your `FTP_USERNAME` (often `user@pqsensing.com`
     or your cPanel username).
   - Port is 21 (already handled by the workflow).
6. **Password** = the password for that FTP account. If you don't remember it,
   use **Change Password** on that account — but if you do, update Codex with
   the new one too so it doesn't fail elsewhere.
7. **Confirm your web-root folder:** in cPanel → **File Manager**, find where the
   current `index.html` lives. For a primary domain it's usually `public_html`.
   Remember that folder name — you'll confirm it in Part D.

---

## Part C — Add the three secrets to GitHub

1. Go to **https://github.com/MrOweItAll/PQSensing.com** → **Settings** (top tab).
2. Left sidebar → **Secrets and variables** → **Actions**.
3. Click **New repository secret** and add each of these (Name, then Secret value
   from Part B), one at a time:
   - `FTP_SERVER`
   - `FTP_USERNAME`
   - `FTP_PASSWORD`
4. They'll be masked and stored securely; GitHub never shows them again.

---

## Part D — Confirm the deploy target

1. Open `.github/workflows/deploy.yml` on the branch.
2. Find `server-dir: public_html/` and make sure it matches the folder from
   Part B step 7. If your site lives in a subfolder (add-on domain), change it
   (e.g. `server-dir: public_html/pqsensing.com/`).

---

## Part E — Stop the old Codex raw-FTP for this site

After migration, the *repo root* is source code and the *built `dist/`* is the
site. The GitHub Action publishes `dist/`. So **turn off / don't run** the Codex
job that FTPs the repo root to `public_html` for this project — otherwise it
would overwrite the built site with un-built source.

---

## Part F — Push, merge, deploy

From your local clone (`…\PQS PKB WEB\website\pqsensing.com`):

```bash
git checkout astro-migration
npm install
npm run dev        # final local review at http://localhost:4321
git push -u origin astro-migration
```

Then on GitHub:

1. Open a **Pull Request**: `astro-migration` → `main`.
2. **Merge** it. The merge to `main` triggers the deploy workflow automatically.
3. Watch it under the repo's **Actions** tab — it runs `npm ci → npm test →
   npm run build → FTP dist/ to public_html`. Green check = live.

---

## Part G — Post-launch smoke test (2 minutes)

Load **https://www.pqsensing.com** and hard-refresh (Ctrl+F5), then check:

- [ ] Homepage hero, "Patent pending", and the live NSL demo render
- [ ] `/architecture` — packages show ranges, portfolio filters work
- [ ] `/contact` — submit a test message; confirm the Formspree email arrives
- [ ] `/updates` and `/updates/rss.xml` load
- [ ] "Read the lab one-pager (PDF)" opens the PDF
- [ ] (fun) Konami code on the homepage: ↑ ↑ ↓ ↓ ← → ← → B A

That's it. If the Action fails, open the failed step in the Actions tab — it's
almost always a wrong `server-dir` or a mistyped FTP secret.
