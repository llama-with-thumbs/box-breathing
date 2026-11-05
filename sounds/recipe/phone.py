"""Less clank on the phone: rounder corner clicks (four speeds as shipped) and tone options, rendered as they would play."""
import json, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, butter, sosfilt
sr, pair = wavfile.read('p-56.wav'); pair = pair.astype(float) / 32767
_, k6 = wavfile.read('x-k6.wav'); k6 = k6.astype(float) / 32767; k6 = k6[int(0.02 * sr):]
def lp(x, fc, o=4): return sosfilt(butter(o, fc, 'low', fs=sr, output='sos'), x)
def norm(y, peak=0.89): return y / (np.abs(y).max() + 1e-9) * peak
def save(name, y): wavfile.write(name + '.wav', sr, (norm(y) * 32767).astype(np.int16))
def slow(x, f): return resample_poly(x, int(round(f * 10)), 10)
def soft_start(x, onset, fc_lo, fc_hi, over):
    a, b = lp(x, fc_lo), lp(x, fc_hi)
    w = np.zeros(len(x)); s = int(onset * sr); n = int(over * sr)
    w[s:s + n] = np.linspace(0, 1, n) ** 2; w[s + n:] = 1; w[:s] = 0
    return a * (1 - w) + b * w
def trim(x):
    a = np.abs(x); pk = a.max(); s = max(0, np.argmax(a > 0.01 * pk) - int(0.005 * sr))
    F = int(0.02 * sr); env = np.array([a[j:j+F].max() for j in range(0, len(a), F)])
    last = np.max(np.nonzero(env > 0.005 * pk)[0]); y = x[s:min(len(x), (last + 2) * F)].copy()
    y[-int(0.01*sr):] *= np.linspace(1, 0, int(0.01*sr)); return y
def rounded(x, fade):                      # round the first edge: a fade-in over `fade` seconds from the first sound
    y = x.copy(); s = int(np.argmax(np.abs(y) > 0.01 * np.abs(y).max())); n = int(fade * sr)
    y[s:s + n] *= np.linspace(0, 1, n) ** 1.5; return y
# clicks (all at 8x for the gallery; the four speeds come after)
C = {}
C['c1'] = trim(soft_start(slow(pair, 8), 0.16, 180, 500, 0.2))                         # as shipped
C['c2'] = trim(rounded(soft_start(slow(pair, 8), 0.16, 180, 350, 0.3), 0.03))          # rounder: to 350 Hz, 30 ms fade-in
C['c3'] = trim(rounded(lp(soft_start(slow(pair, 10), 0.2, 160, 300, 0.4), 300, 2), 0.05))  # duller: 10x, to 300 Hz, 50 ms in
C['c4'] = trim(rounded(soft_start(slow(k6, 8), 0.0, 180, 400, 0.2), 0.03))             # one hit only (click 6), to 400 Hz
for k, y in C.items(): save('ph-' + k, y)
# tones: 4 s, ramp in 1 s, pitch up two semitones over 2-4 s (smoothstep), fifth at 0.6
def tone(f0, fifth=0.6, dur=4.0, shape='sine'):
    t = np.arange(int(dur * sr)) / sr
    b = np.clip((t - 2) / 2, 0, 1); e = b * b * (3 - 2 * b); f = f0 * 2 ** (e * 2 / 12)
    ph = 2 * np.pi * np.cumsum(f) / sr
    y = np.sin(ph) + fifth * np.sin(1.5 * ph)
    env = np.minimum(1, t / 1.0); env[-int(0.3 * sr):] *= np.linspace(1, 0, int(0.3 * sr))
    return y * env * 0.45
T = {'t1': tone(220), 't2': tone(330), 't3': tone(440), 't4': tone(220, fifth=0.25)}
for k, y in T.items(): wavfile.write('ph-' + k + '.wav', sr, (y * 32767).astype(np.int16))
# together: tone running, click at 2.0 s with the duck (30 %, 10 ms in, 150 ms back)
def together(tk, ck, name):
    tn = tone(tk, dur=5.0); c = C[ck]; s = int(2.0 * sr); n = len(c)
    d = np.ones(len(tn)); d[s:s + int(0.01 * sr)] = np.linspace(1, 0.3, int(0.01 * sr)); d[s + int(0.01 * sr):s + n] = 0.3
    back = int(0.15 * sr); d[s + n:s + n + back] = np.linspace(0.3, 1, back)
    y = tn * d; y[s:s + n] += c * 0.8 * 0.89 / (np.abs(c).max() + 1e-9)
    wavfile.write(name + '.wav', sr, (np.clip(y, -1, 1) * 32767).astype(np.int16))
together(220, 'c1', 'ph-x1'); together(220, 'c2', 'ph-x2'); together(330, 'c2', 'ph-x3'); together(440, 'c3', 'ph-x4')
json.dump({"title": "Phone Pass", "h1": "on the phone · less clank", "out": "phone-pass.html", "vars": [
 ["ph-x1", "Now: tone 220 + click as shipped", "What the page does today, one corner.", "X1"],
 ["ph-x2", "Tone 220 + rounder click", "Same tone, click to 350 Hz with a 30 ms fade-in.", "X2"],
 ["ph-x3", "Tone 330 + rounder click", "Tone a fifth up: the phone speaker plays 330 Hz cleanly, 220 Hz it strains at.", "X3"],
 ["ph-x4", "Tone 440 + duller click", "Tone an octave up, click at 10x to 300 Hz.", "X4"],
 ["ph-c1", "Click as shipped", "8x, to 500 Hz.", "C1"],
 ["ph-c2", "Click, rounder", "8x, to 350 Hz, first edge faded in over 30 ms.", "C2"],
 ["ph-c3", "Click, duller", "10x, to 300 Hz, 50 ms in.", "C3"],
 ["ph-c4", "Click, one hit", "Only the second hit of the pair, 8x, to 400 Hz.", "C4"],
 ["ph-t1", "Tone 220 (now)", "Breathes in over the second half.", "T1"],
 ["ph-t2", "Tone 330", "A fifth up.", "T2"],
 ["ph-t3", "Tone 440", "An octave up.", "T3"],
 ["ph-t4", "Tone 220, fifth quieter", "The 330 Hz partner at a quarter instead of 0.6: purer, less beating on a small speaker.", "T4"]
]}, open('vars-ph.json', 'w', encoding='utf-8'), indent=1)
# the four corner speeds with the rounder click, for the page
import base64
out = {}
for i, f in enumerate([8.0, 7.3, 8.6, 9.3], 1):
    y = trim(rounded(soft_start(slow(pair, f), 0.02 * f, 180, 350, 0.0375 * f), 0.03))
    y8 = norm(resample_poly(y, 8000, 44100))
    wavfile.write(f'corner{i}.wav', 8000, (y8 * 32767).astype(np.int16))
    out[f'corner{i}'] = base64.b64encode(open(f'corner{i}.wav', 'rb').read()).decode()
    print(f'corner{i}', round(len(y8) / 8000, 3), 's')
json.dump(out, open('embed4.json', 'w'))
