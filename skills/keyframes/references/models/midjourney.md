# Midjourney (current family: V8.x; V7 still available)

Summary: Midjourney's V8 line (V8.1, and a V8.2 Edit model per secondary sources) is prompted with natural description plus `--` parameters. Official docs returned 403, so most specifics here come from the V7 Omni Reference page and a V8.1 API-route guide; treat Discord/web behaviour as needing a check.

Sources (checked 2026-11-11):
- https://docs.midjourney.com/hc/en-us/articles/36285124473997 (official Omni Reference page, V7-era; seen via search listing)
- https://docs.midjourney.com/docs/parameter-list (official; seen only in a listing)
- https://evolink.ai/docs/en/api-manual/image-series/midjourney/midjourney-v8-1-prompt-guide (third-party API host for V8.1; readable)
- https://miraflow.ai/blog/midjourney-v8-2-edit-model-guide-prompts-2026 (secondary, about V8.2 Edit)
- Midjourney has no public official API in my sources; a host route may behave differently from the app.

## Modes

- Text to image, image prompts (image URLs before the text), style reference `--sref`, object/character reference `--oref`, and on V8.2 an Edit model that secondary sources say replaces Omni Reference, Character Reference and Retexture (unverified).
- V8.1 host guide: up to 20 image prompts and up to 20 `--sref` images; only one `--oref` image. A single image with no text is invalid. `--sref` and `--oref` need a text prompt.
- Official V7 note: Omni Reference costs 2x GPU time and is not compatible with Fast, Draft or Conversational modes or `--q 4`. On V8 jobs `--oref` is reportedly handled by V7 (secondary).
- Aspect ratio: `--ar W:H` integers only; extreme ratios may be unpredictable.
- Resolution (host): `hd` is native 2K; draft mode gives small sketches and cannot use image references.
- `--stylize` / `--s` 0 to 1000 (default 100); `--raw` reduces default beautification; `--sw` 0 to 1000 for style weight; `--ow` 1 to 1000 for omni weight (default 100; host advises staying under 400).
- `--no` is not exposed on the V8.1 host route; whether the app keeps it in V8.x is unverified.
- Prompt length limit and text-in-image behaviour: not documented in what I read.

## How it reads a prompt

- Subject first, then setting, light, lens and medium, in short descriptive phrases. Parameters go at the end, with a space before `--`, no punctuation inside them, nothing after them.
- Dependencies: `--sw` needs `--sref`, `--ow` needs `--oref`, `--iw` needs an image prompt.
- General experience, not from the docs: multi-character blocking from text alone is unreliable; use image prompts for position and identity.
- No multi-shot or timestamp syntax; this is a still-image tool.

## Consistency

- `--oref` with the hero image plus `--ow` (default 100; the host advises staying under 400; the 200 in the example is a starting guess, not a documented value); add `--sref` of the style frame to lock look. Using the same image for both is described as a way to lock subject and look together (secondary).
- Reuse the same style reference and weights on every keyframe.

## Failure modes and fixes

- Extra fingers or merged hands: crop-friendly framing, or regenerate; fix hands in an edit pass.
- Identity drift: raise `--ow` moderately, add a clean three-quarter reference.
- Style overpowering the character: lower `--sw`.
- Over-beautified look that ignores the prompt: use `--raw`, lower `--stylize`.
- Text in image warps: avoid it; add titles in post.
- Failed or filtered jobs can still cost credits (host note).

## Worked example (keyframe image for the hero-catches-card shot)

```
Mara, a stylised treasure hunter in a copper breastplate and red scarf, right arm raised mid-catch, fingers open, a glowing amber card hovering just above her hand trailing sparks, ruined stone temple with cracked pillars, low three-quarter angle from the floor, warm torchlight and drifting dust, painterly storybook illustration, one person only, five fingers on each hand, no text --ar 16:9 --oref https://example.com/mara.png --ow 200 --sref https://example.com/style.png --sw 100 --s 150
```

House format reminder: STORY (above, folded in), THIS SHOT 1 of 5 (low three-quarter), ACTION frozen (arm raised, card above hand), LOCKED (one person, five fingers, no text), CAMERA (floor-level wide). Midjourney wants it as one phrase list, not labelled sections.
