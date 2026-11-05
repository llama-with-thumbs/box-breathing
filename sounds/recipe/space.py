"""Spacious, slow, low: the 5+6 pair slowed 12-20x, rounded, in a dark room. Five options; set S2 for the four corners."""
import json, base64, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, butter, sosfilt, fftconvolve
sr, pair = wavfile.read('p-56.wav'); pair = pair.astype(float) / 32767
_, k6 = wavfile.read('x-k6.wav'); k6 = k6.astype(float) / 32767; k6 = k6[int(0.02 * sr):]
def lp(x, fc, o=4): return sosfilt(butter(o, fc, 'low', fs=sr, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=sr, output='sos'), x)
def norm(y, peak=0.89): return y / (np.abs(y).max() + 1e-9) * peak
def slow(x, f): return resample_poly(x, int(round(f * 10)), 10)
def soft_start(x, onset, fc_lo, fc_hi, over):
    a, b = lp(x, fc_lo), lp(x, fc_hi)
    w = np.zeros(len(x)); s = int(onset * sr); n = int(over * sr)
    w[s:s + n] = np.linspace(0, 1, n) ** 2; w[s + n:] = 1; w[:s] = 0
    return a * (1 - w) + b * w
def rounded(x, fade):
    y = x.copy(); s = int(np.argmax(np.abs(y) > 0.01 * np.abs(y).max())); n = int(fade * sr)
    y[s:s + n] *= np.linspace(0, 1, n) ** 1.5; return y
def trim(x, floor=0.004):
    a = np.abs(x); pk = a.max(); s = max(0, np.argmax(a > 0.01 * pk) - int(0.005 * sr))
    F = int(0.02 * sr); env = np.array([a[j:j+F].max() for j in range(0, len(a), F)])
    last = np.max(np.nonzero(env > floor * pk)[0]); y = x[s:min(len(x), (last + 2) * F)].copy()
    n = int(0.05 * sr); y[-n:] *= np.linspace(1, 0, n); return y
def room(x, rt, dark, wet, pre=0.02):
    n = int(rt * sr)
    ir = np.random.default_rng(3).standard_normal(n) * np.exp(-6.9 * np.arange(n) / n)
    ir = hp(lp(ir, dark, 2), 170); ir /= np.sqrt((ir ** 2).sum())
    w = fftconvolve(x, ir)[:len(x) + n]
    out = np.zeros(len(w) + int(pre * sr)); out[:len(x)] += x * (1 - wet)
    out[int(pre * sr):int(pre * sr) + len(w)] += w * wet; return out
def click(src, f, fc=350, fade=0.04):
    return rounded(soft_start(slow(src, f), 0.02 * f, 180, fc, 0.0375 * f), fade)
S = {
 's1': trim(room(click(pair, 12), 1.0, 500, 0.35)),            # 12x, small dark room
 's2': trim(room(click(pair, 16), 1.6, 450, 0.45)),            # 16x, a bigger room
 's3': trim(room(click(pair, 20, fc=300, fade=0.06), 1.6, 400, 0.45)),   # 20x, lower still, darker
 's4': trim(room(click(k6, 16, fc=350), 2.2, 450, 0.55)),      # one hit, 16x, a big room
 's5': trim(room(click(pair, 16), 2.4, 400, 0.65)),            # 16x, mostly room
}
for k, y in S.items():
    wavfile.write('sp-' + k + '.wav', sr, (norm(y) * 32767).astype(np.int16)); print(k, round(len(y) / sr, 2), 's')
json.dump({"title": "Spacious Corners", "h1": "corner click · spacious, slow, low", "out": "spacious.html", "vars": [
 ["ph-c2", "Now", "What the page does today: 8x, to 350 Hz, dry.", "0"],
 ["sp-s1", "S1 · 12x, small dark room", "Half again slower and lower; a short room, nothing above 500 Hz in the tail.", "S1"],
 ["sp-s2", "S2 · 16x, bigger room", "Twice as slow as now, an octave lower; a room of about 1.6 s.", "S2"],
 ["sp-s3", "S3 · 20x, lower still, darker", "Two and a half times slower; nothing above 300 Hz in the hit, 400 in the room.", "S3"],
 ["sp-s4", "S4 · one hit, 16x, big room", "Only the second hit of the pair, so one event, then its room.", "S4"],
 ["sp-s5", "S5 · 16x, mostly room", "The hit nearly inside the room: more air than object.", "S5"]
]}, open('vars-sp.json', 'w', encoding='utf-8'), indent=1)
# ship S2 as the four corners: 16x * (1, .9125, 1.075, 1.1625)
out = {}
for i, f in enumerate([16.0, 14.6, 17.2, 18.6], 1):
    y = trim(room(click(pair, f), 1.6, 450, 0.45))
    y8 = norm(resample_poly(y, 8000, 44100))
    wavfile.write(f'corner{i}.wav', 8000, (y8 * 32767).astype(np.int16))
    out[f'corner{i}'] = base64.b64encode(open(f'corner{i}.wav', 'rb').read()).decode()
    print(f'corner{i}', round(len(y8) / 8000, 2), 's', len(out[f'corner{i}']) // 1024, 'KB')
json.dump(out, open('embed4.json', 'w'))
