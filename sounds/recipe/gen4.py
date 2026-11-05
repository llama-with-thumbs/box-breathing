"""Round 4: clicks 1, 4 and 5 of c, combined."""
import numpy as np, os, json
from scipy.io import wavfile
from gen3 import c_clicks, SR
D = os.path.dirname(os.path.abspath(__file__))
t, hits = c_clicks()
pick = [0, 3, 4]
g = 0.89 / max(np.abs(hits[i]).max() for i in pick)
def lay(times, name):
    n = int((max(times) + 0.25) * SR); out = np.zeros(n)
    for ti, i in zip(times, pick):
        s = int(ti * SR); c = hits[i] * g; out[s:s + len(c)] += c[:n - s]
    wavfile.write(os.path.join(D, name + '.wav'), SR, (out * 32767).astype(np.int16)); return n / SR
V = {}
V['a'] = lay([0.0, 0.78, 0.94], 'r4-a')         # as they sat in the cluster: one, a wait, then two close
V['b'] = lay([0.0, 0.26, 0.42], 'r4-b')         # tightened: same shape, a third of the wait
V['c'] = lay([0.0, 0.18, 0.36], 'r4-c')         # even: three in a row, 180 ms apart
json.dump({"title": "Three Clicks", "h1": "clicks 1 + 4 + 5 · combined", "out": "click-clusters-4.html", "vars": [
 ["r4-a", "As they sat", "Original timing from the cluster: 0.00 · 0.78 · 0.94 s. One, a wait, then two close."],
 ["r4-b", "Tightened", "Same shape, the wait cut to a third: 0.00 · 0.26 · 0.42 s."],
 ["r4-c", "Even", "Three in a row, 180 ms apart: 0.00 · 0.18 · 0.36 s."]
]}, open('vars4.json', 'w', encoding='utf-8'), indent=1)
print(V)
