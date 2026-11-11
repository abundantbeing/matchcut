#!/usr/bin/env node
// Checks this machine for what matchcut needs and says what each missing piece is for.
//   node scripts/doctor.mjs
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const rows = [];
const ok = (name, detail) => rows.push(['ok  ', name, detail]);
const miss = (name, why, fix) => rows.push(['MISS', name, `${why}. ${fix}`]);
const run = cmd => { try { return execSync(cmd, { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(); } catch { return null; } };

const major = Number(process.versions.node.split('.')[0]);
major >= 20 ? ok('Node', process.version) : miss('Node 20+', 'runs the recorder and Remotion', 'install Node 20 or newer');

const py = ['python3', 'python', 'py -3'].map(c => [c, run(`${c} --version`)]).find(([, v]) => v);
if (!py) miss('Python 3', 'storyboards, the 60 fps encoder and the score', 'install Python 3.9+');
else {
  ok('Python', py[1]);
  for (const [mod, why] of [['PIL', 'storyboards and frame checks (pip install Pillow)'], ['numpy', 'the score and voiceover mix (pip install numpy)'], ['scipy', 'the score (pip install scipy)'], ['soundfile', 'the score (pip install soundfile)']]) {
    run(`${py[0]} -c "import ${mod}"`) !== null ? ok(`  ${mod}`, 'found') : miss(`  ${mod}`, why.split(' (')[0], why.match(/\((.*)\)/)[1]);
  }
}

const ff = run('ffmpeg -version');
ff ? ok('ffmpeg', ff.split('\n')[0].slice(0, 60)) : miss('ffmpeg', 'encodes the 60 fps take (frames2cfr.py) and muxes voiceover', 'install ffmpeg (a full build: the one bundled with Remotion lacks image and filter support)');

const chrome = process.env.CHROME;
if (chrome && fs.existsSync(chrome)) ok('Chrome for Testing', chrome);
else miss('Chrome for Testing', 'records the product headless (never your everyday browser)', 'npx @puppeteer/browsers install chrome@stable, then set CHROME to its path');

const rem = fs.existsSync(path.join(process.cwd(), 'node_modules', 'remotion'));
rem ? ok('Remotion', 'in this folder') : miss('Remotion', 'renders the film (only needed in a film project)', 'cd templates/reel && npm install');

const skillDirs = ['.claude', '.codex', '.hermes', '.agents'].map(d => path.join(os.homedir(), d, 'skills', 'matchcut'));
skillDirs.some(d => fs.existsSync(d)) ? ok('Skills linked', skillDirs.filter(d => fs.existsSync(d)).join(', ')) : miss('Skills linked', 'lets your agent find matchcut', './install.sh or ./install.ps1');

for (const [s, n, d] of rows) console.log(`${s}  ${n.padEnd(22)} ${d}`);
const missing = rows.filter(r => r[0] === 'MISS').length;
console.log(missing ? `\n${missing} missing. Nothing above is needed for prompting only (keyframes, clip-prompts).` : '\nReady.');
