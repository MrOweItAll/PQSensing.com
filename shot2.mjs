import { createRequire } from 'module';
const require = createRequire('/home/claude/.npm-global/lib/node_modules/');
const { chromium } = require('playwright');
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
try { await page.goto('http://localhost:8099/index.html', { waitUntil: 'load', timeout: 15000 }); } catch(e){}
await page.waitForTimeout(1000);
const el = await page.$('#dpi-demo'); if (el) await el.scrollIntoViewIfNeeded();
await page.waitForTimeout(500);
// read the recovery status text
const status = await page.$eval('#dpiRecStatus', n => n.textContent).catch(()=>'?');
const trueLag = await page.$eval('#dpiTrueLag', n => n.textContent).catch(()=>'?');
const recLag = await page.$eval('#dpiRecLag', n => n.textContent).catch(()=>'?');
const gain = await page.$eval('#dpiGain', n => n.textContent).catch(()=>'?');
console.log('DPI default:', JSON.stringify({trueLag, recLag, status, gain}));
const el2 = await page.$('#dpi-demo'); if (el2) await el2.screenshot({ path: '/tmp/dpi2.png' });
await browser.close();
