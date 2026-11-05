"""Breath-tone options, 8 s each: in 1 s, up over 2-6 s (smoothstep, like an inhale), held, out. For the phone."""
import json, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
sr = 44100
def tone(f0, parts, semis=1.0, dur=8.0, swell=0.0, lp=None):
    t = np.arange(int(dur * sr)) / sr
    b = np.clip((t - 2) / 4, 0, 1); e = b * b * (3 - 2 * b); f = f0 * 2 ** (e * semis / 12)
    ph = 2 * np.pi * np.cumsum(f) / sr
    y = sum(g * np.sin(r * ph) for r, g in parts)
    if lp: y = sosfilt(butter(2, lp, 'low', fs=sr, output='sos'), y)
    env = np.minimum(1, t / 1.0); env[-int(0.5 * sr):] *= np.linspace(1, 0, int(0.5 * sr))
    if swell: env = env * (1 - swell + swell * (0.5 - 0.5 * np.cos(2 * np.pi * t / 8)))
    return y * env * 0.45
T = {
 't0': tone(220, [(1, 1), (1.5, 0.6)], semis=2),         # before: fifth, two semitones
 't1': tone(220, [(1, 1), (2, 0.4)]),                      # now: octave
 't2': tone(196, [(1, 1), (2, 0.4)]),                      # G, a little deeper
 't3': tone(220, [(1, 1), (2, 0.4), (3, 0.15)], lp=900),   # warm: a quiet third harmonic, rounded
 't4': tone(220, [(1, 1)]),                                # one sine alone
 't5': tone(220, [(1, 1), (2, 0.4)], swell=0.35),          # octave with a slow swell, 8 s round
 't6': tone(185, [(1, 1), (2, 0.5)]),                      # F#, deeper still; the phone carries mostly the 370
}
for k, y in T.items(): wavfile.write('tn-' + k + '.wav', sr, (y * 32767).astype(np.int16))
json.dump({"title": "Breath Tone Options", "h1": "breath tone · deeper, slower, less buzz", "out": "tones.html", "vars": [
 ["tn-t0", "T0 · Before: 220 + fifth", "Two notes a fifth apart pulse at 110 Hz; on a phone that is the buzz.", "T0"],
 ["tn-t1", "T1 · Now: 220 + octave", "Same low note, its octave quietly above it. One semitone of rise, slower.", "T1"],
 ["tn-t2", "T2 · 196 + octave", "A tone and a half deeper (G).", "T2"],
 ["tn-t3", "T3 · 220, warm", "Octave plus a quiet third harmonic, rounded off: fuller, still smooth.", "T3"],
 ["tn-t4", "T4 · 220 alone", "One sine, nothing else.", "T4"],
 ["tn-t5", "T5 · 220 + octave, slow swell", "T1 with the loudness rolling slowly, like a far engine.", "T5"],
 ["tn-t6", "T6 · 185 + octave", "Deeper still (F#). The phone speaker carries mostly the upper note.", "T6"]
]}, open('vars-tn.json', 'w', encoding='utf-8'), indent=1)
