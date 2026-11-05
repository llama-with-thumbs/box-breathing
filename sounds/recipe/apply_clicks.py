"""Puts the two recorded clicks into both pages: the corner click on index.html, the switch click on both."""
import json, os, re, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
E = json.load(open(os.path.join(HERE, 'embed.json')))
os.chdir(r"C:\Users\laman\Documents\git\box-breathing")

PLAYER = """  // ---- two recorded clicks, embedded so the page stays one file (8 kHz wav; from sounds/README.md) ----
  const SWITCH_WAV = '%s';
%s  const bufs = {};
  const anyAudio = () => {                      // like audio(), but ignores the sound setting: the switch always clicks
    try {
      if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
      if (ctx.state === 'suspended') ctx.resume();
      return ctx;
    } catch (e) { return null; }
  };
  function play(key, b64, gain, always) {
    const c = always ? anyAudio() : audio(); if (!c) return;
    const go = buf => { const s = c.createBufferSource(), g = c.createGain(); s.buffer = buf; g.gain.value = gain; s.connect(g).connect(c.destination); s.start(); };
    if (bufs[key]) return go(bufs[key]);
    const bin = atob(b64), arr = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
    c.decodeAudioData(arr.buffer, buf => { bufs[key] = buf; go(buf); }, () => {});
  }
  const switchClick = () => play('switch', SWITCH_WAV, 0.9, true);
"""
INDEX_PLAYER = PLAYER % (E['switch'], "  const CORNER_WAV = '%s';\n" % E['corner']) + "  const cornerClick = () => play('corner', CORNER_WAV, 0.8, false);\n"
UNCLENCH_PLAYER = PLAYER % (E['switch'], "")

THUMP_RE = re.compile(r"  // a soft thump: a short low knock, pitch falling, no click\n  function thump\(\) \{.*?\n  \}\n", re.S)

def apply(path, player, reps):
    s = open(path, encoding='utf-8').read()
    assert THUMP_RE.search(s), path
    s = THUMP_RE.sub(lambda m: player, s, count=1)
    for a, b in reps:
        assert s.count(a) == 1, (path, a[:60])
        s = s.replace(a, b)
    open(path, 'w', encoding='utf-8', newline='\n').write(s)

apply('index.html', INDEX_PLAYER, [
    ("    if (sound) thump(); else toneOff();", "    switchClick(); if (!sound) toneOff();"),
    ("  let running = false, elapsed = 0, last = 0, raf = 0;\n", "  let running = false, elapsed = 0, last = 0, raf = 0, lastSide = -1;\n"),
    ("    const f = (inCycle - p * PHASE) / PHASE;        // 0..1 along that side\n",
     "    const f = (inCycle - p * PHASE) / PHASE;        // 0..1 along that side\n    if (running && p !== lastSide) { lastSide = p; cornerClick(); }   // the dot reaches a corner\n"),
    ("    elapsed = TOTAL;\n    dot.setAttribute('cx', 0);", "    elapsed = TOTAL; lastSide = -1;\n    dot.setAttribute('cx', 0);"),
    ("    if (elapsed >= TOTAL) elapsed = 0;\n    running = true;", "    if (elapsed >= TOTAL) { elapsed = 0; lastSide = -1; }\n    running = true;"),
    ("Space starts or pauses. The tone rises as you breathe in.", "Space starts or pauses. The tone rises as you breathe in; a click marks each corner."),
    ("  // ---- sound: made here, no files. Nothing plays before a tap. One setting for all instruments. ----",
     "  // ---- sound: a tone made here, two clicks recorded. Nothing plays before a tap. One setting for all instruments. ----"),
])
apply('unclench.html', UNCLENCH_PLAYER, [
    ("    if (sound) thump(); else toneOff();", "    switchClick(); if (!sound) toneOff();"),
])

for f in ['index.html', 'unclench.html']:
    s = open(f, encoding='utf-8').read()
    js = re.search(r'<script>(.*?)</script>', s, re.S).group(1)
    t = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); t.write(js); t.close()
    r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True)
    print(f, 'syntax ok' if r.returncode == 0 else r.stderr[:400], os.path.getsize(f), 'bytes'); os.unlink(t.name)
