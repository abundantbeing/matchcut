# Kling (3.0 and 4.0, plus Omni/O3 variants)

Summary: Kling 4.0 is Kuaishou's current model: 3 to 30 s clips, native stereo audio, up to 15 reference assets, keyframes at timestamps, multi-shot on by default. Kling 3.0 (3 to 15 s) is still offered.

Sources (checked 2026-11-11):
- https://kling.ai/quickstart/kling-4-model-user-guide (official; I read the first 100,000 of about 124,000 characters)
- https://kling.ai/blog/kling-ai-prompt-guide (official prompt guide, 3.0 era)
- https://kling.ai/blog/kling-4-ai-video-model and https://kling.ai/blog/kling-4-vs-3 (official, via search listing)
- https://docs.dev.runwayml.com/guides/models/ (third-party model catalog for 3.0 and 4.0 ranges)

## Modes

- Kling 4.0: Omni Reference (default; text, image, keyframe-to-video, references, video editing) and Keyframes (first frame, first+last, or middle frames at timestamps; images only). The two entry points cannot be combined in one task.
- Kling 4.0 Flash: faster and cheaper, 3 to 20 s, 720p SDR only.
- Length: 4.0 is 3 to 30 s in 1 s steps, default 10 s. 3.0 is 3 to 15 s.
- Resolution: 720p, 1080p, 4K on 4.0. HDR is listed as available in the spec table but "coming soon" in the overview; unverified.
- Ratios: 21:9, 16:9, 1:1, 9:16, or Auto. With uploaded keyframes the first image sets the ratio.
- Omni Reference limits: 15 assets total; up to 10 images (ratio 2:5 to 5:2), 5 videos (3 to 30 s, 30 s combined), 7 elements (up to 3 video elements), 3 voice profiles. Keyframes: up to 10 images, no reference assets.
- Native audio: stereo, lip sync, many languages. Dialogue goes in quotation marks. Background music can be excluded.
- Prompt limit: 8,000 tokens (official 4.0 guide).

## How it reads a prompt

- Official structure: asset roles, overall setting, timed sequence of events, then audio.
- Six prompt elements on the 3.0 guide: subject, action, scene, camera, lighting, mood. Write plain scene direction, not object lists.
- Assign roles with tags: `@Image1` for appearance, `@Video1` for camera or pacing. Use "Edit @Video1" for edits, not "Reference @Video1", and add "keep everything else unchanged".
- Multi-shot: automatic (model plans coverage) or custom. Time-coded segments like `0-5s: ...`, or bracketed headers like `[Shot 1: Wide shot]`.
- Camera words documented: close-up, medium close-up, extreme close-up, full body, wide, low angle, push-in, pan, tilt, tracking. Pacing words (slow, steady, quick) help.
- Negative prompts: the official guide says to avoid negative instructions and abstract terms. Exclude only subtitles and background music when needed.
- Short on-screen text: state placement, surface and distance.

## Consistency

- Bind an Element (or video element, 3 to 8 s source footage) to the character or product and keep its description steady while scene and camera change.
- Do not re-describe in text what the start image already shows (host advice, secondary); describe motion.
- Keyframes at timestamps pin pose or composition mid-clip.

## Failure modes and fixes

- Auto multi-shot cuts when you want one take: write "one continuous shot, no cuts" and a single camera move, or use a custom single segment.
- Asset quota exhausted: video references, editing videos and video elements share one video quota.
- Drift on long clips: plan 30 s as timed beats with one master scene description.
- Garbled text: keep it short and specify placement, or add in post.
- Mixed speakers: use clear speaker labels.
- Access and 4K/HDR availability vary by plan and host; confirm in your account.

## Worked example (image-to-video, one shot)

```
@Image1 is the start frame and Mara's look (red scarf, copper breastplate, painterly).
STORY: Mara, a stylised treasure hunter, has just thrown a glowing amber card in a ruined temple. She is about to catch it and the hall will light up. Tense, then awe.
THIS SHOT (1 of 5): low three-quarter angle, 6 seconds. Mara is the only person.
ACTION: 0-6s: the glowing card spins down from the dark ceiling. Mara steps back on her left foot and catches it with her right hand between two fingers. Amber light spreads over her face and the cracked pillars. Dust drifts.
LOCKED: one character, one card, five fingers per hand, card stays in her right hand after the catch, costume as in @Image1.
CAMERA: slow push in toward her raised hand. One continuous shot, no cuts, no text.
Audio: stone echo, rising chime on the catch. No dialogue, no background music.
```
