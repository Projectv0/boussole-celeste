"""Les vignettes des douze énergies : la constellation en filets, ses étoiles, le glyphe dessous.

    python3 outils/vignettes.py   → donnees/vignettes.json (SVG compacts, sans couleur fixe)
                                     .cache/vignettes.svg (planche de contrôle)

Chaque vignette est un SVG de 100 × 120 qui hérite des couleurs de la page par des variables
CSS : --filet (traits), --etoile (étoiles), --glyphe. Aucune image matricielle : tout tient
en quelques centaines d'octets par signe, et rien ne bloque le premier affichage.
"""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))
from constellations import ORDRE, projeter  # noqa: E402
from glyphes import GLYPHES  # noqa: E402


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def vignette(signe, glyphe=True):
    pts, traits = projeter(signe, 100, 88, 0.1)
    lignes = " ".join(f"M{f(xa)} {f(ya)}L{f(xb)} {f(yb)}" for xa, ya, xb, yb in traits)
    etoiles = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(0.9 + 2.3 * r)}"/>' for x, y, r in pts.values())
    bas = (f'<g transform="translate(41 94) scale(.75)" fill="none" stroke="var(--glyphe,currentColor)" '
           f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="{GLYPHES[signe]}"/></g>'
           if glyphe else "")
    hauteur = 120 if glyphe else 92
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 {hauteur}" aria-hidden="true">'
            f'<path d="{lignes}" fill="none" stroke="var(--filet,currentColor)" stroke-width="1" '
            f'stroke-linecap="round" opacity=".7"/>'
            f'<g fill="var(--etoile,currentColor)">{etoiles}</g>{bas}</svg>')


if __name__ == "__main__":
    data = {s: vignette(s) for s in ORDRE}
    (RACINE / "donnees" / "vignettes.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    taille = sum(len(v) for v in data.values())
    cases = "".join(
        f'<g transform="translate({20 + (k % 6) * 125},{20 + (k // 6) * 150})">'
        f'<rect width="115" height="140" rx="16" fill="#1F2849"/>'
        f'<svg x="7" y="8" width="100" height="120" viewBox="0 0 100 120" '
        f'style="--filet:#D4B06A;--etoile:#F2EBDD;--glyphe:#D4B06A">{v[v.index(">") + 1:-6]}</svg></g>'
        for k, v in enumerate(data.values()))
    page = (f'<svg xmlns="http://www.w3.org/2000/svg" width="780" height="330"><rect width="780" height="330" '
            f'fill="#141A31"/>{cases}</svg>')
    (RACINE / ".cache").mkdir(exist_ok=True)
    (RACINE / ".cache" / "vignettes.svg").write_text(page)
    print(f"12 vignettes · {taille} octets en tout")
