"""Round 7: from r6-c (three times as long). Variants with the click ten times as long as the original."""
import numpy as np, os, json
from gen import click, cluster, servo, reverb, mix, save, SR
D = os.path.dirname(os.path.abspath(__file__))

def click5(size, thump_db=-4):
    rng = np.random.default_rng(13)
    cluster(rng, 5, 1.0, accel=1.4)
    for i in range(5):
        layers = rng.random()
        c = click(rng, snap=layers > 0.15, body=layers < 0.9, thump_db=thump_db,
                  pitch=-7 + rng.uniform(-3, 3), size=size)
        c *= 10 ** (rng.uniform(-4, 4) / 20)
    return c

def one(size, gap, sgain, sdur, fall, name, thump_db=-4, rt=1.6, wet=0.6):
    c = click5(size, thump_db)
    head = np.concatenate([np.zeros(int(0.02 * SR)), c])
    if sgain > 0:
        sv = servo(160, 900, sdur, 'saw', lp_hz=1600, hum_db=-36, rise=0.15, fall=fall)
        tail = np.concatenate([np.zeros(int(gap * SR)), sv]) * sgain
        return save(name, mix(head, reverb(tail, rt=rt, dark=1500, wet=wet)))
    return save(name, mix(head, reverb(np.zeros(int(0.3 * SR)), rt=rt)))

V = {}
V['a'] = one(20, 0.25, 0.05, 1.3, 0.8, 'r7-a')                 # 10x click, siren as in c
V['b'] = one(20, 0.40, 0.035, 1.3, 0.8, 'r7-b')                # 10x click, siren later and fainter
V['c'] = one(20, 0.0, 0.0, 0, 0, 'r7-c')                       # 10x click, no siren
V['d'] = one(20, 0.25, 0.05, 1.3, 0.8, 'r7-d', thump_db=-1)    # 10x click with more low weight, siren as in c
V['e'] = one(20, 0.25, 0.05, 1.3, 0.8, 'r7-e', rt=3.0, wet=0.8)  # 10x click, siren in a much bigger room
json.dump({"title": "Click Five Long", "h1": "click 5 · ten times as long", "out": "click-clusters-7.html", "vars": [
 ["r7-a", "10×, siren as before", "The click rings ten times as long as the original (about a quarter second). Siren as in the one you chose."],
 ["r7-b", "10×, siren later", "Same click. The siren waits 0.4 s and is fainter."],
 ["r7-c", "10×, no siren", "The long click alone, with a little room."],
 ["r7-d", "10×, heavier", "Same click with more low weight in the thump. Siren as before."],
 ["r7-e", "10×, big room", "Same click; the siren sits in a much bigger, darker room."]
]}, open('vars7.json', 'w', encoding='utf-8'), indent=1)
print(V)
