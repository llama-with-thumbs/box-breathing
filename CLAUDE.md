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
  width-stable), silent on press, one shared `localStorage` key `instruments.sound`.
  `index.html` also plays a low tone (220 Hz + its octave at 0.4, not a fifth: a fifth buzzes on a phone speaker) that rises one semitone on inhale. Hue `--h` drifts on both pages.
- Cross link: one grey word under the hint on each page (`.x`), chosen from six mocks
  (gallery artifact https://claude.ai/artifact/URBYeBMrWPFSUtqTjZtvZk).
- No clicks. Recorded clicks (switch press, each corner) were in the pages for a day on 5 Nov; on the S22
  they read as buzz and distortion, and Vlad asked for them out. The tone (220 Hz + octave) and Unclench's
  ping/slide stay. The recipe for the clicks is kept in `sounds/` for later.

## State as of 4 Nov 2026

Live at https://llama-with-thumbs.github.io/box-breathing/ and /unclench.html: cross links, recorded
clicks (sounds/), then the clicks taken out again (5 Nov). Gallery of corner siblings
(set A shipped, set B brightness variants): https://claude.ai/artifact/ULgCLzEArHa5uBv1Eev4dc. Vlad confirmed the wake lock on his Android. Sound switch #6, thump and breath
tone verified in Chrome on the live URLs. Local test server, if needed: `python -m http.server 8771`
(8765 is taken by the materials project); none running now.

## Next step

Vlad checks the tone on the S22 (now 220 + octave; options T2-T6 at https://claude.ai/artifact/Ju8UShdZLE68CDLzvRM213). `unclench.html` still has the red square and
outlined frame; the Turrell/Waking Up pass for it is offered, not decided.
