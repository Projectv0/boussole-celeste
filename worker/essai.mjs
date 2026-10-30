/* Essais du Worker, sans réseau ni compte : Stripe est simulé, la base est une vraie
   SQLite en mémoire montée sur schema.sql. C'est ce qui contrôle l'argent, et Stripe
   n'existera qu'avec la société : ces cas ne peuvent pas encore se jouer en ligne.

       node worker/essai.mjs
*/
import { readFileSync, writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { DatabaseSync } from "node:sqlite";

const ICI = dirname(fileURLToPath(import.meta.url));
const SOURCE = readFileSync(join(ICI, "verification.js"), "utf8");
const dossier = mkdtempSync(join(tmpdir(), "essai-worker-"));

async function charger(nom, source) {
  const f = join(dossier, nom + ".mjs");
  writeFileSync(f, source);
  return (await import(f)).default;
}
const sansPrix = await charger("sans-prix", SOURCE);
const avecPrix = await charger("avec-prix", SOURCE
  .replace("resultats: [],", 'resultats: ["price_res"],')
  .replace("dossier: [],", 'dossier: ["price_dos", "price_compl"],'));

function baseD1() {
  const db = new DatabaseSync(":memory:");
  db.exec(readFileSync(join(ICI, "schema.sql"), "utf8"));
  return {
    db,
    prepare(sql) {
      const st = db.prepare(sql);
      return { bind: (...a) => ({
        run: async () => ({ meta: { changes: st.run(...a).changes } }),
        first: async () => st.get(...a) || null,
        all: async () => ({ results: st.all(...a) }),
      }) };
    },
  };
}

/* Les réponses de Stripe, par référence d'achat. */
const seance = (prix, autre = {}) => ({
  payment_status: "paid", currency: "eur",
  payment_intent: { latest_charge: { refunded: false, amount_refunded: 0, disputed: false } },
  line_items: { data: [{ price: { id: prix } }] }, ...autre,
});
const charge = c => ({ payment_intent: { latest_charge: c } });
const STRIPE = {
  cs_test_resultats00: seance("price_res"),
  cs_test_dossier0000: seance("price_dos"),
  cs_test_complement0: seance("price_compl"),
  cs_test_autresite00: seance("price_boussole_emotionnelle"),
  cs_test_impayee0000: seance("price_dos", { payment_status: "unpaid" }),
  cs_test_rembourse00: seance("price_dos", charge({ refunded: true, amount_refunded: 599 })),
  cs_test_partiel0000: seance("price_dos", charge({ refunded: false, amount_refunded: 100 })),
  cs_test_conteste000: seance("price_dos", charge({ disputed: true })),
  cs_test_dollars0000: seance("price_dos", { currency: "usd" }),
};
let stripeEnPanne = false;
globalThis.fetch = async u => {
  if (stripeEnPanne) throw new Error("panne");
  const id = decodeURIComponent(String(u).split("/sessions/")[1].split("?")[0]);
  if (!String(u).includes("expand[]=line_items")) throw new Error("line_items non demandé");
  return STRIPE[id] ? new Response(JSON.stringify(STRIPE[id])) : new Response("{}", { status: 404 });
};

const SITE = "https://boussole-celeste.fr";
const ENV = o => ({ STRIPE_CLE: "k", MESURE_CLE: "secret", MESURE: baseD1(), ...o });
const appel = (w, env, chemin, o = {}) =>
  w.fetch(new Request("https://w.test" + chemin, { headers: { Origin: SITE, ...(o.headers || {}) }, ...o }), env);
const poster = (w, env, chemin, corps, o = {}) =>
  appel(w, env, chemin, { method: "POST", body: typeof corps === "string" ? corps : JSON.stringify(corps), ...o });
const verifier = async (env, id, w = avecPrix) => {
  const r = await appel(w, env, "/?session_id=" + id);
  return { status: r.status, ...(await r.json()) };
};

let ok = 0, ko = 0;
function vu(nom, cond) { cond ? ok++ : ko++; console.log(`${cond ? "  ok " : "RATÉ "} ${nom}`); }
const lignes = env => env.MESURE.db.prepare("SELECT jour, evenement, page, n FROM compteur").all();

/* ———— Vérification d'achat ———— */
let e = ENV();
let v = await verifier(e, "abc");                   vu("référence mal formée : 400", v.status === 400 && !v.valide);
v = await verifier(ENV({ STRIPE_CLE: undefined }), "cs_test_dossier0000");
                                                    vu("sans clé Stripe : 501, rien d'accordé", v.status === 501 && !v.valide);
v = await verifier(e, "cs_test_dossier0000", sansPrix);
                                                    vu("sans identifiants de prix : 501, rien d'accordé", v.status === 501 && !v.valide);
v = await verifier(e, "cs_test_inventee000");       vu("référence inventée : refusée", v.status === 200 && !v.valide && v.niveau === null);
v = await verifier(e, "cs_test_resultats00");       vu("1,99 € : résultats", v.valide && v.niveau === "resultats");
v = await verifier(e, "cs_test_dossier0000");       vu("5,99 € : dossier", v.valide && v.niveau === "dossier");
v = await verifier(e, "cs_test_complement0");       vu("complément 4 € : dossier", v.valide && v.niveau === "dossier");
v = await verifier(e, "cs_test_autresite00");       vu("achat de l'autre site : refusé", !v.valide && v.niveau === null);
v = await verifier(e, "cs_test_impayee0000");       vu("non payé : refusé", !v.valide);
v = await verifier(e, "cs_test_rembourse00");       vu("remboursé : refusé", !v.valide);
v = await verifier(e, "cs_test_partiel0000");       vu("remboursé en partie : refusé", !v.valide);
v = await verifier(e, "cs_test_conteste000");       vu("contesté : refusé", !v.valide);
v = await verifier(e, "cs_test_dollars0000");       vu("autre devise : refusé", !v.valide);
stripeEnPanne = true;
v = await verifier(e, "cs_test_dossier0000");       vu("Stripe injoignable : 502, rien d'accordé", v.status === 502 && !v.valide);
stripeEnPanne = false;

/* ———— Mesure ———— */
e = ENV();
let r = await poster(avecPrix, e, "/mesure", { e: "inconnu" });
vu("événement inconnu : 204, rien d'écrit", r.status === 204 && lignes(e).length === 0);
r = await poster(avecPrix, e, "/mesure", { e: "accueil" }, { headers: { Origin: "https://ailleurs.example" } });
vu("autre origine : 204, rien d'écrit", r.status === 204 && lignes(e).length === 0);
r = await poster(avecPrix, e, "/mesure", "pas du json");
vu("corps illisible : 204, rien d'écrit", r.status === 204 && lignes(e).length === 0);
await poster(avecPrix, e, "/mesure", { e: "accueil" });
await poster(avecPrix, e, "/mesure", { e: "accueil" });
vu("deux accueils : une ligne, n = 2", lignes(e).length === 1 && lignes(e)[0].n === 2);
await poster(avecPrix, e, "/mesure", { e: "article", p: "/guide/energie-belier.html?id=42#x" });
vu("article : le chemin seul, sans paramètre", lignes(e).some(l => l.page === "/guide/energie-belier.html"));
await poster(avecPrix, e, "/mesure", { e: "article", p: "/etrange/<script>" });
vu("chemin inattendu : page vide", lignes(e).some(l => l.evenement === "article" && l.page === ""));
vu("seulement jour, événement, page, n", Object.keys(lignes(e)[0]).join() === "jour,evenement,page,n");
r = await appel(avecPrix, e, "/mesure");
vu("lecture sans clé : 403", r.status === 403);
r = await appel(avecPrix, e, "/mesure", { headers: { Authorization: "Bearer mauvaise" } });
vu("lecture avec une mauvaise clé : 403", r.status === 403);
r = await appel(avecPrix, e, "/mesure?cle=secret");
vu("clé dans l'adresse : 403", r.status === 403);
r = await appel(avecPrix, e, "/mesure", { headers: { Authorization: "Bearer secret" } });
const tab = await r.json();
vu("lecture avec la clé : le tableau", r.status === 200 && tab.total.some(t => t.evenement === "accueil" && t.n === 2));
r = await appel(avecPrix, ENV({ MESURE_CLE: undefined }), "/mesure", { headers: { Authorization: "Bearer " } });
vu("sans clé configurée : 403", r.status === 403);

/* ———— Code cadeau ———— */
e = ENV();
const creer = (id, o) => poster(avecPrix, e, "/cadeau", { session_id: id }, o);
const utiliser = async code => {
  const x = await poster(avecPrix, e, "/cadeau/utiliser", { code });
  return { status: x.status, ...(await x.json()) };
};
r = await creer("cs_test_resultats00");             vu("code réservé au dossier", r.status === 403);
r = await creer("cs_test_inventee000");             vu("code sur référence inventée : refusé", r.status === 403);
r = await creer("cs_test_autresite00");             vu("code sur un achat de l'autre site : refusé", r.status === 403);
r = await creer("cs_test_dossier0000", { headers: { Origin: "https://ailleurs.example" } });
vu("code depuis une autre origine : refusé", r.status === 403);
const c1 = await (await creer("cs_test_dossier0000")).json();
const c2 = await (await creer("cs_test_dossier0000")).json();
vu("forme BC-XXXX-XXXX", /^BC-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$/.test(c1.code));
vu("un achat, un seul code", c1.code === c2.code);
vu("valable 24 h", Math.round((Date.parse(c1.expire_le) - Date.now()) / 3600000) === 24);
v = await utiliser("BC1-ABCD---EFGH");              vu("code de comparaison : écarté", v.status === 400 && v.raison === "format");
v = await utiliser("BC-ZZZZ-ZZZZ");                 vu("code inconnu", !v.valide && v.raison === "inconnu");
v = await utiliser(c1.code.toLowerCase().replace(/-/g, " "));
                                                    vu("code retapé en minuscules : résultats, jamais le dossier", v.valide && v.niveau === "resultats");
v = await utiliser(c1.code);                        vu("deuxième usage : refusé", !v.valide && v.raison === "utilise");
e.MESURE.db.exec("INSERT INTO cadeau VALUES ('BC-AAAA-AAAA','s','2020-01-01','2020-01-02',NULL)");
v = await utiliser("BC-AAAA-AAAA");                 vu("code périmé : refusé", !v.valide && v.raison === "expire");

/* ———— Limitation de débit ———— */
const clefs = [];
e = ENV({ LIMITE: { limit: async o => (clefs.push(o.key), { success: false }) } });
r = await appel(avecPrix, e, "/?session_id=cs_test_dossier0000", { headers: { "CF-Connecting-IP": "203.0.113.9" } });
vu("trop de vérifications : 429", r.status === 429);
r = await poster(avecPrix, e, "/mesure", { e: "accueil" }, { headers: { "CF-Connecting-IP": "203.0.113.9" } });
vu("trop de mesures : 204, rien d'écrit", r.status === 204 && lignes(e).length === 0);
vu("deux compteurs distincts par adresse", clefs[0] === "achat:203.0.113.9" && clefs[1] === "mesure:203.0.113.9");
v = await verifier(ENV({ LIMITE: { limit: async () => { throw new Error("panne"); } } }), "cs_test_dossier0000");
vu("limite en panne : on laisse passer", v.valide);
r = await appel(avecPrix, e, "/mesure", { method: "OPTIONS" });
vu("requête préalable jamais limitée", r.status === 204);
r = await appel(avecPrix, ENV(), "/", { method: "OPTIONS", headers: { Origin: "https://ailleurs.example" } });
vu("CORS : une autre origine n'est pas reflétée", r.headers.get("Access-Control-Allow-Origin") === SITE);

console.log(`\n${ok} ok, ${ko} raté(s)`);
process.exit(ko ? 1 : 0);
