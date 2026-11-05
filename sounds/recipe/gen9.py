"""Round 9: the 8x slow click, no siren, made more complex: layers, after-rattle, weight, air, room."""
import numpy as np, os, json
from scipy.signal import resample_poly
from gen import reverb, mix, save, lp, bp, click, cluster, SR
from gen3 import c_clicks
D = os.path.dirname(os.path.abspath(__file__))

t, hits = c_clicks()
k1, k4, k5 = hits[0], hits[3], hits[4]
slow = lambda c, f: resample_poly(c, f, 1)
def at(x, sec, n):
    out = np.zeros(n); s = int(sec * SR); x = x[:max(0, n - s)]; out[s:s + len(x)] = x; return out
def room(x, rt=1.2, wet=0.3, dark=1500):
    return reverb(x, rt=rt, dark=dark, wet=wet)
N = int(1.6 * SR)
base = at(slow(k5, 8), 0.02, N)

V = {}
# a · a real edge on the slow body: the original (fast) click sits on top of the slow one at the start
V['a'] = save('r9-a', room(base + at(k5 * 0.5, 0.02, N)))
# b · two-stage: the slow click, then click 4 slowed 8x, quieter, 140 ms later: the mechanism has two parts
V['b'] = save('r9-b', room(base + at(slow(k4, 8) * 0.45, 0.16, N)))
# c · after-rattle: three tiny slowed fragments of click 1 after the main one, each softer, like parts settling
rat = sum(at(slow(k1, 6) * g, 0.02 + d, N) for d, g in [(0.11, 0.28), (0.19, 0.17), (0.25, 0.09)])
V['c'] = save('r9-c', room(base + rat))
# d · weight: a 42 Hz sine thump, 0.35 s, under the start
tt = np.arange(int(0.4 * SR)) / SR
sub = np.sin(2 * np.pi * 42 * tt) * np.exp(-tt / 0.12) * 0.6
V['d'] = save('r9-d', room(base + at(sub, 0.02, N)))
# e · air: a quiet band of noise rising behind the click, 300 -> 1500 Hz over 0.8 s, then gone
rng = np.random.default_rng(9); n = int(0.9 * SR); tt = np.arange(n) / SR
air = rng.standard_normal(n); f = 300 * (1500 / 300) ** (tt / 0.9)
air = bp(air, 250, 1800, 2) * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.sin(np.pi * tt / 0.9) ** 1.5 * 0.08
V['e'] = save('r9-e', room(base + at(air, 0.1, N), rt=1.8, wet=0.4))
# f · all of it, held back: edge, second stage, after-rattle, weight, each quieter than above, in a slightly bigger room
V['f'] = save('r9-f', room(base + at(k5 * 0.35, 0.02, N) + at(slow(k4, 8) * 0.3, 0.16, N) + rat * 0.6 + at(sub * 0.6, 0.02, N), rt=1.6, wet=0.35))
json.dump({"title": "Slow Click Nuanced", "h1": "8× slow click · six nuances", "out": "click-clusters-9.html", "vars": [
 ["r9-a", "Edge on top", "The original fast click rides on the front of the slow one: a crisp edge, then the slow body."],
 ["r9-b", "Two stages", "The slow click, then click 4 slowed the same way, quieter, 140 ms later. A mechanism with two parts."],
 ["r9-c", "After-rattle", "Three tiny slowed fragments after the main hit, each softer, 80 ms apart: parts settling."],
 ["r9-d", "Weight", "A 42 Hz thump under the start, a third of a second. Felt more than heard on headphones; lost on a phone speaker."],
 ["r9-e", "Air", "A faint band of noise rises behind the click and is gone within a second."],
 ["r9-f", "All of it, held back", "Edge, two stages, after-rattle and weight together, each quieter, in a slightly bigger room."]
]}, open('vars9.json', 'w', encoding='utf-8'), indent=1)
print(V)
