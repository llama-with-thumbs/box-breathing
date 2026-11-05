"""Corner clicks: cut everything under 170 Hz. A phone speaker cannot play it; at full level it only overdrives the cone."""
import base64, json, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
out = {}
for i in range(1, 5):
    sr, x = wavfile.read(f'corner{i}.wav'); x = x.astype(float) / 32767
    lo = lambda y: np.sqrt(np.mean(sosfilt(butter(4, 170, 'low', fs=sr, output='sos'), y) ** 2))
    y = sosfilt(butter(2, 170, 'high', fs=sr, output='sos'), x)
    y = y / (np.abs(y).max() + 1e-9) * 0.89
    n = int(0.01 * sr); y[-n:] *= np.linspace(1, 0, n)
    print(f'corner{i}: under 170 Hz rms {lo(x):.3f} -> {lo(y):.3f}; peak {np.abs(x).max():.2f} -> {np.abs(y).max():.2f}')
    wavfile.write(f'corner{i}.wav', sr, (y * 32767).astype(np.int16))
    out[f'corner{i}'] = base64.b64encode(open(f'corner{i}.wav', 'rb').read()).decode()
json.dump(out, open('embed4.json', 'w'))
