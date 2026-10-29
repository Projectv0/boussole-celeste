# Boussole céleste

Un test par mises en situation qui mesure la place de douze énergies (une par signe du
zodiaque) dans la vie de quelqu'un en ce moment, avec un journal, des résultats notés, un
dossier complet et un guide. L'astrologie y sert de langage de réflexion : rien n'est prédit.
Jumeau de Boussole émotionnelle.

Tout tient dans `index.html`, une page autonome (HTML, CSS et JS en ligne, sans dépendance
ni build côté navigateur), assemblée par un script :

```bash
python3 outils/construire.py      # vérifie la banque, puis écrit index.html et sw.js
python3 outils/relecture.py       # contraintes du test, rotations, donnees/RELECTURE.md
python3 outils/legal.py           # pages légales (en ligne, et version SAS du jour J)
```

| Dossier | Contenu |
|---|---|
| `donnees/` | tous les textes : énergies, situations, lectures croisées |
| `site/` | le style, les vues et le code de la page (`site/VERSION` nomme le cache) |
| `outils/` | assemblage, relecture, constellations, glyphes, icônes, image de partage |
| `legal/` | mentions légales, confidentialité, conditions de vente |
| `worker/` | le Worker Cloudflare : vérification d'achat, mesure, code à offrir |
| `da/` | les planches de direction artistique |

Les polices TTF des scripts PIL ne sont pas versionnées :

```bash
mkdir -p polices/ttf && cd polices/ttf && for f in "cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf" "jost/Jost%5Bwght%5D.ttf"; do curl -sLO "https://github.com/google/fonts/raw/main/ofl/$f"; done
```

Ce qui reste à faire, et qui demande un compte ou une décision : `A-FAIRE.md`.
