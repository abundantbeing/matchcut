"""Turn a rec capture (JPEG frames + frames.json timestamps) into a constant-60fps clip whose frame i is
exactly what the page showed at i/60 s: output frame i is the last captured frame at or before i/60.
The frames are hard-linked into a numbered sequence (no copies) and encoded as an image sequence, so no
demuxer timing is involved (tools/frames2mp4.py's concat durations drifted by up to 1.3 s).

    python tools/frames2cfr.py <captureDir> <out.mp4> [crf]
"""
import json
import os
import shutil
import subprocess
import sys

cap, out = sys.argv[1], sys.argv[2]
crf = sys.argv[3] if len(sys.argv) > 3 else '12'
FPS = 60
frames = json.load(open(os.path.join(cap, 'frames.json')))
if not frames:
    sys.exit('no frames')
# A screencast can deliver a stale frame from before the viewport override; keep the majority size only.
from collections import Counter
from PIL import Image
size = lambda fr: Image.open(os.path.join(cap, fr['file'])).size
major = Counter(size(fr) for fr in frames[:: max(1, len(frames) // 40)]).most_common(1)[0][0]
frames = [fr for fr in frames if size(fr) == major]
seq = os.path.join(cap, 'seq')
shutil.rmtree(seq, ignore_errors=True)
os.makedirs(seq)
total = int(round((frames[-1]['t'] + 0.5) * FPS))
j = 0
for i in range(total):
    t = i / FPS
    while j + 1 < len(frames) and frames[j + 1]['t'] <= t + 1e-6:
        j += 1
    src = os.path.join(cap, frames[j]['file'])
    os.link(src, os.path.join(seq, f'{i:05d}.jpg'))
ff = os.environ.get('FFMPEG', 'ffmpeg')
subprocess.run([ff, '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(seq, '%05d.jpg'),
                '-vf', 'format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-movflags', '+faststart', out], check=True)
shutil.rmtree(seq, ignore_errors=True)
print(out, total, 'frames', f'{total / FPS:.2f}s')
