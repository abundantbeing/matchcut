# Seedance (ByteDance): 2.0 family, 2.5 newer

Summary: Seedance 2.x is a reference-driven video model: it takes images, video and audio references bound by tags, writes native audio, and likes labelled shots with closing constraints. Version 2.5 exists (longer clips, more references); this file covers 2.0 firmly and flags 2.5 as less verified.

Sources (checked 2026-11-11):
- https://runway.com/resources/seedance-2-0-prompt-guide (host guide, most complete text I could read)
- https://docs.byteplus.com/en/docs/ModelArk/seedance-2-5-prompt-guide (official; page body did not load for me, only title and date Nov 7 2026)
- https://fal.ai/learn/devs/how-to-use-seedance-2-5 (secondary, limits)
- https://docs.dev.runwayml.com/guides/models/ (lists Seedance 2.0, Fast, Mini and 2.5)

## Modes

- Text-to-video, start/end frame, and references (images, videos, audio).
- Seedance 2.0: 5 to 15 s, 480p/720p/1080p, ratios from 21:9 to 9:16. Fast and Mini variants use the same prompt grammar, top out at 720p.
- References on 2.0: up to 9 images, 3 videos, 3 audio clips; video plus audio share a 15 s budget. Hosts disagree (12 or 15 files total). Four to five assets total works best.
- Reference videos should be 720p or lower.
- Seedance 2.5: up to 30 s, 480p to 1080p, partial editing and extension, many more references (host sources say 30 or 50; unverified). Native 4K is reportedly not supported.
- Native audio is generated in all modes.
- Prompt length: not documented in what I read. Hosts suggest 30 to 100 words for simple prompts; longer labelled prompts work for multi-shot.

## How it reads a prompt

- Tag references as `@Image 1`, `@Video 1`, `@Audio 1` and bind each to a job (look, camera, voice). Put the most precise assets first.
- Order inside a prompt: format line, reference roles, shots in event order, audio, constraints last.
- Cover subject, action details, scene, light and colour, camera, style, quality, constraints.
- Two layers: labelled shots (Shot 1, Shot 2) outside, connected sentences inside. Inside a shot: camera or transition, subject action, spatial change, audio.
- One camera move per shot. Let the model set pacing; precise timing is unstable.
- Symbols (per the host guide): curly braces for dialogue, parentheses for music, angle brackets for effects, corner brackets for subtitles.
- Negative prompts: no separate field; state constraints positively and close with a constraint line (no text, logos, subtitles, watermarks).
- For edits or extensions, refer to the video itself, not "reference", which can trigger a new generation.

## Consistency

- Use a close-up headshot plus a full-body image, not a multi-view sheet, if the face shifts.
- List what to preserve (hair, costume, props, palette) and say "one continuous shot".
- First frame as `@Image 1` anchors the opening look.

## Failure modes and fixes

- Generic motion: name the body part, degree and speed.
- Borrowed qualities from unassigned references: bind every reference to a job.
- Unwanted cuts or one flat take: use labelled shots, or ask for one continuous shot.
- Subtitles or logos appearing: constraint line at the end.
- Too many assets cause drift: use fewer.
- Warping on sprints or violent motion: slow, continuous action.
- Instability from stacked camera moves: one per shot.

## Worked example (image-to-video, one shot)

```
Format: 8 s, 16:9, painterly fantasy, one continuous shot.
@Image 1 is the start frame and the only look reference for Mara.
STORY: Mara, a stylised treasure hunter, has just thrown a glowing amber card across a ruined temple. She is about to catch it and the hall will light up. Mood: tense, then awe.
THIS SHOT (1 of 5): low three-quarter angle. Mara (red scarf, copper breastplate, as in @Image 1) is the only person.
ACTION: Shot 1: slow push in. The glowing card spins down from the dark ceiling. Mara steps back on her left foot and snaps her right hand up, catching the card between two fingers. Amber light spreads over her face and the cracked pillars; dust drifts.
LOCKED: one character, one card, five fingers per hand, card stays in her right hand, costume unchanged.
CAMERA: slow push in, no other camera move.
Audio: stone echo, rising chime on the catch, no dialogue.
Constraints: no cuts, no text, no subtitles, no logos, no watermark.
```
