"""Les icônes de l'application et le logo des réseaux, tirés de la même roue que le site.

    python3 outils/icones.py   → icone-192.png, icone-512.png, icone-maskable-512.png,
                                  apple-touch-icon.png (180), favicon.svg, logo-instagram.png (1080)

La roue : douze rayons courts sur un cercle d'or, une étoile à huit branches au centre,
sur le fond encre de nuit du thème. L'icône « maskable » garde tout le dessin dans la zone
sûre (80 % du diamètre), puisque Android la découpe en cercle, en carré ou en goutte.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

RACINE = Path(__file__).resolve().parent.parent
FOND_HAUT, FOND_BAS = (15, 20, 36), (26, 33, 64)
OR = (212, 176, 106)
IVOIRE = (242, 235, 221)


def fond(n):
    im = Image.new("RGB", (1, n))
    for y in range(n):
        t = y / (n - 1)
        im.putpixel((0, y), tuple(int(a + (b - a) * t) for a, b in zip(FOND_HAUT, FOND_BAS)))
    return im.resize((n, n)).convert("RGBA")


def roue(n, echelle=1.0, etoiles=True):
    """Dessine à 4× puis réduit : c'est ce qui lisse les traits."""
    S = 4
    N = n * S
    im = fond(N)
    if etoiles:
        rnd = random.Random(5)
        d = ImageDraw.Draw(im)
        for _ in range(int(n / 6)):
            x, y = rnd.uniform(0, N), rnd.uniform(0, N)
            r = rnd.choice([0.6, 0.8, 1.0, 1.3]) * N / 512
            d.ellipse([x - r, y - r, x + r, y + r], fill=IVOIRE + (rnd.randint(60, 170),))
    c = N / 2
    R = N * 0.30 * echelle
    halo = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([c - R * 1.5, c - R * 1.5, c + R * 1.5, c + R * 1.5], fill=OR + (34,))
    im = Image.alpha_composite(im, halo.filter(ImageFilter.GaussianBlur(R * 0.45)))
    d = ImageDraw.Draw(im)
    w = max(2, int(N * 0.018 * echelle))
    d.ellipse([c - R, c - R, c + R, c + R], outline=OR, width=w)
    for k in range(12):
        t = math.radians(k * 30 - 90)
        d.line([c + math.cos(t) * R * 0.66, c + math.sin(t) * R * 0.66, c + math.cos(t) * R, c + math.sin(t) * R],
               fill=OR, width=max(2, int(w * 0.8)))
    pts = []
    for k in range(16):
        t = math.radians(k * 22.5 - 90)
        rk = R * (0.5 if k % 4 == 0 else 0.3 if k % 2 == 0 else 0.11)
        pts.append((c + math.cos(t) * rk, c + math.sin(t) * rk))
    d.polygon(pts, fill=IVOIRE)
    return im.resize((n, n), Image.LANCZOS)


def favicon_svg():
    rayons = "".join(
        f'<path d="M{16 + math.cos(math.radians(k * 30 - 90)) * 7.6:.2f} {16 + math.sin(math.radians(k * 30 - 90)) * 7.6:.2f}'
        f'L{16 + math.cos(math.radians(k * 30 - 90)) * 11.5:.2f} {16 + math.sin(math.radians(k * 30 - 90)) * 11.5:.2f}"/>'
        for k in range(12))
    etoile = " ".join(
        f"{16 + math.cos(math.radians(k * 45 - 90)) * (5.4 if k % 2 == 0 else 1.6):.2f},"
        f"{16 + math.sin(math.radians(k * 45 - 90)) * (5.4 if k % 2 == 0 else 1.6):.2f}" for k in range(8))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" '
            'fill="#141A31"/><g fill="none" stroke="#D4B06A" stroke-width="1.6" stroke-linecap="round">'
            f'<circle cx="16" cy="16" r="11.5"/>{rayons}</g><polygon fill="#F2EBDD" points="{etoile}"/></svg>\n')


if __name__ == "__main__":
    roue(192).convert("RGB").save(RACINE / "icone-192.png", optimize=True)
    roue(512).convert("RGB").save(RACINE / "icone-512.png", optimize=True)
    roue(512, echelle=0.78, etoiles=False).convert("RGB").save(RACINE / "icone-maskable-512.png", optimize=True)
    roue(180).convert("RGB").save(RACINE / "apple-touch-icon.png", optimize=True)
    roue(1080, echelle=1.05).convert("RGB").save(RACINE / "logo-instagram.png", optimize=True)
    (RACINE / "favicon.svg").write_text(favicon_svg())
    for f in ("icone-192.png", "icone-512.png", "icone-maskable-512.png", "apple-touch-icon.png",
              "logo-instagram.png", "favicon.svg"):
        print(f, (RACINE / f).stat().st_size, "octets")
