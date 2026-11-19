"""hum.html: hum a melody, breathe in where a singer would.
Melody: "Bre, Petrunko" (Bulgarian traditional), top voice of the free violin-duet score by Violin Republic
(youtube 6_MC5bH2_EY, linked PDF), 2/4, D with E flat, F sharp, and C sharp above. Synthesized with DawDreamer + Faust
(pip install dawdreamer): soft pipes an octave apart in a small room. One round is rendered and embedded as mp3.
Also rewrites the bottom switch on every page."""
import re, os, subprocess, tempfile, base64, json, sys, numpy as np, dawdreamer as daw
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
REPO = r"C:\Users\laman\Documents\git\box-breathing"
WORK = sys.argv[1] if len(sys.argv) > 1 else tempfile.gettempdir()
FF = r"C:\Users\laman\Downloads\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
SR = 44100
BPM = 88; BEAT = 60 / BPM
D, Eb, Fs, G, A, Bb, Cs, R = 62, 63, 66, 67, 69, 70, 73, None
q, e = 1, 0.5
def bars(*bs): return [n for b in bs for n in b]
run_low = [(Eb, e), (Eb, e), (Eb, e), (Fs, e)]; run_high = [(Bb, e), (Bb, e), (Bb, e), (Cs, e)]
PHRASES = [   # each ends where the score has a rest: that is where the singer breathes
    bars([(D, q), (Eb, q)], run_low, [(Eb, q), (D, q)], [(D, q)]),                                                        # bars 1-4
    bars([(D, q), (Eb, q)], [(Eb, q), (Fs, q)], [(Eb, q), (D, q)], [(D, q), (D, q)], [(D, q), (Eb, q)], run_low, [(Eb, q), (D, q)], [(D, q)]),          # 5-12
    bars([(D, q), (Eb, q)], [(Eb, q), (Eb, e), (Fs, e)], [(Eb, q), (D, q)], [(D, q), (D, q)], [(D, q), (Eb, q)], run_low, [(G, q), (G, e), (A, e)], [(Fs, q)]),   # 13-20
    bars([(Fs, q), (G, q)], [(G, q), (A, e), (Bb, e)], [(Bb, q), (A, q)], [(A, q), (A, q)], [(D, q), (Eb, q)], run_low, [(G, q), (G, e), (A, e)], [(Fs, q)]),     # 21-28
    bars([(Fs, q), (G, q)], [(G, q), (A, e), (Bb, e)], [(Bb, q), (A, q)], [(A, q), (A, q)], [(A, q), (Bb, q)], run_high, [(Bb, q), (A, q)], [(A, q)]),            # 29-36
    bars([(A, q), (Bb, q)], [(Bb, q), (Bb, e), (Cs, e)], [(Bb, q), (A, q)], [(A, q), (A, q)], [(A, q), (Bb, q)], run_high, [(Bb, q), (A, q)], [(A, q)]),          # 37-44
    bars([(A, q), (Bb, q)], [(Bb, q), (Bb, e), (Cs, e)], [(Bb, q), (A, q)], [(A, 6)]),                                    # second ending, 49-54
]
LEAD = 2          # beats of breath before the first phrase
BREATH = 3        # beats of breath between phrases: the score's one-beat rest and one more bar
notes = []; hums = []; t = LEAD
for ph in PHRASES:
    t0 = t
    for p, d in ph: notes.append((t * BEAT, (t + d) * BEAT, p)); t += d
    hums.append([round(t0 * BEAT, 3), round(t * BEAT, 3)]); t += BREATH
ROUND = (t - BREATH + 2) * BEAT                    # two beats of quiet after the last note; the next round's lead-in follows
print('round %.2f s, %d notes, hum %.1f s, longest phrase %.1f s' % (ROUND, len(notes), sum(b - a for a, b in hums), max(b - a for a, b in hums)))

n = int((ROUND + 2.5) * SR); freq = np.zeros(n, dtype=np.float32); lvl = np.zeros(n, dtype=np.float32)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
freq[:] = hz(notes[0][2])
for i, (a, b, p) in enumerate(notes):
    ia, ib = int(a * SR), int(b * SR); freq[ia:] = hz(p)
    joined = i + 1 < len(notes) and abs(notes[i + 1][0] - b) < 1e-6
    tt = np.arange(ib - ia) / SR; dur = b - a
    start = lvl[ia - 1] if ia else 0
    env = np.where(tt < 0.05, start + (1 - start) * (0.5 - 0.5 * np.cos(np.pi * tt / 0.05)), 1 - 0.15 * np.minimum(1, (tt - 0.05) / 1.5))
    rel = 0.07 if joined else min(0.35, dur * 0.4); floor = 0.4 if joined else 0.0
    k = np.clip((tt - (dur - rel)) / rel, 0, 1); env = env * (1 - (1 - floor) * (0.5 - 0.5 * np.cos(np.pi * k)))
    lvl[ia:ib] = env
DSP = """import("stdfaust.lib");
room(w, t) = _ <: (_ * (1 - w)), ((_ <: _,_ : re.zita_rev1_stereo(30, 200, 5000, t, t * 0.7, 44100) :> _ * 0.5) * w) :> _;
f = hslider("freq", 293, 100, 2000, 0.01) : si.smooth(ba.tau2pole(0.012));
lvl = hslider("lvl", 0, 0, 1, 0.0001) : si.smooth(ba.tau2pole(0.008));
process = (os.osc(f) + os.osc(f * 1.0015) * 0.7 + os.osc(f * 2) * 0.4 + os.osc(f * 2.003) * 0.25 + os.osc(f * 3) * 0.05 + os.osc(f * 4) * 0.08) * 0.12 * lvl : room(0.28, 1.8);
"""
eng = daw.RenderEngine(SR, 256); f = eng.make_faust_processor('f'); f.set_dsp_string(DSP)
if not f.compile(): raise SystemExit('faust did not compile')
f.set_automation('/dawdreamer/freq', freq); f.set_automation('/dawdreamer/lvl', lvl)
eng.load_graph([(f, [])]); eng.render(n / SR)
x = eng.get_audio().mean(axis=0).astype(np.float64)[:n]
x = sosfilt(butter(4, 180, 'high', fs=SR, output='sos'), x)
x[-int(0.5 * SR):] *= np.linspace(1, 0, int(0.5 * SR)) ** 2
x = x / (np.abs(x).max() + 1e-9) * 0.7
wav = os.path.join(WORK, 'hum.wav'); mp3 = os.path.join(WORK, 'hum.mp3')
wavfile.write(wav, SR, (x * 32767).astype(np.int16))
subprocess.run([FF, '-y', '-loglevel', 'error', '-i', wav, '-ac', '1', '-ar', '24000', '-b:a', '32k', mp3], check=True)
B64 = base64.b64encode(open(mp3, 'rb').read()).decode(); print('mp3 %d KB' % (os.path.getsize(mp3) // 1024))

os.chdir(REPO)
hexp = open('hexagon.html', encoding='utf-8').read()
SWITCH = re.search(r"const SWITCH_WAV = '([^']+)'", hexp).group(1)
css = re.search(r'<style>(.*?)</style>', hexp, re.S).group(1)
a = css.index("  .hex {"); b = css.index("  .meta {")
css = css[:a] + """  .fig { fill: hsl(var(--h) 60% calc(var(--l) * 1%)); }
  .dot { fill: var(--on); opacity: .9; }
  .air { fill: hsl(4 100% 54%); }             /* the red square is your air: it fills on the breath in and is spent by the hum */
  #phase { min-width: 6.5em; text-align: right; } #left { min-width: 6.5em; text-align: left; }   /* the word changes, the time does not move */

""" + css[b:]
FIG = "34.5,2 65.5,2 54.7,20.5 72.5,20.5 61,42.5 80.3,42.5 80.3,57.5 61,57.5 72.5,79.5 54.7,79.5 65.5,98 34.5,98 45.3,79.5 27.5,79.5 39,57.5 19.7,57.5 19.7,42.5 39,42.5 27.5,20.5 45.3,20.5"
total = 2 * ROUND; label = '%d:%02d' % (int(np.ceil(total)) // 60, int(np.ceil(total)) % 60)
body = """<main>
  <h1>Hum · 2½ minutes</h1>

  <div class="box" id="box" title="Click to start or pause">
    <svg viewBox="0 0 100 100" role="img" aria-label="A figure of light from Bulgarian embroidery, with a red square at its centre. The square fills on each breath in and empties while you hum; a dot travels the outline once per round">
      <polygon class="fig" points="%s"/>
      <rect class="air" id="air" x="47" y="47" width="6" height="6"/>
      <circle class="dot" id="dot" cx="34.5" cy="2" r="2.6"/>
    </svg>
  </div>

  <div class="meta">
    <span id="phase">Ready</span>
    <span id="left">%s</span>
  </div>

  <div class="row">
    <button id="btn" type="button">Start</button>
    <button id="snd" type="button" class="snd" aria-pressed="true"><span class="sq"></span><span class="word"><span>Sound </span><span class="on">on</span><span class="off">off</span></span></button>
  </div>
  <p class="hint">Hum along with the melody. Where it stops, breathe in, as a singer would. The red square is your air.</p>
  <nav class="nav" aria-label="Instruments"></nav>
</main>
""" % (FIG, label)
js = r"""
(() => {
  // ---- the song: "Bre, Petrunko" (Bulgarian traditional). One round is recorded below; HUMS are the stretches to hum,
  // in seconds from the start of a round. Everything between them is a breath in. Made by sounds/recipe/hum.py. ----
  const HUMS = %HUMS%;
  const ROUND = %ROUND%, ROUNDS = 2, TOTAL = ROUND * ROUNDS;
  const AIR = [2.2, 6.6];                           // half-size of the red square: spent, full
  const V = '%FIG%'.split(' ').map(p => p.split(',').map(Number));
  const LEN = V.map((p, i) => Math.hypot(V[(i + 1) % V.length][0] - p[0], V[(i + 1) % V.length][1] - p[1]));
  const PERIM = LEN.reduce((a, b) => a + b, 0);

  const $ = id => document.getElementById(id);
  const dot = $('dot'), box = $('box'), btn = $('btn'), air = $('air');
  const phaseEl = $('phase'), leftEl = $('left');
  const root = document.documentElement, css = getComputedStyle(root);
  const L0 = +css.getPropertyValue('--l0'), L1 = +css.getPropertyValue('--l1');
  let running = false, elapsed = 0, last = 0, raf = 0, playing = -1;

  // ---- sound: the recorded melody and one click for the switch. Nothing plays before a tap. ----
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
  const SONG_MP3 = '%SONG%';
  const SRC = { switch: SWITCH_WAV, song: SONG_MP3 }, bufs = {};
  const bytes = b64 => { const bin = atob(b64), arr = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i); return arr.buffer; };
  try {                                         // decode at load, off the main context, so the first note is on time
    const off = new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(1, 8, 44100);
    for (const [key, b64] of Object.entries(SRC)) off.decodeAudioData(bytes(b64), buf => { bufs[key] = buf; }, () => {});
  } catch (e) {}
  let voices = [];                              // melody sources now sounding (a round's last echo may overlap the next round)
  function sing(at) {                           // play the round from `at` seconds in
    const c = audio(); if (!c) return;
    const go = buf => {
      if (!running || at >= buf.duration) return;
      const s = c.createBufferSource(), g = c.createGain(); s.buffer = buf; g.gain.value = 0.9; s.connect(g).connect(c.destination);
      s.start(0, Math.max(0, at)); voices.push({ s, g });
      s.onended = () => { voices = voices.filter(v => v.s !== s); };
    };
    if (bufs.song) return go(bufs.song);
    const asked = elapsed;
    c.decodeAudioData(bytes(SONG_MP3), buf => { bufs.song = buf; go.call(null, buf); at += elapsed - asked; }, () => {});
  }
  function hush() {
    if (!ctx) { voices = []; return; }
    const t = ctx.currentTime;
    voices.forEach(({ s, g }) => { try { g.gain.cancelScheduledValues(t); g.gain.setValueAtTime(g.gain.value, t); g.gain.linearRampToValueAtTime(0, t + 0.12); s.stop(t + 0.15); } catch (e) {} });
    voices = [];
  }
  function switchClick() {                      // the switch always clicks, whatever the setting
    const c = anyAudio(); if (!c) return;
    const go = buf => { const s = c.createBufferSource(), g = c.createGain(); s.buffer = buf; g.gain.value = 0.9; s.connect(g).connect(c.destination); s.start(); };
    if (bufs.switch) return go(bufs.switch);
    c.decodeAudioData(bytes(SWITCH_WAV), buf => { bufs.switch = buf; go(buf); }, () => {});
  }
  sndBtn.addEventListener('click', e => {
    e.stopPropagation();
    sound = !sound; showSound();
    try { localStorage.setItem('instruments.sound', sound ? 'on' : 'off'); } catch (e) {}
    switchClick();
    if (!sound) hush(); else if (running) { playing = Math.floor(elapsed / ROUND); sing(elapsed % ROUND); }
  });

  // Keep the phone's screen on while the timer runs. Released on pause, finish, or when the tab is hidden.
  let lock = null;
  async function keepAwake() {
    try { if (!lock && navigator.wakeLock) { lock = await navigator.wakeLock.request('screen'); lock.addEventListener('release', () => { lock = null; }); } } catch (e) {}
  }
  function letSleep() { if (lock) { lock.release().catch(() => {}); lock = null; } }

  const fmt = s => { s = Math.max(0, Math.ceil(s)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };
  const ease = x => { x = Math.max(0, Math.min(1, x)); return x * x * (3 - 2 * x); };

  function along(f) {                           // a point f of the way round the outline, from the top left corner
    let d = (f % 1) * PERIM, i = 0;
    while (d > LEN[i]) { d -= LEN[i]; i++; }
    const a = V[i], b = V[(i + 1) % V.length], k = d / LEN[i];
    return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k];
  }
  function setAir(k) {                          // k: 0 spent .. 1 full
    const h = AIR[0] + (AIR[1] - AIR[0]) * k;
    air.setAttribute('x', 50 - h); air.setAttribute('y', 50 - h); air.setAttribute('width', 2 * h); air.setAttribute('height', 2 * h);
  }
  // where in the breath we are, r seconds into a round: humming (air goes down) or breathing in (air comes up)
  function breath(r) {
    let prevEnd = 0;
    for (const [a, b] of HUMS) {
      if (r < a) return { hum: false, k: ease((r - prevEnd) / (a - prevEnd)) };
      if (r < b) return { hum: true, k: 1 - (r - a) / (b - a) };
      prevEnd = b;
    }
    return { hum: false, k: 0.0 };              // after the last note: rest, the next round's breath follows
  }

  function render(t) {
    const round = Math.floor(t / ROUND), r = t - round * ROUND;
    if (round !== playing) { playing = round; sing(r); }
    const p = along(r / ROUND);
    dot.setAttribute('cx', p[0]); dot.setAttribute('cy', p[1]);
    const b = breath(r);
    setAir(b.k);
    box.style.setProperty('--l', L0 + (L1 - L0) * (b.hum ? 0.55 : 0.55 * (1 - b.k) + 0.15));    // the figure is brighter while it sings
    root.style.setProperty('--h', 215 + 110 * (0.5 - 0.5 * Math.cos(2 * Math.PI * t / TOTAL)));
    phaseEl.textContent = b.hum ? 'Hum' : (r > HUMS[HUMS.length - 1][1] ? 'Rest' : 'Breathe in');
    leftEl.textContent = fmt(TOTAL - t);
  }

  function tick(now) {
    if (!running) return;
    const dt = Math.max(0, (now - last) / 1000);   // a frame's timestamp can sit just before the press
    elapsed += dt; last = now;
    if (elapsed >= TOTAL) { finish(); return; }
    render(elapsed);
    raf = requestAnimationFrame(tick);
  }
  function start() {
    if (elapsed >= TOTAL) elapsed = 0;
    running = true; last = performance.now(); playing = -1;
    btn.textContent = 'Pause';
    keepAwake(); audio();
    raf = requestAnimationFrame(tick);
  }
  function pause() {
    running = false; cancelAnimationFrame(raf);
    letSleep(); hush();
    btn.textContent = elapsed > 0 ? 'Resume' : 'Start';
    phaseEl.textContent = 'Paused';
  }
  function finish() {
    running = false; letSleep();                 // the last echo is left to ring out
    elapsed = TOTAL; playing = -1;
    dot.setAttribute('cx', V[0][0]); dot.setAttribute('cy', V[0][1]);
    setAir(0.2); box.style.setProperty('--l', L0); root.style.setProperty('--h', 215);
    phaseEl.textContent = 'Done'; leftEl.textContent = '0:00';
    btn.textContent = 'Again';
  }

  const toggle = () => running ? pause() : start();
  btn.addEventListener('click', toggle);
  box.addEventListener('click', toggle);
  document.addEventListener('keydown', e => { if (e.code === 'Space' && !e.repeat) { e.preventDefault(); toggle(); } });
  document.addEventListener('visibilitychange', () => { if (document.hidden && running) pause(); });
  setAir(0.2); box.style.setProperty('--l', L0);
})();
""".replace('%HUMS%', json.dumps(hums)).replace('%ROUND%', '%.3f' % ROUND).replace('%FIG%', FIG).replace('%SWITCH%', SWITCH).replace('%SONG%', B64)
js = js.replace("c.decodeAudioData(bytes(SONG_MP3), buf => { bufs.song = buf; go.call(null, buf); at += elapsed - asked; }, () => {});",
                "c.decodeAudioData(bytes(SONG_MP3), buf => { bufs.song = buf; at += elapsed - asked; go(buf); }, () => {});")
t = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); t.write(js); t.close()
r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True); os.unlink(t.name); assert r.returncode == 0, r.stderr[:600]
head = hexp[:hexp.index('<style>')].replace('<title>Hex</title>', '<title>Hum</title>').replace('content="#f4f1ea"', 'content="#ece9e2"')
head, k = re.subn(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Hum along with an old Bulgarian melody and breathe in where a singer would.">', head); assert k == 1
open('hum.html', 'w', encoding='utf-8', newline='\n').write(head + '<style>' + css + '</style>\n</head>\n<body>\n' + body + '\n<script>' + js + '</script>\n</body>\n</html>\n')

ORDER = [('index.html', 'Box', '<rect x="8" y="8" width="84" height="84"/>'),
         ('unclench.html', 'Unclench', '<rect x="8" y="8" width="84" height="84"/><rect x="38" y="38" width="24" height="24"/>'),
         ('hexagon.html', 'Hex', '<polygon points="50,5 89,27.5 89,72.5 50,95 11,72.5 11,27.5"/>'),
         ('sit.html', 'Sit', '<polygon points="50,8 94,40 77,92 23,92 6,40"/>'),
         ('widen.html', 'Widen', '<polygon points="50,10 94,86 6,86"/>'),
         ('hum.html', 'Hum', '<polygon points="%s"/>' % FIG)]
icon = lambda shape: '<svg viewBox="0 0 100 100" aria-hidden="true">%s</svg>' % shape
L = '<svg class="ar" viewBox="0 0 100 100" aria-hidden="true"><path d="M94 50H10M40 20L10 50l30 30"/></svg>'
Rr = '<svg class="ar" viewBox="0 0 100 100" aria-hidden="true"><path d="M6 50h84M60 20l30 30-30 30"/></svg>'
for i, (p, name, shape) in enumerate(ORDER):
    pf, pn, ps = ORDER[i - 1]; nf, nn, ns = ORDER[(i + 1) % len(ORDER)]
    nav = ('  <nav class="nav" aria-label="Instruments"><a class="x" href="%s" aria-label="Previous: %s">%s<span class="n">%s</span>%s</a>'
           '<span class="x" aria-current="page">%s<span class="n">%s</span></span>'
           '<a class="x" href="%s" aria-label="Next: %s">%s<span class="n">%s</span>%s</a></nav>\n') % (pf, pn, icon(ps), pn, L, icon(shape), name, nf, nn, Rr, nn, icon(ns))
    s = open(p, encoding='utf-8').read()
    s, k = re.subn(r'  <nav class="nav".*?</nav>\n', lambda m: nav, s); assert k == 1, p
    open(p, 'w', encoding='utf-8', newline='\n').write(s); print(p, 'ok', len(s))
