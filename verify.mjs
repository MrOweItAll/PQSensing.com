import { createRequire } from 'module';
const require = createRequire('/home/claude/.npm-global/lib/node_modules/');
const { chromium } = require('playwright');
const seq = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'];
const b = await chromium.launch();
// Test 1: typing sequence inside a form field must NOT trigger egg
const p1 = await b.newPage();
try { await p1.goto('http://localhost:8099/contact.html',{waitUntil:'load',timeout:15000}); } catch(e){}
await p1.click('#cf-message');
for (const k of seq){ await p1.keyboard.press(k); await p1.waitForTimeout(20); }
await p1.waitForTimeout(400);
console.log('in-form egg (should be false):', !!(await p1.$('#eggPort')));
// Test 2: sequence on the body DOES trigger
const p2 = await b.newPage();
try { await p2.goto('http://localhost:8099/index.html',{waitUntil:'load',timeout:15000}); } catch(e){}
await p2.click('body', { position: { x: 5, y: 5 } }).catch(()=>{});
for (const k of seq){ await p2.keyboard.press(k); await p2.waitForTimeout(20); }
await p2.waitForTimeout(400);
console.log('body egg (should be true):', !!(await p2.$('#eggPort')));
await b.close();
