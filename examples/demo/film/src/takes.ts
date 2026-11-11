// The pointer path of each recorded take (written by the record step), so the cursor is redrawn in sync.
import reveal from '../public/scenes/reveal.json';
import launch from '../public/scenes/launch.json';
import sweep from '../public/scenes/sweep.json';
export type Take = { pointer: { t: number; x: number; y: number; down?: boolean }[]; marks?: { t: number; label: string }[] };
export const TAKES: Record<string, Take> = { reveal, launch, sweep };
