"""Round 2: variations of #1 — slower, deeper, fewer clicks; quieter servo."""
import numpy as np, os, json
from gen import cluster, render_clicks, servo, reverb, mix, save, click, SR

def one(seed, hits, span, accel, pitch, size, thump_db, servo_gain, f0=200, f1=1200, sdur=1.6, lp_hz=2200, rt=2.2, name=''):
    rng = np.random.default_rng(seed)
    t = cluster(rng, hits, span, accel=accel)
    # deeper: every hit sits `pitch` semitones down, bigger body, more thump
    end = t.max() + 0.25
    n = int(end * SR); out = np.zeros(n + int(0.15 * SR))
    for ti in t:
        layers = rng.random()
        c = click(rng, snap=layers > 0.15, body=layers < 0.9, thump_db=thump_db,
                  pitch=pitch + rng.uniform(-3, 3), size=size)
        c *= 10 ** (rng.uniform(-4, 4) / 20)
        s = int(ti * SR); out[s:s + len(c)] += c
    cl = out[:n]
    sv = servo(f0, f1, sdur, 'saw', lp_hz=lp_hz, hum_db=-34)
    tail = np.concatenate([np.zeros(int((t.max() + 0.06) * SR)), sv]) * servo_gain
    return save(name, mix(cl, reverb(tail, rt=rt, dark=1600)))

V = {}
# a · one notch each: 10 hits over 0.8 s, 3 semitones down, servo at half
V['a'] = one(11, 10, 0.8, 1.8, -3, 1.3, -9, 0.17, name='r2-a')
# b · fewer and slower: 7 hits over 0.9 s, 5 down, bigger body, servo at a third
V['b'] = one(12, 7, 0.9, 1.6, -5, 1.6, -7, 0.12, name='r2-b')
# c · sparse and heavy: 5 hits over 1.0 s, 7 down, thump up front, servo faint and low
V['c'] = one(13, 5, 1.0, 1.4, -7, 2.0, -4, 0.09, f0=160, f1=900, sdur=1.8, lp_hz=1600, name='r2-c')
# d · slow and even: 8 hits over 1.1 s, almost no acceleration, 5 down, servo quiet and short
V['d'] = one(14, 8, 1.1, 1.15, -5, 1.5, -8, 0.12, sdur=1.1, name='r2-d')
# e · like b but the servo barely there, mostly its room
V['e'] = one(15, 7, 0.9, 1.6, -5, 1.6, -7, 0.06, rt=3.0, name='r2-e')
json.dump(V, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'durations2.json'), 'w'))
print(V)
