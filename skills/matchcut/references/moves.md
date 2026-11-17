# Moves

The beats message (step 2) offers one move per beat. These are matchcut's own: each says why it works, how to build
it with what the skills already have, and one way to push it further. Offer two for a beat when you are unsure, and
let the person pick. Use each move once in a film; a move used twice is a habit.

## Five questions

Ask them of the beats before the person says yes, and again of the render before delivering. Answer each in a line.

1. **What stays the same across the match cut?** The hero object, at the same size, place and angle on both sides.
   If something else changes too (its colour, its tilt), the cut reads as a jump, not a match.
2. **What is each shot about, in three words?** If it takes more, the shot is doing two things: split it or cut one.
   The caption is usually those three words.
3. **What did we leave out?** Name one thing removed from the film. A film with nothing removed has not been edited.
4. **Where does the eye go first?** In every frame the hero should be the brightest or the only coloured thing.
   Squint at the stills and the contact sheet: if something else wins, dim it or crop it.
5. **What does the open promise, and when is it paid?** Name the second. A cold open that asks nothing has no
   payoff to land.

Then the heroes: the 3 to 5 moments (`tl.json` `heroes`) that land exactly on the music with the biggest sounds. If
everything is a hero, nothing is.

## Cold open

- **Grow into the frame.** The default. The subject grows across the clips until it fills the space the product
  will fill. Why: the viewer's eye is already where the product appears. Push it: the last clip's camera is the
  first camera key of the product, measured in pixels.
- **Too close to read.** Open so close on the hero object (its edge, its surface, a seam of light) that it is a
  landscape, then pull back until it is a thing. Why: a puzzle makes people lean in, and the match cut answers it.
  Build: three stills of the same object at three distances (`keyframes`), one single-image clip each.
- **Lights out, one light.** Hold near black, then the hero object lights first and the world after it. Why: the
  first light is where everyone looks. Build: a still lit only from the object; clip prompt "only the object glows,
  then the room fades up". Push it: the light it gives off is the film's glow colour, the same one the cuts bloom in.
- **The object travels.** The same hero object passes through two or three places in the story before it lands
  flat. Why: one constant carried across changing worlds is already a match cut, so the real one feels inevitable.

## The match cut

- **Bloom.** The default. The object flat to camera, a bloom in the glow colour, the same object live in the
  product, and the letterbox opens. A hero: hit and tail.
- **Stop, then land.** A silence just before the cut, so the hit lands into nothing: `stops` in `score.json` for
  the code band; with a produced song, ask for the break in the prompt (`song_prompt.py --breath`) and cut on the
  bar after it. The biggest move a film has: use it on the match cut or the payoff, never both.
- **Dissolve.** `dissolve` on the last still: no bloom, no hit, the generated world fades over the product's own
  entrance. For a calm film, where a bang would be wrong.

## Title intro (a product reel, no generated pictures)

- **Wordmark, cut, swirl.** The default (`intro`): dots land as the wordmark, a line of light cuts it, the dots swirl
  into the product's first shape. Push it: aim the swirl (`into`) at the hero object, so the intro ends where the
  product begins.

## The product

- **Cut into the action.** Every shot opens framed on what it is about, just before it moves (`check-tl.mjs`
  enforces it).
- **One thing alone.** Push in (`cam` `s` 1.8 to 2.2) until the one element that changes fills a third of the frame,
  then hold while it changes. Why: one idea per shot, and the footage is sharp enough at 2x to carry it.
- **Same frame, new state.** Two takes framed by the same camera key, cut on the beat: empty, then full; before,
  then after. Only the content changes, so the change is all anyone sees.
- **In the hand.** A `phone` shot rises in for the mobile view. Use it once, where the phone is the point.
- **Say the result.** Captions name what the viewer gets ("EVERY FRAME KEPT"), not the feature ("60 FPS CAPTURE
  ENGINE"). 2 to 6 words, voices rotating.

## The payoff

- **All of it at once.** Every tier, every result, the full gallery, in one pull back on the finished state. A hero.
- **The number moves.** One real count changing in the product, held until it can be read.
- **Before and after on the bar.** The same framing as an earlier shot, now finished. The callback is the proof.

## End card

- **Callback.** The mark echoes the hero object (its shape, its glow), so the film closes where it opened.
- **One true fact, landed.** The name, the install line, one fact the film proved. The end card is a hero; let the
  last chord ring under it, never a fade.

## When the person names a film they love

Keep why it works and change what it does, at least one change per borrowed move. Never rebuild a shot.

- **Swap who does it.** A hand did it there; here the hero object does it.
- **Swap the scale.** A chip becomes a landscape; a planet becomes a badge.
- **Make it literal.** "Connects" becomes two objects snapping together.
- **Run it backwards.** Open on the finished state and take it apart.
- **Constrain it.** One take, one colour, one word.
