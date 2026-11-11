# MiniMax Hailuo (current: MiniMax-H3, "Hailuo 3.0")

Summary: MiniMax's current video model is H3, which takes text, 1 or 2 frame images, and mixed references, and writes native audio. Prefers a scene description followed by timed shots.

Sources (checked 2026-11-11):
- https://platform.minimax.io/docs/guides/video-generation (official API guide)
- https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide (summarizes MiniMax's own H3 prompt guides)
- https://fal.ai/learn/devs/minimax-h3-prompting-guide (host guide, secondary)
- Older Hailuo 2.3 notes come only from third-party hosts and are marked below.

## Modes

- Text-to-video: prompt only. Set a fixed aspect ratio; "adaptive" is not allowed here.
- Image-to-video: prompt plus 1 or 2 images (first frame, last frame, or both). Ratio follows the image.
- First+last frame: same endpoint, two images. Good for transitions and for landing on a known end pose.
- Reference mode: up to 9 images, 3 videos (2-15 s each, 15 s total), 3 audio clips (2-15 s each, 15 s total), 12 files in total. Inputs must have a ratio between 2:5 and 5:2.
- Audio: native audio is generated (dialogue, effects, ambience, music).
- Length: 4 to 15 s, integers (official page). fal's guide says 5 to 15 s; treat 5 to 15 as the safe range.
- Resolution: 768P or 2K (official page).
- Prompt limit: 7,000 characters (official page).
- There is also a cheaper "H3 Max" tier listed by Runway's catalog (480p, 768p, frames and audio); details unverified.

## How it reads a prompt

- Describe the whole scene first, then the shots in time order, with camera and sound written in the same block.
- Timed shots (per the ComfyUI summary of MiniMax's guide): label `[Shot 1]`, `[Shot 2]`. Shot 1 starts at 0.00 s. Later shots open with one cut time such as `At 00:03.500`. Do not write ranges like `[5s-8s]`. Cut times must increase and stay inside the clip length.
- Start a new shot only when subject, space, viewpoint or time changes. Small reframes stay as camera motion inside one shot.
- The ComfyUI workflow splits text into three fields: scene plus timed shots, `overall_soundscape` (1 to 4 sentences), `non_diegetic_music` (1 to 3 sentences, score only). Use `N/A` only for true silence. This field layout is specific to that workflow; for the API a single prompt is expected (unverified).
- Dialogue goes in `<d>` tags with speaker IDs like `(S1)`. Write dialogue and on-screen text verbatim in English double quotes.
- Camera: official page shows bracketed commands `[pan]`, `[zoom]`, `[static]` and says to put them right after the description they affect. The full command list for H3 is unverified. Older Hailuo 2.3 hosts list about 15 bracket commands (Push in, Pull out, Pan left, Tracking shot, Static shot); do not assume all exist in H3.
- Negative prompts: not supported in the documented H3 flow. Say what should appear instead. If unwanted speech shows up, fill both audio fields explicitly.
- Reference prompts: name inputs by number ("reference video 1") and say how each is used. ComfyUI's page documents `<Picture N>` and `<Subject N>` labels and retention words (fully preserved, partially preserved).
- Prompt refinement: the official page mentions an H3-Context-IR task that returns an enhanced prompt without making a video.

## Consistency

- Image-to-video with the hero frame as first frame is the strongest anchor.
- For recurring characters use reference mode with a labelled sheet: one `<Picture N>` per sheet, each panel described, shots pointed at specific panels.
- Say what to keep ("outfit and scarf preserved") and what may change.

## Failure modes and fixes

- Garbled on-screen text: put each string in double quotes, verbatim, or leave text out of the shot.
- Speech when none wanted: fill the soundscape field and state "no dialogue".
- Wrong speaker assigned: tie lines to visible events, not timecodes.
- Unwanted concepts: remove negatives and describe the wanted result.
- Morph or drift on cuts: keep the clip to one shot, one camera move.
- Hard-to-read speech: avoid ellipses in dialogue.

## Worked example (image-to-video, one shot)

Note: H3 prefers a scene paragraph plus timed shots. The house format is kept but written as plain prose under one shot.

```
STORY: Mara, a stylised treasure hunter in a copper breastplate and red scarf, has just thrown a spinning amber-glowing card across a ruined temple. Next she catches it and the hall lights up. Mood: tense, then awe. Style: painterly, warm torchlight, matches the start frame.
THIS SHOT (1 of 5): low three-quarter angle from the temple floor. Mara, red scarf, copper breastplate, is the only person in frame.
ACTION: [Shot 1] The glowing card spins down out of the dark ceiling. Mara steps back on her left foot, reaches up with her right hand, and catches it between two fingers. Amber light spreads across her face and the cracked pillars. Dust drifts.
LOCKED: one character, one card, both hands normal, five fingers, card stays in her right hand once caught, no other people, same costume as the start frame.
CAMERA: [Push in] slowly toward Mara's raised hand. One continuous shot, no cuts, no text.
Soundscape: low stone echo, a rising chime as the card is caught. No dialogue, no music.
```
