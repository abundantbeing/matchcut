# The demo film

A made-up product (Orbit, mission control for a satellite fleet) and the 36 second film matchcut makes from it:
a title intro made in code (`intro` in `film/src/tl.json`): thousands of dots fly in and land as the wordmark, a line
of light cuts the word in two, then the dots swirl toward the app as it boots and its own dots lock into the live
globe. Then real footage. Every product frame is a recording of `site/index.html` running in a headless browser.

| File | What it is |
|---|---|
| `site/index.html` | The app: a live dot-matrix Earth with day and night, 240 tracked objects, the fleet's orbits, ground stations and downlink beams, a fleet list with live telemetry, a pass timeline. Launch a satellite: brackets lock on the pad and an ignition ring fills, the ascent with live altitude and speed, orbit insertion, then its first image downlinks scanline by scanline and opens full size |
| `site/land.js`, `site/img/` | The Earth's land mask at one degree, and six generated satellite photos |
| `takes.mjs` | Three takes: `reveal` (the app boots: the match-cut landing), `launch` (name, launch, first light), `sweep` |
| `score.json` | The mix: a produced song (`music/`, not in the repo: generate your own and set `track`) placed so its biggest hit lands on the liftoff, and 40 sound cues written by `cues.py` |
| `film/` | The Remotion project: `src/tl.json` (shots, camera, captions, story sounds, end card), `src/takes.ts` |

## Rebuild it

From this folder, with Chrome for Testing and ffmpeg installed (`node ../../scripts/doctor.mjs`):

```bash
RIG=../../skills/ui-reel/assets/rig
mkdir -p out film/public/scenes film/public/audio
(cd site && python -m http.server 8776 --bind 127.0.0.1 &)
CHROME=/path/to/chrome bash $RIG/launch.sh &
node $RIG/cdp.mjs open http://127.0.0.1:8776/index.html > out/target.txt
for t in reveal launch sweep; do
  SLOW=8 node $RIG/take.mjs $t      # the globe is heavy: 8x slow motion keeps the capture above 60 fps
  python $RIG/frames2cfr.py out/rec/$t film/public/scenes/$t.mp4
  node -e "const j=require('./out/rec/$t/take.json');require('fs').writeFileSync('film/public/scenes/$t.json',JSON.stringify({pointer:j.pointer,marks:j.marks,keys:j.keys}))"
done
# the song is not in the repo: without music/song-a.mp3 the code band in score.json plays. For a produced song:
#   python ../../skills/score/assets/song_prompt.py film/src/tl.json --mood epic-tech --breath 24.6-27.5
#   (generate it in your music tool, save it as music/song-a.mp3), then check the cuts against its beats:
#   python ../../skills/score/assets/song_fit.py music/song-a.mp3 --tl film/src/tl.json --at 0.06
python ../../skills/score/assets/cues.py film/src/tl.json film/public/scenes --into score.json   # the bundled kit; add a folder of your own WAVs to use yours first
python ../../skills/score/assets/score.py score.json --out film/public/audio/soundtrack.wav
cd film && npm install && npm run check && npm run render
```

Fonts are not included (they carry their own licences): put `JetBrainsMono-Bold.woff2` and
`JetBrainsMono-Regular.woff2` ([JetBrains Mono](https://www.jetbrains.com/lp/mono/), OFL) in `film/public/fonts`,
or change `look.fonts` in `film/src/tl.json`. A missing font falls back to the system face.
