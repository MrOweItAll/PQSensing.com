#!/usr/bin/env node
/**
 * check-links.mjs — build-time internal link gate for the PQSensing static site.
 *
 * Why this exists: the site builds with `output: 'static'` + `build.format: 'file'`,
 * so pages emit as `/contact.html` (not `/contact/`). The static host has no
 * rewrite, so an extensionless link like `/contact?type=x` resolves to `/contact`
 * and 404s. A batch of those shipped once. This script fails the build if any
 * internal href/src points at a file that doesn't exist in `dist/`, so that
 * class of bug can never ship again.
 *
 * Usage:  node scripts/check-links.mjs [distDir]   (default: ./dist)
 * Exit:   0 = all internal links resolve; 1 = one or more broken.
 * No external dependencies. Node 20+.
 */
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';

const DIST = resolve(process.argv[2] || 'dist');

if (!existsSync(DIST)) {
  console.error(`✗ check-links: dist directory not found at ${DIST}. Run the build first.`);
  process.exit(1);
}

/** Recursively collect every .html file under a directory. */
function htmlFiles(dir, out = []) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) htmlFiles(full, out);
    else if (entry.name.endsWith('.html')) out.push(full);
  }
  return out;
}

/** True if a resolved filesystem path is a servable file (or a dir with index.html). */
function servable(fsPath) {
  if (!existsSync(fsPath)) return false;
  if (statSync(fsPath).isDirectory()) return existsSync(join(fsPath, 'index.html'));
  return true;
}

const SKIP = /^(https?:|mailto:|tel:|data:|javascript:|#)/i;
const LINK_RE = /(?:href|src)\s*=\s*"([^"]+)"/g;

const pages = htmlFiles(DIST);
const broken = []; // { page, link, resolved }
let checked = 0;

for (const page of pages) {
  const html = readFileSync(page, 'utf8');
  const seen = new Set();
  let m;
  while ((m = LINK_RE.exec(html)) !== null) {
    const raw = m[1].trim();
    if (seen.has(raw)) continue;
    seen.add(raw);

    if (!raw || SKIP.test(raw)) continue;
    if (raw.includes('${')) continue; // unresolved template expression in inline JS — not a real link

    // Strip fragment + query, keep the path only.
    const path = raw.split('#')[0].split('?')[0];
    if (!path) continue; // was a pure #fragment / query on the same page

    // Resolve: absolute paths against dist root, relative against the page's dir.
    const fsPath = path.startsWith('/')
      ? join(DIST, path)
      : join(dirname(page), path);

    checked++;
    if (!servable(fsPath)) {
      broken.push({ page: page.replace(DIST + '/', ''), link: raw, resolved: fsPath.replace(DIST + '/', '') });
    }
  }
}

if (broken.length === 0) {
  console.log(`✓ check-links: ${checked} internal links OK across ${pages.length} pages.`);
  process.exit(0);
}

// Group the report by source page for readability.
console.error(`✗ check-links: ${broken.length} broken internal link(s) found:\n`);
const byPage = new Map();
for (const b of broken) {
  if (!byPage.has(b.page)) byPage.set(b.page, []);
  byPage.get(b.page).push(b);
}
for (const [pageName, items] of byPage) {
  console.error(`  ${pageName}`);
  for (const it of items) console.error(`     ✗ ${it.link}   →   missing: ${it.resolved}`);
  console.error('');
}
console.error('Build failed: fix the links above (static host serves /page.html, not /page).');
process.exit(1);
