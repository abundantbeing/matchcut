# Grok Imagine video (xAI)

Summary: xAI's `grok-imagine-video-1.5` does text-to-video, image-to-video and reference-to-video with pinned frames. It is short-prompt friendly and the docs give little prompt theory.

Sources (checked 2026-11-11):
- https://docs.x.ai/docs/guides/video-generations
- https://docs.x.ai/developers/model-capabilities/video/reference-to-video
- https://docs.x.ai/developers/model-capabilities/video/generation (via search listing)
- https://docs.x.ai/docs/models (pricing list only)
- Third-party tips: https://morphic.com/resources/how-to/grok-imagine-video-1-5-guide (secondary)

## Modes

- Models: `grok-imagine-video-1.5` (text, image, reference), `grok-imagine-video-1.5-lite` (text or start frame, cheaper), and `grok-imagine-video` (editing and the older model).
- Text-to-video: duration, aspect ratio and resolution are settable.
- Image-to-video: the image is the starting frame. Native 1080p is mentioned for this mode in xAI's search listing (unverified in the docs I read).
- Reference-to-video (1.5): up to 14 reference images and up to 3 voice references (the base model: 7 images). A first-frame `image`, a `last_frame`, and up to 4 timed `keyframes` can be pinned. At least one reference, voice, last frame or keyframe is required.
- First+last frame: `image` plus `last_frame` interpolates between both. `last_frame` alone makes the clip end on that image. The same image as both makes a loop.
- Extension: continues an existing clip from its last frame; edit mode changes an existing clip by text.
- Duration: up to 15 s on 1.5 (up to 10 s on the base model) in reference mode. Examples use 8 to 12 s.
- Resolution: up to 720p on the reference page; ratios shown are 16:9 and 9:16, full list unverified.
- Audio: voice references use preset voice IDs (such as "eve", "leo"). Custom audio is limited to approved partners. Whether generated clips always carry audio is not stated in the docs I read.
- Prompt length limit: not documented.

## How it reads a prompt

- Tag references by list position in the prompt: `<IMAGE_0>`, `<IMAGE_1>`. If you also pin a first frame, it takes `<IMAGE_0>` and references start at `<IMAGE_1>`. Voices are `<AUDIO_0>` to `<AUDIO_2>`.
- Docs examples are short, comma-separated fragments with a camera direction. Prompt is optional when a frame is pinned.
- Keyframes: each pairs an image with `timestamp_s`, strictly inside the clip, snapped to a 1/3 s grid, at least 1/3 s apart.
- Negative prompts and bracket camera syntax: not documented. State what you want.
- Third-party advice: one action per clip, one camera move, include an audio cue (secondary source).

## Consistency

- Give each reference one clear role and a fixed place in the scene. Keep the cast small and props static.
- Make the stills first with an image editor so only intended elements differ, then animate.
- Pin first frame for identity and last frame to control where the clip ends.

## Failure modes and fixes

- Identity drift: add the hero as a reference and as first frame; shorten the clip.
- Objects drifting off a hand: pin a last frame that shows the object held.
- Too many references blur roles: cut to the few that matter.
- Long takes degrade: generate shorter clips and extend.
- Platform wrappers expose different features (some are image-only); confirm what your host supports.

## Worked example (image-to-video, one shot)

Format note: keep it short and fragment-like; the house headings compress into a few lines.

```
STORY: Mara, painterly treasure hunter, copper breastplate and red scarf, has just thrown a glowing amber card. She is about to catch it as the ruined temple lights up. Warm torchlight, painterly.
THIS SHOT (1 of 5): low three-quarter angle. <IMAGE_0> is the start frame: Mara, red scarf, copper breastplate, alone in a ruined temple hall.
ACTION: the glowing card spins down from the dark ceiling, Mara steps back and catches it with her right hand, amber light spreads over her face and the pillars, dust drifts.
LOCKED: one character, one card, five fingers each hand, card stays in her right hand after the catch, same costume as <IMAGE_0>, no text.
CAMERA: slow push in toward her raised hand. One continuous shot, no cuts. Audio: stone echo, rising chime on the catch.
```
