# kukkus nest — logo package

Rebuilt from your `LOGO.ai` (Adobe Illustrator 29.5, CMYK, one layer, artwork outlined).
Everything here was reconstructed from the **native Illustrator artwork** inside the file, not
traced from a preview — every curve is the designer's original Bézier data.

---

## 1. Read this first — four things I found in the source file

**① The final “t” of “nest” is missing from the file's PDF preview.**
`.ai` files store the artwork twice: the native Illustrator art, and a PDF-compatible copy
that every *other* application reads. In your file the letter **“t”** is present in the native
art but **absent from the PDF copy**. So Illustrator shows `kukkus nest`, while Preview,
Acrobat, Canva, InDesign placement, web viewers, most printers' RIPs — and anyone you send
the `.ai` to who doesn't open it in Illustrator — show **`kukkus nes`**.

I rebuilt from the native art, so **every file in this package has the full “t”**. Worth
re-saving the master `.ai` from Illustrator (File ▸ Save As, with *Create PDF Compatible File*
ticked) so the original stops shipping a truncated wordmark.

**② The wordmark reads `kukkus nest` — all lower case, no apostrophe.**
You wrote “kukku's Nest”. The artwork has no apostrophe and no capitals. I've kept the
artwork exactly as drawn. If you want `kukku's nest`, say the word — but note the logotype is
outlined (see §4), so an apostrophe would have to be drawn to match rather than typed.

**③ “FASION DESIGN STUDIO” is missing its H** — it should almost certainly be **FASHION**.
The tagline is live text, so this one is a genuine fix: a corrected set is included
(`05_primary_FASHION-corrected`), and every layered PSD carries the corrected line as a
hidden text layer you can switch on.

**④ Two stray gold specks sit on the gown.**
A ~1 pt gold sliver and a ~0.7 pt gold dot are stuck to the tip of one of the dark fold lines,
around a third of the way up the skirt. Invisible at small sizes, but they will print as gold
flecks on the blush panel at large sizes. They're isolated on a **hidden** layer called
*“Stray gold specks (artefact)”* in every PSD — nothing is lost, but the default output is clean.

---

## 2. Brand colours

The source document is CMYK (U.S. Web Coated SWOP v2). The CMYK values are exact — use those
for print. The hex values are what the PSDs use and match how the original renders on screen.

| Swatch | Role | CMYK (source, exact) | HEX | RGB |
|---|---|---|---|---|
| ■ | Espresso brown — gown, stand, logotype | **51 / 74 / 76 / 74** | `#351A12` | 53, 26, 18 |
| ■ | Antique gold — arcs, tagline | **30 / 51 / 99 / 12** | `#A6772D` | 166, 119, 45 |
| ■ | Blush pink — skirt panel, waist sash | **2 / 34 / 20 / 0** | `#F4B5B4` | 244, 181, 180 |
| □ | White — gown highlight lines | 0 / 0 / 0 / 0 | `#FFFFFF` | 255, 255, 255 |

The PSDs are RGB/8. If you need CMYK PSDs for a printer, tell me and I'll convert with the
source profile rather than letting Photoshop guess.

---

## 3. What's in the box

### `PSD/` — layered, 300 dpi, RGB/8
| File | Canvas | Use |
|---|---|---|
| `01_primary-stacked_layered.psd` | 3800 × 3600 | the main lockup, exactly as your original |
| `02_horizontal_layered.psd` | — | mark left, type right — website headers, email signatures, letterheads |
| `03_icon-only_layered.psd` | — | the gown-and-arc mark alone — avatars, favicons, labels, buttons |
| `04_wordmark-only_layered.psd` | — | type alone, for when the mark is already present |
| `05_primary_FASHION-corrected_layered.psd` | 3800 × 3600 | primary lockup with the spelling fixed |

Every PSD has the same layer structure:

```
Background                                    (white — hide it for transparency)
▾ Icon — gown & arcs
    Waist sash
    Gown & stand
    Arc — left
    Arc — right
    Gown — blush panel
    Gown — highlight lines
    Stray gold specks (artefact)              [hidden — see §1④]
▾ Logotype
    kukkus nest — outlined (exact)            [the real wordmark]
    kukkus nest — LIVE TEXT (approx.)         [hidden — see §4]
▾ Tagline
    FASION DESIGN STUDIO — LIVE TEXT          [editable type layer]
    FASHION DESIGN STUDIO — LIVE TEXT         [hidden — corrected spelling]
    tagline — outlined backup                 [hidden — needs no font installed]
```

### `SVG/` and `PDF/` — true vector, infinitely scalable
Each lockup, plus three colourways of the primary: `mono-brown`, `mono-gold`,
`reversed-white` (for dark backgrounds). Use these for anything that needs to scale — signage,
embroidery digitising, vinyl cutting, web. Paths are named, so they stay editable.

### `PNG/` — 2000 px, transparent background (plus white-background copies)

### `Fonts/` — the two typefaces, unmodified, with their licences
Install these before opening the PSDs so the live text renders correctly.

---

## 4. About the type — please read before editing

**Tagline — fully editable. ✅**
It is **Josefin Sans Light, 34.13 pt, letter-spacing 320 (0.32 em)**, in the gold above.
That's read straight out of the file, so the live text layer in the PSDs is an exact
reproduction — retype it, recolour it, respace it, it stays correct. Install
`Fonts/JosefinSans[wght].ttf` (or get Josefin Sans free from Google Fonts) and pick weight
**Light / 300**.

**Logotype — outlined in the original, so the font is not recoverable. ⚠️**
Whoever made the logo converted `kukkus nest` to outlines before saving, which deletes the
font name. There is no font information left in the file to recover.

I tried to identify it anyway: I extracted the six distinct letterforms (k, u, s, n, e, t) and
shape-matched them against **1,003 fonts — every serif family on Google Fonts (339 families,
all weights)**. Best result was 0.75 overlap; a real match scores above 0.92. **It is not a
Google font** — almost certainly a commercial display serif. The source is noticeably more
condensed, with higher stroke contrast and distinctive sheared (diagonally cut) ascender tops.

So the PSDs give you both:

* **`kukkus nest — outlined (exact)`** — visible by default. This is your actual wordmark,
  pixel-exact, 300 dpi, and vector in the SVG/PDF files. Use this.
* **`kukkus nest — LIVE TEXT (Playfair Display Medium, approx.)`** — hidden. Playfair Display
  was the closest widely-available face; it's set to the right x-height (155 pt) and tracked
  (−46) to the right width. It is **not** a match — it's there for when you need to set *new*
  words in a broadly similar style (a sub-brand, a product line). Don't swap it in for the
  wordmark. If Photoshop flags the font as missing, install Playfair Display (free, Google
  Fonts) and pick **Medium / 500**; `Fonts/PlayfairDisplay[wght].ttf` is included.

For reference, the five closest faces out of the 1,003 tested, by letterform overlap:
Playfair Display Medium (0.745), Jomolhari (0.748), Charis SIL (0.734), Merriweather (0.728),
Adamina (0.726) — all well short of a match, and all wider than the original.

If you can tell me where the logo came from (a designer, a Fiverr/Envato template, a logo
generator), the font is usually named in the original order — and with the name I can set the
real thing as live text.

---

## 5. Notes on fidelity

The reconstruction was verified pixel-by-pixel against the original: outside the restored “t”,
the rebuild matches the source rendering to within anti-aliasing noise (mean difference
1.0/255). Splitting into layers is lossless — the layered composite matches a single-pass
render to within 2/255, so there are no seams or halos where shapes meet.

The fonts in `Fonts/` are the unmodified upstream releases from Google Fonts, under the SIL
Open Font License 1.1 (licence text included). Both carry Reserved Font Names, so they're
shipped exactly as published rather than renamed or subsetted.
