# Ce que tu as à faire — Boussole céleste

*État au 29 octobre 2026. Ce document ne liste que ce qui demande un compte, une identité,
de l'argent ou un arbitrage, donc toi. Je le tiens à jour à chaque livraison.*

## Où on en est

| Étape (§ 12 du cahier des charges) | État |
|---|---|
| 1. Lire Boussole, poser les questions | ✅ 29/10 |
| 2. Nom et direction artistique | ✅ **Boussole céleste**, thème **nuit étoilée** (29/10) |
| 3. Les contenus | ✅ validés le 29/10 (`donnees/RELECTURE.md`) |
| 4. Le site, en mode test | ✅ testé sur téléphone le 30/10 |
| 5. Le guide (39 articles + la page pilier) | ⏸ **à lire : cinq articles au hasard** |
| 6. Le Worker (vérification, mesure, code à offrir) | code prêt dans `worker/`, à déployer |
| 7. Publications et vidéos | à venir |

**Le site ne vend rien aujourd'hui** : `modeTest: true`, aucun lien de paiement. La fenêtre
de fin de test s'affiche, et le bouton « Passer le paiement — version test » ouvre tout.
Tant que le domaine n'est pas branché, la page demande aux moteurs de ne pas l'indexer
(`noindex`) : elle s'ouvrira d'elle-même le jour où le fichier `CNAME` existera.

---

# A — Maintenant, sans attendre la société

## A1 · Acheter le domaine — le seul point urgent

`boussole-celeste.fr` **et** `boussole-celeste.com` étaient libres le 29 octobre 2026.
Achète-les chez IONOS, comme Boussole. Je ne touche ni à l'achat, ni à la zone DNS.

Quand c'est fait, dis-le-moi : je pose le fichier `CNAME`, et je te donne les
enregistrements DNS à créer pour GitHub Pages (les mêmes que pour Boussole).

## A2 · L'adresse de contact

Ton choix du 29/10 : comme Boussole. Dans IONOS, crée une **redirection** de
`contact@boussole-celeste.fr` vers `contact@odem-app.com`. Les pages du site affichent déjà
cette adresse : **tant que la redirection n'existe pas, un message envoyé là se perd.**

> À corriger avant la première vente, comme pour Boussole : une redirection reçoit, mais les
> réponses partent de `contact@odem-app.com`, au nom de Jimmy Blettner.

## A3 · La marque — au nom de la SAS, plus tard

Vérifié le 29/10 dans TMview (marques françaises et européennes) : aucune marque « Boussole
céleste ». À savoir : « BOUSSOLE » seule est déposée par WAKE UP (2017, classes 9, 35, 41,
42, 44), et « LA BOUSSOLE » par l'Université de Tours (classes 9, 16, 21, 28, 41, 42). C'est
le même risque que pour Boussole émotionnelle. Un dépôt **semi-figuratif** (le nom et la
roue) le réduit. Classes à viser : 9, 41, 42. Le dépôt se fait **au nom de la SAS**. Les
noms de société n'ont pas été vérifiés : data.inpi.fr affichait une vérification anti-robot.

## A4 · Search Console et Bing — dès que le domaine répond

Le guide compte 39 articles et un sitemap de 41 adresses. Tant que le domaine n'est pas
branché, toutes les pages portent `noindex` : rien ne s'indexe sur l'adresse provisoire. Le
jour où `boussole-celeste.fr` répond, je retire `noindex` et je republie. Ensuite :

1. Dans **Google Search Console**, ajoute une propriété à préfixe d'URL
   `https://boussole-celeste.fr/`, méthode « balise HTML ». Donne-moi la balise : je la pose
   dans l'accueil, puis tu cliques sur « Valider ». Ensuite, envoie le sitemap
   `https://boussole-celeste.fr/sitemap.xml`.
2. Même chose dans **Bing Webmaster Tools**, en ajoutant le site à la main. N'accepte ni
   l'import depuis Search Console, ni la connexion à IONOS : ce sont les deux voies que tu
   avais écartées pour Boussole.

## A5 · Les comptes réseaux — plus tard, à l'étape 7

Ton choix du 29/10 : des comptes à part. Instagram et TikTok, que tu crées toi-même le
moment venu. Je te préparerai les noms, la bio et la photo de profil (`logo-instagram.png`
est prêt).

---

# B — Pouvoir vendre (bloqué par la société)

Les mêmes étapes que pour Boussole (son `A-FAIRE.md`, bloc B), et les mêmes sept champs du
Kbis : ils serviront aux deux sites. Les pages légales version SAS sont prêtes dans
`societe/site-jour-J/` (hors dépôt), générées par `outils/legal.py` : il suffira d'y écrire
les champs, le médiateur et le téléphone.

### Les trois produits Stripe, le jour venu

Sur le compte Stripe de la SAS, en production :

| Produit | Prix | URL de retour |
|---|---|---|
| Boussole céleste — Tes résultats | 1,99 € | `https://boussole-celeste.fr/merci.html?formule=resultats&session_id={CHECKOUT_SESSION_ID}` |
| Boussole céleste — Résultats + Dossier complet | 5,99 € | `https://boussole-celeste.fr/merci.html?formule=dossier&session_id={CHECKOUT_SESSION_ID}` |
| Boussole céleste — Complément dossier | 4,00 € | `https://boussole-celeste.fr/merci.html?formule=dossier&session_id={CHECKOUT_SESSION_ID}` |

Sur les trois liens : « Exiger l'acceptation des conditions de vente » avec l'URL
`https://boussole-celeste.fr/legal/cgv.html`, et la collecte de l'adresse e-mail. Dans les
réglages des reçus : « Vous avez accepté les conditions de vente et renoncé à votre droit de
rétractation pour un accès immédiat. »

**Ce que tu me donnes ensuite :** les trois liens **et les trois identifiants de prix**
(`price_…`). Ici, ils sont indispensables, et pas seulement utiles :

> **Un seul compte Stripe pour deux sites.** Les deux sites vendent aux mêmes montants. Le
> Worker de Boussole céleste reconnaît donc un achat à son identifiant de prix, et refuse
> tout le reste. **Le Worker de Boussole émotionnelle, lui, se fie encore au montant** : le
> jour où les deux vendent sur le même compte, un achat de Boussole céleste ouvrirait
> Boussole émotionnelle. À corriger là-bas avant la première vente des deux (une demi-heure
> de travail, sur le modèle de `worker/verification.js` ici).

---

## Ce que tu dois savoir, et qui ne se corrigera pas

**Le contenu vendu est présent dans la page.** Comme sur Boussole, le verrou est côté
navigateur : il cache, il n'empêche pas. À 1,99 € et 5,99 €, c'est une décision commerciale,
pas un défaut.
