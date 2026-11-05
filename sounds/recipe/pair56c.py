"""Four siblings of 8b (the corner click), one per corner. Set A: speed (pitch) differs. Set B: brightness differs."""
import json, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, butter, sosfilt
sr, pair = wavfile.read('p-56.wav'); pair = pair.astype(float) / 32767
def save(name, y, peak=0.89):
    y = y / (np.abs(y).max() + 1e-9) * peak; wavfile.write(name + '.wav', sr, (y * 32767).astype(np.int16))
def lp(x, fc): return sosfilt(butter(4, fc, 'low', fs=sr, output='sos'), x)
def soft_start(x, onset, fc_lo, fc_hi, over):
    a, b = lp(x, fc_lo), lp(x, fc_hi)
    w = np.zeros(len(x)); s = int(onset * sr); n = int(over * sr)
    w[s:s + n] = np.linspace(0, 1, n) ** 2; w[s + n:] = 1; w[:s] = 0
    return a * (1 - w) + b * w
def slow(x, f):                                   # fractional slow-down: f = up/down
    up, down = int(round(f * 10)), 10
    return resample_poly(x, up, down)
# A: speed. The onset and the 200 ms soft start scale with the speed so the shape stays the same.
A = {'a1': 8.0, 'a2': 7.3, 'a3': 8.6, 'a4': 9.3}
for k, f in A.items():
    save('c-' + k, soft_start(slow(pair, f), 0.02 * f, 180, 500, 0.025 * f))
# B: same 8x speed, the top edge moves: 420, 500 (= 8b), 580, 680 Hz
B = {'b1': 500, 'b2': 420, 'b3': 580, 'b4': 680}
x8 = slow(pair, 8.0)
for k, fc in B.items():
    save('c-' + k, soft_start(x8, 0.16, 180, fc, 0.2))
json.dump({"title": "Corner Siblings", "h1": "corner click · four siblings", "out": "corner-siblings.html", "vars": [
 ["c-a1", "A1 · 8.0× (= 8b)", "The corner click as it is now. Inhale starts.", "A1"],
 ["c-a2", "A2 · 7.3×, a little higher", "Top of the inhale.", "A2"],
 ["c-a3", "A3 · 8.6×, a little lower", "Exhale starts.", "A3"],
 ["c-a4", "A4 · 9.3×, lower still", "Bottom of the exhale.", "A4"],
 ["c-b1", "B1 · to 500 Hz (= 8b)", "Same speed for all four of B; only the top edge moves. Inhale starts.", "B1"],
 ["c-b2", "B2 · to 420 Hz, duller", "Top of the inhale.", "B2"],
 ["c-b3", "B3 · to 580 Hz, a touch brighter", "Exhale starts.", "B3"],
 ["c-b4", "B4 · to 680 Hz, brightest", "Bottom of the exhale.", "B4"]
]}, open('vars-c.json', 'w', encoding='utf-8'), indent=1)
