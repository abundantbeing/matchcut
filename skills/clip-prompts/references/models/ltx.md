# LTX (Lightricks): LTX-2 and newer LTX-2.5

Summary: LTX-2 is Lightricks' open-weight video model with synchronized audio; LTX-2.5 (Pro and Fast) is the newer hosted line. Prompt rules are shared: one flowing present-tense paragraph with six layers. Official LTX docs returned 403 to my fetcher, so I relied on a host guide for the 2.5 specifics.

Sources (checked 2026-11-11):
- https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/prompting (host guide for LTX-2.5 Pro; readable)
- https://docs.ltx.video/api-documentation/prompting-guide (official; HTTP 403)
- https://ltx.io/blog/prompting-guide-for-ltx-2 (official; fetch failed)
- https://docs.comfy.org/tutorials/video/ltx/ltx-2 (seen in a listing only)

## Modes

- Text-to-video, image-to-video, first and last frame (`frameImages`), audio-driven with a reference image (lip sync). Mode names are from the Runware host.
- LTX-2.5 Pro: 6, 8 or 10 s, or "auto"; 1280x720 or 1920x1080, and portrait 720x1280 or 1080x1920; fps 24, 25 or 50. Audio on or off. Prompt limit 5,000 characters (host).
- LTX-2.5 Fast: 2K or 4K, clips up to 20 s, 48 fps (host statement).
- LTX-2 (open weights): sizes, lengths and frame counts depend on your pipeline; unverified here.
- Negative prompt: not mentioned on the host page; support in LTX-2 open pipelines is unverified.

## How it reads a prompt

- Write one flowing paragraph, present tense, not a bullet list. Cover shot, scene, action, character, camera, audio.
- Describe a character's identity once, then use the action clause for what they do. Show emotion by physical cues, not labels.
- Keep one coherent light source per shot.
- Camera movement in its own clause, separate from subject motion: static or locked, gentle push-in, crane, slow tilt. The host mentions eight camera presets in settings.
- Match detail to shot scale. A focused brief often beats an exhaustive one.
- Audio: describe ambience and effects tied to the action in a plain sentence. Add "no music" if you will score it yourself.
- Use 6 s for one clean action; 8 or 10 s for a short developing sequence.

## Consistency

- Animate an approved still with first-frame anchoring. Use a last frame to direct the ending or build a loop.
- Do not re-describe appearance beyond what the image does not show.

## Failure modes and fixes

- In-frame text: spelling and consistency are not guaranteed. Keep it short, or composite in post.
- Chaotic motion smears: use plausible everyday movement.
- Two competing action arcs lose fidelity: one dominant arc.
- Mixed light sources confuse the render: pick one.
- Crowded action renders poorly: keep the cast small.
- Drift when camera is unspecified: name the camera move or "static camera".

## Worked example (image-to-video, one shot)

Format note: LTX prefers a single paragraph, so the house sections are folded into one block of prose below, with the labels kept in short form.

```
STORY and SHOT: A low three-quarter shot in a ruined temple hall, 6 seconds, painterly, lit only by warm torchlight, matching the start image. Mara, a stylised treasure hunter in a copper breastplate and red scarf, is the only person; the glowing amber card she just threw is the only light-emitting object.
ACTION: The card spins down from the dark ceiling. Mara steps back on her left foot and catches it with her right hand between two fingers. Amber light spreads across her face and the cracked pillars while dust drifts. She looks at the card with quiet awe.
LOCKED: one character, one card, five fingers per hand, the card stays in her right hand once caught, costume unchanged.
CAMERA: a slow push in toward her raised hand. One continuous shot, no cuts, no text.
AUDIO: low stone echo, a rising chime as the card is caught, no dialogue, no music.
```
