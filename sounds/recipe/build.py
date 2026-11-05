"""Builds the gallery page: each variation as a data-URI WAV with a peak envelope drawn as SVG."""
import base64, json, os, sys
import numpy as np
from scipy.io import wavfile

D = os.path.dirname(os.path.abspath(__file__))
VARS = [
 ('1-as-written', 'As written', '14 hits speeding up over 0.6 s, snap + body + thump, then a sawtooth servo 200 → 1200 Hz into a dark room. Hum under it at −30 dB.'),
 ('2-heavy-relay', 'Heavy relay', '8 slower, bigger hits with more thump. Servo lower and longer, 140 → 900 Hz. Bigger room.'),
 ('3-self-test', 'Self-test', '20 light hits in 0.45 s, higher snap, ±4 semitones. A short bright servo and a smaller room.'),
 ('4-winding-down', 'Winding down', 'The same hits, but slowing instead of speeding up, like a ratchet running out. Servo falls 1200 → 220 Hz.'),
 ('5-clicks-and-latch', 'Clicks and latch', 'No servo. The cluster, a pause, then one heavy latch click. Hum underneath, fading.'),
 ('6-power-up', 'Power-up', 'Reversed order: a noise swell rises first, the clicks fire at the end as the self-test.'),
 ('7-two-bursts', 'Two bursts', 'Shutter-like: a burst, 150 ms of nothing, a second burst, then the servo.'),
]

TITLE = 'Click Clusters'; H1 = 'Click clusters · seven variations'; OUTNAME = 'click-clusters.html'
if len(sys.argv) > 1:
    cfg = json.load(open(sys.argv[1], encoding='utf-8')); VARS = cfg['vars']; TITLE = cfg['title']; H1 = cfg['h1']; OUTNAME = cfg['out']
rows = []
for row in VARS:
    key, name, desc = row[:3]; label = row[3] if len(row) > 3 else (key.split('-')[-1] if key.startswith('r2') else key[0])
    sr, x = wavfile.read(os.path.join(D, key + '.wav'))
    x = x.astype(np.float32) / 32767
    N = 240
    seg = np.array_split(np.abs(x), N)
    env = [float(s.max()) for s in seg]
    pts = ' '.join(f'{i / (N - 1) * 100:.2f},{(1 - e) * 20:.2f}' for i, e in enumerate(env))
    pts_lo = ' '.join(f'{i / (N - 1) * 100:.2f},{(1 + e) * 20:.2f}' for i, e in reversed(list(enumerate(env))))
    b64 = base64.b64encode(open(os.path.join(D, key + '.wav'), 'rb').read()).decode()
    dur = len(x) / sr
    rows.append(f'''
  <section>
    <h2>{label} · {name} <small>{dur:.1f} s</small></h2>
    <div class="stage">
      <button class="play" type="button" data-src="data:audio/wav;base64,{b64}" aria-label="Play {name}"><span class="sq"></span></button>
      <svg class="wave" viewBox="0 0 100 40" preserveAspectRatio="none" aria-hidden="true"><polygon points="{pts} {pts_lo}"/></svg>
    </div>
    <p class="note">{desc}</p>
  </section>''')

html = '''<title>''' + TITLE + '''</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
  /* Layout: one column; each variation is a square play button and its waveform. Single dark theme, like the instruments at night. */
  :root { --bg: #0b0c10; --fg: #ece9e2; --muted: #8a877f; --line: #2a2b31; --h: 215; --light: hsl(var(--h) 60% 44%); --ink: hsl(var(--h) 70% 72%); color-scheme: dark; }
  body { background: var(--bg); color: var(--fg); font: 300 17px/1.45 system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
         padding-block: 32px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
  main { max-width: 440px; margin: 0 auto; display: grid; gap: 28px; }
  h1 { font-size: 13px; font-weight: 500; letter-spacing: .22em; text-transform: uppercase; color: var(--muted); text-align: center; }
  p.lead { text-align: center; color: var(--muted); font-size: 15px; }
  section { border-top: 1px solid var(--line); padding-top: 20px; display: grid; gap: 12px; }
  section h2 { font-size: 15px; font-weight: 500; display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }
  section h2 small { color: var(--muted); font-weight: 300; font-size: 13px; }
  .stage { display: flex; gap: 16px; align-items: center; }
  .note { font-size: 14px; color: var(--muted); }
  button { font: inherit; color: inherit; background: none; border: 0; border-radius: 0; padding: 0; cursor: pointer; }
  button:focus-visible { outline: 2px solid var(--fg); outline-offset: 3px; }
  .play { width: 44px; height: 44px; display: grid; place-items: center; flex: none; }
  .play .sq { display: block; width: 18px; height: 18px; border: 2px solid var(--fg); box-sizing: border-box; transition: background .15s, border-color .15s, box-shadow .15s, transform .15s; }
  .play:active .sq { transform: scale(.85); }
  .play.on .sq { background: var(--light); border-color: var(--light); box-shadow: 0 0 16px var(--light); }
  .wave { flex: 1; height: 40px; min-width: 0; }
  .wave polygon { fill: var(--muted); opacity: .7; }
  .play.on + .wave polygon { fill: var(--ink); opacity: .9; }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<main>
  <h1>''' + H1 + '''</h1>
  <p class="lead">Dry mechanical clicks against a wet servo tail. Tap a square to play. Headphones show the dry-against-wet contrast; a phone speaker loses the thump.</p>
''' + ''.join(rows) + '''
</main>

<script>
(() => {
  let current = null;
  document.querySelectorAll('.play').forEach(b => {
    const a = new Audio(b.dataset.src);
    a.addEventListener('ended', () => b.classList.remove('on'));
    b.addEventListener('click', () => {
      if (current && current !== a) { current.pause(); current.currentTime = 0; document.querySelectorAll('.play.on').forEach(x => x.classList.remove('on')); }
      current = a; a.currentTime = 0; a.play(); b.classList.add('on');
    });
  });
})();
</script>
'''
open(os.path.join(D, OUTNAME), 'w', encoding='utf-8').write(html)
print(len(html) / 1e6, 'MB')
