# Sounds

Five recorded clicks live inside the pages as base64 WAV (8 kHz, mono, 16-bit), so each page stays one file that works offline.

| File | Used for | Where it came from |
| --- | --- | --- |
| `switch.wav` (0.18 s, 3 KB) | the sound switch, on and off, both pages | clicks 5+6 of `source/voice-030.m4a`, hum removed, slowed 4x, nothing above 400 Hz, first 150 ms under 180 Hz |
| `corner1.wav` … `corner4.wav` (0.36-0.44 s, 6-7 KB each) | `index.html`, one per corner: inhale starts, top, exhale starts, bottom | the same pair slowed 8.0x, 7.3x, 8.6x, 9.3x (about a semitone apart), nothing above 350 Hz, the first 300 ms under 180 Hz, the first edge faded in over 30 ms (`phone.py`, less clank on the S22), then everything under 180 Hz cut, 6th order (`hp4.py`: at full level it only overdrove the phone speaker, heard as distortion at Start) |

Both are heard on laptop speakers and a Galaxy S22, so nothing in them relies on frequencies under about 180 Hz.

## How they were made (`recipe/`)

Python with numpy + scipy (`python -m pip install numpy scipy`); ffmpeg decodes the m4a.

1. `ffmpeg -i source/voice-030.m4a -ac 1 -ar 44100 in.wav`
2. `clean3.py` finds the clicks (2 ms frames, a frame 2.2x the 40 ms before it), keeps each from 6 ms before its edge until it has died back, and subtracts the hum (median spectrum of everything between the clicks, 2.5x, floor 4 %). Writes `x-k1..9.wav`.
3. `pair56.py` lays clicks 5 and 6 40 ms apart as recorded (`p-56.wav`) and slows the pair with `resample_poly` (pitch drops with it, like a slowed recording).
4. `pair56b.py` cuts the highs and holds the first part of the sound even lower so the start has no bright edge. Writes `q-4b.wav` (the switch) and `q-8b.wav`.
5. `pair56c.py` makes four siblings of `q-8b`: set A at 8.0x/7.3x/8.6x/9.3x (shipped), set B at 8x with the top edge at 420/500/580/680 Hz (gallery only).
6. `phone.py` rounds the corner clicks for the phone (to 350 Hz, 30 ms fade-in) and renders tone + click options as a gallery.
7. `space.py` slows the pair 12-20x and puts it in a dark room (decaying noise impulse, band-limited 170-450 Hz); was on the page for an hour on 5 Nov; Vlad: no, the clicks as they were.
8. `embed.py` / `embed4.py` trim, resample to 8 kHz and base64-encode; `apply_clicks.py` / `apply4.py` put them into the pages.

In `index.html` the tone ducks to 30 % while any click sounds (`duck()`): tone 0.72 + click 0.71 would clip at every corner, which was heard as a buzz.

The earlier rounds are here too, for more variations later:

| Script | What it makes |
| --- | --- |
| `gen.py` | synthetic click clusters with a servo tail, from a written description (snap + body + thump, accelerating hits, saw sweep, dark reverb) |
| `gen2.py` – `gen5.py` | slower, deeper, fewer clicks; single clicks; combined; overlapping |
| `gen6.py` – `gen9.py` | one click made longer, slow motion, nuanced layers (edge, two stages, after-rattle, weight, air) |
| `gen10.py` – `gen12.py` | closed-in versions: no highs, small dead room; then re-tuned for small speakers (weight as harmonics of 50 Hz) |
| `gen13.py` | heart (echocardiogram lub-dub with Doppler swish) and whale (low glides, clicks, squeaks) under water |
| `gen14.py` | the suspensor clack: knock + contact + damped metallic ring pitched down, over a swelling field |
| `build.py vars-N.json` | a one-page gallery with a play square per sound (used as artifacts for choosing) |

Vlad chose by ear each round; the keepers are the two files above.
