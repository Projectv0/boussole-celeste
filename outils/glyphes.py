"""Les douze glyphes des signes, dessinés en traits SVG (grille 24 × 24, trait rond).

Les caractères Unicode ♈ … ♓ s'affichent en émoji violets sur iPhone et sur beaucoup
d'Android : on ne les utilise donc jamais à l'écran. Ces tracés servent au site (vignettes,
roue, antisèche), aux cartes à partager et aux icônes.

    python3 outils/glyphes.py   → .cache/glyphes.svg, planche de contrôle
"""
GLYPHES = {
    "belier":     ("M12 21V10.5 M12 10.5C12 6.2 9.6 3.5 6.9 3.5 4.7 3.5 3 5.2 3 7.4 3 9.3 4.4 10.8 6.3 10.8"
                   " M12 10.5C12 6.2 14.4 3.5 17.1 3.5 19.3 3.5 21 5.2 21 7.4 21 9.3 19.6 10.8 17.7 10.8"),
    "taureau":    ("M3.5 3.5C4.5 7.6 7.8 10.2 12 10.2S19.5 7.6 20.5 3.5"
                   " M12 10.2A5.2 5.2 0 1 0 12 20.6A5.2 5.2 0 1 0 12 10.2"),
    "gemeaux":    "M4.5 4C9.2 5.6 14.8 5.6 19.5 4 M4.5 20C9.2 18.4 14.8 18.4 19.5 20 M9 5.1V18.9 M15 5.1V18.9",
    "cancer":     ("M4 9.2A2.6 2.6 0 1 0 9.2 9.2A2.6 2.6 0 1 0 4 9.2 M6.6 6.6C10.4 3.9 16.6 4 21 7.6"
                   " M20 14.8A2.6 2.6 0 1 0 14.8 14.8A2.6 2.6 0 1 0 20 14.8 M17.4 17.4C13.6 20.1 7.4 20 3 16.4"),
    "lion":       ("M4.4 15.6A3.1 3.1 0 1 0 10.6 15.6A3.1 3.1 0 1 0 4.4 15.6"
                   " M10.6 15.6C10.6 11 8.6 8.6 8.6 6.4 8.6 4.3 10.4 2.8 12.7 2.8 15.1 2.8 16.9 4.5 16.9 6.8"
                   " 16.9 10.6 13.6 12.8 13.6 16.6 13.6 19.3 15.2 21 17.4 21 19.2 21 20.4 19.9 20.8 18.6"),
    "vierge":     ("M3 6.4C4 5.2 5.8 5.4 5.8 7.4V18 M5.8 8.4C5.8 6.3 7.2 5 8.8 5S11.8 6.3 11.8 8.4V18"
                   " M11.8 8.4C11.8 6.3 13.2 5 14.8 5S17.8 6.3 17.8 8.4V14.2C17.8 17.4 19.2 19.6 21 20.6"
                   " M17.8 13.6C17 17 15 19.6 12.6 21"),
    "balance":    ("M3 19.5H21 M3 15.2H8.4C7.2 14.1 6.6 12.6 6.6 11 6.6 8 9 5.6 12 5.6S17.4 8 17.4 11"
                   "C17.4 12.6 16.8 14.1 15.6 15.2H21"),
    "scorpion":   ("M3 6.4C4 5.2 5.8 5.4 5.8 7.4V18 M5.8 8.4C5.8 6.3 7.2 5 8.8 5S11.8 6.3 11.8 8.4V18"
                   " M11.8 8.4C11.8 6.3 13.2 5 14.8 5S17.8 6.3 17.8 8.4V17.2C17.8 18.6 18.7 19.5 20.1 19.5H21.4"
                   " M19.2 17.2L21.5 19.5 19.2 21.8"),
    "sagittaire": "M4 20L20 4 M12.5 4H20V11.5 M6.8 11.6L12.4 17.2",
    "capricorne": ("M3 5.6C4.3 4.6 5.8 5.2 6.3 6.7L9.6 18.4 13.1 7.6C13.8 5.4 15.2 4.3 16.9 4.3"
                   " 18.9 4.3 20.4 5.9 20.4 8V15 M20.4 15C20.4 18.2 18.9 20.6 16.9 20.6 15.2 20.6 14.1 19.4"
                   " 14.1 17.9 14.1 16.3 15.4 15.1 17 15.1 18.4 15.1 19.6 15.8 20.4 15"),
    "verseau":    ("M3 10.4L6 7.6 9 10.4 12 7.6 15 10.4 18 7.6 21 10.4"
                   " M3 16.6L6 13.8 9 16.6 12 13.8 15 16.6 18 13.8 21 16.6"),
    "poissons":   ("M5.5 3.5C8.9 6 10.4 8.9 10.4 12S8.9 18 5.5 20.5 M18.5 3.5C15.1 6 13.6 8.9 13.6 12"
                   "S15.1 18 18.5 20.5 M4 12H20"),
}


def svg(signe, taille=24, couleur="currentColor", epaisseur=1.7):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{taille}" height="{taille}" '
            f'fill="none" stroke="{couleur}" stroke-width="{epaisseur}" stroke-linecap="round" '
            f'stroke-linejoin="round"><path d="{GLYPHES[signe]}"/></svg>')


if __name__ == "__main__":
    from pathlib import Path
    racine = Path(__file__).resolve().parent.parent
    ordre = list(GLYPHES)
    cases = "".join(
        f'<g transform="translate({40 + (k % 6) * 120},{40 + (k // 6) * 130})">'
        f'<rect width="96" height="96" rx="18" fill="#1F2849"/>'
        f'<g transform="translate(18,18) scale(2.5)" fill="none" stroke="#D4B06A" stroke-width="1.6" '
        f'stroke-linecap="round" stroke-linejoin="round"><path d="{GLYPHES[s]}"/></g>'
        f'<text x="48" y="118" fill="#F2EBDD" font-family="Helvetica" font-size="13" text-anchor="middle">{s}</text></g>'
        for k, s in enumerate(ordre))
    page = (f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="320" viewBox="0 0 760 320">'
            f'<rect width="760" height="320" fill="#141A31"/>{cases}</svg>')
    (racine / ".cache").mkdir(exist_ok=True)
    (racine / ".cache" / "glyphes.svg").write_text(page)
    print(racine / ".cache" / "glyphes.svg")
