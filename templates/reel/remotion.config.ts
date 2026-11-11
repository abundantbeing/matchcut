// Render settings for every `npx remotion` command in this project (CLI flags still override).
import { Config } from '@remotion/cli/config';

const browser = process.env.REMOTION_BROWSER;
if (browser) Config.setBrowserExecutable(browser);
Config.setChromiumOpenGlRenderer('angle');
// JPEG q95 intermediates: the default q80 blocks up soft dark gradients
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(95);
// tag the encode BT.709 so every player decodes the same colours
Config.setColorSpace('bt709');
Config.setDelayRenderTimeoutInMilliseconds(120000);
Config.setOverwriteOutput(true);
