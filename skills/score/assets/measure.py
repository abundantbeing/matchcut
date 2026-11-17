#!/usr/bin/env python3
"""measure.py: the finished film, measured like a reference, before it goes out.

    python measure.py out/film.mp4 --tl film/src/tl.json
    python measure.py public/audio/soundtrack.wav --tl film/src/tl.json   # the mix alone, before a render

It prints four numbers and what each one says:
  pace         cuts per 10 s, from tl.json (opening clips, shots). Brand launch films mostly sit at 0.5 to 4
               (a published measure of 82 of them: median 1.85); above 4 reads as a montage, so it had better be one
  loudness     integrated LUFS (ITU-R BS.1770) and true peak. Brand films mostly sit at -18.5 to -13 LUFS;
               the master stays at or under -1 dBTP
  headroom     peak-to-loudness, aiming for 12 to 16 dB: lower and the hits are squashed
  heroes       each hero (tl.json "heroes"; by default the match cut, the "moment" and the end card) against the
               nearest sound that starts there; a hero more than a frame and a half from one has lost its hit
plus the share of all cuts that land on a sound, against what cuts at random times would score. Heroes on, the rest
free is the house rule, so a share near chance is fine as long as the heroes land.
Needs numpy, scipy, soundfile, and ffmpeg for a video (FFMPEG to pick one). score.py uses its loudness().
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from scipy import signal

SR = 48000
# the two published K-weighting biquads at 48 kHz
K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
K2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def loudness(x):
    """integrated loudness (BS.1770: K-weighting, 400 ms blocks, absolute and relative gates) and true peak, 48 kHz"""
    x = x if x.ndim == 2 else x[:, None]
    y = signal.lfilter(*K2, signal.lfilter(*K1, x, axis=0), axis=0)
    n, hop = int(0.4 * SR), int(0.1 * SR)
    z = np.array([(y[i:i + n] ** 2).mean(0).sum() for i in range(0, len(y) - n + 1, hop)])
    z = z[-0.691 + 10 * np.log10(z + 1e-12) > -70]
    if not len(z):
        return -70.0, -120.0
    rel = -0.691 + 10 * np.log10(z.mean()) - 10
    z = z[-0.691 + 10 * np.log10(z) > rel]
    tp = 20 * np.log10(np.abs(signal.resample_poly(x, 4, 1, axis=0)).max() + 1e-12)
    return -0.691 + 10 * np.log10(z.mean()), tp


def headroom(lufs, tp):
    plr = tp - lufs
    return plr, (f'the hits are squashed: lower rms_db by {12.5 - plr:.0f} dB and they come back' if plr < 12
                 else 'a quiet, open mix: fine for a calm film; raise rms_db a little if it must sit beside loud ones' if plr > 16
                 else 'room for the hits')


def onsets(x):
    """times where a sound starts: spectral flux on a log spectrogram, peaks over a running median"""
    m = x.mean(1) if x.ndim == 2 else x
    hop = 240  # 5 ms
    _, t, Z = signal.stft(m, SR, nperseg=2048, noverlap=2048 - hop, boundary=None)
    S = np.log1p(100 * np.abs(Z))
    flux = np.maximum(S[:, 1:] - S[:, :-1], 0).sum(0)
    flux /= flux.max() + 1e-12
    base = signal.medfilt(flux, 101) + 0.04  # half a second of context
    peaks, _ = signal.find_peaks(flux, height=base, distance=10)  # at least 50 ms apart
    return t[1:][peaks] + 0.009  # the flux peaks a little before the attack; measured on the bundled hits and lands


def read(path):
    if path.lower().endswith('.wav'):
        import soundfile as sf
        x, sr = sf.read(path, always_2d=True)
        if sr == SR:
            return x
        return signal.resample_poly(x, SR, sr, axis=0)
    ff = os.environ.get('FFMPEG', 'ffmpeg')
    with tempfile.TemporaryDirectory() as d:
        w = os.path.join(d, 'a.wav')
        r = subprocess.run([ff, '-v', 'error', '-y', '-i', path, '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s24le', w])
        if r.returncode or not os.path.exists(w):
            sys.exit(f'measure.py: no audio read from {path} (is there an audio track? FFMPEG picks the ffmpeg)')
        import soundfile as sf
        x, _ = sf.read(w, always_2d=True)
        return x


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('film', help='the rendered film (mp4) or its soundtrack (wav)')
    ap.add_argument('--tl', help="the film's tl.json, for pace, heroes and cut sync")
    ap.add_argument('--fps', type=float, default=60, help='a hero may be a frame and a half off (default 60 fps)')
    a = ap.parse_args()
    x = read(a.film)
    dur = len(x) / SR

    lufs, tp = loudness(x)
    plr, says = headroom(lufs, tp)
    print(f'loudness  {lufs:.1f} LUFS, true peak {tp:.1f} dBTP' + ('  (over -1 dBTP: lower the master)' if tp > -1 else ''))
    print(f'headroom  {plr:.1f} dB peak-to-loudness: {says}')
    if not a.tl:
        return
    tl = json.load(open(a.tl, encoding='utf-8'))
    shots, opening = tl['shots'], tl.get('opening', [])
    total = tl.get('total', dur)
    cuts = [o['from'] for o in opening[1:]] + [s['from'] for s in shots if s['from'] > 0]
    pace = len(cuts) / total * 10
    print(f'pace      {pace:.1f} cuts per 10 s ({len(cuts)} in {total:.0f} s)' + (
        ': a montage; keep one thing constant so it reads as one sentence' if pace > 4
        else ': long holds; let moves inside the shots carry the change' if pace < 0.5 else ''))

    on = onsets(x)
    if not len(on):
        print('heroes    no sound starts anywhere: is the soundtrack silent?')
        return
    heroes = tl.get('heroes')
    if heroes is None:  # the same default as check-tl.mjs, song_fit.py and cues.py
        heroes = [h for h in (shots[0]['from'] if opening else None, tl.get('moment'), tl.get('end', {}).get('from')) if h is not None]
    tol = 1.5 / a.fps
    lost = 0
    for h in heroes:
        d = on[np.argmin(np.abs(on - h))] - h
        ok = abs(d) <= tol
        lost += not ok
        print(f'hero      {h:6.2f} s  nearest sound {d * 1000:+5.0f} ms  ' + ('lands' if ok else 'LOST: no hit starts here'))
    win = 0.07
    hit = sum(np.min(np.abs(on - c)) <= win for c in cuts) / max(len(cuts), 1)
    grid = np.arange(0, dur, 0.005)  # chance: how much of the film sits within 70 ms of some sound starting
    chance = (np.min(np.abs(grid[:, None] - on[None, :]), 1) <= win).mean() if len(grid) * len(on) < 4e7 else float('nan')
    print(f'cuts      {hit:.0%} land within 70 ms of a sound starting; cuts at random times would score {chance:.0%}')
    print(f'{len(heroes) - lost} of {len(heroes)} heroes land' + ('' if not lost else ': give the lost ones their hit (cues.py) or move them onto the beat (song_fit.py)'))


if __name__ == '__main__':
    main()
