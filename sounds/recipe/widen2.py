"""Widen, second picture (20 Nov): two eyes, a face with shoulders, the seated person, the room, the house
(four storeys, constructivist, the person on the second floor), the neighbourhood, the city; then back to the eyes.

Run from the repository root, on the widen.html made by widen.py:  python -X utf8 sounds/recipe/widen2.py
It swaps the drawing, its styles and the walk in place, and can only run once (it asserts on the old text).
Run sounds/recipe/lang.py after it.

The drawing is in metres, y down, the person's floor at y = 0 and the person at x = 0. Everything is one nested
scene; the page only moves and scales it (VIEWS) and fades detail by scale, so there is nothing to keep in step.
"""
import re

P = 'widen.html'
s = open(P, encoding='utf-8').read()
# the language block repeats the page's English; take it out here, lang.py puts it back
s = re.sub(r'  /\* lang:start.*?/\* lang:end \*/\n', '', s, flags=re.S)
s = re.sub(r'<!-- lang:start.*?<!-- lang:end -->\n', '', s, flags=re.S)


def rect(x0, x1, y0, y1): return '<rect x="%g" y="%g" width="%g" height="%g"/>' % (x0, y0, x1 - x0, y1 - y0)
def line(x0, y0, x1, y1): return '<path d="M%g,%g L%g,%g"/>' % (x0, y0, x1, y1)


# ---- the person: seated, seen from the front, 0.88 m tall ----
BODY = ('M-0.03,-0.70 L-0.035,-0.60 Q-0.05,-0.575 -0.16,-0.56 Q-0.25,-0.55 -0.26,-0.46 L-0.285,-0.24 L-0.42,-0.12 Q-0.5,-0.06 -0.46,0 '
        'L0.46,0 Q0.5,-0.06 0.42,-0.12 L0.285,-0.24 L0.26,-0.46 Q0.25,-0.55 0.16,-0.56 Q0.05,-0.575 0.035,-0.60 L0.03,-0.70 Z')
HEAD = '<ellipse cx="0" cy="-0.76" rx="0.085" ry="0.11"/>'
LIMBS = ('<path d="M-0.2,-0.5 L-0.215,-0.27 L-0.33,-0.135"/><path d="M0.2,-0.5 L0.215,-0.27 L0.33,-0.135"/>'
         '<path d="M-0.42,-0.12 Q-0.1,-0.2 0.14,-0.035"/><path d="M0.42,-0.12 Q0.1,-0.2 -0.14,-0.035"/>')
def eye(x, y=-0.765):
    return ('<path d="M%g,%g Q%g,%g %g,%g Q%g,%g %g,%g Z"/>' % (x - 0.015, y, x, y - 0.012, x + 0.015, y, x, y + 0.009, x - 0.015, y)
            + '<circle cx="%g" cy="%g" r="0.0047"/><circle class="ink" cx="%g" cy="%g" r="0.002"/>' % (x, y - 0.0008, x, y - 0.0008)
            + '<path d="M%g,%g Q%g,%g %g,%g"/>' % (x - 0.019, y - 0.013, x, y - 0.023, x + 0.019, y - 0.014))
FACE = (eye(-0.032) + eye(0.032)
        + '<path d="M-0.004,-0.752 Q-0.012,-0.727 -0.009,-0.717 Q0,-0.711 0.009,-0.717"/>'
        + '<path d="M-0.022,-0.692 Q0,-0.686 0.022,-0.692"/>')
YOU = ('<g id="you"><path class="lit" d="%s"/><g id="limbs">%s</g><g class="lit">%s</g>'
       '<g class="mass" id="mass" opacity="0"><path d="%s"/>%s</g><g id="face">%s</g></g>') % (BODY, LIMBS, HEAD, BODY, HEAD, FACE)

# ---- the house: two bays and a stair tower, four storeys of 3.2 m, flat roof. The person's room is the bay at x = 0, second storey ----
FLOORS = [3.2, 0, -3.2, -6.4]                       # the floor of each storey; the ground is at 3.2
BODYR, TOWER = (-2.1, 6.3, -9.6, 3.2), (-4.9, -2.1, -11.2, 3.2)
HOUSE = rect(*BODYR) + rect(*TOWER)
HDET = ''.join(line(-2.1, y, 6.3, y) for y in FLOORS[1:]) + line(2.1, -9.6, 2.1, 3.2)
for cx in (0, 4.2):
    for yb in FLOORS:                               # a ribbon window in every room
        HDET += rect(cx - 1.5, cx + 1.5, yb - 2.3, yb - 1.2) + line(cx - 0.5, yb - 2.3, cx - 0.5, yb - 1.2) + line(cx + 0.5, yb - 2.3, cx + 0.5, yb - 1.2)
HDET += rect(-3.9, -3.1, -10.2, 0.2) + ''.join(line(-3.9, y, -3.1, y) for y in (-8.6, -7.0, -5.4, -3.8, -2.2, -0.6)) + rect(-4.0, -3.0, 1.1, 3.2)
LAMP = line(-1.1, -3.2, -1.1, -2.75) + '<path d="M-1.35,-2.5 L-1.1,-2.75 L-0.85,-2.5 Z"/>'

# ---- the neighbourhood: the houses along the street, and trees ----
NB = [(-52, -40, 12.8), (-37, -20, 9.6), (13, 27, 16), (30.5, 39, 6.4), (42, 54, 19.2)]
NBR = ''.join(rect(a, b, 3.2 - h, 3.2) for a, b, h in NB)
NDET = ''.join(line(a, 3.2 - k * 3.2, b, 3.2 - k * 3.2) for a, b, h in NB for k in range(1, round(h / 3.2)))
for x in (-16.5, -11, 9.6):
    NDET += line(x, 3.2, x, 0.4) + '<circle cx="%g" cy="-0.9" r="1.7"/>' % x
BMASS = rect(*BODYR) + rect(*TOWER) + NBR

# ---- the city: towers either side, taller than anything near ----
CITY = [(58, 74, 45), (77, 92, 90), (95, 118, 60), (121, 133, 140), (136, 160, 75), (163, 176, 110), (180, 205, 50), (208, 222, 85), (226, 250, 40),
        (-76, -58, 55), (-90, -79, 120), (-116, -93, 70), (-131, -119, 160), (-158, -134, 65), (-173, -161, 95), (-204, -177, 45), (-220, -207, 80), (-250, -224, 35)]
FAR = ''.join(rect(a, b, 3.2 - h, 3.2) for a, b, h in CITY)

SVG = ('''<defs><clipPath id="in"><polygon points="50,7 88.17,73 11.83,73"/></clipPath></defs>
      <polygon class="tri" points="50,7 98,90 2,90"/>
      <g clip-path="url(#in)"><g class="scene" id="scene">
        <g class="far">%s</g>
        <g id="bld">%s<g id="ndet">%s</g>%s<g id="hdet">%s</g></g>
        <g class="mass" id="bmass" opacity="0">%s</g>
        <g id="lamp">%s</g>
        %s
      </g></g>
      <path class="ground" d="M11.83,73 L88.17,73"/>
      <circle class="dot"''') % (FAR, NBR, NDET, HOUSE, HDET, BMASS, LAMP, YOU)

CSS = '''  /* one drawing, each thing inside the next: eyes, face, the seated person, the room, the house, the streets, the city.
     Lines the colour of the page against the light; what is too small to draw becomes a solid shape. */
  .scene, .ground { fill: none; stroke: var(--bg); stroke-linejoin: round; stroke-linecap: round; }
  .ground { stroke-width: .7; }
  .lit { fill: hsl(var(--h) 60% calc(var(--l) * 1%)); }      /* the light itself: what stands in front hides what is behind */
  .mass, .ink { fill: var(--bg); stroke: none; }
  .far { fill: var(--bg); fill-opacity: .3; stroke: none; }'''

WALK = '''  // ---- the walk: nine sides. Seven views, each wider than the last; one side to come back; then the eyes again. ----
  const SIDES = ['Eyes', 'Face', 'You', 'Room', 'House', 'Neighbourhood', 'City', 'Back', 'Eyes'];
  const SIDE = 15;                                  // seconds per side
  const LAPS = 3;                                   // nine sides = three times round = 2:15
  const TOTAL = SIDE * SIDES.length, CYCLE = TOTAL / LAPS;
  const TURN = 5;                                   // seconds the picture takes to widen after a corner
  // the seven views. The drawing is in metres: [x at the middle, y on the ground line, how many times bigger]
  const VIEWS = [[0, -0.715, 380], [0, -0.40, 95], [0, 0, 50], [0, 0, 12], [0.7, 3.2, 2.6], [0.7, 3.2, 0.75], [0, 3.2, 0.16]];
  const GX = 50, GY = 73;                           // the middle and the ground line, in the square
  const V = [[50, 7], [98, 90], [2, 90]];           // corners, clockwise from the top
'''

VIEW = '''  // where the picture is: scale and shift. Between two views it only zooms: the scale moves by equal ratios in equal
  // times and the shift follows the scale, so one point of the picture stays still and nothing slides.
  const at = v => ({ s: v[2], x: GX - v[0] * v[2], y: GY - v[1] * v[2] });
  function zoom(a, b, k) {
    const A = at(a), B = at(b), s = A.s * Math.pow(B.s / A.s, k), q = (s - A.s) / (B.s - A.s);
    return { s, x: A.x + (B.x - A.x) * q, y: A.y + (B.y - A.y) * q };
  }
  function view(t) {
    const p = Math.floor(t / SIDE), into = t - p * SIDE, n = VIEWS.length - 1;
    if (t >= TOTAL || p === 0 || p > n + 1) return at(VIEWS[0]);
    if (p === n + 1) return zoom(VIEWS[n], VIEWS[0], ease(into / (still ? 0.001 : SIDE - 2)));   // the way back, one side long
    return zoom(VIEWS[p - 1], VIEWS[p], ease(into / (still ? 0.001 : TURN)));
  }
  const fade = (s, a, b) => ease(Math.log(s / a) / Math.log(b / a));     // 0 at scale a, 1 at scale b
  const S0 = VIEWS[0][2], S1 = VIEWS[VIEWS.length - 1][2];
  function picture(v) {
    const s = v.s, op = (el, x) => el.setAttribute('opacity', x.toFixed(3));
    scene.setAttribute('transform', `translate(${v.x.toFixed(3)} ${v.y.toFixed(3)}) scale(${s.toFixed(5)})`);
    scene.setAttribute('stroke-width', (0.7 / s).toFixed(6));                    // the line keeps its weight at every scale
    bld.setAttribute('stroke-width', (0.7 * (0.5 + 0.5 * fade(s, 0.25, 1.5)) / s).toFixed(6));
    const solid = fade(s, 40, 14);                                               // the person: drawn when near, a solid shape when small
    op(face, fade(s, 22, 45)); op(limbs, 1 - solid); op(mass, solid); op(you, fade(s, 0.45, 1.2));
    op(lamp, fade(s, 3, 6)); op(hdet, fade(s, 0.35, 0.9)); op(ndet, fade(s, 0.3, 0.6));
    op(bmass, 0.55 * fade(s, 0.6, 0.25));                                        // and so do the houses, from far away
    box.style.setProperty('--l', L0 + (L1 - L0) * 0.6 * Math.log(S0 / s) / Math.log(S0 / S1));   // the light opens a little as the view does
  }
'''

RENDER = '''  function render(t) {
    const p = Math.min(SIDES.length - 1, Math.floor(t / SIDE));      // which side of the walk, 0..8
    const c = p % V.length, f = (t - p * SIDE) / SIDE;               // which side of the triangle, and 0..1 along it
    if (p !== lastSide) {
      if (lastSide !== -1) play('corner' + c, 0.8, false);           // a click at each corner, not at Start
      lastSide = p;
    }
    const a = V[c], b = V[(c + 1) % V.length];
    dot.setAttribute('cx', a[0] + (b[0] - a[0]) * f);
    dot.setAttribute('cy', a[1] + (b[1] - a[1]) * f);
    picture(view(t));
'''


def swap(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:70])
    s = s.replace(old, new)


def cut(start, end, new):                            # replace from start up to (not including) end
    global s
    i = s.index(start); j = s.index(end, i)
    assert s.count(start) == 1, start[:60]
    s = s[:i] + new + s[j:]


cut('  /* three silhouettes against the light', '  .label {', CSS + '\n')
cut('<defs><clipPath id="in">', ' id="dot"', SVG)
cut('  // ---- the three sides', '\n  const $ = id', WALK.rstrip('\n'))
swap("scene = $('scene'), houseEl = $('house'), cityEl = $('city');",
     "scene = $('scene');\n  const [bld, you, face, limbs, mass, lamp, hdet, ndet, bmass] = ['bld', 'you', 'face', 'limbs', 'mass', 'lamp', 'hdet', 'ndet', 'bmass'].map($);")
cut('  // how wide the picture is', '  function render(t) {', VIEW + '\n')
cut('  function render(t) {', "    root.style.setProperty('--h'", RENDER)
swap('if (elapsed >= TOTAL + HOME) { finish(); return; }', 'if (elapsed >= TOTAL) { finish(); return; }')
swap('if (elapsed >= TOTAL + HOME) { elapsed = 0; lastSide = -1; }', 'if (elapsed >= TOTAL) { elapsed = 0; lastSide = -1; }')
swap('elapsed = TOTAL + HOME; lastSide = -1;', 'elapsed = TOTAL; lastSide = -1;')
swap("picture(0); root.style.setProperty('--h', 215);\n    phaseEl.textContent = 'You';", "picture(at(VIEWS[0])); root.style.setProperty('--h', 215);\n    phaseEl.textContent = 'Done';")
swap('  picture(0);\n})();', '  picture(at(VIEWS[0]));\n})();')
swap('You, the house you are in, the city around it, then you again. Fifteen seconds a side. Let your attention widen with the picture.',
     'From your eyes out to the city, then back. Fifteen seconds a side. Let your attention widen with the picture.')
swap('A triangle of light. Inside it a seated figure, then the house around the figure, then the city around the house, then the figure again; a dot travels one side every fifteen seconds',
     'A triangle of light. Inside it two eyes, then the face, the seated person, the room, the house, the neighbourhood and the city, each around the last, then the eyes again; a dot travels one side every fifteen seconds')
swap('content="Two minutes: attention widens from you to the house you are in, to the city around it, and comes back."',
     'content="Two minutes: attention widens from your eyes to the room, the house, the city, and comes back."')
assert 'HOME' not in re.sub(r'<!-- lang:start.*', '', s, flags=re.S).split('<script>')[-1].replace('at(VIEWS', ''), 'HOME still used'
open(P, 'w', encoding='utf-8', newline='\n').write(s)
print(P, len(s))
