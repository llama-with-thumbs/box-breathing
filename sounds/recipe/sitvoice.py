"""sit.html: the fifteen lines recorded in two Kokoro voices (1 = Heart + Nicole blend, 2 = Heart; both two semitones
down) and embedded as mp3. Each line is spoken phrase by phrase, and the silence between phrases is written here by
hand (RHYTHM): a list wants room between its words, a thought that runs on wants almost none.
Needs: pip install kokoro-onnx, and kokoro-v1.0.onnx + voices-v1.0.bin in ../kokoro-model."""
import re, os, sys, json, base64, subprocess, tempfile, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
from fractions import Fraction
from kokoro_onnx import Kokoro
HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(os.path.dirname(HERE), 'kokoro-model')
FF = r"C:\Users\laman\Downloads\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
REPO = r"C:\Users\laman\Documents\git\box-breathing"
SPEED, SEMIS = 0.75, 2

# phrase, seconds of silence after it, phrase, ... One entry per line of the page, in order.
RHYTHM = [
 ["Find where it sits in your body."],
 ["Chest.", 0.9, "Stomach.", 0.9, "Throat.", 0.9, "Hands."],                      # time to look in each place
 ["Name what is there, in plain words.", 1.1, "Tight.", 0.7, "Hot.", 0.7, "Fluttering."],
 ["Watch it.", 1.2, "Nothing to fix."],
 ["This is a sensation."],
 ["It is uncomfortable.", 0.8, "It is not an emergency."],
 ["If the mind runs ahead, come back to what is here."],                          # one thought, no stop
 ["Now the thoughts.", 0.7, "Watch them like a show."],
 ["Is it predicting?", 0.9, "Wanting to be sure?", 0.9, "Solving?", 0.9, "Asking for reassurance?"],
 ["Name the kind.", 1.2, "Stay in your seat."],
 ["Say to yourself what you would say to a friend."],
 ["This is hard.", 1.3, "I can be here with it."],
 ["It can stay as long as it stays."],
 ["Feel your feet.", 1.0, "Your weight in the seat."],
 ["Look at one thing in the room."],
]

page = open(os.path.join(REPO, 'sit.html'), encoding='utf-8').read()
LINES = re.findall(r"\['(\w+)',\s+'([^']+)', (\d+)\]", page); assert len(LINES) == 15, len(LINES)
for (part, text, secs), r in zip(LINES, RHYTHM):
    assert ' '.join(x for x in r if isinstance(x, str)) == text, text       # the rhythm table and the page say the same words

k = Kokoro(os.path.join(M, 'kokoro-v1.0.onnx'), os.path.join(M, 'voices-v1.0.bin'))
VOICES = {1: 0.6 * k.get_voice_style('af_heart') + 0.4 * k.get_voice_style('af_nicole'), 2: k.get_voice_style('af_heart')}
f = 2 ** (SEMIS / 12); fr = Fraction(f).limit_denominator(60)
def phrase(text, st):
    x, sr = k.create(text, voice=st, speed=SPEED * f, lang='en-us')
    x = resample_poly(np.asarray(x, dtype=np.float64), fr.numerator, fr.denominator)
    loud = np.where(np.abs(x) > 0.02 * np.abs(x).max())[0]; m = int(0.03 * sr)   # trim the engine's own silence
    x = x[max(0, loud[0] - m):loud[-1] + m]
    n = int(0.02 * sr); x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
    return x, sr
out = os.path.join(HERE, 'sitvoice'); os.makedirs(out, exist_ok=True)
b64 = {1: [], 2: []}; report = []
for v, st in VOICES.items():
    for i, ((part, text, secs), r) in enumerate(zip(LINES, RHYTHM)):
        parts = []; spoken = 0
        for item in r:
            if isinstance(item, str):
                x, sr = phrase(item, st); assert len(x) / sr > 0.25, (item, len(x) / sr); parts.append(x); spoken += len(x) / sr
            else: parts.append(np.zeros(int(item * sr)))
        x = np.concatenate(parts + [np.zeros(int(0.05 * sr))]); x = x / np.abs(x).max() * 0.8
        name = os.path.join(out, 'v%d-%02d' % (v, i))
        wavfile.write(name + '.wav', sr, (x * 32767).astype(np.int16))
        subprocess.run([FF, '-y', '-loglevel', 'error', '-i', name + '.wav', '-ac', '1', '-ar', '24000', '-b:a', '40k', name + '.mp3'], check=True)
        b64[v].append(base64.b64encode(open(name + '.mp3', 'rb').read()).decode())
        d = len(x) / sr; report.append((v, i, d, int(secs), spoken))
for v, i, d, secs, spoken in report:
    print('v%d %2d  %4.1f s of %2d  (speech %.1f)  %s' % (v, i, d, secs, spoken, '' if d <= secs - 3 else '<-- under 3 s of rest'))
if '--dry' in sys.argv: sys.exit()
assert all(d <= secs - 3 for v, i, d, secs, sp in report), 'a line leaves under 3 s before the next'

new = "const VOICE = { 1: %s,\n    2: %s };" % (json.dumps(b64[1]), json.dumps(b64[2]))
s, n = re.subn(r"const VOICE = \{ 1: \[.*?\],\n    2: \[.*?\] \};", lambda m: new, page, flags=re.S); assert n == 1
js = re.search(r'<script>(.*?)</script>', s, re.S).group(1)
t = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); t.write(js); t.close()
r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True); os.unlink(t.name)
assert r.returncode == 0, r.stderr[:400]
open(os.path.join(REPO, 'sit.html'), 'w', encoding='utf-8', newline='\n').write(s)
print('sit.html written, syntax ok,', len(s) // 1024, 'KB')
