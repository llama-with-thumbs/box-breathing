"""Builds hexagon.html: a hexagon of light, a dot walking its edge 4 s per side, a tone gliding through six notes."""
import re, os, subprocess, tempfile
os.chdir(r"C:\Users\laman\Documents\git\box-breathing")
idx = open('index.html', encoding='utf-8').read()
switch_wav = re.search(r"const SWITCH_WAV = '([^']+)'", idx).group(1)

page = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hexagon</title>
<meta name="description" content="Two minutes: a dot walks a hexagon, four seconds a side, and a tone moves through six notes.">
<meta name="theme-color" content="#f4f1ea">
<style>
  :root {
    --bg: #ece9e2; --fg: #1a1a1a; --muted: #7a766e; --on: #ffffff;
    --l0: 44; --l1: 66;     /* lightness of the light: lowest note, highest note */
    --glow: .35;
    --h: 215;               /* hue of the light; drifts over the session */
    --light: hsl(var(--h) 60% 44%);
    --ink: hsl(var(--h) 70% 72%);
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #0b0c10; --fg: #ece9e2; --muted: #8a877f; --l0: 24; --l1: 46; --glow: .6; }
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; }
  body {
    background: var(--bg); color: var(--fg);
    font: 300 18px/1.4 system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
    display: grid; place-items: center; padding: 16px;
    -webkit-tap-highlight-color: transparent;
  }
  main { width: min(100%, 420px); display: grid; gap: 36px; justify-items: center; text-align: center; }
  h1 { font-size: 13px; font-weight: 500; letter-spacing: .22em; text-transform: uppercase; color: var(--muted); }

  .box { position: relative; width: min(76vw, 310px); aspect-ratio: 1; cursor: pointer; user-select: none; --l: var(--l0); }
  .box svg { position: absolute; inset: 0; width: 100%; height: 100%; display: block; overflow: visible;
             filter: drop-shadow(0 0 45px hsl(var(--h) 60% calc(var(--l) * 1%) / var(--glow))); }
  .hex { fill: hsl(var(--h) 60% calc(var(--l) * 1%)); }
  .dot { fill: var(--on); opacity: .9; }
  .label { position: absolute; inset: 0; display: grid; place-content: center; gap: 8px; pointer-events: none; color: var(--on); }
  .phase { font-size: 15px; font-weight: 500; letter-spacing: .18em; text-transform: uppercase; opacity: .85; }
  .count { font-size: min(64px, 14vw); font-weight: 200; line-height: 1; white-space: nowrap; }

  .meta { display: flex; gap: 32px; color: var(--muted); font-size: 15px; font-variant-numeric: tabular-nums; }
  button {
    font: inherit; font-size: 14px; font-weight: 500; letter-spacing: .1em; text-transform: uppercase;
    border: 0; background: var(--fg); color: var(--bg); padding: 12px 32px; cursor: pointer; border-radius: 0;
  }
  button:hover, button:focus-visible { opacity: .85; outline: none; }
  .hint { color: var(--muted); font-size: 14px; }
  .x { display: inline-flex; align-items: center; min-height: 44px; padding: 10px 8px; color: var(--muted); font-size: 12px; font-weight: 500; letter-spacing: .18em; text-transform: uppercase; text-decoration: none; }
  .x:hover, .x:focus-visible { color: var(--fg); outline: none; }

  .row { display: flex; gap: 20px; align-items: center; justify-content: center; flex-wrap: wrap; }
  .snd { display: inline-flex; align-items: center; gap: 12px; padding: 8px 4px; min-height: 44px; background: none; border: 0; color: var(--muted); letter-spacing: .1em; }
  .snd:hover, .snd:focus-visible { opacity: 1; outline: none; }
  .snd:focus-visible .sq { outline: 2px solid var(--fg); outline-offset: 3px; }
  .snd .sq { display: block; width: 18px; height: 18px; border: 2px solid var(--fg); box-sizing: border-box; transition: background .4s, border-color .4s, box-shadow .4s, transform .15s; }
  .snd:active .sq { transform: scale(.85); }
  .snd[aria-pressed="true"] .sq { background: var(--light); border-color: var(--light); box-shadow: 0 0 16px var(--light); }
  .snd .word { display: inline-grid; grid-auto-flow: column; align-items: baseline; transition: color .5s, text-shadow .5s; }
  .snd .word > :first-child { grid-area: 1 / 1; white-space: pre; }
  .snd .on, .snd .off { grid-area: 1 / 2; visibility: hidden; }
  .snd[aria-pressed="true"] .on { visibility: visible; }
  .snd[aria-pressed="false"] .off { visibility: visible; }
  .snd[aria-pressed="true"] .word { color: var(--ink); text-shadow: 0 0 12px hsl(var(--h) 80% 60% / .7); }
  @media (prefers-reduced-motion: reduce) { .box svg { filter: none; } }
</style>
</head>
<body>
<main>
  <h1>Hexagon · 2 minutes</h1>

  <div class="box" id="box" title="Click to start or pause">
    <svg viewBox="0 0 100 100" role="img" aria-label="A hexagon of light; a dot travels one side every four seconds; the light is brighter on higher notes">
      <polygon class="hex" points="50,0 93.3,25 93.3,75 50,100 6.7,75 6.7,25"/>
      <circle class="dot" id="dot" cx="50" cy="0" r="3"/>
    </svg>
    <div class="label" aria-live="polite">
      <div class="phase" id="phase">Ready</div>
      <div class="count" id="count">6 · 4</div>
    </div>
  </div>

  <div class="meta">
    <span id="round">Lap 0 / 5</span>
    <span id="left">2:00</span>
  </div>

  <div class="row">
    <button id="btn" type="button">Start</button>
    <button id="snd" type="button" class="snd" aria-pressed="true"><span class="sq"></span><span class="word"><span>Sound </span><span class="on">on</span><span class="off">off</span></span></button>
  </div>
  <p class="hint">Six notes, four seconds each. Follow the dot. Space starts or pauses.</p>
  <a class="x" href="index.html">← Box breathing</a>
</main>

<script>
(() => {
  // ---- the six sides: note name and frequency. Change the walk here and nowhere else. ----
  const NOTES = [['A3', 220.00], ['C3', 130.81], ['G3', 196.00], ['C♯4', 277.18], ['G3', 196.00], ['C♯4', 277.18]];
  const SIDE = 4;                                   // seconds per side
  const LAPS = 5;                                   // 5 × 24 s = 2:00
  const CYCLE = SIDE * NOTES.length, TOTAL = CYCLE * LAPS;
  const GLIDE = 0.5;                                // time constant of the slide into a note, s (about 1.5 s to arrive)
  const V = [[50, 0], [93.3, 25], [93.3, 75], [50, 100], [6.7, 75], [6.7, 25]];   // corners, clockwise from the top

  const $ = id => document.getElementById(id);
  const dot = $('dot'), box = $('box'), btn = $('btn');
  const phaseEl = $('phase'), countEl = $('count'), roundEl = $('round'), leftEl = $('left');
  const root = document.documentElement, css = getComputedStyle(root);
  const L0 = +css.getPropertyValue('--l0'), L1 = +css.getPropertyValue('--l1');
  const lo = Math.min(...NOTES.map(n => n[1])), hi = Math.max(...NOTES.map(n => n[1]));
  const height = f => Math.log(f / lo) / Math.log(hi / lo);       // 0 lowest note .. 1 highest
  let running = false, elapsed = 0, last = 0, raf = 0, lastSide = -1, lit = height(NOTES[0][1]);

  // ---- sound: a tone made here, one recorded click for the switch. Nothing plays before a tap. ----
  let ctx = null, sound = true;
  try { sound = localStorage.getItem('instruments.sound') !== 'off'; } catch (e) {}
  const sndBtn = $('snd');
  const showSound = () => sndBtn.setAttribute('aria-pressed', String(sound));
  showSound();
  const mkCtx = () => {                         // on iPhone the 'playback' session keeps the ring switch from muting it
    const c = new (window.AudioContext || window.webkitAudioContext)();
    try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch (e) {}
    return c;
  };
  const anyAudio = () => { try { if (!ctx) ctx = mkCtx(); if (ctx.state === 'suspended') ctx.resume(); return ctx; } catch (e) { return null; } };
  const audio = () => sound ? anyAudio() : null;
  const SWITCH_WAV = '%(switch)s';
  let switchBuf = null;
  const bytes = () => { const bin = atob(SWITCH_WAV), arr = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i); return arr.buffer; };
  try { new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(1, 8, 44100).decodeAudioData(bytes(), b => { switchBuf = b; }, () => {}); } catch (e) {}
  function switchClick() {                      // the switch always clicks, whatever the setting
    const c = anyAudio(); if (!c) return;
    const go = buf => { const s = c.createBufferSource(), g = c.createGain(); s.buffer = buf; g.gain.value = 0.9; s.connect(g).connect(c.destination); duck(Math.min(0.5, buf.duration)); s.start(); };
    if (switchBuf) return go(switchBuf);
    c.decodeAudioData(bytes(), b => { switchBuf = b; go(b); }, () => {});
  }
  sndBtn.addEventListener('click', e => {
    e.stopPropagation();
    sound = !sound; showSound();
    try { localStorage.setItem('instruments.sound', sound ? 'on' : 'off'); } catch (e) {}
    switchClick(); if (!sound) toneOff(); else if (running) toneOn(NOTES[Math.max(0, lastSide)][1]);
  });

  // the tone: a sine with its octave and a trace of the octave above that. Octaves only, so nothing rubs; the
  // upper two carry C3 (131 Hz) on a phone speaker, which cannot play the note itself. It slides into each note.
  const MIX = [1, 0.4, 0.1];
  let oscs = null, gain = null, dip = null;
  function toneOn(f) {
    const c = audio(); if (!c || oscs) return;
    const t = c.currentTime;
    gain = c.createGain(); gain.gain.setValueAtTime(0, t); gain.gain.linearRampToValueAtTime(0.35, t + 2);
    dip = c.createGain();
    oscs = MIX.map((a, i) => { const o = c.createOscillator(), v = c.createGain(); o.type = 'sine'; o.frequency.value = f * (1 << i); v.gain.value = a; o.connect(v).connect(gain); o.start(); return o; });
    gain.connect(dip).connect(c.destination);
  }
  function toneTo(f) { if (oscs) oscs.forEach((o, i) => o.frequency.setTargetAtTime(f * (1 << i), ctx.currentTime, GLIDE)); }
  function duck(sec) {
    if (!dip) return;
    const t = ctx.currentTime;
    dip.gain.cancelScheduledValues(t); dip.gain.setTargetAtTime(0.3, t, 0.01); dip.gain.setTargetAtTime(1, t + sec, 0.05);
  }
  function toneOff() {
    if (!oscs) return;
    const os = oscs, g = gain, t = ctx.currentTime; oscs = gain = dip = null;
    g.gain.cancelScheduledValues(t); g.gain.setValueAtTime(g.gain.value, t); g.gain.linearRampToValueAtTime(0, t + 1.5);
    os.forEach(o => o.stop(t + 1.6));
  }

  // Keep the phone's screen on while the timer runs. Released on pause, finish, or when the tab is hidden.
  let lock = null;
  async function keepAwake() {
    try { if (!lock && navigator.wakeLock) { lock = await navigator.wakeLock.request('screen'); lock.addEventListener('release', () => { lock = null; }); } } catch (e) {}
  }
  function letSleep() { if (lock) { lock.release().catch(() => {}); lock = null; } }

  const fmt = s => { s = Math.max(0, Math.ceil(s)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };

  function render(t, dt) {
    const inCycle = t % CYCLE;
    const p = Math.floor(inCycle / SIDE);           // which side, 0..5
    const f = (inCycle - p * SIDE) / SIDE;          // 0..1 along it
    if (p !== lastSide) { lastSide = p; toneTo(NOTES[p][1]); }
    const a = V[p], b = V[(p + 1) % V.length];
    dot.setAttribute('cx', a[0] + (b[0] - a[0]) * f);
    dot.setAttribute('cy', a[1] + (b[1] - a[1]) * f);
    // the light follows the note at the tone's own pace: higher is brighter
    lit += (height(NOTES[p][1]) - lit) * (1 - Math.exp(-dt / GLIDE));
    box.style.setProperty('--l', L0 + (L1 - L0) * lit);
    root.style.setProperty('--h', 215 + 110 * (0.5 - 0.5 * Math.cos(2 * Math.PI * t / TOTAL)));
    phaseEl.textContent = 'Side ' + (p + 1);
    countEl.textContent = NOTES[p][0];
    roundEl.textContent = `Lap ${Math.min(LAPS, Math.floor(t / CYCLE) + 1)} / ${LAPS}`;
    leftEl.textContent = fmt(TOTAL - t);
  }

  function tick(now) {
    if (!running) return;
    const dt = Math.max(0, (now - last) / 1000);   // a frame's timestamp can sit just before the press
    elapsed += dt; last = now;
    if (elapsed >= TOTAL) { finish(); return; }
    render(elapsed, dt);
    raf = requestAnimationFrame(tick);
  }
  function start() {
    if (elapsed >= TOTAL) elapsed = 0;
    running = true; last = performance.now();
    btn.textContent = 'Pause';
    keepAwake();
    lastSide = Math.floor((elapsed % CYCLE) / SIDE);
    toneOn(NOTES[lastSide][1]);
    raf = requestAnimationFrame(tick);
  }
  function pause() {
    running = false; cancelAnimationFrame(raf);
    letSleep(); toneOff();
    btn.textContent = elapsed > 0 ? 'Resume' : 'Start';
    phaseEl.textContent = 'Paused';
  }
  function finish() {
    running = false; letSleep(); toneOff();
    elapsed = TOTAL; lastSide = -1; lit = height(NOTES[0][1]);
    dot.setAttribute('cx', V[0][0]); dot.setAttribute('cy', V[0][1]);
    box.style.setProperty('--l', L0 + (L1 - L0) * lit); root.style.setProperty('--h', 215);
    phaseEl.textContent = 'Done'; countEl.textContent = '·';
    roundEl.textContent = `Lap ${LAPS} / ${LAPS}`; leftEl.textContent = '0:00';
    btn.textContent = 'Again';
  }

  const toggle = () => running ? pause() : start();
  btn.addEventListener('click', toggle);
  box.addEventListener('click', toggle);
  document.addEventListener('keydown', e => { if (e.code === 'Space' && !e.repeat) { e.preventDefault(); toggle(); } });
  document.addEventListener('visibilitychange', () => { if (document.hidden && running) pause(); });
  box.style.setProperty('--l', L0 + (L1 - L0) * lit);
})();
</script>
</body>
</html>
"""
page = page.replace('%(switch)s', switch_wav)
open('hexagon.html', 'w', encoding='utf-8', newline='\n').write(page)

# the way there: a second grey word on the breathing page
old = '  <a class="x" href="unclench.html">Unclench →</a>\n'
if idx.count(old) == 1: idx = idx.replace(old, '  <div class="row"><a class="x" href="unclench.html">Unclench →</a><a class="x" href="hexagon.html">Hexagon →</a></div>\n')
open('index.html', 'w', encoding='utf-8', newline='\n').write(idx)

for p, s in (('hexagon.html', page), ('index.html', idx)):
    js = re.search(r'<script>(.*?)</script>', s, re.S).group(1)
    t = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); t.write(js); t.close()
    r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True); os.unlink(t.name)
    print(p, 'syntax ok' if r.returncode == 0 else r.stderr[:400], os.path.getsize(p) // 1024, 'KB')
