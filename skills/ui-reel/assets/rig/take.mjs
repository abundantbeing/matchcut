// Record one take of the real product in the headless recording browser, driven like a person
// (trusted CDP mouse input). Writes JPEG screencast frames + frames.json, and take.json with the pointer
// path and named marks on the same clock.
//   node tools/take.mjs <takeName> [--dry]
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
// the takes live in the project, not beside this file: TAKES=path/to/takes.mjs, default ./takes.mjs
const { TAKES } = await import(pathToFileURL(path.resolve(process.env.TAKES || 'takes.mjs')).href);

const name = process.argv[2];
const dry = process.argv.includes('--dry');
// The page runs K times slower than real time while recording (its clocks, timers and CSS animations), and
// the driver moves K times slower too, so a slow screencast still yields every frame of film time.
const K = Number(process.env.SLOW || 4);
const port = process.env.CDP_PORT || 9447;
const targetId = fs.readFileSync('out/target.txt', 'utf8').trim();
const outDir = `out/rec/${name}`;
fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(outDir, { recursive: true });

const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const target = list.find(t => t.id === targetId);
await fetch(`http://127.0.0.1:${port}/json/activate/${targetId}`);
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let id = 0;
const pending = new Map();
const frames = [];
let t0 = null; // screencast clock of the first frame
let wall0 = null; // wall clock at the first frame
let recording = false;
ws.onmessage = ev => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); return; }
  if (msg.method === 'Page.screencastFrame') {
    const { data, metadata, sessionId } = msg.params;
    send('Page.screencastFrameAck', { sessionId });
    if (!recording) return;
    if (t0 === null) { t0 = metadata.timestamp; wall0 = performance.now(); }
    const file = `f${String(frames.length).padStart(5, '0')}.jpg`;
    fs.writeFileSync(path.join(outDir, file), Buffer.from(data, 'base64'));
    frames.push({ file, t: (metadata.timestamp - t0) / K });
  }
};
function send(method, params = {}) {
  return new Promise(res => { id += 1; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
}
const realSleep = ms => new Promise(r => setTimeout(r, ms));
let slow = 1;
const sleep = ms => realSleep(ms * slow);
const now = () => (wall0 === null ? 0 : (performance.now() - wall0) / 1000 / K);
const pointer = []; // {t,x,y,down}
const marks = [];
const keys = []; // {t, key}: every keystroke, for the key sounds
let mouse = { x: 640, y: 380 };
// VIEW=phone records a 390 x 844 touch viewport for the phone shots; default is a 1280 x 720 desktop.
const PHONE = process.env.VIEW === 'phone';
const W = PHONE ? 390 : 1280, H = PHONE ? 844 : 720;

const api = {
  sleep,
  mark: label => { marks.push({ t: now(), label }); console.log(now().toFixed(2), label); },
  async eval(expr) {
    const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
    if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 400));
    return r.result?.result?.value;
  },
  // centre of the first element matching a selector, or whose text matches /re/ among `sel`
  async rect(sel, text) {
    const r = await api.eval(`(() => { const els = [...document.querySelectorAll(${JSON.stringify(sel)})]; const el = ${text ? `els.find(e => new RegExp(${JSON.stringify(text)}, 'i').test(e.textContent))` : 'els[0]'}; if (!el) return null; const b = el.getBoundingClientRect(); return { x: b.left, y: b.top, w: b.width, h: b.height, cx: b.left + b.width / 2, cy: b.top + b.height / 2 }; })()`);
    if (!r) throw new Error(`no element ${sel} ${text || ''}`);
    return r;
  },
  async move(to, ms = 600, ease = t => t * t * (3 - 2 * t)) {
    ms *= slow;
    const from = { ...mouse };
    const steps = Math.max(2, Math.round(ms / 33));
    const start = performance.now();
    for (let i = 1; i <= steps; i++) {
      const k = ease(i / steps);
      mouse = { x: from.x + (to.x - from.x) * k, y: from.y + (to.y - from.y) * k };
      void send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: mouse.x, y: mouse.y });
      pointer.push({ t: now(), x: mouse.x, y: mouse.y });
      const due = start + (ms * i) / steps;
      const wait = due - performance.now();
      if (wait > 0) await realSleep(wait);
    }
  },
  // follow a path function p(k) -> {x,y} for ms
  async trace(fn, ms) {
    ms *= slow;
    const steps = Math.max(2, Math.round(ms / 33));
    const start = performance.now();
    for (let i = 1; i <= steps; i++) {
      mouse = fn(i / steps);
      void send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: mouse.x, y: mouse.y });
      pointer.push({ t: now(), x: mouse.x, y: mouse.y });
      const wait = start + (ms * i) / steps - performance.now();
      if (wait > 0) await realSleep(wait);
    }
  },
  async click() {
    pointer.push({ t: now(), x: mouse.x, y: mouse.y, down: true });
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: mouse.x, y: mouse.y, button: 'left', clickCount: 1 });
    await realSleep(70 * slow);
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: mouse.x, y: mouse.y, button: 'left', clickCount: 1 });
    pointer.push({ t: now(), x: mouse.x, y: mouse.y, down: false });
  },
  async wheel(total, ms) {
    ms *= slow;
    const steps = Math.max(2, Math.round(ms / 33));
    const start = performance.now();
    let done = 0;
    for (let i = 1; i <= steps; i++) {
      const k = i / steps;
      const e = k * k * (3 - 2 * k);
      const want = total * e;
      void send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: mouse.x, y: mouse.y, deltaX: 0, deltaY: want - done });
      done = want;
      pointer.push({ t: now(), x: mouse.x, y: mouse.y });
      const wait = start + (ms * i) / steps - performance.now();
      if (wait > 0) await realSleep(wait);
    }
  },
  // type into the focused field like a person: one key at a time, msPerChar apart (film time)
  async type(text, msPerChar = 90) {
    for (const ch of text) {
      keys.push({ t: now(), key: ch });
      await send('Input.dispatchKeyEvent', { type: 'keyDown', text: ch, key: ch, unmodifiedText: ch });
      await send('Input.dispatchKeyEvent', { type: 'keyUp', key: ch });
      await realSleep(msPerChar * slow * (0.7 + 0.6 * ((ch.charCodeAt(0) * 7) % 10) / 10));
    }
  },
  async press(key = 'Enter') {
    keys.push({ t: now(), key });
    const code = { Enter: 13, Tab: 9, Escape: 27 }[key];
    await send('Input.dispatchKeyEvent', { type: 'keyDown', key, code: key, windowsVirtualKeyCode: code, text: key === 'Enter' ? String.fromCharCode(13) : undefined });
    await send('Input.dispatchKeyEvent', { type: 'keyUp', key, code: key, windowsVirtualKeyCode: code });
  },
  setMouse: p => { mouse = { ...p }; return send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: p.x, y: p.y }); },
  get mouse() { return mouse; },
  async shot(file) {
    const r = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(file, Buffer.from(r.result.data, 'base64'));
  },
  W, H
};

await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 2, mobile: PHONE });
if (PHONE) await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
await send('Page.enable');
await send('Animation.enable');
// rAF gets the slowed clock itself: headless rAF timestamps can lag performance.now() by seconds
const SHIM = `(() => { if (window.__setK) return; let k = 1; const pn = performance.now.bind(performance); const dn = Date.now.bind(Date); let rb = pn(), vb = rb, db = dn(), dvb = db;
  const vnow = () => vb + (pn() - rb) / k; const vdate = () => dvb + (dn() - db) / k;
  window.__setK = nk => { vb = vnow(); rb = pn(); dvb = vdate(); db = dn(); k = nk; };
  performance.now = vnow; Date.now = () => Math.round(vdate());
  const raf = window.requestAnimationFrame.bind(window); window.requestAnimationFrame = cb => raf(() => cb(vnow()));
  const st = window.setTimeout.bind(window); window.setTimeout = (f, d, ...a) => st(f, (d || 0) * k, ...a);
  const si = window.setInterval.bind(window); window.setInterval = (f, d, ...a) => si(f, (d || 0) * k, ...a); })()`;
await send('Page.addScriptToEvaluateOnNewDocument', { source: SHIM });
const take = TAKES[name];
if (!take) throw new Error('no take ' + name + ': ' + Object.keys(TAKES).join(', '));
await take.setup(api);
if (!(await api.eval('!!window.__setK'))) throw new Error('time shim missing: setup must reload the page');
await api.eval(`(window.__setK(${K}), true)`);
// a page the take loads or navigates to during the run starts slow too
await send('Page.addScriptToEvaluateOnNewDocument', { source: `window.__setK && window.__setK(${K})` });
await send('Animation.setPlaybackRate', { playbackRate: 1 / K });
slow = K;
await realSleep(400);
if (!dry) {
  await send('Page.startScreencast', { format: 'jpeg', quality: 95, everyNthFrame: 1, maxWidth: W * 2, maxHeight: H * 2 });
  recording = true;
  // wait for the first frame so the clock exists
  for (let i = 0; i < 100 && t0 === null; i++) await sleep(20);
}
pointer.push({ t: now(), x: mouse.x, y: mouse.y });
await take.run(api);
slow = 1;
await send('Animation.setPlaybackRate', { playbackRate: 1 });
if (!dry) {
  recording = false;
  await send('Page.stopScreencast');
  fs.writeFileSync(path.join(outDir, 'frames.json'), JSON.stringify(frames));
}
fs.writeFileSync(path.join(outDir, 'take.json'), JSON.stringify({ name, w: W, h: H, pointer, marks, keys }));
const dur = frames.length ? frames[frames.length - 1].t : 0;
console.log(`${name}: ${frames.length} frames over ${dur.toFixed(2)}s (${(frames.length / Math.max(dur, 0.01)).toFixed(1)} fps)`);
ws.close();
