/* Cloudflare Worker — trois services sur la même adresse.

   1. VÉRIFICATION D'ACHAT
      GET /?session_id=cs_...  →  { valide, niveau }
      Le Worker interroge Stripe côté serveur : impossible à contourner depuis le
      navigateur.

   2. MESURE D'AUDIENCE
      POST /mesure             →  204, enregistre un événement anonyme
      GET  /mesure             →  le tableau, réservé à l'éditeur
                                  (Authorization: Bearer <clé>, voir outils/mesure.py)

   3. CODE CADEAU
      POST /cadeau             →  { code, expire_le } pour un acheteur du dossier
      POST /cadeau/utiliser    →  { valide, niveau } pour celui qui le reçoit

   Secrets, posés par Martial avec « wrangler secret put » :
     STRIPE_CLE  clé restreinte Stripe, lecture seule sur les sessions Checkout
                 ET sur les PaymentIntents — sans la seconde, une session
                 remboursée resterait valable indéfiniment.
     MESURE_CLE  mot de passe tiré au hasard, pour lire le tableau de mesure.

   Liaisons, déclarées dans wrangler.jsonc :
     MESURE      base D1, avec les tables de schema.sql
     LIMITE      dix requêtes par minute et par adresse IP

   Chaque service se tait si ce qu'il lui faut manque : sans STRIPE_CLE la
   vérification répond 501, sans la base D1 la mesure répond 204 sans rien écrire.
   Le site fonctionne dans les deux cas. */

const ORIGINES = [
  "https://boussole-celeste.fr",
  "https://www.boussole-celeste.fr",
  /* Tant que le domaine n'est pas branché, le site vit sur GitHub Pages. À retirer le
     jour où boussole-celeste.fr répond : sinon une copie du site posée ailleurs sur
     github.io pourrait, elle aussi, écrire dans le compteur. */
  "https://projectv0.github.io",
];

/* Les identifiants de prix Stripe (price_…) de CE site, et d'aucun autre. Un seul compte
   Stripe, celui de la SAS, vend aussi Boussole émotionnelle : se fier au montant seul,
   ce serait laisser un achat de l'autre site ouvrir celui-ci (mêmes montants). On lit
   donc les lignes de la session, et seul un prix listé ici ouvre un accès.
   À remplir avec les identifiants que Martial donnera (fiche produit Stripe). Tant que
   ces listes sont vides, la vérification répond 501 : rien n'est accordé à l'aveugle. */
const PRIX = {
  resultats: [],          // « Tes résultats », 1,99 €
  dossier: [],            // « Résultats + Dossier complet », 5,99 €, et le complément à 4 €
};

const DEVISE = "eur";

/* Les sept seuls événements acceptés (les mêmes que Boussole émotionnelle). Une liste fermée plutôt qu'un champ libre :
   sans elle, n'importe qui pourrait remplir la base de lignes inventées, et le
   tableau deviendrait illisible sans qu'aucune alerte ne se déclenche. */
const EVENEMENTS = new Set([
  "accueil",      // arrivée sur la page du test
  "article",      // arrivée sur une page du guide
  "test-debut",   // clic sur « Commencer le test »
  "test-fin",     // seize situations répondues
  "paywall",      // la fenêtre de choix de formule s'ouvre
  "stripe",       // départ vers le paiement
  "promo-carte",  // clic sur « Découvrir le dossier complet » depuis l'encart de la carte
]);

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const origine = req.headers.get("Origin") || "";
    const cors = {
      "Access-Control-Allow-Origin": ORIGINES.includes(origine) ? origine : ORIGINES[0],
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "content-type",
      "Vary": "Origin",
    };
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });

    /* Deux compteurs par adresse : un gonflage du tableau ne doit pas priver un
       acheteur de sa vérification, s'ils partagent la même adresse. */
    const ecriture = url.pathname === "/mesure" && req.method === "POST";
    if (await tropDeRequetes(req, env, ecriture ? "mesure" : "achat"))
      return ecriture ? vide(cors) : json({ valide: false, erreur: "trop de requêtes" }, 429, cors);

    if (url.pathname === "/mesure") {
      return ecriture
        ? ecrireMesure(req, env, origine, cors)
        : lireMesure(req, url, env, cors);
    }
    if (url.pathname === "/cadeau")          return creerCadeau(req, env, origine, cors);
    if (url.pathname === "/cadeau/utiliser") return utiliserCadeau(req, env, origine, cors);
    return verifierAchat(url, env, cors);
  },
};

/* ————————————————————————— limitation de débit —————————————————————————
   Une règle Cloudflare classique demande un domaine géré chez Cloudflare, ce que
   n'est pas une adresse en workers.dev : la limite vit donc ici. Le compteur est
   tenu par Cloudflare, par site de son réseau, et rien n'est écrit dans la base.
   Si la liaison manque ou tombe en panne, on laisse passer : un acheteur ne doit
   jamais être refusé à cause de la protection elle-même. */
async function tropDeRequetes(req, env, quoi) {
  if (!env.LIMITE) return false;
  try {
    const ip = req.headers.get("CF-Connecting-IP") || "";
    const { success } = await env.LIMITE.limit({ key: `${quoi}:${ip}` });
    return !success;
  } catch (_) {
    return false;
  }
}

/* ————————————————————————— mesure d'audience —————————————————————————
   Ce qui est écrit : un jour, un nom d'événement, et pour les articles le chemin
   de la page. Rien d'autre. Pas d'adresse IP, pas de cookie, pas d'identifiant de
   visite, pas d'en-tête de navigateur. On ne peut donc pas relier deux événements
   à la même personne — c'est délibéré, et c'est ce qui permet au site de continuer
   à dire que tes réponses ne quittent jamais ton navigateur.

   Le prix de ce choix : on compte des événements, pas des visiteurs. « 300
   arrivées et 4 départs vers Stripe » se lit très bien ; « combien de personnes
   distinctes » ne se saura jamais, et c'est un renseignement auquel on renonce. */
async function ecrireMesure(req, env, origine, cors) {
  /* Répondre 204 même quand on n'écrit rien : le navigateur n'a rien à faire de
     l'erreur, et une mesure qui échoue ne doit jamais se voir sur le site. */
  if (!ORIGINES.includes(origine)) return vide(cors);
  if (!env.MESURE) return vide(cors);

  let corps;
  try {
    /* text/plain à dessein : sendBeacon ne sait pas négocier de requête
       préalable, et un content-type JSON en déclencherait une. */
    corps = JSON.parse(await req.text());
  } catch (_) {
    return vide(cors);
  }

  const evenement = String(corps && corps.e || "");
  if (!EVENEMENTS.has(evenement)) return vide(cors);
  const page = evenement === "article" ? chemin(corps.p) : "";
  const jour = new Date().toISOString().slice(0, 10);

  try {
    await env.MESURE.prepare(
      "INSERT INTO compteur (jour, evenement, page, n) VALUES (?, ?, ?, 1) " +
      "ON CONFLICT(jour, evenement, page) DO UPDATE SET n = n + 1"
    ).bind(jour, evenement, page).run();
  } catch (_) { /* la mesure ne casse jamais la page */ }
  return vide(cors);
}

/* Un chemin de page du guide, et rien qui puisse servir à autre chose : pas de
   chaîne de requête (elle pourrait porter un identifiant), pas de fragment, et
   seulement les caractères d'un nom de fichier. */
function chemin(p) {
  const s = String(p || "").split("?")[0].split("#")[0];
  return /^\/guide\/[a-z0-9-]{1,80}\.html$/.test(s) ? s : "";
}

async function lireMesure(req, url, env, cors) {
  /* Dans un en-tête, pas dans l'adresse : une adresse finit dans les journaux. */
  const cle = (req.headers.get("Authorization") || "").replace(/^Bearer /, "");
  if (!env.MESURE_CLE || !egal(cle, env.MESURE_CLE))
    return json({ erreur: "réservé à l'éditeur" }, 403, cors);
  if (!env.MESURE) return json({ erreur: "base non liée" }, 501, cors);

  const jours = Math.min(Math.max(parseInt(url.searchParams.get("jours") || "30", 10) || 30, 1), 365);
  const depuis = new Date(Date.now() - jours * 86400000).toISOString().slice(0, 10);
  try {
    const parJour = await env.MESURE.prepare(
      "SELECT jour, evenement, SUM(n) AS n FROM compteur WHERE jour >= ? " +
      "GROUP BY jour, evenement ORDER BY jour DESC"
    ).bind(depuis).all();
    const total = await env.MESURE.prepare(
      "SELECT evenement, SUM(n) AS n FROM compteur WHERE jour >= ? GROUP BY evenement"
    ).bind(depuis).all();
    const articles = await env.MESURE.prepare(
      "SELECT page, SUM(n) AS n FROM compteur WHERE jour >= ? AND evenement = 'article' " +
      "AND page <> '' GROUP BY page ORDER BY n DESC LIMIT 40"
    ).bind(depuis).all();
    return json({ depuis, jours, total: total.results, parJour: parJour.results,
                  articles: articles.results }, 200, cors);
  } catch (e) {
    return json({ erreur: String(e && e.message || e) }, 500, cors);
  }
}

/* Comparaison à durée constante : comparer deux chaînes avec === laisse fuir la
   longueur du préfixe juste, ce qui suffit à retrouver une clé à l'usure. */
function egal(a, b) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

/* ————————————————————————— vérification d'achat ————————————————————————— */
const REF_ACHAT = /^cs_(live|test)_[A-Za-z0-9]{10,}$/;

async function verifierAchat(url, env, cors) {
  const id = url.searchParams.get("session_id") || "";
  if (!REF_ACHAT.test(id))
    return json({ valide: false, erreur: "référence invalide" }, 400, cors);

  const a = await lireAchat(id, env);
  if (a.erreur) return json({ valide: false, erreur: a.erreur }, a.status, cors);
  return json({ valide: a.valide, niveau: a.niveau }, 200, cors);
}

/* La question posée à Stripe, séparée de la réponse faite au navigateur : le
   code cadeau a besoin de la même vérification, et deux copies du même contrôle
   d'argent finissent toujours par diverger. */
async function lireAchat(id, env) {
  if (!env.STRIPE_CLE) return { erreur: "clé non configurée", status: 501 };
  if (!PRIX.resultats.length || !PRIX.dossier.length) return { erreur: "prix non configurés", status: 501 };

  let s;
  try {
    /* On demande le paiement complet : sans lui, une session remboursée ou
       contestée reste « paid » et continuerait d'ouvrir l'accès indéfiniment. */
    const r = await fetch(
      `https://api.stripe.com/v1/checkout/sessions/${encodeURIComponent(id)}`
        + "?expand[]=payment_intent.latest_charge&expand[]=line_items",
      { headers: { Authorization: `Bearer ${env.STRIPE_CLE}` } }
    );
    if (!r.ok) return { valide: false, niveau: null };
    s = await r.json();
  } catch (_) {
    return { erreur: "stripe injoignable", status: 502 };
  }

  const charge = s.payment_intent && s.payment_intent.latest_charge;
  const rembourse = !!(charge && (charge.refunded || (charge.amount_refunded | 0) > 0));
  const conteste = !!(charge && charge.disputed);
  const bonneDevise = (s.currency || "").toLowerCase() === DEVISE;
  const paye = s.payment_status === "paid" && bonneDevise && !rembourse && !conteste;

  /* Le palier suit le prix acheté. Un prix inconnu — un achat de l'autre site, ou un
     produit oublié ici — n'ouvre rien. */
  const prix = ((s.line_items && s.line_items.data) || []).map(l => l.price && l.price.id).filter(Boolean);
  const niveau = prix.some(p => PRIX.dossier.includes(p)) ? "dossier"
               : prix.some(p => PRIX.resultats.includes(p)) ? "resultats" : null;
  const valide = paye && !!niveau;
  return { valide, niveau: valide ? niveau : null };
}

/* ————————————————————————————— code cadeau —————————————————————————————
   Acheter le dossier ouvre le droit d'offrir le test à quelqu'un. Un code, un
   seul, valable vingt-quatre heures — comptées depuis le moment où on l'engendre,
   pas depuis l'achat : on offre quand on a la personne en tête, pas dans la
   minute qui suit le paiement.

   Ce que le code ouvre : les résultats. Jamais le dossier — celui-là reste
   attaché à l'achat qui l'a payé.

   Un achat, un code, et c'est tout : la contrainte UNIQUE sur session vaut aussi
   bien après la péremption. Un code oublié est perdu, sans réédition — c'est
   voulu, et c'est pourquoi le site prévient avant qu'on appuie sur le bouton.

   Alphabet sans O ni 0, sans I ni 1 : un code se lit à voix haute et se recopie
   d'un téléphone à l'autre, et personne ne devrait avoir à deviner lequel des
   deux caractères c'était. Trente-deux lettres sur huit positions font mille
   milliards de combinaisons : on ne tombe pas dessus par hasard. Une règle de
   limitation de débit côté Cloudflare reste à poser malgré tout (voir A-FAIRE),
   pour qu'on ne puisse pas non plus essayer en masse. */
const ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
const DUREE_CADEAU = 24 * 3600 * 1000;

function engendrerCode() {
  const tirage = new Uint8Array(8);
  crypto.getRandomValues(tirage);
  let s = "";
  /* 256 est un multiple exact de 32 : le reste de la division ne favorise
     aucune lettre. Avec un alphabet d'une autre taille il faudrait retirer. */
  for (let i = 0; i < 8; i++) s += ALPHABET[tirage[i] % 32];
  return `BC-${s.slice(0, 4)}-${s.slice(4)}`;
}

/* On accepte le code tel qu'il aura voyagé : en minuscules, sans les tirets,
   avec des espaces, avec ou sans le BC du début. Ce qui en ressort est la forme
   unique écrite dans la base, ou une chaîne vide si ça n'y ressemble pas. */
function normaliserCode(brut) {
  const brutMaj = String(brut || "").trim().toUpperCase();
  /* Le site a un autre code, celui de la comparaison entre proches : « BC1- »
     suivi de douze caractères dont un tiret pour les énergies non mesurées.
     Ces tirets s'effacent au nettoyage, et un code comptant sept absences
     prendrait exactement la forme d'un code cadeau. Le navigateur écarte déjà
     ce cas ; le serveur ne s'en remet pas à lui pour autant. */
  if (/^BC\d-/.test(brutMaj)) return "";
  const s = brutMaj.replace(/[^A-Z0-9]/g, "");
  const c = s.startsWith("BC") ? s.slice(2) : s;
  if (!new RegExp(`^[${ALPHABET}]{8}$`).test(c)) return "";
  return `BC-${c.slice(0, 4)}-${c.slice(4)}`;
}

async function creerCadeau(req, env, origine, cors) {
  if (req.method !== "POST") return json({ erreur: "méthode" }, 405, cors);
  if (!ORIGINES.includes(origine)) return json({ erreur: "origine" }, 403, cors);
  if (!env.MESURE) return json({ erreur: "base non liée" }, 501, cors);

  let corps;
  try { corps = JSON.parse(await req.text()); } catch (_) { corps = null; }
  const id = String(corps && corps.session_id || "");
  if (!REF_ACHAT.test(id)) return json({ erreur: "référence invalide" }, 400, cors);

  /* Le droit d'offrir se vérifie auprès de Stripe, pas auprès du navigateur :
     autrement n'importe qui réclamerait des codes à la chaîne. */
  const a = await lireAchat(id, env);
  if (a.erreur) return json({ erreur: a.erreur }, a.status, cors);
  if (!a.valide || a.niveau !== "dossier")
    return json({ erreur: "réservé au dossier complet" }, 403, cors);

  const maintenant = new Date().toISOString();
  const expire = new Date(Date.parse(maintenant) + DUREE_CADEAU).toISOString();

  try {
    /* Insérer d'abord, relire ensuite. Lire puis écrire laisserait deux clics
       simultanés engendrer deux codes ; ici la contrainte UNIQUE sur session
       tranche, et la relecture dit simplement lequel a gagné. */
    await env.MESURE.prepare(
      "INSERT INTO cadeau (code, session, cree_le, expire_le) VALUES (?, ?, ?, ?) " +
      "ON CONFLICT(session) DO NOTHING"
    ).bind(engendrerCode(), id, maintenant, expire).run();

    const l = await env.MESURE.prepare(
      "SELECT code, expire_le, utilise_le FROM cadeau WHERE session = ?"
    ).bind(id).first();
    if (!l) return json({ erreur: "code indisponible" }, 500, cors);

    return json({
      code: l.code,
      expire_le: l.expire_le,
      utilise: !!l.utilise_le,
      expire: l.expire_le <= maintenant,
    }, 200, cors);
  } catch (e) {
    return json({ erreur: String(e && e.message || e) }, 500, cors);
  }
}

async function utiliserCadeau(req, env, origine, cors) {
  if (req.method !== "POST") return json({ valide: false, erreur: "méthode" }, 405, cors);
  if (!ORIGINES.includes(origine)) return json({ valide: false, erreur: "origine" }, 403, cors);
  if (!env.MESURE) return json({ valide: false, erreur: "base non liée" }, 501, cors);

  let corps;
  try { corps = JSON.parse(await req.text()); } catch (_) { corps = null; }
  const code = normaliserCode(corps && corps.code);
  if (!code) return json({ valide: false, raison: "format" }, 400, cors);

  const maintenant = new Date().toISOString();
  try {
    /* Une seule écriture, et c'est elle qui décide : les trois conditions sont
       dans le WHERE. Deux navigateurs qui présentent le même code à la même
       seconde ne peuvent donc pas l'utiliser tous les deux — la base n'applique
       la mise à jour qu'une fois. Vérifier d'abord puis écrire laisserait au
       contraire une porte ouverte entre les deux instants. */
    const r = await env.MESURE.prepare(
      "UPDATE cadeau SET utilise_le = ? WHERE code = ? AND utilise_le IS NULL AND expire_le > ?"
    ).bind(maintenant, code, maintenant).run();

    if (r && r.meta && r.meta.changes === 1)
      return json({ valide: true, niveau: "resultats" }, 200, cors);

    /* Rien n'a changé : reste à dire pourquoi, sans rien inventer. */
    const l = await env.MESURE.prepare(
      "SELECT expire_le, utilise_le FROM cadeau WHERE code = ?"
    ).bind(code).first();
    const raison = !l ? "inconnu" : l.utilise_le ? "utilise" : "expire";
    return json({ valide: false, raison }, 200, cors);
  } catch (e) {
    return json({ valide: false, erreur: String(e && e.message || e) }, 500, cors);
  }
}

function vide(cors) {
  return new Response(null, { status: 204, headers: { "cache-control": "no-store", ...cors } });
}

function json(objet, status, cors) {
  return new Response(JSON.stringify(objet), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store", ...cors },
  });
}
