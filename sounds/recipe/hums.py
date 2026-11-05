"""Background hums for breathing (H), for unclench (U), and step signals for unclench (S). All by the twelve rules:
nothing under 180 Hz, octaves only under 500 Hz, onsets >= 30 ms, drones change slower than you notice."""
import json, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
SR = 22050
def t_(dur): return np.arange(int(dur * SR)) / SR
def lp(x, fc, o=2): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=4): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def sine(f, dur, drift=0.0, vib=0.0, vibhz=0.2):          # drift: semitones over the whole clip; vib: cents
    t = t_(dur); semis = drift * t / dur + (vib / 100) * np.sin(2 * np.pi * vibhz * t)
    return np.sin(2 * np.pi * np.cumsum(f * 2 ** (semis / 12)) / SR)
def noise(dur, seed=1): return np.random.default_rng(seed).standard_normal(int(dur * SR))
def fade(x, a=1.0, r=1.0):
    y = x.copy(); n = int(a * SR); m = int(r * SR); y[:n] *= np.linspace(0, 1, n) ** 2; y[-m:] *= np.linspace(1, 0, m) ** 2; return y
def room(x, rt=1.8, dark=1800, wet=0.4):
    n = int(rt * SR); ir = np.random.default_rng(3).standard_normal(n) * np.exp(-6.9 * np.arange(n) / n)
    ir = hp(lp(ir, dark), 180); ir /= np.sqrt((ir ** 2).sum()); w = fftconvolve(x, ir)[:len(x)]
    return x * (1 - wet) + w * wet
def onset(x, ms):                                         # soft start, rule 4
    n = int(ms / 1000 * SR); y = x.copy(); y[:n] *= np.linspace(0, 1, n) ** 1.5; return y
def decay(dur, tau): return np.exp(-t_(dur) / tau)
def save(name, x, peak=0.7):
    x = hp(x, 180); x = x / (np.abs(x).max() + 1e-9) * peak
    wavfile.write(name + '.wav', SR, (x * 32767).astype(np.int16)); return len(x) / SR
D = 12.0
H = {}
# H1 octave stack, the upper voice a quarter-hertz off so the pair swells once every 4 s
H['h1'] = fade(sine(330, D) + 0.4 * np.sin(2 * np.pi * (660 + 0.25) * t_(D)) + 0.12 * sine(1320, D))
# H2 air: a band of noise, swelling once per 16 s cycle (the box), nothing tonal
sw = 0.6 + 0.4 * (0.5 - 0.5 * np.cos(2 * np.pi * t_(D) / 16))
H['h2'] = fade(bp(noise(D), 300, 1500) * sw)
# H3 hum from harmonics only: 330, 660, 1320 at falling levels, a hair of noise, slow vibrato 3 cents at 0.15 Hz
H['h3'] = fade(sine(330, D, vib=3, vibhz=0.15) + 0.5 * sine(660, D, vib=3, vibhz=0.15) + 0.2 * sine(1320, D, vib=3, vibhz=0.15) + 0.05 * bp(noise(D, 2), 300, 1200))
# H4 drift: D4 octave pair sliding down one semitone over the whole clip, in a room
H['h4'] = fade(room(sine(294, D, drift=-1) + 0.4 * sine(588, D, drift=-1), rt=2.5, dark=1400, wet=0.5))
# H5 the old breath tone, moved up where the phone can hold it: 330 + octave, rising one semitone over an inhale
t = t_(D); b = np.clip((t - 2) / 4, 0, 1); e = b * b * (3 - 2 * b); e2 = 1 - np.clip((t - 8) / 4, 0, 1); e = np.minimum(e, e2 * e2 * (3 - 2 * e2))
ph = 2 * np.pi * np.cumsum(330 * 2 ** (e / 12)) / SR
H['h5'] = fade(np.sin(ph) + 0.4 * np.sin(2 * ph))
# H6 air + harmonics together
H['h6'] = fade(0.6 * (sine(330, D, vib=2, vibhz=0.1) + 0.4 * sine(660, D, vib=2, vibhz=0.1)) + 0.5 * bp(noise(D, 4), 300, 1200) * sw)
U = {}
# U1 air only, lower band, one slow swell over the clip (as if over 24 s)
U['u1'] = fade(bp(noise(D, 5), 250, 900) * (0.6 + 0.4 * (0.5 - 0.5 * np.cos(2 * np.pi * t_(D) / 24))))
# U2 C4 octave pair in a big dark room, almost no motion
U['u2'] = fade(room(sine(262, D, vib=2, vibhz=0.07) + 0.35 * sine(524, D, vib=2, vibhz=0.07), rt=3.5, dark=1100, wet=0.6))
# U3 G4 + octave with warm noise, sinking a semitone over the clip (as the body lets go)
U['u3'] = fade(0.7 * (sine(392, D, drift=-1) + 0.4 * sine(784, D, drift=-1)) + 0.35 * bp(noise(D, 6), 300, 800))
# U4 two octaves apart (262 and 1048), beating slow, with air
U['u4'] = fade(room(sine(262, D) + 0.25 * np.sin(2 * np.pi * 1048.3 * t_(D)) + 0.3 * bp(noise(D, 7), 300, 700), rt=2.0, dark=1500, wet=0.4))
S = {}
# S0 the ping as it is: 220 Hz sine, fast on, short
S['s0'] = np.sin(2 * np.pi * 220 * t_(0.6)) * decay(0.6, 0.15)
# S1 same idea up where the phone holds it: 330 + octave, 40 ms on, 0.7 s out
S['s1'] = onset((np.sin(2 * np.pi * 330 * t_(1.0)) + 0.3 * np.sin(2 * np.pi * 660 * t_(1.0))) * decay(1.0, 0.25), 40)
# S2 bowl: 330 with an inharmonic partner at 2.76x, 50 ms on, long out, room
S['s2'] = room(onset((np.sin(2 * np.pi * 330 * t_(2.5)) * decay(2.5, 0.7) + 0.25 * np.sin(2 * np.pi * 330 * 2.76 * t_(2.5)) * decay(2.5, 0.35)), 50), rt=1.5, dark=2500, wet=0.3)
# S3 two soft wooden taps, 300-1200 Hz noise, 30 ms on, 120 ms apart
tap = onset(bp(noise(0.25, 8), 300, 1200) * decay(0.25, 0.03), 30)
s3 = np.zeros(int(0.6 * SR)); s3[:len(tap)] += tap; s3[int(0.12 * SR):int(0.12 * SR) + len(tap)] += tap * 0.8
S['s3'] = room(s3, rt=1.0, dark=2000, wet=0.3)
# S4 the family: the corner click (recorded pair, 8x, rounded) as the step cue
sr8, c8 = wavfile.read('corner1.wav'); S['s4'] = resample_poly(c8.astype(float) / 32767, SR, sr8)
# S5 the exhale slide as it is: 330 -> 165 over 6 s (goes under the phone)
S['s5'] = np.sin(2 * np.pi * np.cumsum(330 * 2 ** (-t_(6.0) / 6.0)) / SR) * fade(np.ones(int(6 * SR)), 0.3, 2.0) * 0.8
# S6 the slide kept above 180: 440 -> 330 over 6 s, with its octave
k = -0.415 * t_(6.0) / 6.0
S['s6'] = (np.sin(2 * np.pi * np.cumsum(440 * 2 ** k) / SR) + 0.3 * np.sin(2 * np.pi * np.cumsum(880 * 2 ** k) / SR)) * fade(np.ones(int(6 * SR)), 0.3, 2.0)
for k_, y in {**H, **U, **S}.items(): save('hm-' + k_, y)
json.dump({"title": "Hums And Signals", "h1": "hums for breathing · hums for unclench · signals for unclench", "out": "hums.html", "vars": [
 ["hm-h1", "Breathing · octave stack, slow beat", "330 Hz with its octave a quarter-hertz off, so the pair swells once every four seconds. Nothing moves faster than that.", "H1"],
 ["hm-h2", "Breathing · air", "A band of noise, 300-1500 Hz, swelling once per box (16 s). No note at all.", "H2"],
 ["hm-h3", "Breathing · hum from harmonics", "330, 660, 1320 at falling levels with a 3-cent wobble every seven seconds. The ear hears something lower than any of them.", "H3"],
 ["hm-h4", "Breathing · drift", "D4 and its octave in a large dark room, sinking one semitone over the clip (on the page that would be over the whole two minutes).", "H4"],
 ["hm-h5", "Breathing · the old tone, moved up", "What the page had, at 330 instead of 220, octave not fifth: rises one semitone on the inhale, falls on the exhale.", "H5"],
 ["hm-h6", "Breathing · air and harmonics", "H3 under H2: a note to lean on and air that breathes.", "H6"],
 ["hm-u1", "Unclench · air only", "Noise 250-900 Hz with one slow swell. Nothing to follow; a room to be in.", "U1"],
 ["hm-u2", "Unclench · C4 in a big room", "An octave pair, almost still, in a 3.5 s dark room.", "U2"],
 ["hm-u3", "Unclench · sinking", "G4 with warm air, dropping a semitone over the clip, as the body lets go.", "U3"],
 ["hm-u4", "Unclench · wide and slow", "C4 and the C two octaves up, beating slowly, with air.", "U4"],
 ["hm-s0", "Signal · the ping as it is", "220 Hz sine, instant on. For comparison; it breaks rules 4 and 5.", "S0"],
 ["hm-s1", "Signal · the ping, moved up", "330 + octave, 40 ms on, 0.7 s out.", "S1"],
 ["hm-s2", "Signal · bowl", "330 with an inharmonic partner (2.76x), 50 ms on, two seconds of ring in a room.", "S2"],
 ["hm-s3", "Signal · two wooden taps", "Noise 300-1200 Hz, 30 ms on, 120 ms apart. No note.", "S3"],
 ["hm-s4", "Signal · the family click", "The corner click from the breathing page as the step cue: one material across both pages (rule 9).", "S4"],
 ["hm-s5", "Signal · the exhale slide as it is", "330 down to 165 over six seconds. Goes under the phone halfway (rule 5).", "S5"],
 ["hm-s6", "Signal · the slide kept above 180", "440 down to 330 with its octave, same six seconds.", "S6"]
]}, open('vars-hm.json', 'w', encoding='utf-8'), indent=1)
