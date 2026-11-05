"""index.html: four corner clicks (one per side) and the tone ducks under every click so nothing clips."""
import json, os, re, subprocess, tempfile
E = json.load(open('embed4.json'))
os.chdir(r"C:\Users\laman\Documents\git\box-breathing")
p = 'index.html'; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:70]; s = s.replace(a, b)
# 1. one CORNER_WAV -> four
m = re.search(r"  const CORNER_WAV = '[^']*';\n", s); assert m
s = s.replace(m.group(0), "  const CORNER_WAVS = [%s];   // one per side: inhale, top, exhale, bottom (8.0x, 7.3x, 8.6x, 9.3x slow)\n" % ', '.join("'%s'" % E['corner%d' % i] for i in range(1, 5)))
rep("  const bufs = {};\n", "  const bufs = {};\n  const WAVS = { switch: SWITCH_WAV }; CORNER_WAVS.forEach((w, i) => { WAVS['corner' + i] = w; });\n")
# 2. play() ducks the tone while a click sounds
rep("    const go = buf => { const s = c.createBufferSource(), g = c.createGain(); s.buffer = buf; g.gain.value = gain; s.connect(g).connect(c.destination); s.start(); };",
    "    const go = buf => { const s = c.createBufferSource(), g = c.createGain(); s.buffer = buf; g.gain.value = gain; s.connect(g).connect(c.destination); duck(buf.duration); s.start(); };")
rep("    for (const [key, b64] of Object.entries(typeof CORNER_WAV === 'string' ? { switch: SWITCH_WAV, corner: CORNER_WAV } : { switch: SWITCH_WAV })) {",
    "    for (const [key, b64] of Object.entries(WAVS)) {")
rep("  const cornerClick = () => play('corner', CORNER_WAV, 0.8, false);",
    "  const cornerClick = side => play('corner' + side, CORNER_WAVS[side], 0.8, false);")
# 3. the tone: a duck gain after the tone gain
rep("  let osc1 = null, osc2 = null, gain = null;\n", "  let osc1 = null, osc2 = null, gain = null, dip = null;\n")
rep("    osc1.connect(gain); osc2.connect(g2).connect(gain); gain.connect(c.destination);",
    "    dip = c.createGain();                       // the tone steps aside while a click sounds; together they would clip\n    osc1.connect(gain); osc2.connect(g2).connect(gain); gain.connect(dip).connect(c.destination);")
rep("  function toneOff() {\n    if (!osc1) return;\n    const o1 = osc1, o2 = osc2, g = gain, t = ctx.currentTime; osc1 = osc2 = gain = null;",
    "  function duck(sec) {                          // tone to 30 % in 10 ms, back over 150 ms after the click\n    if (!dip) return;\n    const t = ctx.currentTime;\n    dip.gain.cancelScheduledValues(t); dip.gain.setTargetAtTime(0.3, t, 0.01); dip.gain.setTargetAtTime(1, t + sec, 0.05);\n  }\n  function toneOff() {\n    if (!osc1) return;\n    const o1 = osc1, o2 = osc2, g = gain, t = ctx.currentTime; osc1 = osc2 = gain = dip = null;")
rep("    if (running && p !== lastSide) { lastSide = p; cornerClick(); }   // the dot reaches a corner",
    "    if (running && p !== lastSide) { lastSide = p; cornerClick(p); }  // the dot reaches a corner; each corner has its own click")
rep("  // ---- two recorded clicks, embedded so the page stays one file (8 kHz wav; from sounds/README.md) ----",
    "  // ---- recorded clicks, embedded so the page stays one file (8 kHz wav; from sounds/README.md) ----")
open(p, 'w', encoding='utf-8', newline='\n').write(s)
js = re.search(r'<script>(.*?)</script>', s, re.S).group(1)
t = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); t.write(js); t.close()
r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True)
print('syntax ok' if r.returncode == 0 else r.stderr[:400], os.path.getsize(p), 'bytes'); os.unlink(t.name)
