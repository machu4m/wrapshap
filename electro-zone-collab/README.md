# Wrapshap × Electro Zone Sialkot: launch post

A square social post (1080 × 1080 px) announcing Wrapshap at Electro Zone, Sialkot. It is rebuilt from the supplied
reference image as editable artwork.

| File | Use |
|---|---|
| `wrapshap-x-electrozone-sialkot-post.ai` | Edit in Illustrator. The artboard is 1080 × 1080 (pt = px) |
| `wrapshap-x-electrozone-sialkot-post.pdf` | The same artwork as a PDF, for sharing or printing (fonts embedded) |
| `wrapshap-x-electrozone-sialkot-post-1080px.png` | Ready to post (Instagram / Facebook / WhatsApp) |
| `wrapshap-x-electrozone-sialkot-post-2160px.png` | The same post at 2×, for sharper uploads or screens |
| `fonts/` | Montserrat and Permanent Marker (free, SIL Open Font License). Install them before editing text |
| `links/` | The photos placed in the post, as separate PNGs, so you can see what each one is or replace it |

## What is editable

- **Text is live**: the headlines, store name, finish cards, device labels and "PREMIUM DEVICE PROTECTION".
  Install the fonts in `fonts/` first, or Illustrator will substitute another font.
- **Vector**: the Wrapshap logo (the original artwork, unchanged), the Electro Zone wordmark and lightning "o",
  the ×, the location pin, the four finish icons, the cards and panels, the yellow "NOW AVAILABLE AT" brush and
  the swoosh. The yellow grunge background is a single traced vector shape, so you can recolour it in one click.
- **Photos (raster images)**: the store front, the phone with the peeling film and the five device images in the
  bottom row. These were cut from the reference image, so they are only about 1,250 px wide in total. They are
  sharp at 1080 px but soft for large prints.

## Before you post

- **Replace the store photo.** The store front in the reference is AI-generated. The posters in the window are
  unreadable gibberish and the shop sign says SAMSUNG. Swap in a real photo of Electro Zone if you have one.
- **Fixed typo**: "SMARTHONES" in the reference is now "SMARTPHONES".
- The **®** next to the Wrapshap logo is kept from the reference. Remove it if the mark is not registered yet.
- The Wrapshap logo is the brand's real logo. It is not the orange 3D version shown in the reference.
- The Electro Zone wordmark is redrawn in Montserrat ExtraBold. If the store has an official logo file, place it
  over this one.

## Rebuilding

The source is in `source/collab/`. You need Python 3 (PyMuPDF, Pillow, NumPy, SciPy, potracer) and Node with Playwright.
Run `grunge.py` → `trace.py` → `assets.py` → `layout.py` → `node render.mjs` → `export.py`.
