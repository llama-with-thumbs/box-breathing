"""Exercise sounds from a real synthesizer: DawDreamer (pip install dawdreamer) running Faust physical models
(struck bars, modal bowls and bells, a drum skin, a plucked string, rubbed glass, breath through a tube) and the Zita
reverb. Rendered offline to wav/mp3, by the twelve sound rules: soft onsets, nothing under 180 Hz, octave spacing low down."""
import json, os, subprocess, sys, numpy as np, dawdreamer as daw
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 44100
FF = r"C:\Users\laman\Downloads\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
HEAD = 'import("stdfaust.lib");\ngate = button("gate");\nlvl = hslider("lvl", 0, 0, 1, 0.0001);\nhit = gate : ba.impulsify;\n'
ROOM = "room(w, t) = _ <: (_ * (1 - w)), ((_ <: _,_ : re.zita_rev1_stereo(30, 200, 5000, t, t * 0.7, 44100) :> _ * 0.5) * w) :> _;\n"
def modes(f, ratios, t60s, gains):
    n = len(ratios)
    return "par(i, %d, pm.modeFilter(%g * ba.take(i + 1, (%s)), ba.take(i + 1, (%s)), ba.take(i + 1, (%s))))" % (
        n, f, ', '.join('%g' % r for r in ratios), ', '.join('%g' % t for t in t60s), ', '.join('%g' % g for g in gains))
def render(body, dur, hits=(0.1,), lvl=None):
    eng = daw.RenderEngine(SR, 256); f = eng.make_faust_processor('f'); f.set_dsp_string(HEAD + ROOM + body)
    if not f.compile(): raise SystemExit('faust did not compile:\n' + body)
    n = int(dur * SR); g = np.zeros(n, dtype=np.float32)
    for h in hits: g[int(h * SR):int(h * SR) + 2000] = 1
    if len(hits): f.set_automation('/dawdreamer/gate', g)
    if lvl is not None: f.set_automation('/dawdreamer/lvl', lvl(np.arange(n) / SR).astype(np.float32))
    eng.load_graph([(f, [])]); eng.render(dur)
    x = eng.get_audio().mean(axis=0).astype(np.float64); print('  raw peak %.3f, rms last second %.4f' % (np.abs(x).max(), np.sqrt((x[-SR:] ** 2).mean()))); return x
def save(key, x, peak=0.7, tail=0.4):
    x = sosfilt(butter(4, 180, 'high', fs=SR, output='sos'), x)
    n = int(tail * SR); x[-n:] *= np.linspace(1, 0, n) ** 2
    x = x / (np.abs(x).max() + 1e-9) * peak
    wavfile.write(key + '.wav', SR, (x * 32767).astype(np.int16))
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', key + '.wav', '-ac', '1', '-b:a', '96k', key + '.mp3'], check=True)
    print(key, '%.1f s' % (len(x) / SR))
smooth = lambda u: u * u * (3 - 2 * u)
def breath(t, period=16):                       # the box: up over 4, hold 4, down over 4, hold 4
    p = (t % period) / period * 4; ph = np.floor(p).astype(int); u = smooth(p - ph)
    return np.where(ph == 0, u, np.where(ph == 1, 1.0, np.where(ph == 2, 1 - u, 0.0)))

S = []
def add(key, name, note, x): save(key, x); S.append([key, name, note, key.split('-')[1].upper()])

# --- struck things: candidates for corner and step cues ---
add('sy-1', 'Wooden bar', 'A marimba bar at E4, struck softly near the middle. One tap, then four a semitone apart as four corners would be.',
    render("process = par(i, 5, pm.marimba(ba.take(i + 1, (330, 330, 349, 370, 392)), 0.4, 2500, 0.35, 0.8, button(\"gate\") * (hslider(\"lvl\", 0, 0, 1, 0.0001) > (i - 0.5) / 4) * (hslider(\"lvl\", 0, 0, 1, 0.0001) < (i + 0.5) / 4))) :> room(0.12, 1.2);",
           7.5, hits=(0.1, 2.5, 3.5, 4.5, 5.5), lvl=lambda t: np.select([t < 2, t < 3, t < 4, t < 5], [0.0, 0.25, 0.5, 0.75], 1.0)))
add('sy-2', 'Singing bowl', 'A metal bowl: five partials that are not harmonics, two of them paired a hertz apart so it slowly turns. Soft mallet, six seconds of ring.',
    render("process = hit : fi.lowpass(2, 900) <: " + modes(330, [1, 1.003, 2.71, 2.72, 5.15, 8.2], [7, 7, 5, 5, 3, 1.5], [1, 0.8, 0.5, 0.4, 0.2, 0.08]) + " :> _ * 0.3 : room(0.25, 3);", 8))
add('sy-3', 'Small chime', 'A tube chime an octave up (E5): clean, short, three seconds.',
    render("process = hit : fi.lowpass(2, 2500) <: " + modes(660, [1, 2.76, 5.4, 8.9], [3, 2, 1, 0.5], [1, 0.4, 0.15, 0.05]) + " :> _ * 0.3 : room(0.2, 2);", 4))
add('sy-4', 'Hand drum', 'A drum skin tapped with a fingertip, tuned to C4. No ring, just the body.',
    render("process = pm.djembe(262, 0.3, 0.25, 0.8, gate) : room(0.1, 0.8);", 2, hits=(0.1, 1.0)))
add('sy-5', 'Plucked string', 'One nylon-like string at E4, plucked softly, damped. A warmer kind of tap.',
    render("process = hit : fi.lowpass(2, 1500) * 0.6 : pm.ks(pm.f2l(330), 0.3) : room(0.15, 1.5);", 3.5, hits=(0.1, 1.8)))
add('sy-6', 'Clay pot', 'A hollow clay tap: three low partials that die in a fifth of a second. Closest in spirit to the recorded corner click.',
    render("process = hit : fi.lowpass(2, 1200) <: " + modes(280, [1, 2.3, 3.9], [0.25, 0.15, 0.08], [1, 0.5, 0.2]) + " :> _ * 0.4 : room(0.1, 0.6);", 2.5, hits=(0.1, 1.2)))
# --- sustained things: candidates for the hum, and the breath ---
add('sy-7', 'Rubbed glass, breathing', 'The bowl again, but rubbed, not struck: it sings as long as it is fed. Fed harder on the inhale, eased on the exhale. Twenty seconds, one and a quarter boxes.',
    render("process = no.pink_noise * (0.004 + 0.02 * (lvl : si.smooth(ba.tau2pole(0.6)))) <: " + modes(220, [1, 1.002, 2, 2.004, 4.01], [3, 3, 2.5, 2.5, 1.5], [1, 0.9, 0.5, 0.4, 0.12]) + " :> _ * 0.2 : room(0.35, 4);",
           20, hits=(), lvl=lambda t: breath(t)))
add('sy-8', 'Breath in a tube', 'Air through a resonant tube: it opens and brightens over four seconds, holds, closes over four. An inhale and an exhale you can hear, without a note.',
    render("process = no.noise * (lvl : si.smooth(ba.tau2pole(0.25))) * 0.25 <: fi.resonbp(380 + 260 * (lvl : si.smooth(ba.tau2pole(0.4))), 3, 1), fi.resonbp(760 + 520 * (lvl : si.smooth(ba.tau2pole(0.4))), 4, 0.4) :> room(0.2, 1.5);",
           17, hits=(), lvl=lambda t: breath(t)))
add('sy-9', 'Organ pipe hum', 'Three sine pipes an octave apart (A3, A4, A5) with a slow chorus, in a three-second hall. The old breath tone, built properly.',
    render("f = 220 * pow(2, (lvl : si.smooth(ba.tau2pole(0.8))) / 12);\nprocess = (os.osc(f) + os.osc(f * 1.0015) * 0.7 + os.osc(f * 2) * 0.4 + os.osc(f * 2.003) * 0.25 + os.osc(f * 4) * 0.08) * 0.12 * (0.55 + 0.45 * (lvl : si.smooth(ba.tau2pole(0.8)))) : room(0.4, 3);",
           20, hits=(), lvl=lambda t: breath(t)))
json.dump({"title": "Synth Sounds", "h1": "nine sounds from the new synthesizer",
           "lead": "Physical models (bars, bowls, a drum skin, a string, rubbed glass, air in a tube) with a real reverb. Nothing here is on the pages yet. Listen on the phone speaker.",
           "out": "synth.html", "vars": S}, open('vars-sy.json', 'w', encoding='utf-8'), indent=1)
