# Box Breathing — context for Claude

Small single-page instruments that help Vlad come back to himself, recover
agency, and land in the present moment. `index.html` (3-minute 4-4-4-4 box
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
- 11 rounds × 16 s = 2:56, labelled "3 minutes"; change `ROUNDS`/`PHASE` only.
- Timing from `requestAnimationFrame` deltas; hidden tab pauses; reduced-motion and dark mode respected.
- No streaks, scores, or notifications: the user runs the instrument, never the reverse.
- Bauhaus: square, one accent (red dot), system font, no ornament.

- `unclench.html`: 6 steps with suggested seconds (`STEPS`), total 120 s. The square
  grows from `SIZE0` to 1 over the step's time, then waits; only a tap advances.
  Sound is Web Audio (220 Hz ping when a step's time is up; 330→165 Hz slide on
  each exhale), on by default, mute remembered in `localStorage` `unclench.sound`.
  No text input: Vlad asked for nothing to type.

## State as of 3 Nov 2026

`index.html` and `unclench.html` written and checked in Chrome (steps, word box,
breath text, finish, no console errors). Vlad chose visual B (growing square),
sound on with mute; the one-word box was tried and removed. Git initialised, nothing committed,
no remote. Local test server: `python -m http.server 8771` (8765 is taken by
the materials project).

## Next step

Vlad tries `unclench.html` on his phone and says what to change (text, timing,
sound level). Then commit, push, enable Pages (README has the steps).
