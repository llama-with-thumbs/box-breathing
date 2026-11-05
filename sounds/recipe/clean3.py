"""Hum out entirely: the hum's spectrum is measured right before each click and subtracted hard inside it; the floor is low."""
import os, json, numpy as np
from scipy.io import wavfile
from scipy.signal import stft, istft, butter, sosfilt
sr, x = wavfile.read('../voice030/in.wav'); x = x.astype(np.float64) / 32768; x -= x.mean()
F = int(0.002 * sr); nf = len(x) // F
e = np.array([np.sqrt((x[i*F:(i+1)*F]**2).mean()) for i in range(nf)])
on = []
for i in range(20, nf):
    bg = e[i-20:i-1].mean() + 1e-6
    if e[i] > 2.2 * bg and e[i] > 0.0025 and (not on or i - on[-1] > 20): on.append(i)
wins = []
for i in on:
    pre = e[max(0, i-20):i-2].mean(); j = i + 30; quiet = 0
    while j < nf and j - i < 150:
        quiet = quiet + 1 if e[j] < 1.3 * pre + 0.0008 else 0
        if quiet >= 10: break
        j += 1
    wins.append((max(0, i * F - int(0.006 * sr)), min(len(x), j * F)))
def gate(sig, fade_in=0.003, fade_out=0.015):
    g = np.zeros(len(sig))
    for s, eN in wins:
        g[s:eN] = 1; fi = int(fade_in * sr); fo = int(fade_out * sr)
        g[s:s+fi] = np.minimum(g[s:s+fi], np.linspace(0, 1, fi)); g[eN-fo:eN] = np.minimum(g[eN-fo:eN], np.linspace(1, 0, fo))
    return sig * g
def dehum(factor, floor, nper=512):
    f, t, Z = stft(x, sr, nperseg=nper, noverlap=nper * 3 // 4); Zc = Z.copy()
    # one hum profile for the whole take: the median spectrum of everything outside the click windows after 0.55 s
    outside = np.ones(len(t), bool)
    for s, eN in wins: outside &= ~((t >= s/sr - 0.01) & (t < eN/sr + 0.01))
    outside &= t > 0.55
    hum = np.median(np.abs(Z[:, outside]), axis=1, keepdims=True)
    mag = np.abs(Z); ph = np.angle(Z)
    Zc = np.maximum(mag - factor * hum, floor * mag) * np.exp(1j * ph)
    _, y = istft(Zc, sr, nperseg=nper, noverlap=nper * 3 // 4); return y[:len(x)]
def save(name, y, peak=0.89):
    y = y / (np.abs(y).max() + 1e-9) * peak
    wavfile.write(name + '.wav', sr, (y * 32767).astype(np.int16)); return y
a = save('x-a', gate(dehum(1.6, 0.12)))
b = save('x-b', gate(dehum(2.5, 0.04)))
c = save('x-c', gate(sosfilt(butter(2, 260, 'high', fs=sr, output='sos'), dehum(2.5, 0.04))))
g = 0.89 / (np.abs(gate(dehum(2.5, 0.04))).max() + 1e-9); src = gate(dehum(2.5, 0.04))
rows = [["x-a", "Hum out", "Hum profile from everything between the clicks, subtracted 1.6x, floor 12 %. Clicks kept whole.", "a"],
        ["x-b", "Hum out, hard", "Subtracted 2.5x, floor 4 %. The hum is gone; the clicks lose a little of their softest body.", "b"],
        ["x-c", "Hum out, hard, under 260 Hz cut", "As b, plus nothing under 260 Hz, in case the hum's lowest part was hiding there.", "c"]]
for k, (s, eN) in enumerate(wins, 1):
    seg = np.concatenate([np.zeros(int(0.02 * sr)), src[s:eN] * g, np.zeros(int(0.12 * sr))])
    wavfile.write(f'x-k{k}.wav', sr, (seg * 32767).astype(np.int16))
    rows.append([f"x-k{k}", f"Click {k}", f"At {on[k-1]*F/sr:.2f} s, from version b.", f"k{k}"])
json.dump({"title": "Voice 030 Clicks III", "h1": "voice 030 · clicks, all hum removed", "out": "voice030-3.html", "vars": rows}, open('vars-x.json', 'w', encoding='utf-8'), indent=1)
print('ok', len(wins))
