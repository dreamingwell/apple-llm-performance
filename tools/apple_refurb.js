/* Harvest Apple Certified Refurbished Mac prices, keyed by (chip, memory).
 *
 *   NODE_PATH=~/.npm/_npx/<hash>/node_modules node tools/apple_refurb.js > /tmp/refurb.json
 *
 * Two stages, because Apple's listing grid does not carry memory: collect the
 * product URLs from each category, then read chip, memory, storage and price
 * off each product page. Titles alone are not enough - "Refurbished 14-inch
 * MacBook Pro Apple M4 Max Chip with 16-Core CPU and 40-Core GPU" describes
 * three different memory configurations at three different prices.
 *
 * These are Apple's own list prices for used hardware, so they are the same
 * confidence class as the new-machine figures and need no median, no outlier
 * rejection and no sample floor. What they are not is a market survey: Apple
 * stocks what it happens to have refurbished, it rotates constantly, and the
 * high-memory desktops this page cares about are usually absent entirely.
 */
const { chromium } = require('playwright');

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ' +
           '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';
const CATEGORIES = ['mac-studio', 'macbook-pro', 'mac-mini', 'mac-pro', 'imac'];

function chipOf(title) {
  const m = title.match(/Apple\s+(M\d)\s*(Pro|Max|Ultra)?\s*[Cc]hip/);
  if (!m) return null;
  return ('m' + m[1].slice(1) + (m[2] ? m[2].toLowerCase() : ''));
}

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  const out = {};
  try {
    const page = await browser.newPage({ userAgent: UA });
    const urls = new Set();
    for (const cat of CATEGORIES) {
      try {
        await page.goto(`https://www.apple.com/shop/refurbished/mac/${cat}`,
                        { waitUntil: 'networkidle', timeout: 60000 });
        const hs = await page.$$eval('a[href*="/shop/product/"]', els =>
          els.map(e => e.getAttribute('href').split('?')[0]));
        hs.forEach(h => { if (!/display|airpod|watch|ipad|iphone|tv|homepod/i.test(h)) urls.add(h); });
      } catch (e) { console.error(`  ${cat}: ${e.message.slice(0, 70)}`); }
    }
    console.error(`  ${urls.size} product pages to read`);

    let n = 0;
    for (const href of urls) {
      n++;
      try {
        await page.goto('https://www.apple.com' + href, { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.waitForTimeout(400);
        const title = await page.title();
        const body = (await page.innerText('body')).replace(/\s+/g, ' ');
        const chip = chipOf(title) || chipOf(body);
        const ram = (body.match(/(\d+)\s?GB unified memory/i) || [])[1];
        const price = (body.match(/\$([\d,]{3,7})\.\d\d/) || [])[1];
        const ssd = (body.match(/(\d+(?:TB|GB))\s+SSD/i) || [])[1] || '';
        if (!chip || !ram || !price) continue;
        const gb = parseInt(ram, 10), usd = parseInt(price.replace(/,/g, ''), 10);
        const key = `${chip}:${gb}`;
        // cheapest wins, which is the smallest storage at that memory
        if (!out[key] || usd < out[key].usd) {
          out[key] = { chip, gb, usd, ssd, title: title.replace(/ - Apple.*$/, '').trim(),
                       url: 'https://www.apple.com' + href };
        }
      } catch (e) { /* a rotated-out product is normal, skip it */ }
      if (n % 25 === 0) console.error(`  ...${n}/${urls.size}`);
    }
  } finally {
    await browser.close();
  }
  console.log(JSON.stringify(out, null, 1));
})().catch(e => { console.error('ERR', e.message.slice(0, 200)); process.exit(1); });
