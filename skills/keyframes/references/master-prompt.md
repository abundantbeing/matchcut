# A master prompt to copy

A complete first message for a chat image model (ChatGPT works well), for a short cinematic cold open that ends on
a frame the product can match: an object, a shape, a place. Replace the bracketed parts. Attach any references in
the order the prompt names them. The worked example in brackets is for the Orbit app in `examples/demo`: sunrise from orbit, a satellite,
then the whole Earth, which match-cuts into the app's live globe.

```
I'm making a short cinematic cold open for a product video. The product is [PRODUCT], [ONE LINE ABOUT IT].
I need [3] still images, one per message. I will animate or push into them afterwards.

STYLE (every image)
[PASTE A STYLE BLOCK FROM styles.md]
The world: [ONE SENTENCE: e.g. low Earth orbit at dawn, seen as a real astronaut would]. Palette: [e.g. deep
black, the atmosphere's thin blue line, warm city lights, white sunlight].

THE MATCH (the last image)
The last image ends on [THE SUBJECT: e.g. the whole Earth], and the next frame of the film is the same subject in
the product: [what it looks like in the product, e.g. a dot-matrix globe centred in a dark dashboard]. Match it:
[framing: e.g. a full disk centred, filling about 72 percent of the frame height], [orientation: e.g. the
Americas facing camera], [light: e.g. sunlit from the upper left, night on the right edge]. Plain black around it.

PEOPLE (only if the film has any; reference images attached in this order)
1. [NAME] (image 1): [role, hair, face, outfit, colours, prop]. [height relative to the others].
Keep each person the same in every image. Nobody looks at the camera.

STEP 1 (do this first, then stop and wait for me)
Generate image 1. If it does not read as a frame from the style above, I will correct the style here, before the
other images copy it.

STEP 2 (after I approve, one image per message, when I ask for it)
COMPOSITION RULES FOR EVERY SHOT
These are film frames, not posters. One subject, one focal point lit hardest, the rest falling into shadow or
black. Real light sources only. A scale change between shots (wide, close, whole). 16:9, room for a 2.39:1
letterbox, slight film grain, light bloom on highlights.

IMAGE 1: the world. [e.g. Earth's night side from low orbit, city lights, the first sliver of sunrise breaking
over the limb at upper right in a starburst.]
IMAGE 2: the detail. [e.g. a satellite in close-up drifting over Earth at sunrise, foil catching the light.]
IMAGE 3: the match. [e.g. the whole Earth, full disk, centred, as described under THE MATCH.]
```

## A style correction (when an image comes back looking like an AI illustration)

```
Redo image [N]. The subject is right but it looks like a digital illustration, and every later image copies this
one. It must look like a frame from [the medium in the style block]: [the rules that matter most, e.g. real optics,
natural light only, deep blacks, film grain, no glossy over-rendering, no painterly edges]. Same subject and
framing. Generate it, then stop and wait for me.
```
