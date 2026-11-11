// Takes for tools/take.mjs. Each take has setup (not recorded: load, seed, open the right screen) and run
// (recorded: what a person would do). Setup must load the page, so the slow-motion shim installs on it.
// The api: sleep, mark(label), eval(js), rect(selector, textRegex), move(to, ms, ease), trace(fn, ms), click(),
// wheel(total, ms), setMouse(p), shot(file), W, H. Movement and sleeps run in film time.
const URL = 'http://127.0.0.1:8771/index.html?demo=1';

async function fresh(a) {
  await a.eval(`(location.href = ${JSON.stringify(URL)}, true)`).catch(() => {});
  await a.sleep(3500);
}

export const TAKES = {
  // the opening take: starts on the hero object at the size and place the cold open leaves it
  hero: {
    async setup(a) {
      await fresh(a);
      await a.eval(`(document.querySelector('[data-hero]')?.click(), true)`);
      await a.sleep(2000);
      await a.setMouse({ x: a.W / 2 + 150, y: a.H / 2 + 120 });
    },
    async run(a) {
      const c = await a.rect('[data-hero]');
      await a.sleep(1300);
      a.mark('tilt');
      // slow loops over the object so hover effects play
      await a.trace(k => { const g = Math.PI * 0.25 - k * Math.PI * 2.4; return { x: c.cx + Math.cos(g) * c.w * 0.36, y: c.cy + Math.sin(g) * c.h * 0.34 }; }, 3000);
      const b = await a.rect('button', '^Flip$');
      await a.move({ x: b.cx, y: b.cy }, 500);
      await a.sleep(200);
      a.mark('flip');
      await a.click();
      await a.sleep(1800);
      a.mark('end');
    }
  },
  // a scroll through a list or gallery
  detail: {
    async setup(a) { await fresh(a); await a.setMouse({ x: 700, y: 470 }); },
    async run(a) {
      await a.sleep(500);
      a.mark('scroll');
      await a.wheel(620, 2400);
      await a.sleep(500);
      await a.wheel(900, 2600);
      await a.sleep(900);
      a.mark('end');
    }
  }
};
