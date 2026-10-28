# Prototipo #20, variante E: la foto dell'urna divisa in tre livelli (sfondo pulito, scheda, mano).
# Coordinate in pixel della miniatura 1920x1277; ritagli uguali a duotono.py.
import sys, os
from PIL import Image, ImageOps, ImageDraw, ImageFilter
d = sys.argv[1]
g = ImageOps.grayscale(Image.open(os.path.join(d, 'urna-originale.jpg')))
W, H = g.size
FESSURA = 872                      # bordo alto della fessura
SCHEDA = [(987, 248), (1338, 545), (1105, FESSURA + 8), (1030, FESSURA + 8), (698, 615)]
MANO = [(x + 550, y + 150) for x, y in [(635, 260), (695, 215), (780, 198), (900, 188), (970, 215), (1030, 270), (1100, 305), (1200, 350), (1300, 380), (1380, 385), (1380, 715), (1200, 660), (1050, 610), (955, 555), (870, 625), (830, 640), (780, 625), (750, 575), (730, 530), (700, 500), (600, 462), (588, 400), (608, 360), (635, 325)]]
def maschera(poli, allarga=0):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(poli, fill=255)
    return m.filter(ImageFilter.MaxFilter(allarga * 2 + 1)) if allarga else m
m_scheda, m_mano = maschera(SCHEDA), maschera(MANO)
buco = Image.new('L', (W, H), 0); buco.paste(255, mask=maschera(SCHEDA, 9)); buco.paste(255, mask=maschera(MANO, 8))
px, b = g.load(), buco.load()
# Sfondo pulito. Tenda (sopra l'urna): pieghe verticali, si riempie a specchio dalle colonne a sinistra del buco,
# tranne la colonna del palo (x 945-1020), che si prolunga verso il basso. Urna: si interpola per righe.
URNA = 728
PALO = range(945, 1021)
for x in PALO:
    ys = [y for y in range(URNA) if b[x, y]]
    if not ys: continue
    sopra = [px[x, y] for y in range(40, min(230, ys[0])) if not b[x, y]] or [30]
    v = sorted(sopra)[len(sopra) // 2]
    for y in ys: px[x, y] = v
for y in range(URNA):
    xs = [x for x in range(W) if b[x, y] and x not in PALO]
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1: j += 1
        a = xs[i]
        L = max(1, min(xs[j] - a + 1, 160, a))
        for x in range(a, xs[j] + 1):
            k = (x - a) % (2 * L)
            sx = a - 1 - (k if k < L else 2 * L - 1 - k)
            if sx in PALO: sx = a - 1
            px[x, y] = px[sx, y]
        i = j + 1
for y in range(URNA, H):
    xs = [x for x in range(W) if b[x, y]]
    if not xs: continue
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1: j += 1
        a, z = xs[i] - 1, xs[j] + 1
        va = px[a, y] if a >= 0 else None; vz = px[z, y] if z < W else None
        va = va if va is not None else vz; vz = vz if vz is not None else va
        for k, x in enumerate(range(xs[i], xs[j] + 1)):
            t = (k + 1) / (xs[j] - xs[i] + 2); px[x, y] = round(va + (vz - va) * t)
        i = j + 1
fondo = g
orig = ImageOps.grayscale(Image.open(os.path.join(d, 'urna-originale.jpg')))
# Scheda: dove la copre il pollice si ricostruisce con lo speculare dell'angolo sinistro,
# rispetto alla diagonale tra l'angolo alto (987,248) e quello basso (1049,912): bordi e riquadri combaciano.
scheda = orig.copy(); sp, op, ms, mm = scheda.load(), orig.load(), m_scheda.load(), maschera(MANO, 3).load()
cx, cy = 1018, 580
for y in range(200, 900):
    for x in range(650, 1400):
        if ms[x, y] and mm[x, y]:
            ax, ay, dx, dy = 987, 248, 62, 664; n = (dx * dx + dy * dy)
            t = ((x - ax) * dx + (y - ay) * dy) / n; qx, qy = ax + t * dx, ay + t * dy
            sx, sy = round(2 * qx - x), round(2 * qy - y)
            if 0 <= sx < W and 0 <= sy < H and ms[sx, sy] and not mm[sx, sy]: sp[x, y] = op[sx, sy]
def duo(im, alfa=None):
    c = ImageOps.colorize(im, black='#271002', white='#FAF8F1')
    if alfa is not None: c = c.convert('RGBA'); c.putalpha(alfa)
    return c
livelli = {
    'fondo': duo(fondo),
    'scheda': duo(scheda, m_scheda.filter(ImageFilter.GaussianBlur(1))),
    'mano': duo(orig, m_mano.filter(ImageFilter.GaussianBlur(1.5))),
}
tagli = {'4x5': (4/5, (0.50, 0.40)), '16x9': (16/9, (0.50, 0.42))}
for t, (r, (fx, fy)) in tagli.items():
    if W / H > r: h = H; w = int(h * r)
    else: w = W; h = int(w / r)
    x = min(max(int(fx * W - w / 2), 0), W - w); y = min(max(int(fy * H - h / 2), 0), H - h)
    print(f'{t}: ritaglio x={x} y={y} {w}x{h}, fessura al {100 * (FESSURA - y) / h:.2f}%, corsa scheda {100 * (FESSURA + 8 - 248) / h:.2f}%')
    for nome, im in livelli.items():
        c = im.crop((x, y, x + w, y + h))
        for lw in (390, 780, 1200):
            if lw > w: continue
            r2 = c.resize((lw, round(lw / r)), Image.LANCZOS)
            p = os.path.join(d, f'e-{nome}-{t}-{lw}.webp')
            r2.save(p, quality=72 if nome == 'fondo' else 80)
            if nome == 'fondo': r2.save(p.replace('.webp', '.avif'), quality=50)
            print(f'  {nome} {lw}: {os.path.getsize(p) // 1024} KB')
