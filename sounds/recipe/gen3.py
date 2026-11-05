"""Round 3: c (sparse, heavy) with the servo fading sooner, plus each of its clicks on its own."""
import numpy as np, os, json
from gen import cluster, servo, reverb, mix, save, click, SR

D = os.path.dirname(os.path.abspath(__file__))

def c_clicks(seed=13):
    """The five hits of c, as separate buffers with their onset times. Same seed, so the same clicks as before."""
    rng = np.random.default_rng(seed)
    t = cluster(rng, 5, 1.0, accel=1.4)
    hits = []
    for ti in t:
        layers = rng.random()
        c = click(rng, snap=layers > 0.15, body=layers < 0.9, thump_db=-4,
                  pitch=-7 + rng.uniform(-3, 3), size=2.0)
        c *= 10 ** (rng.uniform(-4, 4) / 20)
        hits.append(c)
    return t, hits

def assemble(t, hits, sdur, fall, gain=0.09, name=''):
    n = int((t.max() + 0.25) * SR); out = np.zeros(n + int(0.15 * SR))
    for ti, c in zip(t, hits):
        s = int(ti * SR); out[s:s + len(c)] += c
    cl = out[:n]
    sv = servo(160, 900, sdur, 'saw', lp_hz=1600, hum_db=-34, rise=0.12, fall=fall)
    tail = np.concatenate([np.zeros(int((t.max() + 0.06) * SR)), sv]) * gain
    return save(name, mix(cl, reverb(tail, rt=1.6, dark=1600)))

t, hits = c_clicks()
V = {}
V['c1'] = assemble(t, hits, 1.0, 0.6, name='r3-c1')     # servo 1.8 s -> 1.0 s, most of it the fade
V['c2'] = assemble(t, hits, 0.6, 0.45, name='r3-c2')    # servo 0.6 s: a flick, gone almost at once
# the single clicks keep their level relative to each other: the loudest one peaks at 0.89
from scipy.io import wavfile
g = 0.89 / max(np.abs(c).max() for c in hits)
for i, c in enumerate(hits, 1):
    pad = np.concatenate([np.zeros(int(0.02 * SR)), c * g, np.zeros(int(0.15 * SR))])
    wavfile.write(os.path.join(D, f'r3-k{i}.wav'), SR, (pad * 32767).astype(np.int16))
    V[f'k{i}'] = len(pad) / SR
json.dump(V, open(os.path.join(D, 'durations3.json'), 'w'))
print(V, [round(float(x), 3) for x in t])
