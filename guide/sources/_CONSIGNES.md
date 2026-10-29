# Consignes de rédaction du guide — Boussole céleste

Boussole céleste est un site de réflexion sur soi qui utilise l'astrologie comme un
**langage**, jamais comme une prédiction. Il mesure, par un test de seize situations, la
place que douze « énergies » (une par signe, désignées par un verbe : oser, ancrer, relier,
protéger, rayonner, affiner, équilibrer, transformer, explorer, bâtir, libérer, ressentir)
prennent dans la vie de quelqu'un en ce moment. Le guide, en accès libre, amène les
lecteurs vers le test : chaque article doit être utile en lui-même.

## Les fichiers à lire avant d'écrire

- `guide/sources/energie-belier.md` : **l'article modèle**. Ton, longueur, structure, format.
- `outils/guide.py` : le format des sources (en tête du fichier) et les contrôles.
- `outils/plan_guide.py` : la liste des 39 articles (slug, famille, énergies, titre de travail).
  Tu peux faire des liens vers n'importe lequel, même s'il n'est pas encore écrit.
- `donnees/energies.py` : la fiche de chaque énergie (verbe, élément, modalité, planète,
  lumière, ombre, définition, manifestations). C'est la référence de fond : reste cohérent
  avec elle.

## Le format, en bref

Un fichier `guide/sources/<slug>.md` par article : un en-tête (`titre`, `title` si le titre
dépasse 60 caractères, `description` de 110 à 160 caractères, `famille`, `energies`, `cta`),
puis le chapeau, puis **exactement sept `## `**, **exactement trois `### 1.`, `### 2.`,
`### 3.`** (les pratiques, dans la même section), **un `!doux`** et **un `!attention`**.
**880 à 1 070 mots.** Écris les apostrophes droites (') : elles sont converties à
l'affichage. Paragraphes séparés par une ligne vide. Mise en valeur : `**gras**`, `*italique*`,
liens `[texte](slug.html)`. **Au moins deux liens internes** dans le corps, vers des articles
du plan (l'article de l'énergie concernée, une situation proche…).

Vérifie chaque article avec :

```bash
python3 outils/guide.py --verifier <slug> [<slug> …]
```

Il doit afficher ✓ et aucun « ? orthographe » (à part un nom propre évident). Corrige jusqu'à
ce que ce soit le cas.

## Le ton : un ami qui explique au café

- **Tutoiement**, chaleureux, sans condescendance.
- **Phrases complètes**, avec un sujet et un verbe. **Une idée par phrase.** Phrases courtes
  à moyennes (25 mots au plus, l'essentiel sous 18).
- **Le concret avant l'abstrait** : une scène, un geste, une phrase qu'on se dit, puis l'idée.
- **Jamais de maxime à décoder** (« la colère est une boussole qui… », « l'ombre éclaire… »),
  jamais de métaphore filée obscure, jamais de fragment sans verbe pour faire joli.
- Chaque phrase **se lit à voix haute sans buter**.
- Pas de listes à puces dans le corps : des paragraphes.

## Les interdits, absolus

- **Le mot « gratuit »**, sous aucune forme (ni « gratuitement »). Écris « sans frais » s'il le faut.
- **Aucun prix**, aucune mention de paiement, de dossier payant ou de formule.
- **Aucune étiquette sur une personne** : jamais « tu es Bélier », « les Lions sont… »,
  « les natifs de… », « si tu es Scorpion ». On parle d'**une énergie** et de **sa place** :
  « l'énergie d'oser », « quand cette énergie prend beaucoup de place chez toi ».
- **Aucune prédiction**, aucun « les astres », aucun horoscope, aucune compatibilité
  amoureuse entre signes, aucun ascendant. L'astrologie est un vocabulaire ancien qui aide à
  nommer, rien de plus. Chaque article d'énergie, d'élément ou de modalité le rappelle
  simplement dans sa dernière section.
- **Aucune allégation de santé, aucun diagnostic** : pas de « trouble », « dépression »,
  « burn-out », « TOC », « hypersensible », « HPI », « anxiété généralisée », « thérapie »,
  « symptôme », « guérir », « soigner », « traitement ». On parle de ce qu'on vit, pas de
  catégories cliniques. L'encart `!attention` oriente doucement vers un professionnel
  (« ton médecin, ou un psychologue ») quand ça dure et que ça pèse. Les numéros d'urgence
  (le 3114, numéro national de prévention du suicide, joignable jour et nuit ; le 15) ne
  figurent **que** dans un article où le sujet peut toucher une détresse profonde.
- **Non genré** : le lecteur n'a pas de genre. Pas d'adjectif ni de participe accordé à
  « tu » ou « te » : évite « sûr », « prêt », « seul », « content », « fatigué », « vexé »,
  « déçu », « blessé », « perdu », « épuisé », « fier »… Reformule (« ça te fatigue », « tu
  manques de repères », « sans aide ») ; à la rigueur, rarement, la forme « fatigué·e ». Les
  tiers peuvent être genrés (« un collègue », « ta sœur ») ; préfère des prénoms épicènes
  (Camille, Alex, Sacha) quand il faut un exemple.
- **Ne recopie pas les pratiques du dossier** (`donnees/energies.py`, champ `pratiques`) :
  ce dossier est le contenu vendu. Les trois pratiques du guide doivent être **les tiennes**,
  concrètes, faisables cette semaine, décrites en trois à cinq phrases.

## Les plans types (sept sections)

Les intitulés peuvent varier, la logique non.

**Énergie** (`energie-…`) : 1. ce qu'on appelle cette énergie · 2. comment elle se manifeste
(corps, tête, gestes) · 3. à quoi elle sert · 4. quand elle déborde (son ombre) · 5. quand
elle manque · 6. trois pratiques (les trois `###`, suivies de l'encart `!attention`) · 7. ce
que l'astrologie en dit, et ce qu'elle n'en dit pas (élément, modalité, planète, puis le
rappel : un langage, pas une prédiction). Titre du CTA : « Quelle place prend l'énergie
de … dans ta vie ? ».

**Élément** (`element-…`) et **modalité** (`energies-…`) : 1. ce que désigne cet élément
(ou cette famille) · 2. les trois (ou quatre) énergies qui le composent, chacune en un
paragraphe, avec un lien vers son article · 3. comment on le reconnaît au quotidien ·
4. quand il domine · 5. quand il manque · 6. trois pratiques · 7. ce que l'astrologie en dit,
et ce qu'elle n'en dit pas. Pour les modalités : cardinal = lancer, fixe = tenir, mutable =
s'adapter ; « signe cardinal » est le terme que les gens cherchent, explique-le simplement.

**Situation vécue** (les 20 autres) : le titre est une phrase que les gens tapent vraiment
dans un moteur de recherche (« Pourquoi je veux tout contrôler »). 1. la scène, telle qu'on
la vit (concrète, reconnaissable, sans jugement) · 2. pourquoi ça arrive (ce que ce
comportement protège ou cherche) · 3. l'énergie en jeu, avec un lien vers son article
(« en langage astrologique, c'est l'énergie de… ») · 4. ce que ça coûte, et ce que ça
apporte quand même · 5. trois pistes concrètes (les trois `###`) · 6. une section où l'encart
`!attention` a sa place (quand en parler à quelqu'un) · 7. pour finir, le regard à garder
(sans morale). Titre du CTA : une question tournée vers le test (« Et toi, quelles énergies
prennent de la place en ce moment ? »).

## L'encart doux

Il apporte une nuance qui rassure ou qui éclaire (« Ce n'est pas la même chose que… »,
« Tout le monde fait ça parfois »), en trois ou quatre phrases. Pas de conseil médical.

## Le référencement, sans rien forcer

- Le `titre` (h1) reprend le titre de travail du plan, que tu peux affiner.
- Le `title` (balise de la page) fait 60 caractères au plus : mets l'essentiel au début.
- La `description` dit en 110 à 160 caractères ce que la personne va trouver, avec les mots
  qu'elle a tapés.
- Le chapeau et la première section emploient naturellement ces mots-là.
