// Checks src/tl.json for edits that waste a cut. Run by `npm run check`; exits 1 on a problem.
//
// cut, then travel: a shot that opens on one place and then pans or zooms somewhere else in its first moments.
//   The cut's whoosh and bloom land on nothing and the viewer waits for the subject. Open the shot already framed
//   on what it is about (its first camera key), and start it (t0) just before that thing moves.
// overlapping shots, captions outside the film, an end card before the last shot ends: plain timing mistakes.
import fs from 'node:fs';

const tl = JSON.parse(fs.readFileSync(new URL('./src/tl.json', import.meta.url), 'utf8'));
const problems = [];
const PAN = 300; // footage pixels of focus travel
const ZOOM = 1.6; // zoom ratio
const SLOW = 0.6; // seconds: a faster move reads as a snap, not a wait

tl.shots.forEach((s, i) => {
  const next = tl.shots[i + 1];
  if (next && next.from < s.to - 1e-6) problems.push(`${s.id}: ends at ${s.to} s but ${next.id} starts at ${next.from} s`);
  if (s.to <= s.from) problems.push(`${s.id}: ends before it starts`);
  if (i === 0 || !s.cam?.length) return;
  // only the first move after the cut: later moves follow the action
  const [a, b] = s.cam;
  if (b && b.T - s.from <= 1.5) {
    const pan = Math.hypot(b.fx - a.fx, b.fy - a.fy), zoom = Math.max(b.s / a.s, a.s / b.s), dur = b.T - a.T;
    if ((pan > PAN || zoom > ZOOM) && dur > SLOW)
      problems.push(`${s.id}: cut, then travel - the camera moves ${Math.round(pan)} px and ${zoom.toFixed(2)}x over ${dur.toFixed(2)} s right after the cut at ${s.from} s; open the shot framed on its subject`);
  }
});
const lastShot = tl.shots[tl.shots.length - 1];
if (tl.end && tl.end.from < lastShot.to - 1e-6) problems.push(`end card at ${tl.end.from} s starts before ${lastShot.id} ends (${lastShot.to} s)`);
for (const l of tl.lines ?? []) if (l.from < 0 || l.to > tl.total || l.to <= l.from) problems.push(`caption "${l.text}" has bad times`);

if (problems.length) { console.error(problems.map(p => '  ' + p).join('\n')); process.exit(1); }
console.log(`tl.json ok: ${tl.shots.length} shots, no cut lands on a camera move`);
