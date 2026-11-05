"""Round 11: round 10 remade for small speakers (laptop, Galaxy S22). Nothing relies on anything under ~180 Hz.
The weight is a stack of harmonics of a low note (the ear hears the missing fundamental); the body sits 200-900 Hz."""
import numpy as np, os, json
from scipy.signal import resample_poly
from gen import reverb, mix, save, lp, hp, SR
from gen3 import c_clicks
D = os.path.dirname(os.path.abspath(__file__))
t, hits = c_clicks(); k1, k4, k5 = hits[0], hits[3], hits[4]
slow = lambda c, f: resample_poly(c, f, 1)
def at(x, sec, n):
    out = np.zeros(n); s = int(sec * SR); x = x[:max(0, n - s)]; out[s:s + len(x)] = x; return out
def band(x, lo=180, hi=900):                      # the speaker's window: cut what it cannot play, cut the highs you did not want
    return lp(hp(x, lo, 2), hi, 4)
def box(x, rt=0.35, wet=0.5, dark=700):
    return reverb(x, rt=rt, dark=dark, pre=0.004, wet=wet)
def weight(f0=55, dur=0.4, tau=0.12, g=0.5):      # harmonics 3..7 of f0 (165-385 Hz): the ear hears 55 Hz, the speaker plays it
    tt = np.arange(int(dur * SR)) / SR
    x = sum(np.sin(2 * np.pi * f0 * k * tt) / k for k in range(3, 8))
    return x / np.abs(x).max() * g * np.exp(-tt / tau)
def hum(n, f=100, g=0.05, cut=0.9):
    tt = np.arange(n) / SR
    h = (np.sin(2 * np.pi * f * tt) + 0.6 * np.sin(2 * np.pi * 2 * f * tt) + 0.3 * np.sin(2 * np.pi * 3 * f * tt)) * g
    c = int(cut * SR); h[c:] = 0; h[c - 400:c] *= np.linspace(1, 0, 400)
    return h
N = int(1.6 * SR)
s8 = at(slow(k5, 8), 0.02, N)
rat = sum(at(slow(k1, 8) * g, 0.02 + d, N) for d, g in [(0.13, 0.3), (0.23, 0.18), (0.31, 0.1)])

V = {}
V['a'] = save('r11-a', box(band(s8, 180, 1000)))
V['b'] = save('r11-b', box(band(s8, 180, 700) + at(weight(), 0.02, N), wet=0.6))
V['c'] = save('r11-c', box(band(s8 + at(slow(k5, 16) * 0.7, 0.02, N), 180, 800), rt=0.45))
V['d'] = save('r11-d', box(band(s8 + at(slow(k4, 8) * 0.5, 0.16, N), 180, 700) + at(weight(g=0.35), 0.02, N)))
V['e'] = save('r11-e', mix(box(band(s8 + rat, 180, 600), rt=0.3, wet=0.55), hum(N + int(0.4 * SR))))
V['f'] = save('r11-f', mix(box(band(at(slow(k5, 12), 0.02, N), 180, 500) + at(weight(f0=50, dur=0.6, tau=0.18), 0.02, N), rt=0.25, wet=0.6, dark=500), hum(N + int(0.3 * SR), g=0.04, cut=1.1)))
json.dump({"title": "Slow Click Closed II", "h1": "8× slow click · closed in · tuned for laptop and S22", "out": "click-clusters-11.html", "vars": [
 ["r11-a", "Muffled", "The slow click kept between 180 Hz and 1 kHz, small dead room. Nothing the speaker cannot play."],
 ["r11-b", "Muffled, weight", "Under 700 Hz, with weight made of harmonics of 55 Hz (165-385 Hz): the ear hears a low note the speaker never plays."],
 ["r11-c", "Doubled deeper", "The 8× click with a 16× copy under it, under 800 Hz."],
 ["r11-d", "Two stages, closed", "Second slowed click 140 ms later, under 700 Hz, lighter weight."],
 ["r11-e", "Settling, pressure", "After-rattle under 600 Hz, and a 100 Hz hum with its harmonics that cuts off at 0.9 s."],
 ["r11-f", "Shut", "12× slow, under 500 Hz, weight from 50 Hz harmonics, tiniest room, hum cutting off. The most closed."]
]}, open('vars11.json', 'w', encoding='utf-8'), indent=1)
print(V)
