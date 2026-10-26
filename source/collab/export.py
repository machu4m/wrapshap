"""Place the original vector logo and write the deliverables:
.ai (PDF-compatible Illustrator file), .pdf, and PNGs at 1080 and 2160 px."""
import json, os, shutil
import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, 'build')
OUT = os.path.abspath(os.path.join(HERE, '..', '..', 'electro-zone-collab'))
NAME = 'wrapshap-x-electrozone-sialkot-post'
PX = 0.75                                          # CSS px -> PDF pt

doc = fitz.open(os.path.join(B, 'raw.pdf'))
pg = doc[0]
logo = fitz.open(os.path.join(HERE, '..', 'logo.pdf'))
for s in json.load(open(os.path.join(B, 'slots.json'))):
    r = fitz.Rect(s['x'] * PX, s['y'] * PX, (s['x'] + s['w']) * PX, (s['y'] + s['h']) * PX)
    pg.show_pdf_page(r, logo, 0, keep_proportion=True)
doc.set_metadata({'title': 'Wrapshap x Electro Zone Sialkot', 'author': 'Wrapshap',
                  'creator': 'Wrapshap visual system v1.0', 'subject': 'Retail launch post, 1080 x 1080'})
os.makedirs(OUT, exist_ok=True)
pdf = os.path.join(OUT, NAME + '.pdf')
doc.save(pdf, garbage=3, deflate=True)
shutil.copyfile(pdf, os.path.join(OUT, NAME + '.ai'))
for px in (1080, 2160):
    pix = fitz.open(pdf)[0].get_pixmap(matrix=fitz.Matrix(px / 1080, px / 1080))
    pix.save(os.path.join(OUT, f'{NAME}-{px}px.png'))
links = os.path.join(OUT, 'links')                   # the placed photos, for swapping
os.makedirs(links, exist_ok=True)
for n in ('shop', 'phone', 'dev-phone', 'dev-tablet', 'dev-laptop', 'dev-watch', 'dev-earbuds'):
    shutil.copyfile(os.path.join(B, n + '.png'), os.path.join(links, n + '.png'))
print('exported to', OUT)
