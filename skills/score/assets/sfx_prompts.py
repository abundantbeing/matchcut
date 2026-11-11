#!/usr/bin/env python3
"""sfx_prompts.py: prompts for a sound-effect generator, one per role cues.py places, in the film's own style.

    python sfx_prompts.py [--style clean-tech] [--tl film/src/tl.json] [--out kit-prompts.md]

Any text-to-sound tool works (ElevenLabs Sound Effects, Stable Audio, AudioGen and others). For each role it gives
the prompt, the length to set, how many takes to make and the file names to save them as, so cues.py picks them
up from your kit folder (`cues.py tl.json scenes kit/`; roles you skip come from the bundled kit). Styles:
clean-tech (glassy, modern UI), warm (soft, wooden, analog), cinematic (big, deep, trailer), playful (bouncy, bright),
or your own words. With --tl it counts how many of each sound the film will use, so you make enough takes.
"""
import argparse
import json

STYLES = {
    'clean-tech': 'clean modern digital interface sound, glassy, precise, close-miked, no music',
    'warm': 'soft warm analog sound, wooden and felt textures, gentle, close-miked, no music',
    'cinematic': 'big cinematic trailer sound design, deep and polished, no music',
    'playful': 'bright bouncy playful sound, rounded and friendly, no music',
}
# role: (what it is, seconds, takes, note on placement)
ROLES = {
    'click': ('a single crisp click of a mouse or trackpad button, one click only, very short', 0.3, 3, 'starts instantly, no silence before it'),
    'key': ('a single soft laptop keyboard key press and release, one key only', 0.3, 6, 'starts instantly; slightly different each take'),
    'key-return': ('a single enter key press on a laptop keyboard, a little heavier than a normal key', 0.4, 1, 'starts instantly'),
    'tick': ('a tiny bright interface tick, one short high blip', 0.3, 3, 'starts instantly'),
    'tick-crisp': ('a soft glassy notification ping for text appearing on screen, one short note', 0.6, 3, 'starts instantly, short ring'),
    'whoosh-short': ('a fast air whoosh passing close to the camera, swells quickly then fades', 0.6, 3, 'loudest about 0.2 s in: it is placed 0.18 s before a cut'),
    'whoosh-long': ('a long cinematic whoosh rising toward a big moment, swelling then passing', 1.6, 2, 'loudest about 0.9 s in: it is placed 0.9 s before a big cut'),
    'hit': ('a heavy cinematic impact boom with a deep sub drop and a short tail', 2.5, 2, 'the impact at the very start'),
    'land': ('a soft deep thud of something settling firmly into place', 1.0, 2, 'the thud at the very start'),
}

ap = argparse.ArgumentParser()
ap.add_argument('--style', default='clean-tech', help='a preset (' + ', '.join(STYLES) + ') or your own words')
ap.add_argument('--tl', help="the film's tl.json, to count how many of each sound it uses")
ap.add_argument('--roles', help='only these roles, comma separated')
ap.add_argument('--out', help='also write the prompts to this markdown file')
args = ap.parse_args()

style = STYLES.get(args.style, args.style)
counts = {}
if args.tl:
    tl = json.load(open(args.tl, encoding='utf-8'))
    counts['whoosh-short'] = max(0, len(tl.get('shots', [])) - 1)
    counts['tick-crisp'] = len(tl.get('lines', []))
    for e in tl.get('sfx', []):
        for r in (e['role'] if isinstance(e['role'], list) else [e['role']])[:1]:
            counts[r] = counts.get(r, 0) + 1
want = args.roles.split(',') if args.roles else list(ROLES)

lines = ['# Sound-effect prompts', '',
         f'Style: {style}. Make each take as its own generation, trim any silence before the sound, and save it as',
         '`kit/<role>_<n>.wav` (WAV or anything ffmpeg converts). Then: `cues.py tl.json scenes kit/`.', '']
print(f'style: {style}\n')
for role in want:
    what, secs, takes, note = ROLES[role]
    used = counts.get(role)
    prompt = f'{what}. {style[0].upper() + style[1:]}.'
    head = f'{role}: {secs} s, {takes} takes' + (f' (this film uses it {used} times)' if used else '') + f', save as kit/{role}_1.wav ... kit/{role}_{takes}.wav'
    print(head + f'\n  {prompt}\n  {note}\n')
    lines += [f'## {role}', '', head, '', '```', prompt, '```', '', note, '']
lines += ['## Tool notes', '',
          '- ElevenLabs Sound Effects: set the duration to the length above; a higher prompt influence keeps it literal.',
          '- Stable Audio: set the length; it may add room tone, so trim the start.',
          '- Any other: if it cannot set a length, generate and trim to the length above.',
          '- Check every take by ear (or a listening tool) before keeping it: one wrong sound repeated 40 times ruins a film.', '']
if args.out:
    open(args.out, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    print(f'written {args.out}')
