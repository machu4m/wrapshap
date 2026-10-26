"""Cut the photo elements out of the supplied reference poster (ref.webp, 1254 x 1254).

Each crop is saved as an RGBA PNG with feathered edges, placed in the layout at the
same ref coordinates it was cut from. Swap any of them for a better photo later."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'build')
ref = Image.open(os.path.join(HERE, 'ref.webp')).convert('RGB')
UP = 2                                            # upsample so feathering stays smooth


def save(name, box, mask_fn):
    x0, y0, x1, y1 = box
    im = ref.crop(box).resize(((x1 - x0) * UP, (y1 - y0) * UP), Image.LANCZOS)
    m = Image.new('L', im.size, 0)
    mask_fn(ImageDraw.Draw(m), x0, y0)
    im.putalpha(m)
    im.save(os.path.join(OUT, name + '.png'))
    print(name, box)


def ramp(size, x0, x1, y0, y1, box):
    """Alpha that fades in over [x0,x1] from the left and fades out over [y0,y1] at the bottom (ref coords)."""
    bx0, by0, bx1, by1 = box
    xs = np.linspace(bx0, bx1, size[0]); ys = np.linspace(by0, by1, size[1])
    ax = np.clip((xs - x0) / (x1 - x0), 0, 1); ay = np.clip((y1 - ys) / (y1 - y0), 0, 1)
    top = np.clip((ys - by0) / 14, 0, 1)
    a = np.outer(ay * top, ax)
    return Image.fromarray((a ** 1.2 * 255).astype(np.uint8))


# store front: fades in from the left (under the banner) and out at the bottom (under the tagline)
SHOP = (585, 212, 1254, 705)
im = ref.crop(SHOP).resize(((SHOP[2] - SHOP[0]) * UP, (SHOP[3] - SHOP[1]) * UP), Image.LANCZOS)
im.putalpha(ramp(im.size, 585, 640, 640, 705, SHOP))
im.save(os.path.join(OUT, 'shop.png'))

# phone with the peeling film: hand-drawn outline, feathered
PHONE = (30, 465, 680, 910)
PHONE_POLY = [(46, 548), (62, 508), (98, 484), (140, 476), (210, 486), (300, 507), (380, 532),
              (414, 543), (436, 555), (470, 590), (505, 640), (540, 690), (590, 725), (640, 722),
              (660, 742), (660, 800), (640, 806), (590, 790), (560, 800), (600, 860), (612, 910),
              (232, 910), (150, 760), (70, 620)]


def phone_mask(d, x0, y0):
    d.polygon([((x - x0) * UP, (y - y0) * UP) for x, y in PHONE_POLY], fill=255)


save('phone', PHONE, phone_mask)
p = Image.open(os.path.join(OUT, 'phone.png'))
a = p.getchannel('A').filter(ImageFilter.GaussianBlur(5 * UP))
p.putalpha(a); p.save(os.path.join(OUT, 'phone.png'))

# device row: each on the black panel, soft rectangle edge
DEVICES = {'dev-phone': (88, 1040, 206, 1176), 'dev-tablet': (300, 1040, 452, 1174),
           'dev-laptop': (548, 1056, 724, 1166), 'dev-watch': (806, 1040, 922, 1174),
           'dev-earbuds': (1044, 1046, 1160, 1162)}
for name, (x0, y0, x1, y1) in DEVICES.items():
    def soft(d, bx, by, w=x1 - x0, h=y1 - y0):
        d.rounded_rectangle([6 * UP, 6 * UP, (w - 6) * UP, (h - 6) * UP], radius=10 * UP, fill=255)
    save(name, (x0, y0, x1, y1), soft)
    q = Image.open(os.path.join(OUT, name + '.png'))
    q.putalpha(q.getchannel('A').filter(ImageFilter.GaussianBlur(3 * UP)))
    q.save(os.path.join(OUT, name + '.png'))
