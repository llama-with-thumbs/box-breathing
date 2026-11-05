"""Trim, resample to 8 kHz and base64 the four corner siblings (set A) -> embed4.json + corner1..4.wav"""
import numpy as np, base64, json
from scipy.io import wavfile
from scipy.signal import resample_poly
out = {}
for i, src in enumerate(['c-a1.wav', 'c-a2.wav', 'c-a3.wav', 'c-a4.wav'], 1):
    sr, x = wavfile.read(src); x = x.astype(float) / 32767
    a = np.abs(x); pk = a.max()
    s = max(0, np.argmax(a > 0.01 * pk) - int(0.005 * sr))
    F = int(0.02 * sr); env = np.array([a[j:j+F].max() for j in range(0, len(a), F)])
    last = np.max(np.nonzero(env > 0.005 * pk)[0]); e = min(len(x), (last + 2) * F)
    y = x[s:e]; y[-int(0.01*sr):] *= np.linspace(1, 0, int(0.01*sr))
    y8 = resample_poly(y, 8000, 44100); y8 = y8 / (np.abs(y8).max() + 1e-9) * 0.89
    name = f'corner{i}'
    wavfile.write(name + '.wav', 8000, (y8 * 32767).astype(np.int16))
    out[name] = base64.b64encode(open(name + '.wav', 'rb').read()).decode()
    print(name, round(len(y8) / 8000, 3), 's', len(out[name]) // 1024, 'KB b64')
json.dump(out, open('embed4.json', 'w'))
