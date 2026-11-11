# Google Veo 3.x (current: Veo 3.1)

Summary: Veo 3.1 makes 4, 6 or 8 second clips with native audio from text, an image, first+last frames, or reference images. Google's guide gives a five-part formula and explicit audio syntax.

Sources (checked 2026-11-11):
- https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1 (official prompt guide)
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/veo/3-1-generate (official model spec, formerly Vertex AI)
- https://aistudio.google.com/docs/video (official; says the Veo 3.1 preview model IDs in the Gemini API shut down on 2026-10-22 and points to Gemini Omni Flash)
- https://developers.googleblog.com/en/introducing-veo-3-1-and-new-creative-capabilities-in-the-gemini-api/ (official, via search listing)

## Modes

- Model IDs: `veo-3.1-generate-001` (GA), `veo-3.1-fast-generate-001` (GA), `veo-3.1-lite-generate-001` (Preview). Availability moved to the Gemini Enterprise Agent Platform; check where your key lives.
- Inputs: text, image. Image-to-video up to 20 MB.
- First+last frame: supported on all three. Describe the transition in the prompt.
- Reference images ("ingredients"): supported on Generate and Fast, not Lite. The maximum count is not stated on Google's spec page; hosts say up to 3 (unverified). Reference-image mode is 8 s only.
- Extension: supported.
- Audio: native audio (dialogue, effects, ambience). No audio input.
- Length: 4, 6 or 8 s. Resolution: 720p or 1080p; 4K output on Generate only. Ratios: 16:9 and 9:16. 24 fps. Up to 4 videos per request.
- Prompt language: English. Prompt length limit: not documented.
- Gemini Omni Flash (`gemini-omni-1.2-flash`) is named by Google as the replacement route in the Gemini API: 3 to 15 s, up to 6 reference images. It is a different model; verify before routing Veo prompts to it.

## How it reads a prompt

- Formula: Cinematography + Subject + Action + Context + Style and ambiance, in that order.
- Camera vocabulary the guide uses: dolly, tracking, crane, aerial, slow pan, POV; wide, close-up, extreme close-up, low angle, two-shot; shallow depth of field, wide-angle, macro, soft focus.
- Dialogue in quotes: `A woman says, "We have to leave now."`. Effects as `SFX: ...`. Ambience as `Ambient noise: ...`.
- Timestamp prompting for several beats in one clip: `[00:00-00:02] ...`, `[00:02-00:04] ...`. Keep to what fits in 8 s.
- Negative prompts: Google advises describing what you want instead ("a desolate landscape with no buildings" rather than a "no X" list). A negative-prompt field is not documented on the spec page.
- Reference images are named by role in the prompt ("using the provided images for the detective and the office...").

## Consistency

- Generate stills first (Google suggests its Gemini image model), then use them as first frame, last frame or references.
- Hosts report the first frame is followed closely and the last frame acts more as a guide (secondary, one author).

## Failure modes and fixes

- Thin prompt gives generic output: use the formula and name the shot and the move.
- Reference mode locked to 8 s: plan beats to fit, or use image-to-video for 4 or 6 s.
- Extra or morphing characters: name each visible character once; keep the cast small; use references.
- Unwanted music or speech: describe the audio you want, including "no dialogue".
- Complex scene fails in one pass: build stills first and animate.
- Preview/GA naming churn: pin a `-001` model ID and re-check the date of the docs.

## Worked example (image-to-video, one shot)

```
STORY: Mara, a stylised treasure hunter in a copper breastplate and red scarf, has just thrown a glowing amber card across a ruined temple. She is about to catch it. Mood: tense, then awe. Painterly, warm torchlight.
THIS SHOT (1 of 5): Low three-quarter angle from the floor, 8 seconds. Mara, red scarf and copper breastplate, is the only person; the start image shows her pose.
ACTION: The glowing card spins down from the dark ceiling. Mara steps back on her left foot and catches it with her right hand between two fingers. Amber light spreads over her face and cracked pillars. Dust drifts.
LOCKED: one character, one card, five fingers per hand, card stays in her right hand after the catch, costume matches the start image.
CAMERA: Slow dolly in toward her raised hand. One continuous shot, no cuts, no text.
SFX: stone echo, a rising chime as the card is caught. Ambient noise: faint wind through the ruin. No dialogue, no music.
```
