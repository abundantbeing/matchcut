#!/usr/bin/env python3
"""song_fit.py: measure a song and fit the film to it.

    python song_fit.py song.mp3                      # tempo, beat grid, bar lines, the strongest hits, the energy
    python song_fit.py song.mp3 --tl film/src/tl.json [--moment 15.82]

With a timeline it places the song so its strongest hit lands on the film's biggest moment (`--moment`, default
the loudest hit in tl.json "sfx" between the first shot and the end card), prints the `track_at` / `track_from` for score.json, and
lists every cut, the intro beats and the end card next to the nearest beat so you can move them onto it.
Models only roughly follow the times in a prompt: measure, then cut the picture to the song.

Needs numpy, scipy, soundfile and an ffmpeg (FFMPEG to pick one).
"""
import argparse
import json
import os
import subprocess
import tempfile

import numpy as np
import soundfile as sf
from scipy import signal

ap = argparse.ArgumentParser()
ap.add_argument('song')
ap.add_argument('--tl', help="the film's tl.json")
ap.add_argument('--moment', type=float, help='film time of the biggest moment (default: the loudest sfx hit)')
ap.add_argument('--at', type=float, help='check a placement you chose: the song starts this many seconds into the film')
args = ap.parse_args()

SR = 22050
tmp = os.path.join(tempfile.mkdtemp(), 'song.wav')
subprocess.run([os.environ.get('FFMPEG', 'ffmpeg'), '-y', '-loglevel', 'error', '-i', args.song, '-ac', '1', '-ar', str(SR), tmp], check=True)
x, _ = sf.read(tmp)
dur = len(x) / SR

# onset strength: positive spectral flux in 512-sample hops, low end weighted (kicks and hits carry the grid)
HOP, NFFT = 256, 1024
f, t, Z = signal.stft(x, SR, nperseg=NFFT, noverlap=NFFT - HOP, boundary=None)
mag = np.log1p(np.abs(Z) * 50)
w = np.where(f < 200, 2.0, 1.0)[:, None]
flux = np.maximum(np.diff(mag, axis=1), 0) * w
onset = flux.sum(0)
onset = (onset - np.median(onset)).clip(0)
ot = t[1:]
fps = SR / HOP

# tempo from the onset autocorrelation, 80 to 160 BPM, favouring the strongest periodicity
ac = np.correlate(onset, onset, 'full')[len(onset) - 1:]
lags = np.arange(len(ac)) / fps
ok = (lags > 60 / 160) & (lags < 60 / 80)
period = lags[ok][np.argmax(ac[ok])]
bpm = 60 / period

# beat phase: the offset whose grid collects the most onset strength (the period refined the same way)
def grid_score(phase, step):
    idx = np.round((np.arange(phase, ot[-1], step) - ot[0]) * fps).astype(int)
    idx = idx[(idx >= 0) & (idx < len(onset))]
    return onset[idx].sum()

best = (0, period, 0)
for per in np.linspace(period * 0.99, period * 1.01, 21):
    for ph in np.linspace(0, per, 48, endpoint=False):
        sc = grid_score(ph, per)
        if sc > best[0]:
            best = (sc, per, ph)
_, period, phase = best
bpm = 60 / period
beat_t = np.arange(phase, dur, period)

# the strongest hits: how far the sound jumps over the bed of the second and a half before it (what a drop is)
win = int(0.02 * SR)
lev = 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(win) / win, 'same')) + 1e-9)
step = int(0.01 * SR)
L = lev[::step]
peaks, _ = signal.find_peaks(onset, distance=int(0.2 * fps))
acc = []
for p in peaks:
    tt = float(ot[p])
    if tt < 0.3:
        continue
    i = int(tt / 0.01)
    bed = L[max(0, i - 150):max(1, i - 10)]
    acc.append((float(L[i:i + 6].max() - np.median(bed)), tt))
acc.sort(reverse=True)
hits, accent = [], {}
for a_, tt in acc:
    if all(abs(tt - h) > 0.4 for h in hits):
        hits.append(tt)
        accent[tt] = a_
    if len(hits) >= 8:
        break
hits.sort()
# bars: the beat of four that the strongest hits fall on
def beat_index(tt):
    return int(round((tt - phase) / period))
bar_phase = max(range(4), key=lambda k: sum(accent[h] for h in hits if beat_index(h) % 4 == k))
bars = beat_t[bar_phase::4]

# energy per bar, to find the sections
rms = [float(np.sqrt(np.mean(x[int(a * SR):int(min(dur, a + 4 * period) * SR)] ** 2) + 1e-12)) for a in bars]
db = 20 * np.log10(np.array(rms) + 1e-9)

print(f'{os.path.basename(args.song)}: {dur:.2f} s, {bpm:.1f} BPM (beat {period:.3f} s), first beat {phase:.3f} s')
print('bar lines:', ' '.join(f'{b:.2f}' for b in bars))
print('strongest hits:', ' '.join(f'{h:.2f} (+{accent[h]:.0f} dB)' for h in hits))
print('energy per bar (dB):', ' '.join(f'{d:.0f}' for d in db))
quiet = [f'{bars[i]:.2f}' for i in range(1, len(db)) if db[i] < db.max() - 8]
if quiet:
    print('quiet bars (a breath, an outro):', ' '.join(quiet))

if args.tl:
    tl = json.load(open(args.tl, encoding='utf-8'))
    moment = args.moment if args.moment is not None else tl.get('moment')
    if moment is None:
        first, last = tl['shots'][0]['from'], tl['end']['from']
        cands = [e for e in tl.get('sfx', []) if 'hit' in (e['role'] if isinstance(e['role'], list) else [e['role']]) and first < e['t'] < last]
        moment = max(cands, key=lambda e: e.get('gain', 0.5))['t'] if cands else first
    # put the biggest moment on the nearest bar line (the drop lands on a downbeat); a strong hit just before it is
    # a pickup, which also works: the tool says so, and --at checks either choice
    best = float(bars[np.argmin(np.abs(bars - moment))])
    at = moment - best if args.at is None else args.at
    print(f'\nbiggest moment {moment:.2f} s -> the bar line at {best:.2f} s of the song')
    for h in hits:
        if 0 < best - h <= 0.5:
            print(f'  (a hit at {h:.2f} s leads into it: put the moment there with --at {moment - h:.3f} to land on the hit)')
    print(f'score.json: "track_at": {max(0.0, at):.3f}' + (f', "track_from": {-at:.3f}' if at < 0 else ''))
    film_beats = beat_t + at

    def near(tm):
        b = film_beats[np.argmin(np.abs(film_beats - tm))]
        return b, tm - b

    print('\nfilm events vs the nearest beat (move the ones over 0.06 s):')
    ev = [(f'cut into {s["id"]}', s['from']) for s in tl['shots'][1:]] + [('end card', tl['end']['from'])]
    if tl.get('intro'):
        ev = [('intro lock', tl['intro']['lock']), ('intro cut', tl['intro']['cut'])] + ev
    for name, tm in sorted(ev, key=lambda e: e[1]):
        b, d = near(tm)
        print(f'  {name:<22} {tm:6.2f} s   beat {b:6.2f} s   {"ok" if abs(d) <= 0.06 else f"off by {d:+.2f} s"}')
    song_end = dur + at
    if song_end < tl['total'] - 0.5:
        print(f'  the song ends at {song_end:.2f} s, before the film ({tl["total"]} s): end the film sooner or extend the song')
