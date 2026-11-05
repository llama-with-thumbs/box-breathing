"""Keep the clicks whole this time: onsets from the full band, windows that run until the click has actually died away,
nothing subtracted inside them. A second, gentle version takes out only the steady hum that sits under each click."""
import sys, os, json, numpy as np
from scipy.io import wavfile
from scipy.signal import stft, istft
src, outdir = sys.argv[1], sys.argv[2]
sr, x = wavfile.read(src); x = x.astype(np.float64) / 32768; x -= x.mean()
F = int(0.002 * sr); nf = len(x) // F
e = np.array([np.sqrt((x[i*F:(i+1)*F]**2).mean()) for i in range(nf)])

# onsets: a 2 ms frame at least 2.2x the mean of the 40 ms before it, and above an absolute floor; one per 40 ms
on = []
for i in range(20, nf):
    bg = e[i-20:i-1].mean() + 1e-6
    if e[i] > 2.2 * bg and e[i] > 0.0025 and (not on or i - on[-1] > 20): on.append(i)
# each click runs from 6 ms before its onset until the envelope has sat at the pre-onset level for 20 ms (60-300 ms)
wins = []
for i in on:
    pre = e[max(0, i-20):i-2].mean()
    j = i + 30; quiet = 0
    while j < nf and j - i < 150:
        quiet = quiet + 1 if e[j] < 1.3 * pre + 0.0008 else 0
        if quiet >= 10: break
        j += 1
    wins.append((max(0, i * F - int(0.006 * sr)), min(len(x), j * F)))
def gate(sig, wins, fade_in=0.003, fade_out=0.015):
    g = np.zeros(len(sig))
    for s, eN in wins:
        g[s:eN] = 1
        fi = int(fade_in * sr); fo = int(fade_out * sr)
        g[s:s+fi] = np.minimum(g[s:s+fi], np.linspace(0, 1, fi)); g[eN-fo:eN] = np.minimum(g[eN-fo:eN], np.linspace(1, 0, fo))
    return sig * g
whole = gate(x, wins)
# gentle hum removal: for each click, the spectrum of the 60 ms just before it is the hum; subtract 0.8 of it, floor at 35 %
f, t, Z = stft(x, sr, nperseg=512, noverlap=384)
Zc = Z.copy()
for (s, eN), i in zip(wins, on):
    pre_frames = (t >= (i*F)/sr - 0.06) & (t < (i*F)/sr - 0.004)
    in_frames = (t >= s/sr) & (t < eN/sr)
    if pre_frames.sum() < 2: continue
    hum = np.abs(Z[:, pre_frames]).mean(axis=1, keepdims=True)
    mag = np.abs(Z[:, in_frames]); ph = np.angle(Z[:, in_frames])
    Zc[:, in_frames] = np.maximum(mag - 0.8 * hum, 0.35 * mag) * np.exp(1j * ph)
_, xc = istft(Zc, sr, nperseg=512, noverlap=384); xc = xc[:len(x)]
gentle = gate(xc, wins)
def save(name, y, peak=0.89):
    y = y / (np.abs(y).max() + 1e-9) * peak
    wavfile.write(os.path.join(outdir, name + '.wav'), sr, (y * 32767).astype(np.int16)); return len(y) / sr
save('w-orig', x); save('w-whole', whole); save('w-gentle', gentle)
g = 0.89 / (np.abs(whole).max() + 1e-9)
rows = [["w-orig", "Original", "As recorded, brought up to level.", "0"],
        ["w-whole", "Clicks, whole", "Only the gaps are silenced. Each click kept from 6 ms before its edge until it has died back to the level before it. Nothing taken out of the clicks.", "1"],
        ["w-gentle", "Clicks, hum taken out", "Same windows; inside each, only the steady hum that was already there just before the click is subtracted, gently.", "2"]]
for k, ((s, eN), i) in enumerate(zip(wins, on), 1):
    seg = np.concatenate([np.zeros(int(0.02 * sr)), whole[s:eN] * g, np.zeros(int(0.12 * sr))])
    wavfile.write(os.path.join(outdir, f'w-k{k}.wav'), sr, (seg * 32767).astype(np.int16))
    rows.append([f"w-k{k}", f"Click {k}", f"At {i*F/sr:.2f} s, kept for {(eN-s)/sr*1000:.0f} ms, peak {e[i:i+5].max()*100:.1f} % of full scale.", f"k{k}"])
json.dump({"title": "Voice 030 Clicks II", "h1": "voice 030 · the clicks, whole", "out": "voice030-2.html", "vars": rows}, open('vars-w.json', 'w', encoding='utf-8'), indent=1)
print([(round(i*F/sr, 2), round((eN-s)/sr*1000)) for (s, eN), i in zip(wins, on)])
