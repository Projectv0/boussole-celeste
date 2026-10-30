"""Les trois pages légales, en deux versions tirées du même texte.

    python3 outils/legal.py   → legal/*.html                (aujourd'hui : éditeur non professionnel, aucune vente)
                                 societe/site-jour-J/*.html  (le jour J : la SAS, champs du Kbis entre crochets)

Une seule source pour les deux versions : la version SAS ne peut donc pas retarder sur
celle en ligne (piège Boussole : sa version SAS des CGV ignorait le complément et le
code à offrir, ajoutés après coup à la seule version en ligne).

Le jour J : remplir CHAMPS_SAS ci-dessous, relancer, relire, puis copier
societe/site-jour-J/ vers legal/ — et faire relire par un juriste.
"""
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CONTACT = "contact@boussole-celeste.fr"
MAJ = "29 octobre 2026"

CHAMPS_SAS = {
    "denomination": "[DÉNOMINATION]", "capital": "[CAPITAL]", "rcs": "[VILLE DU GREFFE]", "siren": "[SIREN]",
    "siege": "[ADRESSE DU SIÈGE]", "tva": "[NUMÉRO DE TVA INTRACOMMUNAUTAIRE, ou « TVA non applicable, article 293 B du CGI »]",
    "directeur": "[NOM DU DIRECTEUR DE LA PUBLICATION]", "telephone": "[TÉLÉPHONE]",
    "mediateur": "[NOM, ADRESSE POSTALE ET SITE DU MÉDIATEUR ADHÉRÉ]",
}

ENTETE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre} · Boussole céleste</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#0F1424">
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<link rel="preload" href="../polices/jost-400-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../polices/cormorant-garamond-600-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../polices/polices.css">
<link rel="stylesheet" href="../guide/style.css">
</head>
<body>

<div class="top">
  <a class="marque" href="../"><span class="logo"><img src="../favicon.svg" alt="" width="32" height="32"></span> Boussole céleste</a>
  <nav><a href="../">Retour au site</a></nav>
</div>

<main>
<article>
"""
PIED = """</article>
</main>

<footer>
  <p><a href="../">Boussole céleste</a> · <a href="../guide/">Le guide</a> · <a href="mentions-legales.html">Mentions légales</a> · <a href="confidentialite.html">Confidentialité</a>{lien_cgv}</p>
  <p>Un langage pour réfléchir à soi, pas une prédiction. Ne remplace l’avis d’aucun professionnel.</p>
</footer>

</body>
</html>
"""


def mail(a=CONTACT):
    return f'<a href="mailto:{a}">{a}</a>'


def mentions(sas):
    c = CHAMPS_SAS
    if sas:
        editeur = f"""  <h2>Éditeur du site</h2>
  <p>Le site <strong>Boussole céleste</strong> est édité par <strong>{c['denomination']}</strong>, société par actions simplifiée au capital de {c['capital']} euros, immatriculée au registre du commerce et des sociétés de {c['rcs']} sous le numéro {c['siren']}, dont le siège social est situé {c['siege']}.</p>
  <p>Numéro de TVA intracommunautaire : {c['tva']}.</p>
  <p>Directeur de la publication : {c['directeur']}.</p>
  <p>Contact : {mail()} · téléphone : {c['telephone']}.</p>
  <p>Médiateur de la consommation : {c['mediateur']}.</p>"""
    else:
        editeur = f"""  <h2>Éditeur du site</h2>
  <p>Le site <strong>Boussole céleste</strong> est édité à titre <strong>non professionnel</strong>, par une personne physique agissant en dehors de toute activité commerciale. Aucune vente n’y est réalisée à ce jour, et il ne contient aucune publicité.</p>
  <p>Conformément à l’article 6, III, 2 de la loi n° 2004-575 du 21 juin 2004 pour la confiance dans l’économie numérique, l’éditeur non professionnel peut ne pas rendre publiques ses coordonnées personnelles, sous réserve d’avoir communiqué son identité à son hébergeur. Ces éléments ont été communiqués à l’hébergeur ci-dessous.</p>
  <p>Contact : {mail()}</p>"""
    return f"""  <span class="meta">Informations légales</span>
  <h1>Mentions légales</h1>
  <p class="chapeau">Dernière mise à jour : {MAJ}.</p>

{editeur}

  <h2>Hébergement</h2>
  <p><strong>GitHub, Inc.</strong><br>88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis<br><a href="https://github.com" target="_blank" rel="noopener">github.com</a></p>
  <p>Les pages sont diffusées par le service GitHub Pages. L’hébergeur n’intervient ni dans la conception ni dans le contenu du site.</p>

  <h2>Objet du site</h2>
  <p>Boussole céleste propose un contenu de <strong>réflexion sur soi et de divertissement</strong>. Il utilise l’astrologie comme un langage&nbsp;: douze énergies, une par signe du zodiaque, pour mettre des mots sur ce que chacun vit en ce moment. Il comprend un questionnaire par mises en situation, un journal personnel et des contenus explicatifs.</p>
  <p><strong>Ce site ne prédit rien.</strong> Il ne conseille aucune décision de vie, de santé, d’argent ni de relation, ne fournit aucun diagnostic ni aucun avis médical ou psychologique, et ne remplace aucun professionnel. Si une période te pèse durablement, en parler à un professionnel est une bonne porte. En cas d’urgence&nbsp;: le 15, ou le 3114, numéro national de prévention du suicide, joignable jour et nuit.</p>

  <h2>Propriété intellectuelle</h2>
  <p>L’ensemble des éléments du site (textes, questionnaire, méthode de calcul, illustrations, identité visuelle, code source) est protégé par le droit de la propriété intellectuelle et demeure la propriété de l’éditeur, sauf mention contraire. Les tracés des constellations s’appuient sur les positions publiques des étoiles.</p>
  <p>Toute reproduction, représentation, adaptation ou exploitation, totale ou partielle, sans autorisation écrite préalable, est interdite. L’usage personnel et privé est autorisé, ainsi que le partage du lien vers le site et de ce que le site produit sur toi&nbsp;: la carte à partager et le texte de tes résultats.</p>
  <p>Les polices de caractères (Cormorant Garamond et Jost) sont publiées sous licence SIL Open Font et hébergées sur le site.</p>

  <h2>Responsabilité</h2>
  <p>L’éditeur s’efforce de fournir des informations exactes, sans garantir l’exhaustivité ni l’absence d’erreur. Les contenus ont une visée de réflexion générale et ne tiennent pas compte de la situation particulière de chaque personne.</p>
  <p>L’éditeur ne saurait être tenu responsable des décisions prises sur la seule base des résultats du questionnaire, ni d’une interruption du service, d’une perte de données stockées sur l’appareil de l’utilisateur, ou d’un dysfonctionnement lié au navigateur ou à l’appareil utilisé.</p>

  <h2>Signalement</h2>
  <p>Tout contenu qui semblerait inexact, inapproprié ou portant atteinte à des droits peut être signalé à l’adresse de contact. Une réponse sera apportée dans les meilleurs délais.</p>

  <h2>Droit applicable</h2>
  <p>Les présentes mentions sont soumises au droit français. En cas de litige, et à défaut de résolution amiable, les tribunaux français seront compétents.</p>
"""


def confidentialite(sas):
    c = CHAMPS_SAS
    responsable = (f"""  <h2>Qui est responsable</h2>
  <p>Le responsable du traitement des quelques données décrites plus bas (celles d’un achat) est <strong>{c['denomination']}</strong>, {c['siege']}. Contact : {mail()}.</p>
""" if sas else f"""  <h2>Qui est responsable</h2>
  <p>Le site est édité à titre non professionnel (voir les <a href="mentions-legales.html">mentions légales</a>). Pour toute question sur cette page : {mail()}.</p>
""")
    return f"""  <span class="meta">Confidentialité</span>
  <h1>Ce que devient ce que tu écris</h1>
  <p class="chapeau">Réponse courte&nbsp;: rien de ce que tu écris ne part. Ni tes réponses au test, ni ton journal, ni tes résultats, ni ton signe de naissance si tu le donnes. Voici le détail, sans langue de bois.</p>

  <div class="encart doux">
    <strong>Le principe du site</strong>
    Tout est calculé et stocké <em>dans ton navigateur</em>. Il n’existe aucun compte, aucun profil te concernant, et aucune base qui contienne quoi que ce soit venant de toi.
  </div>

{responsable}
  <h2>Tes réponses au test</h2>
  <p>Elles vivent en mémoire pendant que tu fais le test. Elles ne sont ni transmises, ni enregistrées sur un serveur. Deux exceptions, toutes deux locales à ton appareil et sous ton contrôle&nbsp;:</p>
  <ul>
    <li><strong>Le brouillon d’un test en cours</strong> reste dans le stockage local de ton navigateur pendant sept jours, pour que tu puisses reprendre là où tu t’es arrêté·e. Il s’efface dès que tes résultats s’ouvrent, ou si tu choisis «&nbsp;Repartir de zéro&nbsp;».</li>
    <li><strong>Tes résultats</strong> ne sont gardés que si tu cliques sur «&nbsp;Garder mes résultats sur cet appareil&nbsp;», pour suivre ce qui bouge d’un passage à l’autre.</li>
  </ul>

  <h2>Ton jour et ton mois de naissance</h2>
  <p>Après tes résultats, tu peux, si tu le veux, indiquer ton jour et ton mois de naissance, pour comparer ton signe à ce que tu vis. On ne te demande ni l’année, ni l’heure, ni le lieu. Le signe est calculé dans ton navigateur. <strong>Le jour, le mois et le signe choisi restent dans le stockage local de ton navigateur, sur cet appareil uniquement</strong>&nbsp;: ils ne sont jamais envoyés et n’entrent dans aucun calcul. Un lien «&nbsp;Effacer mon signe&nbsp;» les supprime.</p>

  <h2>Ton journal</h2>
  <p>Les moments que tu notes sont enregistrés dans le stockage local de ton navigateur, sur cet appareil uniquement. Ils ne sont jamais transmis, ni à l’éditeur, ni à un tiers. Vider les données de navigation, changer de navigateur ou d’appareil les fait disparaître&nbsp;: un bouton d’<strong>export</strong> te permet d’en garder une sauvegarde, un fichier que tu es seul·e à détenir. Un bouton «&nbsp;Tout effacer&nbsp;» supprime tout le journal.</p>

  <h2>Ce que le site ne fait pas</h2>
  <ul>
    <li>Aucun compte, aucune inscription. Faire le test et tenir ton journal ne demande aucune adresse e-mail.</li>
    <li>Aucun cookie, d’aucune sorte&nbsp;: c’est pourquoi le site ne t’affiche aucune bannière de consentement.</li>
    <li>Aucun traceur, aucun pixel publicitaire, aucun réseau social embarqué, aucune publicité.</li>
    <li>Aucun profilage, aucune décision automatisée te concernant.</li>
  </ul>

  <h2>Le comptage de fréquentation</h2>
  <p>Pour savoir si le site est lu, sept moments peuvent être comptés&nbsp;: l’ouverture de la page du test, l’ouverture d’une page du guide, le début du test, sa fin, l’affichage du choix de formule, le départ vers le paiement, et un clic sur la présentation du dossier. <strong>Ce qui est enregistré tient en deux informations&nbsp;: la date du jour et le nom du moment</strong>, plus l’adresse de la page pour une page du guide. Pas de cookie, pas d’identifiant, pas d’adresse IP conservée, pas d’empreinte de navigateur.</p>
  <p>Rien ne permet donc de relier deux moments à la même personne. Aucune de tes réponses n’est jamais envoyée, à ce comptage pas plus qu’ailleurs. Il est hébergé chez <strong>Cloudflare</strong>, dans l’Union européenne. Contre les abus, Cloudflare limite le nombre de requêtes qu’une même adresse IP peut envoyer à ce comptage, comme à la vérification d’un achat. Ce contrôle n’écrit rien dans la base du site.</p>
  <h2>Si tu achètes une formule</h2>
  <p>Le paiement est traité par <strong>Stripe</strong>, prestataire de paiement. Tes coordonnées bancaires sont saisies chez Stripe et ne passent jamais par ce site. Pour payer, tu donnes une adresse e-mail à Stripe&nbsp;: elle sert à t’envoyer ton reçu, et elle apparaît à l’éditeur dans le tableau de bord Stripe, avec le montant et la date. Base légale&nbsp;: l’exécution du contrat de vente. Conservation&nbsp;: dix ans pour les pièces comptables.</p>
  <p>Ton achat ne transmet rien de ton test&nbsp;: le dossier est fabriqué dans ton navigateur, il ne t’est pas envoyé par e-mail et l’éditeur n’en reçoit aucune copie.</p>
  <p>Au moment de choisir ta formule, une case <em>décochée par défaut</em> te propose d’être prévenu·e de la sortie de l’application en préparation. Si tu la coches, une simple mention est jointe à ton paiement chez Stripe. L’éditeur pourra alors t’écrire <strong>une fois</strong>, à l’adresse de ton paiement, le jour de la sortie, et pour rien d’autre. Base légale&nbsp;: ton consentement, que tu peux retirer à tout moment en écrivant à {mail()}.</p>
  <p>La vérification d’un achat interroge un service hébergé chez <strong>Cloudflare</strong>, avec ta seule référence d’achat. L’achat du dossier ouvre aussi un <strong>code à offrir</strong>&nbsp;: sont alors enregistrés le code, la référence de l’achat, la date de création et celle d’utilisation. Rien de la personne qui l’utilise.</p>

  <h2>Les seules connexions extérieures</h2>
  <ul>
    <li><strong>Aucune police extérieure</strong>&nbsp;: les polices sont hébergées sur le site. Ton navigateur ne contacte ni Google ni aucun autre fournisseur pour les afficher.</li>
    <li><strong>GitHub Pages</strong>, l’hébergeur, qui tient des journaux techniques de connexion comme tout hébergeur, sur des serveurs situés notamment aux États-Unis.</li>
    <li><strong>Cloudflare</strong>, pour le comptage, la vérification d’un achat et le code à offrir.</li>
    <li><strong>Stripe</strong>, uniquement si tu choisis une formule et cliques pour payer.</li>
  </ul>
  <p>Le site met ses fichiers en cache sur ton appareil dès ta première visite&nbsp;: c’est ce qui lui permet de fonctionner hors connexion. Ce cache contient les pages et les images du site, jamais tes réponses ni ton journal.</p>

  <h2>Tes droits</h2>
  <p>Pour le test, le journal et ton signe de naissance, l’éditeur ne réalise aucun traitement&nbsp;: ces données restent chez toi, et tu peux les consulter, les exporter ou les supprimer à tout moment, depuis le site ou les réglages de ton navigateur.</p>
  <p>Pour les données d’un achat, tes droits d’accès, de rectification, d’effacement, de limitation, d’opposition et de portabilité s’exercent en écrivant à {mail()}, dans la limite des durées de conservation comptables. Tu peux aussi introduire une réclamation auprès de la <a href="https://www.cnil.fr" target="_blank" rel="noopener">CNIL</a>.</p>

  <h2>Modifications et contact</h2>
  <p>Cette politique peut évoluer avec le site&nbsp;; la date de dernière mise à jour figure ci-dessous. Pour toute question&nbsp;: {mail()}.</p>
  <p class="chapeau" style="font-size:.92rem">Dernière mise à jour : {MAJ}.</p>
"""


def cgv(sas):
    c = CHAMPS_SAS
    vendeur = (f"""  <p>Le vendeur est <strong>{c['denomination']}</strong>, société par actions simplifiée au capital de {c['capital']} euros, immatriculée au RCS de {c['rcs']} sous le numéro {c['siren']}, dont le siège social est situé {c['siege']}, représentée par son président. Contact&nbsp;: {mail()} · téléphone&nbsp;: {c['telephone']}. Numéro de TVA intracommunautaire&nbsp;: {c['tva']}.</p>"""
               if sas else f"""  <p>Le vendeur sera identifié ici le jour de la mise en vente&nbsp;: dénomination, forme, capital, immatriculation, siège, téléphone et numéro de TVA. Contact&nbsp;: {mail()}.</p>""")
    bandeau = "" if sas else """  <div class="encart attention">
    <strong>Document préparatoire : aucune vente en cours</strong>
    À ce jour, aucune formule n’est vendue sur Boussole céleste, et ces conditions ne s’appliquent à personne. Ce texte prépare la mise en vente. Il sera complété (identité du vendeur, médiateur de la consommation) et relu par un juriste avant la première transaction.
  </div>
"""
    return f"""  <span class="meta">Conditions de vente</span>
  <h1>Conditions générales de vente</h1>
  <p class="chapeau">Applicables aux formules payantes de Boussole céleste. Dernière mise à jour : {MAJ}.</p>
{bandeau}
  <h2>1. Identification du vendeur</h2>
{vendeur}
  <p>Les paiements sont encaissés par <strong>Stripe Payments Europe, Ltd.</strong>, prestataire de services de paiement. Stripe traite les données bancaires de l’acheteur&nbsp;; le vendeur n’y a jamais accès. La vente est conclue directement entre l’acheteur et le vendeur.</p>

  <h2>2. Produits proposés</h2>
  <p>Il s’agit de <strong>contenus numériques fournis sans support matériel</strong>, accessibles immédiatement après l’achat&nbsp;:</p>
  <ul>
    <li><strong>Formule «&nbsp;Tes résultats&nbsp;» : 1,99 € TTC.</strong> Les résultats du test&nbsp;: la roue des douze énergies, leur classement et leurs notes sur 10, les éléments et les façons d’avancer, le ciel du moment, l’analyse de chaque énergie et la synthèse personnalisée.</li>
    <li><strong>Formule «&nbsp;Résultats + Dossier complet&nbsp;» : 5,99 € TTC</strong> (tarif de lancement, susceptible d’évoluer). La formule précédente, et le dossier&nbsp;: douze fiches approfondies, trente-six pratiques, les croisements du profil, un plan de trente jours et l’export du dossier en PDF. Elle donne aussi accès à la <strong>carte à partager</strong>, une image du profil aux formats «&nbsp;post&nbsp;» et «&nbsp;story&nbsp;», réservée à cette formule, et ouvre un <strong>code à offrir</strong>, décrit à l’article 5.</li>
  </ul>
  <p><strong>Complément&nbsp;: 4 € TTC.</strong> L’acheteur de la formule «&nbsp;Tes résultats&nbsp;» peut passer à la formule «&nbsp;Résultats + Dossier complet&nbsp;» en ne réglant que la différence, depuis sa page de résultats. Le complément n’est pas vendu seul et donne accès exactement au même contenu que la formule complète, code à offrir compris.</p>
  <p>Les prix sont indiqués en euros, toutes taxes comprises. Le montant affiché avant le paiement est celui qui est débité.</p>

  <h2>3. Nature du produit</h2>
  <p>Boussole céleste propose un contenu de <strong>réflexion sur soi et de divertissement</strong>, qui utilise l’astrologie comme un langage. <strong>Il ne prédit rien</strong>, ne conseille aucune décision de vie, de santé, d’argent ni de relation, et ne remplace aucun professionnel. Il ne constitue ni un diagnostic, ni un avis médical ou psychologique, ni un accompagnement.</p>
  <p>Aucun résultat ni aucun bénéfice n’est garanti&nbsp;: le produit fournit une lecture indicative et des pistes de réflexion, à partir des seules réponses de l’acheteur.</p>

  <h2>4. Commande et livraison</h2>
  <p>La commande s’effectue depuis la fin du test ou la page de résultats, qui renvoient vers la page de paiement sécurisée de Stripe une fois la case de l’article 6 cochée. Après le paiement, l’acheteur est redirigé vers le site avec une <strong>référence d’achat</strong>, affichée avec un bouton pour la copier, et reçoit un reçu par courrier électronique.</p>
  <p>La livraison consiste en l’activation de l’accès&nbsp;: au retour du paiement, la formule se débloque dans le navigateur de l’acheteur, ou par saisie de la référence d’achat. Le contenu est alors préparé dans son navigateur, à partir de ses propres réponses. Les réponses au test n’étant conservées sur aucun serveur, il est recommandé de garder l’onglet du test ouvert pendant l’achat.</p>
  <p>La référence d’achat est personnelle&nbsp;: sa communication à des tiers, sa revente ou sa publication ne sont pas autorisées.</p>

  <h2>5. Le code à offrir</h2>
  <p>L’achat de la formule «&nbsp;Résultats + Dossier complet&nbsp;» permet d’obtenir <strong>un code unique</strong>, à transmettre à la personne de son choix. Ce code donne accès à la formule «&nbsp;Tes résultats&nbsp;» pour cette personne, à partir de ses propres réponses. <strong>Il ne donne jamais accès au dossier complet.</strong> Ce code est unique par achat, valable vingt-quatre heures à compter de sa création, utilisable une seule fois, et n’est pas réédité. Il n’est pas vendu séparément, n’a aucune valeur monétaire, ne peut être ni échangé ni remboursé, et son expiration n’ouvre droit à aucune indemnité.</p>

  <h2>6. Droit de rétractation</h2>
  <p>Conformément à l’article L221-28 13° du code de la consommation, le droit de rétractation ne peut être exercé pour la fourniture d’un contenu numérique non fourni sur support matériel dont l’exécution a commencé après accord préalable exprès du consommateur et renoncement exprès à son droit de rétractation.</p>
  <p>Avant tout paiement, l’acheteur coche une case par laquelle il accepte les présentes conditions et renonce à son droit de rétractation pour un accès immédiat. Tant que cette case n’est pas cochée, aucun paiement ne peut être engagé. Cette acceptation est confirmée sur le reçu envoyé par e-mail.</p>
  <p>Tant que l’accès n’a pas été activé, l’acheteur peut demander le remboursement dans les quatorze jours suivant l’achat, en écrivant à {mail()}&nbsp;; il est remboursé par le même moyen de paiement, dans un délai de quatorze jours.</p>

  <h2>7. Problème technique et garanties</h2>
  <p>Si un dysfonctionnement empêche l’accès au contenu acheté, l’acheteur écrit à {mail()} en indiquant sa référence d’achat et le problème rencontré. Une solution, déblocage manuel ou remboursement, est recherchée dans les meilleurs délais.</p>
  <p>Le contenu numérique bénéficie de la garantie légale de conformité prévue aux articles L224-25-12 et suivants du code de la consommation. L’acheteur la met en œuvre en écrivant à la même adresse.</p>

  <h2>8. Propriété intellectuelle</h2>
  <p>L’achat confère un droit d’usage <strong>personnel et non exclusif</strong>. L’acheteur peut lire, conserver et imprimer son dossier pour son propre usage. Toute diffusion publique, revente ou exploitation commerciale est interdite sans autorisation écrite.</p>
  <p>Par exception, <strong>ce qui décrit le profil de l’acheteur est fait pour être partagé</strong>&nbsp;: la carte à partager et le texte produit par «&nbsp;Copier mes résultats&nbsp;» peuvent être diffusés librement, y compris sur les réseaux sociaux, sans modification ni usage commercial.</p>

  <h2>9. Données personnelles</h2>
  <p>L’éditeur n’a accès ni aux coordonnées bancaires, ni au contenu du test ou du journal de l’acheteur, qui ne quittent pas son appareil. Voir la <a href="confidentialite.html">politique de confidentialité</a>.</p>

  <h2>10. Modification des conditions</h2>
  <p>Les conditions applicables sont celles en vigueur à la date de la commande.</p>

  <h2>11. Droit applicable et litiges</h2>
  <p>Les présentes conditions sont soumises au droit français. En cas de différend, l’acheteur est invité à contacter le vendeur pour rechercher une solution amiable. Conformément à l’article L612-1 du code de la consommation, le consommateur peut recourir sans frais à un médiateur de la consommation&nbsp;: <strong>{c['mediateur'] if sas else "[médiateur désigné le jour de la mise en vente]"}</strong>. À défaut d’accord, les tribunaux français sont compétents.</p>
"""


PAGES = [
    ("mentions-legales.html", "Mentions légales", "Mentions légales de Boussole céleste : éditeur, hébergeur, objet du site, propriété intellectuelle.", mentions),
    ("confidentialite.html", "Confidentialité", "Ce que devient ce que tu écris sur Boussole céleste : rien ne quitte ton navigateur.", confidentialite),
    ("cgv.html", "Conditions de vente", "Conditions générales de vente des formules de Boussole céleste.", cgv),
]

if __name__ == "__main__":
    for sas, dossier in ((False, RACINE / "legal"), (True, RACINE / "societe" / "site-jour-J")):
        dossier.mkdir(parents=True, exist_ok=True)
        for fichier, titre, desc, corps in PAGES:
            robots = "noindex, nofollow" if (fichier == "cgv.html" and not sas) else "noindex, follow"
            lien_cgv = ' · <a href="cgv.html">Conditions de vente</a>' if sas else ""
            page = ENTETE.format(titre=titre, desc=desc, robots=robots) + corps(sas) + PIED.format(lien_cgv=lien_cgv)
            assert "gratuit" not in page.lower(), fichier
            assert "'" not in page.replace("rel='", ""), f"apostrophe droite dans {fichier}"
            (dossier / fichier).write_text(page)
        print(dossier.relative_to(RACINE), "· 3 pages")
