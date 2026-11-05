"""Round 12: variations on Shut (r11-f)."""
import numpy as np, os, json
from gen import mix, save, SR
from gen11 import slow, at, band, box, weight, hum, k1, k4, k5
D = os.path.dirname(os.path.abspath(__file__))
N = int(1.8 * SR)

def shut(stretch=12, hi=500, w_g=0.5, w_tau=0.18, w_f0=50, rt=0.25, wet=0.6, dark=500, hum_g=0.04, hum_cut=1.1, extra=None, name=''):
    x = at(slow(k5, stretch), 0.02, N)
    if extra is not None: x = x + extra
    core = box(band(x, 180, hi) + at(weight(f0=w_f0, dur=0.7, tau=w_tau, g=w_g), 0.02, N), rt=rt, wet=wet, dark=dark)
    if hum_g > 0: core = mix(core, hum(N + int(0.3 * SR), g=hum_g, cut=hum_cut))
    return save(name, core)

V = {}
V['a'] = shut(name='r12-a')                                              # Shut as chosen (reference)
V['b'] = shut(hum_g=0.0, name='r12-b')                                   # no hum
V['c'] = shut(hum_cut=1.6, name='r12-c')                                 # hum holds longer, cuts at 1.6 s
V['d'] = shut(stretch=16, hi=400, name='r12-d')                          # slower and darker still
V['e'] = shut(w_g=0.8, w_tau=0.3, name='r12-e')                          # more weight, longer
V['f'] = shut(extra=at(slow(k4, 12) * 0.45, 0.2, N), name='r12-f')       # second stage 180 ms later
V['g'] = shut(extra=at(slow(k5, 12) * 0.3, 0.42, N), rt=0.4, name='r12-g')  # a fainter copy of itself 0.4 s later, slightly bigger room
V['h'] = shut(rt=0.12, wet=0.7, dark=400, name='r12-h')                  # tinier room still, almost in the ear
json.dump({"title": "Shut Variations", "h1": "shut · eight variations", "out": "click-clusters-12.html", "vars": [
 ["r12-a", "Shut", "The one you chose, for reference."],
 ["r12-b", "No hum", "Shut without the hum. Just the hit and the room."],
 ["r12-c", "Hum holds", "The hum stays to 1.6 s before it cuts, so the cut lands after the room has died."],
 ["r12-d", "Slower, darker", "16× instead of 12×, nothing above 400 Hz."],
 ["r12-e", "More weight", "The low note stronger and longer under the hit."],
 ["r12-f", "Second stage", "A second slowed click 180 ms after, quieter. Two parts to the mechanism."],
 ["r12-g", "Echo of itself", "A fainter copy 0.4 s later, in a slightly bigger room. Something further away answers."],
 ["r12-h", "In the ear", "The smallest room of all, almost no air around it."]
]}, open('vars12.json', 'w', encoding='utf-8'), indent=1)
print(V)
