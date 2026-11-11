# Runway (Gen-4.5 for generation; Aleph 2 for video editing)

Summary: Gen-4.5 is Runway's current generation model for text-to-video and image-to-video; Aleph 2 edits existing video. Runway's own help-center pages were blocked to my fetcher, so several details below come from hosts and are marked.

Sources (checked 2026-11-11):
- https://docs.dev.runwayml.com/guides/models/ (official model catalog, readable)
- https://help.scenario.com/articles/5854126955-runway-gen4-5-the-essentials (host summary, readable)
- https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide (official; HTTP 403, only search snippets seen)
- https://academy.runway.com/prompt-guide (official; seen only in a search listing)
- https://runware.ai/docs/models/runway-gen-4-5/guides/directing-motion (host guide, seen only in a listing)

## Modes

- Gen-4.5 (`gen4.5`): text-to-video and image-to-video. Per the official snippet, more inputs are "coming soon".
- Gen-4 Turbo (`gen4_turbo`): image-to-video, cheaper.
- Aleph 2 (`aleph2`): video-to-video with keyframe guidance. Host says source up to 30 s with output the same length.
- Runway also hosts third-party models (Seedance, Kling, Veo and others per its catalog), each with its own rules; use that model's file.
- Length (Gen-4.5): 2 to 10 s (host). Resolution and ratio: about 7 ratio presets including 16:9, 9:16, 1:1, 21:9 (host). Exact pixel sizes unverified.
- First frame image sets composition and identity. A seed value can be reused to keep motion style (host).
- Audio: not documented for Gen-4.5 in what I read.
- Prompt length limit: not documented.

## How it reads a prompt

- Image-to-video: the image defines composition, subject, light and style; the prompt describes what moves. Official outline per snippets: subject action, environmental motion, camera motion, motion style and timing, direction and speed.
- Text-to-video guide structure (DataCamp attributing Runway): camera shot, subject and action, environment, supporting detail.
- Use film terms: dolly in, tracking shot, pan; add lighting and weather (volumetric light, golden hour).
- Strict formatting is not needed; clarity beats structure (host).
- Negative prompts: the documented advice favours positive description (host; unverified in official text).
- No tag or bracket syntax is documented for Gen-4.5.

## Consistency

- Make a strong still first and use it as the first frame so the model does not guess appearance.
- Match the frame's aspect ratio to the chosen ratio to avoid stretching or bars.
- To change the subject but keep the camera move, keep the seed and change only the subject text.

## Failure modes and fixes

- Subject redescribed in the prompt, causing drift: describe motion only.
- Stretched or letterboxed output: match image ratio to output ratio.
- Too many actions in a short clip: one action, one camera move.
- Identity change across clips: reuse the same first-frame image and seed.
- Text and fine logos are unreliable in generated video generally; plan to add them in post (general caution, not a Runway statement).

## Worked example (image-to-video, one shot)

Format note: keep the prompt about motion. STORY and LOCKED are brief because the image carries the look.

```
STORY: Mara, painterly treasure hunter, has just thrown a glowing amber card in a ruined temple; she is about to catch it. Tense, then awe.
THIS SHOT (1 of 5): low three-quarter angle, 5 seconds. Mara, red scarf, copper breastplate, is the only person (see the first frame).
ACTION: The glowing card spins down from the dark ceiling. Mara steps back and catches it with her right hand between two fingers. Amber light spreads over her face and the pillars. Dust drifts in the air.
LOCKED: one character, one card, five fingers per hand, card stays in her right hand after the catch, costume as in the first frame.
CAMERA: slow dolly in toward her raised hand. One continuous shot, no cuts, no text.
```
