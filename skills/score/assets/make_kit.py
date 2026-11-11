#!/usr/bin/env python3
"""make_kit.py: write a film's sound-effect kit in code, nothing to download or license.

    python make_kit.py kit/ [--seed 7] [--roles click,key,whoosh-short]

Writes WAVs named by role, several takes each, in the shape cues.py places them:
  click_N        a crisp UI click (a press)           key_N         a soft laptop key, press and release
  key-return_N   a heavier enter key                   tick_N        a tiny bright interface tick
  tick-crisp_N   a caption tick, glassy                 whoosh-short_N  air into a cut; its peak sits 0.18 s in
  whoosh-long_N  a long rise into a big cut; peak 0.9 s in      hit_N   a cinematic boom: sub drop, body, air
  land_N         a soft deep thud as something settles
cues.py lays a whoosh 0.18 s (short) or 0.9 s (long) before the cut, so each whoosh peaks on the cut itself.
The bundled kit (assets/kit) mixes public-domain recordings with the whooshes and hits from this script.

Needs numpy, scipy, soundfile.
"""
import argparse
import os

import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('--seed', type=int, default=7)
ap.add_argument('--roles', help='only these roles, comma separated')
args = ap.parse_args()
R = np.random.default_rng(args.seed)


def t_(sec):
    return np.arange(int(sec * SR)) / SR


def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo / (SR / 2), min(hi, SR / 2 - 200) / (SR / 2)], 'band', output='sos'), x, axis=0)


def lp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, min(fc, SR / 2 - 200) / (SR / 2), 'low', output='sos'), x, axis=0)


def hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc / (SR / 2), 'high', output='sos'), x, axis=0)


def room(x, secs=0.35, wet=0.12):
    """a small room: a short decaying noise tail, so dry synthesis does not sound like a test tone"""
    n = int(secs * SR)
    ir = R.normal(0, 1, n) * np.exp(-np.arange(n) / SR * (9 / secs))
    ir = lp(hp(ir, 300), 7000)
    ir /= np.sqrt((ir ** 2).sum())
    if x.ndim == 1:
        return x + signal.fftconvolve(x, ir)[:len(x)] * wet
    return x + np.stack([signal.fftconvolve(x[:, c], np.roll(ir, c * 37))[:len(x)] for c in (0, 1)], 1) * wet


def norm(x, peak_db=-3.0):
    x = x - np.mean(x, axis=0)
    return x / (np.abs(x).max() + 1e-9) * 10 ** (peak_db / 20)


def fade_tail(x, ms=8):
    n = int(ms / 1000 * SR)
    x[-n:] *= np.linspace(1, 0, n)[:, None] if x.ndim > 1 else np.linspace(1, 0, n)
    return x


def transient(dur, lo, hi, decay):
    t = t_(dur)
    return bp(R.normal(0, 1, len(t)), lo, hi) * np.exp(-t * decay)


def click(v):
    t = t_(0.09)
    body_f = 2300 + 500 * v
    x = transient(0.09, 1800, 9000, 380) * 0.9 + np.sin(2 * np.pi * body_f * t) * np.exp(-t * 160) * 0.35
    x += transient(0.09, 300, 1500, 220) * 0.25  # the plastic underneath
    return norm(fade_tail(room(x, 0.2, 0.06)), -4)


def key(v, heavy=False):
    t = t_(0.24 if heavy else 0.16)
    down = transient(len(t) / SR, 600, 4500, 120 if heavy else 170) + np.sin(2 * np.pi * (180 + 60 * v) * t) * np.exp(-t * 60) * (0.6 if heavy else 0.35)
    up_at = int((0.075 + 0.02 * v) * SR)
    up = np.zeros_like(t)
    rel = transient(len(t) / SR, 1200, 6000, 260) * 0.35
    up[up_at:] = rel[:len(t) - up_at]
    return norm(fade_tail(room(down + up, 0.25, 0.08)), -5 if not heavy else -3.5)


def tick(v, crisp=False):
    t = t_(0.18 if crisp else 0.1)
    f = (3400 if crisp else 2800) + 600 * v
    tone = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 60)
    x = tone * np.exp(-t * (28 if crisp else 55)) + transient(len(t) / SR, 4000, 12000, 600) * 0.3
    return norm(fade_tail(room(x, 0.3, 0.1 if crisp else 0.05)), -6)


def whoosh(peak, total, v):
    """air rushing past: pink-ish noise through a band that sweeps up into the peak and falls after it (stereo pass)"""
    t = t_(total)
    n = len(t)
    noise = np.cumsum(R.normal(0, 1, (n, 2)), axis=0)
    noise = hp(noise - signal.savgol_filter(noise, 2001, 2, axis=0), 120)
    k = np.clip(t / peak, 0, None)
    centre = np.where(t < peak, 400 + 3200 * k ** 2, 3600 * np.exp(-(t - peak) * 5) + 300)
    out = np.zeros((n, 2))
    step = 512
    for i in range(0, n, step):
        c = centre[i] * (1 + 0.04 * v)
        out[i:i + step] = bp(noise[max(0, i - 4096):i + step], c * 0.55, c * 1.8)[-len(noise[i:i + step]):]
    env = np.where(t < peak, k ** 2.4, np.exp(-(t - peak) * (6 if total < 1 else 3.5)))
    pan = np.clip((t - peak) / (total - peak + 1e-6) * 2 - 1, -1, 1) * 0.6
    out[:, 0] *= env * (1 - pan) / 2 * 1.4
    out[:, 1] *= env * (1 + pan) / 2 * 1.4
    return norm(fade_tail(room(out, 0.6, 0.18)), -4)


def hit(v):
    t = t_(2.2)
    f = 34 + 70 * np.exp(-t * 9) + 4 * v
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    body = np.sin(2 * np.pi * (95 + 10 * v) * t) * np.exp(-t * 9) * 0.5
    crack = transient(2.2, 200, 6000, 30) * 0.5
    air = hp(R.normal(0, 1, len(t)), 3000) * np.exp(-t * 7) * 0.12
    x = np.tanh((sub + body + crack + air) * 1.6)
    x = np.stack([x, np.roll(x, 23)], 1)
    return norm(fade_tail(room(x, 1.6, 0.22), 40), -2)


def land(v):
    t = t_(0.9)
    f = 48 + 60 * np.exp(-t * 18) + 3 * v
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) + transient(0.9, 150, 2500, 40) * 0.35
    return norm(fade_tail(room(np.tanh(x * 1.3), 0.7, 0.15), 20), -3)


ROLES = {
    'click': lambda v: click(v), 'key': lambda v: key(v), 'key-return': lambda v: key(v, True),
    'tick': lambda v: tick(v), 'tick-crisp': lambda v: tick(v, True),
    'whoosh-short': lambda v: whoosh(0.18, 0.5, v), 'whoosh-long': lambda v: whoosh(0.9, 1.5, v),
    'hit': lambda v: hit(v), 'land': lambda v: land(v),
}
TAKES = {'click': 3, 'key': 6, 'key-return': 1, 'tick': 3, 'tick-crisp': 3, 'whoosh-short': 3, 'whoosh-long': 2, 'hit': 2, 'land': 2}

os.makedirs(args.out, exist_ok=True)
want = set(args.roles.split(',')) if args.roles else set(ROLES)
made = 0
for role in ROLES:
    if role not in want:
        continue
    for i in range(TAKES[role]):
        v = (i - (TAKES[role] - 1) / 2) / max(1, TAKES[role] - 1) * 2  # -1..1 across the takes
        sf.write(os.path.join(args.out, f'{role}_{i + 1}.wav'), ROLES[role](v), SR, subtype='PCM_16')
        made += 1
print(f'{made} sounds in {args.out}')
