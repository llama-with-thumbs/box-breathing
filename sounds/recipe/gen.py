"""Mechanical click cluster + servo tail. Six variations, written as 44.1 kHz 16-bit mono WAVs."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
import os, json

SR = 44100
OUT = os.path.dirname(os.path.abspath(__file__))

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x)

def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, btype='low', fs=SR, output='sos'), x)

def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, btype='high', fs=SR, output='sos'), x)

def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))

def click(rng, snap=True, body=True, thump_db=-12, pitch=0.0, size=1.0):
    """One hit: snap (1-3 ms noise, 3-6 kHz), body (settle, 0.8-2 kHz, a bit longer), thump (60-120 Hz)."""
    n = int(0.06 * SR)
    out = np.zeros(n)
    k = 2 ** (pitch / 12)
    if snap:
        d = rng.uniform(0.001, 0.003)
        s = rng.standard_normal(n) * env_exp(n, d)
        s = bp(s, 3000 * k, min(6500 * k, 20000), 2)
        out += s * 1.0
    if body:
        d = rng.uniform(0.004, 0.009) * size
        b = rng.standard_normal(n) * env_exp(n, d)
        b = bp(b, 700 * k, 2200 * k, 2)
        delay = int(rng.uniform(0.002, 0.003) * SR)        # micro-delay so layers never phase-lock
        out[delay:] += b[:n - delay] * 0.8
    if thump_db is not None:
        f = rng.uniform(60, 120)
        t = np.arange(n) / SR
        th = np.sin(2 * np.pi * f * t) * env_exp(n, 0.012 * size)
        out += th * 10 ** (thump_db / 20) * 2.5
    # hard attack: nothing before sample 0; a 0.2 ms fade so there is no DC step
    out[:9] *= np.linspace(0, 1, 9)
    return out

def cluster(rng, hits, span, accel=1.0, jitter=0.3, size=1.0, thump_db=-12, groups=1, gap=0.15):
    """hits over span seconds. accel>1: inter-onset times shrink toward the end. Returns onset times."""
    per_group = max(1, hits // groups)
    times = []
    t0 = 0.0
    for g in range(groups):
        w = np.array([accel ** (-i / max(1, per_group - 1)) for i in range(per_group)])
        w = w / w.sum() * span / groups
        w = w * rng.uniform(1 - jitter, 1 + jitter, per_group)
        on = t0 + np.concatenate([[0], np.cumsum(w[:-1])])
        times.extend(on.tolist())
        t0 = on[-1] + w[-1] + gap
    return np.array(times)

def render_clicks(rng, times, size=1.0, thump_db=-12, vel_db=4, pitch_st=3, dur=None):
    end = times.max() + 0.2
    n = int((dur or end) * SR)
    out = np.zeros(n + int(0.1 * SR))
    for i, t in enumerate(times):
        layers = rng.random()
        c = click(rng, snap=layers > 0.15, body=layers < 0.9, thump_db=thump_db,
                  pitch=rng.uniform(-pitch_st, pitch_st), size=size)
        c *= 10 ** (rng.uniform(-vel_db, vel_db) / 20)
        s = int(t * SR)
        out[s:s + len(c)] += c
    return out[:n]

def servo(f0, f1, dur, kind='saw', lp_hz=2500, hum_db=None, rise=0.15, fall=0.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    # frequency glides on a log curve
    f = f0 * (f1 / f0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    if kind == 'saw':
        x = 2 * ((ph / (2 * np.pi)) % 1) - 1
        x = lp(x, lp_hz, 2)
    else:  # noise swell, bandpassed and swept
        x = np.random.default_rng(7).standard_normal(n)
        x = hp(lp(x, lp_hz), 300)
        # resonant sweep by modulating with a sine at f
        x = x * (0.5 + 0.5 * np.sin(ph))
    env = np.ones(n)
    r = int(rise * SR); fl = int(fall * SR)
    env[:r] = np.linspace(0, 1, r) ** 2
    env[-fl:] = np.linspace(1, 0, fl) ** 1.5
    x = x * env
    if hum_db is not None:
        hum = np.sin(2 * np.pi * 60 * t) + 0.4 * np.sin(2 * np.pi * 120 * t)
        x += hum * env * 10 ** (hum_db / 20)
    return x

def reverb(x, rt=2.2, dark=1800, pre=0.012, wet=0.6):
    n = int(rt * SR)
    ir = np.random.default_rng(3).standard_normal(n) * np.exp(-6.9 * np.arange(n) / n)
    ir = lp(ir, dark, 1)
    ir /= np.sqrt((ir ** 2).sum())
    w = fftconvolve(x, ir)[:len(x) + n]
    out = np.zeros(len(w) + int(pre * SR))
    out[:len(x)] += x * (1 - wet)
    out[int(pre * SR):int(pre * SR) + len(w)] += w * wet * 0.9
    return out

def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[:len(p)] += p
    return out

def norm(x, peak=0.89):
    return x / (np.abs(x).max() + 1e-9) * peak

def save(name, x):
    x = norm(x)
    # 10 ms fade at the very end so nothing clicks on stop
    f = int(0.01 * SR); x[-f:] *= np.linspace(1, 0, f)
    wavfile.write(os.path.join(OUT, name + '.wav'), SR, (x * 32767).astype(np.int16))
    return len(x) / SR

variants = {}

# 1 · as described: 14 hits accelerating over 600 ms, two layers, servo saw 200 → 1200 Hz over 1.5 s into a dark room
rng = np.random.default_rng(1)
t = cluster(rng, 14, 0.6, accel=2.2)
cl = render_clicks(rng, t)
sv = servo(200, 1200, 1.6, 'saw', lp_hz=2200, hum_db=-30)
sv_start = int((t.max() + 0.05) * SR)
tail = np.concatenate([np.zeros(sv_start), sv]) * 0.35
variants['1-as-written'] = save('1-as-written', mix(cl, reverb(tail)))

# 2 · heavier relay: 8 hits, slower, more thump, bigger body, slower servo
rng = np.random.default_rng(2)
t = cluster(rng, 8, 0.75, accel=1.6)
cl = render_clicks(rng, t, size=1.6, thump_db=-6)
sv = servo(140, 900, 2.0, 'saw', lp_hz=1600, hum_db=-28)
tail = np.concatenate([np.zeros(int((t.max() + 0.08) * SR)), sv]) * 0.3
variants['2-heavy-relay'] = save('2-heavy-relay', mix(cl, reverb(tail, rt=2.8, dark=1400)))

# 3 · self-test: 20 light hits in 450 ms, higher snap, short bright servo
rng = np.random.default_rng(3)
t = cluster(rng, 20, 0.45, accel=3.0, jitter=0.35)
cl = render_clicks(rng, t, size=0.7, thump_db=-18, pitch_st=4)
sv = servo(400, 1800, 0.9, 'saw', lp_hz=3200)
tail = np.concatenate([np.zeros(int((t.max() + 0.03) * SR)), sv]) * 0.3
variants['3-self-test'] = save('3-self-test', mix(cl, reverb(tail, rt=1.6)))

# 4 · ratchet winding down: hits slow instead of speed up; servo falls 1200 → 200
rng = np.random.default_rng(4)
t = cluster(rng, 14, 0.7, accel=1 / 2.4)
cl = render_clicks(rng, t)
sv = servo(1200, 220, 1.4, 'saw', lp_hz=2200, hum_db=-30, rise=0.05, fall=0.6)
tail = np.concatenate([np.zeros(int((t.max() + 0.05) * SR)), sv]) * 0.33
variants['4-winding-down'] = save('4-winding-down', mix(cl, reverb(tail)))

# 5 · clicks only: cluster, then one loud latch; hum underneath; no servo
rng = np.random.default_rng(5)
t = cluster(rng, 12, 0.55, accel=2.0)
cl = render_clicks(rng, t, thump_db=-14)
latch = click(rng, snap=True, body=True, thump_db=-4, size=2.2) * 1.8
s = int((t.max() + 0.18) * SR)
lt = np.zeros(s + len(latch)); lt[s:] = latch
n = len(lt) + int(0.6 * SR)
hum = (np.sin(2 * np.pi * 60 * np.arange(n) / SR) + 0.4 * np.sin(2 * np.pi * 120 * np.arange(n) / SR)) * 10 ** (-32 / 20)
hum[-int(0.5 * SR):] *= np.linspace(1, 0, int(0.5 * SR))
variants['5-clicks-and-latch'] = save('5-clicks-and-latch', mix(cl, reverb(lt, rt=1.8, wet=0.35), hum))

# 6 · power-up: the servo swell comes first (noise, rising), the clicks fire at the end as the self-test
rng = np.random.default_rng(6)
sv = servo(200, 1200, 1.4, 'noise', lp_hz=2600, hum_db=-30, rise=0.5, fall=0.25) * 0.4
t = cluster(rng, 16, 0.5, accel=2.5) + 1.1
cl = render_clicks(rng, t, dur=t.max() + 0.3)
variants['6-power-up'] = save('6-power-up', mix(reverb(sv), cl))

# 7 · two bursts, shutter-like: burst, 150 ms, burst, then the servo
rng = np.random.default_rng(7)
t = cluster(rng, 12, 0.5, accel=1.8, groups=2, gap=0.15)
cl = render_clicks(rng, t)
sv = servo(250, 1100, 1.3, 'saw', lp_hz=2200, hum_db=-30)
tail = np.concatenate([np.zeros(int((t.max() + 0.05) * SR)), sv]) * 0.33
variants['7-two-bursts'] = save('7-two-bursts', mix(cl, reverb(tail)))

json.dump(variants, open(os.path.join(OUT, 'durations.json'), 'w'), indent=1)
print(json.dumps(variants, indent=1))
