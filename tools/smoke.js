/* Drive the built page in a real browser and fail on any thrown error.
 *
 *   NODE_PATH=~/.npm/_npx/<hash>/node_modules node tools/smoke.js [docs/index.html]
 *
 * Everything on this page that depends on the picker is computed in the browser,
 * and a handler that throws does not look broken - it looks like a page that has
 * stopped responding to one control. The bug that prompted this got shipped and
 * was found by a reader: selecting a memory size with no price on record threw
 * inside the picker handler, so the "What for?" selector silently stopped
 * reordering the table. Nothing was visibly wrong. Nothing in CI executed the
 * JavaScript at all.
 *
 * So this walks every chip, several memory sizes including the unpriced ones,
 * one and two units, and every use case, and treats a single pageerror as a
 * failure. It is slower than the other checks and needs a browser, which is why
 * it is a separate tool rather than part of build.py.
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const FILE = path.resolve(process.argv[2] || 'docs/index.html');

(async () => {
  if (!fs.existsSync(FILE)) {
    console.error(`no such file: ${FILE} - run tracker/build.py first`);
    process.exit(1);
  }
  // CI has Playwright's own chromium; a developer machine usually has Chrome
  // installed and no downloaded browser. Try the bundled one first so CI is the
  // predictable path, and fall back rather than making everyone download 150 MB.
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
  } catch (e) {
    browser = await chromium.launch({ headless: true, channel: 'chrome' });
  }
  const failures = [];
  let checks = 0;
  try {
    const page = await browser.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push(e.message.split('\n')[0]));
    page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 140)); });

    await page.goto('file://' + FILE, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);
    const chips = await page.$$eval('#rig-chip option', o => o.map(x => x.value).filter(Boolean));
    const ucs = await page.$$eval('#uc-sel option', o => o.map(x => x.value));

    for (const chip of chips) {
      await page.selectOption('#rig-chip', chip);
      await page.waitForTimeout(120);
      const mems = await page.$$eval('#rig-mem option', o => o.map(x => x.value).filter(Boolean));
      for (const mem of mems) {
        for (const n of ['1', '2']) {
          errs.length = 0;
          await page.selectOption('#rig-mem', mem);
          try { await page.selectOption('#rig-n', n); } catch (e) { /* single-unit chips */ }
          for (const uc of ucs) {
            await page.selectOption('#uc-sel', uc);
            await page.waitForTimeout(35);
            checks++;
          }
          if (errs.length) {
            failures.push(`${chip} ${mem}GB x${n}: ${[...new Set(errs)].slice(0, 2).join(' | ')}`);
          }
        }
      }
    }
  // The ranking bar is drawn behind the model name and sized as a percentage of
  // that cell, so anything making the cell width vary per row makes the chart lie.
  // It did: on mobile the name shared a row with the status pill, and a long label
  // like "Fastest, with caveats" cut the cell from 225px to 128px, drawing a
  // SHORTER bar for a BETTER-ranked model. Assert bars never grow downward.
  // reducedMotion matters - the bar has a 180ms width transition and sampling
  // mid-animation reports inversions that are not real.
  const inversions = [];
  try {
    const page = await browser.newPage({ viewport: { width: 390, height: 900 },
                                         reducedMotion: 'reduce' });
    for (const vp of [{ w: 390, n: 'mobile' }, { w: 1280, n: 'desktop' }]) {
      await page.setViewportSize({ width: vp.w, height: 900 });
      await page.goto('file://' + FILE, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(400);
      const ucs = await page.$$eval('#uc-sel option', o => o.map(x => x.value).filter(Boolean));
      for (const uc of ucs) {
        await page.selectOption('#uc-sel', uc);
        await page.waitForTimeout(120);
        const rows = await page.$$eval('.ix-row', rs => rs.filter(r => !r.hidden)
          .map(r => ({ m: r.getAttribute('data-model'),
                       o: parseInt(getComputedStyle(r).order) || 0,
                       w: r.querySelector('.ix-bar').getBoundingClientRect().width }))
          .sort((a, c) => a.o - c.o));
        for (let i = 1; i < rows.length; i++) {
          if (rows[i].w > rows[i - 1].w + 1.5) {
            inversions.push(`${vp.n} ${uc}: ${rows[i].m} draws ${rows[i].w.toFixed(0)}px ` +
              `below ${rows[i - 1].m} at ${rows[i - 1].w.toFixed(0)}px`);
          }
        }
        checks++;
      }
    }
    await page.close();
  } catch (e) {
    failures.push('bar monotonicity check: ' + e.message.slice(0, 90));
  }
  if (inversions.length) failures.push(...[...new Set(inversions)].slice(0, 6));
  } finally {
    await browser.close();
  }

  console.log(`${checks} picker/use-case combinations exercised`);
  if (failures.length) {
    console.error(`\n${failures.length} configurations threw:`);
    [...new Set(failures)].slice(0, 20).forEach(f => console.error('  ' + f));
    process.exit(1);
  }
  console.log('no page errors');
})().catch(e => { console.error('ERR', e.message.slice(0, 200)); process.exit(1); });
