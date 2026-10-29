"""Les textes de la page pilier du guide (guide/index.html), assemblée par outils/guide.py."""

TITLE = "Le guide de Boussole céleste : les 12 énergies du zodiaque"
DESCRIPTION = ("Les douze énergies du zodiaque, les éléments, les signes cardinaux, fixes et mutables, "
               "et des situations vécues : un guide pour se comprendre, sans prédiction.")
H1 = "Le guide : se comprendre par le langage du ciel"
INTRO = [
    "L'astrologie décrit douze grandes façons d'être au monde. Ce guide s'en sert comme d'un langage, pour mettre des mots sur ce que tu vis : quand tu fonces, quand tu tiens bon, quand tu te protèges, quand tu cherches ailleurs. Rien ici ne prédit quoi que ce soit.",
    "Chaque énergie porte le nom d'un signe, mais elle se désigne par un verbe : oser, ancrer, relier, protéger, rayonner, affiner, équilibrer, transformer, explorer, bâtir, libérer, ressentir. Tout le monde porte les douze en soi. Ce qui change, d'une personne à l'autre et d'une période à l'autre, c'est la place que chacune occupe.",
    "Tu peux lire ce guide dans l'ordre que tu veux. Les articles sur les énergies expliquent chacune d'elles, ses forces et ses excès. Les éléments et les façons d'avancer les regroupent en familles. Les situations vécues partent de ce qu'on se dit vraiment, un soir, en tapant une question dans un moteur de recherche.",
]
SECTIONS = [
    {"famille": "energie", "element": "feu", "titre": "Les énergies de Feu : agir",
     "intro": "Oser, rayonner, explorer : les trois énergies qui passent à l'action, chacune à sa façon. Le [Feu](element-feu.html) en astrologie, c'est l'élan."},
    {"famille": "energie", "element": "terre", "titre": "Les énergies de Terre : concrétiser",
     "intro": "Ancrer, affiner, bâtir : les trois énergies qui rendent les choses réelles et durables. La [Terre](element-terre.html), c'est le concret."},
    {"famille": "energie", "element": "air", "titre": "Les énergies d'Air : penser et relier",
     "intro": "Relier, équilibrer, libérer : les trois énergies des idées et des liens entre les gens. L'[Air](element-air.html), c'est la circulation."},
    {"famille": "energie", "element": "eau", "titre": "Les énergies d'Eau : ressentir",
     "intro": "Protéger, transformer, ressentir : les trois énergies de la vie intérieure et des attachements. L'[Eau](element-eau.html), c'est la profondeur."},
    {"famille": "element", "titre": "Les quatre éléments",
     "intro": "Le Feu, la Terre, l'Air et l'Eau regroupent les douze énergies trois par trois. Ils se lisent comme des tendances : ce qui domine en ce moment, et ce qui manque peut-être.",
     "ordre": ["element-feu", "element-terre", "element-air", "element-eau"]},
    {"famille": "modalite", "titre": "Les trois façons d'avancer",
     "intro": "Les signes cardinaux lancent, les signes fixes tiennent, les signes mutables s'adaptent. Trois rythmes, que tout le monde utilise, dans des proportions qui changent.",
     "ordre": ["energies-cardinales", "energies-fixes", "energies-mutables"]},
    {"famille": "situation", "titre": "Situations vécues",
     "intro": "Des moments que beaucoup de gens reconnaissent, et les énergies qui s'y jouent. Chaque article propose trois pistes concrètes, à essayer dès cette semaine."},
]
ENCART = ("Un langage, pas une prédiction",
          "Ce guide ne dit pas ce qui va t'arriver, et il ne remplace aucun professionnel. Il propose des mots et des pistes. Si une période te pèse durablement, en parler à un professionnel est une bonne porte.")
CTA = ("Et toi, quelles énergies prennent de la place en ce moment ?",
       "Le test de Boussole céleste mesure la place des douze énergies dans ta vie, à partir de seize situations du quotidien. Rien n'est prédit : tout part de tes réponses, qui ne quittent jamais ton navigateur.")
