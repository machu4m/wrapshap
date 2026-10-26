"""Wrapshap x Electro Zone (Sialkot) launch post, 1080 x 1080 px.

Laid out in the reference poster's own coordinates (1254 x 1254 units), so the photo
crops from assets.py drop in where they were cut from. Writes build/post.html."""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, 'build')
FONTS = os.path.abspath(os.path.join(HERE, '..', '..', 'electro-zone-collab', 'fonts'))
YEL, BLK, WHT = '#FFC400', '#0B0B0C', '#FFFFFF'
rng = np.random.default_rng(11)


def rough_band(x0, x1, ytop, ybot, slope, jitter, n=90):
    """Dry-brush band: ragged top and bottom edges, frayed right end. Returns SVG path data."""
    xs = np.linspace(x0, x1, n)
    top = ytop + slope * (xs - x0) + np.convolve(rng.normal(0, jitter, n), np.ones(3) / 3, 'same')
    bot = ybot + slope * (xs - x0) + np.convolve(rng.normal(0, jitter, n), np.ones(3) / 3, 'same')
    pts = list(zip(xs, top))
    # frayed end: zig-zag between the edges
    for t in np.linspace(0, 1, 9)[1:-1]:
        y = top[-1] + (bot[-1] - top[-1]) * t
        pts.append((x1 + rng.uniform(-40, 25), y))
    pts += list(zip(xs[::-1], bot[::-1]))
    d = 'M' + ' L'.join('%.1f %.1f' % p for p in pts) + 'Z'
    # loose streaks beyond the band
    for _ in range(14):
        sx = rng.uniform(x1 - 160, x1 + 30); sy = rng.uniform(ytop, ybot) + slope * (sx - x0)
        L = rng.uniform(25, 90); h = rng.uniform(1.5, 4.5)
        d += 'M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1fZ' % (sx, sy, sx + L, sy + slope * L, sx + L, sy + slope * L + h, sx, sy + h)
    return d


grunge = open(os.path.join(B, 'grunge_path.txt')).read()
banner = rough_band(-10, 590, 236, 344, -0.06, 2.2)
swoosh = 'M842 846 C930 826 1050 812 1172 800 L1176 808 C1060 822 940 838 846 856 Z'

ICON = {   # 64 x 64 line icons, stroke drawn by CSS
    'clear': '<path d="M14 24 L22 12 H42 L50 24 L32 52 Z M14 24 H50 M22 12 L28 24 L32 52 L36 24 L42 12 M28 24 H36"/>',
    'matte': '<path d="M32 8 L56 20 L32 32 L8 20 Z"/><path d="M8 31 L32 43 L56 31"/><path d="M8 42 L32 54 L56 42"/>',
    'privacy': '<path d="M6 32 C14 20 22 15 32 15 C42 15 50 20 58 32 C50 44 42 49 32 49 C22 49 14 44 6 32 Z"/><circle cx="32" cy="32" r="8"/><path d="M12 54 L52 10"/>',
    'tuff': '<path d="M32 6 L54 14 V30 C54 44 44 53 32 58 C20 53 10 44 10 30 V14 Z"/><path d="M22 32 L29 39 L43 25"/>',
}
CARDS = [('clear', 'CLEAR', 'Crystal clear<br>protection', 233), ('matte', 'MATTE', 'Smooth,<br>anti-glare finish', 440),
         ('privacy', 'PRIVACY', 'Keeps your<br>screen private', 642), ('tuff', 'TUFF', 'Extra strong<br>protection', 845)]
DEVICES = [('dev-phone', (88, 1040, 206, 1176), 'SMARTPHONES', 148), ('dev-tablet', (300, 1040, 452, 1174), 'TABLETS / iPADS', 390),
           ('dev-laptop', (548, 1056, 724, 1166), 'LAPTOPS', 634), ('dev-watch', (806, 1040, 922, 1174), 'SMART WATCHES', 875),
           ('dev-earbuds', (1044, 1046, 1160, 1162), 'EARBUDS<br>&amp; MORE', 1107)]


def img(name, box):
    x0, y0, x1, y1 = box
    return f'<img src="{name}.png" style="left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{y1 - y0}px">'


cards = ''.join(f'''
<div class="card" style="left:{x}px">
  <svg class="icon" viewBox="0 0 64 64">{ICON[k]}</svg>
  <div class="ct">{t}</div><div class="cd">{d}</div>
</div>''' for k, t, d, x in CARDS)
devices = ''.join(img(n, b) + f'<div class="dl" style="left:{c - 110}px;top:{1178 if "<br>" not in l else 1160}px">{l}</div>'
                  for n, b, l, c in DEVICES)
seps = ''.join(f'<div class="sep" style="left:{x}px"></div>' for x in (264, 519, 760, 995))

html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Montserrat; font-weight: 500; src: url("file://{FONTS}/Montserrat-Medium.ttf"); }}
@font-face {{ font-family: Montserrat; font-weight: 600; src: url("file://{FONTS}/Montserrat-SemiBold.ttf"); }}
@font-face {{ font-family: Montserrat; font-weight: 700; src: url("file://{FONTS}/Montserrat-Bold.ttf"); }}
@font-face {{ font-family: Montserrat; font-weight: 800; src: url("file://{FONTS}/Montserrat-ExtraBold.ttf"); }}
@font-face {{ font-family: "Permanent Marker"; src: url("file://{FONTS}/PermanentMarker-Regular.ttf"); }}
@page {{ size: 1080pt 1080pt; margin: 0; }}
html, body {{ margin: 0; width: 1440px; height: 1440px; overflow: hidden; background: {BLK}; }}
#art {{ position: absolute; left: 0; top: 0; width: 1254px; height: 1254px; transform: scale({1440 / 1254:.6f}); transform-origin: 0 0;
        background: {BLK}; font-family: Montserrat; color: {WHT}; }}
#art > * , .abs {{ position: absolute; }}
img {{ position: absolute; display: block; }}
.mk {{ font-family: "Permanent Marker"; white-space: nowrap; line-height: 1; }}
.card {{ top: 868px; width: 183px; height: 152px; box-sizing: border-box; border: 1.6px solid {YEL}; border-radius: 14px;
         background: rgba(8,8,9,.93); text-align: center; }}
.icon {{ display: block; width: 52px; height: 52px; margin: 13px auto 4px; fill: none; stroke: {YEL}; stroke-width: 3.4;
         stroke-linejoin: round; stroke-linecap: round; }}
.ct {{ font-weight: 800; font-size: 21px; letter-spacing: .01em; line-height: 1.1; }}
.cd {{ font-weight: 500; font-size: 15.5px; line-height: 1.22; margin-top: 3px; }}
.sep {{ top: 1058px; width: 1.5px; height: 134px; background: {YEL}; opacity: .55; }}
.dl {{ width: 220px; text-align: center; font-weight: 700; font-size: 19px; line-height: 1.22; }}
</style></head><body><div id="art">

<svg style="left:0;top:0" width="1254" height="1254" viewBox="0 0 1254 1254">
  <path fill="{YEL}" fill-rule="evenodd" d="{grunge}"/>
</svg>
{img('shop', (585, 212, 1254, 705))}
{img('phone', (30, 465, 680, 910))}

<!-- header: wrapshap logo (placed as vector afterwards) x Electro Zone -->
<div class="logo-slot" id="wrapshap" style="left:103px;top:22px;width:430px;height:148px"></div>
<div style="left:531px;top:40px;font-size:20px;font-weight:600">&reg;</div>
<div style="left:68px;top:188px;width:500px;text-align:center;font-weight:600;font-size:16.5px;letter-spacing:.34em">PREMIUM DEVICE PROTECTION</div>
<svg style="left:592px;top:76px" width="66" height="66" viewBox="0 0 66 66"><path d="M3 3 L63 63 M63 3 L3 63" stroke="{WHT}" stroke-width="4.5" stroke-linecap="round"/></svg>
<div style="left:712px;top:58px;font-weight:800;font-size:69px;letter-spacing:-.035em;line-height:1;white-space:nowrap">Electro
  <span style="color:{YEL}">Z<svg style="width:.62em;height:.62em;vertical-align:-.02em;margin:0 .005em" viewBox="0 0 62 62">
  <circle cx="31" cy="31" r="24" fill="none" stroke="{YEL}" stroke-width="12.5"/>
  <path d="M36 3 L18 35 H30 L24 59 L45 25 H33 L40 3 Z" fill="{YEL}" stroke="{BLK}" stroke-width="4.5" stroke-linejoin="round"/></svg>ne</span></div>
<div style="left:718px;top:144px;width:470px;display:flex;align-items:center;gap:22px;font-weight:600;font-size:24px;letter-spacing:.45em">
  <span style="flex:1;height:2px;background:{WHT}"></span><span style="margin-right:-.45em">SIALKOT</span><span style="flex:1;height:2px;background:{WHT}"></span></div>

<!-- now available at -->
<svg style="left:0;top:0" width="700" height="420" viewBox="0 0 700 420"><path fill="{YEL}" d="{banner}"/></svg>
<div class="mk" style="left:52px;top:250px;font-size:64px;color:{BLK};transform:rotate(-4deg) scaleX(.8);transform-origin:0 50%">NOW AVAILABLE AT</div>
<div style="left:35px;top:343px;width:543px;height:113px;border-radius:24px;background:{YEL}"></div>
<svg style="left:62px;top:362px" width="58" height="78" viewBox="0 0 58 78"><path fill-rule="evenodd" fill="{BLK}"
  d="M29 0 C13 0 0 12.6 0 28.5 C0 49 29 78 29 78 C29 78 58 49 58 28.5 C58 12.6 45 0 29 0 Z M29 16 A12.5 12.5 0 1 0 29.01 16 Z"/></svg>
<div style="left:146px;top:354px;width:412px;text-align:center;color:{BLK}">
  <div style="font-weight:800;font-size:51px;line-height:1;letter-spacing:-.01em">ELECTRO ZONE</div>
  <div style="font-weight:600;font-size:27px;letter-spacing:.45em;margin-right:-.45em;margin-top:9px">SIALKOT</div></div>

<!-- tagline -->
<div class="abs" style="left:728px;top:732px;transform:rotate(-8deg) scaleX(.72);transform-origin:0 0">
  <div class="mk" style="font-size:66px;color:{WHT}">STAY WRAPPED.</div>
  <div class="mk" style="font-size:66px;color:{YEL};margin:-10px 0 0 130px">STAY PROTECTED.</div></div>
<svg style="left:0;top:0" width="1254" height="1254" viewBox="0 0 1254 1254"><path fill="{YEL}" d="{swoosh}"/></svg>

<!-- protection finishes -->
{cards}

<!-- devices -->
<div style="left:30px;top:1033px;width:1195px;height:182px;box-sizing:border-box;border:2px solid {YEL};border-radius:22px;background:#050505"></div>
{seps}
{devices}
</div></body></html>'''
open(os.path.join(B, 'post.html'), 'w').write(html)
print('wrote build/post.html')
