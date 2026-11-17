#!/usr/bin/env python3
"""cues.py: place sound effects on the film's events, from the timeline and the recorded takes.

    python cues.py film/src/tl.json film/public/scenes [kit/] > fx.json
    # then paste or merge fx.json into score.json "fx" (or pass --into score.json)

It reads every shot in tl.json, maps each take's pointer presses and keystrokes (take.json, written by take.mjs)
into film time through the shot's t0 and speed, and lays:
  click on every press          key on every keystroke      whoosh into every cut
  hit on the match cut          tick when a caption lands   land on the end card
  plus the story sounds listed in tl.json "sfx" (a countdown, a launch, a finish)
The heroes (tl.json "heroes", 3 to 5 moments; by default the match cut, the "moment" and the end card) get the film's
biggest sound in two layers on the same frame: the hit (or land) for the punch, a tail for the bloom. Nothing else
gets a tail, so the heroes stay special. Small repeated sounds (clicks, keys, ticks, short whooshes) never play the
same way twice: a different take than last time, a few percent of pitch and up to 1.5 dB of level, seeded (--seed)
so a re-run gives the same mix. score.py plays the "pitch" field.
Sounds come from a kit folder of WAV files named by role (click_1.wav, key_3.wav, whoosh-short_2.wav, hit_1.wav,
land_1.wav, tick_1.wav ...). With no kit given, the bundled kit next to this script is used (public-domain
recordings plus whooshes and hits made in code); a kit you give is used first and the bundled one fills any role it
lacks. Make a kit fully in code with make_kit.py, or prompt one from any sound-effect generator with sfx_prompts.py.
It ends with how often each file plays; more than 4 times in 30 s is worth more takes (make_kit.py or sfx_prompts.py).
"""
import argparse
import glob
import json
import os
import random
import re
import sys

ap = argparse.ArgumentParser()
ap.add_argument('tl')
ap.add_argument('scenes')
ap.add_argument('kit', nargs='?', help='your kit folder (default: the bundled kit)')
ap.add_argument('--into', help='write the cues into this score.json "fx" (replacing it)')
ap.add_argument('--seed', type=int, default=7, help='the scatter of pitch, level and takes (default 7)')
a = ap.parse_args()
tl = json.load(open(a.tl, encoding='utf-8'))
base = os.path.dirname(os.path.abspath(a.into)) if a.into else os.getcwd()

BUNDLED = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kit')


def rel(f):
    try:
        return os.path.relpath(f, base).replace('\\', '/')
    except ValueError:  # another drive on Windows
        return os.path.abspath(f).replace('\\', '/')


kit = {}
for folder in [d for d in (a.kit, BUNDLED) if d]:
    found = {}
    for f in sorted(glob.glob(os.path.join(folder, '*.wav'))):
        found.setdefault(re.sub(r'_\d+$', '', os.path.splitext(os.path.basename(f))[0]), []).append(rel(f))
    for role, files in found.items():
        kit.setdefault(role, files)
rng = random.Random(a.seed)
last = {}
SCATTER = {'click', 'key', 'key-return', 'tick', 'tick-crisp', 'whoosh-short'}  # the small sounds that repeat


def pick(*roles):
    for r in roles:
        if r in kit:
            takes = [f for f in kit[r] if f != last.get(r)] or kit[r]  # never the same take twice in a row
            last[r] = rng.choice(takes)
            return r, last[r]
    return None, None


fx = []


def add(t, gain, *roles):
    r, f = pick(*roles)
    if f is None or t < 0:
        return
    cue = {'file': f, 't': round(t, 3), 'gain': gain, 'role': r}
    if r in SCATTER:  # about +-3.5 % of pitch and +-1.5 dB, so forty keystrokes are forty different keystrokes
        cue['pitch'] = round(2 ** (rng.uniform(-0.6, 0.6) / 12), 4)
        cue['gain'] = round(gain * 10 ** (rng.uniform(-1.5, 1.5) / 20), 3)
    fx.append(cue)


shots = tl['shots']
cuts = [s['from'] for s in shots]
opening = tl.get('opening', [])
for s in shots:
    path = os.path.join(a.scenes, f"{s['take']}.json")
    if not os.path.exists(path):
        continue
    take = json.load(open(path, encoding='utf-8'))
    film = lambda t: s['from'] + (t - s['t0']) / s['speed']
    inside = lambda T: s['from'] + 0.05 <= T < s['to'] - 0.05
    for p in take.get('pointer', []):
        if p.get('down') and inside(film(p['t'])):
            add(film(p['t']) - 0.008, 0.55, 'click', 'tick')
    for k in take.get('keys', []):
        if inside(film(k['t'])):
            add(film(k['t']) - 0.005, 0.32, 'key-return' if k['key'] == 'Enter' else 'key', 'tick')
for i, c in enumerate(cuts):
    if i == 0 and opening:
        add(c - 0.9, 0.5, 'whoosh-long', 'whoosh-short')
        if not opening[-1].get('dissolve'):  # a dissolve lands its hit where the timeline's sfx says
            add(c, 0.75, 'hit')
    elif i > 0:
        add(c - 0.18, 0.42, 'whoosh-short', 'whoosh-long')
for o in opening[1:]:
    add(o['from'] - 0.15, 0.3, 'whoosh-short')
for line in tl.get('lines', []):
    add(line['from'] + 0.05, 0.22, 'tick-crisp', 'tick', 'text')
if 'end' in tl:
    add(tl['end']['from'], 0.6, 'land', 'hit')
# story sounds the takes cannot show (a countdown, a launch, a download finishing): tl.json "sfx",
# each {"t": seconds, "role": "hit", "gain": 0.6} with a fallback list of roles if the kit lacks the first
for e in tl.get('sfx', []):
    roles = e['role'] if isinstance(e['role'], list) else [e['role']]
    add(e['t'], e.get('gain', 0.5), *roles)
# the heroes: a hit (or land) and a tail on the same frame. A hero the timeline already gave a hit keeps it.
heroes = tl.get('heroes')
if heroes is None:  # the same default as check-tl.mjs and song_fit.py
    heroes = [h for h in (shots[0]['from'] if opening else None, tl.get('moment'), tl.get('end', {}).get('from')) if h is not None]
for h in heroes:
    if not any(abs(c['t'] - h) <= 0.03 and c['role'] in ('hit', 'land') for c in fx):
        add(h, 0.7, 'hit', 'land')
    add(h, 0.3, 'tail')
fx.sort(key=lambda f: f['t'])
# how often each file plays: a file heard more than 4 times in 30 s starts to sound like a loop
crowded = {}
for c in fx:
    n = sum(1 for d in fx if d['file'] == c['file'] and 0 <= d['t'] - c['t'] < 30)
    crowded[c['role']] = max(crowded.get(c['role'], 0), n)
crowded = {r: n for r, n in crowded.items() if n > 4}
for c in fx:
    del c['role']
if crowded:
    print('busiest files (plays in 30 s): ' + ', '.join(f'{r} {n} ({len(kit[r])} take' + 's' * (len(kit[r]) > 1) + ')' for r, n in sorted(crowded.items()))
          + '; the scatter hides some of it, more takes hide the rest', file=sys.stderr)
if a.into:
    score = json.load(open(a.into, encoding='utf-8'))
    score['fx'] = fx
    json.dump(score, open(a.into, 'w', encoding='utf-8', newline='\n'), indent=2)
    print(f'{len(fx)} cues into {a.into}')
else:
    print(json.dumps(fx, indent=1))
