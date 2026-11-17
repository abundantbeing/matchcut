// Checks src/tl.json for edits that waste a cut. Run by `npm run check`; exits 1 on a problem.
//
// cut, then travel: a shot that opens on one place and then pans or zooms somewhere else in its first moments.
//   The cut's whoosh and bloom land on nothing and the viewer waits for the subject. Open the shot already framed
//   on what it is about (its first camera key), and start it (t0) just before that thing moves.
// a caption too short to read: it lands in about 0.3 s, then needs 0.8 s held, longer when it has more words
//   (0.18 s a word: a glance, not a sentence). Hold it longer or cut words; never speed the reader up.
// heroes: the 3 to 5 moments that land exactly on the music with the film's biggest sounds. More than five and
//   none of them is special. Without the key, the match cut, the "moment" and the end card are the heroes.
// overlapping shots, captions outside the film, an end card before the last shot ends: plain timing mistakes.
import fs from 'node:fs';

const tl = JSON.parse(fs.readFileSync(new URL('./src/tl.json', import.meta.url), 'utf8'));
const problems = [];
const PAN = 300; // footage pixels of focus travel
const ZOOM = 1.6; // zoom ratio
const SLOW = 0.6; // seconds: a faster move reads as a snap, not a wait
const LANDS = 0.3, HOLD = 0.8, PER_WORD = 0.18; // caption: seconds to land, least held, held per word

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
for (const l of tl.lines ?? []) {
  if (l.from < 0 || l.to > tl.total || l.to <= l.from) { problems.push(`caption "${l.text}" has bad times`); continue; }
  const words = l.text.trim().split(/\s+/).length, need = LANDS + Math.max(HOLD, PER_WORD * words);
  if (l.to - l.from < need - 1e-6)
    problems.push(`caption "${l.text}": on screen ${(l.to - l.from).toFixed(2)} s, needs ${need.toFixed(2)} s to read (${words} words); hold it longer or cut words`);
}
const heroes = tl.heroes ?? [tl.opening?.length ? tl.shots[0].from : null, tl.moment, tl.end?.from].filter(t => t != null);
if (heroes.length > 5) problems.push(`heroes: ${heroes.length} moments; pick the 3 to 5 that matter, the rest of the cuts are free`);
for (const h of heroes) if (!(h >= 0 && h <= tl.total)) problems.push(`hero at ${h} s is outside the film (0 to ${tl.total} s)`);

if (problems.length) { console.error(problems.map(p => '  ' + p).join('\n')); process.exit(1); }
console.log(`tl.json ok: ${tl.shots.length} shots, no cut lands on a camera move, every caption reads, heroes at ${heroes.map(h => h + ' s').join(', ') || 'none'}`);
