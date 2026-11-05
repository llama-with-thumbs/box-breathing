import json, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, butter, sosfilt
sr, pair = wavfile.read('p-56.wav'); pair = pair.astype(float) / 32767
def save(name, y, peak=0.89):
    y = y / (np.abs(y).max() + 1e-9) * peak; wavfile.write(name + '.wav', sr, (y * 32767).astype(np.int16))
def lp(x, fc): return sosfilt(butter(4, fc, 'low', fs=sr, output='sos'), x)
def soft_start(x, onset, fc_lo, fc_hi, over):
    """no edge: for the first `over` seconds after the onset the cutoff sits at fc_lo and rises to fc_hi"""
    a, b = lp(x, fc_lo), lp(x, fc_hi)
    w = np.zeros(len(x)); s = int(onset * sr); n = int(over * sr)
    w[s:s + n] = np.linspace(0, 1, n) ** 2; w[s + n:] = 1; w[:s] = 0
    return a * (1 - w) + b * w
x4, x8 = resample_poly(pair, 4, 1), resample_poly(pair, 8, 1)
save('q-4a', soft_start(x4, 0.08, 220, 600, 0.10))     # 4x, under 600, the first 100 ms under 220: no edge
save('q-4b', soft_start(x4, 0.08, 180, 400, 0.15))     # 4x, under 400, first 150 ms under 180: softer still
save('q-8a', x8)                                        # 8x as it was
save('q-8b', soft_start(x8, 0.16, 180, 500, 0.2))      # 8x, under 500, first 200 ms under 180
json.dump({"title": "Clicks Five Six Slow", "h1": "5 + 6 · slow · no highs, no edge", "out": "voice030-56b.html", "vars": [
 ["q-4a", "4×, no highs, no edge", "Four times slow, nothing above 600 Hz, and the first 100 ms held under 220 Hz so the start has no bright edge.", "4a"],
 ["q-4b", "4×, softer still", "Nothing above 400 Hz, the first 150 ms under 180 Hz.", "4b"],
 ["q-8a", "8×", "Eight times slow, as before.", "8a"],
 ["q-8b", "8×, no highs, no edge", "Eight times, nothing above 500 Hz, the first 200 ms under 180 Hz.", "8b"]
]}, open('vars-q.json', 'w', encoding='utf-8'), indent=1)
