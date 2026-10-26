"""Yellow dry-brush grunge for the Electro Zone collab post, as a 1-bit mask (ref coords 1254 x 1254).

Streaks are anisotropic noise thresholded against a density map, plus paint splatter.
Fixed seed, so the result is repeatable. Writes grunge_mask.png at SCALE x."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
N, SCALE, SEED = 1254, 2, 7
W = N * SCALE
rng = np.random.default_rng(SEED)
yy, xx = np.mgrid[0:W, 0:W] / SCALE                 # ref-pixel coordinates


def blob(cx, cy, rx, ry, ang, w=1.0):
    """Soft elliptical density patch, rotated (degrees)."""
    a = np.deg2rad(ang)
    u = ((xx - cx) * np.cos(a) + (yy - cy) * np.sin(a)) / rx
    v = (-(xx - cx) * np.sin(a) + (yy - cy) * np.cos(a)) / ry
    return w * np.exp(-(u * u + v * v) ** 1.6)


# where the paint goes (strokes run lower-left -> upper-right, about -35 degrees)
D = (blob(60, 95, 210, 55, -30) + blob(60, 300, 220, 50, -35, .9)
     + blob(120, 650, 200, 300, -60) + blob(40, 980, 130, 260, -60, .9)
     + blob(1250, 215, 150, 50, -40, .9) + blob(1230, 420, 90, 260, -70, .8)
     + blob(1190, 1000, 270, 105, -30) + blob(1245, 610, 70, 110, -45, .6)
     + blob(520, 905, 230, 55, -25, .5) + blob(470, 560, 120, 90, -35, .6)
     + blob(120, 1000, 200, 45, -20, .55))
D = np.clip(D, 0, 1.2)

# streaky noise: white noise blurred long along the stroke direction, short across it
noise = rng.standard_normal((W, W)).astype(np.float32)
ang = -35
n1 = ndi.gaussian_filter(noise, (1.2 * SCALE, 1.2 * SCALE))
n1 = ndi.rotate(n1, ang, reshape=False, order=1, mode='wrap')
n1 = ndi.gaussian_filter1d(n1, 14 * SCALE, axis=1)
n1 = ndi.rotate(n1, -ang, reshape=False, order=1, mode='wrap')
n1 = (n1 - n1.mean()) / n1.std()
n2 = ndi.gaussian_filter(rng.standard_normal((W, W)).astype(np.float32), 9 * SCALE)
n2 = (n2 - n2.mean()) / n2.std()
field = D * 1.45 + 0.30 * n1 + 0.20 * n2
mask = field > 0.98

# splatter around the painted areas
img = Image.fromarray((mask * 255).astype(np.uint8))
dr = ImageDraw.Draw(img)
edge = (D > 0.15) & (D < 0.6)
ys, xs = np.nonzero(edge[::4, ::4])
for i in rng.choice(len(xs), 1600, replace=False):
    x, y = xs[i] * 4 + rng.normal(0, 30 * SCALE), ys[i] * 4 + rng.normal(0, 30 * SCALE)
    r = SCALE * (0.8 + rng.pareto(2.6) * 1.6)
    r = min(r, 9 * SCALE)
    dr.ellipse([x - r, y - r, x + r, y + r], fill=255)
    if r > 3 * SCALE and rng.random() < .35:            # small trailing drop
        a = np.deg2rad(rng.uniform(0, 360)); d = r * rng.uniform(1.6, 2.6)
        r2 = r * .45
        dr.ellipse([x + d * np.cos(a) - r2, y + d * np.sin(a) - r2, x + d * np.cos(a) + r2, y + d * np.sin(a) + r2], fill=255)
m = np.array(img) > 127
m = ndi.binary_opening(m, iterations=1)
Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(HERE, 'build', 'grunge_mask.png'))
print('grunge done', m.mean())
