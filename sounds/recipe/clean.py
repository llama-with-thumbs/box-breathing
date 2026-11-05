"""Keep only the clicks of a recording: gate everything else to silence, with a light spectral clean inside the clicks."""
import sys, os, json, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, stft, istft
src, outdir = sys.argv[1], sys.argv[2]
sr, x = wavfile.read(src); x = x.astype(np.float64) / 32768
x = x - x.mean()

# 1 · spectral subtraction: noise profile from the first 0.6 s (nothing happens there)
f, t, Z = stft(x, sr, nperseg=1024, noverlap=768)
noise = np.abs(Z[:, t < 0.6]).mean(axis=1, keepdims=True)
mag = np.abs(Z); ph = np.angle(Z)
clean_mag = np.maximum(mag - 2.0 * noise, 0.08 * mag)
_, xc = istft(clean_mag * np.exp(1j * ph), sr, nperseg=1024, noverlap=768)
xc = xc[:len(x)]

# 2 · onsets from high-frequency energy, 2 ms frames
hf = sosfilt(butter(2, 1500, 'high', fs=sr, output='sos'), x)
F = int(0.002 * sr); nf = len(x) // F
e = np.array([np.sqrt((hf[i*F:(i+1)*F]**2).mean()) for i in range(nf)])
med = np.median(e); on = []
for i in range(2, nf):
    bg = e[max(0, i-25):i-1].mean() + 1e-6
    if e[i] > 4.5 * med and e[i] > 3 * bg and (not on or i - on[-1] > 8): on.append(i)
onsets = [i * F / sr for i in on]

# 3 · gate: keep 4 ms before each onset to where the energy has fallen back to the floor (max 120 ms), 3 ms fades
def gate(sig):
    g = np.zeros(len(sig))
    for i in on:
        s = i * F - int(0.004 * sr)
        # end: first frame after the onset whose hf energy is back under 1.5x median, at least 25 ms, at most 120 ms
        j = i + 12
        while j < nf and j - i < 60 and e[j] > 1.5 * med: j += 1
        eN = min(len(sig), j * F + int(0.01 * sr))
        g[max(0, s):eN] = 1
    fade = int(0.003 * sr); k = np.ones(fade) / fade
    g = np.convolve(g, k, mode='same')
    return sig * g
clicks_raw = gate(x)
clicks_clean = gate(xc)

def save(name, y, peak=0.89):
    y = y / (np.abs(y).max() + 1e-9) * peak
    wavfile.write(os.path.join(outdir, name + '.wav'), sr, (y * 32767).astype(np.int16)); return len(y) / sr
V = {}
V['orig'] = save('v-orig', x)
V['gated'] = save('v-gated', clicks_raw)
V['clean'] = save('v-clean', clicks_clean)
g = 0.89 / (np.abs(clicks_clean).max() + 1e-9)
for k, i in enumerate(on, 1):
    s = max(0, i * F - int(0.004 * sr)); seg = clicks_clean[s:s + int(0.14 * sr)] * g
    seg = np.concatenate([np.zeros(int(0.02 * sr)), seg, np.zeros(int(0.1 * sr))])
    wavfile.write(os.path.join(outdir, f'v-k{k}.wav'), sr, (seg * 32767).astype(np.int16)); V[f'k{k}'] = len(seg) / sr
# 4 · the clicks tightened: same clicks, 180 ms apart
tight = np.zeros(int((0.18 * len(on) + 0.3) * sr))
for k, i in enumerate(on):
    s = max(0, i * F - int(0.004 * sr)); seg = clicks_clean[s:s + int(0.14 * sr)]
    p = int((0.02 + 0.18 * k) * sr); tight[p:p + len(seg)] += seg
V['tight'] = save('v-tight', tight)
json.dump({'onsets': onsets, 'durations': V}, open(os.path.join(outdir, 'info.json'), 'w'))
print(json.dumps({'onsets': [round(o, 3) for o in onsets], 'n': len(on)}))
