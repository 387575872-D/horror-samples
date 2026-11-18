import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';

const ROOT = process.argv[2] || 'C:/Users/39288/WorkBuddy/2026-11-17-19-03-56/elevator_horror';
const FPS = Number(process.argv[3] || 20);
const DURATION = Number(process.argv[4] || 60);
const HTML = path.join(ROOT, 'render.html');
const FRAMES = path.join(ROOT, 'frames');
const PORT = 9300 + (process.pid % 500);
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PROFILE = path.join(ROOT, 'edge-profile-' + Date.now());
const VERSION = String(Date.now());

fs.mkdirSync(FRAMES, { recursive: true });

const args = [
  '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
  '--disable-extensions', '--disable-background-networking',
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`,
  '--window-size=540,960', '--force-device-scale-factor=1',
  'file:///' + HTML.replace(/\\/g, '/') + '?capture=1&v=' + VERSION
];
const proc = spawn(EDGE, args, { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));
let target;
for (let i = 0; i < 80; i++) {
  try {
    const res = await fetch(`http://127.0.0.1:${PORT}/json`);
    const list = await res.json();
    target = list.find(x => x.type === 'page' && x.url.includes('render.html') && x.url.includes(VERSION));
    if (target) break;
  } catch {}
  await sleep(250);
}
if (!target) { proc.kill(); throw new Error('无法连接 Edge 调试端口'); }

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
let id = 0;
const pending = new Map();
ws.onmessage = ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
};
function send(method, params = {}) {
  return new Promise(resolve => {
    const n = ++id; pending.set(n, resolve);
    ws.send(JSON.stringify({ id: n, method, params }));
  });
}
await send('Page.enable');
await send('Runtime.enable');
await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });
await send('Emulation.setDeviceMetricsOverride', { width: 540, height: 960, deviceScaleFactor: 1, mobile: false });
for (let i = 0; i < 40; i++) {
  const r = await send('Runtime.evaluate', { expression: 'window.__ready === true', returnByValue: true });
  if (r.result?.result?.value) break;
  await sleep(100);
}

const total = FPS * DURATION;
for (let i = 0; i < total; i++) {
  const t = i / FPS;
  await send('Runtime.evaluate', {
    expression: `window.seek(${t}); new Promise(r=>requestAnimationFrame(()=>r(1)))`,
    awaitPromise: true
  });
  const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  const b64 = shot.result?.data;
  if (!b64) throw new Error('截图失败 @ frame ' + i);
  fs.writeFileSync(path.join(FRAMES, String(i).padStart(4, '0') + '.png'), Buffer.from(b64, 'base64'));
  if (i % 100 === 0) console.log('captured', i, '/', total);
}
console.log('captured', total, '/', total);
try { await send('Browser.close'); } catch {}
ws.close(); proc.kill();
