#!/usr/bin/env python3
"""song_prompt.py: write the music prompt for a film, from its own timeline.

    python song_prompt.py film/src/tl.json --mood epic-tech [--bpm 120] [--key minor] [--extra "..."]
                          [--moment 15.8] [--breath 24.6-27.4] [--tool all|generic|elevenlabs|suno|udio|stable-audio]
                          [--out song-prompt.md]

It reads where the intro ends, where the biggest moment is (the loudest hit in tl.json "sfx" between the first
shot and the end card, or --moment), where the end card lands and how long the film is, and writes a prompt that
asks for that arc in seconds: a quiet build, an impact as the product appears, a rise into the big moment, the full
section, an optional breath, a last hit on the end card and a short ring-out. One prompt per tool, because tools
take different shapes: a paragraph, section tags, a style line plus a duration. --mood takes a preset (below) or
your own words.

No music tool? The code band (score.py) needs nothing: this is the upgrade, not a requirement.
"""
import argparse
import json
import re

MOODS = {
    'epic-tech': ('cinematic electronic trailer', 'pulsing sixteenth-note synth bass, punchy modern drums, shimmering arpeggios, wide pads, a soaring synth lead', 'confident, driving, awe', 120),
    'calm-premium': ('modern minimal electronica', 'soft felt piano, warm analog pads, light glitchy percussion, a deep sub', 'calm, precise, expensive', 96),
    'bright-playful': ('upbeat indie electronic pop', 'plucky synths, claps, a bouncy bass, glockenspiel', 'playful, sunny, quick', 118),
    'warm-human': ('uplifting acoustic pop', 'fingerpicked guitar, light hand percussion, claps, warm strings', 'warm, hopeful, personal', 104),
    'dark-intense': ('dark hybrid trailer', 'low brass hits, taiko and staccato strings, a distorted sub, ticking percussion', 'tense, powerful, serious', 110),
    'lofi-focus': ('chill lo-fi hip hop', 'dusty drums, mellow electric piano, a warm round bass, soft vinyl texture', 'focused, relaxed, late night', 84),
    'luxury-sleek': ('deep house', 'a smooth sub bass, crisp shuffled hats, airy chords, a soft plucked hook', 'sleek, smooth, premium', 122),
    'retro-synth': ('synthwave', 'analog arpeggios, gated-reverb drums, a warm bass, a bright neon lead', 'nostalgic, fast, glowing', 110),
    'orchestral-hero': ('modern orchestral score', 'string ostinato, french horns, big percussion, a piano motif', 'heroic, rising, cinematic', 100),
}

ap = argparse.ArgumentParser()
ap.add_argument('tl')
ap.add_argument('--mood', default='epic-tech', help='a preset (' + ', '.join(MOODS) + ') or your own words')
ap.add_argument('--bpm', type=int)
ap.add_argument('--key', help='minor or major, or a key like "D minor" (default: the preset key)')
ap.add_argument('--extra', default='', help='anything else, e.g. "no guitars" or "like a space launch"')
ap.add_argument('--moment', type=float, help='film time of the biggest moment')
ap.add_argument('--breath', help='a quiet stretch, "from-to" in seconds')
ap.add_argument('--tool', default='all', choices=['all', 'generic', 'elevenlabs', 'suno', 'udio', 'stable-audio'])
ap.add_argument('--out', help='also write the prompts to this markdown file')
args = ap.parse_args()

tl = json.load(open(args.tl, encoding='utf-8'))
total = float(tl['total'])
first = float(tl['shots'][0]['from'])
intro_end = float(tl['intro']['to']) if tl.get('intro') else first
end = float(tl['end']['from']) if tl.get('end') else total
moment = args.moment if args.moment is not None else tl.get('moment')
if moment is None:
    hits = [e for e in tl.get('sfx', []) if 'hit' in (e['role'] if isinstance(e['role'], list) else [e['role']]) and first + 1 < e['t'] < end - 1]
    moment = max(hits, key=lambda e: e.get('gain', 0.5))['t'] if hits else (first + end) / 2
breath = tuple(float(v) for v in args.breath.split('-')) if args.breath else None

genre, instruments, feel, bpm = MOODS.get(args.mood, (args.mood, '', '', 110))
bpm = args.bpm or bpm
key = args.key or ({'calm-premium': 'major', 'bright-playful': 'major', 'warm-human': 'major', 'luxury-sleek': 'minor'}.get(args.mood, 'minor') if args.mood in MOODS else '')
# electronic and trailer music builds to a drop; everything else swells
DROP = re.search(r'electronic|trailer|edm|house|techno|synth|dubstep|trap|hip hop|drum and bass|hybrid', genre, re.I) is not None
W = ({'enter': 'a clear impact and the groove enters: drums and bass, steady and confident', 'build': 'a rising build, a riser and a snare roll',
      'peak': 'the full drop: everything in, the main hook', 'end': 'one final big hit, then a clean held chord ringing out', 'peak_tag': 'Drop'}
     if DROP else
     {'enter': 'the rhythm enters and the melody begins, warm and steady', 'build': 'a gentle lift, the rhythm getting fuller',
      'peak': 'the fullest moment: the melody soars, every instrument in', 'end': 'a last strong chord, then a short ring-out', 'peak_tag': 'Chorus'})
length = round(total + 1)


def s(t):
    return f'{t:.0f} s' if abs(t - round(t)) < 0.05 else f'{t:.1f} s'


# the arc, in the film's own seconds
arc = []
if intro_end >= 2:
    arc.append(('Intro', 0, intro_end, f'0-{s(intro_end)}: a quiet build, sparse and wide, tension slowly rising'))
build = max(intro_end, moment - 2.5)
arc.append(('Groove', intro_end, build, f'at {s(intro_end)} ' + W['enter']))
arc.append(('Build', build, moment, f'{s(build)}-{s(moment)}: ' + W['build']))
if breath:
    arc.append((W['peak_tag'], moment, breath[0], f'at {s(moment)} ' + W['peak']))
    arc.append(('Breakdown', breath[0], breath[1], f'{s(breath[0])}-{s(breath[1])}: a short breath, pads and the arpeggio only'))
    arc.append((W['peak_tag'] + ' 2', breath[1], end, f'from {s(breath[1])} full energy again'))
else:
    arc.append((W['peak_tag'], moment, end, f'at {s(moment)} ' + W['peak']))
arc.append(('Ending', end, total, f'at {s(end)} ' + W['end'] + f'; the music ends by {s(total)}'))

head = f'A {length}-second instrumental {genre} cue at {bpm} BPM' + (f' in a {key} key' if key else '') + (f', {feel}' if feel else '') + ', crisp modern production, wide and polished.'
inst = f' Instruments: {instruments}.' if instruments else ''
rules = ' Steady tempo, no tempo changes, no vocals, no long fade-out.' + (f' {args.extra.strip().rstrip(".")}.' if args.extra.strip() else '')
generic = head + inst + ' ' + ' '.join(a[3][0].upper() + a[3][1:] + '.' for a in arc) + rules

out = {}
out['generic'] = ('Any text-to-music tool (ElevenLabs Music, Lyria, Beatoven, Soundraw, Mubert and others): paste this. '
                  'Set the length to the film length if the tool has one.', generic)
plan = [{'section_name': a[0], 'duration_ms': int(round((a[2] - a[1]) * 1000)),
         'positive_local_styles': [a[3].split(': ', 1)[-1]], 'negative_local_styles': ['vocals']} for a in arc if a[2] > a[1]]
out['elevenlabs'] = ('ElevenLabs Music: paste the paragraph in the app. Through the API, a composition plan pins each section '
                     'to its length (shape below; check the current API docs for the field names).',
                     generic + '\n\n' + json.dumps({'positive_global_styles': [genre, f'{bpm} bpm', 'instrumental', feel],
                                                    'negative_global_styles': ['vocals', 'long fade out'], 'sections': plan}, indent=2))
style = ', '.join(v for v in [genre, f'{bpm} bpm', key, 'instrumental', instruments.replace(', a ', ', ').replace('a ', '', 1) if instruments else '', feel] if v)
tags = '\n'.join(f'[{a[0]}]' + (' (big impact)' if a[0] in ('Groove', W['peak_tag']) else '') + (' (final hit, ring out)' if a[0] == 'Ending' else '') for a in arc)
out['suno'] = ('Suno: Instrumental on. "Style of Music" gets the first block (keep it short); the lyrics box gets the section tags. '
               'Length is not exact: generate, then measure with song_fit.py and trim with track_from.',
               style[:200] + '\n\n' + tags)
out['udio'] = ('Udio: Manual mode, instrumental. The prompt is the first line; put the arc in the lyrics box as tags.',
               style[:200] + '\n\n' + tags)
out['stable-audio'] = (f'Stable Audio: set the duration to {length} s. It follows the BPM and the instruments well and the arc '
                       'loosely: keep the prompt short.',
                       ', '.join(v for v in [genre, instruments, feel, f'{bpm} BPM', f'{key} key' if key else '', 'instrumental',
                                             'builds to a big ' + ('drop' if DROP else 'swell'), 'ends on a final hit'] if v))

print(f'film {s(total)}: intro to {s(intro_end)}, biggest moment {s(moment)}, end card {s(end)}' + (f', breath {args.breath}' if breath else ''))
md = ['# Song prompt', '', f'Film: {args.tl}, {s(total)}. Mood: {args.mood}. Generate two takes, then run',
      '`song_fit.py song.mp3 --tl ' + args.tl + '` to place it and move the cuts onto its beats.', '']
for name, (note, text) in out.items():
    if args.tool not in ('all', name):
        continue
    print(f'\n== {name}: {note}\n{text}')
    md += [f'## {name}', '', note, '', '```', text, '```', '']
if args.out:
    open(args.out, 'w', encoding='utf-8', newline='\n').write('\n'.join(md))
    print(f'\nwritten {args.out}')
