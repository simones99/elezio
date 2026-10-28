# Prototipo #25: trattamenti grafici per gli 8 fotogrammi della variante E (stessi ritagli di fotogrammi.py).
# Uso: python -P trattamenti.py <cartella fotogrammi fNN.jpg> <cartella foto>
# Scrive foto/t-<trattamento>/v-<taglio>-<larghezza>-<n>.{avif,webp} e stampa peso e contrasto del titolo.
# Retino a punti e retino o dithering a piena risoluzione in build pesano 0,9-2 MB per 8 fotogrammi: il retino
# si fa nel browser con un filtro SVG sui fotogrammi lisci (index.html, #f-retino), come la grana CSS (#f-grana-n);
# il dithering si fa qui ma a bassa risoluzione (195 e 400 px), WebP senza perdita, ingrandito dal browser a pixel netti.
import sys, os
import numpy as np
from PIL import Image, ImageOps, ImageFilter
src, out = sys.argv[1], sys.argv[2]
SCELTI = [5, 10, 13, 14, 15, 16, 17, 20]
TOP = 340
TAGLI = {'16x9': (80, TOP, 80 + 1350, TOP + 740), '4x5': (560, TOP, 560 + 592, TOP + 740)}
LARGH = {'16x9': (780, 1200), '4x5': (780,)}
INK, PAPER = np.array([0x27, 0x10, 0x02], float), np.array([0xFA, 0xF8, 0xF1], float)

def duo(g):                                   # g: grigio 0..1 -> RGB inchiostro-carta
    return Image.fromarray((INK + (PAPER - INK) * g[..., None]).round().astype(np.uint8))

def curva(g, nero=.08, bianco=.92, gamma=1.0):
    return np.clip((g - nero) / (bianco - nero), 0, 1) ** gamma

def grana(g, n, forza):
    rng = np.random.default_rng(n)            # grana diversa per fotogramma: si muove come pellicola
    rumore = rng.normal(0, 1, g.shape)
    rumore = np.array(Image.fromarray(((rumore * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6)), float) / 255 - .5
    peso = 1 - np.abs(g - .5) * 1.2           # più grana nei mezzitoni, meno nei bianchi e neri pieni
    return np.clip(g + rumore * forza * 2.5 * peso, 0, 1)

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 + 1 / 32
def dither(g, livelli):                       # dithering ordinato di Bayer 4x4, a 3 livelli: carta, mezzatinta, inchiostro
    s = g.shape
    soglia = np.tile(BAYER, (s[0] // 4 + 1, s[1] // 4 + 1))[:s[0], :s[1]]
    return np.clip(np.floor(g * (livelli - 1) + soglia) / (livelli - 1), 0, 1)

def poster(g, livelli):
    gg = np.array(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)).filter(ImageFilter.MedianFilter(9)), float) / 255
    q = np.round(gg * (livelli - 1)) / (livelli - 1)
    return q

def tratta(nome, g, n, lw):                   # g già ridotto alla larghezza finale
    if nome == 'liscio': return g
    if nome == 'grana': return grana(curva(g, .04, .96), n, .10)
    if nome == 'forte': return grana(curva(g, .18, .82, 1.15), n, .07)
    if nome == 'poster': return poster(curva(g, .06, .94), livelli=4)
    raise ValueError(nome)

def lum(c):
    c = c / 255; return np.where(c <= .03928, c / 12.92, ((c + .055) / 1.055) ** 2.4)
LINK = (lum(INK) * [.2126, .7152, .0722]).sum()

def contrasto(img, passo):                   # sul tono percepito: media su una cella del retino o del dither
    r = img.filter(ImageFilter.BoxBlur(passo)) if passo else img
    w, h = r.size
    a = np.array(r.crop((0, 0, int(w * .7), int(h * .22))), float).reshape(-1, 3)
    L = (lum(a) * [.2126, .7152, .0722]).sum(1)
    p10 = np.sort(L)[int(len(L) * .1)]
    return (p10 + .05) / (LINK + .05)

PIXEL = {'16x9': 400, '4x5': 195}            # larghezza del file di dithering: 2 px CSS per pixel su telefono, ~3,6 da 1440
nomi = sys.argv[3:] or ['liscio', 'grana', 'forte', 'poster', 'pixel']
for nome in nomi:
    d = os.path.join(out, f't-{nome}'); os.makedirs(d, exist_ok=True)
    tot, cr = {}, []
    for n, i in enumerate(SCELTI):
        g0 = ImageOps.grayscale(Image.open(os.path.join(src, f'f{i:02d}.jpg')))
        for t, box in TAGLI.items():
            c = g0.crop(box)
            if nome == 'pixel':
                lw = PIXEL[t]
                r = c.resize((lw, round(lw * c.size[1] / c.size[0])), Image.LANCZOS)
                img = duo(dither(curva(np.array(r, float) / 255, .06, .94), 3))
                if t == '4x5' and n == 0: cr.append(contrasto(img, 2))
                p = os.path.join(d, f'v-{t}-{lw}-{n}.webp'); img.save(p, lossless=True, quality=100, method=6)
                k = (t, lw); tot.setdefault(k, [0, 0]); tot[k][1] += os.path.getsize(p)
                continue
            for lw in LARGH[t]:
                r = c.resize((lw, round(lw * c.size[1] / c.size[0])), Image.LANCZOS)
                img = duo(tratta(nome, np.array(r, float) / 255, n, lw))
                if t == '4x5' and n == 0: cr.append(contrasto(img, 0))
                p = os.path.join(d, f'v-{t}-{lw}-{n}.avif')
                q = 42 if nome in ('liscio', 'poster') else 50
                img.save(p, quality=q)
                img.save(p.replace('.avif', '.webp'), quality=60 if nome in ('liscio', 'poster') else 70)
                k = (t, lw); tot.setdefault(k, [0, 0])
                tot[k][0] += os.path.getsize(p); tot[k][1] += os.path.getsize(p.replace('.avif', '.webp'))
    pesi = ', '.join(f'{t}-{lw}: AVIF {a // 1024} KB / WebP {w // 1024} KB' for (t, lw), (a, w) in tot.items())
    print(f'{nome:7} titolo {cr[0]:.1f}:1 | {pesi}')
