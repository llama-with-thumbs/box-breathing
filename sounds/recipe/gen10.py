"""Round 10: the slow click, no highs, in a small dead space. Claustrophobic: close, muffled, low, nowhere for the sound to go."""
import numpy as np, os, json
from scipy.signal import resample_poly
from gen import reverb, mix, save, lp, SR
from gen3 import c_clicks
D = os.path.dirname(os.path.abspath(__file__))
t, hits = c_clicks(); k1, k4, k5 = hits[0], hits[3], hits[4]
slow = lambda c, f: resample_poly(c, f, 1)
def at(x, sec, n):
    out = np.zeros(n); s = int(sec * SR); x = x[:max(0, n - s)]; out[s:s + len(x)] = x; return out
def box(x, rt=0.35, wet=0.5, dark=500):          # a small dead room: short, very dark, close
    return reverb(x, rt=rt, dark=dark, pre=0.004, wet=wet)
def sub(f=42, dur=0.4, tau=0.12, g=0.6):
    tt = np.arange(int(dur * SR)) / SR
    return np.sin(2 * np.pi * f * tt) * np.exp(-tt / tau) * g
def hum(n, f=50, g=0.05, cut=0.9):
    tt = np.arange(n) / SR
    h = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * 2 * f * tt)) * g
    c = int(cut * SR); h[c:] = 0; h[c - 400:c] *= np.linspace(1, 0, 400)
    return h
N = int(1.6 * SR)
s8 = at(slow(k5, 8), 0.02, N)

V = {}
V['a'] = save('r10-a', box(lp(s8, 800, 4)))
V['b'] = save('r10-b', box(lp(s8, 500, 4) + at(sub(), 0.02, N), wet=0.6))
V['c'] = save('r10-c', box(lp(s8 + at(slow(k5, 16) * 0.7, 0.02, N), 600, 4), rt=0.45))
V['d'] = save('r10-d', box(lp(s8 + at(slow(k4, 8) * 0.5, 0.16, N), 500, 4) + at(sub(g=0.4), 0.02, N)))
rat = sum(at(slow(k1, 8) * g, 0.02 + d, N) for d, g in [(0.13, 0.3), (0.23, 0.18), (0.31, 0.1)])
V['e'] = save('r10-e', mix(box(lp(s8 + rat, 400, 4), rt=0.3, wet=0.55), hum(N + int(0.4 * SR))))
V['f'] = save('r10-f', mix(box(lp(at(slow(k5, 12), 0.02, N) + at(sub(f=38, dur=0.6, tau=0.18), 0.02, N), 350, 4), rt=0.25, wet=0.6, dark=350), hum(N + int(0.3 * SR), g=0.04, cut=1.1)))
json.dump({"title": "Slow Click Closed", "h1": "8× slow click · no highs · a small dead room", "out": "click-clusters-10.html", "vars": [
 ["r10-a", "Muffled", "The slow click with nothing above 800 Hz, in a small dead room: short, dark, close."],
 ["r10-b", "Muffled, weight", "Nothing above 500 Hz, a 42 Hz thump underneath, the room a little wetter."],
 ["r10-c", "Doubled deeper", "The 8× click with a 16× copy under it, nothing above 600 Hz. One hit, two depths."],
 ["r10-d", "Two stages, closed", "The slow click and click 4 slowed, 140 ms apart, both under 500 Hz, with weight."],
 ["r10-e", "Settling, pressure", "After-rattle under 400 Hz in the deadest room, with a faint 50 Hz hum that cuts off at 0.9 s, like a pressure leaving."],
 ["r10-f", "Shut", "12× slow, nothing above 350 Hz, 38 Hz weight, a tiny room, the hum cutting off. The most closed of the six."]
]}, open('vars10.json', 'w', encoding='utf-8'), indent=1)
print(V)
