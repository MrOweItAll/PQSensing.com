# deploy/ — Prepared, UNEXECUTED deployment package

> **Do not run until Jon has completed REVIEW.md and given approval.**

Contents:

- `MANIFEST.md` — the exact 13 files that changed relative to the live site (7 modified, 6 new). Nothing is deleted on the host.
- `upload.lftp` — ready-to-run `lftp` script with placeholders for host/username/password. Fill in credentials locally at run time; never commit them.
- `htaccess.suggested` — one-line `ErrorDocument` rule to enable the custom 404 page. Merge into the live `.htaccess` by hand; it is deliberately excluded from the upload script.

Deployment steps (after approval):

1. Review `MANIFEST.md`.
2. Edit `upload.lftp`: replace `FTP_USERNAME`, `FTP_PASSWORD`, `FTP_HOST` (from cPanel), confirm the `public_html` docroot.
3. From the repo root: `lftp -f deploy/upload.lftp`
4. In cPanel File Manager, view the live `.htaccess` (show hidden files); append the line from `htaccess.suggested` if no conflicting `ErrorDocument` exists.
5. Spot-check https://www.pqsensing.com/ — tab icon, footer legal line, metrology201 ISL section styling, and a made-up URL for the 404 page.

Alternative (WinSCP on Windows): open a session to the same host and upload the 13 manifest files, preserving paths (`drafting/index.html` into `public_html/drafting/`).

No DNS, hosting-plan, or mail configuration is touched by this package.
