#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Met en tableau les chiffres du compteur d'audience.

    python3 outils/mesure.py               les 30 derniers jours
    python3 outils/mesure.py 90            les 90 derniers jours

Le Worker renvoie du JSON ; ce script en fait quelque chose qui se lit. Il calcule
surtout l'entonnoir — la suite arrivée → test commencé → test fini → formule
affichée → départ vers Stripe —, parce que c'est le seul endroit où les nombres
disent quoi faire : l'étape où la chute est la plus brutale est celle à reprendre.

Ces nombres comptent des ÉVÉNEMENTS, pas des personnes. Aucun identifiant n'est
enregistré, donc deux événements ne peuvent pas être rattachés au même visiteur.
Les pourcentages ci-dessous sont des rapports entre totaux, pas des taux de
conversion par personne — ils se comparent d'une semaine à l'autre, ils ne se
lisent pas comme « 30 % des visiteurs ont fait X ».

La clé de lecture reste dans ~/.config/boussole-celeste/mesure.cle : ce script la lit
et ne l'affiche jamais.
"""
import json, pathlib, sys, urllib.error, urllib.request

ADRESSE = "https://boussole-celeste.projectv0-0.workers.dev/mesure"
FICHIER_CLE = pathlib.Path.home() / ".config" / "boussole-celeste" / "mesure.cle"

# L'ordre du parcours, du premier au dernier pas.
ETAPES = [("accueil",    "Ouverture de l'accueil"),
          ("test-debut", "Test commencé"),
          ("test-fin",   "Test terminé"),
          ("paywall",    "Choix de formule affiché"),
          ("stripe",     "Départ vers le paiement")]

# Hors entonnoir : ce repère ne se place pas entre deux étapes, il compte les
# clics sur l'encart qui propose la carte à partager aux acheteurs de la formule
# simple. C'est le seul moyen de savoir si la réserver au dossier a servi.
A_COTE = [("promo-carte", "Clic sur la présentation du dossier")]


def charger(jours):
    # La clé part dans un en-tête : une adresse finit dans les journaux.
    cle = FICHIER_CLE.read_text(encoding="utf-8").strip()
    demande = urllib.request.Request(f"{ADRESSE}?jours={jours}", headers={
        "Authorization": f"Bearer {cle}", "User-Agent": "boussole-celeste-mesure"})
    try:
        with urllib.request.urlopen(demande, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"erreur": f"{e.code} {e.read().decode('utf-8', 'replace')}"}


def barre(part, largeur=28):
    plein = int(round(part * largeur))
    return "█" * plein + "·" * (largeur - plein)


def principal(jours):
    if not FICHIER_CLE.exists():
        print(f"Clé introuvable : {FICHIER_CLE}. Voir A-FAIRE.md.")
        return 1
    d = charger(jours)
    if "erreur" in d:
        print("le Worker a répondu :", d["erreur"])
        return 1

    totaux = {t["evenement"]: t["n"] for t in d.get("total", [])}
    print(f"Du {d.get('depuis','?')} à aujourd'hui · {d.get('jours','?')} jours\n")

    depart = totaux.get("accueil", 0)
    print("L'ENTONNOIR")

    # Les pertes d'abord, l'affichage ensuite : la marche à reprendre est la PLUS
    # haute, et on ne peut pas le savoir avant de les avoir toutes vues. Signaler
    # chaque chute forte séparément désignait trois étapes sur quatre, donc aucune.
    pertes, precedent = {}, None
    for cle, _ in ETAPES:
        n = totaux.get(cle, 0)
        if precedent:
            pertes[cle] = 100 * (1 - n / precedent)
        precedent = n
    pire = max(pertes, key=pertes.get) if pertes else None

    precedent = None
    for cle, nom in ETAPES:
        n = totaux.get(cle, 0)
        part = n / depart if depart else 0
        chute = ""
        if cle in pertes:
            chute = f"   −{pertes[cle]:.0f} %"
            if cle == pire:
                chute += "  ← c'est ici qu'on perd le plus"
        print(f"  {nom:<26} {n:>6}  {barre(part)}{chute}")
        precedent = n

    lus = totaux.get("article", 0)
    if lus:
        print(f"\n  {'Pages du guide ouvertes':<26} {lus:>6}"
              "   (elles ne passent pas par l'accueil)")

    articles = d.get("articles") or []
    if articles:
        print("\nLES PAGES DU GUIDE LES PLUS OUVERTES")
        for a in articles[:15]:
            nom = a["page"].replace("/guide/", "").replace(".html", "")
            print(f"  {nom:<46} {a['n']:>6}")

    for cle, nom in A_COTE:
        if totaux.get(cle):
            print(f"\nÀ CÔTÉ DE L'ENTONNOIR\n  {nom:<46} {totaux[cle]:>6}")

    parJour = d.get("parJour") or []
    if parJour:
        jours = sorted({l["jour"] for l in parJour}, reverse=True)[:14]
        index = {(l["jour"], l["evenement"]): l["n"] for l in parJour}
        cles = [c for c, _ in ETAPES] + ["article"]
        print("\nLES QUATORZE DERNIERS JOURS")
        print("  " + " " * 12 + "".join(f"{c[:8]:>10}" for c in cles))
        for j in jours:
            print(f"  {j:<12}" + "".join(f"{index.get((j, c), 0):>10}" for c in cles))

    if not totaux:
        print("Aucun événement enregistré pour l'instant.")
    return 0


if __name__ == "__main__":
    sys.exit(principal(int(sys.argv[1]) if len(sys.argv) > 1 else 30))
