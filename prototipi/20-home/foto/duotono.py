# Prototipo #20: duotono e ritagli delle due foto candidate per la copertina della home.
import sys, os
from PIL import Image, ImageOps
d = sys.argv[1]
foto = {
    # nome: (file, punto focale per i ritagli verticali, punto focale per i ritagli larghi)
    'seggio': ('seggio-originale.jpg', (0.22, 0.48), (0.50, 0.50)),
    'urna': ('urna-originale.jpg', (0.50, 0.40), (0.50, 0.42)),
}
tagli = {'4x5': 4/5, '2x3': 2/3, '16x9': 16/9, '21x9': 21/9}
def lum(v):  # luminanza relativa sRGB
    c = v / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
CARTA = 0.2126*lum(0xFA) + 0.7152*lum(0xF8) + 0.0722*lum(0xF1)
for nome, (f, fv, fl) in foto.items():
    g = ImageOps.grayscale(Image.open(os.path.join(d, f)))
    duo = ImageOps.colorize(g, black='#271002', white='#FAF8F1')
    W, H = duo.size
    for t, r in tagli.items():
        fx, fy = fv if r < 1 else fl
        if W / H > r: h = H; w = int(h * r)
        else: w = W; h = int(w / r)
        x = min(max(int(fx * W - w / 2), 0), W - w)
        y = min(max(int(fy * H - h / 2), 0), H - h)
        c = duo.crop((x, y, x + w, y + h))
        # contrasto del titolo in carta sul 10% più chiaro di tre zone a sinistra
        gl = c.convert('L')
        for zona, (y0, y1) in {'basso': (2/3, 1), 'centro': (1/3, 2/3), 'alto': (0, 1/3)}.items():
            z = sorted(gl.crop((0, int(y0*h), int(w*0.6), int(y1*h))).getdata())
            p90 = z[int(len(z)*0.9)]
            # il grigio p90 nel duotono: interpolazione lineare inchiostro->carta
            rgb = [a + (b - a) * p90 / 255 for a, b in ((0x27, 0xFA), (0x10, 0xF8), (0x02, 0xF1))]
            L = 0.2126*lum(rgb[0]) + 0.7152*lum(rgb[1]) + 0.0722*lum(rgb[2])
            print(f'{nome} {t} {zona}: contrasto {(CARTA+0.05)/(L+0.05):.1f}:1')
        for lw in (390, 780, 1200):
            if lw > w: continue
            im = c.resize((lw, round(lw / r)), Image.LANCZOS)
            for ext, kw in (('avif', {'quality': 50}), ('webp', {'quality': 72})):
                im.save(os.path.join(d, f'{nome}-{t}-{lw}.{ext}'), **kw)
