# Nano Banana (Google Gemini image models)

Summary: Google's Gemini image line is branded Nano Banana. Current: Nano Banana 2.1 (`gemini-nano-banana-2.1`) as the default, Nano Banana Pro (`gemini-3-pro-image`) for hard text and brand work, Nano Banana 2 Lite for speed. Up to 14 reference images and multi-turn editing make it a good keyframe tool.

Sources (checked 2026-11-11):
- https://aistudio.google.com/docs/image-generation (official; I read the first 100,000 of about 241,000 characters, so the prompting tips and failure sections were mostly cut off)
- https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1 (official; mentions generating Veo frames with Gemini image)

## Modes

- Models: Nano Banana 2.1 (`gemini-nano-banana-2.1`, recommended for new work), Nano Banana 2 (`gemini-3.1-flash-image`, previous), Nano Banana 2 Lite (`gemini-3.1-flash-lite-image`, fastest; not optimized for multiple references or multi-turn editing, no Search grounding), Nano Banana Pro (`gemini-3-pro-image`, premium reasoning and text), Nano Banana (`gemini-2.5-flash-image`, legacy).
- Text to image, edit with reference images, multi-turn conversational editing (chain turns with `previous_interaction_id`), interleaved text and image output.
- Reference images: 2.1 and 3.1 Flash up to 14 total (up to 10 object and 4 character). Pro up to 14 (6 object, 5 character, 3 style).
- Resolution: 1K, 2K, 4K (default 1K). Uppercase "K" required; lowercase is rejected. 0.5K only on 3.1 Flash Image.
- Aspect ratios: 2.1 and 3.1 Flash add 1:4, 4:1, 1:8, 8:1 to the usual set (16:9, 5:4, 1:1 and others in examples).
- Thinking levels: 2.1 minimal, medium (default), high. 3.1 Flash and Lite minimal (default), high. Thinking cannot be turned off and is billed.
- Google Search and Image Search grounding exist; image-search results do not inform generation.
- All images carry a SynthID watermark.
- Prompt length limit: not captured.

## How it reads a prompt

- Photoreal template: shot type, subject, setting, lighting, camera angle, lens.
- Illustration template: artistic style, subject, medium, visual details.
- Describe a scene in full sentences; Google recommends multi-turn iteration over one giant prompt.
- Text rendering is described as strong for infographics, menus and diagrams; Pro is the pick for dense or branded text.
- Reference roles: say what each image is for (character, object, style). No tag syntax is documented in what I read.
- Negative prompts: no field in what I read; phrase constraints positively.
- For keyframes feeding Veo, Google's guide suggests generating the first and last frames here.

## Consistency

- Use character reference slots for the hero and object slots for the card; Pro adds style slots.
- Edit the previous frame in the same conversation and say what to keep ("do not change anything else", as in Google's infographic example).
- Avoid Lite for multi-reference or sequential work.

## Failure modes and fixes

- Lowercase `1k`: use `1K`.
- Lite drifts across turns: switch to 2.1 or Pro.
- Cast or object changes when only one element should: add an explicit keep-unchanged clause.
- Slow or costly runs: lower thinking level for drafts.
- Beyond the above, the failure guidance was in the part of the page I did not read; verify.

## Worked example (keyframe image for the hero-catches-card shot)

```
STORY: Mara, a stylised treasure hunter, has just thrown a glowing amber card in a ruined temple and is about to catch it. Painterly storybook illustration, warm torchlight, soft dust.
THIS SHOT (1 of 5): low three-quarter angle from the temple floor, wide lens, 16:9. Use the character reference for Mara (copper breastplate, red scarf); she is the only person. Use the object reference for the glowing amber card.
ACTION FROZEN AT: her right arm is raised, fingers open, the card hovering just above her palm, trailing a few sparks; cracked stone pillars frame the left and right.
LOCKED: one person, two arms, five fingers on each hand, one card, face and costume identical to the references, no text, no logos.
CAMERA: floor-level, looking slightly up, shallow depth of field on the hand.
Settings: aspect ratio 16:9, size 2K. Follow-up turn: "Same image, but the card is now held between her thumb and forefinger. Do not change anything else." (this becomes the last frame)
```
