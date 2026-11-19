"""widen.html: a triangle. Each side is 15 s: you, the house you are in, the city the house is in, then back to you.
Built from hexagon.html's frame (same geometry, switch and sound switch) with the corner clicks of index.html.
Also rewrites the bottom switch on every page for the new order."""
import re, os, subprocess, tempfile
os.chdir(r"C:\Users\laman\Documents\git\box-breathing")
hexp = open('hexagon.html', encoding='utf-8').read()
idx = open('index.html', encoding='utf-8').read()
SWITCH = re.search(r"const SWITCH_WAV = '([^']+)'", hexp).group(1)
CORNERS = re.search(r"const CORNER_WAVS = (\[[^\]]+\]);", idx).group(1)
css = re.search(r'<style>(.*?)</style>', hexp, re.S).group(1)
a = css.index("  .hex {"); b = css.index("  .meta {")
css = css[:a] + """  .tri { fill: hsl(var(--h) 60% calc(var(--l) * 1%)); }
  .dot { fill: var(--on); opacity: .9; }
  /* three silhouettes against the light, one inside the next: you, the house, the city */
  .sil { fill: var(--bg); }
  .label { position: absolute; left: 0; right: 0; top: 74%; height: 11%; display: grid; place-content: center; pointer-events: none; color: var(--on); }
  .phase { font-size: 15px; font-weight: 500; letter-spacing: .18em; text-transform: uppercase; opacity: .85; }

""" + css[b:]
city = [(-15, 2.5, 3), (-12, 3, 6.5), (-8.6, 2.2, 4), (-6, 3, 7), (-2.6, 5.2, 9), (3, 2.6, 5.5), (6, 3.4, 7.5), (9.8, 2.2, 4.2), (12.5, 2.5, 3)]
CITY = ''.join('<rect x="%g" y="%g" width="%g" height="%g"/>' % (x, -h, w, h) for x, w, h in city)
body = """<main>
  <h1>Widen · 2 minutes</h1>

  <div class="box" id="box" title="Click to start or pause">
    <svg viewBox="0 0 100 100" role="img" aria-label="A triangle of light. Inside it a seated figure, then the house around the figure, then the city around the house, then the figure again; a dot travels one side every fifteen seconds">
      <defs><clipPath id="in"><polygon points="50,7 98,90 2,90"/></clipPath></defs>
      <polygon class="tri" points="50,7 98,90 2,90"/>
      <g clip-path="url(#in)"><g id="scene" transform="translate(50 73) scale(24)">
        <g class="sil" id="city" opacity="0">CITY</g>
        <g class="sil" id="house" opacity="0"><rect x="-1.8" y="-2.2" width="3.6" height="2.2"/><polygon points="-2.15,-2.2 0,-3.4 2.15,-2.2"/></g>
        <g class="sil" id="you"><circle cx="0" cy="-0.82" r="0.16"/><path d="M-0.2,-0.6 Q0,-0.68 0.2,-0.6 L0.3,-0.2 L0.5,0 L-0.5,0 L-0.3,-0.2 Z"/></g>
      </g></g>
      <circle class="dot" id="dot" cx="50" cy="7" r="3"/>
    </svg>
    <div class="label" aria-live="polite"><div class="phase" id="phase">Ready</div></div>
  </div>

  <div class="meta">
    <span id="round">Round 0 / 3</span>
    <span id="left">2:15</span>
  </div>

  <div class="row">
    <button id="btn" type="button">Start</button>
    <button id="snd" type="button" class="snd" aria-pressed="true"><span class="sq"></span><span class="word"><span>Sound </span><span class="on">on</span><span class="off">off</span></span></button>
  </div>
  <p class="hint">You, the house you are in, the city around it, then you again. Fifteen seconds a side. Let your attention widen with the picture.</p>
  <nav class="nav" aria-label="Instruments"></nav>
</main>
""".replace('CITY', CITY)
js = r"""
(() => {
  // ---- the three sides: what the attention holds. Change the walk here and nowhere else. ----
  const SIDES = ['You', 'House', 'City'];
  const SIDE = 15;                                  // seconds per side
  const LAPS = 3;                                   // 3 x 45 s = 2:15
  const CYCLE = SIDE * SIDES.length, TOTAL = CYCLE * LAPS;
  const TURN = 5;                                   // seconds the picture takes to widen (or come back) after a corner
  const HOME = 5;                                   // after the last side: the picture comes back to you, then it is done
  const ZOOM = [24, 8.5, 2.3];                      // scale of the scene when it shows you, the house, the city
  const V = [[50, 7], [98, 90], [2, 90]];           // corners, clockwise from the top

  const $ = id => document.getElementById(id);
  const dot = $('dot'), box = $('box'), btn = $('btn'), scene = $('scene'), houseEl = $('house'), cityEl = $('city');
  const phaseEl = $('phase'), roundEl = $('round'), leftEl = $('left');
  const root = document.documentElement, css = getComputedStyle(root);
  const L0 = +css.getPropertyValue('--l0'), L1 = +css.getPropertyValue('--l1');
  const still = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  let running = false, elapsed = 0, last = 0, raf = 0, lastSide = -1;

  // ---- sound: recorded clicks only, one at each corner. Nothing plays before a tap. ----
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
  const SWITCH_WAV = '%SWITCH%';
  const CORNER_WAVS = %CORNERS%;
  const WAVS = { switch: SWITCH_WAV }; CORNER_WAVS.slice(0, 3).forEach((w, i) => { WAVS['corner' + i] = w; });
  const bufs = {};
  const bytes = b64 => { const bin = atob(b64), arr = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i); return arr.buffer; };
  try {                                         // decode at load, off the main context, so the first click is on time
    const off = new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(1, 8, 44100);
    for (const [key, b64] of Object.entries(WAVS)) off.decodeAudioData(bytes(b64), buf => { bufs[key] = buf; }, () => {});
  } catch (e) {}
  function play(key, gain, always) {
    const c = always ? anyAudio() : audio(); if (!c) return;
    const go = buf => { const s = c.createBufferSource(), g = c.createGain(); s.buffer = buf; g.gain.value = gain; s.connect(g).connect(c.destination); s.start(); };
    if (bufs[key]) return go(bufs[key]);
    c.decodeAudioData(bytes(WAVS[key]), buf => { bufs[key] = buf; go(buf); }, () => {});
  }
  sndBtn.addEventListener('click', e => {
    e.stopPropagation();
    sound = !sound; showSound();
    try { localStorage.setItem('instruments.sound', sound ? 'on' : 'off'); } catch (e) {}
    play('switch', 0.9, true);                  // the switch always clicks, whatever the setting
  });

  // Keep the phone's screen on while the timer runs. Released on pause, finish, or when the tab is hidden.
  let lock = null;
  async function keepAwake() {
    try { if (!lock && navigator.wakeLock) { lock = await navigator.wakeLock.request('screen'); lock.addEventListener('release', () => { lock = null; }); } } catch (e) {}
  }
  function letSleep() { if (lock) { lock.release().catch(() => {}); lock = null; } }

  const fmt = s => { s = Math.max(0, Math.ceil(s)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };
  const ease = x => { x = Math.max(0, Math.min(1, x)); return x * x * (3 - 2 * x); };

  // how wide the picture is: 0 you, 1 the house, 2 the city. It moves only in the first TURN seconds after a corner.
  function width(t) {
    if (t >= TOTAL) return 2 - 2 * ease((t - TOTAL) / (still ? 0.001 : HOME));
    const p = Math.floor((t % CYCLE) / SIDE), into = (t % CYCLE) - p * SIDE;
    const from = p > 0 ? p - 1 : (t < CYCLE ? 0 : 2);
    return from + (p - from) * ease(into / (still ? 0.001 : TURN));
  }
  function picture(u) {
    const k = Math.min(1, u), s = u <= 1 ? ZOOM[0] * Math.pow(ZOOM[1] / ZOOM[0], k) : ZOOM[1] * Math.pow(ZOOM[2] / ZOOM[1], u - 1);
    scene.setAttribute('transform', `translate(50 73) scale(${s.toFixed(4)})`);
    houseEl.setAttribute('opacity', (0.5 * ease(u / 0.6)).toFixed(3));           // each wider thing comes out of the light as it comes into view
    cityEl.setAttribute('opacity', (0.28 * ease((u - 1) / 0.6)).toFixed(3));
    box.style.setProperty('--l', L0 + (L1 - L0) * 0.3 * u);                      // the light opens a little as the view does
  }

  function render(t) {
    const home = t >= TOTAL;
    const inCycle = t % CYCLE;
    const p = home ? 0 : Math.floor(inCycle / SIDE);                 // which side, 0..2
    const f = home ? 0 : (inCycle - p * SIDE) / SIDE;                // 0..1 along it
    if (p !== lastSide || (home && lastSide !== -2)) {
      if (lastSide !== -1) play('corner' + p, 0.8, false);           // a click at each corner, not at Start
      lastSide = home ? -2 : p;
    }
    const a = V[p], b = V[(p + 1) % V.length];
    dot.setAttribute('cx', a[0] + (b[0] - a[0]) * f);
    dot.setAttribute('cy', a[1] + (b[1] - a[1]) * f);
    picture(width(t));
    root.style.setProperty('--h', 215 + 110 * (0.5 - 0.5 * Math.cos(2 * Math.PI * Math.min(t, TOTAL) / TOTAL)));
    phaseEl.textContent = SIDES[p];
    roundEl.textContent = `Round ${Math.min(LAPS, Math.floor(t / CYCLE) + 1)} / ${LAPS}`;
    leftEl.textContent = fmt(TOTAL - t);
  }

  function tick(now) {
    if (!running) return;
    const dt = Math.max(0, (now - last) / 1000);   // a frame's timestamp can sit just before the press
    elapsed += dt; last = now;
    if (elapsed >= TOTAL + HOME) { finish(); return; }
    render(elapsed);
    raf = requestAnimationFrame(tick);
  }
  function start() {
    if (elapsed >= TOTAL + HOME) { elapsed = 0; lastSide = -1; }
    running = true; last = performance.now();
    btn.textContent = 'Pause';
    keepAwake(); audio();
    raf = requestAnimationFrame(tick);
  }
  function pause() {
    running = false; cancelAnimationFrame(raf);
    letSleep();
    btn.textContent = elapsed > 0 ? 'Resume' : 'Start';
    phaseEl.textContent = 'Paused';
  }
  function finish() {
    running = false; letSleep();
    elapsed = TOTAL + HOME; lastSide = -1;
    dot.setAttribute('cx', V[0][0]); dot.setAttribute('cy', V[0][1]);
    picture(0); root.style.setProperty('--h', 215);
    phaseEl.textContent = 'You';
    roundEl.textContent = `Round ${LAPS} / ${LAPS}`; leftEl.textContent = '0:00';
    btn.textContent = 'Again';
  }

  const toggle = () => running ? pause() : start();
  btn.addEventListener('click', toggle);
  box.addEventListener('click', toggle);
  document.addEventListener('keydown', e => { if (e.code === 'Space' && !e.repeat) { e.preventDefault(); toggle(); } });
  document.addEventListener('visibilitychange', () => { if (document.hidden && running) pause(); });
  picture(0);
})();
""".replace('%SWITCH%', SWITCH).replace('%CORNERS%', CORNERS)
t = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); t.write(js); t.close()
r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True); os.unlink(t.name); assert r.returncode == 0, r.stderr[:600]
head = hexp[:hexp.index('<style>')]
head = head.replace('<title>Hex</title>', '<title>Widen</title>')
head, n = re.subn(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Two minutes: attention widens from you to the house you are in, to the city around it, and comes back.">', head); assert n == 1
head = head.replace('content="#f4f1ea"', 'content="#ece9e2"')
page = head + '<style>' + css + '</style>\n</head>\n<body>\n' + body + '\n<script>' + js + '</script>\n</body>\n</html>\n'
open('widen.html', 'w', encoding='utf-8', newline='\n').write(page)

# ---- the switch on every page, new order ----
ORDER = [('index.html', 'Box', '<rect x="8" y="8" width="84" height="84"/>'),
         ('unclench.html', 'Unclench', '<rect x="8" y="8" width="84" height="84"/><rect x="38" y="38" width="24" height="24"/>'),
         ('hexagon.html', 'Hex', '<polygon points="50,5 89,27.5 89,72.5 50,95 11,72.5 11,27.5"/>'),
         ('sit.html', 'Sit', '<polygon points="50,8 94,40 77,92 23,92 6,40"/>'),
         ('widen.html', 'Widen', '<polygon points="50,10 94,86 6,86"/>')]
icon = lambda shape: '<svg viewBox="0 0 100 100" aria-hidden="true">%s</svg>' % shape
L = '<svg class="ar" viewBox="0 0 100 100" aria-hidden="true"><path d="M94 50H10M40 20L10 50l30 30"/></svg>'
R = '<svg class="ar" viewBox="0 0 100 100" aria-hidden="true"><path d="M6 50h84M60 20l30 30-30 30"/></svg>'
for i, (p, name, shape) in enumerate(ORDER):
    pf, pn, ps = ORDER[i - 1]; nf, nn, ns = ORDER[(i + 1) % len(ORDER)]
    nav = ('  <nav class="nav" aria-label="Instruments"><a class="x" href="%s" aria-label="Previous: %s">%s<span class="n">%s</span>%s</a>'
           '<span class="x" aria-current="page">%s<span class="n">%s</span></span>'
           '<a class="x" href="%s" aria-label="Next: %s">%s<span class="n">%s</span>%s</a></nav>\n') % (pf, pn, icon(ps), pn, L, icon(shape), name, nf, nn, R, nn, icon(ns))
    s = open(p, encoding='utf-8').read()
    s, n = re.subn(r'  <nav class="nav".*?</nav>\n', lambda m: nav, s); assert n == 1, p
    open(p, 'w', encoding='utf-8', newline='\n').write(s); print(p, 'ok', len(s))
