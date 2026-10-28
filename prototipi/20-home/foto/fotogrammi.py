# Prototipo #20, variante E vera: 8 fotogrammi dal video del Parlamento europeo I257607 (© Unione europea, 2024),
# seggio vicino al Colosseo, tra 2:47,6 e 2:50,8. Duotono, ritaglio sotto la fila dei simboli di partito del manifesto.
import sys, os
from PIL import Image, ImageOps
src, d = sys.argv[1], sys.argv[2]
SCELTI = [5, 10, 13, 14, 15, 16, 17, 20]          # fotogrammi estratti a 6,25 fps da 2:47,6
TOP = 340                                         # sotto i simboli dei partiti (y 120-300 su 1080)
tagli = {'16x9': (80, TOP, 80 + 1350, TOP + 740), '4x5': (560, TOP, 560 + 592, TOP + 740)}
def lum(v):
    c = v / 255; return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
INK = 0.2126*lum(0x27) + 0.7152*lum(0x10) + 0.0722*lum(0x02)
tot = {}
for n, i in enumerate(SCELTI):
    g = ImageOps.grayscale(Image.open(os.path.join(src, f'f{i:02d}.jpg')))
    g = ImageOps.autocontrast(g, cutoff=(0.5, 0.5)) if False else g
    duo = ImageOps.colorize(g, black='#271002', white='#FAF8F1')
    for t, box in tagli.items():
        c = duo.crop(box)
        if n == 0:
            w, h = c.size
            z = sorted(c.convert('L').crop((0, 0, int(w * .7), int(h * .22))).getdata())
            p10 = z[int(len(z) * .1)]
            rgb = [a + (b - a) * p10 / 255 for a, b in ((0x27, 0xFA), (0x10, 0xF8), (0x02, 0xF1))]
            L = 0.2126*lum(rgb[0]) + 0.7152*lum(rgb[1]) + 0.0722*lum(rgb[2])
            print(f'{t}: titolo in inchiostro sul 10% più scuro della fascia alta: {(L + .05) / (INK + .05):.1f}:1')
        for lw in ((780,) if t == '4x5' else (780, 1200)):
            r = c.resize((lw, round(lw * c.size[1] / c.size[0])), Image.LANCZOS)
            p = os.path.join(d, f'v-{t}-{lw}-{n}.avif'); r.save(p, quality=42)
            q = p.replace('.avif', '.webp'); r.save(q, quality=60)
            tot.setdefault((t, lw), [0, 0]); tot[(t, lw)][0] += os.path.getsize(p); tot[(t, lw)][1] += os.path.getsize(q)
for k, (a, w) in tot.items(): print(k, f'AVIF {a // 1024} KB, WebP {w // 1024} KB per 8 fotogrammi')
