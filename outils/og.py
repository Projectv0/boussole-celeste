"""L'image de partage des liens (og.jpg, 1200 × 630) : la roue, le nom, la promesse.

    python3 outils/og.py
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))
from constellations import ORDRE, projeter  # noqa: E402

S = 2
W, H = 1200, 630
POL = RACINE / "polices" / "ttf"
ELEM = ["feu", "terre", "air", "eau"] * 3
COUL = {"feu": (232, 121, 79), "terre": (169, 181, 101), "air": (159, 208, 236), "eau": (110, 151, 224)}
# Une roue d'exemple, pour l'image seulement : elle ne décrit personne.
NOTES = [7.8, 5.2, 4.1, 6.4, 5.6, 3.9, 6.8, 4.6, 7.1, 5.9, 3.4, 6.1]


def police(fichier, taille, poids):
    f = ImageFont.truetype(str(POL / fichier), taille * S)
    axes = f.get_variation_axes()
    f.set_variation_by_axes([poids if (a["name"] in (b"Weight", "Weight")) else a["default"] for a in axes])
    return f


def main():
    fond = Image.new("RGB", (1, H * S))
    for y in range(H * S):
        t = y / (H * S - 1)
        fond.putpixel((0, y), tuple(int(a + (b - a) * t) for a, b in zip((15, 20, 36), (26, 33, 64))))
    im = fond.resize((W * S, H * S)).convert("RGBA")
    rnd = random.Random(3)
    d = ImageDraw.Draw(im)
    for _ in range(170):
        x, y, r = rnd.uniform(0, W * S), rnd.uniform(0, H * S), rnd.choice([1, 1.2, 1.6, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(242, 235, 221, rnd.randint(50, 190)))
    cx, cy, R, r0 = 880 * S, 315 * S, 235 * S, 52 * S
    halo = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([cx - R * 1.3, cy - R * 1.3, cx + R * 1.3, cy + R * 1.3], fill=(212, 176, 106, 26))
    im = Image.alpha_composite(im, halo.filter(ImageFilter.GaussianBlur(60 * S)))
    cou = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cou)

    def secteur(k, re, ri):
        a1, a2 = -90 - 14.2 + k * 30, -90 + 14.2 + k * 30
        pts = [(cx + math.cos(math.radians(a1 + (a2 - a1) * i / 30)) * re, cy + math.sin(math.radians(a1 + (a2 - a1) * i / 30)) * re) for i in range(31)]
        pts += [(cx + math.cos(math.radians(a2 - (a2 - a1) * i / 30)) * ri, cy + math.sin(math.radians(a2 - (a2 - a1) * i / 30)) * ri) for i in range(31)]
        return pts

    for k in range(12):
        d.polygon(secteur(k, R, r0), fill=(242, 235, 221, 9))
        d.polygon(secteur(k, r0 + (R - r0) * NOTES[k] / 10, r0), fill=COUL[ELEM[k]] + (235,))
    for v in (2.5, 5, 7.5, 10):
        rv = r0 + (R - r0) * v / 10
        d.ellipse([cx - rv, cy - rv, cx + rv, cy + rv], outline=(242, 235, 221, 60 if v < 10 else 110), width=S)
    d.ellipse([cx - r0 + 6, cy - r0 + 6, cx + r0 - 6, cy + r0 - 6], fill=(31, 40, 73, 255))
    etoile = [(cx + math.cos(math.radians(k * 45 - 90)) * (24 if k % 2 == 0 else 7) * S,
               cy + math.sin(math.radians(k * 45 - 90)) * (24 if k % 2 == 0 else 7) * S) for k in range(8)]
    d.polygon(etoile, fill=(212, 176, 106, 255))
    im = Image.alpha_composite(im, cou)

    # une constellation en filigrane, à gauche
    pts, traits = projeter("lion", 300 * S, 150 * S, 0.1)
    cou = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cou)
    ox, oy = 60 * S, 40 * S
    for xa, ya, xb, yb in traits:
        d.line([ox + xa, oy + ya, ox + xb, oy + yb], fill=(212, 176, 106, 110), width=S)
    for x, y, r in pts.values():
        rr = (1.5 + 3.5 * r) * S
        d.ellipse([ox + x - rr, oy + y - rr, ox + x + rr, oy + y + rr], fill=(242, 235, 221, 220))
    im = Image.alpha_composite(im, cou)

    d = ImageDraw.Draw(im)
    d.text((70 * S, 238 * S), "Boussole céleste", font=police("CormorantGaramond[wght].ttf", 84, 600), fill=(242, 235, 221))
    d.text((72 * S, 352 * S), "Ton ciel du moment,", font=police("CormorantGaramond[wght].ttf", 40, 600), fill=(227, 198, 139))
    d.text((72 * S, 400 * S), "lu dans ce que tu vis.", font=police("CormorantGaramond[wght].ttf", 40, 600), fill=(227, 198, 139))
    d.text((72 * S, 474 * S), "16 situations · 12 énergies · aucune prédiction", font=police("Jost[wght].ttf", 22, 400), fill=(185, 183, 201))
    d.text((72 * S, 545 * S), "boussole-celeste.fr", font=police("Jost[wght].ttf", 22, 500), fill=(212, 176, 106))
    im.convert("RGB").resize((W, H), Image.LANCZOS).save(RACINE / "og.jpg", quality=88, optimize=True)
    print("og.jpg", (RACINE / "og.jpg").stat().st_size // 1024, "Ko")


if __name__ == "__main__":
    main()
