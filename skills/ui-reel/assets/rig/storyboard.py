"""A contact sheet of a recorded take, with its marks, so the take can be checked without watching it.

    python storyboard.py <captureDir> [out.png] [--n 12]

Reads <captureDir>/frames.json (from take.mjs) and take.json, picks frames evenly plus one at every mark, and tiles
them with their film time and the mark's label. Needs Pillow only.
"""
import argparse
import json
import os

from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument('cap')
ap.add_argument('out', nargs='?')
ap.add_argument('--n', type=int, default=12)
ap.add_argument('--width', type=int, default=480)
a = ap.parse_args()
frames = json.load(open(os.path.join(a.cap, 'frames.json')))
take = json.load(open(os.path.join(a.cap, 'take.json'))) if os.path.exists(os.path.join(a.cap, 'take.json')) else {'marks': []}
if not frames:
    raise SystemExit('no frames')
end = frames[-1]['t']
picks = [(end * i / max(1, a.n - 1), '') for i in range(a.n)] + [(m['t'], m['label']) for m in take['marks']]
picks.sort()


def at(t):
    best = frames[0]
    for f in frames:
        if f['t'] <= t + 1e-6:
            best = f
        else:
            break
    return best


first = Image.open(os.path.join(a.cap, frames[0]['file']))
w = a.width
h = round(first.height * w / first.width)
cols = 4
rows = (len(picks) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w, rows * (h + 26)), '#0b0b12')
d = ImageDraw.Draw(sheet)
for i, (t, label) in enumerate(picks):
    im = Image.open(os.path.join(a.cap, at(t)['file'])).convert('RGB').resize((w, h))
    x, y = (i % cols) * w, (i // cols) * (h + 26)
    sheet.paste(im, (x, y))
    d.text((x + 6, y + h + 6), f'{t:6.2f}s  {label}', fill='#ffd166' if label else '#c9d2e0')
out = a.out or os.path.join(a.cap, 'storyboard.png')
sheet.save(out)
print(out, len(picks), 'frames,', f'{len(frames)} captured over {end:.2f}s ({len(frames) / max(end, 0.01):.0f} fps)')
