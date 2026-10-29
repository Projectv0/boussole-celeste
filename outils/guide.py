"""Le guide : des sources texte (guide/sources/*.md) aux pages HTML, et leurs contrôles.

    python3 outils/guide.py                     → guide/*.html, guide/index.html, sitemap.xml
    python3 outils/guide.py --verifier a b c    → contrôle ces sources (structure, longueur,
                                                  liens, vocabulaire, orthographe), n'écrit rien

Toutes les pages sortent du même gabarit que guide/anxiete.html de Boussole : sept h2,
trois h3 numérotés (les pratiques), un encart doux et un encart attention, un appel vers
le test (sans prix), quatre liens « à lire aussi », JSON-LD Article et fil d'Ariane,
canonical, style.css partagé. Le gabarit est écrit une fois, ici : un article ne peut
pas s'en écarter.

Format d'une source :

    ---
    titre: L'énergie Bélier : oser, et quand ça déborde     (le h1)
    title: …                                                 (facultatif, le <title>, 60 caractères au plus)
    description: …                                           (110 à 160 caractères)
    famille: energie | element | modalite | situation
    energies: belier, capricorne                             (les énergies dont parle l'article)
    cta: Quelle place prend l'énergie d'oser dans ta vie ?   (le titre de l'appel vers le test)
    ---
    Le chapeau, en un paragraphe.

    ## Un titre de section
    Un paragraphe, avec **du gras**, *de l'italique* et [un lien](energie-lion.html).

    !doux Le titre de l'encart doux
    Son texte.

    ### 1. Une pratique
    …
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOURCES = RACINE / "guide" / "sources"
sys.path.insert(0, str(RACINE / "donnees"))
sys.path.insert(0, str(RACINE / "outils"))
import energies as E  # noqa: E402
from glyphes import GLYPHES  # noqa: E402
from plan_guide import SLUGS as PREVUS  # noqa: E402

SITE = "https://boussole-celeste.fr"
INDEXABLE = (RACINE / "CNAME").exists()
MESURE = ""   # l'adresse du compteur, la même que dans site/app.js (étape 6)
EN = {e["id"]: e for e in E.ENERGIES}
EL_DE = {e["id"]: e["element"] for e in E.ENERGIES}
MOD_DE = {e["id"]: e["modalite"] for e in E.ENERGIES}
AXE = {"belier": "balance", "taureau": "scorpion", "gemeaux": "sagittaire", "cancer": "capricorne",
       "lion": "verseau", "vierge": "poissons"}
AXE.update({v: k for k, v in list(AXE.items())})
MOD_SLUG = {"cardinal": "energies-cardinales", "fixe": "energies-fixes", "mutable": "energies-mutables"}
COMPLEMENT = {"feu": "air", "air": "feu", "terre": "eau", "eau": "terre"}
MOTS_MIN, MOTS_MAX = 880, 1070

INTERDITS = [
    (r"gratuit", "le mot interdit"),
    (r"\btu es (un|une|le|la|né|née|quelqu)", "étiquette « tu es… »"),
    (r"\bles (béliers|taureaux|cancers|lions|vierges|balances|scorpions|sagittaires|capricornes|verseaux)\b", "signe posé sur des personnes"),
    (r"\bles gémeaux (sont|ont|aiment|détestent|font)\b|\bles poissons (sont|ont|aiment|détestent|font)\b", "signe posé sur des personnes"),
    (r"\bnatifs?\b|\bnatives?\b", "« natif »"),
    (r"\b(destin|horoscope|prévision|les astres (ont|veulent|décident)|compatibilit|ascendant)", "vocabulaire de prédiction"),
    (r"\b(guéri|soign|thérap|diagnost|maladie|symptôm|traitement|médica|pathologi|trouble (anxieux|de)|dépression|burn-out|burnout|toc\b|hypersensib|haut potentiel)", "vocabulaire de santé"),
]


def typo(t):
    t = t.replace("'", "’")
    t = re.sub(r" ([:;!?»])", " \\1", t)
    return t.replace("« ", "« ")


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([a-z0-9-]+\.html|\.\./|\./)\)", r'<a href="\2">\1</a>', t)
    return typo(t)


def lire(slug):
    brut = (SOURCES / f"{slug}.md").read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", brut, re.S)
    if not m:
        raise ValueError(f"{slug} : en-tête --- manquant")
    meta = {}
    for ligne in m.group(1).splitlines():
        if ":" in ligne:
            k, v = ligne.split(":", 1)
            meta[k.strip()] = v.strip()
    meta["energies"] = [x.strip() for x in meta.get("energies", "").split(",") if x.strip()]
    blocs = [b.strip("\n") for b in re.split(r"\n\s*\n", m.group(2).strip()) if b.strip()]
    return meta, blocs


def analyser(slug):
    """(meta, éléments) — éléments : (type, titre, texte)."""
    meta, blocs = lire(slug)
    el = []
    for k, b in enumerate(blocs):
        lignes = b.split("\n")
        tete = lignes[0]
        if tete.startswith("### "):
            el.append(("h3", tete[4:].strip(), ""))
            if len(lignes) > 1:
                el.append(("p", "", " ".join(l.strip() for l in lignes[1:])))
        elif tete.startswith("## "):
            el.append(("h2", tete[3:].strip(), ""))
            if len(lignes) > 1:
                el.append(("p", "", " ".join(l.strip() for l in lignes[1:])))
        elif tete.startswith("!doux ") or tete.startswith("!attention "):
            genre, titre = tete[1:].split(" ", 1)
            el.append((genre, titre.strip(), " ".join(l.strip() for l in lignes[1:])))
        else:
            el.append(("chapeau" if k == 0 else "p", "", " ".join(l.strip() for l in lignes)))
    return meta, el


def mots(t):
    return len(re.findall(r"[\wÀ-ÿ’'-]+", re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)))


# ─── le plan du guide ────────────────────────────────────────────────────────

def slugs():
    return sorted(p.stem for p in SOURCES.glob("*.md") if not p.stem.startswith("_"))


def catalogue():
    return {s: analyser(s)[0] for s in slugs()}


def court(meta):
    """Le nom d'un article dans une liste de liens : le h1, sans sa promesse de clic."""
    return meta.get("court") or meta["titre"].split(" : ")[0]


def a_lire_aussi(slug, cat):
    m = cat[slug]
    f, ens = m["famille"], m["energies"]
    if f == "energie":
        e = ens[0]
        liens = [f"element-{EL_DE[e]}", MOD_SLUG[MOD_DE[e]], f"energie-{AXE[e]}"]
        voisins = [i for i in E.ELEMENTS[EL_DE[e]]["ids"] if i != e]
        liens.append(f"energie-{voisins[0]}")
    elif f == "element":
        el = slug.split("-", 1)[1]
        liens = [f"energie-{i}" for i in E.ELEMENTS[el]["ids"]] + [f"element-{COMPLEMENT[el]}"]
    elif f == "modalite":
        mod = [k for k, v in MOD_SLUG.items() if v == slug][0]
        liens = [f"energie-{i}" for i in E.MODALITES[mod]["ids"]]
    else:
        liens = [f"energie-{e}" for e in ens]
        autres = [s for s, mm in cat.items() if mm["famille"] == "situation" and s != slug]
        autres.sort(key=lambda s: (-len(set(cat[s]["energies"]) & set(ens)), s))
        liens += autres
    vus, out = set(), []
    for l in liens:
        if l in cat and l not in vus and l != slug:
            vus.add(l); out.append(l)
    return out[:4]


def situations_de(ids, cat, exclure=()):
    s = [k for k, m in cat.items() if m["famille"] == "situation" and set(m["energies"]) & set(ids) and k not in exclure]
    s.sort(key=lambda k: (-len(set(cat[k]["energies"]) & set(ids)), k))
    return s[:4]


# ─── contrôles ───────────────────────────────────────────────────────────────

def verifier(slug, cat):
    soucis = []
    try:
        meta, el = analyser(slug)
    except Exception as e:
        return [str(e)]
    for champ in ("titre", "description", "famille", "cta"):
        if not meta.get(champ):
            soucis.append(f"champ « {champ} » manquant")
    if meta.get("famille") not in ("energie", "element", "modalite", "situation"):
        soucis.append(f"famille inconnue : {meta.get('famille')}")
    for e in meta["energies"]:
        if e not in EN:
            soucis.append(f"énergie inconnue : {e}")
    if meta.get("famille") in ("energie", "situation") and not meta["energies"]:
        soucis.append("aucune énergie rattachée")
    titre = meta.get("title") or meta.get("titre", "")
    if len(titre) > 60:
        soucis.append(f"<title> trop long ({len(titre)} caractères, 60 au plus) : ajoute un champ « title » plus court")
    d = meta.get("description", "")
    if not 110 <= len(d) <= 160:
        soucis.append(f"description de {len(d)} caractères (110 à 160)")
    types = [t for t, _, _ in el]
    if types.count("h2") != 7:
        soucis.append(f"{types.count('h2')} h2 au lieu de 7")
    h3 = [ti for t, ti, _ in el if t == "h3"]
    if [x[:2] for x in h3] != ["1.", "2.", "3."]:
        soucis.append(f"les h3 doivent être exactement « 1. … », « 2. … », « 3. … » (trouvé : {h3})")
    if types.count("doux") != 1 or types.count("attention") != 1:
        soucis.append(f"encarts : {types.count('doux')} doux et {types.count('attention')} attention (1 de chaque attendu)")
    if types[:1] != ["chapeau"]:
        soucis.append("le texte doit commencer par le chapeau, avant le premier ##")
    corps = " ".join(f"{ti} {tx}" for _, ti, tx in el)
    n = mots(corps)
    if not MOTS_MIN <= n <= MOTS_MAX:
        soucis.append(f"{n} mots ({MOTS_MIN} à {MOTS_MAX})")
    for lien in re.findall(r"\]\(([^)]+)\)", corps):
        if lien.endswith(".html") and lien[:-5] not in cat and lien[:-5] not in PREVUS:
            soucis.append(f"lien vers une page qui n'existe pas et n'est pas au plan : {lien}")
    tout = " ".join([meta.get("titre", ""), meta.get("description", ""), meta.get("cta", ""), corps])
    for motif, nom in INTERDITS:
        for m in re.finditer(motif, tout, re.I):
            soucis.append(f"{nom} : …{tout[max(0, m.start() - 40):m.end() + 40]}…")
    for m in re.finditer(r"\bprédi\w*", tout, re.I):
        avant = tout[max(0, m.start() - 25):m.start()].lower()
        if not re.search(r"\b(ne|n’|n'|sans|pas|aucune?|ni|jamais)\b[^.!?]{0,22}$", avant):
            soucis.append(f"« {m.group()} » hors négation : …{tout[max(0, m.start() - 40):m.end() + 30]}…")
    return soucis


def orthographe(slugs_):
    blocs = []
    for s in slugs_:
        meta, el = analyser(s)
        textes = [meta.get("titre", ""), meta.get("description", ""), meta.get("cta", "")] + [f"{ti} {tx}" for _, ti, tx in el]
        blocs += [{"source": s, "texte": typo(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", re.sub(r"\*+", "", t)))} for t in textes if t.strip()]
    import os
    import tempfile
    (RACINE / ".cache").mkdir(exist_ok=True)
    # un fichier par appel : plusieurs rédacteurs vérifient en même temps
    fd, nom = tempfile.mkstemp(suffix=".json", dir=RACINE / ".cache")
    os.write(fd, json.dumps(blocs, ensure_ascii=False).encode()); os.close(fd)
    r = subprocess.run(["swift", str(RACINE / "outils" / "orthographe.swift"), nom], capture_output=True, text=True)
    os.remove(nom)
    try:
        return [x for x in json.loads(r.stdout) if x["mot"] not in {"qu", "Céleste", "Boussole"}]
    except Exception:
        return [{"source": "?", "mot": "(correcteur indisponible)", "contexte": r.stderr[:200], "suggestions": []}]


# ─── pages ───────────────────────────────────────────────────────────────────

def puce(slug, cat):
    m = cat[slug]
    if m["energies"] and m["famille"] in ("energie", "situation"):
        return (f'<svg class="puce" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
                f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{GLYPHES[m["energies"][0]]}"/></svg>')
    return '<svg class="puce" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="5" fill="currentColor"/></svg>'


def grille(titre, liste, cat, classe="autres"):
    if not liste:
        return ""
    liens = "\n".join(f'    <a href="{s}.html">{puce(s, cat)} {html.escape(typo(court(cat[s])))}</a>' for s in liste)
    return f'<section class="{classe}">\n  <h2>{titre}</h2>\n  <div class="grille">\n{liens}\n  </div>\n</section>\n'


def dates(chemin):
    r = subprocess.run(["git", "log", "--format=%cI", "--", chemin], capture_output=True, text=True, cwd=RACINE)
    jours = [l.strip()[:10] for l in r.stdout.splitlines() if l.strip()]
    import datetime
    auj = datetime.date.today().isoformat()
    return (jours[-1], jours[0]) if jours else (auj, auj)


def entete(titre, description, url, ld, robots_force=None):
    robots = robots_force or ("" if INDEXABLE else '<meta name="robots" content="noindex">\n')
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}<title>{titre}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{titre}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{SITE}/og.jpg">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Boussole céleste">
<meta property="og:locale" content="fr_FR">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Boussole céleste : la roue des douze énergies sur un ciel de nuit">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0F1424">
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<link rel="preload" href="../polices/jost-400-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../polices/cormorant-garamond-600-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../polices/polices.css">
<link rel="stylesheet" href="style.css">
{ld}</head>
<body>

<div class="top">
  <a class="marque" href="../"><span class="logo"><img src="../favicon.svg" alt="" width="32" height="32"></span> Boussole céleste</a>
  <nav><a href="./">Le guide</a></nav>
</div>

<main>
"""


def pied(chemin):
    mesure = f"""
<script>
/* Un seul repère : quelqu'un a ouvert cette page. Pas de cookie, pas d'identifiant.
   Le chemin est écrit en dur : rien de l'adresse (recherche, paramètre) ne s'y glisse.
   MESURE vide : rien n'est envoyé. */
(function(){{
  var MESURE = "{MESURE}";
  if(!MESURE) return;
  try{{
    var c = JSON.stringify({{ e: "article", p: "{chemin}" }});
    var b = new Blob([c], {{ type: "text/plain" }});
    if(navigator.sendBeacon && navigator.sendBeacon(MESURE, b)) return;
    fetch(MESURE, {{ method: "POST", body: c, keepalive: true, mode: "cors" }});
  }}catch(_){{}}
}})();
</script>"""
    return f"""</main>

<footer>
  <p><a href="../">Boussole céleste</a> · <a href="./">Le guide</a> · <a href="../legal/mentions-legales.html">Mentions légales</a> · <a href="../legal/confidentialite.html">Confidentialité</a></p>
  <p>Un langage pour réfléchir à soi, pas une prédiction. Ce guide ne remplace l’avis d’aucun professionnel.</p>
</footer>
{mesure}
</body>
</html>
"""


ETIQUETTES = {"element": "Élément", "modalite": "Façon d’avancer", "situation": "Situation vécue"}


def cta_texte(meta):
    f, ens = meta["famille"], meta["energies"]
    if f == "energie":
        v = EN[ens[0]]["verbe"]
        de = ("d’" if re.match(r"[aeéèêio]", v) else "de ") + v
        return f"Le test de Boussole céleste mesure la place de l’énergie {de} et des onze autres dans ta vie en ce moment, à partir de seize situations du quotidien. Tes réponses ne quittent jamais ton navigateur."
    if f in ("element", "modalite"):
        return "Le test de Boussole céleste mesure la place des douze énergies dans ta vie en ce moment, et ce que ça donne pour chaque élément et chaque façon d’avancer. Tes réponses ne quittent jamais ton navigateur."
    return "Seize situations du quotidien pour voir quelles énergies prennent de la place chez toi en ce moment. Rien n’est prédit : tout part de tes réponses, qui ne quittent jamais ton navigateur."


def page_article(slug, cat):
    meta, el = analyser(slug)
    url = f"{SITE}/guide/{slug}.html"
    titre = html.escape(typo(meta.get("title") or meta["titre"]))
    desc = html.escape(typo(meta["description"]))
    creation, modif = dates(f"guide/sources/{slug}.md")
    editeur = {"@type": "Organization", "name": "Boussole céleste", "url": SITE + "/"}
    article = {"@context": "https://schema.org", "@type": "Article", "headline": typo(meta["titre"]),
               "description": typo(meta["description"]), "inLanguage": "fr", "url": url,
               "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "image": f"{SITE}/og.jpg",
               "datePublished": creation, "dateModified": modif, "author": editeur,
               "publisher": {**editeur, "logo": {"@type": "ImageObject", "url": f"{SITE}/icone-512.png"}},
               "isPartOf": {"@type": "WebSite", "name": "Boussole céleste", "url": SITE + "/"}}
    ariane = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Le guide", "item": SITE + "/guide/"},
        {"@type": "ListItem", "position": 3, "name": typo(court(meta)), "item": url}]}
    ld = "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>\n' for o in (article, ariane))
    f = meta["famille"]
    if f == "energie":
        e = EN[meta["energies"][0]]
        etiquette = f"Énergie · {E.ELEMENTS[e['element']]['nom']} · {e['modalite']}"
    else:
        etiquette = ETIQUETTES[f]
    corps = []
    for t, ti, tx in el:
        if t == "chapeau":
            corps.append(f'  <p class="chapeau">{inline(tx)}</p>')
        elif t == "h2":
            corps.append(f"\n  <h2>{inline(ti)}</h2>")
        elif t == "h3":
            corps.append(f"  <h3>{inline(ti)}</h3>")
        elif t == "p":
            corps.append(f"  <p>{inline(tx)}</p>")
        else:
            corps.append(f'  <div class="encart {t}">\n    <strong>{inline(ti)}</strong>\n    {inline(tx)}\n  </div>')
    vraie_vie = ""
    if f == "energie":
        vraie_vie = grille("Quand ça arrive dans la vraie vie", situations_de(meta["energies"], cat), cat, "autres situations")
    elif f == "element":
        el_id = slug.split("-", 1)[1]
        vraie_vie = grille("Quand ça arrive dans la vraie vie", situations_de(E.ELEMENTS[el_id]["ids"], cat), cat, "autres situations")
    page = (entete(titre, desc, url, ld)
            + f'<article>\n  <span class="meta">{etiquette}</span>\n  <h1>{inline(meta["titre"])}</h1>\n'
            + "\n".join(corps) + "\n</article>\n\n"
            + f'<section class="cta">\n  <h2>{inline(meta["cta"])}</h2>\n  <p>{typo(cta_texte(meta))}</p>\n'
              f'  <a class="bouton" href="../">Faire le test <span aria-hidden="true">→</span></a>\n</section>\n\n'
            + vraie_vie + grille("À lire aussi", a_lire_aussi(slug, cat), cat)
            + pied(f"/guide/{slug}.html"))
    return page


def page_pilier(cat):
    import pilier
    url = f"{SITE}/guide/"
    titre = html.escape(typo(pilier.TITLE))
    desc = html.escape(typo(pilier.DESCRIPTION))
    parties = []
    tous = []
    for sec in pilier.SECTIONS:
        if sec["famille"] == "energie":
            liste = [f"energie-{i}" for i in E.ELEMENTS[sec["element"]]["ids"]] if sec.get("element") else []
        else:
            liste = sorted([s for s, m in cat.items() if m["famille"] == sec["famille"]],
                           key=lambda s: (sec.get("ordre", []).index(s) if s in sec.get("ordre", []) else 99, s))
        liste = [s for s in liste if s in cat]
        tous += liste
        cartes = "\n".join(
            f'    <a href="{s}.html">{puce(s, cat)} <span><b>{html.escape(typo(court(cat[s])))}</b><br>'
            f'<small>{html.escape(typo(cat[s]["description"]))}</small></span></a>' for s in liste)
        parties.append(f'  <h2>{inline(sec["titre"])}</h2>\n  <p>{inline(sec["intro"])}</p>\n  <div class="grille pilier">\n{cartes}\n  </div>')
    collection = {"@context": "https://schema.org", "@type": "CollectionPage", "name": typo(pilier.H1), "url": url,
                  "description": typo(pilier.DESCRIPTION), "inLanguage": "fr",
                  "isPartOf": {"@type": "WebSite", "name": "Boussole céleste", "url": SITE + "/"},
                  "hasPart": [{"@type": "Article", "name": typo(court(cat[s])), "url": f"{SITE}/guide/{s}.html"} for s in tous]}
    ariane = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Le guide", "item": url}]}
    ld = "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>\n' for o in (collection, ariane))
    classe = lambda k: ' class="chapeau"' if k == 0 else ""
    intro = "\n".join(f"  <p{classe(k)}>{inline(p)}</p>" for k, p in enumerate(pilier.INTRO))
    page = (entete(titre, desc, url, ld).replace('<nav><a href="./">Le guide</a></nav>', '<nav><a href="../">Faire le test</a></nav>')
            + f'<article>\n  <span class="meta">Le guide</span>\n  <h1>{inline(pilier.H1)}</h1>\n{intro}\n\n'
            + "\n\n".join(parties)
            + f'\n\n  <div class="encart doux">\n    <strong>{inline(pilier.ENCART[0])}</strong>\n    {inline(pilier.ENCART[1])}\n  </div>\n</article>\n\n'
            + f'<section class="cta">\n  <h2>{inline(pilier.CTA[0])}</h2>\n  <p>{inline(pilier.CTA[1])}</p>\n'
              f'  <a class="bouton" href="../">Faire le test <span aria-hidden="true">→</span></a>\n</section>\n\n'
            + pied("/guide/"))
    return page, tous


def sitemap(pages):
    lignes = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, chemin, prio in pages:
        lignes += ["  <url>", f"    <loc>{SITE}{url}</loc>", f"    <lastmod>{dates(chemin)[1]}</lastmod>",
                   "    <changefreq>monthly</changefreq>", f"    <priority>{prio}</priority>", "  </url>"]
    lignes.append("</urlset>")
    (RACINE / "sitemap.xml").write_text("\n".join(lignes) + "\n")


def construire():
    cat = catalogue()
    soucis = {s: verifier(s, cat) for s in cat}
    soucis = {s: v for s, v in soucis.items() if v}
    if soucis:
        for s, v in soucis.items():
            print(f"✗ {s}"); [print("   ·", x) for x in v]
        sys.exit(1)
    for s in cat:
        (RACINE / "guide" / f"{s}.html").write_text(page_article(s, cat))
    page, tous = page_pilier(cat)
    (RACINE / "guide" / "index.html").write_text(page)
    oublies = set(cat) - set(tous)
    if oublies:
        print("✗ articles absents de la page pilier :", ", ".join(sorted(oublies))); sys.exit(1)
    pages = [("/", "index.html", "1.0"), ("/guide/", "guide/index.html", "0.9")]
    pages += [(f"/guide/{s}.html", f"guide/sources/{s}.md", "0.8") for s in tous]
    sitemap(pages)
    total = sum(mots(" ".join(f"{ti} {tx}" for _, ti, tx in analyser(s)[1])) for s in cat)
    print(f"guide : {len(cat)} articles + la page pilier · {total} mots · sitemap.xml ({len(pages)} URL)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verifier":
        cat = catalogue()
        demandes = sys.argv[2:] or list(cat)
        ok = True
        for s in demandes:
            v = verifier(s, cat)
            meta, el = analyser(s)
            n = mots(" ".join(f"{ti} {tx}" for _, ti, tx in el))
            print(("✓ " if not v else "✗ ") + f"{s} ({n} mots)")
            for x in v:
                print("   ·", x)
            ok = ok and not v
        for x in orthographe(demandes):
            ok = False
            print(f"   ? orthographe — {x['source']} : « {x['mot']} » dans …{x['contexte']}… → {', '.join(x['suggestions'][:3])}")
        sys.exit(0 if ok else 1)
    construire()
