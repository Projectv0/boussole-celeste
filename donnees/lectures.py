"""Les lectures croisées : croisements, ciels du moment, leviers, plan de 30 jours,
signe de naissance, page de suivi.

Toutes se lisent sur les PLACES (ce qu'une énergie occupe dans les réponses), sauf les
leviers et le plan qui parlent d'une note (« dépasse 7/10 »). Aucune règle ne se
déclenche sur une énergie non mesurée : c'est vérifié dans le code (listeCombos,
cielDuMoment, leviers, planTrenteJours) et par les auto-tests.

Variables entre accolades, remplacées par le site :
  {v1} {v2}      verbes des énergies concernées       {s1} {s2}  leurs signes
  {el} {el_art}  nom de l'élément, avec son article    {el_ids}   ses trois verbes
  {el_mode}      ce que fait l'élément (agir…)         {note}     une note « 7,4 »
  {mesures}     « 1 mesure », « 7 mesures »            {verbe}    le verbe d'une énergie
  {de_verbe}     « d'oser », « de bâtir » (élision)    {rang}     « 1re », « 2e » (position, féminin)
"""

SEUIL_HAUT = 5.5      # une place à partir de laquelle une énergie « occupe le terrain »
SEUIL_BAS = 2.5       # en dessous, une énergie est « très discrète »
SEUIL_OMBRE = 7       # au-delà, la fiche du dossier parle d'abord de l'excès
PALIERS = {"discrete": 3.5, "dominante": 7}   # discrète < 3,5 ≤ présente ≤ 7 < dominante

# ─── Les 15 croisements ───────────────────────────────────────────────────────
# type « paire » : les deux énergies mesurées et toutes deux ≥ SEUIL_HAUT.
# type « element_retrait » : les trois énergies de l'élément mesurées, moyenne ≤ SEUIL_BAS.
# type « element_domine » : un élément ≥ 5,5 et au moins 2 points au-dessus du suivant.
# type « modalite » : la première modalité ≥ 5 et au moins 2 points au-dessus de l'autre.

CROISEMENTS = [
  {"type": "paire", "a": "belier", "b": "capricorne", "titre": "Construire, et vite",
   "texte": "Oser et bâtir prennent ensemble beaucoup de place. Tu veux construire quelque chose de solide, et tu veux que ça avance vite. Ce mélange aide à faire aboutir les projets. Il peut aussi te mettre sous pression : tout lancer et tout porter en même temps fatigue. Choisir chaque semaine ce qui peut attendre allège la charge."},
  {"type": "paire", "a": "cancer", "b": "scorpion", "titre": "La loyauté qui retient",
   "texte": "Protéger et transformer occupent ensemble une grande place. Tes liens sont profonds, et tu y tiens fort. C'est une loyauté précieuse. Le revers, c'est de trop retenir : garder une relation qui fait mal, ou une blessure qu'on ne dit pas. Te demander si un lien te fait encore du bien, c'est sain : ce n'est pas une trahison."},
  {"type": "paire", "a": "gemeaux", "b": "sagittaire", "titre": "L'esprit qui ne se pose pas",
   "texte": "Relier et explorer sont tous deux très présents. Ton esprit cherche, apprend, saute d'une idée à l'autre et voit loin. C'est une richesse. Le risque, c'est de ne jamais t'arrêter assez longtemps pour approfondir. Choisir chaque mois une seule idée, et la creuser jusqu'au bout, donne souvent plus de satisfaction."},
  {"type": "paire", "a": "vierge", "b": "balance", "titre": "La peur de mal faire",
   "texte": "Affiner et équilibrer prennent ensemble beaucoup de place. Tu veux que ce soit bien fait, et que ce soit juste pour tout le monde. Cette double exigence peut rendre chaque décision très lourde. Décider qu'une solution assez bonne pour tous suffit, c'est souvent ce qui débloque."},
  {"type": "paire", "a": "lion", "b": "poissons", "titre": "Créer à fleur de peau",
   "texte": "Rayonner et ressentir sont tous deux très présents. Tu as envie de créer et de partager, et tu ressens tout avec intensité. C'est un terrain très fertile. Le revers, c'est qu'une critique ou un silence peut te toucher profondément. Créer d'abord pour toi, et montrer ensuite, protège ce qui compte."},
  {"type": "paire", "a": "belier", "b": "balance", "titre": "S'affirmer sans froisser",
   "texte": "Oser et équilibrer occupent ensemble une grande place. Tu as envie de dire les choses franchement, et tu tiens à ce que tout le monde reste en bons termes. Ces deux élans tirent parfois en sens contraire. Dire ton avis tôt, avec douceur, t'évite de le garder trop longtemps puis de le lâcher d'un coup."},
  {"type": "paire", "a": "taureau", "b": "scorpion", "titre": "Garder, puis tout changer",
   "texte": "Ancrer et transformer prennent ensemble beaucoup de place. Tu tiens à ce qui est stable, et tu sens en même temps un besoin de changement profond. Souvent, ça donne une longue période où rien ne bouge, puis un grand bouleversement d'un coup. De petits ajustements réguliers aident à l'éviter."},
  {"type": "paire", "a": "cancer", "b": "capricorne", "titre": "Le foyer et le devoir",
   "texte": "Protéger et bâtir occupent ensemble une grande place. Tu prends soin des tiens et tu portes des responsabilités. C'est une force sur laquelle beaucoup de gens s'appuient. Le risque, c'est de ne garder aucune place pour toi. Une soirée par semaine sans obligation ne retire rien à personne."},
  {"type": "paire", "a": "lion", "b": "verseau", "titre": "Briller sans entrer dans le moule",
   "texte": "Rayonner et libérer sont tous deux très présents. Tu aimes qu'on remarque ce que tu apportes, et tu tiens à ta liberté. C'est un mélange original : tu aimes être dans la lumière, mais pas dans un cadre imposé. Ça demande de choisir des endroits où tu peux briller à ta façon, sans te plier aux attentes des autres."},
  {"type": "paire", "a": "vierge", "b": "poissons", "titre": "Le détail et le flou",
   "texte": "Affiner et ressentir prennent ensemble beaucoup de place. Tu vois les détails avec précision, et tu perçois aussi ce qui ne se dit pas. Ces deux regards se complètent bien. Ils peuvent aussi se contredire : tu sens que quelque chose ne va pas, sans réussir à dire quoi. Écrire ce que tu ressens aide à le préciser."},
  {"type": "paire", "a": "taureau", "b": "verseau", "titre": "Tenir et tout bousculer",
   "texte": "Ancrer et libérer occupent ensemble une grande place. Tu as besoin de repères stables, et en même temps d'air et de nouveauté. Ces deux besoins sont légitimes. Le plus simple est souvent de leur donner chacun un terrain : un quotidien bien réglé, et un espace où tu changes tout ce que tu veux."},
  {"type": "element_retrait", "titre": "Un élément en retrait",
   "texte": "Les trois énergies de l'élément {el} ({el_ids}) restent très discrètes dans tes réponses. Ce n'est pas un défaut : c'est la place qu'elles ont prise dans ces scènes-là. Si tu veux leur faire plus de place, {piste}",
   "pistes": {
     "feu": "oser une petite chose chaque semaine est une bonne porte d'entrée.",
     "terre": "un rituel concret et régulier est une bonne porte d'entrée.",
     "air": "une conversation ou une lecture nouvelle chaque semaine est une bonne porte d'entrée.",
     "eau": "quelques minutes par jour pour écouter ce que tu ressens sont une bonne porte d'entrée.",
   }},
  {"type": "element_domine", "titre": "Un élément qui prend toute la place",
   "texte": "{El_art}{el} domine nettement ton profil : {el_ids} pèsent plus que tout le reste. En ce moment, tu vis surtout sur le mode « {el_mode} ». C'est ce qui donne le ton à cette période. Garde un œil sur l'élément le plus en retrait, {bas_art}{bas} : c'est souvent là que se trouve ce qui manque."},
  {"type": "modalite", "haut": "cardinal", "bas": "fixe", "titre": "Lancer plus que tenir",
   "texte": "Les énergies qui lancent (oser, protéger, équilibrer, bâtir) pèsent bien plus que celles qui tiennent (ancrer, rayonner, transformer, libérer). Tu démarres facilement, et tu tiens moins longtemps. Ça n'a rien d'un défaut. Avant de commencer une nouvelle chose, demande-toi laquelle des anciennes tu veux vraiment finir."},
  {"type": "modalite", "haut": "fixe", "bas": "mutable", "titre": "Tenir plus que s'adapter",
   "texte": "Les énergies qui tiennent (ancrer, rayonner, transformer, libérer) pèsent bien plus que celles qui s'adaptent (relier, affiner, explorer, ressentir). Tu restes fidèle à tes choix, et on peut compter sur toi. Le revers, c'est la difficulté à changer de cap quand la situation bouge. Faire chaque semaine une petite chose autrement assouplit tes habitudes sans rien casser."},
]

# ─── Ton ciel du moment ──────────────────────────────────────────────────────
# Lu sur le duo dominant (les deux énergies les plus présentes, mesurées, places ≥ 4),
# selon la paire d'éléments. Une règle par paire : dix au total, sans trou.
# Le site écrit d'abord « {V1} et {v2} prennent le plus de place en ce moment. »,
# puis la phrase de la règle, puis « C'est une saison, pas une identité. »

CIEL_PLANCHER = 4
CIELS = [
  {"elements": ("feu", "terre"), "titre": "Le feu qui bâtit",
   "phrase": "Tu vis une saison de réalisation : tu lances, puis tu construis. C'est une période où les choses peuvent vraiment aboutir. Pense à te faire aider."},
  {"elements": ("feu", "air"), "titre": "Le vent qui attise",
   "phrase": "Tu vis une saison d'idées et d'action : ce que tu penses, tu as envie de le faire, et vite. Pense à vérifier que les autres suivent."},
  {"elements": ("feu", "eau"), "titre": "La flamme sensible",
   "phrase": "Tu vis une saison intense : tu agis avec le cœur, et tu ressens fort ce qui arrive. Pense à te laisser des temps de calme entre deux élans."},
  {"elements": ("terre", "air"), "titre": "Le plan qui se dessine",
   "phrase": "Tu vis une saison d'organisation : tu réfléchis et tu concrétises, et les idées deviennent des plans. Pense à garder de la place pour l'imprévu."},
  {"elements": ("terre", "eau"), "titre": "L'eau qui veille",
   "phrase": "Tu vis une saison de soin et de stabilité : tu protèges, tu tiens, tu veilles sur ce qui compte. Pense à te compter parmi les personnes dont tu t'occupes."},
  {"elements": ("air", "eau"), "titre": "L'air qui rêve",
   "phrase": "Tu vis une saison d'imagination : tu penses et tu ressens beaucoup, et les idées se mêlent aux émotions. Pense à faire d'un de ces rêves un petit geste concret."},
  {"elements": ("feu", "feu"), "titre": "Le feu qui avance",
   "phrase": "Tu vis une saison d'élan : tu avances, tu entraînes les autres, tu as envie que ça bouge. Pense à garder un peu de souffle pour la suite."},
  {"elements": ("terre", "terre"), "titre": "La terre qui tient",
   "phrase": "Tu vis une saison de construction et de stabilité : tu poses des bases, tu tiens bon. Pense à t'accorder aussi des moments sans objectif."},
  {"elements": ("air", "air"), "titre": "L'air qui cherche",
   "phrase": "Tu vis une saison de questions et d'échanges : tu réfléchis, tu fais circuler les idées, tu mets les gens en contact. Pense à choisir, de temps en temps, une idée à mettre en pratique."},
  {"elements": ("eau", "eau"), "titre": "L'eau profonde",
   "phrase": "Tu vis une saison intérieure : tu ressens beaucoup, tu tiens à tes liens, tu vas au fond des choses. Pense à dire ce que tu ressens, plutôt que de tout garder."},
]
CIEL_FIN = "C'est une saison, pas une identité."
# Replis, quand le duo n'est pas assez net (deuxième place < CIEL_PLANCHER) :
CIEL_ELEMENT = {   # un élément au moins 1,5 point au-dessus des autres
  "titre": {"feu": "Le Feu en tête", "terre": "La Terre en tête", "air": "L'Air en tête", "eau": "L'Eau en tête"},
  "phrase": "Aucune énergie ne domine seule, mais {el_art}{el} pèse plus que le reste : {el_ids} donnent le ton. En ce moment, tu vis surtout sur le mode « {el_mode} ».",
}
CIEL_PARTAGE = {"titre": "Le ciel partagé",
  "phrase": "Aucune énergie et aucun élément n'écrasent les autres. Tes réactions changent avec les situations, plutôt que de suivre un seul pli. C'est une souplesse, même si le portrait est moins tranché."}
CIEL_VOILE = {"titre": "Le ciel voilé",   # moins de deux énergies avec une place au-dessus de zéro
  "phrase": "Tes réponses ont laissé presque toutes les énergies au plus bas. Il n'y a pas assez de matière pour dessiner un ciel. Ce n'est pas un verdict : refais le test un autre jour, ou commence par noter quelques moments dans ton journal."}

# ─── Les trois leviers du dossier ─────────────────────────────────────────────
# Le titre de la section suit le nombre réellement produit (« Tes deux leviers »…).
LEVIERS = {
  "force": {"quand": "Cette semaine", "titre": "Ta force du moment",
    "pourquoi": "{Verbe} est l'énergie qui prend le plus de place chez toi en ce moment ({note}/10, sur {mesures}). C'est sur elle que tu peux t'appuyer pour avancer sur ce qui compte.",
    "pratique": 2},
  "retrait": {"quand": "La semaine suivante", "titre": "Ce qui manque peut-être",
    "pourquoi": "{Verbe} est l'énergie la plus en retrait parmi celles que le test a mesurées ({note}/10). Ce n'est pas un manque à combler à tout prix : c'est une piste, si tu sens qu'elle te ferait du bien.",
    "pratique": 0, "seulement_sous": 4},
  "ombre": {"quand": "Quand les deux premiers seront installés", "titre": "L'excès à surveiller",
    "pourquoi": "{Verbe} dépasse 7/10. Quand une énergie prend autant de place, son excès se fait souvent sentir : {ombre}. Cette pratique aide à garder ce qu'elle a de bon, sans le trop-plein.",
    "pratique": "apaiser"},
  "appui": {"quand": "Quand les deux premiers seront installés", "titre": "Un second appui",
    "pourquoi": "{Verbe} arrive juste après ({note}/10). C'est un second appui, sur lequel tu peux compter quand le premier fatigue.",
    "pratique": 2, "seulement_dessus": 4},
}

# ─── Le plan de 30 jours ─────────────────────────────────────────────────────
PLAN = {
  "s1": {"titre": "Semaine 1 — Observer et nommer",
    "texte": "Chaque soir, prends une minute pour te demander quelle énergie a pris le plus de place dans ta journée : as-tu surtout osé, protégé, exploré, bâti ? Note-la en un mot dans ton journal, avec le moment qui l'a montrée. Ne cherche rien à changer : cette semaine, on regarde."},
  "s2": {"titre": "Semaine 2 — Faire une place à l'énergie {de_verbe}",
    "texte": "C'est l'énergie la plus discrète de ton profil ({note}/10). Cette semaine, essaie ceci : « {p0} » Puis, si tu en as envie, va plus loin : « {p2} »"},
  "s3_ombre": {"titre": "Semaine 3 — Tempérer l'énergie {de_verbe}",
    "texte": "{Verbe} dépasse 7/10 : c'est ta force, et c'est aussi là que l'excès guette ({ombre}). Cette semaine : « {pa} » Et garde un œil sur ce signal : {signal}."},
  "s3_force": {"titre": "Semaine 3 — Cultiver ta force",
    "texte": "{Verbe} est l'énergie la plus présente de ton profil, sans excès. Cette semaine, appuie-toi sur elle : « {p0} »"},
  "s4": {"titre": "Semaine 4 — Garder ce qui a marché",
    "texte": "Relis tes notes des trois semaines. Garde les deux pratiques qui t'ont fait le plus de bien, et donne-leur une place fixe dans ton agenda. Puis, à J30, refais le test et remplis la page de suivi : compare ce qui a bougé, sans te juger."},
}

SUIVI = {
  "titre": "Ta page de suivi, à J30",
  "intro": "Refais le test trente jours après celui-ci, puis remplis cette page à la main. Elle sert à voir ce qui a bougé, pas à te noter.",
  "questions": [
    "Quelle pratique as-tu gardée ? Qu'est-ce qu'elle t'a apporté ?",
    "Quelle énergie a le plus changé entre les deux tests ? Est-ce que ça correspond à ce que tu as vécu ?",
    "Qu'est-ce qui a été plus difficile que prévu ?",
    "Quelle énergie veux-tu nourrir le mois prochain, et par quel premier geste ?",
  ],
}

# ─── Le signe de naissance (facultatif, après les résultats) ──────────────────
SIGNE = {
  "titre": "Et ton signe de naissance ?",
  "intro": "Si tu veux, indique ton jour et ton mois de naissance. On ne te demande ni l'année, ni l'heure, ni le lieu. Le calcul se fait dans ton navigateur, et rien n'est envoyé.",
  "limite": "Ce jour-là, le Soleil change de signe, et le jour exact varie d'une année à l'autre. Choisis le signe qu'on t'a toujours donné :",
  "meme": "Ton signe de naissance, {s0}, est aussi celui de ton énergie la plus présente en ce moment : {v1}. Certaines personnes s'y reconnaissent, d'autres y voient un hasard. C'est une chose à regarder, rien de plus.",
  "element": "Ton signe de naissance, {s0}, et ton énergie la plus présente, {v1} ({s1}), partagent le même élément : {el_art}{el}. Ce n'est pas la même énergie, mais les deux parlent un peu la même langue. Regarde si tu t'y retrouves.",
  "modalite": "Ton signe de naissance, {s0}, et ton énergie la plus présente, {v1} ({s1}), partagent la même façon d'avancer : les deux {mod_mode}. Ce n'est pas la même énergie, mais il y a un air de famille. Regarde si tu t'y retrouves.",
  "autre": "Ton signe de naissance, {s0}, n'est pas de la même famille que ton énergie la plus présente en ce moment, {v1}. C'est fréquent, et c'est tout l'intérêt de mesurer : ce que tu vis aujourd'hui ne se résume pas à une date.",
  "rang": "Dans ton profil, l'énergie de ton signe ({v0}) arrive en {rang} position, à {note}/10.",
  "garde": "Ton signe reste dans ce navigateur. Il n'entre dans aucun calcul, et tu peux l'effacer quand tu veux.",
  "mod_mode": {"cardinal": "lancent les choses", "fixe": "tiennent dans la durée", "mutable": "s'adaptent"},
}

# Date de début de chaque signe (jour, mois). Le jour précédent et ce jour-là sont des
# « jours limites » : selon l'année, le Soleil y entre ou non dans le signe, et le site
# propose alors les deux.
DEBUTS = [("capricorne", 22, 12), ("verseau", 20, 1), ("poissons", 19, 2), ("belier", 21, 3),
          ("taureau", 20, 4), ("gemeaux", 21, 5), ("cancer", 21, 6), ("lion", 23, 7),
          ("vierge", 23, 8), ("balance", 23, 9), ("scorpion", 23, 10), ("sagittaire", 22, 11)]

# ─── Phrases fixes ────────────────────────────────────────────────────────────
RAPPEL_RESULTATS = "L'astrologie sert ici de langage pour réfléchir à toi : elle ne prédit rien, et ne remplace aucun professionnel."
NON_MESUREE = "Pas mesurée dans ce test"
DOUCE = "Si une période te pèse durablement, en parler à un professionnel est une bonne porte."
