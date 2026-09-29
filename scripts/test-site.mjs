#!/usr/bin/env node
/** Repository build regression gate. Never submits contact messages.
 * npm ci && npm run build
 * PLAYWRIGHT_MODULE_PATH=/absolute/node_modules/playwright/index.mjs node scripts/test-site.mjs
 * The local server is deliberately simple: it cannot validate production Apache
 * redirects, authentication, host-managed paths, DNS, or release activation.
 */
import { createServer } from 'node:http';
import { createReadStream, existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { dirname, extname, join, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
const require = createRequire(import.meta.url);
const options = { dist: 'dist', report: 'verification/browser.json' };
for (let i = 2; i < process.argv.length; i += 2) {
  const name = process.argv[i]?.replace(/^--/, '');
  if (!Object.hasOwn(options, name) || !process.argv[i + 1]) throw new Error('Usage: test-site.mjs [--dist dist] [--report verification/browser.json]');
  options[name] = process.argv[i + 1];
}
const dist = resolve(options.dist);
const reportPath = resolve(options.report);
const widths = [320, 375, 390, 768, 1024, 1280, 1440, 1441, 1536];
const report = { schemaVersion: 1, startedAt: new Date().toISOString(), scope: 'local repository build only; not live reconciliation', sourceSha: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(), node: process.version, widths, checks: [], diagnostics: [], externalRequestsStubbed: [], contactSubmissions: 0, status: 'running' };
const check = (name, passed, detail = {}) => report.checks.push({ name, status: passed ? 'passed' : 'failed', ...detail });
const walk = (dir) => readdirSync(dir, { withFileTypes: true }).flatMap(e => e.isDirectory() ? walk(join(dir, e.name)) : [join(dir, e.name)]);
let server, browser;
let base;
try {
  if (!existsSync(dist)) throw new Error('Build output absent. Run npm run build first.');
  const routes = walk(dist).filter(p => p.endsWith('.html')).map(p => '/' + relative(dist, p).split(sep).join('/')).sort();
  report.routes = routes;
  const baseline = JSON.parse(readFileSync('tests/site/repository-baseline.json', 'utf8'));
  check('repository route inventory', JSON.stringify(routes) === JSON.stringify(baseline.htmlRoutes), { actual: routes, expected: baseline.htmlRoutes });
  const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.ico': 'image/x-icon', '.pdf': 'application/pdf', '.xml': 'application/xml', '.json': 'application/json', '.woff2': 'font/woff2', '.woff': 'font/woff', '.mp4': 'video/mp4', '.m4v': 'video/mp4', '.m4a': 'audio/mp4', '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation' };
  server = createServer((req, res) => {
    if (!['GET', 'HEAD'].includes(req.method)) { res.writeHead(405).end(); return; }
    let pathname;
    try { pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname); } catch { res.writeHead(400).end(); return; }
    let file = resolve(dist, '.' + pathname);
    if (file !== dist && !file.startsWith(dist + sep)) { res.writeHead(403).end(); return; }
    if (existsSync(file) && statSync(file).isDirectory()) file = join(file, 'index.html');
    if (!existsSync(file) || !statSync(file).isFile()) { res.writeHead(404).end('Not found'); return; }
    res.writeHead(200, { 'Content-Type': types[extname(file)] || 'application/octet-stream', 'Content-Length': statSync(file).size });
    if (req.method === 'HEAD') res.end(); else createReadStream(file).pipe(res);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  base = `http://127.0.0.1:${server.address().port}`;
  // These checks still run if a browser binary is missing.
  for (const route of ['/', ...routes, '/updates/rss.xml', '/sitemap-index.xml', '/robots.txt']) {
    const response = await fetch(base + route);
    check('HTTP route', response.status === 200, { route, statusCode: response.status });
  }
  check('local missing route preserves 404', (await fetch(base + '/__pqs_nonexistent_9f442.html')).status === 404);
  for (const file of walk(dist).filter(p => /\.(pdf|pptx)$/i.test(p))) {
    const route = '/' + relative(dist, file).split(sep).join('/');
    const bytes = Buffer.from(await (await fetch(base + route)).arrayBuffer());
    check('download bytes', bytes.equals(readFileSync(file)), { route, bytes: bytes.length });
  }
  let playwright, playwrightPackage;
  if (process.env.PLAYWRIGHT_MODULE_PATH) {
    playwright = await import(pathToFileURL(resolve(process.env.PLAYWRIGHT_MODULE_PATH)));
    playwrightPackage = join(dirname(resolve(process.env.PLAYWRIGHT_MODULE_PATH)), 'package.json');
  }
  else {
    try { playwright = await import('playwright'); playwrightPackage = require.resolve('playwright/package.json'); }
    catch {
      if (!process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES) throw new Error('Playwright unavailable; set PLAYWRIGHT_MODULE_PATH to the pinned playwright/index.mjs.');
      playwright = await import(pathToFileURL(join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES, 'playwright/index.mjs')));
      playwrightPackage = join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES, 'playwright/package.json');
    }
  }
  report.playwright = require(playwrightPackage).version;
  browser = await playwright.chromium.launch({ headless: true });
  report.browser = browser.version();
  const context = await browser.newContext({ reducedMotion: 'reduce' });
  await context.route('**/*', async route => {
    const request = route.request();
    if (!['GET', 'HEAD'].includes(request.method())) {
      report.contactSubmissions++;
      check('no form or other write request', false, { method: request.method(), destination: new URL(request.url()).origin });
      await route.abort(); return;
    }
    const url = new URL(request.url());
    if (['http:', 'https:'].includes(url.protocol) && url.origin !== base) {
      if (!report.externalRequestsStubbed.includes(url.origin)) report.externalRequestsStubbed.push(url.origin);
      await route.fulfill({ status: 200, contentType: request.resourceType() === 'stylesheet' ? 'text/css' : 'text/plain', body: '' }); return;
    }
    await route.continue();
  });
  // A metadata check per document and viewport checks around the menu breakpoint.
  for (const route of routes) {
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    for (const width of widths) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(base + route, { waitUntil: 'load', timeout: 20000 });
      if (route === '/drafting/index.html') await page.waitForURL('**/architecture.html');
      await page.evaluate(async () => { await document.fonts.ready; await new Promise(requestAnimationFrame); });
      const info = await page.evaluate(() => ({
        title: document.title,
        canonical: document.querySelector('link[rel="canonical"]')?.href,
        description: document.querySelector('meta[name="description"]')?.content,
        width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
        overflow: [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && s.display !== 'none' && s.visibility !== 'hidden' && (r.right > innerWidth + 1 || r.left < -1); }).slice(0, 8).map(e => ({ element: e.tagName, id: e.id, class: typeof e.className === 'string' ? e.className.slice(0, 100) : '' }))
      }));
      check('responsive width', info.scrollWidth <= width + 1, { route, width, scrollWidth: info.scrollWidth, overflow: info.overflow });
      if (width === widths[0]) {
        check('title and description', !!info.title && !!info.description, { route, title: info.title });
        check('canonical origin preserved', info.canonical?.startsWith('https://www.pqsensing.com/'), { route, canonical: info.canonical });
      }
      if (width === 1440) {
        const brokenImages = await page.evaluate(async () => {
          const images = [...document.images].filter(image => image.getAttribute('src') && !image.closest('[hidden]'));
          for (const image of images) image.loading = 'eager';
          await Promise.all(images.map(image => image.decode().catch(() => {})));
          return images.filter(image => !image.complete || image.naturalWidth === 0).map(image => image.getAttribute('src'));
        });
        check('page images load', brokenImages.length === 0, { route, brokenImages });
      }
      const toggle = page.locator('.nav-toggle');
      if (await toggle.count() && await toggle.isVisible()) {
        await toggle.click();
        check('mobile menu opens', await page.locator('.nav-links').isVisible(), { route, width });
        check('open menu stays within viewport', await page.locator('.nav-links').evaluate(e => { const r = e.getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth && r.bottom <= innerHeight && e.clientWidth >= e.scrollWidth; }), { route, width });
        const link = page.locator('.nav-links a').first();
        await link.click();
        await page.waitForLoadState('load');
        check('mobile menu closes after navigation', !(await page.locator('body').evaluate(e => e.classList.contains('nav-open'))), { route, width });
      }
      if (['/index.html', '/architecture.html', '/contact.html'].includes(route) && [375, 1440].includes(width)) {
        await page.goto(base + route, { waitUntil: 'load' });
        const screenshot = join(dirname(reportPath), 'screenshots', `${route.slice(1).replace('.html', '')}-${width}.png`);
        mkdirSync(dirname(screenshot), { recursive: true });
        await page.screenshot({ path: screenshot, fullPage: true });
      }
    }
    check('browser console and runtime errors', errors.length === 0, { route, errors: [...new Set(errors)] });
    await page.close();
  }
  const page = await context.newPage();
  const site = JSON.parse(readFileSync('src/data/site.json', 'utf8'));
  await page.goto(base + '/contact.html?type=architecture&package=Regression%20Preview');
  const contact = await page.evaluate(() => {
    const form = document.getElementById('contactForm');
    return { action: form.action, method: form.method, fields: [...form.elements].map(e => e.name).filter(Boolean), type: document.getElementById('cf-type').value, package: document.getElementById('cf-package').value, packageHidden: document.getElementById('cf-package-wrap').hidden, subject: document.getElementById('cf-subject').value, mailto: document.getElementById('cf-mailto').href, emptyValid: form.checkValidity() };
  });
  check('contact target and method', contact.action === site.formspreeEndpoint && contact.method === 'post', { action: contact.action });
  check('contact expected fields', ['name', 'email', 'inquiry_type', 'package', 'message', '_subject', '_gotcha'].every(x => contact.fields.includes(x)));
  check('contact query prefill', contact.type === 'architecture' && contact.package === 'Regression Preview' && !contact.packageHidden && contact.subject.includes('Regression Preview'));
  check('contact fallback address', contact.mailto.startsWith('mailto:' + site.contactEmail + '?subject='));
  check('empty required fields invalid', contact.emptyValid === false);
  await page.locator('#cf-name').fill('Local regression check');
  await page.locator('#cf-email').fill('invalid-email');
  await page.locator('#cf-message').fill('No submission occurs.');
  check('invalid email rejected', !(await page.locator('#contactForm').evaluate(f => f.checkValidity())));
  await page.locator('#cf-email').fill('preview@example.invalid');
  check('valid fields accepted without submission', await page.locator('#contactForm').evaluate(f => f.checkValidity()));
  await page.locator('#cf-type').selectOption('validation');
  check('non-architecture package hidden', await page.locator('#cf-package-wrap').evaluate(e => e.hidden));
  const portfolio = JSON.parse(readFileSync('src/data/portfolio.json', 'utf8'));
  await page.goto(base + '/architecture.html');
  check('gallery project and image inventory', await page.locator('.arch-tile').count() === baseline.gallery.projects && portfolio.reduce((n, p) => n + p.images.length, 0) === baseline.gallery.images, baseline.gallery);
  for (const filter of await page.locator('.arch-filter').all()) {
    const category = await filter.getAttribute('data-filter');
    await filter.click();
    check('gallery filter', await page.locator('.arch-tile:visible').count() === portfolio.filter(p => category === 'all' || p.cat === category).length, { category });
  }
  await page.locator('.arch-filter[data-filter="all"]').click();
  for (let i = 0; i < portfolio.length; i++) {
    const project = portfolio[i];
    await page.locator(`.arch-tile[data-project="${i}"]`).click();
    check('gallery opens', await page.locator('#archLightbox').isVisible(), { project: project.title });
    for (let j = 0; j < project.images.length; j++) {
      await page.waitForFunction(() => { const image = document.getElementById('archLbImage'); return image.complete && image.naturalWidth > 0; });
      check('gallery image', await page.locator('#archLbImage').getAttribute('src') === project.images[j].full, { project: project.title, image: j + 1 });
      if (j < project.images.length - 1) await page.keyboard.press('ArrowRight');
    }
    await page.keyboard.press('Escape');
    check('gallery closes and restores focus', !(await page.locator('#archLightbox').isVisible()) && await page.locator(`.arch-tile[data-project="${i}"]`).evaluate(e => document.activeElement === e), { project: project.title });
  }
  check('zero contact submissions', report.contactSubmissions === 0);
  await context.close();
  report.status = report.checks.some(c => c.status === 'failed') ? 'failed' : 'passed';
} catch (error) {
  report.status = 'blocked_or_failed';
  report.error = error.message;
} finally {
  await browser?.close();
  if (server) await new Promise(resolve => server.close(resolve));
  report.finishedAt = new Date().toISOString();
  report.summary = { passed: report.checks.filter(c => c.status === 'passed').length, failed: report.checks.filter(c => c.status === 'failed').length };
  mkdirSync(dirname(reportPath), { recursive: true });
  writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ status: report.status, ...report.summary, report: reportPath, error: report.error }));
  process.exitCode = report.status === 'passed' ? 0 : 1;
}
