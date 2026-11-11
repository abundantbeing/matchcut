# Luma Ray (current: Ray 3.2; Ray 3.14, Ray 3 Modify, Ray 2 earlier)

Summary: Luma's current model is Ray 3.2 (announced 2026-06-09): multi-keyframe control, HDR, 20 s, 1080p, now with an API. My sources for prompting specifics are thin; most prompt rules below are unverified.

Sources (checked 2026-11-11):
- https://lumalabs.ai/news/introducing-ray-3-2 (official announcement)
- https://docs.lumalabs.ai/docs/video-generation (official API docs; still describes Ray 2 and Ray 2 Flash)
- https://docs.agents.lumalabs.ai/guides/videos/editing (official editing docs, via search listing)
- https://lumalabs.ai/learning-center/articles/ray-3-2-introduction-and-core-concepts (official; returned 404 to me, snippets only)

## Modes

- Ray 3.2 per announcement: multi-keyframe placement ("up to 16 keyframes" in the announcement; a Luma article snippet says up to 64 in edit mode, so the two disagree), performance tracking of body and up to eight faces, native HDR with 16-bit EXR export, Reframe (aspect ratio change, frame extension, background replace), clips to 20 s at 1080p.
- Text-to-video and image-to-video with `frame0` (start) and `frame1` (end) are documented for Ray 2; assume Ray 3.x keeps start/end frames (Luma's own Dec 2025 release added start/end for video-to-video).
- Extend: forward, reverse, with an end frame, or interpolate between two generations (Ray 2 docs; source must be a completed Luma generation).
- Ray 3 Modify: video-to-video; one third-party source says 10 s max input and original audio kept (unverified).
- Ray 2 docs list 540p, 720p, 1080p, 4k and a `loop` flag; only 5 s and 16:9 appear in examples.
- Audio generation for Ray 3.2: not mentioned in the announcement; unverified.
- Aspect ratios and prompt length: not documented in what I read.

## How it reads a prompt

- Camera moves are controlled by wording. The Ray 2 docs say to fetch the supported camera motions from the camera list endpoint and use that wording; close phrasing often works.
- A `concepts` parameter exists (for example `dolly_zoom`); list concepts via the concepts endpoint.
- Luma's messaging favours concrete nouns and observable motion over style words like "cinematic" (secondary).
- Keyframes are the main control lever in edit mode; a prompt is optional if keyframes are given (docs listing).
- Negative prompts and tag syntax: not documented in what I read.

## Consistency

- Pin start (and end) frames with the approved hero images.
- Use keyframes to fix pose at chosen moments instead of describing them in text.
- Modify strength: lower strength keeps source detail, higher allows reinterpretation (secondary).

## Failure modes and fixes

- Vague style words give generic motion: write what moves and where.
- Pose or camera drift mid-clip: add a keyframe near the problem moment.
- Edit changes too much: lower the modify strength (secondary) and anchor with keyframes.
- Wrong camera behaviour: use the exact phrasing from the camera list.
- Frame image URLs must be on your own CDN for the Ray 2 API.

## Worked example (image-to-video, one shot)

Format note: use the house format; the wording below is kept observable and concrete. Send the start image as `frame0` and, if you have one, the "card in hand" image as `frame1`.

```
STORY: Mara, painterly treasure hunter, has just thrown a glowing amber card in a ruined temple; she is about to catch it and the hall lights up. Tense, then awe.
THIS SHOT (1 of 5): low three-quarter angle, 5 seconds. Mara, red scarf, copper breastplate, is the only person.
ACTION: The glowing card spins down from the dark ceiling. Mara steps back on her left foot and catches it with her right hand between two fingers. Amber light spreads over her face and the cracked pillars. Dust drifts.
LOCKED: one character, one card, five fingers per hand, card stays in her right hand after the catch, costume matches frame0.
CAMERA: slow push in toward her raised hand. One continuous shot, no cuts, no text.
```
