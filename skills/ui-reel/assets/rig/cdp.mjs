// Tiny CDP driver for the recording browser (launch.sh, CDP on :9447; CDP_PORT overrides).
// node cdp.mjs targets
// node cdp.mjs open <url>            -> prints targetId
// node cdp.mjs eval <targetId> <js>  -> prints JSON result (awaits promises)
// node cdp.mjs shot <targetId> <file.png> [width] [height]
// node cdp.mjs close <targetId>
import fs from 'node:fs';

const base = `http://127.0.0.1:${process.env.CDP_PORT || 9447}`;
const [cmd, ...args] = process.argv.slice(2);

async function session(targetId) {
  const list = await (await fetch(`${base}/json/list`)).json();
  const target = list.find((t) => t.id === targetId);
  if (!target) throw new Error(`no target ${targetId}`);
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
  let id = 0;
  const pending = new Map();
  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
  };
  const send = (method, params = {}) => new Promise((resolve) => { id += 1; pending.set(id, resolve); ws.send(JSON.stringify({ id, method, params })); });
  return { send, close: () => ws.close() };
}

if (cmd === 'targets') {
  const list = await (await fetch(`${base}/json/list`)).json();
  for (const t of list) console.log(t.id, t.type, t.url.slice(0, 120));
} else if (cmd === 'open') {
  const res = await fetch(`${base}/json/new?${encodeURI(args[0])}`, { method: 'PUT' });
  const t = await res.json();
  console.log(t.id);
} else if (cmd === 'eval') {
  const s = await session(args[0]);
  const r = await s.send('Runtime.evaluate', { expression: args[1], awaitPromise: true, returnByValue: true });
  console.log(JSON.stringify(r.result?.result?.value ?? r.result?.exceptionDetails ?? r, null, 1));
  s.close();
} else if (cmd === 'shot') {
  const s = await session(args[0]);
  if (args[2]) await s.send('Emulation.setDeviceMetricsOverride', { width: Number(args[2]), height: Number(args[3] || 900), deviceScaleFactor: 1, mobile: false });
  const r = await s.send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(args[1], Buffer.from(r.result.data, 'base64'));
  console.log('saved', args[1]);
  s.close();
} else if (cmd === 'close') {
  await fetch(`${base}/json/close/${args[0]}`);
  console.log('closed');
}

// node cdp.mjs watch <targetId> <seconds> <js>  -> runs js, logs console, ws frames, http status for N seconds
if (cmd === 'watch') {
  const list = await (await fetch(`${base}/json/list`)).json();
  const target = list.find((t) => t.id === args[0]);
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve) => { ws.onopen = resolve; });
  let id = 0;
  const send = (method, params = {}) => { id += 1; ws.send(JSON.stringify({ id, method, params })); return id; };
  const out = [];
  const t0 = Date.now();
  const stamp = () => ((Date.now() - t0) / 1000).toFixed(1).padStart(5);
  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    const p = msg.params || {};
    if (msg.method === 'Runtime.consoleAPICalled') out.push(`${stamp()} console.${p.type} ${p.args.map((a) => a.value ?? a.description ?? '').join(' ').slice(0, 400)}`);
    else if (msg.method === 'Network.webSocketFrameSent') out.push(`${stamp()} WS> ${p.response.payloadData.slice(0, 500)}`);
    else if (msg.method === 'Network.webSocketFrameReceived') out.push(`${stamp()} WS< ${p.response.payloadData.slice(0, 500)}`);
    else if (msg.method === 'Network.responseReceived') out.push(`${stamp()} HTTP ${p.response.status} ${p.request?.method || ''} ${p.response.url.slice(0, 160)}`);
    else if (msg.method === 'Network.requestWillBeSent') out.push(`${stamp()} REQ ${p.request.method} ${p.request.url.slice(0, 160)}`);
    else if (msg.method === 'Network.eventSourceMessageReceived') out.push(`${stamp()} SSE ${p.eventName} ${String(p.data).slice(0, 300)}`);
  };
  send('Runtime.enable');
  send('Network.enable');
  await new Promise((r) => setTimeout(r, 300));
  send('Runtime.evaluate', { expression: args[2], awaitPromise: true });
  await new Promise((r) => setTimeout(r, Number(args[1]) * 1000));
  fs.writeFileSync(args[3] || 'watch.log', out.join('\n'));
  console.log(`${out.length} events -> ${args[3] || 'watch.log'}`);
  ws.close();
}
