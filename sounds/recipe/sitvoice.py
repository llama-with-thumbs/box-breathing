"""sit.html: the fifteen lines recorded in two Kokoro voices (gallery 6 = Heart + Nicole blend, 2 = Heart; both two
semitones down, speed 0.85) and embedded as mp3. The switch cycles Voice 1, Voice 2, Voice off. The device voice goes."""
import re, os, sys, json, base64, subprocess, tempfile, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
from fractions import Fraction
from kokoro_onnx import Kokoro
HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(os.path.dirname(HERE), 'kokoro-model')
FF = r"C:\Users\laman\Downloads\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
REPO = r"C:\Users\laman\Documents\git\box-breathing"
def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:70], s.count(a)); return s.replace(a, b)

page = open(os.path.join(REPO, 'sit.html'), encoding='utf-8').read()
LINES = re.findall(r"\['(\w+)',\s+'([^']+)', (\d+)\]", page); assert len(LINES) == 15, len(LINES)

k = Kokoro(os.path.join(M, 'kokoro-v1.0.onnx'), os.path.join(M, 'voices-v1.0.bin'))
VOICES = {1: 0.6 * k.get_voice_style('af_heart') + 0.4 * k.get_voice_style('af_nicole'), 2: k.get_voice_style('af_heart')}
SPEED, SEMIS = 0.85, 2
f = 2 ** (SEMIS / 12); fr = Fraction(f).limit_denominator(60)
out = os.path.join(HERE, 'sitvoice'); os.makedirs(out, exist_ok=True)
b64 = {1: [], 2: []}; worst = 0
for v, st in VOICES.items():
    for i, (part, text, secs) in enumerate(LINES):
        x, sr = k.create(text, voice=st, speed=SPEED * f, lang='en-us')
        x = resample_poly(np.asarray(x, dtype=np.float64), fr.numerator, fr.denominator)
        x = x / np.abs(x).max() * 0.8
        n = int(0.03 * sr); x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
        x = np.concatenate([x, np.zeros(int(0.05 * sr))])
        name = os.path.join(out, 'v%d-%02d' % (v, i))
        wavfile.write(name + '.wav', sr, (x * 32767).astype(np.int16))
        subprocess.run([FF, '-y', '-loglevel', 'error', '-i', name + '.wav', '-ac', '1', '-ar', '24000', '-b:a', '40k', name + '.mp3'], check=True)
        b64[v].append(base64.b64encode(open(name + '.mp3', 'rb').read()).decode())
        d = len(x) / sr; worst = max(worst, d / int(secs))
        assert d < int(secs) - 2, (text, d, secs)          # the line ends at least two seconds before the next
print('recorded; fullest slot is %.0f %% spoken; audio %d KB' % (worst * 100, sum(len(b) for v in b64.values() for b in v) // 1024))
if '--dry' in sys.argv: sys.exit()

s = page
s = rep(s, '<span class="word"><span>Voice </span><span class="on">on</span><span class="off">off</span></span>',
           '<span class="word"><span>Voice </span><span class="on" id="vn">1</span><span class="off">off</span></span>')
s = rep(s, "  // ---- sound: the device's voice, and one recorded click for the switch. Nothing sounds before a tap. ----\n  let ctx = null, sound = true;\n",
           "  // ---- sound: a recorded voice (two to choose from), and one recorded click for the switch. Nothing sounds before a tap. ----\n  let ctx = null, sound = true, which = 1;\n  try { which = localStorage.getItem('sit.voice') === '2' ? 2 : 1; } catch (e) {}\n")
s = rep(s, "  const showSound = () => sndBtn.setAttribute('aria-pressed', String(sound));\n",
           "  const showSound = () => { sndBtn.setAttribute('aria-pressed', String(sound)); $('vn').textContent = which; };\n")
a = s.index("  // the voice:"); b = s.index("  // Keep the phone's screen on")
VOICE = """  // the voice: fifteen lines, recorded twice (Kokoro, Apache-2.0: 1 = Heart + Nicole blend, 2 = Heart; both lowered
  // two semitones and slowed), embedded as mp3 so the page stays one file. Recipe: sounds/recipe/sitvoice.py.
  const VOICE = { 1: %s,
    2: %s };
  const bufs = { 1: [], 2: [] };
  const bytesOf = b64 => { const bin = atob(b64), arr = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i); return arr.buffer; };
  try {                                         // decode at load, off the main context, so each line starts on time
    const off = new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(1, 8, 44100);
    for (const v of [1, 2]) VOICE[v].forEach((b64, i) => off.decodeAudioData(bytesOf(b64), buf => { bufs[v][i] = buf; }, () => {}));
  } catch (e) {}
  let src = null;
  function hush() { if (src) { try { src.stop(); } catch (e) {} src = null; } }
  function say(i) {
    hush();
    if (!sound) return;
    const c = anyAudio(); if (!c) return;
    const v = which;
    const go = buf => { if (!running || lastLine !== i || which !== v || !sound) return; hush(); const n = c.createBufferSource(); n.buffer = buf; n.connect(c.destination); n.start(); src = n; };
    if (bufs[v][i]) return go(bufs[v][i]);
    c.decodeAudioData(bytesOf(VOICE[v][i]), buf => { bufs[v][i] = buf; go(buf); }, () => {});
  }
  sndBtn.addEventListener('click', e => {         // one switch, three places: voice 1, voice 2, off
    e.stopPropagation();
    if (sound && which === 1) which = 2; else if (sound) sound = false; else { sound = true; which = 1; }
    showSound();
    try { localStorage.setItem('instruments.sound', sound ? 'on' : 'off'); localStorage.setItem('sit.voice', String(which)); } catch (e) {}
    switchClick();
    if (!sound) hush(); else if (running && lastLine >= 0) say(lastLine);
  });

""" % (json.dumps(b64[1]), json.dumps(b64[2]))
s = s[:a] + VOICE + s[b:]
s = rep(s, "      say(LINES[i][1]);\n", "      say(i);\n")
s = rep(s, "A voice reads each line; the words are on the square too. The aim is to stay, not to make it go.",
           "A voice reads each line; the switch changes it or turns it off. The aim is to stay, not to make it go.")
assert 'synth' not in s and 'speechSynthesis' not in s
js = re.search(r'<script>(.*?)</script>', s, re.S).group(1)
t = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); t.write(js); t.close()
r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True); os.unlink(t.name)
assert r.returncode == 0, r.stderr[:400]
open(os.path.join(REPO, 'sit.html'), 'w', encoding='utf-8', newline='\n').write(s)
print('sit.html written, syntax ok,', len(s) // 1024, 'KB')
