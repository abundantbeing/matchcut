# Seedream (ByteDance): 5.0 Pro and 5.0 Lite

Summary: Seedream 5.0 Pro is ByteDance's precision image model with up to 10 reference images and content-based multi-image prompting; 5.0 Lite is the cheaper line with higher resolution tiers. BytePlus's own pages returned only navigation to me, so details come from a host guide.

Sources (checked 2026-11-11):
- https://runware.ai/docs/models/bytedance-seedream-5-0-pro/guides/prompting (host guide; readable and detailed)
- https://docs.byteplus.com/en/docs/ModelArk/doubao-seedream-5-0-pro (official; body not retrieved)
- https://help.artlist.io/hc/en-us/articles/37481273737757-Seedream-5-0-Pro and https://help.runwayml.com/hc/en-us/articles/53253654113299-Creating-with-Seedream-5-0-Pro (hosts; seen in search listings only)

## Modes

- Text to image, and image-to-image editing or fusion when references are supplied.
- Pro references: up to 10 images (URL, data URI or media ID). Several hosts agree on 10.
- Pro limits (host): prompt up to 3,000 characters, provider recommends under 600 English words. Total pixels 1,048,576 to 4,194,304. Ratios 1:16 to 16:1. Billing tiers: up to 2.36 MP is "1.5K", above that "2K". At 1:1 the ceiling is 2048x2048; at 16:9 the long edge reaches 2752x1536.
- Lite (Artlist table, secondary): up to 4K output, up to 14 references, sequential generation. Unverified.
- With references present, width and height become optional.
- Negative prompts: not mentioned; use positive statements and "pin" clauses.

## How it reads a prompt

- Layer clauses: format, subject, composition, lighting, in-image text, style. Each clause is treated as a directive; skipping one hands that decision to the model.
- Name the format first ("cinematic key frame, 16:9") so the model composes for it.
- Overlong prompts scatter attention. Tighten ambiguous clauses instead of adding more.
- Multi-image: refer to references by content ("the tan leather journal") rather than position ("the first reference"), because content stays valid when the set changes. This is the opposite of FLUX; follow each model's rule.
- Name in-image text explicitly if you want any; a separate multilingual text guide exists (not read).

## Consistency

- Pass the approved asset as a reference and add a pin clause: "Keep the exact silhouette, camera angle, backdrop and lighting." Unmentioned elements drift without it.
- Packshots or clean sheets lock geometry, materials and logos better than prose.
- Use the cheaper 1.5K tier to iterate and 2K for finals (host).

## Failure modes and fixes

- Lost details in long prompts: keep under about 600 words.
- Missing layer gives default choices (for example no format clause makes a portrait that does not read as a cover): include all layers.
- Unpinned reference changes: add the pin clause.
- Position-based references breaking when images are reordered: name by content.
- Dense or non-Latin text: check the dedicated guide or composite in post.

## Worked example (keyframe image for the hero-catches-card shot)

```
STORY: Mara, a stylised treasure hunter, has just thrown a glowing amber card in a ruined temple and is about to catch it. Painterly storybook illustration, warm torchlight, soft dust, 16:9 cinematic key frame.
THIS SHOT (1 of 5): low three-quarter angle from the temple floor, wide lens. The woman in the copper breastplate and red scarf from the character reference is the only person. The glowing amber card from the card reference is her only prop.
ACTION FROZEN AT: her right arm is raised, fingers open, the card hovering just above her palm and trailing sparks; cracked stone pillars frame the left and right.
LOCKED: one person, two arms, five fingers on each hand, one card; keep her face, costume and proportions exactly as in the character reference; no text, no logos.
CAMERA: floor level, slightly looking up, shallow depth of field on the hand.
Settings: 2752x1536 (16:9), 2K tier.
```
