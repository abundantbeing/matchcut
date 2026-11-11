import React from 'react';
import { Composition } from 'remotion';
import { Reel } from './Reel';
import tl from './tl.json';

export const RemotionRoot: React.FC = () => (
  <Composition id="Reel" component={Reel} durationInFrames={Math.round(tl.total * tl.fps)} fps={tl.fps} width={1920} height={1080} />
);
