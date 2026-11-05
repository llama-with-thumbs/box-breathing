import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
sr, x = wavfile.read(sys.argv[1]); x = x.astype(np.float64) / 32768
print('len', len(x) / sr, 'peak', np.abs(x).max(), 'rms', np.sqrt((x**2).mean()))
# high-frequency energy in 2 ms frames: where the transients are
hf = sosfilt(butter(2, 1500, 'high', fs=sr, output='sos'), x)
F = int(0.002 * sr); nf = len(x) // F
e = np.array([np.sqrt((hf[i*F:(i+1)*F]**2).mean()) for i in range(nf)])
el = np.array([np.sqrt((x[i*F:(i+1)*F]**2).mean()) for i in range(nf)])
med = np.median(e)
print('hf median', med, 'hf max', e.max())
# onsets: frames where hf energy jumps above 4x the local background and 6x median
on = []
for i in range(2, nf):
    bg = e[max(0, i-25):i-1].mean() + 1e-6
    if e[i] > 6 * med and e[i] > 4 * bg and (not on or i - on[-1] > 8):
        on.append(i)
print('onsets (s):', [round(i * F / sr, 3) for i in on])
print('frame energies (ms: hf, full) around peaks:')
for i in on:
    print(round(i*F/sr,3), [round(float(v),4) for v in e[i-1:i+6]])
# spectral centroid of the whole thing vs of click frames
def cent(seg):
    S = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))); f = np.fft.rfftfreq(len(seg), 1/sr); return (S*f).sum()/S.sum()
print('centroid all', round(cent(x)), 'Hz')
for i in on[:12]:
    s = i*F; print(' click at', round(s/sr,3), 'centroid', round(cent(x[s:s+int(0.03*sr)])), 'Hz')
