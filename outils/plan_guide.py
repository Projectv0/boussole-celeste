"""Le plan du guide : les 39 articles prévus, leur famille, leurs énergies, leur titre de travail.

Sert de liste de référence aux rédacteurs et au contrôle des liens (un article peut
renvoyer vers un autre qui n'est pas encore écrit, tant qu'il est au plan).
"""

ENERGIES = [
    ("energie-belier", "belier", "L'énergie Bélier : oser, et quand ça déborde"),
    ("energie-taureau", "taureau", "L'énergie Taureau : ancrer, et quand ça fige"),
    ("energie-gemeaux", "gemeaux", "L'énergie Gémeaux : relier, et quand ça disperse"),
    ("energie-cancer", "cancer", "L'énergie Cancer : protéger, et quand ça enferme"),
    ("energie-lion", "lion", "L'énergie Lion : rayonner, et quand on attend trop le regard des autres"),
    ("energie-vierge", "vierge", "L'énergie Vierge : affiner, et quand rien n'est assez bien"),
    ("energie-balance", "balance", "L'énergie Balance : équilibrer, et quand on n'ose plus trancher"),
    ("energie-scorpion", "scorpion", "L'énergie Scorpion : transformer, et quand ça veut tout contrôler"),
    ("energie-sagittaire", "sagittaire", "L'énergie Sagittaire : explorer, et quand ça devient une fuite"),
    ("energie-capricorne", "capricorne", "L'énergie Capricorne : bâtir, et quand ça devient trop lourd"),
    ("energie-verseau", "verseau", "L'énergie Verseau : libérer, et quand ça éloigne des autres"),
    ("energie-poissons", "poissons", "L'énergie Poissons : ressentir, et quand ça submerge"),
]
ELEMENTS = [
    ("element-feu", ["belier", "lion", "sagittaire"], "Le Feu en astrologie : oser, rayonner, explorer"),
    ("element-terre", ["taureau", "vierge", "capricorne"], "La Terre en astrologie : ancrer, affiner, bâtir"),
    ("element-air", ["gemeaux", "balance", "verseau"], "L'Air en astrologie : relier, équilibrer, libérer"),
    ("element-eau", ["cancer", "scorpion", "poissons"], "L'Eau en astrologie : protéger, transformer, ressentir"),
]
MODALITES = [
    ("energies-cardinales", ["belier", "cancer", "balance", "capricorne"], "Les signes cardinaux : les énergies qui lancent"),
    ("energies-fixes", ["taureau", "lion", "scorpion", "verseau"], "Les signes fixes : les énergies qui tiennent"),
    ("energies-mutables", ["gemeaux", "vierge", "sagittaire", "poissons"], "Les signes mutables : les énergies qui s'adaptent"),
]
SITUATIONS = [
    ("vouloir-tout-controler", ["scorpion", "capricorne"], "Pourquoi je veux tout contrôler"),
    ("ne-pas-arriver-a-se-decider", ["balance", "vierge"], "Je n'arrive pas à me décider"),
    ("besoin-qu-on-me-voie", ["lion"], "J'ai besoin qu'on me voie"),
    ("s-ennuyer-des-que-c-est-acquis", ["sagittaire", "verseau"], "Je m'ennuie dès que c'est acquis"),
    ("fuir-quand-ca-devient-serieux", ["verseau", "sagittaire"], "Je fuis dès que ça devient sérieux"),
    ("dire-oui-pour-ne-pas-deplaire", ["balance", "cancer"], "Je dis oui pour ne pas déplaire"),
    ("ruminer-une-remarque", ["scorpion", "vierge"], "Je rumine une remarque pendant des jours"),
    ("tout-commencer-rien-finir", ["belier", "gemeaux"], "Je commence tout et je ne finis rien"),
    ("ne-pas-arriver-a-changer-ses-habitudes", ["taureau"], "Je n'arrive pas à changer mes habitudes"),
    ("rien-n-est-jamais-assez-bien", ["vierge", "capricorne"], "Rien de ce que je fais n'est assez bien"),
    ("s-occuper-de-tous-sauf-de-soi", ["cancer", "poissons"], "Je m'occupe de tout le monde, sauf de moi"),
    ("absorber-les-emotions-des-autres", ["poissons", "cancer"], "J'absorbe les émotions des autres"),
    ("s-emporter-trop-vite", ["belier"], "Je m'emporte trop vite"),
    ("tout-porter-sur-ses-epaules", ["capricorne", "cancer"], "Je porte tout sur mes épaules"),
    ("ne-pas-se-sentir-comme-les-autres", ["verseau"], "Je ne me sens pas comme les autres"),
    ("l-esprit-qui-part-dans-tous-les-sens", ["gemeaux", "sagittaire"], "Mon esprit part dans tous les sens"),
    ("ne-pas-arriver-a-tourner-la-page", ["scorpion", "taureau"], "Je n'arrive pas à tourner la page"),
    ("rever-sa-vie-plus-que-la-vivre", ["poissons", "sagittaire"], "Je rêve ma vie plus que je ne la vis"),
    ("ne-pas-oser-se-montrer", ["lion", "belier"], "Je n'ose pas me montrer"),
    ("ne-pas-arriver-a-se-reposer", ["capricorne", "taureau"], "Je n'arrive pas à me reposer"),
]


def tous():
    return ([(s, "energie", [e], t) for s, e, t in ENERGIES]
            + [(s, "element", ids, t) for s, ids, t in ELEMENTS]
            + [(s, "modalite", ids, t) for s, ids, t in MODALITES]
            + [(s, "situation", ids, t) for s, ids, t in SITUATIONS])


SLUGS = {s for s, *_ in tous()}
