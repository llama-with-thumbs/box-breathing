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

- `unclench.html`: 6 steps with suggested seconds (`STEPS`), total 120 s. The square
  grows from `SIZE0` to 1 over the step's time; when it is up a ping sounds and the next step
  starts by itself (Vlad, 5 Nov); a tap moves on early.
  Sound is Web Audio (220 Hz ping at each step change; 330→165 Hz slide on
  each exhale), on by default, mute remembered in `localStorage` `unclench.sound`.
  No text input: Vlad asked for nothing to type.
- Sound switch on both pages: a small lit square + "Sound on/off" (word lit by the square,
  width-stable), thump on press-on, one shared `localStorage` key `instruments.sound`.
  `index.html` also plays a low tone that rises on inhale. Hue `--h` drifts on both pages.
- Cross link: one grey word under the hint on each page (`.x`), chosen from six mocks
  (gallery artifact https://claude.ai/artifact/URBYeBMrWPFSUtqTjZtvZk).
- Two recorded clicks are embedded in the pages as base64 8 kHz WAV (`sounds/`): `switch.wav`
  plays on every press of the sound switch (on and off, both pages, ignores the setting);
  `corner1-4.wav` play on `index.html`, one per corner (the same click at 8.0x/7.3x/8.6x/9.3x slow,
  about a semitone apart; `lastSide`). The tone ducks to 30 % under any click (`duck()`): tone + click
  clipped before, heard as a buzz. The synthetic thump is gone. Recipe: `sounds/README.md`, `sounds/recipe/`.

## State as of 4 Nov 2026

Live at https://llama-with-thumbs.github.io/box-breathing/ and /unclench.html: cross links, recorded
clicks (sounds/), four corner clicks with the tone ducking under them (5 Nov). Gallery of corner siblings
(set A shipped, set B brightness variants): https://claude.ai/artifact/ULgCLzEArHa5uBv1Eev4dc. Vlad confirmed the wake lock on his Android. Sound switch #6, thump and breath
tone verified in Chrome on the live URLs. Local test server, if needed: `python -m http.server 8771`
(8765 is taken by the materials project); none running now.

## Next step

Vlad checks on the S22 whether the buzz is gone (if it is still there and continuous, not at the corners, it is the speaker rattling at 220 Hz: raise the tone an octave). Set B of the corner siblings is an alternative. `unclench.html` still has the red square and
outlined frame; the Turrell/Waking Up pass for it is offered, not decided.
