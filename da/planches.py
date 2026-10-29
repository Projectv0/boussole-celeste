"""Les trois planches de direction artistique (1 600 × 1 000), rendues avec PIL.

Chaque planche montre trois écrans de téléphone — l'accueil, une situation du test, la page
de résultats — dans un thème : nuit étoilée, aube dorée, observatoire. La colonne de gauche
donne les couleurs, les polices et les contrastes, calculés (formule WCAG 2), pas estimés.

    python3 da/planches.py        → da/planche-1-nuit.png, -2-aube.png, -3-observatoire.png
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))
from constellations import ORDRE, projeter  # noqa: E402

S = 2                      # rendu à 2×, puis réduit : c'est ce qui lisse les traits
W, H = 1600, 1000
POL = RACINE / "polices" / "ttf"
SYMB = "/System/Library/Fonts/Apple Symbols.ttf"
NOM = "Boussole céleste"   # nom provisoire, le temps que Martial choisisse

GLYPHES = dict(zip(ORDRE, "♈♉♊♋♌♍♎♏♐♑♒♓"))
VERBES = dict(zip(ORDRE, ["oser", "ancrer", "relier", "protéger", "rayonner", "affiner",
                          "équilibrer", "transformer", "explorer", "bâtir", "libérer", "ressentir"]))
SIGNES = dict(zip(ORDRE, ["Bélier", "Taureau", "Gémeaux", "Cancer", "Lion", "Vierge",
                          "Balance", "Scorpion", "Sagittaire", "Capricorne", "Verseau", "Poissons"]))
ELEMENT = dict(zip(ORDRE, ["feu", "terre", "air", "eau"] * 3))

# Un profil d'exemple : le Scorpion n'a pas été mesuré (aucune note, jamais un zéro).
NOTES = {"belier": 8.2, "taureau": 4.1, "gemeaux": 3.0, "cancer": 2.4, "lion": 5.0,
         "vierge": 3.6, "balance": 2.0, "scorpion": None, "sagittaire": 4.4,
         "capricorne": 7.1, "verseau": 2.8, "poissons": 1.6}
MESURES = {"belier": 7, "capricorne": 6, "lion": 6}

THEMES = [
    dict(cle="nuit", nom="Nuit étoilée", num=1,
         desc="Fond encre de nuit, cartes bleu nuit, texte ivoire lunaire, accents or et cuivre, "
              "bleu glacier pour les liens. Constellations en filets fins, étoiles en points, "
              "croissant de lune dans le héros, grain de film discret.",
         fond=("#0F1424", "#1A2140"), carte="#1F2849", bord=(242, 235, 221, 26),
         texte="#F2EBDD", doux="#B9B7C9", accent="#D4B06A", accent2="#C68B5E", lien="#9CCBE0",
         btn="#D4B06A", btn_t="#141A30", filet=(212, 176, 106), etoile=(242, 235, 221),
         sel_fond="#D4B06A", sel_t="#141A30",
         titre=("CormorantGaramond[wght].ttf", 600), texte_p=("Jost[wght].ttf", 400),
         polices=("Cormorant Garamond", "Jost"), echelle_titre=1.12,
         elements={"feu": "#E8794F", "terre": "#A9B565", "air": "#9FD0EC", "eau": "#5D8BDB"},
         sombre=True, grain=14, motif="lune"),
    dict(cle="aube", nom="Aube dorée", num=2,
         desc="Fond ivoire chaud, encre bleu nuit pour le texte, accents or et bleu lavande. "
              "Les mêmes constellations, en filets bleu nuit sur fond clair, et une lueur dorée "
              "en haut de page. La plus proche de Boussole en lisibilité.",
         fond=("#FBF6EC", "#F4E9D4"), carte="#FFFDF8", bord=(27, 33, 64, 30),
         texte="#1B2140", doux="#474E6E", accent="#8A6420", accent2="#6F7CC6", lien="#3A4BA3",
         btn="#1B2140", btn_t="#FBF6EC", filet=(27, 33, 64), etoile=(27, 33, 64),
         sel_fond="#1B2140", sel_t="#FBF6EC",
         titre=("Fraunces[SOFT,WONK,opsz,wght].ttf", 560), texte_p=("Manrope[wght].ttf", 450),
         polices=("Fraunces", "Manrope"), echelle_titre=1.0,
         elements={"feu": "#D35A30", "terre": "#76862F", "air": "#4E9ACB", "eau": "#2D58A6"},
         sombre=False, grain=7, motif="aube"),
    dict(cle="observatoire", nom="Observatoire", num=3,
         desc="Fond gris-bleu profond, cuivre et vert-de-gris. Un astrolabe en filigrane, des "
              "graduations d'instrument, plus « cabinet de curiosités ». Le plus singulier des "
              "trois, et le plus éloigné de Boussole.",
         fond=("#1C262E", "#26333D"), carte="#2C3A45", bord=(236, 229, 216, 24),
         texte="#ECE5D8", doux="#BEC5C3", accent="#DC9C6E", accent2="#79B0A2", lien="#8FC7BA",
         btn="#C9875A", btn_t="#1A232A", filet=(201, 135, 90), etoile=(236, 229, 216),
         sel_fond="#79B0A2", sel_t="#152026",
         titre=("PlayfairDisplay[wght].ttf", 600), texte_p=("PlusJakartaSans[wght].ttf", 400),
         polices=("Playfair Display", "Plus Jakarta Sans"), echelle_titre=0.94,
         elements={"feu": "#E07A52", "terre": "#AEB46C", "air": "#9CC9D9", "eau": "#6693CC"},
         sombre=True, grain=12, motif="astrolabe"),
]


# ─── outils ────────────────────────────────────────────────────────────────────

def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(h):
    c = [x / 255 for x in rgb(h)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


_cache = {}


def police(fichier, taille, poids=None):
    cle = (fichier, taille, poids)
    if cle not in _cache:
        chemin = fichier if fichier.startswith("/") else str(POL / fichier)
        f = ImageFont.truetype(chemin, int(round(taille * S)))
        if poids is not None:
            axes = f.get_variation_axes()
            vals = []
            for a in axes:
                n = a["name"].decode() if isinstance(a["name"], bytes) else a["name"]
                if n == "Weight":
                    vals.append(max(a["minimum"], min(a["maximum"], poids)))
                elif n == "Optical Size":
                    vals.append(max(a["minimum"], min(a["maximum"], taille)))
                elif n == "Wonky":
                    vals.append(0)
                elif n == "Softness":
                    vals.append(30)
                else:
                    vals.append(a["default"])
            f.set_variation_by_axes(vals)
        _cache[cle] = f
    return _cache[cle]


def T(th, taille, poids=None, titre=False):
    fichier, p = th["titre"] if titre else th["texte_p"]
    if titre:
        taille *= th["echelle_titre"]
    return police(fichier, taille, poids or p)


def typo(t):
    """Espace insécable avant les ponctuations hautes, comme en typographie française."""
    for p_ in (" :", " ?", " !", " ;", " »"):
        t = t.replace(p_, "\u00a0" + p_[1])
    return t.replace("« ", "«\u00a0")


def couper(d, texte, f, largeur):
    mots, lignes, cour = typo(texte).split(" "), [], ""
    for m in mots:
        essai = (cour + " " + m).strip()
        if d.textlength(essai, font=f) <= largeur * S or not cour:
            cour = essai
        else:
            lignes.append(cour)
            cour = m
    if cour:
        lignes.append(cour)
    return lignes


def ecrire(d, x, y, texte, f, coul, largeur=None, interligne=1.38, espace=0):
    """Écrit (en coordonnées logiques) et renvoie le y logique sous le texte."""
    taille = f.size / S
    lignes = couper(d, texte, f, largeur) if largeur else [typo(texte)]
    for ligne in lignes:
        if espace:
            cx = x * S
            for ch in ligne:
                d.text((cx, y * S), ch, font=f, fill=coul)
                cx += d.textlength(ch, font=f) + espace * S
        else:
            d.text((x * S, y * S), ligne, font=f, fill=coul)
        y += taille * interligne
    return y


def largeur(d, texte, f, espace=0):
    return (d.textlength(texte, font=f) + espace * S * max(0, len(texte) - 1)) / S


def rr(d, box, r, fill=None, outline=None, w=1):
    d.rounded_rectangle([v * S for v in box], radius=r * S, fill=fill,
                        outline=outline, width=max(1, int(w * S)))


def degrade(w, h, haut, bas):
    a, b = rgb(haut), rgb(bas)
    col = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        col.putpixel((0, y), tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    return col.resize((w, h)).convert("RGBA")


def grain(img, force, graine):
    if not force:
        return img
    rnd = random.Random(graine)
    w, h = img.size[0] // 2, img.size[1] // 2
    bruit = Image.frombytes("L", (w, h), bytes(rnd.randrange(256) for _ in range(w * h)))
    bruit = bruit.resize(img.size)
    couche = Image.merge("RGBA", (bruit, bruit, bruit, Image.new("L", img.size, force)))
    return Image.alpha_composite(img, couche)


def ciel(img, th, n, graine, zone=None):
    """Semis d'étoiles en points."""
    rnd = random.Random(graine)
    cou = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cou)
    x0, y0, x1, y1 = zone or (0, 0, img.size[0] / S, img.size[1] / S)
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.choice([0.5, 0.6, 0.7, 0.8, 1.0, 1.3])
        a = int(rnd.uniform(0.25, 0.85 if th["sombre"] else 0.35) * 255)
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=th["etoile"] + (a,))
    return Image.alpha_composite(img, cou)


def constellation(img, th, signe, box, alpha_trait=0.55, alpha_etoile=0.95, epais=0.8, taille=2.6):
    x0, y0, x1, y1 = box
    pts, traits = projeter(signe, (x1 - x0) * S, (y1 - y0) * S, 0.08)
    cou = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cou)
    for xa, ya, xb, yb in traits:
        d.line([x0 * S + xa, y0 * S + ya, x0 * S + xb, y0 * S + yb],
               fill=th["filet"] + (int(alpha_trait * 255),), width=max(1, int(epais * S)))
    for x, y, r in pts.values():
        rr_ = (0.9 + taille * r) * S
        cx, cy = x0 * S + x, y0 * S + y
        if th["sombre"]:
            halo = rr_ * 2.6
            d.ellipse([cx - halo, cy - halo, cx + halo, cy + halo], fill=th["etoile"] + (28,))
        d.ellipse([cx - rr_, cy - rr_, cx + rr_, cy + rr_], fill=th["etoile"] + (int(alpha_etoile * 255),))
    return Image.alpha_composite(img, cou)


def lune(img, th, cx, cy, r):
    cou = Image.new("RGBA", img.size, (0, 0, 0, 0))
    lueur = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lueur).ellipse([(cx - r * 2.2) * S, (cy - r * 2.2) * S, (cx + r * 2.2) * S,
                                   (cy + r * 2.2) * S], fill=rgb(th["accent"]) + (40,))
    lueur = lueur.filter(ImageFilter.GaussianBlur(r * S * 0.9))
    masque = Image.new("L", img.size, 0)
    dm = ImageDraw.Draw(masque)
    dm.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=255)
    dm.ellipse([(cx - r * 0.55) * S, (cy - r * 1.12) * S, (cx + r * 1.35) * S, (cy + r * 0.78) * S], fill=0)
    plein = Image.new("RGBA", img.size, rgb("#F4E7C6") + (255,) if th["sombre"] else rgb(th["accent"]) + (255,))
    cou.paste(plein, (0, 0), masque)
    return Image.alpha_composite(Image.alpha_composite(img, lueur), cou)


def astrolabe(img, th, cx, cy, r, alpha=0.32):
    cou = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cou)
    c = th["filet"] + (int(alpha * 255),)
    fin = max(1, int(0.8 * S))
    for k in (1.0, 0.93, 0.72, 0.38):
        d.ellipse([(cx - r * k) * S, (cy - r * k) * S, (cx + r * k) * S, (cy + r * k) * S], outline=c, width=fin)
    for a in range(0, 360, 5):
        t = math.radians(a)
        long_ = 0.86 if a % 30 == 0 else 0.9
        d.line([(cx + math.cos(t) * r * long_) * S, (cy + math.sin(t) * r * long_) * S,
                (cx + math.cos(t) * r * 0.93) * S, (cy + math.sin(t) * r * 0.93) * S], fill=c, width=fin)
    # le cercle de l'écliptique, excentré, et l'alidade
    d.ellipse([(cx - r * 0.62 + r * 0.12) * S, (cy - r * 0.62 - r * 0.08) * S,
               (cx + r * 0.62 + r * 0.12) * S, (cy + r * 0.62 - r * 0.08) * S], outline=c, width=fin)
    t = math.radians(-28)
    d.line([(cx - math.cos(t) * r) * S, (cy - math.sin(t) * r) * S,
            (cx + math.cos(t) * r) * S, (cy + math.sin(t) * r) * S], fill=c, width=int(1.6 * S))
    for a in (0, 90, 180, 270):
        t = math.radians(a)
        d.line([(cx + math.cos(t) * r * 0.38) * S, (cy + math.sin(t) * r * 0.38) * S,
                (cx + math.cos(t) * r * 0.72) * S, (cy + math.sin(t) * r * 0.72) * S], fill=c, width=fin)
    return Image.alpha_composite(img, cou)


def logo(img, th, cx, cy, r):
    """Le logo provisoire : une petite roue à douze rayons et une étoile."""
    cou = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cou)
    c = rgb(th["accent"]) + (255,)
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], outline=c, width=int(1.3 * S))
    for k in range(12):
        t = math.radians(k * 30 - 90)
        d.line([(cx + math.cos(t) * r * 0.62) * S, (cy + math.sin(t) * r * 0.62) * S,
                (cx + math.cos(t) * r) * S, (cy + math.sin(t) * r) * S], fill=c, width=int(1 * S))
    pts = []
    for k in range(8):
        t = math.radians(k * 45 - 90)
        rk = r * (0.5 if k % 2 == 0 else 0.16)
        pts.append(((cx + math.cos(t) * rk) * S, (cy + math.sin(t) * rk) * S))
    d.polygon(pts, fill=c)
    return Image.alpha_composite(img, cou)


def barre_etat(d, th, w):
    f = T(th, 11, 600)
    d.text((22 * S, 12 * S), "9:41", font=f, fill=th["texte"])
    x = w - 24
    for k, h in enumerate((4, 6, 8, 10)):
        d.rectangle([(x - 44 + k * 5) * S, (22 - h) * S, (x - 41 + k * 5) * S, 22 * S], fill=th["texte"])
    rr(d, (x - 20, 13, x, 22), 2.5, outline=th["texte"], w=1)
    rr(d, (x - 18, 15, x - 6, 20), 1.2, fill=th["texte"])


def nav(img, th, w):
    img = logo(img, th, 28, 52, 10)
    d = ImageDraw.Draw(img)
    d.text((46 * S, 41 * S), NOM, font=T(th, 18, titre=True), fill=th["texte"])
    for k in range(3):
        rr(d, (w - 38, 46 + k * 6, w - 20, 47.4 + k * 6), 0.7, fill=th["texte"])
    return img


# ─── les trois écrans ──────────────────────────────────────────────────────────

def ecran_accueil(th, w, h):
    img = degrade(w * S, h * S, *th["fond"])
    if th["motif"] == "aube":
        lueur = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lueur).ellipse([(w * 0.15) * S, -h * 0.25 * S, (w * 1.25) * S, h * 0.32 * S],
                                      fill=rgb("#F2C879") + (120,))
        img = Image.alpha_composite(img, lueur.filter(ImageFilter.GaussianBlur(60 * S)))
    img = ciel(img, th, 60, 3, (0, 70, w, 228))
    if th["motif"] == "astrolabe":
        img = astrolabe(img, th, w - 70, 150, 118, 0.34)
    img = constellation(img, th, "lion", (120, 78, w - 14, 238), 0.5, 0.9)
    if th["motif"] in ("lune", "aube"):
        img = lune(img, th, w - 64, 104, 24)
    d = ImageDraw.Draw(img)
    barre_etat(d, th, w)
    img = nav(img, th, w)
    d = ImageDraw.Draw(img)
    y = ecrire(d, 22, 236, "SE COMPRENDRE PAR LE CIEL", T(th, 10.5, 600), th["accent"], espace=1.6)
    y = ecrire(d, 22, y + 8, "Ton ciel du moment, lu dans ce que tu vis.", T(th, 31, titre=True),
               th["texte"], largeur=w - 44, interligne=1.12)
    y = ecrire(d, 22, y + 10, "Douze énergies, une par signe. Seize scènes du quotidien mesurent la "
               "place que chacune prend dans ta vie en ce moment. Rien n'est prédit : tout part de toi.",
               T(th, 13.5), th["doux"], largeur=w - 44, interligne=1.5)
    y += 14
    rr(d, (22, y, w - 22, y + 48), 24, fill=th["btn"])
    f = T(th, 15, 600)
    t = "Commencer le test"
    d.text(((w / 2 - largeur(d, t, f) / 2) * S, (y + 14) * S), t, font=f, fill=th["btn_t"])
    y = ecrire(d, 22, y + 60, "16 situations · environ 10 minutes", T(th, 12, 500), th["doux"])
    y = ecrire(d, 22, y, "Tes réponses restent dans ton navigateur.", T(th, 12), th["doux"])
    y += 24
    y = ecrire(d, 22, y, "Le déroulé en quatre temps", T(th, 21, titre=True), th["texte"])
    etapes = [("1", "Découvrir", "Les douze énergies, ce que chacune apporte."),
              ("2", "Partir du réel", "Jusqu'à cinq moments vécus, si tu veux."),
              ("3", "Se projeter", "Seize scènes, des réactions à noter.")]
    y += 8
    for n, titre, texte in etapes:
        lignes = couper(d, texte, T(th, 12), w - 22 - 76 - 12)
        hc = 44 + 17 * len(lignes)
        rr(d, (22, y, w - 22, y + hc), 16, fill=th["carte"], outline=th["bord"], w=1)
        d.ellipse([34 * S, (y + hc / 2 - 14) * S, 62 * S, (y + hc / 2 + 14) * S], outline=th["accent"], width=int(1.2 * S))
        fn = T(th, 14, titre=True)
        d.text(((48 - largeur(d, n, fn) / 2) * S, (y + hc / 2 - 10) * S), n, font=fn, fill=th["accent"])
        d.text((76 * S, (y + 12) * S), titre, font=T(th, 14, 600), fill=th["texte"])
        ecrire(d, 76, y + 32, texte, T(th, 12), th["doux"], largeur=w - 22 - 76 - 12, interligne=1.4)
        y += hc + 10
    return grain(img, th["grain"], 11)


def ecran_situation(th, w, h):
    img = degrade(w * S, h * S, *th["fond"])
    img = ciel(img, th, 14, 5, (110, 84, w, 112))
    if th["motif"] == "astrolabe":
        img = astrolabe(img, th, w + 20, 40, 90, 0.18)
    d = ImageDraw.Draw(img)
    barre_etat(d, th, w)
    d.text((22 * S, 42 * S), "‹ Retour", font=T(th, 13), fill=th["doux"])
    t = "Situation 5 sur 16"
    f = T(th, 13, 500)
    d.text(((w - 22 - largeur(d, t, f)) * S, 42 * S), t, font=f, fill=th["doux"])
    rr(d, (22, 68, w - 22, 72), 2, fill=th["bord"][:3] + (60,) if th["sombre"] else th["bord"][:3] + (40,))
    rr(d, (22, 68, 22 + (w - 44) * 5 / 16, 72), 2, fill=th["accent"])
    f = T(th, 10, 600)
    t = "TRAVAIL"
    lw = largeur(d, t, f, 1.4)
    rr(d, (22, 88, 22 + lw + 22, 110), 11, outline=th["accent"], w=1)
    ecrire(d, 33, 93.5, t, f, th["accent"], espace=1.4)
    y = ecrire(d, 22, 124, "Ta responsable annonce un nouveau projet en réunion, sans dire qui le "
               "pilotera. Un silence s'installe. Chacun regarde la table.",
               T(th, 20, titre=True), th["texte"], largeur=w - 44, interligne=1.24)
    y = ecrire(d, 22, y + 8, "À quel point chaque réaction te ressemble ?", T(th, 12.5), th["doux"])
    reactions = [("Tu te proposes avant même d'avoir fini de réfléchir.", 3),
                 ("Tu demandes d'abord le calendrier et les moyens prévus.", 2),
                 ("Tu regardes qui, autour de la table, a l'air inquiet.", None)]
    crans = ["Pas du tout", "Un peu", "Moyennement", "Beaucoup", "Énormément"]
    y += 10
    fp = T(th, 11.5, 500)
    for texte, choix in reactions:
        lignes = couper(d, texte, T(th, 14, 500), w - 72)
        # disposition des pastilles, en retour à la ligne comme un flex-wrap
        rangs, cour, lx = [], [], 0
        for k, c in enumerate(crans):
            pw = largeur(d, c, fp) + 20
            if cour and lx + pw > w - 72:
                rangs.append(cour)
                cour, lx = [], 0
            cour.append((k, c, pw))
            lx += pw + 6
        rangs.append(cour)
        hc = 16 + len(lignes) * 19 + 10 + len(rangs) * 32 + 8
        rr(d, (22, y, w - 22, y + hc), 18, fill=th["carte"], outline=th["bord"], w=1)
        yy = ecrire(d, 36, y + 14, texte, T(th, 14, 500), th["texte"], largeur=w - 72, interligne=1.36)
        yy += 8
        for rang in rangs:
            xx = 36
            for k, c, pw in rang:
                sel = choix == k
                rr(d, (xx, yy, xx + pw, yy + 26), 13, fill=th["sel_fond"] if sel else None,
                   outline=th["sel_fond"] if sel else th["bord"][:3] + (110,), w=1)
                d.text(((xx + 10) * S, (yy + 5.5) * S), c, font=fp, fill=th["sel_t"] if sel else th["doux"])
                xx += pw + 6
            yy += 32
        y += hc + 10
    # barre du bas
    yb = h - 56
    d.text((22 * S, (yb + 14) * S), "Tout à « pas du tout »", font=T(th, 12.5, 500), fill=th["lien"])
    rr(d, (w - 132, yb, w - 22, yb + 44), 22, fill=th["btn"])
    f = T(th, 14, 600)
    d.text(((w - 77 - largeur(d, "Suivante", f) / 2) * S, (yb + 12) * S), "Suivante", font=f, fill=th["btn_t"])
    return grain(img, th["grain"], 12)


def roue(img, th, cx, cy, R):
    """La roue zodiacale : Bélier en haut, sens horaire, secteurs remplis selon la note."""
    cou = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cou)
    r0 = R * 0.24
    elem = {e: (sum(NOTES[s] for s in ORDRE if ELEMENT[s] == e and NOTES[s] is not None) /
                max(1, sum(1 for s in ORDRE if ELEMENT[s] == e and NOTES[s] is not None)))
            for e in ("feu", "terre", "air", "eau")}
    dominant = max(elem, key=elem.get)

    def secteur(k, r_ext, r_int, ecart=1.6):
        a1, a2 = -90 - 15 + k * 30 + ecart / 2, -90 + 15 + k * 30 - ecart / 2
        pts = []
        for i in range(25):
            t = math.radians(a1 + (a2 - a1) * i / 24)
            pts.append(((cx + math.cos(t) * r_ext) * S, (cy + math.sin(t) * r_ext) * S))
        for i in range(25):
            t = math.radians(a2 - (a2 - a1) * i / 24)
            pts.append(((cx + math.cos(t) * r_int) * S, (cy + math.sin(t) * r_int) * S))
        return pts

    # anneaux de lecture (2,5 · 5 · 7,5 · 10)
    for v in (2.5, 5, 7.5, 10):
        rv = r0 + (R - r0) * v / 10
        d.ellipse([(cx - rv) * S, (cy - rv) * S, (cx + rv) * S, (cy + rv) * S],
                  outline=th["bord"][:3] + (55 if v < 10 else 90,), width=max(1, int(0.7 * S)))
    for k, s in enumerate(ORDRE):
        c = rgb(th["elements"][ELEMENT[s]])
        d.polygon(secteur(k, R, r0), fill=th["bord"][:3] + (22 if th["sombre"] else 16,))
        n = NOTES[s]
        if n is None:
            # pas mesurée : un secteur en pointillés, jamais un zéro
            for i in range(0, 25, 3):
                t = math.radians(-90 - 13 + k * 30 + 26 * i / 24)
                rm = r0 + (R - r0) * 0.5
                d.ellipse([(cx + math.cos(t) * rm - 0.9) * S, (cy + math.sin(t) * rm - 0.9) * S,
                           (cx + math.cos(t) * rm + 0.9) * S, (cy + math.sin(t) * rm + 0.9) * S],
                          fill=rgb(th["doux"]) + (200,))
            continue
        d.polygon(secteur(k, r0 + (R - r0) * n / 10, r0), fill=c + (235,))
    # arc doré sur l'élément dominant
    for k, s in enumerate(ORDRE):
        if ELEMENT[s] == dominant:
            a1, a2 = -90 - 14 + k * 30, -90 + 14 + k * 30
            ra = R + 5
            d.arc([(cx - ra) * S, (cy - ra) * S, (cx + ra) * S, (cy + ra) * S], a1, a2,
                  fill=rgb(th["accent"]) + (255,), width=int(2.2 * S))
    d.ellipse([(cx - r0 + 3) * S, (cy - r0 + 3) * S, (cx + r0 - 3) * S, (cy + r0 - 3) * S],
              fill=rgb(th["carte"]) + (255,), outline=th["bord"][:3] + (120,), width=int(0.8 * S))
    img = Image.alpha_composite(img, cou)
    img = logo(img, th, cx, cy, r0 * 0.55)
    d = ImageDraw.Draw(img)
    fg = police(SYMB, 13)
    for k, s in enumerate(ORDRE):
        t = math.radians(-90 + k * 30)
        rg = R + 17
        g = GLYPHES[s]
        bw = d.textbbox((0, 0), g, font=fg)
        gx = (cx + math.cos(t) * rg) * S - (bw[2] - bw[0]) / 2 - bw[0]
        gy = (cy + math.sin(t) * rg) * S - (bw[3] - bw[1]) / 2 - bw[1]
        d.text((gx, gy), g, font=fg, fill=th["elements"][ELEMENT[s]] if NOTES[s] is not None else th["doux"])
    return img, elem, dominant


def ecran_resultats(th, w, h):
    img = degrade(w * S, h * S, *th["fond"])
    img = ciel(img, th, 40, 7, (0, 180, w, 470))
    d = ImageDraw.Draw(img)
    barre_etat(d, th, w)
    y = ecrire(d, 22, 42, "TON CIEL DU MOMENT", T(th, 10.5, 600), th["accent"], espace=1.6)
    y = ecrire(d, 22, y + 4, "Le feu qui bâtit", T(th, 31, titre=True), th["texte"])
    y = ecrire(d, 22, y + 4, "Oser et bâtir prennent le plus de place en ce moment : tu lances, puis tu "
               "construis. C'est une saison, pas une identité.", T(th, 13), th["doux"],
               largeur=w - 44, interligne=1.48)
    img, elem, dom = roue(img, th, w / 2, y + 146, 112)
    d = ImageDraw.Draw(img)
    y += 290
    noms = {"feu": "Feu · agir", "terre": "Terre · concrétiser", "air": "Air · relier", "eau": "Eau · ressentir"}
    for e in ("feu", "terre", "air", "eau"):
        c = th["elements"][e]
        d.ellipse([22 * S, (y + 4) * S, 32 * S, (y + 14) * S], fill=c)
        f = T(th, 12, 600 if e == dom else 450)
        d.text((40 * S, y * S), noms[e], font=f, fill=th["texte"] if e == dom else th["doux"])
        bx0, bx1 = 168, w - 58
        rr(d, (bx0, y + 6, bx1, y + 12), 3, fill=th["bord"][:3] + (70,))
        rr(d, (bx0, y + 6, bx0 + (bx1 - bx0) * elem[e] / 10, y + 12), 3, fill=c)
        v = f"{elem[e]:.1f}".replace(".", ",")
        d.text(((w - 22 - largeur(d, v, f)) * S, y * S), v, font=f, fill=th["texte"] if e == dom else th["doux"])
        y += 23
    y += 10
    tri = sorted([s for s in ORDRE if NOTES[s] is not None], key=lambda s: -NOTES[s])[:3]
    for k, s in enumerate(tri):
        rr(d, (22, y, w - 22, y + 44), 14, fill=th["carte"], outline=th["bord"], w=1)
        fn = T(th, 18, titre=True)
        d.text((36 * S, (y + 10) * S), str(k + 1), font=fn, fill=th["accent"])
        d.text((60 * S, (y + 7) * S), VERBES[s].capitalize(), font=T(th, 14, 600), fill=th["texte"])
        d.text((60 * S, (y + 25) * S), f"{SIGNES[s]} · {MESURES.get(s, 5)} mesures", font=T(th, 11), fill=th["doux"])
        v = f"{NOTES[s]:.1f}".replace(".", ",")
        f = T(th, 18, titre=True)
        d.text(((w - 56 - largeur(d, v, f)) * S, (y + 10) * S), v, font=f, fill=th["texte"])
        d.text(((w - 52) * S, (y + 17) * S), "/10", font=T(th, 11), fill=th["doux"])
        y += 50
    ecrire(d, 22, y + 4, "Un langage pour réfléchir à toi, pas une prédiction.", T(th, 11), th["doux"])
    return grain(img, th["grain"], 13)


# ─── la planche ────────────────────────────────────────────────────────────────

def telephone(planche, ecran, x, y):
    w, h = ecran.size[0] // S, ecran.size[1] // S
    b = 8
    cou = Image.new("RGBA", planche.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cou)
    ombre = Image.new("RGBA", planche.size, (0, 0, 0, 0))
    ImageDraw.Draw(ombre).rounded_rectangle([(x - b + 6) * S, (y - b + 16) * S, (x + w + b + 6) * S,
                                            (y + h + b + 22) * S], radius=48 * S, fill=(0, 0, 0, 90))
    planche = Image.alpha_composite(planche, ombre.filter(ImageFilter.GaussianBlur(18 * S)))
    d.rounded_rectangle([(x - b) * S, (y - b) * S, (x + w + b) * S, (y + h + b) * S],
                        radius=46 * S, fill=(10, 12, 20, 255))
    planche = Image.alpha_composite(planche, cou)
    masque = Image.new("L", ecran.size, 0)
    ImageDraw.Draw(masque).rounded_rectangle([0, 0, ecran.size[0], ecran.size[1]], radius=38 * S, fill=255)
    planche.paste(ecran, (x * S, y * S), masque)
    d = ImageDraw.Draw(planche)
    d.rounded_rectangle([(x + w / 2 - 44) * S, (y + 8) * S, (x + w / 2 + 44) * S, (y + 30) * S],
                        radius=11 * S, fill=(10, 12, 20, 255))
    return planche


def planche(th):
    img = degrade(W * S, H * S, *th["fond"])
    img = ciel(img, th, 200 if th["sombre"] else 90, th["num"], (410, 0, W, H))
    img = ciel(img, th, 40 if th["sombre"] else 18, th["num"] + 7, (0, 690, 410, H - 50))
    if th["motif"] == "astrolabe":
        img = astrolabe(img, th, 210, 850, 250, 0.2)
    else:
        img = constellation(img, th, "scorpion", (60, 700, 380, 950), 0.26, 0.6, 0.7, 2)
    d = ImageDraw.Draw(img)
    x0 = 56
    y = ecrire(d, x0, 70, f"PLANCHE {th['num']} SUR 3", T(th, 11, 600), th["accent"], espace=2)
    y = ecrire(d, x0, y + 6, th["nom"], T(th, 46, titre=True), th["texte"], interligne=1.1)
    y = ecrire(d, x0, y + 8, th["desc"], T(th, 13.5), th["doux"], largeur=330, interligne=1.5)

    y += 18
    y = ecrire(d, x0, y, "COULEURS", T(th, 10, 600), th["accent"], espace=1.6)
    nuancier = [("Fond", th["fond"][1]), ("Carte", th["carte"]), ("Texte", th["texte"]),
                ("Texte doux", th["doux"]), ("Accent", th["accent"]), ("Second accent", th["accent2"]),
                ("Lien", th["lien"])]
    y += 6
    for k, (n, c) in enumerate(nuancier):
        cx, cy = x0 + (k % 2) * 168, y + (k // 2) * 30
        rr(d, (cx, cy, cx + 22, cy + 22), 6, fill=c, outline=th["bord"][:3] + (140,), w=1)
        d.text(((cx + 30) * S, (cy + 1) * S), n, font=T(th, 11.5, 600), fill=th["texte"])
        d.text(((cx + 30) * S, (cy + 13) * S), c.upper(), font=T(th, 9.5), fill=th["doux"])
    y += 4 * 30 + 10
    y = ecrire(d, x0, y, "CONTRASTES, CALCULÉS", T(th, 10, 600), th["accent"], espace=1.6)
    paires = [("Texte sur fond", th["texte"], th["fond"][1], 7),
              ("Texte sur carte", th["texte"], th["carte"], 7),
              ("Texte doux sur carte", th["doux"], th["carte"], 4.5),
              ("Accent sur carte", th["accent"], th["carte"], 4.5),
              ("Lien sur fond", th["lien"], th["fond"][1], 4.5),
              ("Bouton", th["btn_t"], th["btn"], 4.5)]
    y += 4
    for n, a, b, mini in paires:
        c = contraste(a, b)
        niveau = "AAA" if c >= 7 else "AA" if c >= 4.5 else "ÉCHEC"
        assert c >= mini, f"{th['nom']} — {n} : {c:.2f} < {mini}"
        d.text((x0 * S, y * S), n, font=T(th, 12), fill=th["doux"])
        v = f"{c:.1f}:1 · {niveau}".replace(".", ",", 1)
        f = T(th, 12, 600)
        d.text(((x0 + 330 - largeur(d, v, f)) * S, y * S), v, font=f, fill=th["texte"])
        y += 19
    y += 12
    y = ecrire(d, x0, y, "POLICES", T(th, 10, 600), th["accent"], espace=1.6)
    y = ecrire(d, x0, y + 4, th["polices"][0], T(th, 24, titre=True), th["texte"])
    y = ecrire(d, x0, y, th["polices"][1] + " — le texte courant, très lisible", T(th, 13), th["doux"])
    y += 12
    y = ecrire(d, x0, y, "ÉLÉMENTS", T(th, 10, 600), th["accent"], espace=1.6)
    y += 6
    xx = x0
    for e, n in (("feu", "Feu"), ("terre", "Terre"), ("air", "Air"), ("eau", "Eau")):
        d.ellipse([xx * S, y * S, (xx + 14) * S, (y + 14) * S], fill=th["elements"][e])
        d.text(((xx + 20) * S, (y - 1) * S), n, font=T(th, 12, 500), fill=th["texte"])
        xx += 80

    ew, eh = 340, 780
    xs = [1600 - 56 - 3 * (ew + 16) - 2 * 24 + 8 + k * (ew + 16 + 24) for k in range(3)]
    legendes = ["L'accueil", "Une situation du test", "Tes résultats"]
    ecrans = [ecran_accueil(th, ew, eh), ecran_situation(th, ew, eh), ecran_resultats(th, ew, eh)]
    for k, (x, e) in enumerate(zip(xs, ecrans)):
        d = ImageDraw.Draw(img)
        f = T(th, 12, 600)
        d.text(((x + ew / 2 - largeur(d, legendes[k], f) / 2) * S, 84 * S), legendes[k], font=f, fill=th["doux"])
        img = telephone(img, e, x, 116)
    d = ImageDraw.Draw(img)
    note = f"Nom provisoire sur les écrans : « {NOM} ». Glyphes des signes : dessinés en SVG sur le site."
    d.text((x0 * S, (H - 34) * S), note, font=T(th, 10.5), fill=th["doux"])
    img = grain(img, th["grain"] // 2, 99)
    return img.convert("RGB").resize((W, H), Image.LANCZOS)


if __name__ == "__main__":
    for th in THEMES:
        sortie = RACINE / "da" / f"planche-{th['num']}-{th['cle']}.png"
        planche(th).save(sortie, optimize=True)
        print(sortie.relative_to(RACINE))
