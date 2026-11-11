// The pointer path of each recorded take, so the film can redraw the cursor in sync.
// After recording a take, add a line:  import hero from '../public/scenes/hero.json';  and list it below.
export type Take = { pointer: { t: number; x: number; y: number; down?: boolean }[]; marks?: { t: number; label: string }[] };
export const TAKES: Record<string, Take> = {};
