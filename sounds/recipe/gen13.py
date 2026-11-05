"""Round 13: Shut, given the qualities of an echocardiogram (Doppler heart: lub-dub, swish) and blue whale song under water
(long low moans, clicks and squeaks, a huge dark space). Everything kept above 180 Hz for laptop and S22."""
import numpy as np, os, json
from gen import mix, save, reverb, lp, hp, bp, SR
from gen11 import slow, at, band, box, weight, hum, k1, k4, k5
D = os.path.dirname(os.path.abspath(__file__))

def shut_dry(n, t0=0.02, stretch=12, g=1.0):
    x = at(slow(k5, stretch), t0, n)
    return (band(x, 180, 500) + at(weight(f0=50, dur=0.7, tau=0.18, g=0.5), t0, n)) * g

def sea(x, rt=3.5, wet=0.55, dark=700):            # under water: long, dark, everything far
    return reverb(lp(x, 1500, 2), rt=rt, dark=dark, pre=0.02, wet=wet)

def moan(dur, f0=190, f1=125, harm=(1, .6, .35, .2), g=0.35, rise=0.8, fall=1.2, wob=0.0):
    """a whale call, pitched up into what the speakers play: a slow glide with harmonics, swelling in and out"""
    n = int(dur * SR); tt = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (tt / dur) * (1 + wob * np.sin(2 * np.pi * 0.7 * tt))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(a * np.sin(k * ph) for k, a in enumerate(harm, 1))
    env = np.ones(n); r = int(rise * SR); fl = int(fall * SR)
    env[:r] = np.sin(np.linspace(0, np.pi / 2, r)) ** 2; env[-fl:] = np.cos(np.linspace(0, np.pi / 2, fl)) ** 2
    return x / np.abs(x).max() * env * g

def swish(dur=0.35, lo=300, hi=900, g=0.18, seed=1):
    """the Doppler whoosh of an echocardiogram: a band of noise that swells with the beat"""
    n = int(dur * SR); tt = np.arange(n) / SR
    x = bp(np.random.default_rng(seed).standard_normal(n), lo, hi, 2)
    return x / np.abs(x).max() * np.sin(np.pi * tt / dur) ** 2 * g

def squeak(f0=700, f1=1100, dur=0.25, g=0.12, bend=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = f0 + (f1 - f0) * (np.sin(np.pi * tt / dur) ** bend)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(2 * np.pi * 2 * np.cumsum(f) / SR)
    env = np.sin(np.pi * tt / dur) ** 0.7
    return x / np.abs(x).max() * env * g

def heart(n, t0, beats=3, bpm=62, dub_gap=0.2, g=1.0, sw=0.18):
    """lub (Shut) + dub (Shut softer, shorter) + the Doppler swish riding each pair"""
    out = np.zeros(n); per = 60 / bpm
    for b in range(beats):
        t = t0 + b * per
        out += shut_dry(n, t, 12, g) + shut_dry(n, t + dub_gap, 9, g * 0.55)
        out += at(swish(0.45, g=sw, seed=b + 1), t - 0.08, n) + at(swish(0.3, g=sw * 0.6, seed=b + 11), t + dub_gap - 0.05, n)
    return out

V = {}
# a · echocardiogram: three lub-dubs at 62 bpm, with the Doppler swish, under water
N = int(4.2 * SR)
V['a'] = save('r13-a', sea(heart(N, 0.1), rt=2.5, wet=0.45))
# b · whale moan: Shut opens it, then a 4 s glide down with harmonics, in a huge dark space
N = int(5.5 * SR)
V['b'] = save('r13-b', sea(shut_dry(N) + at(moan(4.2, g=0.4, wob=0.004), 0.05, N), rt=4.5, wet=0.6, dark=600))
# c · whale with clicks and squeaks: the moan, sparse slowed clicks sprinkled across it, two squeaks near the end
N = int(6.0 * SR)
x = shut_dry(N) + at(moan(4.5, f0=170, f1=115, g=0.33, wob=0.005), 0.05, N)
for tt_, g_ in [(0.9, .35), (1.35, .25), (1.6, .3), (2.4, .2), (2.55, .28), (3.3, .18)]:
    x += at(band(slow(k1, 4), 180, 1200) * g_, tt_, N)
x += at(squeak(650, 1000, 0.3, 0.1), 3.6, N) + at(squeak(900, 600, 0.22, 0.08, bend=0.6), 4.1, N)
V['c'] = save('r13-c', sea(x, rt=4.0, wet=0.6, dark=800))
# d · heart under the whale: beats at 56 bpm, faint, beneath a moan
N = int(6.0 * SR)
x = heart(N, 0.1, beats=5, bpm=56, g=0.6, sw=0.1) + at(moan(4.8, f0=200, f1=130, g=0.3, rise=1.5, fall=1.5), 0.6, N)
V['d'] = save('r13-d', sea(x, rt=3.5, wet=0.5))
# e · clicks and squeaks only, under water: Shut, then a loose cluster of clicks and three squeaks, huge space
N = int(5.0 * SR)
x = shut_dry(N)
rng = np.random.default_rng(13)
t_ = 0.5
for i in range(9):
    t_ += rng.uniform(0.12, 0.42)
    x += at(band(slow(k1 if i % 2 else k4, rng.integers(3, 6)), 180, 1200) * rng.uniform(0.15, 0.4), t_, N)
x += at(squeak(700, 1050, 0.28, 0.1), 2.3, N) + at(squeak(1000, 700, 0.2, 0.08, bend=0.6), 3.0, N) + at(squeak(600, 850, 0.35, 0.07), 3.7, N)
V['e'] = save('r13-e', sea(x, rt=5.0, wet=0.65, dark=900))
# f · all of it: Shut, two faint beats, the moan, a few clicks, one squeak at the end
N = int(6.5 * SR)
x = shut_dry(N) + heart(N, 0.9, beats=2, bpm=58, g=0.45, sw=0.08) + at(moan(4.5, f0=185, f1=120, g=0.3, rise=1.2, fall=1.4, wob=0.004), 0.4, N)
for tt_, g_ in [(2.9, .25), (3.15, .2), (3.9, .22)]:
    x += at(band(slow(k1, 4), 180, 1200) * g_, tt_, N)
x += at(squeak(650, 950, 0.3, 0.09), 4.6, N)
V['f'] = save('r13-f', sea(x, rt=4.5, wet=0.6, dark=700))
json.dump({"title": "Shut Heart Whale", "h1": "shut · echocardiogram · blue whale, under water", "out": "click-clusters-13.html", "vars": [
 ["r13-a", "Echocardiogram", "Shut as the lub, a softer one as the dub, three beats at 62 bpm with the Doppler swish riding each pair. Under water."],
 ["r13-b", "Whale moan", "Shut opens it, then a four-second call gliding down with its harmonics, in a huge dark space."],
 ["r13-c", "Whale, clicks, squeaks", "The moan with slowed clicks sprinkled across it and two muted squeaks near the end."],
 ["r13-d", "Heart under the whale", "Five faint beats at 56 bpm beneath a call."],
 ["r13-e", "Clicks and squeaks", "Shut, then a loose run of clicks and three squeaks in the biggest space. No moan."],
 ["r13-f", "All of it", "Shut, two faint beats, the call, a few clicks, one squeak at the end."]
]}, open('vars13.json', 'w', encoding='utf-8'), indent=1)
print(V)
