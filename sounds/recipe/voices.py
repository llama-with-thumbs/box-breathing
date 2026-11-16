"""Voice candidates for sit.html: Kokoro (Apache-2.0) American women, slowed, some lowered, reading the same three lines.
Lowering: speak faster by k, then stretch by k at the same sample rate; duration comes back, pitch drops by k."""
import json, os, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
from fractions import Fraction
from kokoro_onnx import Kokoro
M = r"C:\Users\laman\AppData\Local\Temp\claude\1c7efbda850f1907\8dfa7eca-8b6d-42dc-b786-656d7fd446e6\scratchpad\kokoro-model"
FF = r"C:\Users\laman\Downloads\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
k = Kokoro(os.path.join(M, 'kokoro-v1.0.onnx'), os.path.join(M, 'voices-v1.0.bin'))
TEXT = ["Find where it sits in your body.", "This is a sensation. It is uncomfortable. It is not an emergency.", "Say to yourself what you would say to a friend."]
def style(spec):
    if isinstance(spec, str): return k.get_voice_style(spec)
    return sum(k.get_voice_style(n) * w for n, w in spec)
def speak(text, spec, speed, semis):
    f = 2 ** (semis / 12)
    x, sr = k.create(text, voice=style(spec), speed=speed * f, lang='en-us')
    if semis:
        fr = Fraction(f).limit_denominator(60); x = resample_poly(x, fr.numerator, fr.denominator)
    return np.asarray(x, dtype=np.float64), sr
CAND = [
 ('vc-1', 'Heart', 'af_heart', 0.85, 0, 'Kokoro\u2019s best-rated voice, slowed. Warm, as recorded.'),
 ('vc-2', 'Heart, lower', 'af_heart', 0.85, 2, 'The same voice two semitones down. Reads ten or fifteen years older.'),
 ('vc-3', 'Sarah, lower', 'af_sarah', 0.85, 2, 'Plainer, steadier; two semitones down.'),
 ('vc-4', 'Nicole', 'af_nicole', 0.9, 0, 'Close and quiet, almost a whisper.'),
 ('vc-5', 'Nicole, lower', 'af_nicole', 0.9, 1.5, 'The quiet voice, a semitone and a half down.'),
 ('vc-6', 'Heart + Nicole, lower', [('af_heart', 0.6), ('af_nicole', 0.4)], 0.85, 2, 'A blend: Heart\u2019s warmth with some of Nicole\u2019s hush, two semitones down.'),
 ('vc-7', 'Kore, lower', 'af_kore', 0.85, 2.5, 'A firmer voice, two and a half semitones down. The oldest-sounding of the set.'),
 ('vc-8', 'Bella, lower and slower', 'af_bella', 0.8, 2, 'Fuller voice, slowest pace, two semitones down.'),
]
rows = []
for key, name, spec, speed, semis, note in CAND:
    parts = []
    for line in TEXT:
        x, sr = speak(line, spec, speed, semis); parts += [x, np.zeros(int(sr * 1.2))]
    y = np.concatenate(parts[:-1]); y = y / np.abs(y).max() * 0.85
    wavfile.write(key + '.wav', sr, (y * 32767).astype(np.int16))
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', key + '.wav', '-ac', '1', '-b:a', '64k', key + '.mp3'], check=True)
    print(key, name, '%.1f s' % (len(y) / sr)); rows.append([key, name, note, key[-1]])
json.dump({"title": "Sit Voices", "h1": "eight voices for sit \u00b7 the same three lines",
           "lead": "Kokoro voices, American women, slowed; most are lowered to read older. Three lines from the page with the page\u2019s kind of pause between them. Pick by ear, on the phone.",
           "out": "voices.html", "vars": rows}, open('vars-vc.json', 'w', encoding='utf-8'), indent=1)
