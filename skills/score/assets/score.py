#!/usr/bin/env python3
"""score.py: the film's soundtrack, cut to its own timeline.

    python score.py score.json [--out public/audio/soundtrack.wav]

A. The code band (the default: nothing to sign up for). score.json says the key, tempo, palette and the sections
(in seconds, from the film's tl.json), plus the moments that need a hit: cuts, a stop before the reveal, slams, the
end card. Every section has an energy level:
  0  pad and drone only           (an intro, a held title)
  1  + the plucked or keyed riff  (the first product shot)
  2  + bass and a light kit       (the body of the film)
  3  + full kit and the lead      (the payoff)
B. A produced song: score.json "track" (any file ffmpeg reads) placed at "track_at" seconds of the film, from
"track_from" seconds into the song, shaped by "track_curve" [[seconds, dB], ...]. If the file is missing, the code
band plays instead, so a film always has music.
Effects (clicks, whooshes, a land) are listed in score.json "fx" with their own files, scaled by "fx_gain"; cues.py
writes that list, from the bundled kit or yours. A kit of licensed recordings stays out of public repos.

Needs numpy, scipy, soundfile (and ffmpeg for a track: FFMPEG to pick one).
"""
import argparse
import json
import os
import subprocess
import tempfile

import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument('score')
ap.add_argument('--out', default='public/audio/soundtrack.wav')
args = ap.parse_args()
S = json.load(open(args.score, encoding='utf-8'))
base = os.path.dirname(os.path.abspath(args.score))

TOTAL = S['total']
N = int(SR * TOTAL)
RNG = np.random.default_rng(S.get('seed', 7))
BPM = S.get('bpm', 120)
BEAT = 60 / BPM
BAR = 4 * BEAT
MODES = {'ionian': [0, 2, 4, 5, 7, 9, 11], 'dorian': [0, 2, 3, 5, 7, 9, 10], 'phrygian': [0, 1, 3, 5, 7, 8, 10],
         'lydian': [0, 2, 4, 6, 7, 9, 11], 'mixolydian': [0, 2, 4, 5, 7, 9, 10], 'aeolian': [0, 2, 3, 5, 7, 8, 10]}
NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
ROOT = 48 + NOTE[S.get('key', 'E')]
SCALE = MODES[S.get('mode', 'dorian')]
PALETTE = S.get('palette', 'lyre')  # lyre (plucked), keys (FM piano), marimba, glass (bells)
mix = {k: np.zeros((N, 2)) for k in ('music', 'drums', 'fx')}


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def deg(d, octave=0):
    """scale degree d (0-based, may exceed 6) to a MIDI note"""
    return ROOT + 12 * (octave + d // 7) + SCALE[d % 7]


def put(bus, x, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= N or i < 0:
        return
    x = x[: N - i]
    if x.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        mix[bus][i:i + len(x), 0] += x * gain * l * 1.414
        mix[bus][i:i + len(x), 1] += x * gain * r * 1.414
    else:
        mix[bus][i:i + len(x)] += x * gain


def env(n, a=0.005, r=0.1):
    e = np.ones(n)
    na, nr = max(1, min(n, int(a * SR))), max(1, min(n, int(r * SR)))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, min(fc, SR / 2 - 100) / (SR / 2), 'low', output='sos'), x, axis=0)


def hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc / (SR / 2), 'high', output='sos'), x, axis=0)


# ---------- instruments ----------
def pluck(m, dur=1.2, bright=0.6):
    f, n = mtof(m), int(dur * SR)
    p = int(SR / f)
    buf = lp(RNG.uniform(-1, 1, p), 1500 + 6000 * bright)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out * env(n, 0.001, 0.05)


def fm_keys(m, dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    return np.sin(2 * np.pi * f * t + 1.4 * np.exp(-t * 4) * np.sin(2 * np.pi * f * t)) * np.exp(-t * 2.2) * env(n, 0.003, 0.08)


def marimba(m, dur=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 20)) * np.exp(-t * 7) * env(n, 0.001, 0.03)


def bell(m, dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    return np.sin(2 * np.pi * f * t + 2.2 * np.exp(-t * 5) * np.sin(2 * np.pi * f * 3.01 * t)) * np.exp(-t * 3.2) * env(n, 0.002, 0.05)


VOICE = {'lyre': pluck, 'keys': fm_keys, 'marimba': marimba, 'glass': bell}[PALETTE]


def pad(notes, dur, fc=1400):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for m in notes:
        for d, pan in ((-0.07, -0.7), (0.0, 0.0), (0.08, 0.7)):
            f = mtof(m + d)
            saw = sum(np.sin(2 * np.pi * f * k * t + RNG.uniform(0, 6.28)) / k for k in range(1, 9))
            out[:, 0] += saw * np.cos((pan + 1) * np.pi / 4)
            out[:, 1] += saw * np.sin((pan + 1) * np.pi / 4)
    return lp(out, fc) * env(n, min(1.2, dur * 0.3), min(1.5, dur * 0.35))[:, None] / (len(notes) * 3)


def sub(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * mtof(m) * t) + 0.25 * np.sin(4 * np.pi * mtof(m) * t)) * env(n, 0.01, 0.08)


def kick(big=False):
    n = int((0.7 if big else 0.32) * SR)
    t = np.arange(n) / SR
    f = (38 if big else 46) + (150 if big else 120) * np.exp(-t * (18 if big else 30))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (5 if big else 11))
    if big:
        x += lp(RNG.normal(0, 1, n), 900) * np.exp(-t * 14) * 0.6
    return x


def clap():
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    x = hp(lp(RNG.normal(0, 1, n), 5200), 900)
    e = sum(np.exp(-np.maximum(t - d, 0) * 60) * (t >= d) for d in (0, 0.011, 0.023)) + np.exp(-t * 22) * 0.6
    return x * e * 0.5


def hat(open_=False):
    n = int((0.16 if open_ else 0.045) * SR)
    t = np.arange(n) / SR
    return hp(RNG.normal(0, 1, n), 7000) * np.exp(-t * (22 if open_ else 90)) * 0.6


def riser(dur):
    n = int(dur * SR)
    k = np.linspace(0, 1, n)
    x = RNG.normal(0, 1, n)
    out = np.zeros(n)
    step = 2048
    for i in range(0, n, step):
        out[i:i + step] = lp(x[max(0, i - step):i + step], 300 + 9000 * k[i] ** 2)[-len(x[i:i + step]):]
    tone = np.sin(2 * np.pi * np.cumsum(110 * 2 ** (k * 2)) / SR) * 0.3
    return (out * 0.5 + tone) * k ** 2.2


# ---------- the arrangement ----------
# a progression is scale degrees of chord roots, one per bar; chords are stacked thirds in the mode
PROG = S.get('progression', [0, 3, 5, 4])
LEAD = [(0, 4), (1, 6), (1.5, 7), (2.5, 9), (4, 8), (5, 7), (5.5, 6), (6.5, 4)]  # (beat, degree) over two bars


def chord(d, octave=0):
    return [deg(d, octave), deg(d + 2, octave), deg(d + 4, octave)]


def section(a, b, energy):
    bars = max(1, int(round((b - a) / BAR)))
    for k in range(bars):
        t = a + k * BAR
        if t >= b - 0.05:
            break
        d = PROG[k % len(PROG)]
        put('music', pad(chord(d, 0), min(BAR * 1.05, b - t + 0.6), 900 + 500 * energy), t, 0.42)
        if energy == 0:
            put('music', pad([deg(d, -2)], min(BAR, b - t + 0.6), 500), t, 0.4)
            continue
        notes = chord(d, 1) + [deg(d + 7, 1)]
        for s in range(8):  # eighths
            m = notes[(0, 2, 1, 2, 3, 2, 1, 0)[s]]
            put('music', VOICE(m, 1.1), t + s * BEAT / 2 + (0.01 if s % 2 else 0), 0.5 * (1 if s % 4 == 0 else 0.72), pan=(-0.35 if s % 2 else 0.35))
        if energy >= 2:
            for beat, dur in ((0, 0.7), (1.5, 0.4), (2.5, 0.6), (3.5, 0.3)):
                put('music', sub(deg(d, -1), dur * BEAT), t + beat * BEAT, 0.38)
            put('drums', kick(), t, 0.85)
            put('drums', kick(), t + 2.5 * BEAT, 0.55)
            for s in range(8):
                put('drums', hat(s == 7), t + s * BEAT / 2, (0.4 if s % 2 else 0.65) * (0.6 if energy == 2 else 1), pan=0.2)
        if energy >= 3:
            put('drums', clap(), t + 2 * BEAT, 0.8)
            if k % 2 == 0:
                for beat, dg in LEAD:
                    put('music', bell(deg(dg, 2), 1.1), t + beat * BEAT, 0.3, pan=0.15)


def resolve(at):  # the resolve rings out: a wide chord and a rolled arpeggio
    put('music', pad(chord(0, -1) + chord(0, 0), TOTAL - at + 0.5, 2200), at, 0.6)
    for i, dg in enumerate((0, 2, 4, 7, 9, 11, 14)):
        put('music', VOICE(deg(dg, 1), 3.0), at + i * 0.09, 0.4, pan=(-0.6 + i * 0.2))


def code_band():
    for sec in S.get('sections', [{'from': 0, 'to': TOTAL, 'energy': 1}]):
        section(sec['from'], sec['to'], sec['energy'])
    for h in S.get('hits', []):  # a time, or [time, gain] for a softer hit
        t, g = (h[0], h[1]) if isinstance(h, list) else (h, 1.0)
        put('drums', kick(True), t, g)
    for r in S.get('risers', []):
        put('fx', riser(r['dur']), r['to'] - r['dur'], 0.5)
    for t in S.get('stops', []):  # silence just before a reveal, then the hit
        i0, i1 = int((t - 0.22) * SR), int(t * SR)
        for b in mix:
            mix[b][i0:i1] *= (np.linspace(1, 0, i1 - i0) ** 2)[:, None]
        put('drums', kick(True), t, 1.3)
    if 'end' in S:  # the end card lands; with a `finale` the band plays on and the last chord lands there instead
        put('drums', kick(True), S['end'], 1.2)
        if 'finale' not in S:
            resolve(S['end'])
    if 'finale' in S:
        i0, i1 = int((S['finale'] - 0.18) * SR), int(S['finale'] * SR)
        for b in ('music', 'drums'):
            mix[b][i0:i1] *= (np.linspace(1, 0, i1 - i0) ** 2)[:, None]
            mix[b][i1:] = 0
        put('drums', kick(True), S['finale'], 1.25)
        resolve(S['finale'])


TRACK = S.get('track') and os.path.join(base, S['track'])
if TRACK and not os.path.exists(TRACK):
    print(f'{S["track"]} not found: playing the code band instead')
    TRACK = None
if TRACK:
    tmp = os.path.join(tempfile.mkdtemp(), 'track.wav')
    subprocess.run([os.environ.get('FFMPEG', 'ffmpeg'), '-y', '-loglevel', 'error', '-ss', str(S.get('track_from', 0)),
                    '-i', TRACK, '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', tmp], check=True)
    x, _ = sf.read(tmp, always_2d=True)
    put('music', x * S.get('track_gain', 1.0), S.get('track_at', 0))
    if S.get('track_curve'):  # [[seconds, dB], ...] over the film: lift a quiet outro, dip under a voice
        pts = np.array(S['track_curve'], dtype=float)
        mix['music'] *= (10 ** (np.interp(np.arange(N) / SR, pts[:, 0], pts[:, 1]) / 20))[:, None]
else:
    code_band()

missing = 0
for f in S.get('fx', []):  # recorded effects: {"file": "kit/click.wav", "t": 12.3, "gain": 0.5}
    path = os.path.join(base, f['file'])
    if not os.path.exists(path):
        missing += 1
        continue
    x, sr = sf.read(path, always_2d=True)
    if sr != SR:
        x = signal.resample(x, int(len(x) * SR / sr))
    put('fx', x if x.shape[1] == 2 else np.repeat(x, 2, axis=1), f['t'], f.get('gain', 0.6) * S.get('fx_gain', 1.0))


if missing:
    print(f'{missing} effect files not found (no kit?): the music renders without them')

# ---------- space and master ----------
def reverb(x, secs=2.2, wet=0.22):
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = np.stack([RNG.normal(0, 1, n), RNG.normal(0, 1, n)], 1) * np.exp(-t * 3.2)[:, None]
    ir = hp(lp(ir, 6000), 250)
    ir /= np.sqrt((ir ** 2).sum(0)).max()
    return x + np.stack([signal.fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in (0, 1)], 1) * wet


music = mix['music'] if TRACK else reverb(mix['music'], 2.6, 0.3)
out = music * 0.9 + reverb(lp(mix['drums'], 9000), 1.2, 0.1) * 0.8 + mix['fx'] * 0.9
out = hp(out, 28)
fade = int(S.get('fade', 1.2) * SR)
out[-fade:] *= (np.linspace(1, 0, fade) ** 2)[:, None]
loud = out[np.abs(out).max(1) > 0.01]
out *= 10 ** (S.get('rms_db', -18) / 20) / np.sqrt((loud ** 2).mean())
ceil = 10 ** (-1.5 / 20)
out = np.clip(np.tanh(out / ceil * 0.9) * ceil / np.tanh(0.9), -ceil, ceil)
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
sf.write(args.out, out, SR, subtype='PCM_24')
print(args.out, round(len(out) / SR, 2), 's, peak', round(20 * np.log10(np.abs(out).max()), 2), 'dBFS, rms', round(10 * np.log10((out ** 2).mean()), 2), 'dB')
