"""Round 8: click 5 in slow motion: the click itself stretched, pitch dropping with it, as a slowed-down recording does."""
import numpy as np, os, json
from scipy.signal import resample_poly
from gen import servo, reverb, mix, save, SR
from gen7 import click5
D = os.path.dirname(os.path.abspath(__file__))

def slow(c, factor):
    return resample_poly(c, factor, 1)              # factor x longer, factor x lower

def one(c, factor, sgain, name, gap=0.25, sdur=1.3, fall=0.8):
    s = slow(c, factor)
    head = np.concatenate([np.zeros(int(0.02 * SR)), s])
    if sgain > 0:
        sv = servo(160, 900, sdur, 'saw', lp_hz=1600, hum_db=-36, rise=0.15, fall=fall)
        tail = np.concatenate([np.zeros(int((len(head) / SR + gap) * SR)), sv]) * sgain
        return save(name, mix(head, reverb(tail, rt=1.6, dark=1500)))
    return save(name, mix(head, reverb(np.zeros(int(0.3 * SR)), rt=1.6)))

c0 = click5(2.0)      # the click as it was in the cluster (60 ms)
c10 = click5(20)      # the ten-times version you chose from
V = {}
V['a'] = one(c0, 4, 0.05, 'r8-a')          # 4x slow: quarter second, two octaves down
V['b'] = one(c0, 8, 0.05, 'r8-b')          # 8x slow: half second, three octaves down
V['c'] = one(c0, 16, 0.05, 'r8-c')         # 16x slow: one second, four octaves down
V['d'] = one(c10, 4, 0.05, 'r8-d')         # the long click, 4x slow: about a second
V['e'] = one(c0, 8, 0.0, 'r8-e')           # 8x slow, no siren
json.dump({"title": "Slow Motion Click", "h1": "click 5 · slow motion", "out": "click-clusters-8.html", "vars": [
 ["r8-a", "4× slow", "The original click stretched four times: a quarter second, pitch two octaves down. Then the quiet siren."],
 ["r8-b", "8× slow", "Eight times: half a second, three octaves down. The snap becomes a thud, the settle a rumble."],
 ["r8-c", "16× slow", "Sixteen times: a full second, four octaves down. More a door than a click."],
 ["r8-d", "Long click, 4× slow", "The ten-times click from last round, slowed four times: about a second of ring."],
 ["r8-e", "8× slow, no siren", "Like b, alone."]
]}, open('vars8.json', 'w', encoding='utf-8'), indent=1)
print(V)
