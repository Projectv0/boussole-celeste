"""Vérifie la banque de situations, calcule les rotations et compose le fichier de relecture.

    python3 outils/relecture.py          → donnees/rotations.json, donnees/RELECTURE.md,
                                           .cache/textes.json (pour orthographe.swift)

Échoue (code 1) si une contrainte du cahier des charges n'est pas tenue :
  - 24 situations, 4 à 6 réactions chacune, une seule réaction par énergie et par scène ;
  - 18 domaines ;
  - chaque énergie évaluée 8 à 10 fois sur la banque ;
  - trois jeux de 16 : chaque situation dans deux jeux, 8 nouvelles d'un jeu au suivant,
    chaque énergie au moins 5 fois par jeu, et les 8 premières scènes de chaque jeu
    couvrant les 12 énergies au moins 2 fois ;
  - aucun mot interdit (« gratuit », étiquettes, prédictions).
"""
import itertools
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "donnees"))
from energies import ELEMENTS, ENERGIES, MODALITES  # noqa: E402
from lectures import (CIEL_ELEMENT, CIEL_FIN, CIEL_PARTAGE, CIEL_VOILE, CIELS,  # noqa: E402
                      CROISEMENTS, LEVIERS, PLAN, SIGNE, SUIVI, RAPPEL_RESULTATS, DOUCE)
from situations import SITUATIONS  # noqa: E402

IDS = [e["id"] for e in ENERGIES]
EN = {e["id"]: e for e in ENERGIES}
erreurs = []


def typo(t):
    """Apostrophe courbe et espace insécable avant la ponctuation haute."""
    t = t.replace("'", "’")
    t = re.sub(r" ([:;!?»])", " \\1", t)
    return t.replace("« ", "« ")


# ─── 1. La banque ─────────────────────────────────────────────────────────────
compte = Counter()
for k, s in enumerate(SITUATIONS):
    ids = [e for e, _ in s["reac"]]
    if not 4 <= len(ids) <= 6:
        erreurs.append(f"situation {k + 1} : {len(ids)} réactions (4 à 6 attendues)")
    if len(set(ids)) != len(ids):
        erreurs.append(f"situation {k + 1} : une énergie apparaît deux fois")
    for e in ids:
        if e not in EN:
            erreurs.append(f"situation {k + 1} : énergie inconnue {e}")
        compte[e] += 1
if len(SITUATIONS) != 24:
    erreurs.append(f"{len(SITUATIONS)} situations au lieu de 24")
domaines = Counter(s["dom"] for s in SITUATIONS)
if len(domaines) != 18:
    erreurs.append(f"{len(domaines)} domaines au lieu de 18")
for e in IDS:
    if not 8 <= compte[e] <= 10:
        erreurs.append(f"{e} évaluée {compte[e]} fois (8 à 10 attendues)")
total = sum(compte.values())

# ─── 2. Les rotations ─────────────────────────────────────────────────────────
ENS = [set(e for e, _ in s["reac"]) for s in SITUATIONS]


def couverture(indices):
    c = Counter()
    for i in indices:
        c.update(ENS[i])
    return [c[e] for e in IDS]


def note_partition(g):
    jeux = [g[0] + g[1], g[1] + g[2], g[2] + g[0]]
    cov = [couverture(j) for j in jeux]
    return (min(min(c) for c in cov), -sum(sum(1 for x in c if x < 5) for c in cov))


def meilleure_partition(graine=7, essais=4000):
    rnd = random.Random(graine)
    idx = list(range(24))
    rnd.shuffle(idx)
    g = [idx[0:8], idx[8:16], idx[16:24]]
    best = note_partition(g)
    for _ in range(essais):
        a, b = rnd.sample(range(3), 2)
        i, j = rnd.randrange(8), rnd.randrange(8)
        g[a][i], g[b][j] = g[b][j], g[a][i]
        n = note_partition(g)
        if n >= best:
            best = n
        else:
            g[a][i], g[b][j] = g[b][j], g[a][i]
    return g, best


def ordonner(jeu):
    """Les 8 premières couvrent tout au moins 2 fois ; la suite, gloutonne, reste équilibrée."""
    meilleur = None
    for tete in itertools.combinations(jeu, 8):
        c = couverture(tete)
        cle = (min(c), -max(c), sum(c))
        if meilleur is None or cle > meilleur[0]:
            meilleur = (cle, list(tete))
    tete = meilleur[1]
    reste = [i for i in jeu if i not in tete]
    ordre = list(tete)
    while reste:
        def gain(i):
            c = couverture(ordre + [i])
            return (min(c), -sorted(c).count(min(c)), -i)
        i = max(reste, key=gain)
        ordre.append(i)
        reste.remove(i)
    return ordre


groupes, score = meilleure_partition()
for graine in range(8, 60):
    if score[0] >= 5:
        break
    groupes, score = meilleure_partition(graine)
ROTATIONS = [ordonner(groupes[0] + groupes[1]), ordonner(groupes[1] + groupes[2]),
             ordonner(groupes[2] + groupes[0])]

# vérification indépendante de la recherche
presence = Counter(i for r in ROTATIONS for i in r)
if any(presence[i] != 2 for i in range(24)):
    erreurs.append("une situation n'est pas exactement dans deux jeux")
for k in range(3):
    r, suivant = ROTATIONS[k], ROTATIONS[(k + 1) % 3]
    if len(set(r)) != 16:
        erreurs.append(f"jeu {k + 1} : {len(set(r))} situations distinctes")
    if len(set(suivant) - set(r)) != 8:
        erreurs.append(f"jeu {k + 1} → {(k + 1) % 3 + 1} : {len(set(suivant) - set(r))} nouvelles au lieu de 8")
    if min(couverture(r)) < 5:
        erreurs.append(f"jeu {k + 1} : une énergie n'apparaît que {min(couverture(r))} fois")
    if min(couverture(r[:8])) < 2:
        erreurs.append(f"jeu {k + 1} : les 8 premières ne couvrent pas tout deux fois")

(RACINE / "donnees" / "rotations.json").write_text(json.dumps(ROTATIONS) + "\n")

# ─── 3. Les mots interdits et les tournures à relire ──────────────────────────
blocs = []


def ajoute(source, texte):
    if isinstance(texte, str) and texte.strip():
        blocs.append((source, texte))


for e in ENERGIES:
    for ch in ("court", "definition", "sert", "manifeste", "question"):
        ajoute(f"{e['id']}/{ch}", e[ch])
    for p, t in e["paliers"].items():
        ajoute(f"{e['id']}/palier-{p}", t)
    d = e["dossier"]
    for ch in ("essence", "corps_sent", "corps_pense", "vigilance", "signal"):
        ajoute(f"{e['id']}/dossier-{ch}", d[ch])
    for k, t in enumerate(d["pratiques"]):
        ajoute(f"{e['id']}/pratique-{k + 1}", t)
for k, s in enumerate(SITUATIONS):
    ajoute(f"situation-{k + 1}", s["txt"])
    for e, t in s["reac"]:
        ajoute(f"situation-{k + 1}/{e}", t)
for c in CROISEMENTS:
    ajoute(f"croisement/{c['titre']}", c["titre"] + ". " + c["texte"])
    for el, t in c.get("pistes", {}).items():
        ajoute(f"croisement/piste-{el}", t)
for c in CIELS:
    ajoute(f"ciel/{c['titre']}", c["titre"] + ". " + c["phrase"])
for c in (CIEL_PARTAGE, CIEL_VOILE):
    ajoute(f"ciel/{c['titre']}", c["titre"] + ". " + c["phrase"])
ajoute("ciel/element", CIEL_ELEMENT["phrase"])
for k, v in LEVIERS.items():
    ajoute(f"levier/{k}", v["titre"] + ". " + v["pourquoi"])
for k, v in PLAN.items():
    ajoute(f"plan/{k}", v["titre"] + ". " + v["texte"])
ajoute("suivi/intro", SUIVI["intro"])
for q in SUIVI["questions"]:
    ajoute("suivi/question", q)
for k, v in SIGNE.items():
    if isinstance(v, str):
        ajoute(f"signe/{k}", v)
for t in (CIEL_FIN, RAPPEL_RESULTATS, DOUCE):
    ajoute("phrase", t)

INTERDITS = [(r"gratuit", "« gratuit »"), (r"\btu es (un|une|le|la|né)\b", "étiquette « tu es… »"),
             (r"\bles (béliers|taureaux|gémeaux|cancers|lions|vierges|balances|scorpions|sagittaires|capricornes|verseaux|poissons)\b",
              "signe pluriel posé sur des personnes"),
             (r"\b(destin|horoscope|prévision|les astres ont|compatibilit)", "vocabulaire de prédiction"),
             (r"\b(guéri|soign|thérap|diagnost|maladie|symptôm|traitement|médica)", "vocabulaire de santé")]
for src, t in blocs:
    for motif, nom in INTERDITS:
        if re.search(motif, t, re.I):
            erreurs.append(f"{nom} — {src} : {t[:80]}…")
    if re.search(r"\bprédi", t, re.I) and not re.search(r"ne prédi[ts]? rien|ne prédit", t, re.I):
        erreurs.append(f"« prédire » hors négation — {src}")

# accords au masculin qui trahiraient un genre présumé : à relire, pas bloquant
SUSPECTS = re.compile(r"\b(tu es|tu te sens|tu restes|tu deviens|être|te sentir|tu te retrouves) "
                      r"(\w+(é|és|eux|if|ant|ent|u|us|is|it|ert))\b", re.I)
a_relire = [(src, m.group(0)) for src, t in blocs for m in SUSPECTS.finditer(t)
            if not m.group(2).lower() in {"bien", "là", "content·e", "fier·e"} and "·" not in m.group(0)]

(RACINE / ".cache").mkdir(exist_ok=True)
(RACINE / ".cache" / "textes.json").write_text(
    json.dumps([{"source": s, "texte": typo(t)} for s, t in blocs], ensure_ascii=False, indent=1))

# ─── 4. Les longueurs ─────────────────────────────────────────────────────────
mots = lambda t: len(re.findall(r"[\wÀ-ÿ’'-]+", t))
dossier_fiches = sum(mots(e["dossier"][c]) for e in ENERGIES for c in ("essence", "corps_sent", "corps_pense", "vigilance", "signal"))
dossier_fiches += sum(mots(p) for e in ENERGIES for p in e["dossier"]["pratiques"])
dossier_fiches += sum(mots(e["question"]) for e in ENERGIES)
# Chaque fiche du dossier s'ouvre sur l'analyse personnelle (le palier de la note) :
# on compte le palier moyen de chaque énergie.
perso = sum(round(sum(mots(t) for t in e["paliers"].values()) / 3) for e in ENERGIES)
autour = perso + mots(" ".join(v["texte"] for v in PLAN.values())) + 3 * 60 + 4 * 55 + 350
# 3 leviers (~60 mots chacun), ~4 croisements retenus (~55), sommaire + couverture +
# tableau + moments relus + page de suivi (~350)

# ─── 5. Le fichier de relecture ───────────────────────────────────────────────
L = []
w = L.append
w("# Boussole céleste — les contenus, à relire")
w("")
w("*Fichier produit par `outils/relecture.py` à partir de `donnees/`. Ne le corrige pas à la main : "
  "dis-moi ce qui ne va pas, je corrige la source et je le refais.*")
w("")
w("## En bref")
w("")
w(f"- **12 énergies**, une par signe, affichées par leur verbe. Chacune a sa fiche, trois analyses "
  f"selon la note (discrète, présente, dominante), une fiche de dossier avec trois pratiques "
  f"(**36 pratiques**) et une question de réflexion (**12 questions**).")
nb = (f"exactement {min(compte.values())} fois" if min(compte.values()) == max(compte.values())
      else f"{min(compte.values())} à {max(compte.values())} fois")
w(f"- **24 situations**, {len(domaines)} domaines, **{total} évaluations** : chaque énergie est notée "
  f"{nb} dans la banque.")
w(f"- **3 rotations de 16** : chaque énergie au moins {min(min(couverture(r)) for r in ROTATIONS)} fois par jeu, "
  f"et les 8 premières scènes de chaque jeu couvrent les 12 énergies au moins "
  f"{min(min(couverture(r[:8])) for r in ROTATIONS)} fois.")
w(f"- **15 croisements**, **{len(CIELS)} ciels du moment** (une règle par paire d'éléments, "
  f"plus trois replis), les leviers, le plan de 30 jours, le signe de naissance.")
milliers = lambda n: f"{n:,}".replace(",", "\u00a0")
w(f"- **Le dossier** : environ {milliers(round((dossier_fiches + autour) / 50) * 50)} mots une fois assemblé "
  f"({milliers(round(dossier_fiches / 50) * 50)} pour les douze fiches et les questions, le reste pour les leviers, les "
  f"croisements, le plan et la page de suivi). Cible : 4 500 à 5 000.")
w("")
w("### Deux choix de méthode à connaître")
w("")
w("1. **Le test se répond à l'aveugle.** Chaque scène propose 4 à 6 réactions, écrites comme des "
  "comportements. Tu notes chacune de « pas du tout » à « énormément ». Le nom de l'énergie "
  "n'apparaît qu'aux résultats. Boussole, depuis le 23 septembre, fait au contraire choisir les "
  "émotions par leur nom : ici ce serait répondre « comme son signe ».")
w("2. **La confiance se mesure sur cinq présentations.** Boussole tempère une note par le nombre de "
  "fois où l'émotion a été retenue, rapporté au nombre de scènes. Ici chaque énergie n'est proposée "
  f"que dans les scènes qui portent sa réaction ({min(min(couverture(r)) for r in ROTATIONS)} à "
  f"{max(max(couverture(r)) for r in ROTATIONS)} fois par jeu). Le plafond est donc la couverture "
  "garantie : à partir de cinq mesures, une énergie est crue sur parole. Sans ce changement, "
  "« tout à 4 » ne donnerait jamais 10/10. Une énergie mesurée une seule fois, même à fond, reste "
  "à 4/10. Les auto-tests le vérifieront.")
w("")
w("Dans la banque ci-dessous, chaque réaction porte entre crochets l'énergie qu'elle mesure. "
  "Pendant le test, ces crochets n'apparaissent pas.")
w("")

w("## 1. Les douze énergies")
w("")
w("| | Verbe | Élément | Modalité | Maître | Lumière | Ombre |")
w("|---|---|---|---|---|---|---|")
for e in ENERGIES:
    w(f"| {e['signe']} | **{e['verbe']}** | {ELEMENTS[e['element']]['nom']} | {e['modalite']} | "
      f"{e['maitre']} | {e['lumiere']} | {e['ombre']} |")
w("")
w("**Les éléments** : " + " · ".join(f"{v['nom']} ({v['mode']}) : {', '.join(EN[i]['verbe'] for i in v['ids'])}"
                                     for v in ELEMENTS.values()) + ".")
w("")
w("**Les modalités** : " + " · ".join(f"{v['nom']} ({v['mode']}) : {', '.join(EN[i]['verbe'] for i in v['ids'])}"
                                      for v in MODALITES.values()) + ".")
w("")
for e in ENERGIES:
    w(f"### {e['verbe'].capitalize()} — {e['signe']}")
    w("")
    w(f"*Mots-clés : {', '.join(e['mots'])}. Antisèche du journal : « {typo(e['court'])} »*")
    w("")
    w(f"**Ce que c'est.** {typo(e['definition'])}")
    w("")
    w(f"**À quoi elle sert.** {typo(e['sert'])}")
    w("")
    w(f"**Comment elle se manifeste.** {typo(e['manifeste'])}")
    w("")
    for p, lib in (("discrete", "Discrète (moins de 3,5)"), ("presente", "Présente (3,5 à 7)"),
                   ("dominante", "Dominante (plus de 7)")):
        w(f"- **{lib}.** {typo(e['paliers'][p])}")
    w("")

w("## 2. Les 24 situations")
w("")
w("| Énergie | " + " | ".join(EN[i]["verbe"] for i in IDS) + " |")
w("|---|" + "---|" * 12)
w("| Sur la banque | " + " | ".join(str(compte[i]) for i in IDS) + " |")
for k, r in enumerate(ROTATIONS):
    c = couverture(r)
    w(f"| Jeu {k + 1} (16) | " + " | ".join(str(x) for x in c) + " |")
for k, r in enumerate(ROTATIONS):
    c = couverture(r[:8])
    w(f"| Jeu {k + 1}, 8 premières | " + " | ".join(str(x) for x in c) + " |")
w("")
for k, s in enumerate(SITUATIONS):
    jeux = [str(j + 1) for j, r in enumerate(ROTATIONS) if k in r]
    w(f"### {k + 1}. {s['dom']}  ·  *jeux {' et '.join(jeux)}*")
    w("")
    w(typo(s["txt"]))
    w("")
    for e, t in s["reac"]:
        w(f"- {typo(t)} *[{EN[e]['verbe']}, {EN[e]['signe']}]*")
    w("")
w("### Les rotations")
w("")
w("Numéros des situations, dans l'ordre de priorité de chaque jeu. Quand le journal raccourcit le "
  "test, on garde les premières ; à l'écran, elles s'affichent dans l'ordre de la banque.")
w("")
for k, r in enumerate(ROTATIONS):
    w(f"- **Jeu {k + 1}** : " + ", ".join(str(i + 1) for i in r))
w("")

w("## 3. Les 15 croisements")
w("")
w("Un croisement ne se déclenche que si les énergies concernées ont été mesurées. Seuils : "
  "une paire dès que les deux énergies ont une place d'au moins 5,5 ; un élément « en retrait » "
  "quand la moyenne de ses trois énergies ne dépasse pas 2,5.")
w("")
for c in CROISEMENTS:
    cond = {"paire": lambda c: f"{EN[c['a']]['verbe']} + {EN[c['b']]['verbe']}",
            "element_retrait": lambda c: "les trois énergies d'un élément très discrètes",
            "element_domine": lambda c: "un élément nettement au-dessus des autres",
            "modalite": lambda c: f"{c['haut']} bien au-dessus de {c['bas']}"}[c["type"]](c)
    w(f"**{typo(c['titre'])}** *({cond})*. {typo(c['texte'])}")
    if "pistes" in c:
        w("")
        for el, t in c["pistes"].items():
            w(f"- piste pour {ELEMENTS[el]['art']}{ELEMENTS[el]['nom']} : {typo(t)}")
    w("")

w("## 4. Ton ciel du moment")
w("")
w("Lu sur les deux énergies les plus présentes, selon leurs éléments. Le site écrit d'abord "
  "« Oser et bâtir prennent le plus de place en ce moment. », puis la phrase, puis : "
  f"« {typo(CIEL_FIN)} »")
w("")
for c in CIELS:
    a, b = c["elements"]
    w(f"- **{typo(c['titre'])}** *({ELEMENTS[a]['nom']} + {ELEMENTS[b]['nom']})*. {typo(c['phrase'])}")
w(f"- **Repli, un élément en tête** *(« {', '.join(CIEL_ELEMENT['titre'].values())} »)*. {typo(CIEL_ELEMENT['phrase'])}")
w(f"- **{CIEL_PARTAGE['titre']}** *(rien ne domine)*. {typo(CIEL_PARTAGE['phrase'])}")
w(f"- **{CIEL_VOILE['titre']}** *(presque tout au plus bas)*. {typo(CIEL_VOILE['phrase'])}")
w("")

w("## 5. Le dossier, énergie par énergie")
w("")
w("Une fiche par énergie, une par page en PDF. Chaque fiche s'ouvre sur « Chez toi, en ce moment » : "
  "la note et l'analyse de la page de résultats (le palier). Quand une énergie dépasse 7/10, le "
  "point de vigilance passe juste après. Sinon, il vient en dernier.")
w("")
for e in ENERGIES:
    d = e["dossier"]
    w(f"### {e['verbe'].capitalize()} — {e['signe']}")
    w("")
    w(typo(d["essence"]))
    w("")
    w(f"{typo(d['corps_sent'])} {typo(d['corps_pense'])}")
    w("")
    for k, p in enumerate(d["pratiques"]):
        marque = " *(celle qui tempère l'excès)*" if k == d["apaiser"] else ""
        w(f"{k + 1}. {typo(p)}{marque}")
    w("")
    w(f"**Point de vigilance.** {typo(d['vigilance'])} Le signal à surveiller : {typo(d['signal'])}.")
    w("")
    w(f"**Question de réflexion.** {typo(e['question'])}")
    w("")

w("## 6. Les leviers, le plan, le suivi")
w("")
for k, v in LEVIERS.items():
    w(f"- **{v['titre']}** *({v['quand']})*. {typo(v['pourquoi'])}")
w("")
for k, v in PLAN.items():
    w(f"- **{typo(v['titre'])}.** {typo(v['texte'])}")
w("")
w(f"**{SUIVI['titre']}.** {typo(SUIVI['intro'])}")
w("")
for q in SUIVI["questions"]:
    w(f"- {typo(q)}")
w("")

w("## 7. Le signe de naissance")
w("")
for k in ("titre", "intro", "limite", "meme", "element", "modalite", "autre", "rang", "garde"):
    w(f"- *{k}* — {typo(SIGNE[k])}")
w("")
w("## 8. Les phrases fixes")
w("")
w(f"- Sur la page de résultats : « {typo(RAPPEL_RESULTATS)} »")
w(f"- Sur le site, jamais dans les publications : « {typo(DOUCE)} »")
w("")

# typo() est idempotente : on la repasse sur tout, titres et tableaux compris
(RACINE / "donnees" / "RELECTURE.md").write_text("\n".join(typo(l) for l in L) + "\n")

print(f"{len(SITUATIONS)} situations · {len(domaines)} domaines · {total} évaluations")
print("par énergie :", " ".join(f"{EN[i]['verbe']}={compte[i]}" for i in IDS))
for k, r in enumerate(ROTATIONS):
    print(f"jeu {k + 1} : min {min(couverture(r))} · 8 premières min {min(couverture(r[:8]))} · {r}")
print(f"dossier ≈ {dossier_fiches + autour} mots (fiches {dossier_fiches})")
print(f"{len(blocs)} blocs de texte · {len(a_relire)} accords à relire")
for src, m in a_relire:
    print("  ? ", src, "·", m)
if erreurs:
    print("\n".join("✗ " + e for e in erreurs))
    sys.exit(1)
print("✓ toutes les contraintes tiennent")
