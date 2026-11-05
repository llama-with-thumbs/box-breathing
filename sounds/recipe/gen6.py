"""Round 6: click 5 alone, made longer, ending in a quiet siren."""
import numpy as np, os, json
from gen import click, servo, reverb, mix, save, SR

D = os.path.dirname(os.path.abspath(__file__))

def click5(size):
    """Click 5 of c: same random draws as in the cluster, so the same snap, body and pitch; only the decay (size) changes."""
    rng = np.random.default_rng(13)
    from gen import cluster
    cluster(rng, 5, 1.0, accel=1.4)                    # advance the generator exactly as c did
    for i in range(5):
        layers = rng.random()
        c = click(rng, snap=layers > 0.15, body=layers < 0.9, thump_db=-4,
                  pitch=-7 + rng.uniform(-3, 3), size=size)
        c *= 10 ** (rng.uniform(-4, 4) / 20)
    return c                                            # the fifth

def one(size, gap, sgain, sdur, fall, name, f0=160, f1=900, rt=1.6):
    c = click5(size)
    sv = servo(f0, f1, sdur, 'saw', lp_hz=1600, hum_db=-36, rise=0.15, fall=fall)
    tail = np.concatenate([np.zeros(int(gap * SR)), sv]) * sgain
    head = np.concatenate([np.zeros(int(0.02 * SR)), c])
    return save(name, mix(head, reverb(tail, rt=rt, dark=1500)))

V = {}
V['a'] = one(2.0, 0.08, 0.07, 0.9, 0.5, 'r6-a')     # click as it was, siren quiet (about half of c's), 0.9 s
V['b'] = one(3.5, 0.10, 0.06, 0.9, 0.5, 'r6-b')     # click decays twice as long, same siren
V['c'] = one(5.0, 0.12, 0.05, 1.3, 0.8, 'r6-c')     # click decays three times as long, siren fainter and slower
V['d'] = one(3.5, 0.04, 0.04, 0.7, 0.45, 'r6-d')    # long click, siren comes in almost at once and is barely there
json.dump({"title": "Click Five", "h1": "click 5 · longer · ending in a quiet siren", "out": "click-clusters-6.html", "vars": [
 ["r6-a", "As it was + siren", "Click 5 unchanged, then a siren at half the level it had in c, 0.9 s."],
 ["r6-b", "Twice as long", "The click settles twice as long. Same quiet siren."],
 ["r6-c", "Three times as long", "The click settles three times as long. Siren fainter, slower, 1.3 s."],
 ["r6-d", "Long, siren at once", "Twice-as-long click; the siren starts under its tail and is barely there, 0.7 s."]
]}, open('vars6.json', 'w', encoding='utf-8'), indent=1)
print(V)
