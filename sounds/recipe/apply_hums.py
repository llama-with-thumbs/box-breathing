"""index.html: hum H6 + slow beat + a lean toward each corner. unclench.html: hum U4 with a breath-shaped drift; the
step cue becomes the corner click (S4); the exhale slide stays. Hums duck under clicks (rule 12)."""
import re, os, subprocess, tempfile
os.chdir(r"C:\Users\laman\Documents\git\box-breathing")

def check(p, s):
    js = re.search(r'<script>(.*?)</script>', s, re.S).group(1)
    t = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); t.write(js); t.close()
    r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True); os.unlink(t.name)
    print(p, 'syntax ok' if r.returncode == 0 else r.stderr[:400], os.path.getsize(p) // 1024, 'KB')

def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:70], s.count(a)); return s.replace(a, b)

NOISE = """    const n = c.createBufferSource(), buf = c.createBuffer(1, c.sampleRate * 2, c.sampleRate), d = buf.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    n.buffer = buf; n.loop = true;
"""
DUCK = """  function humDuck(sec) {                       // the hum steps aside under a click, so the two never add past 1 (rule 12)
    if (!hum) return;
    const t = ctx.currentTime, g = hum.out.gain;
    g.cancelScheduledValues(t); g.setTargetAtTime(hum.level * 0.3, t, 0.01); g.setTargetAtTime(hum.level, t + sec, 0.12);
  }
  function humOff() {
    if (!hum) return;
    const h = hum, t = ctx.currentTime; hum = null;
    h.out.gain.cancelScheduledValues(t); h.out.gain.setValueAtTime(h.out.gain.value, t); h.out.gain.linearRampToValueAtTime(0, t + 1.5);
    setTimeout(() => { try { h.stop(); h.out.disconnect(); } catch (e) {} }, 1700);
  }
"""

# ---------------- index.html ----------------
p = 'index.html'; s = open(p, encoding='utf-8').read()
HUM_INDEX = """  // ---- the hum (gallery H6 with H1's beat): 330 Hz, its octave a quarter-hertz off so the pair swells every 4 s, a
  // faint third harmonic, and a band of air (300-1500 Hz) that breathes once per box. It leans up to 25 cents as the
  // dot nears a corner. Level 0.22; ducks under the clicks. Nothing under 180 Hz: a phone speaker can hold all of it.
  let hum = null;
  function humOn() {
    const c = audio(); if (!c || hum) return;
    const t = c.currentTime, out = c.createGain(), level = 0.22;
    out.gain.setValueAtTime(0, t); out.gain.linearRampToValueAtTime(level, t + 2.5);
    const base = [330, 660.25, 1320], mix = [0.6, 0.24, 0.08];
    const voices = base.map((f, i) => { const o = c.createOscillator(), v = c.createGain(); o.type = 'sine'; o.frequency.value = f; v.gain.value = mix[i]; o.connect(v).connect(out); o.start(); return o; });
""" + NOISE + """    const bpf = c.createBiquadFilter(); bpf.type = 'bandpass'; bpf.frequency.value = 670; bpf.Q.value = 0.55;
    const air = c.createGain(); air.gain.value = 0.3;
    n.connect(bpf).connect(air).connect(out); n.start();
    out.connect(c.destination);
    hum = { out, level, base, voices, air, stop: () => { voices.forEach(o => o.stop()); n.stop(); } };
  }
  function humFollow(f, box) {                  // f: 0..1 along the side; box: 0..1 through the 16 s cycle
    if (!hum) return;
    const t = ctx.currentTime, k = Math.pow(2, 25 * f * f / 1200);
    hum.voices.forEach((o, i) => o.frequency.setTargetAtTime(hum.base[i] * k, t, 0.3));
    hum.air.gain.setTargetAtTime(0.3 * (0.6 + 0.4 * (0.5 - 0.5 * Math.cos(2 * Math.PI * box))), t, 0.25);
  }
""" + DUCK
s = rep(s, "  function toneOff() {}                       // nothing sustained on this page\n", HUM_INDEX)
s = rep(s, "    switchClick(); if (!sound) toneOff();", "    switchClick(); if (!sound) humOff(); else if (running) humOn();")
s = rep(s, "    toneOff();\n", "    humOff();\n", 2)
s = rep(s, "s.start(); };", "humDuck(buf.duration); s.start(); };")
s = rep(s, "    const f = (inCycle - p * PHASE) / PHASE;        // 0..1 along that side\n",
           "    const f = (inCycle - p * PHASE) / PHASE;        // 0..1 along that side\n    humFollow(f, inCycle / CYCLE);\n")
m = re.search(r"  function start\(\) \{\n(.*?)    running = true;\n", s, re.S); assert m
s = s.replace(m.group(0), m.group(0) + "    humOn();\n")
s = rep(s, "  // ---- sound: two recorded clicks, nothing sustained. Nothing plays before a tap. One setting for all instruments. ----",
           "  // ---- sound: two recorded clicks and a hum made here. Nothing plays before a tap. One setting for all instruments. ----")
s = rep(s, "Space starts or pauses. A click marks each corner.", "Space starts or pauses. A hum runs; a click marks each corner.")
corner1 = re.search(r"const CORNER_WAVS = \['([^']+)'", s).group(1)
open(p, 'w', encoding='utf-8', newline='\n').write(s); check(p, s)

# ---------------- unclench.html ----------------
p = 'unclench.html'; s = open(p, encoding='utf-8').read()
HUM_UN = """  // ---- the hum (gallery U4): C4 and the C two octaves up, a third of a hertz off so they beat slowly, with a band of
  // air (300-700 Hz), in a 2 s dark room. It breathes: up 40 cents over 4 s, down over 6 s, the whole way through.
  // Level 0.22; ducks under the clicks. Nothing under 180 Hz.
  let hum = null;
  function humOn() {
    const c = audio(); if (!c || hum) return;
    const t = c.currentTime, out = c.createGain(), level = 0.22;
    out.gain.setValueAtTime(0, t); out.gain.linearRampToValueAtTime(level, t + 2.5);
    const base = [262, 1048.3], mix = [0.7, 0.18];
    const dry = c.createGain(); dry.gain.value = 0.6;
    const voices = base.map((f, i) => { const o = c.createOscillator(), v = c.createGain(); o.type = 'sine'; o.frequency.value = f; v.gain.value = mix[i]; o.connect(v).connect(dry); o.start(); return o; });
""" + NOISE + """    const bpf = c.createBiquadFilter(); bpf.type = 'bandpass'; bpf.frequency.value = 460; bpf.Q.value = 1.1;
    const air = c.createGain(); air.gain.value = 0.35;
    n.connect(bpf).connect(air).connect(dry); n.start();
    const ir = c.createBuffer(1, c.sampleRate * 2, c.sampleRate), e = ir.getChannelData(0);   // the room: 2 s of dying noise
    for (let i = 0; i < e.length; i++) e[i] = (Math.random() * 2 - 1) * Math.exp(-6.9 * i / e.length);
    const room = c.createConvolver(); room.buffer = ir; room.normalize = true;
    const dark = c.createBiquadFilter(); dark.type = 'lowpass'; dark.frequency.value = 1500;
    const wet = c.createGain(); wet.gain.value = 0.4;
    dry.connect(out); dry.connect(room).connect(dark).connect(wet).connect(out);
    out.connect(c.destination);
    hum = { out, level, base, voices, stop: () => { voices.forEach(o => o.stop()); n.stop(); } };
  }
  function humBreathe(sec) {                    // a 10 s breath: in over 4, out over 6, up to 40 cents
    if (!hum) return;
    const u = (sec % 10) / 10, b = u < 0.4 ? u / 0.4 : 1 - (u - 0.4) / 0.6, e = b * b * (3 - 2 * b);
    const t = ctx.currentTime, k = Math.pow(2, 40 * e / 1200);
    hum.voices.forEach((o, i) => o.frequency.setTargetAtTime(hum.base[i] * k, t, 0.3));
  }
""" + DUCK
s = rep(s, "  function toneOff() {}                       // nothing sustained on this page\n", HUM_UN)
s = rep(s, "    switchClick(); if (!sound) toneOff();", "    switchClick(); if (!sound) humOff(); else if (running) humOn();")
s = rep(s, "s.start(); };", "humDuck(buf.duration); s.start(); };")
# the step cue: the corner click from the breathing page (one family)
s = rep(s, "  const SWITCH_WAV = '", "  const STEP_WAV = '%s';   // the breathing page's corner click, as the step cue\n  const SWITCH_WAV = '" % corner1)
s = rep(s, "typeof CORNER_WAV === 'string' ? { switch: SWITCH_WAV, corner: CORNER_WAV } : { switch: SWITCH_WAV }", "{ switch: SWITCH_WAV, step: STEP_WAV }")
m = re.search(r"  function ping\(\) \{.*?\n  \}\n", s, re.S); assert m
s = s.replace(m.group(0), "  const ping = () => play('step', STEP_WAV, 0.8, false);   // a step is over: the click\n")
s = rep(s, "    inStep += dt; actual += dt;\n", "    inStep += dt; actual += dt;\n    humBreathe(actual);\n")
s = rep(s, "  function resume() { running = true; last = performance.now(); keepAwake(); raf = requestAnimationFrame(tick); }",
           "  function resume() { running = true; last = performance.now(); keepAwake(); humOn(); raf = requestAnimationFrame(tick); }")
s = rep(s, "  function pause()  { running = false; cancelAnimationFrame(raf); letSleep(); }",
           "  function pause()  { running = false; cancelAnimationFrame(raf); letSleep(); humOff(); }")
s = rep(s, "  // ---- two recorded clicks, embedded so the page stays one file (8 kHz wav; from sounds/README.md) ----",
           "  // ---- recorded clicks, embedded so the page stays one file (8 kHz wav; from sounds/README.md) ----")
s = rep(s, "A ping marks each step.", "A click marks each step.")
open(p, 'w', encoding='utf-8', newline='\n').write(s); check(p, s)
