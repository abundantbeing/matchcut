# GPT Image (OpenAI; ChatGPT image generation)

Summary: OpenAI's current image models are `gpt-image-2.5-sunburst` (best edit precision) and `gpt-image-2.5-flare` (fast everyday generation); 2.6 versions of both are also mentioned. Multi-image edits, transparency and a "complexity" control are the useful parts for keyframes.

Sources (checked 2026-11-11):
- https://developers.openai.com/api/docs/guides/image-generation (official; read about 126,000 characters in two parts)

## Modes

- Generate (text to image), and edit (one or several reference images, optional mask or markup layer).
- Models: `gpt-image-2.5-sunburst`, `gpt-image-2.5-flare`; the page also lists GPT-Image-2.6 Sunburst and Flare, which add complexity control, markup-guided edits, SVG output and animated GIF output. Older GPT Image models top out at `high` quality.
- Sizes: 1024x1024, 1536x1024, 1024x1536, or `auto`. Custom dimensions are supported; rules not captured in what I read.
- Quality: low, medium, high, xhigh, max, auto (2.5 models default to auto). Complexity: low, medium, high (default high); it controls how much the model plans before rendering.
- Background: transparent, opaque, auto. Transparent needs PNG or WebP output.
- Reference images: several allowed; the example uses four; no maximum stated. Inputs can be URL, base64 data URL or Files API ID. With a mask or markup, image 1 is the edited image and the rest are references.
- Input size: first image and markup layer up to 16,777,216 pixels; mask or markup file under 50 MB.
- `input_fidelity`: omit it for `gpt-image-2`; all inputs are processed at high fidelity, so reference edits cost more input tokens.
- Prompt length limit: not stated.
- In the Responses API the mainline model may rewrite your prompt; see `revised_prompt`.
- May need API Organization Verification.

## How it reads a prompt

- Plain descriptive prose works; no special syntax is documented.
- For edits: describe the change and what must stay the same. Mask edits are prompt-driven and may not follow the mask exactly.
- Lower complexity suits focused edits; high complexity helps dense text and layouts but adds latency and sometimes unwanted changes.
- Use `quality: low` for drafts; compare higher settings for finals.
- Negative prompts: no field. Write what to keep or avoid in the sentence ("no extra people") and check the result.
- Multi-image: tell it which image provides what (character from image 1, card from image 2).

## Consistency

- Pass the approved character image as a reference on every keyframe and say what must not change.
- OpenAI states that recurring characters or brand elements may not stay consistent across separate generations, so anchor each time rather than relying on memory.
- Keep one sheet of locked traits (costume, colours, props) and paste it into every prompt.

## Failure modes and fixes

- Imprecise text placement: keep text short, quote it exactly, or add it in post.
- Character drift across shots: always send the reference image; edit the previous keyframe rather than regenerating from text.
- Layout not exact: use mask or markup edits, or lower complexity for a small change.
- Mask shape ignored: describe the region in words as well.
- Slow runs on complex prompts (up to about 2 minutes): draft at low quality first.
- Unrequested changes in an edit: add an explicit "keep everything else unchanged" clause.

## Worked example (keyframe image for the hero-catches-card shot)

Image models make the start frame the video model will animate. Same house format, written for a still.

```
STORY: Mara, a stylised treasure hunter, has just thrown a glowing amber card in a ruined temple and is about to catch it. Mood: tense. Style: painterly, warm torchlight, soft dust, 16:9 frame.
THIS SHOT (1 of 5): low three-quarter angle from the temple floor. Mara, in a copper breastplate and red scarf (use image 1 for her face, costume and proportions), is the only person.
ACTION FROZEN AT: her right arm is raised, fingers open, the glowing amber card (image 2) hovering just above her hand, trailing a few sparks.
LOCKED: one character, one card, five fingers on each hand, two arms, card clearly separate from the pillars, no text, no logos, no extra people. Keep everything else from image 1 unchanged.
CAMERA: eye level just below her chest, wide lens, still frame.
Settings: size 1536x1024, quality high, complexity medium.
```
