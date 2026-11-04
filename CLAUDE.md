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
- Bauhaus: square, system font, no ornament. On `index.html` the square is the light
  (Turrell): no frame, brightens on inhale, dims on exhale, hue drifts 215→325→215 over
  the session, white dot walks the edge. Waking Up gave: air, light type, one filled button.

- `unclench.html`: 6 steps with suggested seconds (`STEPS`), total 120 s. The square
  grows from `SIZE0` to 1 over the step's time, then waits; only a tap advances.
  Sound is Web Audio (220 Hz ping when a step's time is up; 330→165 Hz slide on
  each exhale), on by default, mute remembered in `localStorage` `unclench.sound`.
  No text input: Vlad asked for nothing to type.

## State as of 3 Nov 2026

`index.html` and `unclench.html` written and checked in Chrome (steps, word box,
breath text, finish, no console errors). Vlad chose visual B (growing square),
sound on with mute; the one-word box was tried and removed. Pushed to
https://github.com/llama-with-thumbs/box-breathing, Pages enabled (main, root):
https://llama-with-thumbs.github.io/box-breathing/ and /unclench.html. Local test server: `python -m http.server 8771` (8765 is taken by
the materials project).

## Next step

Vlad tries both pages on his phone from the Pages URL and says what to change.
`unclench.html` has not had the Turrell/Waking Up pass yet; ask whether it should.
