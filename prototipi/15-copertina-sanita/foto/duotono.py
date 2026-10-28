import sys, os
from PIL import Image, ImageOps
d = sys.argv[1]
src = ImageOps.grayscale(Image.open(os.path.join(d, 'originale.jpg')))
duo = ImageOps.colorize(src, black='#271002', white='#FAF8F1')
W, H = duo.size
fx, fy = 0.5, 0.47  # punto di fuga del corridoio
tagli = {'3x1': 3/1, '4x3': 4/3, '16x9': 16/9, '16x7': 16/7}
for nome, r in tagli.items():
    if W / H > r:
        h = H; w = int(h * r)
    else:
        w = W; h = int(w / r)
    x = min(max(int(fx * W - w / 2), 0), W - w)
    y = min(max(int(fy * H - h / 2), 0), H - h)
    c = duo.crop((x, y, x + w, y + h))
    for lw in (390, 780, 1200):
        if lw > w: continue
        im = c.resize((lw, round(lw / r)), Image.LANCZOS)
        for ext, kw in (('avif', {'quality': 50}), ('webp', {'quality': 72})):
            p = os.path.join(d, f'sanita-{nome}-{lw}.{ext}')
            im.save(p, **kw)
            print(f'{nome} {lw} {ext} {os.path.getsize(p)//1024} KB')
