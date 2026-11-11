# Wan (Alibaba): current Wan 3.0; 2.7, 2.6, 2.5 and 2.2 also documented

Summary: Wan 3.0 does text, image (first/last frame), reference, edit, extension and audio-driven video, 2 to 30 s, with native audio. Alibaba's prompt guide gives formulas per mode. Older Wan 2.x open weights exist; Wan 3.0 open-weight status is unverified.

Sources (checked 2026-11-11):
- https://www.alibabacloud.com/help/en/model-studio/text-to-video-prompt (official Model Studio prompt guide)
- https://runware.ai/docs/models/alibaba-wan3-0/guides/prompting (host guide for Wan 3.0: limits and inputs)
- https://docs.dev.runwayml.com/guides/models/ (third-party catalog: Wan 3.0 and Prime, 2 to 30 s, 480p to 1080p)
- Not read: Wan GitHub or ModelScope repositories, so open-weight details are unverified.

## Modes

- Text-to-video, image-to-video with first and last frame (`frameImages`), reference-driven (`referenceImages`, `referenceVideos`, `referenceAudios`), video editing, temporal extension, audio-driven.
- Length: any whole number 2 to 30 s, or "auto" (host).
- Resolution: 480p, 720p, 1080p for input-driven calls; text-to-video uses fixed width/height pairs (for example 1280x720, 1920x1080, 720x1280, 1080x1920, plus 1:1, 4:3, 3:4).
- Prompt length: host allows 20,000 characters but warns attention narrows past a few hundred well-chosen words.
- Audio: native audio on 3.0, 2.7, 2.6 and 2.5; `settings.audio: false` gives a silent file (host).
- `prompt_extend` can auto-expand short prompts; turn it off if you need exact wording (inference; not stated by the guide).

## How it reads a prompt

- Official formulas: Basic = Entity + Scene + Motion. Advanced adds Aesthetic control and Stylization.
- Image-to-video = Motion + Camera movement. The image supplies entity, scene and style, so do not redescribe them.
- Sound = add Voice (line, emotion, tone, speed), Sound effect (source, action, ambient) and Background music.
- Multi-shot (3.0, 2.7, 2.6): overall description, then `Shot 1 [0-3 s] ... Shot 2 [4-6 s] ...`. Keep key elements consistent across shots. For a single shot on 2.7 write "Generate single shot" (official); hosts also cite "one continuous shot".
- Reference-to-video (3.0, 2.7): reference identifier + action + scene + optional lines and music. Older 2.6 format: character + action + lines + scene. The exact identifier syntax is on a separate page I did not read.
- Camera: push in, pull out, move left, tracking, orbit, aerial; "fixed camera" holds still. Keep orbits under 45 degrees. Shot sizes, angles (eye, low, high, top-down, over-the-shoulder), lenses and light words are listed in the guide.
- Speed words ("quickly", "slowly") are recommended.
- Negative prompts: not covered in the guide pages I read; Wan 2.x open-source pipelines have a negative prompt input (unverified for 3.0).

## Consistency

- Image-to-video with the approved frame; reference images for recurring cast.
- Name a static camera explicitly; without camera direction, expect slight drift.
- Fix a near miss by naming the specific problem, not rewriting everything.

## Failure modes and fixes

- Official "avoid" list: real named people, rapid scene changes inside one clip (cut between clips instead), exact text legibility, very long or complex action, exact-word lip sync.
- Several beats in a short clip get compressed or dropped: one action per take, 5 to 8 s per beat.
- Spatial distortion on orbits: keep under 45 degrees.
- Camera drift: add "fixed camera" when you want it still.
- Defaults fill gaps: name subject, setting, camera and audio that matter.

## Worked example (image-to-video, one shot)

Format note: Wan wants motion plus camera for image-to-video, so STORY and LOCKED are kept short.

```
STORY: Mara, painterly treasure hunter, has just thrown a glowing amber card in a ruined temple; next she catches it and the hall lights up. Tense, then awe.
THIS SHOT (1 of 5): low three-quarter angle. Mara (red scarf, copper breastplate) from the input image is the only person.
ACTION: Generate single shot. The glowing card spins down from the dark ceiling. Mara steps back on her left foot, then quickly raises her right hand and catches the card between two fingers. Amber light spreads over her face and the pillars. Dust drifts slowly.
LOCKED: one character, one card, five fingers per hand, card stays in her right hand, costume unchanged.
CAMERA: slow push in toward her raised hand. No cuts, no text.
Sound: stone echo, rising chime when the card is caught, no dialogue.
```
