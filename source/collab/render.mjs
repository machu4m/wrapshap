// Prints build/post.html to a vector PDF (build/raw.pdf) and records the logo slot.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
import path from 'path';

const here = path.dirname(new URL(import.meta.url).pathname);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1440 } });
await page.goto('file://' + path.join(here, 'build', 'post.html'));
await page.evaluate(() => document.fonts.ready);
await page.emulateMedia({ media: 'print' });
const slots = await page.$$eval('.logo-slot', els => els.map(e => {
  const r = e.getBoundingClientRect();
  return { id: e.id, x: r.x, y: r.y, w: r.width, h: r.height };
}));
fs.writeFileSync(path.join(here, 'build', 'slots.json'), JSON.stringify(slots));
await page.pdf({ path: path.join(here, 'build', 'raw.pdf'), width: '15in', height: '15in', printBackground: true });
await browser.close();
console.log('printed raw.pdf');
