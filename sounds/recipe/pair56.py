import json, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, butter, sosfilt
sr, k5 = wavfile.read('x-k5.wav'); _, k6 = wavfile.read('x-k6.wav')
k5 = k5.astype(float) / 32767; k6 = k6.astype(float) / 32767
k5 = k5[int(0.02 * sr):]; k6 = k6[int(0.02 * sr):]          # drop the lead-in silence
def at(x, sec, n):
    out = np.zeros(n); s = int(sec * sr); x = x[:max(0, n - s)]; out[s:s + len(x)] = x; return out
def save(name, y, peak=0.89):
    y = y / (np.abs(y).max() + 1e-9) * peak; wavfile.write(name + '.wav', sr, (y * 32767).astype(np.int16))
def slow(x, f): return resample_poly(x, f, 1)
def lp(x, fc): return sosfilt(butter(4, fc, 'low', fs=sr, output='sos'), x)
N = int(0.6 * sr)
pair = at(k5, 0.02, N) + at(k6, 0.06, N)                      # 40 ms apart, as recorded
save('p-5', at(k5, 0.02, N)); save('p-6', at(k6, 0.02, N)); save('p-56', pair)
save('p-56x2', slow(pair, 2)); save('p-56x4', slow(pair, 4)); save('p-56x8', slow(pair, 8))
save('p-56x4lp', lp(slow(pair, 4), 600))
json.dump({"title": "Clicks Five Six", "h1": "voice 030 · clicks 5 and 6", "out": "voice030-56.html", "vars": [
 ["p-5", "Click 5", "At 0.95 s in the take. Alone.", "5"],
 ["p-6", "Click 6", "At 0.99 s, the loudest in the take. Alone.", "6"],
 ["p-56", "5 + 6 as recorded", "40 ms apart, as they sat.", "56"],
 ["p-56x2", "5 + 6, 2× slow", "The pair stretched twice, an octave down.", "2×"],
 ["p-56x4", "5 + 6, 4× slow", "Four times, two octaves down.", "4×"],
 ["p-56x8", "5 + 6, 8× slow", "Eight times, three octaves down.", "8×"],
 ["p-56x4lp", "5 + 6, 4× slow, no highs", "Four times, nothing above 600 Hz.", "4× lp"]
]}, open('vars-p.json', 'w', encoding='utf-8'), indent=1)
