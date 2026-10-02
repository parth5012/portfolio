// Renders tools/og-card.html to static/og.png at 1200x630, the size every
// social platform expects for a link preview. Run: node tools/make-og.mjs
import { chromium } from '/home/parth/.local/lib/node_modules/playwright/index.mjs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
await page.goto('file://' + resolve(here, 'og-card.html'), { waitUntil: 'load' });
await page.waitForTimeout(400);
await page.screenshot({ path: resolve(here, '../static/og.png') });
await browser.close();
console.log('wrote static/og.png (1200x630)');