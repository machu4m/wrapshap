"""Trace the grunge mask to one compound vector path (SVG path data in ref coords)."""
import os, sys, time
import numpy as np
import potrace
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SCALE = 2
m = np.array(Image.open(os.path.join(HERE, 'build', 'grunge_mask.png'))) > 127
t = time.time()
bm = potrace.Bitmap(~m)                    # potracer traces the False pixels
plist = bm.trace(turdsize=6, alphamax=1.0, opticurve=True, opttolerance=0.3)
f = lambda p: '%.1f %.1f' % (p.x / SCALE, p.y / SCALE)
parts = []
for c in plist:
    s = ['M' + f(c.start_point)]
    for seg in c.segments:
        if seg.is_corner:
            s.append('L' + f(seg.c) + 'L' + f(seg.end_point))
        else:
            s.append('C' + f(seg.c1) + ' ' + f(seg.c2) + ' ' + f(seg.end_point))
    parts.append(''.join(s) + 'Z')
open(os.path.join(HERE, 'build', 'grunge_path.txt'), 'w').write(''.join(parts))
print('traced', len(plist), 'curves in %.0fs' % (time.time() - t), sum(map(len, parts)) // 1024, 'KB')
