"""Round 14: the suspensor clack (Harkonnen palette). Heavy, spaced-out thunk-ticks over a swelling electromagnetic hum.
Kept playable on laptop and S22: the knock sits 180-320 Hz, the 'sub' is harmonics of 50 Hz."""
import numpy as np, os, json
from scipy.signal import resample_poly
from gen import mix, save, reverb, lp, hp, bp, SR
D = os.path.dirname(os.path.abspath(__file__))

def at(x, sec, n):
    out = np.zeros(n); s = int(sec * SR); x = x[:max(0, n - s)]; out[s:s + len(x)] = x; return out
def envx(n, tau): return np.exp(-np.arange(n) / (tau * SR))

def clack(rng, knock_g=1.0, contact_g=0.7, ring_g=0.18, ring_tau=0.09, wet_g=0.0, down=(5, 3)):
    """one engagement, built bright then pitched down (sample-rate style, so the transient smears)"""
    n = int(0.35 * SR); tt = np.arange(n) / SR
    # 1 · low knock, 20-40 ms: a short sine burst with a pitch drop, 300 -> 180 Hz
    f = 300 * (180 / 300) ** np.clip(tt / 0.03, 0, 1)
    knock = np.sin(2 * np.pi * np.cumsum(f) / SR) * envx(n, rng.uniform(0.012, 0.02)) * knock_g
    # 2 · contact: 3 ms noise snap, 2-5 kHz before the pitch-down
    contact = bp(rng.standard_normal(n) * envx(n, rng.uniform(0.0015, 0.003)), 2000, 5000, 2) * contact_g
    # 3 · damped metallic ring, inharmonic partials around 700-1300 Hz before pitch-down, -15 dB
    partials = [rng.uniform(680, 760), rng.uniform(980, 1060), rng.uniform(1250, 1380)]
    ring = sum(np.sin(2 * np.pi * p * tt + rng.uniform(0, 6.28)) * envx(n, ring_tau * rng.uniform(0.8, 1.2)) / (i + 1) for i, p in enumerate(partials)) * ring_g
    ring = np.concatenate([np.zeros(int(0.004 * SR)), ring])[:n]
    # 4 · optional wet, fleshy layer: a soft low squelch, lowpassed noise with a slow envelope, just after the knock
    wet = lp(rng.standard_normal(n), 500, 4) * envx(n, 0.05) * (1 - envx(n, 0.006)) * wet_g
    x = knock + contact + ring + wet
    x[:12] *= np.linspace(0, 1, 12)
    return resample_poly(x, *down)                  # pitch down: (5,3) is about -9 semitones, (2,1) an octave

def drone(dur, f_saw=140, detune=1.5, saw_g=0.12, sub_g=0.25, lift_db=3.0, rise=0.3, fall=0.6, lp_hz=600, noise_g=0.0):
    """the field: 'sub' as harmonics 3-6 of 50 Hz, plus two detuned saws filtered dark, swelling by lift_db"""
    n = int(dur * SR); tt = np.arange(n) / SR
    sub = sum(np.sin(2 * np.pi * 50 * k * tt) / k for k in range(3, 7)); sub = sub / np.abs(sub).max() * sub_g
    ph1 = 2 * np.pi * f_saw * tt; ph2 = 2 * np.pi * (f_saw + detune) * tt
    saw = (2 * ((ph1 / 6.2832) % 1) - 1) + (2 * ((ph2 / 6.2832) % 1) - 1)
    saw = lp(saw, lp_hz, 2) * saw_g
    nz = bp(np.random.default_rng(4).standard_normal(n), 150, 400, 2) * noise_g
    lift = 10 ** (lift_db / 20 * (tt / dur))
    env = np.ones(n); r = int(rise * SR); fl = int(fall * SR)
    env[:r] = np.linspace(0, 1, r) ** 2; env[-fl:] = np.linspace(1, 0, fl) ** 1.5
    return (sub + saw + nz) * lift * env

def room(x, rt=0.9, wet=0.35, dark=1200):
    return reverb(x, rt=rt, dark=dark, pre=0.015, wet=wet)

def scene(seed, times, dur, clack_kw={}, drone_kw={}, room_kw={}, vel_db=3, drone_on=True, name=''):
    rng = np.random.default_rng(seed)
    n = int(dur * SR); x = np.zeros(n)
    for t in times:
        c = clack(rng, **clack_kw) * 10 ** (rng.uniform(-vel_db, vel_db) / 20)
        x += at(c, t, n)
    out = room(x, **room_kw)
    if drone_on: out = mix(out, drone(dur, **drone_kw) * 0.9)
    return save(name, out)

V = {}
V['a'] = scene(1, [0.3, 0.95, 1.6, 2.5, 3.1, 4.4], 5.5, name='r14-a')
V['b'] = scene(2, [0.3, 1.5, 2.4, 3.9], 5.5, clack_kw=dict(knock_g=1.4, contact_g=0.5, ring_tau=0.12, down=(2, 1)), drone_kw=dict(f_saw=110, lp_hz=450, sub_g=0.3), name='r14-b')
V['c'] = scene(3, [0.3, 0.9, 1.7, 2.2, 3.2, 3.8, 4.6], 5.8, clack_kw=dict(ring_g=0.3, ring_tau=0.15, wet_g=0.5), drone_kw=dict(detune=4, saw_g=0.16, noise_g=0.05), room_kw=dict(rt=1.2, dark=900), name='r14-c')
V['d'] = scene(4, [0.4, 1.9, 3.4], 5.5, drone_kw=dict(saw_g=0.16, sub_g=0.3, lift_db=4), name='r14-d')
V['e'] = scene(5, [0.3, 1.3, 2.1, 2.7, 3.15, 3.5, 3.78], 5.5, drone_kw=dict(lift_db=7, fall=0.3), name='r14-e')
V['f'] = scene(6, [0.3, 0.95, 1.6, 2.5, 3.1, 4.4], 5.5, drone_on=False, room_kw=dict(rt=1.1, wet=0.4), name='r14-f')
json.dump({"title": "Suspensor Clacks", "h1": "suspensor clacks · six variations", "out": "click-clusters-14.html", "vars": [
 ["r14-a", "As written", "Six clacks 300-1300 ms apart, each a knock + contact + damped ring, pitched down about nine semitones. A dark medium room. Under it the field: a 50 Hz harmonic stack and two detuned saws, lifting 3 dB."],
 ["r14-b", "Heavier, slower", "Four clacks, an octave down, more knock, longer ring. Drone lower and darker."],
 ["r14-c", "Dirty, wet", "Seven clacks with a louder, longer metallic ring and a soft fleshy squelch under each. Saws detuned wider, a little grit in the field. Bigger room."],
 ["r14-d", "Sparse, field first", "Three clacks far apart, the hum doing most of the work, lifting 4 dB."],
 ["r14-e", "Lift-off", "Clacks slowly closing up, as the units step faster; the field lifts 7 dB and cuts."],
 ["r14-f", "Clacks only", "No field: six clacks in the room. The mechanism alone."]
]}, open('vars14.json', 'w', encoding='utf-8'), indent=1)
print(V)
