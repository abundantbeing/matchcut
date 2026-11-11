// The demo's takes. Serve examples/demo/site on :8776, then from examples/demo:
//   SLOW=8 node ../../skills/ui-reel/assets/rig/take.mjs reveal   (and launch, sweep)
const URL = 'http://127.0.0.1:8776/index.html';
const fresh = async a => { await a.eval(`(location.href = ${JSON.stringify(URL)}, true)`).catch(() => {}); await a.sleep(4200); };

export const TAKES = {
  // the match-cut landing: the app boots (?hold waits for boot()): the dots fly in and lock into the globe,
  // the orbits draw on and the panels glide in. The pointer is parked off screen.
  reveal: {
    async setup(a) {
      await a.eval(`(location.href = ${JSON.stringify(URL + '?hold')}, true)`).catch(() => {});
      await a.sleep(2600);
      await a.setMouse({ x: 1300, y: 760 });
    },
    async run(a) {
      await a.sleep(200);
      a.mark('boot');
      await a.eval('(boot(), true)');
      await a.sleep(5600);
      a.mark('end');
    }
  },
  // name a satellite, launch it: the pad locks and ignites, ascent, orbit, then its first image downlinks and opens full size
  launch: {
    async setup(a) { await fresh(a); await a.setMouse({ x: 980, y: 140 }); },
    async run(a) {
      const b = await a.rect('#launch');
      await a.sleep(300);
      await a.move({ x: b.cx, y: b.cy }, 650);
      await a.sleep(120);
      a.mark('open');
      await a.click();
      await a.sleep(700);
      a.mark('type');
      await a.type('Kestrel', 110);
      await a.sleep(300);
      const go = await a.rect('#go');
      await a.move({ x: go.cx, y: go.cy }, 500);
      await a.sleep(120);
      a.mark('go');
      await a.click();
      await a.move({ x: 900, y: 600 }, 900);
      await a.sleep(1800);
      a.mark('liftoff');
      await a.sleep(3600);
      a.mark('orbit');
      await a.sleep(1000);
      a.mark('downlink');
      await a.sleep(3400);
      const cap = await a.rect('#capbox');
      await a.move({ x: cap.cx, y: cap.cy }, 700);
      await a.sleep(150);
      a.mark('open-image');
      await a.click();
      await a.sleep(2600);
      a.mark('end');
    }
  },
  // the pointer runs down the fleet; each satellite's orbit lights up on the globe as it passes
  sweep: {
    async setup(a) { await fresh(a); await a.setMouse({ x: 150, y: 120 }); },
    async run(a) {
      await a.sleep(300);
      a.mark('sweep');
      await a.trace(k => ({ x: 150 + 20 * Math.sin(k * 6), y: 135 + 430 * k }), 3600);
      await a.sleep(400);
      a.mark('end');
    }
  }
};
