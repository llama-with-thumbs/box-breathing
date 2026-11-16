# Box Breathing — context for Claude

Small single-page instruments that help Vlad come back to himself, recover
agency, and land in the present moment. `index.html` (2-minute 4-4-4-4 box
breathing, a dot walking a square) is the first. Hosted on GitHub Pages.
Rules for Vlad: `~/.claude/CLAUDE.md`. Who you are here: the agent file.

## Session defaults

| Property | Value | How |
| --- | --- | --- |
| Name | `Breathing` | SessionStart hook in `.claude/settings.local.json` |
| Model | newest Fable | `"model": "fable"` |
| Agent | `Rosenberg` | `.claude/agents/Rosenberg.md` — NVC spirit, builds instruments, never diagnoses |
| Color | — | run `/color` by hand after connecting |

`.claude/` is gitignored: the agent and settings stay off GitHub Pages.

## Decisions

- One file per instrument, no build, no libraries, no network, no tracking, no accounts.
- 8 rounds × 16 s = 2:08, labelled "2 minutes"; change `ROUNDS`/`PHASE` only.
- Both pages hold a Screen Wake Lock while running (`keepAwake`/`letSleep`); released on pause/finish/hidden.
- Timing from `requestAnimationFrame` deltas; hidden tab pauses; reduced-motion and dark mode respected.
- No streaks, scores, or notifications: the user runs the instrument, never the reverse.
- Sound is heard on laptop speakers and a Galaxy S22: nothing below ~180 Hz carries. Put weight in
  harmonics (missing fundamental), keep cues 200 Hz-2 kHz, check on a phone speaker, not headphones.
- Bauhaus: square, system font, no ornament. On `index.html` the square is the light
  (Turrell): no frame, brightens on inhale, dims on exhale, hue drifts 215→325→215 over
  the session, white dot walks the edge. Waking Up gave: air, light type, one filled button.

- `unclench.html`: 6 steps with suggested seconds (`STEPS`), total 120 s. The frame is a window onto a room (16 Nov,
  variation 1 of https://claude.ai/artifact/HWx46XJyvrKQG7E4aV8DEc): black walls, the room wider than the window (`MX` 12,
  `MY` 3) so its hairline edges leave through the sides, not the corners; the red back wall comes closer (`room(k)`) and
  the walls take a faint red (`GLOW`) only on the last stretch. The text in the room is pale in both themes. The square
  grows from `SIZE0` to 1 over the step's time; when it is up a ping sounds and the next step
  starts by itself (Vlad, 5 Nov); a tap moves on early.
  Sound is Web Audio (220 Hz ping at each step change; 330→165 Hz slide on
  each exhale), on by default, mute remembered in `localStorage` `unclench.sound`.
  No text input: Vlad asked for nothing to type.
- Sound switch on both pages: a small lit square + "Sound on/off" (word lit by the square,
  width-stable), click on press, one shared `localStorage` key `instruments.sound`.
  `index.html` runs a hum (see Hums). Hue `--h` drifts on both pages.
- Cross link: one grey word under the hint on each page (`.x`), chosen from six mocks
  (gallery artifact https://claude.ai/artifact/URBYeBMrWPFSUtqTjZtvZk).
- Recorded clicks are embedded in the pages as base64 8 kHz WAV (`sounds/`): `switch.wav` on every press of
  the sound switch (both pages, ignores the setting); `corner1-4.wav` on `index.html` at each corner except
  the first at Start (`lastSide`; the same click at four speeds, 180-350 Hz, edge faded in for the S22).
  Recipe: `sounds/README.md`, `sounds/recipe/`. On `unclench.html` the step cue is the same corner click (`STEP_WAV`).
- Hums, made in Web Audio, level 0.22, duck to 30 % under any click (rule 12), nothing under 180 Hz:
  `index.html` = gallery H6 + H1 (330 Hz, octave a quarter-hertz off, third harmonic, air 300-1500 Hz swelling once
  per box; leans up to 25 cents as the dot nears a corner, `humFollow`). `unclench.html` = gallery U4 (C4 + C6 beating,
  air 300-700 Hz, 2 s room; breathes 40 cents up over 4 s, down over 6 s, `humBreathe`). The exhale slide stays as it was.
  The old 220 Hz breath tone (a fifth) buzzed on the phone and is gone. Gallery: https://claude.ai/artifact/3jC8SKcGoHdXojwGqZamNs

- Switching pages (10 Nov): every page ends with the same carousel `nav.nav`: left arrow, the page's name (lit, fixed width),
  right arrow. Order Box, Unclench, Hexagon, Sit, wrapping both ways. Each has a contour pictogram of its shape (16 Nov):
  neighbour's shape, arrow, current shape + name, arrow, neighbour's shape. Pictograms appear only here. This replaces the single grey cross link.
- `hexagon.html` (10 Nov): a hexagon of light, the dot walks one side every 4 s, 5 laps = 2:00. A tone (sine + octave +
  second octave, level 0.35) slides into a new note at each corner: A3, B4, G3, C#4, G3, C#4 (`NOTES`, `GLIDE` 0.5 s).
  The light is brighter on higher notes. No corner clicks; the switch clicks. Linked from `index.html`. Built by
  `sounds/recipe/hexagon.py`.
- `sit.html` (16 Nov): spoken guidance for sitting with anxiety, 15 lines in 5 parts (Body, Facts, Mind, Kind, Here),
  2:44. The script is `LINES` ([part, line, seconds]); it follows Jenny Matthews, LMFT, "How to sit with anxiety"
  (stateofmindtherapy.com), reworded. The voice is recorded, not the device's (16 Nov): Kokoro (Apache-2.0), two takes
  of every line embedded as mp3 (about 570 KB): voice 1 = Heart + Nicole blend (gallery 6), voice 2 = Heart (gallery 2),
  both two semitones down, speed 0.75. Each line is spoken phrase by phrase with hand-set silences between
  (`RHYTHM` in the recipe: lists get 0.7-0.9 s between words, paired sentences 0.7-1.3 s, run-on thoughts none). The switch cycles Voice 1, Voice 2, Voice off (`sit.voice`, and the shared
  `instruments.sound`). Each line is also on the shape: a pentagon (16 Nov), one side per part; the dot walks a side while its part is spoken. A resume
  goes back to the start of the line. The aim is to stay with it, not to make it go; the page never promises relief.
  Recipe: `sounds/recipe/sitvoice.py` (needs `pip install kokoro-onnx` and the two model files; changing a line in
  `LINES` means running it again). Voice gallery: https://claude.ai/artifact/JzeNk1z3jpkKqXdDuPXkYd
- Geometry (16 Nov): the square (72vw, 300 px), gap 36, `#btn` 140 px, `#snd` 128 px and a three-line `.hint` are the
  same on all four pages, so nothing moves when switching. Keep them equal on any new page.

## Sound rules (from the 5 Nov research; full page https://claude.ai/artifact/BEDzSjEsEmwnASBvgEMgJY)

1. One sound per meaning, one meaning per sound; never two at once.
2. A cue invites; it never repeats, escalates or speeds up (rate = urgency).
3. Nothing sounds on the person's own tap; cues come from the clock.
4. Onset 30-50 ms, never a hard edge. Decay short (tap) or long (bell), not the onset.
5. Nothing under 180 Hz leaves the page; weight by harmonics; high-pass every cue.
6. Octaves and wide spacing only; no fifths or thirds under 500 Hz (critical band ~100 Hz there).
7. A drone changes slower than you can notice (< 1 semitone/min, beating < 1 Hz) or it is a signal.
8. A drone only if the phone speaker can hold it (>= 300 Hz and rule 6); clicks-only is complete.
9. One family of material per instrument set; cues differ by rhythm and timbre first, pitch by >= 1 semitone.
10. Sound is never the only channel; the page works with the switch off.
11. Decide on the S22, not on headphones; every sound round ends in a gallery heard on the phone.
12. Peak budget is one: sum the peaks of what can sound together; over 1.0, something ducks or goes.

## State as of 4 Nov 2026

Live at https://llama-with-thumbs.github.io/box-breathing/ and /unclench.html: cross links, recorded
clicks (sounds/), then hums by the sound rules on both pages, clicks kept, step cue = corner click (5 Nov). Gallery of corner siblings
(set A shipped, set B brightness variants): https://claude.ai/artifact/ULgCLzEArHa5uBv1Eev4dc. Vlad confirmed the wake lock on his Android. Sound switch #6, thump and breath
tone verified in Chrome on the live URLs. Local test server, if needed: `python -m http.server 8771`
(8765 is taken by the materials project); none running now.

## Next step

16 Nov: `sit.html` is live with the two recorded voices Vlad chose (6 first, 2 second); pacing and wording are still first guesses,
unheard on the S22. The Kokoro model sits in that session's scratchpad and will need downloading again (about 330 MB).

10 Nov: `index.html` has the 220+440 breath tone back (rolled back twice on 6 Nov; hums are off both pages). Vlad is choosing
among breathing hums 5/6/9 (https://claude.ai/artifact/5TYzihGFusRA2t7PjhVGTY) and has not heard `hexagon.html` on the phone yet.
`soundcheck.html` is built but untracked. Older note follows.

Vlad tries both hums on the S22 (level 0.22 is a first guess; may want louder or quieter). `unclench.html` still has the red square and
outlined frame; the Turrell/Waking Up pass for it is offered, not decided.
