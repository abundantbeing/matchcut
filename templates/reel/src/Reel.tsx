// A real-product reel: recorded takes (public/scenes/<take>.mp4 + .json) under a camera that pushes, pans and
// lands, the recorded pointer redrawn crisp on top, one caption per shot, a bloom over every cut, an end card.
// Pure function of the frame; all timing in tl.json (seconds). Footage is 2560x1440 (1280x720 at device scale 2).
import React, { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { AbsoluteFill, Audio, continueRender, delayRender, Freeze, Img, OffthreadVideo, staticFile, useCurrentFrame } from 'remotion';
import tl from './tl.json';
import { TAKES } from './takes';

const FPS = tl.fps;
const W = 1920;
const BG = tl.look.bg;
const DISPLAY = tl.look.display;
const MONO = tl.look.mono;

const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
const inOut = (k: number) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
const out = (k: number) => 1 - Math.pow(1 - k, 4);
const prog = (T: number, from: number, dur: number) => clamp((T - from) / dur);
const bump = (T: number, at: number, half: number) => clamp(1 - Math.abs(T - at) / half);

const FontGate: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [handle] = useState(() => delayRender('fonts'));
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const faces = tl.look.fonts.map(f => new FontFace(f.family, `url(${staticFile(f.file)})`, { weight: String(f.weight) }));
    // a missing font file falls back to the system face instead of stalling the render
    Promise.allSettled(faces.map(f => f.load().then(l => document.fonts.add(l)))).then(() => { setReady(true); continueRender(handle); });
  }, [handle]);
  return ready ? <>{children}</> : null;
};

// the cold open: generated stills (slow push-in about an origin) or clips (played from their first frame)
// dissolve (last item only): instead of a bloom, the still fades out over the first shot for this many seconds,
// masked to a circle of `mask` px about (ox, oy); fit 'contain' keeps a whole subject (a planet) in frame on black
type Open = { file: string; from: number; to: number; ox?: number; oy?: number; zoom?: number[]; speed?: number; dissolve?: number; fit?: 'cover' | 'contain'; mask?: number };
const OPENING: Open[] = (tl as unknown as { opening?: Open[] }).opening ?? [];
const DISSOLVE = OPENING.length ? OPENING[OPENING.length - 1].dissolve ?? 0 : 0;
const Opening: React.FC<{ T: number }> = ({ T }) => {
  const o = OPENING.find(x => T >= x.from && T < x.to + (x === OPENING[OPENING.length - 1] ? DISSOLVE : 0));
  if (!o) return null;
  const k = (T - o.from) / (o.to - o.from);
  const fade = T < o.to ? 1 : 1 - inOut(prog(T, o.to, DISSOLVE));
  const [z0, z1] = o.zoom ?? [1.02, 1.1];
  const scale = Math.exp(lerp(Math.log(z0), Math.log(z1), k <= 1 ? inOut(k) : 1 + (k - 1) * 1.5));
  const origin = `${(o.ox ?? 0.5) * 100}% ${(o.oy ?? 0.5) * 100}%`;
  return (
    <AbsoluteFill style={{ background: fade < 1 ? 'transparent' : '#000', overflow: 'hidden', opacity: fade,
      // while dissolving, only the subject around the origin stays, so the still's edges never show
      ...(fade < 1 ? { maskImage: `radial-gradient(circle ${Math.round(o.mask ?? W * 0.34)}px at ${origin}, #000 72%, transparent 100%)`, WebkitMaskImage: `radial-gradient(circle ${Math.round(o.mask ?? W * 0.34)}px at ${origin}, #000 72%, transparent 100%)` } : {}) }}>
      {o.file.endsWith('.mp4') ? (
        <Freeze frame={Math.round((T - o.from) * FPS * (o.speed ?? 1))}>
          <OffthreadVideo src={staticFile(o.file)} muted style={{ width: W, height: 1080, objectFit: 'cover', transform: `scale(${scale.toFixed(4)})`, transformOrigin: origin }} />
        </Freeze>
      ) : (
        <Img src={staticFile(o.file)} style={{ width: W, height: 1080, objectFit: o.fit ?? 'cover', transform: `scale(${scale.toFixed(4)})`, transformOrigin: origin }} />
      )}
    </AbsoluteFill>
  );
};

// the title intro, all in code: dots stream in and land as the wordmark's letters, the real wordmark resolves over
// them (lock), a cut line slices it in two (cut), then the dots fly off and swirl in toward `into` (the product's first
// shape, in frame pixels) and fade over the first shot while the product's own entrance takes over (handoff)
type Intro = { to: number; handoff: number; image: string; box: number[]; over?: string; under?: string; lock: number; cut: number; line: number[]; into: { cx: number; cy: number; r: number } };
const INTRO = (tl as unknown as { intro?: Intro }).intro;
type Dot = { x: number; y: number; dl: number; sp: number; tw: number; qx: number; qy: number; sp2: number; tw2: number; d2: number; top: boolean; c: string };
const seeded = (s: number) => () => { s |= 0; s = (s + 0x6d2b79f5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const mix = (a: string, b: string, k: number) => { const p = (h: string, i: number) => parseInt(h.slice(1 + i * 2, 3 + i * 2), 16); return `${[0, 1, 2].map(i => Math.round(lerp(p(a, i), p(b, i), k))).join(',')}`; };
const sideOfLine = (x: number, y: number, L: number[]) => (L[2] - L[0]) * (y - L[1]) - (L[3] - L[1]) * (x - L[0]) < 0;
const useIntroDots = (I: Intro | undefined) => {
  const [dots, setDots] = useState<Dot[] | null>(null);
  const [handle] = useState(() => (I ? delayRender('intro dots') : 0));
  useEffect(() => {
    if (!I) return;
    const img = new Image();
    img.onload = () => {
      const [bx, by, bw, bh] = I.box;
      const cv = document.createElement('canvas'); cv.width = bw; cv.height = bh;
      const g = cv.getContext('2d')!; g.drawImage(img, 0, 0, bw, bh);
      const px = g.getImageData(0, 0, bw, bh).data;
      const rnd = seeded(7), pts: Dot[] = [], step = 5;
      for (let y = 0; y < bh; y += step) for (let x = 0; x < bw; x += step) {
        if (px[(y * bw + x) * 4 + 3] < 140) continue;
        const X = bx + x, Y = by + y, u = x / bw, ang = rnd() * Math.PI * 2, rr = I.into.r * Math.sqrt(rnd());
        pts.push({ x: X, y: Y, dl: 0.2 + 0.75 * rnd() * rnd() + 0.3 * u, sp: 1.4 + 2.8 * rnd(), tw: (rnd() - 0.5) * 2.6,
          qx: I.into.cx + rr * Math.cos(ang), qy: I.into.cy + rr * Math.sin(ang), sp2: 1.2 + 2.4 * rnd(), tw2: (rnd() - 0.5) * 2.4, d2: 0.5 * rnd(),
          top: sideOfLine(X, Y, I.line), c: mix('#39E0C3', '#8C9BFF', u) });
      }
      setDots(pts); continueRender(handle);
    };
    img.onerror = () => { setDots([]); continueRender(handle); };
    img.src = staticFile(I.image);
  }, [I, handle]);
  return dots;
};
const STARS = (() => { const r = seeded(3); return Array.from({ length: 140 }, () => ({ x: r() * W, y: r() * 1080, s: 0.8 + r() * 1.6, a: 0.15 + r() * 0.5, f: r() * 6.28 })); })();
const IntroFilm: React.FC<{ T: number; I: Intro; dots: Dot[] }> = ({ T, I, dots }) => {
  const ref = useRef<HTMLCanvasElement>(null);
  const [bx, by, bw, bh] = I.box, L = I.line;
  const cx = bx + bw / 2, cy = by + bh / 2;
  const len = Math.hypot(L[2] - L[0], L[3] - L[1]), ux = (L[2] - L[0]) / len, uy = (L[3] - L[1]) / len;
  // the slice: after the cut the two halves open apart across the line and slip a little along it
  const sk = out(prog(T, I.cut, 0.7)), offX = (uy * 34 - ux * 24) * sk, offY = (-ux * 34 - uy * 24) * sk;
  const release = I.cut + 0.45;
  const handoff = I.to;
  const word = inOut(prog(T, I.lock - 0.1, 0.5)) * (1 - inOut(prog(T, release, 0.4)));
  const creep = 1 + 0.025 * prog(T, I.lock, release - I.lock);
  useLayoutEffect(() => {
    const g = ref.current?.getContext('2d');
    if (!g) return;
    g.clearRect(0, 0, W, 1080);
    const fade = 1 - prog(T, handoff, I.handoff);
    for (const s of STARS) { g.globalAlpha = s.a * (0.7 + 0.3 * Math.sin(T * 1.3 + s.f)) * (1 - prog(T, handoff - 0.3, 0.6)); g.fillStyle = '#cfd8ff'; g.fillRect(s.x, s.y, s.s, s.s); }
    const conv = out(prog(T, release + 0.6, handoff + I.handoff - release - 0.6));
    const flying: [number, number, number][] = [];
    for (const d of dots) {
      let x: number, y: number, a: number, fly = 0;
      if (T < release) {
        const kk = out(prog(T, d.dl, 1.0));
        if (kk <= 0) continue;
        const f = 1 + (1 - kk) * d.sp, an = (1 - kk) * d.tw, dx = (d.x - cx) * f, dy = (d.y - cy) * f;
        x = cx + dx * Math.cos(an) - dy * Math.sin(an); y = cy + dx * Math.sin(an) + dy * Math.cos(an);
        a = kk * (1 - 0.85 * word); fly = kk < 1 ? Math.sin(kk * Math.PI) : 0;
        // the lock: a brief flare running left to right through the letters
        a += 0.9 * bump(T, I.lock - 0.15 + 0.3 * ((d.x - bx) / bw), 0.12);
      } else {
        const sx = d.x + (d.top ? 1 : -1) * offX, sy = d.y + (d.top ? 1 : -1) * offY;
        const kb = inOut(prog(T, release + d.d2, 1.3));
        const F = 1 + d.sp2 * (1 - conv), an = d.tw2 * (1 - conv), dx = (d.qx - I.into.cx) * F, dy = (d.qy - I.into.cy) * F;
        const ex = I.into.cx + dx * Math.cos(an) - dy * Math.sin(an), ey = I.into.cy + dx * Math.sin(an) + dy * Math.cos(an);
        x = lerp(sx, ex, kb); y = lerp(sy, ey, kb);
        a = (1 - 0.85 * word) * fade; fly = Math.sin(kb * Math.PI);
      }
      g.globalAlpha = clamp(a); g.fillStyle = `rgb(${d.c})`; g.fillRect(x - 1.3, y - 1.3, 2.6, 2.6);
      if (fly > 0.02) flying.push([x, y, fly * (T < release ? 1 : fade)]);
    }
    g.globalCompositeOperation = 'lighter';
    for (const [x, y, f] of flying) { g.globalAlpha = 0.9 * f; g.fillStyle = 'rgb(170,255,235)'; g.fillRect(x - 1.4, y - 1.4, 2.8, 2.8); }
    // the cut line: drawn across the frame along the wordmark's own slash, flashing as the word splits
    const draw = out(prog(T, I.cut - 0.35, 0.35)), flash = bump(T, I.cut, 0.3);
    if (draw > 0 && T < release + 0.4) {
      const ext = W * 0.8, x0 = L[0] - ux * ext, y0 = L[1] - uy * ext, x1 = lerp(x0, L[2] + ux * ext, draw), y1 = lerp(y0, L[3] + uy * ext, draw);
      g.globalAlpha = (0.55 + 0.45 * flash) * (1 - prog(T, release, 0.4));
      g.strokeStyle = 'rgb(160,240,255)'; g.lineWidth = 2 + 6 * flash; g.shadowColor = 'rgb(57,224,195)'; g.shadowBlur = 24;
      g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); g.shadowBlur = 0;
    }
    g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1;
  }, [T, dots, I, bx, bw, cx, cy, release, handoff, offX, offY, word, L]);
  const clip = (top: boolean) => {
    // the part of the wordmark box on one side of the cut line, in the box's own pixels
    const at = (x: number) => L[1] - by + ((L[3] - L[1]) / (L[2] - L[0])) * (x + bx - L[0]);
    const l = at(-bw), r = at(2 * bw);
    return top ? `polygon(-100% -100%, 200% -100%, 200% ${r}px, -100% ${l}px)` : `polygon(-100% ${l}px, 200% ${r}px, 200% 300%, -100% 300%)`;
  };
  const textIn = out(prog(T, 0.9, 0.8)), textOut = inOut(prog(T, I.cut - 0.1, 0.35));
  const subIn = out(prog(T, I.lock + 0.4, 0.7));
  return (
    <AbsoluteFill style={{ background: `rgba(${mix(BG, BG, 0)},${(1 - inOut(prog(T, handoff, 0.6))).toFixed(3)})` }}>
      <canvas ref={ref} width={W} height={1080} style={{ position: 'absolute', inset: 0 }} />
      {word > 0.001 && [true, false].map(top => (
        <Img key={String(top)} src={staticFile(I.image)} style={{ position: 'absolute', left: bx, top: by, width: bw, height: bh, objectFit: 'contain', clipPath: clip(top), opacity: word,
          transform: `translate(${((top ? 1 : -1) * offX).toFixed(2)}px, ${((top ? 1 : -1) * offY).toFixed(2)}px) scale(${(creep * (0.97 + 0.03 * word)).toFixed(4)})`,
          filter: `blur(${((1 - word) * 14).toFixed(1)}px) drop-shadow(0 0 ${(18 * bump(T, I.lock + 0.1, 0.4)).toFixed(1)}px rgba(57,224,195,.9))` }} />
      ))}
      {I.over && <div style={{ position: 'absolute', width: W, top: by - 92, textAlign: 'center', fontFamily: MONO, fontWeight: 700, fontSize: 30, color: '#C9D2F5',
        letterSpacing: `${(0.5 + (1 - textIn) * 0.3).toFixed(3)}em`, opacity: textIn * (1 - textOut), filter: `blur(${((1 - textIn) * 8 + textOut * 8).toFixed(1)}px)` }}>{I.over}</div>}
      {I.under && <div style={{ position: 'absolute', width: W, top: by + bh + 58, textAlign: 'center', fontFamily: MONO, fontSize: 30, color: '#EEF1FF', letterSpacing: '0.12em',
        opacity: subIn * (1 - textOut), clipPath: `inset(-20% ${((1 - subIn) * 50).toFixed(1)}% -20% ${((1 - subIn) * 50).toFixed(1)}%)`, filter: `blur(${(textOut * 8).toFixed(1)}px)` }}>{I.under}</div>}
    </AbsoluteFill>
  );
};
const IntroLayer: React.FC<{ T: number }> = ({ T }) => {
  const dots = useIntroDots(INTRO);
  if (!INTRO || !dots || T >= INTRO.to + INTRO.handoff) return null;
  return <IntroFilm T={T} I={INTRO} dots={dots} />;
};

// every cut hides inside a short blur and a bloom of light
const CUTS = [...(OPENING.length && !DISSOLVE ? [tl.shots[0].from] : []), ...tl.shots.slice(1).map(s => s.from)];
const SOFT = OPENING.slice(1).map(o => o.from);
const Bloom: React.FC<{ T: number }> = ({ T }) => {
  let a = 0;
  for (const c of CUTS) a = Math.max(a, Math.pow(bump(T, c, c === tl.shots[0].from && OPENING.length ? 0.3 : 0.2), 1.6));
  for (const c of SOFT) a = Math.max(a, 0.6 * Math.pow(bump(T, c, 0.12), 1.4));
  return a > 0.001 ? <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 48%, #FFFFFF 0%, ${tl.look.glow} 60%, ${BG} 100%)`, opacity: a }} /> : null;
};
const cutBlur = (T: number) => { let b = 0; for (const c of CUTS) b = Math.max(b, bump(T, c, 0.22)); return 34 * b * b; };

type Key = { T: number; s: number; fx: number; fy: number; sx: number; sy: number };
// s: zoom (1 = the 1280x720 page fills the frame); (fx, fy): page point in footage pixels; (sx, sy): where it sits on screen
const camAt = (keys: Key[], T: number): Key => {
  if (T <= keys[0].T) return keys[0];
  for (let i = 1; i < keys.length; i++) {
    if (T <= keys[i].T) {
      const a = keys[i - 1], b = keys[i];
      const k = inOut(prog(T, a.T, b.T - a.T));
      return { T, s: Math.exp(lerp(Math.log(a.s), Math.log(b.s), k)), fx: lerp(a.fx, b.fx, k), fy: lerp(a.fy, b.fy, k), sx: lerp(a.sx, b.sx, k), sy: lerp(a.sy, b.sy, k) };
    }
  }
  return keys[keys.length - 1];
};
const pointerAt = (take: string, t: number) => {
  const p = TAKES[take]?.pointer;
  if (!p?.length) return null;
  if (t <= p[0].t) return { x: p[0].x, y: p[0].y, press: 0 };
  let lo = 0, hi = p.length - 1;
  while (lo < hi - 1) { const mid = (lo + hi) >> 1; if (p[mid].t <= t) lo = mid; else hi = mid; }
  const a = p[lo], b = p[hi];
  const k = b.t > a.t ? clamp((t - a.t) / (b.t - a.t)) : 0;
  let press = 0;
  for (const q of p) if (q.down && t >= q.t) press = Math.max(press, 1 - clamp((t - q.t) / 0.45));
  return { x: lerp(a.x, b.x, k), y: lerp(a.y, b.y, k), press };
};
const Pointer: React.FC<{ x: number; y: number; press: number }> = ({ x, y, press }) => (
  <>
    {press > 0.01 && <div style={{ position: 'absolute', left: x * 2 - 60, top: y * 2 - 60, width: 120, height: 120, borderRadius: 60, border: '5px solid rgba(220,230,255,.9)', opacity: press, transform: `scale(${0.35 + (1 - press) * 0.9})` }} />}
    <svg width={56} height={56} viewBox="0 0 24 24" style={{ position: 'absolute', left: x * 2 - 6, top: y * 2 - 4, filter: 'drop-shadow(0 4px 6px rgba(0,0,0,.55))' }}>
      <path d="M4 2.5 L4 19 L8.6 14.9 L11.6 21.6 L14.4 20.3 L11.5 13.8 L17.6 13.6 Z" fill="#FFFFFF" stroke="#0A0B2A" strokeWidth={1.3} strokeLinejoin="round" />
    </svg>
  </>
);
const Shot: React.FC<{ T: number; shot: (typeof tl.shots)[number] }> = ({ T, shot }) => {
  const t = shot.t0 + (T - shot.from) * shot.speed;
  const frame = Math.round(clamp(t * FPS, 0, shot.frames - 1));
  const c = camAt(shot.cam as Key[], T);
  const k = 0.75 * c.s;
  const p = pointerAt(shot.take, t);
  const blur = cutBlur(T);
  // a phone take (VIEW=phone, 780 x 1688 footage) stands upright in a phone-shaped frame, rising a little as it lands
  if ((shot as { phone?: boolean }).phone) {
    const rise = 1 - out(prog(T, shot.from, 0.9));
    return (
      <AbsoluteFill style={{ background: BG, filter: blur > 0.3 ? `blur(${blur.toFixed(1)}px)` : undefined }}>
        <div style={{ position: 'absolute', left: W / 2 - 212, top: 60 + rise * 60, width: 424, height: 918, borderRadius: 54, overflow: 'hidden', border: '10px solid #0B0B10' }}>
          <Freeze frame={frame}><OffthreadVideo src={staticFile(`scenes/${shot.take}.mp4`)} muted style={{ width: 404, height: 874, objectFit: 'cover' }} /></Freeze>
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ background: BG, filter: blur > 0.3 ? `blur(${blur.toFixed(1)}px)` : undefined }}>
      <div style={{ position: 'absolute', width: 2560, height: 1440, transformOrigin: '0 0', transform: `translate(${(c.sx - c.fx * k).toFixed(2)}px, ${(c.sy - c.fy * k).toFixed(2)}px) scale(${k.toFixed(5)})` }}>
        <Freeze frame={frame}><OffthreadVideo src={staticFile(`scenes/${shot.take}.mp4`)} muted style={{ width: 2560, height: 1440 }} /></Freeze>
        {p && <Pointer {...p} />}
      </div>
    </AbsoluteFill>
  );
};

// captions rotate three voices: rise, track (letter-spacing settles), wipe
const Line: React.FC<{ T: number; line: (typeof tl.lines)[number] }> = ({ T, line }) => {
  if (T < line.from - 0.02 || T > line.to + 0.4) return null;
  const a = out(prog(T, line.from, 0.55));
  const z = inOut(prog(T, line.to, 0.35));
  const o = a * (1 - z);
  const base: React.CSSProperties = { position: 'absolute', left: 0, width: W, top: 978, textAlign: 'center', fontFamily: DISPLAY, fontWeight: 700, fontSize: 62, lineHeight: 1, color: '#FFFFFF', whiteSpace: 'nowrap', textShadow: '0 2px 18px rgba(3,4,20,.95)' };
  const v = line.voice === 'rise' ? { opacity: o, transform: `translateY(${(1 - a) * 34 - z * 14}px)`, filter: `blur(${((1 - a) * 10 + z * 8).toFixed(1)}px)` }
    : line.voice === 'track' ? { opacity: o, letterSpacing: `${(0.05 + (1 - a) * 0.22).toFixed(3)}em`, filter: `blur(${((1 - a) * 6 + z * 8).toFixed(1)}px)` }
    : { opacity: 1 - z, clipPath: `inset(-20% ${((1 - a) * 100).toFixed(1)}% -20% 0)`, filter: `blur(${(z * 8).toFixed(1)}px)` };
  return <div style={{ ...base, ...v }}>{line.text}</div>;
};
const Scrim: React.FC<{ T: number }> = ({ T }) => (
  <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(4,5,22,0) 76%, rgba(4,5,22,.8) 88%, rgba(4,5,22,.96) 100%)', opacity: prog(T, tl.shots[0].from + 0.6, 0.8) * (1 - prog(T, tl.end.from - 0.4, 0.4)) }} />
);

const EndCard: React.FC<{ T: number }> = ({ T }) => {
  const E = tl.end;
  const a = out(prog(T, E.from, 0.9)), b = out(prog(T, E.from + 1.2, 0.7));
  const creep = 1 + 0.035 * prog(T, E.from, E.to - E.from);
  return (
    <AbsoluteFill style={{ background: BG, transform: `scale(${creep.toFixed(5)})`, opacity: 1 - inOut(prog(T, E.to - 0.9, 0.9)) }}>
      {(E as { mark?: string }).mark && <Img src={staticFile((E as { mark?: string }).mark!)} style={{ position: 'absolute', left: W / 2 - 130, top: 110, width: 260, height: 260, objectFit: 'contain', opacity: a, transform: `scale(${(0.9 + 0.1 * a).toFixed(4)}) rotate(${((1 - a) * -6).toFixed(2)}deg)`, filter: `blur(${((1 - a) * 12).toFixed(1)}px)` }} />}
      {(E as { wordmark?: string }).wordmark ? (
        <Img src={staticFile((E as { wordmark?: string }).wordmark!)} style={{ position: 'absolute', left: W / 2 - 520, top: 400, width: 1040, height: 225, objectFit: 'contain', opacity: a, filter: `blur(${((1 - a) * 16).toFixed(1)}px)`, transform: `scale(${(0.94 + 0.06 * a).toFixed(4)})` }} />
      ) : (
      <div style={{ position: 'absolute', width: W, top: 372, textAlign: 'center', fontFamily: DISPLAY, fontWeight: 700, fontSize: 200, color: '#FFFFFF', letterSpacing: `${(0.02 + (1 - a) * 0.16).toFixed(3)}em`, opacity: a, filter: `blur(${((1 - a) * 16).toFixed(1)}px)` }}>{E.name}</div>
      )}
      <div style={{ position: 'absolute', width: W, top: 668, textAlign: 'center', opacity: b, transform: `translateY(${(1 - b) * 20}px)`, fontFamily: MONO, fontSize: 32, color: '#EEF1FF' }}>{E.install}</div>
      <div style={{ position: 'absolute', width: W, top: 790, textAlign: 'center', fontFamily: MONO, fontSize: 20, letterSpacing: '0.42em', color: '#B9C2E8', opacity: b * 0.9 }}>{E.fact}</div>
    </AbsoluteFill>
  );
};

export const Reel: React.FC = () => {
  const T = useCurrentFrame() / FPS;
  const shot = tl.shots.find(s => T >= s.from && T < s.to);
  // letterbox bars carried over from a cold open, opening on the first shot
  const bars = tl.bars * (1 - out(prog(T, tl.shots[0].from, 0.9)));
  return (
    <FontGate>
      <AbsoluteFill style={{ background: BG }}>
        {T < tl.shots[0].from && <Opening T={T} />}
        {shot && <Shot T={T} shot={shot} />}
        {DISSOLVE > 0 && T >= tl.shots[0].from && T < tl.shots[0].from + DISSOLVE && <Opening T={T} />}
        <IntroLayer T={T} />
        {T >= tl.end.from && <EndCard T={T} />}
        <Scrim T={T} />
        {tl.lines.map(l => <Line key={l.text} T={T} line={l} />)}
        {bars > 0.5 && <><div style={{ position: 'absolute', top: 0, width: W, height: bars, background: '#000' }} /><div style={{ position: 'absolute', bottom: 0, width: W, height: bars, background: '#000' }} /></>}
        <Bloom T={T} />
        {tl.audio && <Audio src={staticFile(tl.audio)} />}
      </AbsoluteFill>
    </FontGate>
  );
};
