const { chromium } = require('playwright');
const path = require('path');
const [,, PAGE, FRAMES, TOTAL_S] = process.argv; const FPS = 30, TOTAL = parseFloat(TOTAL_S);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await p.addInitScript(() => {
    let vt = 0; const q = [];
    performance.now = () => vt;
    window.requestAnimationFrame = (cb) => { q.push(cb); return q.length; };
    window.__step = (ms) => { vt += ms; const cbs = q.splice(0); cbs.forEach(cb => cb(vt)); };
  });
  await p.goto('file://' + path.resolve(PAGE));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(800);
  await p.evaluate(() => { document.getElementById('sound').click(); document.getElementById('play').click(); });
  await p.addStyleTag({ content: '.controls{display:none!important}' });
  const n = Math.round(TOTAL * FPS);
  for (let i = 0; i < n; i++) {
    await p.evaluate((ms) => window.__step(ms), 1000 / FPS);
    await p.screenshot({ path: path.join(path.resolve(FRAMES), `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 92 });
  }
  await b.close();
  console.log('frames', n);
})();
