"""The language switch: one small word in the top right corner of every page (RUS / ENG).

Run from the repository root:  python -X utf8 sounds/recipe/lang.py
It writes the same block into all six pages, between the lang:start and lang:end marks, and can be run again.

How it works: the pages keep writing English. The block watches the page's text and, when Russian is chosen,
shows the Russian for each piece (RU: whole strings; RULES: strings with numbers in them). The English is kept
on each text node, so switching back needs no reload and a running exercise keeps running.
The choice is remembered in localStorage 'instruments.lang'; with no choice yet, a Russian browser starts in Russian.

Font: none is added. The pages' system font (Roboto / One UI on Android, Segoe UI on Windows, San Francisco on Apple)
has Cyrillic in the same light weights, so both languages are set in one face. <html lang> is switched too, so the
browser picks Russian letterforms and a screen reader the Russian voice.

The voice on Sit is recorded in English only (Kokoro has no Russian voice); its hint says so in Russian.
"""
import json, re, os

PAGES = ['index.html', 'unclench.html', 'hexagon.html', 'sit.html', 'widen.html', 'hum.html']

RU = {
    # shared
    'Ready': 'Начнём', 'Paused': 'Пауза', 'Done': 'Готово',
    'Start': 'Начать', 'Begin': 'Начать', 'Pause': 'Пауза', 'Resume': 'Дальше', 'Again': 'Снова',
    'Sound ': 'Звук ', 'Voice ': 'Голос ', 'on': 'вкл', 'off': 'выкл',
    'Click to start or pause': 'Нажми, чтобы начать или поставить на паузу',
    'Tap to begin or pause': 'Нажми, чтобы начать или поставить на паузу',
    'Instruments': 'Инструменты',
    # names
    'Box': 'Квадрат', 'Unclench': 'Разожми', 'Hex': 'Гекс', 'Sit': 'Посиди', 'Widen': 'Шире', 'Hum': 'Напев',
    'Box Breathing': 'Дыхание по квадрату',
    # Box
    'Box breathing · 2 minutes': 'Квадрат · 2 минуты',
    'Inhale': 'Вдох', 'Hold': 'Задержка', 'Exhale': 'Выдох',
    'Inhale 4 · Hold 4 · Exhale 4 · Hold 4. Space starts or pauses. The tone rises as you breathe in; a click marks each corner.':
        'Вдох 4 · Задержка 4 · Выдох 4 · Задержка 4. Пробел — старт и пауза. На вдохе тон поднимается; щелчок отмечает каждый угол.',
    'A square of light; it brightens as you inhale, dims as you exhale; a dot travels one edge per phase':
        'Квадрат света; на вдохе он светлеет, на выдохе тускнеет; точка проходит одну сторону за фазу',
    # Unclench
    'Unclench · 2 minutes': 'Разожми · 2 минуты',
    'Put the day down for two minutes.': 'Отложи день на две минуты.',
    'Feet': 'Ступни', 'Feel the floor under them.': 'Почувствуй пол под ними.',
    'Jaw': 'Челюсть', 'Let it drop a little.': 'Пусть чуть опустится.',
    'Shoulders': 'Плечи', 'Let them fall away from your ears.': 'Пусть опустятся, подальше от ушей.',
    'Hands': 'Руки', 'Open them. Palms up.': 'Раскрой их. Ладонями вверх.',
    'Breath': 'Дыхание', 'Three long exhales.': 'Три долгих выдоха.',
    'Eyes': 'Глаза', 'One thing you can see. Just look.': 'Одна вещь, которую видишь. Просто смотри.',
    'The next thing is yours to choose.': 'Что дальше — выбираешь ты.',
    'A ping marks each step; it moves on by itself. Tap to pause. Space works too.':
        'Сигнал отмечает каждый шаг; дальше идёт само. Нажми — пауза. Пробел тоже работает.',
    'A room seen from its doorway; the red back wall comes closer with each step until it fills the frame':
        'Комната, если смотреть из дверей; красная дальняя стена подходит ближе с каждым шагом, пока не займёт всю рамку',
    # Hex
    'Hex · 2 minutes': 'Гекс · 2 минуты',
    'Six notes, four seconds each. Follow the dot. Space starts or pauses.':
        'Шесть нот, по четыре секунды. Следи за точкой. Пробел — старт и пауза.',
    'A hexagon of light; a dot travels one side every four seconds; the light is brighter on higher notes':
        'Шестиугольник света; точка проходит одну сторону за четыре секунды; на высоких нотах свет ярче',
    # Sit
    'Sit · under 3 minutes': 'Посиди · до 3 минут',
    'Sit with it. Nothing to fix.': 'Побудь с этим. Исправлять нечего.',
    'Body': 'Тело', 'Facts': 'Факты', 'Mind': 'Ум', 'Kind': 'Тепло', 'Here': 'Здесь',
    'Find where it sits in your body.': 'Найди, где это сидит в теле.',
    'Chest. Stomach. Throat. Hands.': 'Грудь. Живот. Горло. Руки.',
    'Name what is there, in plain words. Tight. Hot. Fluttering.': 'Назови, что там, простыми словами. Сжато. Горячо. Дрожит.',
    'Watch it. Nothing to fix.': 'Наблюдай. Исправлять нечего.',
    'This is a sensation.': 'Это ощущение.',
    'It is uncomfortable. It is not an emergency.': 'Это неприятно. Это не опасно.',
    'If the mind runs ahead, come back to what is here.': 'Если ум убегает вперёд, вернись к тому, что здесь.',
    'Now the thoughts. Watch them like a show.': 'Теперь мысли. Смотри на них, как на спектакль.',
    'Is it predicting? Wanting to be sure? Solving? Asking for reassurance?': 'Ум предсказывает? Хочет уверенности? Решает? Просит, чтобы успокоили?',
    'Name the kind. Stay in your seat.': 'Назови, какая это мысль. Оставайся на месте.',
    'Say to yourself what you would say to a friend.': 'Скажи себе то, что говорят другу.',
    'This is hard. I can be here with it.': 'Это трудно. Я могу быть с этим рядом.',
    'It can stay as long as it stays.': 'Пусть остаётся, сколько останется.',
    'Feel your feet. Your weight in the seat.': 'Почувствуй ступни. Свой вес на сиденье.',
    'Look at one thing in the room.': 'Посмотри на одну вещь в комнате.',
    'You stayed.': 'Ты всё ещё здесь.',
    'A voice reads each line; the switch changes it or turns it off. The aim is to stay, not to make it go.':
        'Голос читает каждую строку, по-английски; переключатель меняет его или выключает. Цель — остаться, а не прогнать.',
    'A pentagon of light that holds still; a dot travels one side for each of the five parts':
        'Пятиугольник света стоит неподвижно; точка проходит по одной стороне на каждую из пяти частей',
    # Widen
    'Widen · 2 minutes': 'Шире · 2 минуты',
    'You': 'Ты', 'House': 'Дом', 'City': 'Город',
    'You, the house you are in, the city around it, then you again. Fifteen seconds a side. Let your attention widen with the picture.':
        'Ты, твой дом, город вокруг, и снова ты. По пятнадцать секунд на сторону. Пусть внимание расширяется вместе с картинкой.',
    'A triangle of light. Inside it a seated figure, then the house around the figure, then the city around the house, then the figure again; a dot travels one side every fifteen seconds':
        'Треугольник света. В нём сидящая фигура, потом дом вокруг фигуры, потом город вокруг дома, потом снова фигура; точка проходит одну сторону за пятнадцать секунд',
    # Hum
    'Hum · 2½ minutes': 'Напев · 2½ минуты',
    'Breathe in': 'Вдох', 'Rest': 'Отдых',
    'Hum along with the melody. Where it stops, breathe in, as a singer would. The red square is your air.':
        'Напевай вместе с мелодией. Где она замолкает — вдохни, как певец. Красный квадрат — твой воздух.',
    'A figure of light from Bulgarian embroidery, with a red square at its centre. The square fills on each breath in and empties while you hum; a dot travels the outline once per round':
        'Фигура света из болгарской вышивки, с красным квадратом в центре. Квадрат наполняется на вдохе и пустеет, пока ты напеваешь; точка обходит контур один раз за круг',
}
# the page name "Hum" and the word shown while humming are one English string; the phase word on hum.html is set below
HUM_PHASE = 'Напевай'

# strings with numbers in them: [pattern, replacement], tried in order when there is no whole-string match
RULES = [
    ['^Round ', 'Круг '], ['^Lap ', 'Круг '], ['^Step ', 'Шаг '], ['^Part ', 'Часть '], ['^Side ', 'Сторона '],
    ['^You took ', 'Заняло '], ['^In · ', 'Вдох · '], ['^Out, long · ', 'Долгий выдох · '], [' of ', ' из '],
    ['^Previous: ', 'Назад: '], ['^Next: ', 'Дальше: '],
]

CSS = """  /* lang:start (written by sounds/recipe/lang.py) */
  /* the language switch: one small word in the corner, the language it would change to */
  #lang { position: fixed; top: 0; right: 0; min-width: 48px; min-height: 44px; padding: 7px 12px 0 0; display: grid; place-content: start end;
          background: none; border: 0; color: var(--muted); font-size: 10.5px; font-weight: 500; letter-spacing: .16em; text-transform: uppercase; opacity: 1; }
  #lang:hover, #lang:focus-visible { color: var(--fg); opacity: 1; outline: none; }
  #lang:focus-visible { text-decoration: underline; text-underline-offset: 4px; }
  /* lang:end */
"""

JS = """<!-- lang:start (written by sounds/recipe/lang.py) -->
<button id="lang" type="button"></button>
<script>
(() => {
  // The page writes English; this shows Russian in its place when Russian is chosen. The English stays on each
  // text node (_en), so the switch works both ways, at any moment, without a reload.
  const RU = %(ru)s;
  const RULES = %(rules)s.map(([a, b]) => [new RegExp(a), b]);
  const HERE = %(here)s;                               // this page's phase word only, where it differs from the shared one
  const ru = (s, n) => n && n.parentNode.id === 'phase' && HERE[s] !== undefined ? HERE[s] : RU[s] !== undefined ? RU[s] : RULES.reduce((x, [a, b]) => x.replace(a, b), s);
  const btn = document.getElementById('lang'), root = document.documentElement;
  let lang = 'en';
  try { lang = localStorage.getItem('instruments.lang') || ((navigator.language || '').slice(0, 2) === 'ru' ? 'ru' : 'en'); } catch (e) {}
  const TITLE = document.title, ATTRS = [];
  for (const el of document.querySelectorAll('[title], [aria-label]')) for (const a of ['title', 'aria-label']) if (el.hasAttribute(a)) ATTRS.push([el, a, el.getAttribute(a)]);
  const show = n => {                                  // one text node
    if (n._en === undefined) n._en = n.data;
    if (!n._en.trim() || btn.contains(n)) return;
    const s = lang === 'ru' ? ru(n._en, n) : n._en;
    if (n.data !== s) n.data = s;
  };
  const walk = el => { const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); for (let n; (n = w.nextNode());) if (!n.parentNode.closest('script, style')) show(n); };
  const apply = () => {
    root.lang = lang;
    document.title = lang === 'ru' ? ru(TITLE) : TITLE;
    for (const [el, a, s] of ATTRS) el.setAttribute(a, lang === 'ru' ? ru(s) : s);
    btn.textContent = lang === 'ru' ? 'Eng' : 'Рус';
    btn.setAttribute('aria-label', lang === 'ru' ? 'English' : 'Русский язык');
    btn.lang = lang === 'ru' ? 'en' : 'ru';
    walk(document.body);
  };
  // whatever the page writes later: textContent makes a new text node, which arrives here before it is painted
  new MutationObserver(recs => { for (const r of recs) for (const n of r.addedNodes) { if (n.nodeType === 3) show(n); else if (n.nodeType === 1) walk(n); } })
    .observe(document.body, { childList: true, subtree: true });
  btn.addEventListener('click', e => {
    e.stopPropagation();
    lang = lang === 'ru' ? 'en' : 'ru';
    try { localStorage.setItem('instruments.lang', lang); } catch (e) {}
    apply();
  });
  apply();
})();
</script>
<!-- lang:end -->
"""


def build(root='.'):
    for k in RU: RU[k] = RU[k].replace(' — ', ' — ')        # a dash never starts a line in Russian
    for page in PAGES:
        p = os.path.join(root, page)
        s = open(p, encoding='utf-8').read()
        s = re.sub(r'  /\* lang:start.*?/\* lang:end \*/\n', '', s, flags=re.S)
        s = re.sub(r'<!-- lang:start.*?<!-- lang:end -->\n', '', s, flags=re.S)
        here = {'Hum': HUM_PHASE} if page == 'hum.html' else {}
        js = JS % {'ru': json.dumps(RU, ensure_ascii=False), 'rules': json.dumps(RULES, ensure_ascii=False), 'here': json.dumps(here, ensure_ascii=False)}
        assert s.count('</style>') == 1 and s.count('</body>') == 1, page
        s = s.replace('</style>', CSS + '</style>').replace('</body>', js + '</body>')
        open(p, 'w', encoding='utf-8', newline='\n').write(s)
        print(page, len(s))


if __name__ == '__main__':
    build()
