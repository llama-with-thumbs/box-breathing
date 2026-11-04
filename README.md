# Box Breathing

Three minutes of box breathing on one page. Inhale 4 · Hold 4 · Exhale 4 · Hold 4,
eleven rounds (2:56). A dot walks the four sides of a square, one side per phase.

No build, no libraries, one file per instrument:

| File | Instrument | Length |
| --- | --- | --- |
| `index.html` | Box breathing, 4-4-4-4, a dot walking a square | 2:56 |
| `unclench.html` | Unclench: feet, jaw, shoulders, hands, three exhales, one thing you see. A tight red square grows one size per step. You move on by tap or space; nothing moves you. Soft tones made by the page (mute button, remembered on the device). | ~2:00 |

## Use

Open `index.html`, or the GitHub Pages URL. Start with the button, the square, or
the space bar. Space or a click pauses. Switching tabs pauses too.

## Host on GitHub Pages

1. Push this folder to a repository (branch `main`).
2. Repository → Settings → Pages → Source: *Deploy from a branch*, branch `main`, folder `/ (root)`.
3. The page appears at `https://<user>.github.io/<repo>/` within a minute.

`.nojekyll` is there so Pages serves the folder as-is.

## Change the rhythm

In `index.html`, the three constants at the top of the script:

| Constant | Default | Meaning |
| --- | --- | --- |
| `PHASE` | 4 | seconds per side |
| `ROUNDS` | 11 | rounds in a session |
| `PHASES` | Inhale / Hold / Exhale / Hold | labels, top → right → bottom → left |
