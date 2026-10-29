"""Assemble le site : un seul index.html, autonome, à partir de site/ et de donnees/.

    python3 outils/construire.py        → index.html, sw.js

Les textes ne s'écrivent que dans donnees/ ; le style, les vues et le code dans site/.
Ce script les réunit, convertit la typographie (apostrophe courbe, espace insécable
avant : ; ! ? »), dessine les décors en SVG, et refuse de produire une page qui
contiendrait le mot interdit ou une apostrophe droite dans un texte.

Le numéro de version (site/VERSION) nomme le cache du service worker et se lit dans
la page (<meta name="version">) : c'est le marqueur unique qui permet de vérifier en
ligne qu'un déploiement est bien arrivé.
"""
import html
import json
import random
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "donnees"))
sys.path.insert(0, str(RACINE / "outils"))
import energies as E  # noqa: E402
import lectures as L  # noqa: E402
import situations as S  # noqa: E402
from constellations import ORDRE, projeter  # noqa: E402
from glyphes import GLYPHES  # noqa: E402
from vignettes import vignette  # noqa: E402

SITE = "https://boussole-celeste.fr/"
# Tant que le domaine n'est pas branché, le site vit sur projectv0.github.io : on demande
# aux moteurs de ne pas l'indexer là, pour ne pas créer un doublon du futur domaine.
INDEXABLE = (RACINE / "CNAME").exists()
VERSION = int((RACINE / "site" / "VERSION").read_text().strip())


def typo(t):
    t = t.replace("'", "’")
    t = re.sub(r" ([:;!?»])", " \\1", t)
    return t.replace("« ", "« ")


def profond(o):
    if isinstance(o, str):
        return typo(o)
    if isinstance(o, dict):
        return {k: profond(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [profond(v) for v in o]
    return o


def js(nom, valeur):
    texte = json.dumps(valeur, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"const {nom} = {texte};"


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


# ─── décors en SVG ─────────────────────────────────────────────────────────────

def logo_svg():
    import math
    angles = [math.radians(k * 30 - 90) for k in range(12)]
    rayons = "".join(f'<path d="M{f(16 + math.cos(a) * 8.2)} {f(16 + math.sin(a) * 8.2)}'
                     f'L{f(16 + math.cos(a) * 12.5)} {f(16 + math.sin(a) * 12.5)}"/>' for a in angles)
    etoile = " ".join(f"{f(16 + math.cos(math.radians(k * 45 - 90)) * (6 if k % 2 == 0 else 1.8))},"
                      f"{f(16 + math.sin(math.radians(k * 45 - 90)) * (6 if k % 2 == 0 else 1.8))}" for k in range(8))
    return ('<svg viewBox="0 0 32 32" aria-hidden="true"><g fill="none" style="stroke:var(--or)" stroke-width="1.5" '
            f'stroke-linecap="round"><circle cx="16" cy="16" r="12.5"/>{rayons}</g>'
            f'<polygon style="fill:var(--ink)" points="{etoile}"/></svg>')


def hero_svg():
    pts, traits = projeter("lion", 300, 170, 0.1)
    ox, oy = 30, 40
    lignes = "".join(f'<path d="M{f(ox + xa)} {f(oy + ya)}L{f(ox + xb)} {f(oy + yb)}"/>' for xa, ya, xb, yb in traits)
    etoiles = "".join(f'<circle cx="{f(ox + x)}" cy="{f(oy + y)}" r="{f(1.2 + 2.6 * r)}"/>' for x, y, r in pts.values())
    rnd = random.Random(4)
    poussiere = "".join(f'<circle cx="{f(rnd.uniform(0, 400))}" cy="{f(rnd.uniform(0, 230))}" r="{f(rnd.choice([.5, .7, .9, 1.1]))}" '
                        f'opacity="{f(rnd.uniform(.25, .8))}"/>' for _ in range(46))
    return ('<svg class="hero-ciel reveal" viewBox="0 0 400 230" aria-hidden="true">'
            '<defs><radialGradient id="halo"><stop offset="0" stop-color="#D4B06A" stop-opacity=".35"/>'
            '<stop offset="1" stop-color="#D4B06A" stop-opacity="0"/></radialGradient>'
            '<mask id="croissant"><rect width="400" height="230" fill="#fff"/><circle cx="330" cy="54" r="30" fill="#000"/></mask></defs>'
            f'<g style="fill:var(--ink)">{poussiere}</g>'
            '<circle cx="316" cy="66" r="70" fill="url(#halo)"/>'
            '<circle cx="316" cy="66" r="32" fill="#F4E7C6" mask="url(#croissant)"/>'
            f'<g fill="none" style="stroke:var(--or)" stroke-width="1" opacity=".75" stroke-linecap="round">{lignes}</g>'
            f'<g style="fill:var(--ink)">{etoiles}</g></svg>')


def roulette_svg():
    import math
    s = ""
    for k, e in enumerate(E.ENERGIES):
        a1, a2 = math.radians(-90 - 14 + k * 30), math.radians(-90 + 14 + k * 30)
        r = 46
        s += (f'<path d="M50 50L{f(50 + math.cos(a1) * r)} {f(50 + math.sin(a1) * r)}A{r} {r} 0 0 1 '
              f'{f(50 + math.cos(a2) * r)} {f(50 + math.sin(a2) * r)}Z" style="fill:var(--{e["element"]})" opacity=".85"/>')
    return (f'<svg viewBox="0 0 100 100" aria-hidden="true">{s}<circle cx="50" cy="50" r="13" style="fill:var(--card)"/>'
            '<circle cx="50" cy="50" r="4" style="fill:var(--or)"/></svg>')


def fond_etoiles():
    rnd = random.Random(11)
    points = "".join(f'<circle cx="{f(rnd.uniform(0, 620))}" cy="{f(rnd.uniform(0, 620))}" r="{f(rnd.choice([.5, .6, .7, .9, 1.1]))}" '
                     f'fill-opacity="{f(rnd.uniform(.18, .7))}"/>' for _ in range(70))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="620" height="620"><g fill="#F2EBDD">{points}</g></svg>'


def carte_du_ciel(signes, graine):
    """Une colonne de carte céleste : graduations, et quelques constellations en filigrane."""
    rnd = random.Random(graine)
    w, h = 480, 1500
    s = ""
    for k in range(1, 7):
        s += f'<circle cx="{-200 if graine % 2 else w + 200}" cy="750" r="{k * 170}" fill="none" stroke="#D4B06A" stroke-opacity=".12"/>'
    for k in range(9):
        y = 90 + k * 165
        s += f'<path d="M0 {y}L{w} {y + rnd.uniform(-40, 40):.0f}" stroke="#D4B06A" stroke-opacity=".07" stroke-dasharray="2 8"/>'
    for k, signe in enumerate(signes):
        pts, traits = projeter(signe, 300, 220, 0.1)
        ox, oy = rnd.uniform(40, 150), 60 + k * 240
        s += "".join(f'<path d="M{f(ox + xa)} {f(oy + ya)}L{f(ox + xb)} {f(oy + yb)}" stroke="#D4B06A" stroke-opacity=".38"/>'
                     for xa, ya, xb, yb in traits)
        s += "".join(f'<circle cx="{f(ox + x)}" cy="{f(oy + y)}" r="{f(1 + 2.2 * r)}" fill="#F2EBDD" fill-opacity=".7"/>'
                     for x, y, r in pts.values())
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{s}</svg>'


def url_svg(svg):
    return 'url("data:image/svg+xml,' + quote(svg, safe=" =:/,.-#()'") .replace('"', "'") + '")'


# ─── assemblage ───────────────────────────────────────────────────────────────

def donnees():
    rot = json.loads((RACINE / "donnees" / "rotations.json").read_text())
    energies = []
    for e in E.ENERGIES:
        e = {k: v for k, v in e.items() if k != "glyphe"}   # le caractère Unicode n'est jamais affiché
        energies.append(e)
    situations = [{"dom": s["dom"], "txt": s["txt"], "reac": [list(r) for r in s["reac"]]} for s in S.SITUATIONS]
    morceaux = [
        js("ENERGIES", profond(energies)),
        js("ELEMENTS", profond(E.ELEMENTS)),
        js("MODALITES", profond(E.MODALITES)),
        js("SITUATIONS", profond(situations)),
        js("ROTATIONS", rot),
        js("CROISEMENTS", profond(L.CROISEMENTS)),
        js("CIELS", profond([{**c, "elements": list(c["elements"])} for c in L.CIELS])),
        js("CIEL_FIN", typo(L.CIEL_FIN)),
        js("CIEL_PLANCHER", L.CIEL_PLANCHER),
        js("CIEL_ELEMENT", profond(L.CIEL_ELEMENT)),
        js("CIEL_PARTAGE", profond(L.CIEL_PARTAGE)),
        js("CIEL_VOILE", profond(L.CIEL_VOILE)),
        js("LEVIERS", profond(L.LEVIERS)),
        js("PLAN", profond(L.PLAN)),
        js("SUIVI", profond(L.SUIVI)),
        js("SIGNE", profond(L.SIGNE)),
        js("DEBUTS", [list(d) for d in L.DEBUTS]),
        js("SEUILS", {"haut": L.SEUIL_HAUT, "bas": L.SEUIL_BAS, "ombre": L.SEUIL_OMBRE, "paliers": L.PALIERS}),
        js("VIGNETTES", {s: vignette(s) for s in ORDRE}),
        js("GLYPHES", GLYPHES),
        js("RAPPEL_RESULTATS", typo(L.RAPPEL_RESULTATS)),
        js("DOUCE", typo(L.DOUCE)),
        js("NON_MESUREE", typo(L.NON_MESUREE)),
    ]
    return "\n".join(morceaux)


def entete():
    desc = ("Un test par mises en situation pour voir la place que douze énergies, une par signe du "
            "zodiaque, prennent dans ta vie en ce moment. Rien n’est prédit : tout part de tes réponses, "
            "qui ne quittent jamais ton navigateur.")
    app = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Boussole céleste", "url": SITE,
           "description": desc, "applicationCategory": "LifestyleApplication", "operatingSystem": "Web", "inLanguage": "fr",
           "isAccessibleForFree": False,
           "offers": [{"@type": "Offer", "name": "Tes résultats", "price": "1.99", "priceCurrency": "EUR"},
                      {"@type": "Offer", "name": "Résultats et dossier complet", "price": "5.99", "priceCurrency": "EUR"}]}
    org = {"@context": "https://schema.org", "@type": "Organization", "name": "Boussole céleste", "url": SITE,
           "logo": {"@type": "ImageObject", "url": SITE + "icone-512.png"}, "email": "contact@boussole-celeste.fr",
           "description": "Un test et un guide pour se comprendre par le langage du ciel, sans prédiction."}
    web = {"@context": "https://schema.org", "@type": "WebSite", "name": "Boussole céleste",
           "alternateName": ["Boussole celeste", "boussole-celeste.fr"], "url": SITE, "inLanguage": "fr",
           "publisher": {"@type": "Organization", "name": "Boussole céleste", "url": SITE}}
    ld = "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>\n' for o in (app, org, web))
    robots = "" if INDEXABLE else '<meta name="robots" content="noindex">\n'
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="version" content="celeste-v{VERSION}">
{robots}<title>Boussole céleste · le test des douze énergies</title>
<link rel="canonical" href="{SITE}">
<meta name="description" content="{html.escape(desc)}">
{ld}<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}">
<meta property="og:site_name" content="Boussole céleste">
<meta property="og:locale" content="fr_FR">
<meta property="og:title" content="Boussole céleste">
<meta property="og:description" content="Ton ciel du moment, lu dans ce que tu vis : seize scènes du quotidien, douze énergies, aucune prédiction.">
<meta property="og:image" content="{SITE}og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Boussole céleste : la roue des douze énergies sur un ciel de nuit">
<meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#0F1424">
<meta name="color-scheme" content="dark">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Céleste">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="icon" type="image/png" href="icone-192.png">
<link rel="preload" href="polices/jost-400-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="polices/cormorant-garamond-600-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="polices/polices.css">
"""


def construire():
    style = (RACINE / "site" / "style.css").read_text()
    corps = (RACINE / "site" / "corps.html").read_text()
    app = (RACINE / "site" / "app.js").read_text()
    logo = logo_svg()
    remplacements = {
        "@@LOGO@@": logo, "@@HERO_CIEL@@": hero_svg(), "@@ROULETTE@@": roulette_svg(),
        "@@RAPPEL@@": html.escape(typo(L.RAPPEL_RESULTATS)), "@@DOUCE@@": html.escape(typo(L.DOUCE)),
        "@@SIGNE_TITRE@@": html.escape(typo(L.SIGNE["titre"])), "@@SIGNE_INTRO@@": html.escape(typo(L.SIGNE["intro"])),
        "@@SIGNE_GARDE@@": html.escape(typo(L.SIGNE["garde"])),
    }
    for k, v in remplacements.items():
        assert k in corps, k
        corps = corps.replace(k, v)
    assert "@@" not in corps, re.findall(r"@@\w+@@", corps)
    assert "/*@DONNEES@*/" in app
    app = app.replace("/*@DONNEES@*/", donnees()).replace("@@LOGO_JS@@", logo)
    gauche = carte_du_ciel(["belier", "cancer", "balance", "capricorne", "lion", "verseau"], 3)
    droite = carte_du_ciel(["taureau", "scorpion", "gemeaux", "sagittaire", "vierge", "poissons"], 6)
    decor = (f".ciel{{ background-image:{url_svg(fond_etoiles())}; }}\n"
             f".aura::before{{ background-image:{url_svg(gauche)}; }}\n"
             f".aura::after{{ background-image:{url_svg(droite)}; }}\n")
    page = (entete() + "<style>\n" + style + "</style>\n</head>\n<body>\n" + corps
            + "\n<script>\n" + app + "</script>\n"
            + "<!-- Décor : les étoiles et les cartes du ciel des marges, chargés après le reste ;\n"
              "     rien de ce qui se lit n'en dépend. -->\n<style>\n" + decor + "</style>\n</body>\n</html>\n")

    # ─── contrôles ───
    soucis = []
    if re.search(r"gratuit", page, re.I):
        soucis.append("le mot interdit apparaît dans la page")
    texte_visible = re.sub(r"<(script|style|svg)[\s\S]*?</\1>", " ", corps)
    texte_visible = re.sub(r"<!--[\s\S]*?-->", " ", texte_visible)
    texte_visible = re.sub(r"<[^>]+>", " ", texte_visible)
    for m in re.finditer(r"[A-Za-zÀ-ÿ]'[A-Za-zÀ-ÿ]", texte_visible):
        soucis.append("apostrophe droite dans un texte : …" + texte_visible[max(0, m.start() - 30):m.end() + 30].strip() + "…")
    texte_visible = re.sub(r"<!--[\s\S]*?-->", " ", texte_visible)
    for m in re.finditer(r"\w[?!;:](?=[\s<]|$)", texte_visible):
        soucis.append("espace insécable manquante : …" + texte_visible[max(0, m.start() - 30):m.end() + 10].strip() + "…")
    if soucis:
        print("\n".join("✗ " + s for s in soucis))
        sys.exit(1)

    (RACINE / "index.html").write_text(page)
    sw = (RACINE / "site" / "sw.js").read_text().replace("@@VERSION@@", f"celeste-v{VERSION}")
    (RACINE / "sw.js").write_text(sw)
    taille = len(page.encode())
    print(f"index.html · {taille // 1024} Ko · version celeste-v{VERSION} · {'indexable' if INDEXABLE else 'noindex (pas encore de domaine)'}")


if __name__ == "__main__":
    # la banque et les rotations d'abord : si une contrainte casse, on ne construit rien
    r = subprocess.run([sys.executable, str(RACINE / "outils" / "relecture.py")], capture_output=True, text=True)
    if r.returncode:
        print(r.stdout, r.stderr)
        sys.exit(1)
    construire()
