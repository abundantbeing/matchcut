#!/usr/bin/env bash
# The recording browser: headless Chrome for Testing at device scale 2, its own throwaway profile, muted.
# Never the owner's own browser or profile. Delete the profile folder when the film is done.
#   CHROME=/path/to/chrome CDP_PORT=9447 PROFILE=/tmp/reel-profile bash launch.sh
: "${CHROME:?set CHROME to a Chrome for Testing binary}"
PORT="${CDP_PORT:-9447}"
PROFILE="${PROFILE:-$(mktemp -d)/reel-profile}"
exec "$CHROME" --headless=new --force-device-scale-factor=2 \
  --remote-debugging-port="$PORT" --user-data-dir="$PROFILE" \
  --no-first-run --no-default-browser-check --window-size=1280,720 --mute-audio --autoplay-policy=user-gesture-required \
  --disable-background-timer-throttling --disable-renderer-backgrounding --disable-backgrounding-occluded-windows \
  --enable-gpu --ignore-gpu-blocklist --use-angle=d3d11 --enable-unsafe-swiftshader about:blank
