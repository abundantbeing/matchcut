# A three-clip cold open, worked through

Sunrise over Earth's night side from orbit, a satellite catching the first light, then the whole Earth, which
match-cuts into the product's live globe (the Orbit app in `examples/demo`). Each prompt is complete on its own:
paste one per generation with its still.

## Clip 1: sunrise from orbit (single image)

```
STORY: The first shot of a short cinematic film. We are in low Earth orbit on the night side; the sun is about to
rise over the planet's edge. Next we meet a satellite catching that first light. Mood: vast, silent, awe.
Style: photoreal, IMAX 65mm, real optics, deep blacks. Keep the planet, the coastline and the city lights exactly
as in the first frame.
ACTION: the camera drifts slowly forward along the orbit. The thin blue line of atmosphere brightens, and the sun
breaks over the limb at upper right: a white starburst that grows and flares across the lens. City lights shimmer
below, lightning flickers inside a distant storm.
CAMERA: one slow, steady push forward and a slight roll toward the sun. One continuous shot, no cuts, no text,
nothing new enters the frame.
```

## Clip 2: the satellite (single image)

```
STORY: One shot from a short cinematic film. The sun has just risen over Earth as seen from orbit. An
Earth-observation satellite drifts above the planet; it is about to take the first picture of the day.
Mood: precise, beautiful, alive. Style: photoreal, IMAX 65mm. Keep the satellite's shape, foil, panels and camera
exactly as in the first frame.
ACTION: the satellite drifts slowly left to right. Sunlight slides across the gold foil and flashes along the solar
panels. The camera aperture turns a few degrees toward the Earth. Clouds move slowly far below.
CAMERA: a slow orbit around the satellite, keeping it the same size in frame. One continuous shot, no cuts.
LOCKED: the satellite keeps two panel wings and one camera; nothing is added, nothing morphs.
```

## Clip 3: the match (first and last frame)

```
STORY: The last generated shot of a short film. We pull back from orbit until the whole Earth hangs in black
space. Next, the film cuts to the same Earth inside a software dashboard. Mood: the reveal.
Style: photoreal, IMAX 65mm.
ACTION: the Earth turns very slowly. Clouds drift, the night edge on the right glows with city lights, the
atmosphere's blue rim stays sharp.
CAMERA: a steady pull back that ends exactly on the last frame: the full disk centred, filling about 72 percent of
the frame height, the Americas facing camera. Hold still for the final half second.
LOCKED: the Earth stays centred and round; no moon, no stars in front of it, no text.
```

## Cutting it

- Trim each clip to its strongest 2 seconds; generate at the model's shortest length.
- The last frame of clip 3 must match the product frame in position and size. Measure both, then set the first
  camera key of the first product shot (`ui-reel`). Or let the product's own entrance take over under a short
  dissolve from the last clip: `opening[].dissolve` in `tl.json`.
