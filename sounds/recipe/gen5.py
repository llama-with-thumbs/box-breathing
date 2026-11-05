"""Round 5: clicks 1, 4, 5 overlapping, so they fuse into one compound click."""
import numpy as np, os, json
from scipy.io import wavfile
from gen3 import c_clicks, SR
D = os.path.dirname(os.path.abspath(__file__))
t, hits = c_clicks()
pick = [0, 3, 4]
def lay(times, name):
    n = int((max(times) + 0.2) * SR); out = np.zeros(n)
    for ti, i in zip(times, pick):
        s = int(ti * SR); c = hits[i]; out[s:s + len(c)] += c[:n - s]
    out = out / (np.abs(out).max() + 1e-9) * 0.89
    wavfile.write(os.path.join(D, name + '.wav'), SR, (out * 32767).astype(np.int16)); return n / SR
V = {}
V['a'] = lay([0.0, 0.030, 0.060], 'r5-a')   # 30 ms apart: three edges you can still count
V['b'] = lay([0.0, 0.012, 0.024], 'r5-b')   # 12 ms apart: one click with a rough edge
V['c'] = lay([0.0, 0.003, 0.006], 'r5-c')   # 3 ms apart: stacked, one fat click
V['d'] = lay([0.0, 0.060, 0.072], 'r5-d')   # 1 alone, then 4 and 5 fused 12 ms apart
json.dump({"title": "Fused Clicks", "h1": "clicks 1 + 4 + 5 · overlapping", "out": "click-clusters-5.html", "vars": [
 ["r5-a", "30 ms apart", "Each click starts while the last one is still settling. Three edges you can still count."],
 ["r5-b", "12 ms apart", "One click with a rough, doubled edge."],
 ["r5-c", "3 ms apart", "Stacked almost on top of each other: one fat click."],
 ["r5-d", "1, then 4+5 fused", "Click 1 alone, 60 ms later clicks 4 and 5 fused 12 ms apart. Two sounds, the second thicker."]
]}, open('vars5.json', 'w', encoding='utf-8'), indent=1)
print(V)
