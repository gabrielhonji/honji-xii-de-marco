"""Export the approved Giro symbol for browsers, mobile screens and sharing."""
from pathlib import Path
from math import cos, sin, radians
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
CREAM = '#F8F4ED'
WINE = '#761B35'

# Exact cubic segments of the canonical Giro petal (64 x 64 coordinate system).
SEGMENTS = [
    ((28, 28), (10, 26), (6, 18), (13, 10)),
    ((13, 10), (19, 3), (33, 5), (37, 13)),
    ((37, 13), (41, 20), (37, 25), (28, 28)),
]


def draw_giro(target, x, y, size, color):
    points = []
    for controls in SEGMENTS:
        for i in range(81):
            t = i / 80
            weights = ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3)
            points.append(tuple(sum(w*p[axis] for w, p in zip(weights, controls)) for axis in (0, 1)))
    draw = ImageDraw.Draw(target)
    for angle in (0, 90, 180, 270):
        a = radians(angle)
        polygon = []
        for px, py in points:
            dx, dy = px - 32, py - 32
            polygon.append((x + (32 + dx*cos(a) - dy*sin(a))*size/64,
                            y + (32 + dx*sin(a) + dy*cos(a))*size/64))
        draw.polygon(polygon, fill=color)


def font(size, serif=False):
    names = ['C:/Windows/Fonts/georgia.ttf' if serif else 'C:/Windows/Fonts/arial.ttf',
             '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf' if serif else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default(size=size)


icon = Image.new('RGB', (2048, 2048), WINE)
draw_giro(icon, 256, 256, 1536, CREAM)
for name, size in [('apple-touch-icon.png', 180), ('icon-192.png', 192), ('icon-512.png', 512)]:
    icon.resize((size, size), Image.Resampling.LANCZOS).save(OUT / name)
favicon = Image.new('RGBA', (2048, 2048), (0, 0, 0, 0))
ImageDraw.Draw(favicon).ellipse((0, 0, 2047, 2047), fill=WINE)
draw_giro(favicon, 256, 256, 1536, CREAM)
favicon.save(OUT / 'favicon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
symbol = (OUT / 'honji-symbol.svg').read_text(encoding='utf-8')
start, end = symbol.index('<g id="mark"'), symbol.rindex('</g>') + 4
mark = symbol[start:end].replace('fill="currentColor"', 'fill="#F8F4ED"')
(OUT / 'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><title>HONJI</title><circle cx="32" cy="32" r="32" fill="#761B35"/><g transform="translate(8 8) scale(.75)">' + mark + '</g></svg>\n', encoding='utf-8')

card = Image.new('RGB', (2400, 1260), CREAM)
draw = ImageDraw.Draw(card)
for x in range(0, 2400, 120):
    draw.line((x, 0, x, 1260), fill='#E4D6CF', width=2)
for y in range(0, 1260, 120):
    draw.line((0, y, 2400, y), fill='#E4D6CF', width=2)
draw_giro(card, 160, 88, 128, WINE)
draw.text((328, 112), 'HONJI', font=font(108, True), fill=WINE)
draw.text((160, 420), 'XII de Março.', font=font(212, True), fill=WINE)
draw.text((170, 740), 'Secretaria digital / UTFPR Apucarana', font=font(56), fill=WINE)
draw.line((160, 990, 2240, 990), fill=WINE, width=4)
draw.text((160, 1056), 'PARTICIPAÇÕES. SEMESTRES. RECONHECIMENTO.', font=font(38), fill=WINE)
draw.text((1788, 1056), 'gabriel.honji', font=font(42), fill=WINE)
card.resize((1200, 630), Image.Resampling.LANCZOS).save(OUT / 'social-card.png')
print('Exported approved Giro favicon, mobile icons and social card.')
