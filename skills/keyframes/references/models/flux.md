# FLUX (Black Forest Labs): FLUX 3 Image; FLUX.2 and FLUX.1 Kontext earlier

Summary: BFL's current doc set targets FLUX 3 Image. Order matters more than length: image type, subject and action, setting, light, framing. References are cited by position ("image 1"). My fetches only reached summary pages for several sub-guides.

Sources (checked 2026-11-11):
- https://docs.bfl.ai/guides/prompting_summary (official; readable)
- https://docs.bfl.ml/guides/prompting_unified_building.md (official, "Building a good prompt")
- https://docs.bfl.ml/guides/prompting_editing_overview.md (official, image editing)
- Not read: Technical parameters, Style/aesthetics/text, Multi-reference editing, Layout prompts, the FLUX.2 migration page.

## Modes

- Text to image, single-image edit, multi-reference edit/compose. BFL's index also covers layout prompts with bounding boxes and a video section (not read).
- Reference images: 1 to 10 in the `images` list, as URLs or base64. The first is "image 1". With `aspect_ratio` set to `auto`, the output follows image 1, so put the image whose ratio you want first or set the ratio yourself.
- Bounding boxes: add box rows when several similar objects match a description or when position or size must be controlled; layout prompts pair a global caption with a table of boxes.
- Resolution, step counts, prompt length limit: not captured (see the Technical parameters page).
- Negative prompts: the index lists "working without negative prompts" under Technical parameters, which implies the current model takes none; details unread.

## How it reads a prompt

- Start with one sentence; add detail after reviewing results. Longer helps for several subjects, a layout, or text in the image.
- Order: image type and medium; subject and action; setting; light; framing and detail (shot size, angle, lens, depth of field). Put the most important element first. Write full sentences.
- Describe visible details that distinguish the subject, relationships between subjects (who faces whom), positions in plain words, colour as a palette, and one or two effects at most.
- For realism, describe what a camera would record; one generic realism cue is enough. Skip quality tags like "masterpiece" and stacked words like "highly detailed".
- In edits, a hex code can set a target colour.
- If the result pulls back too far, put subject and framing first and move environment details later.
- Remove any sentence that does not describe something visible.

## Consistency

- Give each reference a role in the prompt ("image 1 is the character, image 2 is the card").
- Reuse the same approved image as image 1 on every keyframe so the ratio and identity carry over.
- State what must stay unchanged in an edit.

## Failure modes and fixes

- Over-wide framing: lead with subject and framing.
- Unfocused result from too many effects: keep one or two.
- Wrong aspect ratio in multi-reference: reorder images or set `aspect_ratio`.
- Two similar objects confused: use bounding boxes.
- Text and long-run consistency details: not covered in the pages I read; check Style and Multi-reference guides.

## Worked example (keyframe image for the hero-catches-card shot)

```
STORY: Mara, a stylised treasure hunter, has just thrown a glowing amber card in a ruined temple and is about to catch it. Painterly storybook illustration, warm torchlight, soft dust.
THIS SHOT (1 of 5): low three-quarter angle from the temple floor, wide lens. Image 1 is Mara (copper breastplate, red scarf); she is the only person. Image 2 is the glowing amber card.
ACTION FROZEN AT: Mara's right arm is raised, fingers open, the card from image 2 hovering a few centimetres above her palm, trailing sparks. Cracked stone pillars behind her on the far left and right.
LOCKED: one person, two arms, five fingers on each hand, one card, same costume and face as image 1, no text, no logos.
CAMERA: floor-level, slightly looking up, shallow depth of field on Mara's hand.
Settings: aspect_ratio 16:9 (set explicitly).
```
