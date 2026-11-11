"""Lay voiceover lines over a finished film's own audio, duck the music a little under the voice, and mux.

Works with a stripped ffmpeg (Remotion's `npx remotion ffmpeg` has no asplit or sidechain filters): ffmpeg only
decodes to WAV and muxes; the mix is numpy.

    python voiceover_mix.py film.mp4 out.mp4 vo.mp3:0-6.4@1.0 vo.mp3:6.9-8.67@15.9 [--duck 0.45] [--gain 1.5]

Each placement is <file>:<start>-<end>@<time in film>, seconds. FFMPEG env picks the binary
(default `ffmpeg`; e.g. FFMPEG="npx remotion ffmpeg").
"""
import argparse
import os
import shlex
import subprocess
import tempfile
import wave

import numpy as np

SR = 48000
FF = shlex.split(os.environ.get('FFMPEG', 'ffmpeg'))


def decode(src, dst):
    subprocess.run(FF + ['-v', 'error', '-y', '-i', src, '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s16le', dst], check=True)
    w = wave.open(dst)
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('film')
    ap.add_argument('out')
    ap.add_argument('place', nargs='+')
    ap.add_argument('--duck', type=float, default=0.45, help='how far the music dips under the voice (0-1)')
    ap.add_argument('--gain', type=float, default=1.5, help='voice gain')
    a = ap.parse_args()
    tmp = tempfile.mkdtemp()
    music = decode(a.film, os.path.join(tmp, 'music.wav'))
    vo = np.zeros_like(music)
    cache = {}
    for p in a.place:
        f, rest = p.rsplit(':', 1)
        span, at = rest.split('@')
        s, e = (float(x) for x in span.split('-'))
        if f not in cache:
            cache[f] = decode(f, os.path.join(tmp, f'vo{len(cache)}.wav'))
        seg = cache[f][int(s * SR):int(e * SR)]
        i = int(float(at) * SR)
        n = min(len(seg), len(vo) - i)
        vo[i:i + n] += seg[:n]
    env = np.abs(vo).max(1)
    k = int(0.25 * SR)
    env = np.clip(np.convolve(env, np.ones(k) / k, 'same') * 12, 0, 1)
    mix = music * (1 - a.duck * env)[:, None] + vo * a.gain
    peak = np.abs(mix).max()
    if peak > 0.97:
        mix *= 0.97 / peak
    out_wav = os.path.join(tmp, 'mix.wav')
    w = wave.open(out_wav, 'wb')
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
    subprocess.run(FF + ['-v', 'error', '-y', '-i', a.film, '-i', out_wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', a.out], check=True)
    print(a.out, f'peak {peak:.2f}')


if __name__ == '__main__':
    main()
