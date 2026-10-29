"use strict";
/* Boussole céleste — tout le site tient dans cette page, et tout se calcule ici.
   Les textes et les données viennent de donnees/ (outils/construire.py les insère
   juste au-dessus) : on ne corrige jamais un texte dans ce fichier.

   La logique reprend celle de Boussole émotionnelle, avec ses correctifs — chaque
   commentaire « piège » ci-dessous raconte une erreur déjà payée là-bas. */

/*@DONNEES@*/

/* ————— Configuration ————— */
const URL_SITE = "boussole-celeste.fr";
const PREFIXE = "celeste";              /* préfixe de toutes les clés de stockage */
const VENTE = {
  actif: true,
  /* Phase de test entre amis : la fenêtre de fin s'affiche, mais un bouton « Passer
     le paiement » débloque tout. À passer à false le jour de la mise en vente. */
  modeTest: true,
  prixResultats: "1,99 €",
  lienResultats: "",
  prixDossier: "5,99 €",
  /* Pas de prix barré ni de pourcentage : une réduction ne peut se référer qu'au prix
     le plus bas pratiqué pendant les 30 jours précédents (art. L112-1-1 du code de la
     consommation). « Tarif de lancement », sans référence, tant qu'aucun autre prix
     n'a été réellement pratiqué. */
  prixDossierRef: "",
  remiseDossier: "",
  lienDossier: "",
  /* Le complément, pour qui a déjà payé les résultats : la différence, et rien de plus. */
  prixComplement: "4 €",
  lienComplement: "",
  /* L'adresse du Worker de vérification. Vide : aucun achat ne peut être vérifié, donc
     « J'ai déjà payé » échoue franchement au lieu d'accorder à l'aveugle. */
  verification: "",
  /* Codes cadeaux : ne s'allument qu'avec la vérification (il faut Stripe pour savoir
     si le dossier a été payé). */
  cadeau: ""
};
const cadeauActif = () => !!VENTE.cadeau && !!VENTE.verification;
/* ?apercu=1 montre la fenêtre de fin sans faire le test. Adossé à modeTest : le jour de
   la mise en vente, cette porte se ferme d'elle-même (piège Boussole : elle était
   indépendante et restait ouverte). */
const APERCU = VENTE.modeTest && new URLSearchParams(location.search).has("apercu");
let niveauAcces = "aucun";   /* "aucun" | "resultats" | "dossier" */
const paywallActif = () => APERCU || VENTE.modeTest || (VENTE.actif && !!VENTE.lienResultats && !!VENTE.lienDossier);

/* ————— Mesure d'audience —————
   Un jour, un nom d'événement, et rien d'autre : pas de cookie, pas d'identifiant,
   pas d'adresse IP. Tant que MESURE est vide, rien ne part. */
const MESURE = "";
function mesurer(e, p){
  if(!MESURE) return;
  try{
    const c = JSON.stringify(p ? { e, p } : { e });
    const b = new Blob([c], { type: "text/plain" });   /* text/plain : pas de requête préalable */
    if(navigator.sendBeacon && navigator.sendBeacon(MESURE, b)) return;
    fetch(MESURE, { method: "POST", body: c, keepalive: true, mode: "cors" });
  }catch(_){}
}

/* ————— Outils ————— */
const $ = sel => document.querySelector(sel);
const N = SITUATIONS.length;
const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const fmt = x => (Math.round(x * 10) / 10).toFixed(1).replace(".", ",");
/* Échappe toute valeur que le site n'a pas écrite lui-même (piège Boussole : une
   faille XSS par le journal importé). */
const esc = v => String(v == null ? "" : v)
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
const maj = s => s.charAt(0).toUpperCase() + s.slice(1);
const EN = Object.fromEntries(ENERGIES.map(e => [e.id, e]));
const IDS = ENERGIES.map(e => e.id);
const ELIDE = v => /^[aeéèêiîoôuy]/i.test(v);
const deVerbe = v => (ELIDE(v) ? "d’" : "de ") + v;
const nomEnergie = id => "l’énergie " + deVerbe(EN[id].verbe);
const ordinal = n => n === 1 ? "1re" : n + "e";
/* Remplit un gabarit des données : {verbe}, {Verbe} (majuscule), {de_verbe}… */
function remplir(t, v){
  return String(t).replace(/\{(\w+)\}/g, (m, k) => {
    if(v[k] != null) return v[k];
    const min = k.charAt(0).toLowerCase() + k.slice(1);
    if(k !== min && v[min] != null) return maj(String(v[min]));
    return m;
  });
}
const COULEURS = { feu:"#E8794F", terre:"#A9B565", air:"#9FD0EC", eau:"#6E97E0" };
const VAR_ELEM = el => `var(--${el})`;
const glyphe = (id, cls = "glyphe") => `<span class="${cls}" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="${GLYPHES[id]}"/></svg></span>`;
const vignette = id => `<span class="vignette" aria-hidden="true">${VIGNETTES[id]}</span>`;
const BANDES = {
  discrete:  { lbl:"Discrète",  c:"var(--faint)" },
  presente:  { lbl:"Présente",  c:"var(--glacier)" },
  dominante: { lbl:"Dominante", c:"var(--or-clair)" }
};
const palierDe = n => n < SEUILS.paliers.discrete ? "discrete" : n > SEUILS.paliers.dominante ? "dominante" : "presente";
const INTENSITES = [["0","Pas du tout"],["1","Un peu"],["2","Moyennement"],["3","Beaucoup"],["4","Énormément"]];

/* ————— État (en mémoire ; seul le brouillon est gardé, sept jours) ————— */
const TOUTES = SITUATIONS.map((_, k) => k);
const TAILLE_TEST = 16;
const PLANCHER_TEST = 8;
const MAX_MOMENTS = 5;
const PRIORITE = ROTATIONS[0];
const state = { i:0, answers: Array.from({length:N}, () => null), reelles: [], selection: [...PRIORITE].sort((a, b) => a - b) };
/* Le jeu change à chaque passage gardé : 8 scènes sur 16 se renouvellent. Raccourci
   par les moments réels, on garde le début du jeu, ordonné pour couvrir les douze
   énergies dès les huit premières scènes. */
function construireSelection(){
  const n = Math.max(PLANCHER_TEST, TAILLE_TEST - 2 * state.reelles.length);
  const t = chargerTests();
  const tour = (t && t.passages.length) ? t.passages.length % ROTATIONS.length : 0;
  state.selection = ROTATIONS[tour].slice(0, n).sort((a, b) => a - b);
}

/* ————— Apparitions douces ————— */
const io = new IntersectionObserver(entries => {
  entries.forEach((en, k) => {
    if(en.isIntersecting){
      en.target.style.transitionDelay = prefersReduced ? "0ms" : `${Math.min(k,4)*70}ms`;
      en.target.classList.add("in");
      io.unobserve(en.target);
    }
  });
}, { threshold: .12 });
document.querySelectorAll(".reveal").forEach(el => io.observe(el));

function showView(id){
  document.querySelectorAll(".view").forEach(v => v.classList.toggle("active", v.id === id));
  window.scrollTo({ top:0, behavior: prefersReduced ? "auto" : "smooth" });
}

/* ————— Les douze énergies ————— */
function renderEnergyCards(){
  $("#emoGrid").innerHTML = ENERGIES.map(e => `
    <details class="emo-card">
      <summary>
        ${vignette(e.id)}
        <span><h3>${maj(e.verbe)}</h3><span class="emo-cat">${e.signe} · ${ELEMENTS[e.element].nom} · ${e.modalite}</span></span>
        <span class="chev" aria-hidden="true">▼</span>
      </summary>
      <div class="emo-body">
        <p class="def">${e.definition}</p>
        <p class="fn"><b>À quoi elle sert&nbsp;:</b> ${e.sert}</p>
        <p class="ex"><b>Comment elle se manifeste&nbsp;:</b> ${e.manifeste}</p>
        <p class="lo"><b>Sa lumière&nbsp;:</b> ${e.lumiere}. <b>Son ombre&nbsp;:</b> ${e.ombre}. <b>Planète&nbsp;:</b> ${e.maitre}.</p>
      </div>
    </details>`).join("");
}

/* ————— Le questionnaire —————
   Chaque scène propose ses réactions, toujours les mêmes, et chacune se note de 0 à 4.
   Le nom de l'énergie n'apparaît pas : la personne note des comportements, pas des
   signes, pour ne pas répondre « comme son signe ». */
function renderQuestion(){
  const i = state.i, idx = state.selection[i], s = SITUATIONS[idx];
  const a = state.answers[idx] || (state.answers[idx] = {});
  const total = state.selection.length;
  $("#qDomain").textContent = s.dom;
  $("#qCount").textContent = `${i+1} / ${total}`;
  $("#qFill").style.width = `${((i+1)/total)*100}%`;
  document.querySelector(".track").setAttribute("aria-valuemax", total);
  document.querySelector(".track").setAttribute("aria-valuenow", i+1);
  $("#qText").textContent = s.txt;
  $("#evalRows").innerHTML = s.reac.map(([id, txt], k) => `
    <div class="eval-row${a[id] != null ? " ok" : ""}" data-e="${id}">
      <p class="eval-txt" id="reac-${k}">${txt}</p>
      <span class="eval-scale" role="radiogroup" aria-labelledby="reac-${k}" aria-label="Réaction ${k + 1}">
        ${INTENSITES.map(([v, lbl]) => `<button class="seg${a[id] === +v ? " sel" : ""}" data-v="${v}" role="radio" aria-checked="${a[id] === +v}">${lbl}</button>`).join("")}
      </span>
    </div>`).join("");
  $("#evalRows").querySelectorAll(".eval-row").forEach(row =>
    row.querySelectorAll(".seg").forEach(b => b.addEventListener("click", () => noter(row.dataset.e, +b.dataset.v))));
  $("#btnPrev").innerHTML = i === 0
    ? '<span class="ico" style="order:-1" aria-hidden="true">←</span> Mon journal'
    : '<span class="ico" style="order:-1" aria-hidden="true">←</span> Précédente';
  $("#btnNext").innerHTML = i === total-1
    ? 'Voir mes résultats <span class="ico" aria-hidden="true">✦</span>'
    : 'Suivante <span class="ico" aria-hidden="true">→</span>';
  updateNav();
}
const estComplete = idx => SITUATIONS[idx].reac.every(([id]) => (state.answers[idx] || {})[id] != null);
/* Noter met à jour la ligne sur place, sans redessiner la scène : le focus clavier
   reste où il est (piège Boussole : chaque clic renvoyait le focus en haut). */
function noter(id, v){
  const idx = state.selection[state.i];
  const a = state.answers[idx] || (state.answers[idx] = {});
  a[id] = v;
  const row = $("#evalRows").querySelector(`.eval-row[data-e="${id}"]`);
  row.classList.add("ok");
  row.querySelectorAll(".seg").forEach(b => {
    const sel = +b.dataset.v === v;
    b.classList.toggle("sel", sel);
    b.setAttribute("aria-checked", sel);
    b.tabIndex = sel ? 0 : -1;
  });
  updateNav();
  sauverBrouillon();
}
/* « Tout le reste à pas du tout » : ne touche pas à ce qui est déjà noté. */
function toutRien(){
  const idx = state.selection[state.i];
  const a = state.answers[idx] || (state.answers[idx] = {});
  SITUATIONS[idx].reac.forEach(([id]) => { if(a[id] == null) a[id] = 0; });
  renderQuestion();
  sauverBrouillon();
  $("#btnNext").focus();
}
function updateNav(){
  const btn = $("#btnNext");
  const idx = state.selection[state.i];
  const a = state.answers[idx] || {};
  const reste = SITUATIONS[idx].reac.filter(([id]) => a[id] == null).length;
  btn.disabled = reste > 0;
  $("#nextHint").textContent = reste === 0 ? ""
    : reste === SITUATIONS[idx].reac.length ? "Note chaque réaction pour continuer."
    : `Encore ${reste} réaction${reste > 1 ? "s" : ""} à noter.`;
}
function gotoQuestion(idx){
  sauverBrouillon();
  const card = $("#qCard");
  if(prefersReduced){ state.i = idx; renderQuestion(); window.scrollTo({top:0}); return; }
  card.classList.add("fading");
  setTimeout(() => {
    state.i = idx; renderQuestion();
    card.classList.remove("fading");
    window.scrollTo({ top:0, behavior:"smooth" });
  }, 250);
}

/* ————— Le journal, étape du parcours ————— */
const JOURNAL_KEY = PREFIXE + ".journal.v1";
const CONTEXTES = ["Travail", "Famille", "Couple", "Amis", "Santé", "Argent", "Seul·e", "Autre"];
const JOURS_FR = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
const CORPS_NIVEAUX = ["Très calme", "Posé", "Neutre", "Activé", "En surchauffe"];
const SENSATIONS = ["Gorge serrée", "Ventre noué", "Cœur qui s’accélère", "Chaleur au visage", "Épaules tendues", "Mâchoires serrées", "Souffle court", "Larmes proches", "Lourdeur ou vide", "Bouffée d’énergie"];
const CONFIANCES = ["J’hésite", "Plutôt sûr·e", "Très sûr·e"];
const ELANS = ["Me retirer", "En parler à quelqu’un", "Régler le problème", "Décharger", "Bouger, me dépenser", "Me figer", "Réparer, m’excuser", "Fêter, partager"];
const IMPORTANTS = ["Respect", "Lien", "Reconnaissance", "Sécurité", "Justice", "Liberté", "Appartenance", "Accomplissement"];
const saisieVierge = () => ({ emos: {}, ctx: new Set(), sens: new Set(), imp: new Set(), corps: null, conf: null, elan: null });
let saisie = saisieVierge();

/* Redessine un groupe de puces, et rend le focus à la puce actionnée : sans ça, chaque
   clic renvoyait le focus clavier au début du document. */
function groupeChips(sel, liste, estSel, clic, rerender){
  $(sel).innerHTML = liste.map((c, k) => `<button class="j-chip${estSel(c, k) ? " sel" : ""}" aria-pressed="${!!estSel(c, k)}" data-k="${k}">${esc(c)}</button>`).join("");
  $(sel).querySelectorAll(".j-chip").forEach(b => b.addEventListener("click", () => {
    clic(liste[+b.dataset.k], +b.dataset.k);
    rerender();
    const r = $(`${sel} .j-chip[data-k="${b.dataset.k}"]`);
    if(r) r.focus();
  }));
}
function renderPerso(){
  groupeChips("#jCtx", CONTEXTES, c => saisie.ctx.has(c), c => saisie.ctx.has(c) ? saisie.ctx.delete(c) : saisie.ctx.add(c), renderPerso);
  groupeChips("#jCorps", CORPS_NIVEAUX, (c, k) => saisie.corps === k + 1, (c, k) => { saisie.corps = saisie.corps === k + 1 ? null : k + 1; }, renderPerso);
  groupeChips("#jSens", SENSATIONS, c => saisie.sens.has(c), c => saisie.sens.has(c) ? saisie.sens.delete(c) : saisie.sens.add(c), renderPerso);
  groupeChips("#jConf", CONFIANCES, (c, k) => saisie.conf === k + 1, (c, k) => { saisie.conf = saisie.conf === k + 1 ? null : k + 1; }, renderPerso);
  groupeChips("#jElan", ELANS, c => saisie.elan === c, c => { saisie.elan = saisie.elan === c ? null : c; }, renderPerso);
  groupeChips("#jImp", IMPORTANTS, c => saisie.imp.has(c), c => {
    if(saisie.imp.has(c)) saisie.imp.delete(c);
    else if(saisie.imp.size < 2) saisie.imp.add(c);
  }, renderPerso);

  if(!$("#jTriche").innerHTML){
    $("#jTriche").innerHTML = ENERGIES.map(e => `
      <div class="j-triche-row">${glyphe(e.id)}<span><b>${maj(e.verbe)}</b> (${e.signe}). ${e.court.replace(/^[^:]+:\s*/, "")}</span></div>`).join("");
  }
  $("#jEmos").innerHTML = ENERGIES.map(e => `
    <button class="j-chip${saisie.emos[e.id] != null ? " sel" : ""}" aria-pressed="${saisie.emos[e.id] != null}" data-emo="${e.id}">
      ${glyphe(e.id)}${maj(e.verbe)}
    </button>`).join("");
  $("#jEmos").querySelectorAll(".j-chip").forEach(b => b.addEventListener("click", () => {
    const id = b.dataset.emo;
    if(saisie.emos[id] != null) delete saisie.emos[id];
    else{
      if(Object.keys(saisie.emos).length >= 3){ $("#jFeedback").textContent = "Trois énergies au plus par moment : garde les plus fortes."; return; }
      saisie.emos[id] = 2;
    }
    $("#jFeedback").textContent = "";
    renderPerso();
    const r = $(`#jEmos .j-chip[data-emo="${id}"]`);
    if(r) r.focus();
  }));
  const nb = Object.keys(saisie.emos).length;
  $("#jIntensites").innerHTML = Object.keys(saisie.emos).map(id => `
    <div class="j-int-row" data-emo="${id}"><span class="nm">${maj(EN[id].verbe)}</span>
      <span class="eval-scale" role="radiogroup" aria-label="Force : ${EN[id].verbe}">
        ${[1,2,3,4].map(v => `<button class="seg${saisie.emos[id] === v ? " sel" : ""}" role="radio" aria-checked="${saisie.emos[id] === v}" data-v="${v}">${INTENSITES[v][1]}</button>`).join("")}
      </span></div>`).join("");
  $("#jIntensites").querySelectorAll(".j-int-row").forEach(row =>
    row.querySelectorAll(".seg").forEach(b => b.addEventListener("click", () => {
      saisie.emos[row.dataset.emo] = +b.dataset.v;
      renderPerso();
      const r = $(`#jIntensites .j-int-row[data-emo="${row.dataset.emo}"] .seg[data-v="${b.dataset.v}"]`);
      if(r) r.focus();
    })));
  $("#jConfBloc").classList.toggle("j-attente", nb === 0);
  $("#jConfAttente").hidden = nb > 0;
  $("#btnMomentAjout").disabled = nb === 0 || state.reelles.length >= MAX_MOMENTS;
  const dispo = chargerJournal() !== null;
  $("#jIndispo").hidden = dispo;
  $("#jStockNote").textContent = dispo
    ? "Chaque moment ajouté rejoint ton journal, gardé sur cet appareil uniquement."
    : "";
  majPersoCompte();
  renderJournalBlocs();
}
function majPersoCompte(){
  const R = state.reelles.length;
  const n = Math.max(PLANCHER_TEST, TAILLE_TEST - 2 * R);
  $("#persoCompte").textContent = R === 0
    ? `Rien à noter aujourd’hui ? Aucun souci, le test t’attend : ${TAILLE_TEST} situations.`
    : `${R}/${MAX_MOMENTS} moment${R > 1 ? "s" : ""} noté${R > 1 ? "s" : ""}. Le test passe à ${n} situations.`;
  $("#btnPersoContinuer").innerHTML = (R === 0 ? "Commencer le test" : "Continuer vers le test") + ' <span class="ico" aria-hidden="true">→</span>';
}
function ajouterMoment(){
  if(state.reelles.length >= MAX_MOMENTS){ $("#jFeedback").textContent = "Cinq moments au plus par passage : c’est déjà très riche."; return; }
  if(!Object.keys(saisie.emos).length){ $("#jFeedback").textContent = "Choisis d’abord une ou plusieurs énergies (question 4)."; return; }
  /* Un moment ne parle que des énergies qu'il nomme : lui seul compte pour elles. */
  state.reelles.push({ emos: { ...saisie.emos } });
  const j = chargerJournal();
  if(j){
    const entree = { d: new Date().toISOString(), emos: { ...saisie.emos }, ctx: [...saisie.ctx], note: $("#jNote").value.trim().slice(0, 500) };
    if(saisie.corps) entree.corps = saisie.corps;
    if(saisie.sens.size) entree.sens = [...saisie.sens];
    if(saisie.conf) entree.conf = saisie.conf;
    if(saisie.elan) entree.elan = saisie.elan;
    if(saisie.imp.size) entree.imp = [...saisie.imp];
    j.entrees.push(entree);
    sauverJournal(j);
  }
  saisie = saisieVierge();
  $("#jNote").value = "";
  renderPerso();
  sauverBrouillon();
  $("#jFeedback").textContent = "C’est noté. Ce moment compte dans tes résultats et rejoint ton journal.";
  setTimeout(() => { $("#jFeedback").textContent = ""; }, 4000);
}

/* ————— Le calcul —————
   La note d'une énergie est une intensité moyenne : somme de ses crans ÷ (4 × nombre
   de mesures) × 10. Elle est tempérée par la confiance, pour qu'une énergie mesurée
   une seule fois à fond ne coiffe pas une énergie présente partout.

   Une différence avec Boussole, et elle est voulue : là-bas, chaque émotion était
   proposée à chaque scène, et le plafond de confiance se rapportait au nombre de
   scènes. Ici, chaque énergie n'est proposée que dans les scènes qui portent sa
   réaction — cinq au moins dans un jeu complet. Le plafond se rapporte donc à cette
   couverture garantie : à partir de cinq mesures, une énergie est crue sur parole, et
   « tout à 4 » donne bien 10/10. Une mesure unique ne dépasse pas 4/10.

   Dans ce test, chaque réaction présentée est notée, zéro compris : la note dit donc
   directement la place que l'énergie occupe dans les réponses. Là où Boussole devait
   distinguer une « place » d'une « intensité » (parce qu'on y choisissait ses
   émotions), les deux coïncident ici, et les textes se lisent sur la note. */
const COUVERTURE = 5;
const K_CONFIANCE = 3;
function cumuls(answers, reelles, selection){
  const totaux = {}, maxima = {};
  IDS.forEach(id => { totaux[id] = 0; maxima[id] = 0; });
  const idxs = (selection && selection.length) ? selection : TOUTES;
  idxs.forEach(k => {
    const a = answers[k] || {};
    for(const id in a){
      if(maxima[id] === undefined || a[id] == null) continue;
      maxima[id] += 4; totaux[id] += a[id];
    }
  });
  /* Un moment réel ne compte que pour les énergies qu'il nomme : ne pas nommer une
     énergie ne veut pas dire l'avoir vécue à zéro. */
  (reelles || []).forEach(r => {
    const em = r.emos || {};
    for(const id in em){
      if(maxima[id] === undefined) continue;
      maxima[id] += 4; totaux[id] += em[id];
    }
  });
  return { totaux, maxima };
}
function computeScores(answers, reelles, selection){
  const { totaux, maxima } = cumuls(answers, reelles, selection);
  const plafond = COUVERTURE / (COUVERTURE + K_CONFIANCE);
  const notes = {};
  IDS.forEach(id => {
    if(!maxima[id]){ notes[id] = 0; return; }   /* pas mesurée : jamais lue comme un zéro, voir lastMesures */
    const mesures = maxima[id] / 4;
    const intensite = totaux[id] / maxima[id] * 10;
    const confiance = Math.min(1, (mesures / (mesures + K_CONFIANCE)) / plafond);
    notes[id] = Math.round(intensite * confiance * 10) / 10;
  });
  return notes;
}
function compterMesures(answers, reelles, selection){
  const { maxima } = cumuls(answers, reelles, selection);
  return Object.fromEntries(IDS.map(id => [id, maxima[id] / 4]));
}
/* La répartition : la part de chaque élément dans l'ensemble des crans donnés, en
   pourcentage, arrondie au plus fort reste pour que la somme fasse exactement 100. */
function repartition(answers, reelles, selection){
  const { totaux } = cumuls(answers, reelles, selection);
  const els = Object.keys(ELEMENTS);
  const sommes = els.map(el => ELEMENTS[el].ids.reduce((t, id) => t + totaux[id], 0));
  const tot = sommes.reduce((a, b) => a + b, 0);
  const r = {};
  if(!tot){ els.forEach(el => { r[el] = 0; }); return r; }
  const brut = sommes.map(s => s / tot * 100);
  const bas = brut.map(Math.floor);
  let reste = 100 - bas.reduce((a, b) => a + b, 0);
  brut.map((b, k) => [b - bas[k], k]).sort((a, b) => b[0] - a[0]).forEach(([_, k]) => { if(reste > 0){ bas[k]++; reste--; } });
  els.forEach((el, k) => { r[el] = bas[k]; });
  return r;
}
/* Moyenne d'un groupe (élément ou modalité), sur les seules énergies mesurées :
   compter une énergie non mesurée comme un zéro inventerait un manque. */
function moyenneGroupe(ids, notes){
  const vus = ids.filter(id => mesuree(id));
  if(!vus.length) return null;
  return Math.round(vus.reduce((t, id) => t + notes[id], 0) / vus.length * 10) / 10;
}
function profilGroupes(notes, groupes){
  return Object.fromEntries(Object.entries(groupes).map(([k, g]) => [k, moyenneGroupe(g.ids, notes)]));
}

/* ————— Résultats ————— */
let lastNotes = null, lastMesures = null, lastPart = null;
let resultatsGardesCe = false;
const mesuree = id => !lastMesures || lastMesures[id] > 0;
const rang = id => (lastNotes || {})[id] || 0;
const tri = () => [...ENERGIES].sort((a, b) => rang(b.id) - rang(a.id));
const triMesurees = () => tri().filter(e => mesuree(e.id));
const nbMesures = id => lastMesures ? lastMesures[id] : 0;
const txtMesures = n => `${n} mesure${n > 1 ? "s" : ""}`;

function renderResults(notes){
  const T = tri(), M = triMesurees();
  const date = new Date().toLocaleDateString("fr-FR", { weekday:"long", day:"numeric", month:"long", year:"numeric" });
  $("#resDate").textContent = `Test réalisé le ${date}. Tes réponses n’ont pas quitté ton navigateur.`;

  const ciel = cielDuMoment(notes);
  $("#cielTitre").textContent = ciel.titre;
  $("#cielPhrase").textContent = ciel.phrase;

  $("#resTop3").innerHTML = M.slice(0, 3).map((e, k) => `
    <div class="podium-row">
      <span class="podium-rank">${k+1}</span>
      ${vignette(e.id)}
      <span class="podium-name">${maj(e.verbe)}<span class="podium-sous">${e.signe} · ${txtMesures(nbMesures(e.id))}</span></span>
      <span class="podium-score" style="color:${VAR_ELEM(e.element)}">${fmt(notes[e.id])}</span>
    </div>`).join("");

  const nonMesurees = T.filter(e => !mesuree(e.id));
  const discretes = M.filter(e => palierDe(notes[e.id]) === "discrete").reverse().slice(0, 4);
  $("#resLow").innerHTML = (discretes.length
      ? discretes.map(e => `<span class="low-chip">${glyphe(e.id)} ${maj(e.verbe)} · ${fmt(notes[e.id])}</span>`).join("")
      : `<span class="low-chip">Aucune énergie n’est vraiment en retrait</span>`)
    + nonMesurees.map(e => `<span class="low-chip absente">${glyphe(e.id)} ${maj(e.verbe)} · ${NON_MESUREE.toLowerCase()}</span>`).join("");
  $("#resLowNote").textContent = (discretes.length
      ? "Ces énergies tiennent peu de place dans tes réponses. Ce n’est pas un manque : ta vie actuelle les sollicite moins. "
      : "Toutes tes énergies mesurées occupent au moins une place moyenne. ")
    + (nonMesurees.length ? "Les énergies non mesurées n’ont pas de note : le test n’a rien à en dire, ce n’est pas un zéro." : "");

  /* Éléments et modalités : la moyenne des énergies mesurées de chacun. */
  const pe = profilGroupes(notes, ELEMENTS), pm = profilGroupes(notes, MODALITES);
  const domEl = Object.keys(pe).filter(k => pe[k] != null).sort((a, b) => pe[b] - pe[a])[0];
  const jauge = (k, nom, v, couleur, dom) => `
    <div class="jauge${dom ? " dom" : ""}"><span><span class="pt" style="background:${couleur}"></span>${nom}</span>
      <span class="tr"><span class="fl" style="width:${v == null ? 0 : v * 10}%; background:${couleur}"></span></span>
      <span class="v">${v == null ? "—" : fmt(v)}</span></div>`;
  $("#resElements").innerHTML =
      `<p class="jauge-titre">La part de chaque élément</p>
       <div class="repart">${Object.keys(ELEMENTS).map(el => `<span style="width:${lastPart[el]}%; background:${VAR_ELEM(el)}"></span>`).join("")}</div>
       <div class="repart-legende">${Object.keys(ELEMENTS).map(el => `<span>${ELEMENTS[el].nom}&nbsp;${lastPart[el]}&nbsp;%</span>`).join("")}</div>
       <p class="jauge-titre">Les éléments, sur 10</p>`
    + Object.entries(ELEMENTS).map(([k, g]) => jauge(k, `${g.nom} · ${g.mode}`, pe[k], VAR_ELEM(k), k === domEl)).join("")
    + `<p class="jauge-titre">Tes façons d’avancer</p>`
    + Object.entries(MODALITES).map(([k, g]) => jauge(k, maj(g.mode), pm[k], "var(--or)", false)).join("");
  $("#resElementsNote").textContent = domEl
    ? `${maj(ELEMENTS[domEl].art)}${ELEMENTS[domEl].nom} pèse le plus en ce moment : tu vis surtout sur le mode « ${ELEMENTS[domEl].mode} ».`
    : "";

  $("#roueWrap").innerHTML = buildRoue(notes);
  $("#roueLegende").innerHTML = Object.keys(ELEMENTS).map(el =>
    `<span class="${el === domEl ? "dom" : ""}"><span class="pastille" style="background:${VAR_ELEM(el)}"></span>${ELEMENTS[el].nom}${el === domEl ? " · dominant" : ""}</span>`).join("");

  $("#barsWrap").innerHTML = T.map(e => {
    const nm = mesuree(e.id), b = BANDES[palierDe(notes[e.id])];
    return `<div class="bar-row${nm ? "" : " absente"}">
      <div class="bar-id">${glyphe(e.id)}
        <span><span class="nm">${maj(e.verbe)}</span><span class="band" style="color:${nm ? b.c : "var(--faint)"}">${nm ? `${b.lbl} · ${txtMesures(nbMesures(e.id))}` : NON_MESUREE}</span></span></div>
      <div class="bar-track">${nm ? `<div class="bar-fill" data-w="${notes[e.id]*10}" style="background:${VAR_ELEM(e.element)}"></div>` : ""}</div>
      <div class="bar-score" style="color:${nm ? VAR_ELEM(e.element) : "var(--faint)"}">${nm ? fmt(notes[e.id]) : "—"}</div>
    </div>`;
  }).join("");

  $("#analysesWrap").innerHTML = T.map((e, k) => {
    const nm = mesuree(e.id), bd = palierDe(notes[e.id]), b = BANDES[bd];
    /* Un texte d'analyse décrit une vie intérieure : le servir sur une énergie non
       mesurée, ce serait décrire ce qu'on n'a pas mesuré. */
    const corps = nm ? `<p>${e.paliers[bd]}</p>`
      : `<p>Aucune scène de ton parcours n’a mesuré cette énergie. Le test n’a donc rien à en dire, et surtout pas qu’elle serait absente de ta vie.</p>`;
    return `<details class="ana${nm ? "" : " absente"}"${k < 3 && nm ? " open" : ""}>
      <summary>
        ${vignette(e.id)}
        <span class="ana-name">${maj(e.verbe)}<small>${e.signe} · ${ELEMENTS[e.element].nom} · ${e.modalite}</small></span>
        <span class="ana-band" style="background:var(--or-soft); color:${nm ? b.c : "var(--faint)"}">${nm ? b.lbl : NON_MESUREE}</span>
        <span class="ana-score">${nm ? fmt(notes[e.id]) : "—"}</span>
        <span class="ana-chev" aria-hidden="true">▼</span>
      </summary>
      <div class="ana-body">${corps}</div>
    </details>`;
  }).join("");

  $("#syntheseWrap").innerHTML = buildSynthese(notes);
  $("#compResultat").hidden = true;
  $("#compInfo").textContent = "";
  $("#compCode").value = "";
  majSigne();
  majVenteBox();
  majGardeBox();
  requestAnimationFrame(() => requestAnimationFrame(() => {
    document.querySelectorAll(".bar-fill").forEach(f => f.style.width = f.dataset.w + "%");
  }));
}

/* ————— La roue zodiacale —————
   Douze secteurs, Bélier en haut, dans le sens des aiguilles d'une montre : ce n'est pas
   un thème astral (ni maisons, ni ascendant), et l'œil lit un cadran à partir du haut.
   Chaque secteur est rempli selon la note et coloré par élément ; une énergie non
   mesurée reste en pointillés, jamais à zéro ; un arc doré marque l'élément dominant.
   `pal` permet de dessiner avec des couleurs écrites en clair (pour les cartes en
   canvas, qui ne lisent pas les variables CSS). */
function buildRoue(notes, pal){
  const c = pal || {};
  const col = (nom, defaut) => c[nom] || defaut;
  const cx = 200, cy = 200, R = 146, r0 = 38, RG = 176;
  const pt = (a, r) => [cx + Math.cos(a * Math.PI / 180) * r, cy + Math.sin(a * Math.PI / 180) * r];
  const f = n => n.toFixed(1);
  const secteur = (a1, a2, rExt, rInt) => {
    const [x1, y1] = pt(a1, rExt), [x2, y2] = pt(a2, rExt), [x3, y3] = pt(a2, rInt), [x4, y4] = pt(a1, rInt);
    return `M${f(x1)} ${f(y1)}A${rExt} ${rExt} 0 0 1 ${f(x2)} ${f(y2)}L${f(x3)} ${f(y3)}A${rInt} ${rInt} 0 0 0 ${f(x4)} ${f(y4)}Z`;
  };
  const pe = profilGroupes(notes, ELEMENTS);
  const domEl = Object.keys(pe).filter(k => pe[k] != null).sort((a, b) => pe[b] - pe[a])[0];
  let s = "";
  [2.5, 5, 7.5, 10].forEach(v => {
    s += `<circle cx="${cx}" cy="${cy}" r="${f(r0 + (R - r0) * v / 10)}" fill="none" style="stroke:${col("trait", "var(--hairline-strong)")}" stroke-width="${v === 10 ? 1.2 : .7}"/>`;
  });
  ENERGIES.forEach((e, k) => {
    const a = -90 + k * 30, a1 = a - 14.2, a2 = a + 14.2;
    s += `<path d="${secteur(a1, a2, R, r0)}" style="fill:${col("piste", "var(--hairline)")}"/>`;
    if(mesuree(e.id)){
      const r = r0 + (R - r0) * Math.max(0, Math.min(10, notes[e.id])) / 10;
      if(r > r0 + .5) s += `<path d="${secteur(a1, a2, r, r0)}" style="fill:${col(e.element, VAR_ELEM(e.element))}"/>`;
    }else{
      const rm = r0 + (R - r0) / 2, [x1, y1] = pt(a1 + 2, rm), [x2, y2] = pt(a2 - 2, rm);
      s += `<path d="M${f(x1)} ${f(y1)}A${rm} ${rm} 0 0 1 ${f(x2)} ${f(y2)}" fill="none" style="stroke:${col("discret", "var(--faint)")}" stroke-width="2" stroke-dasharray="1 5" stroke-linecap="round"/>`;
    }
    if(e.element === domEl){
      const ra = R + 7, [x1, y1] = pt(a1, ra), [x2, y2] = pt(a2, ra);
      s += `<path d="M${f(x1)} ${f(y1)}A${ra} ${ra} 0 0 1 ${f(x2)} ${f(y2)}" fill="none" style="stroke:${col("or", "var(--or)")}" stroke-width="3" stroke-linecap="round"/>`;
    }
    const [gx, gy] = pt(a, RG);
    s += `<g transform="translate(${f(gx - 11)} ${f(gy - 11)}) scale(.9167)" fill="none" style="stroke:${mesuree(e.id) ? col(e.element, VAR_ELEM(e.element)) : col("discret", "var(--faint)")}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="${GLYPHES[e.id]}"/></g>`;
  });
  s += `<circle cx="${cx}" cy="${cy}" r="${r0 - 4}" style="fill:${col("centre", "var(--card)")};stroke:${col("trait", "var(--hairline-strong)")}"/>`;
  const etoile = Array.from({length:8}, (_, k) => {
    const [x, y] = pt(k * 45 - 90, k % 2 ? 5 : 16); return `${f(x)},${f(y)}`;
  }).join(" ");
  s += `<polygon points="${etoile}" style="fill:${col("or", "var(--or)")}"/>`;
  const top = triMesurees().slice(0, 3).map(e => `${e.verbe} ${fmt(notes[e.id])}`).join(", ");
  return `<svg viewBox="0 0 400 400" role="img" aria-label="Ta roue des douze énergies. Les plus présentes : ${top}."${pal ? ' xmlns="http://www.w3.org/2000/svg" width="800" height="800"' : ""}>${s}</svg>`;
}

/* ————— Les croisements —————
   Chaque règle exige que les énergies concernées aient été mesurées : un croisement
   tiré d'aucune donnée, c'est le bug le plus coûteux qu'ait eu Boussole. */
function listeCombos(notes){
  const HI = SEUILS.haut, LO = SEUILS.bas;
  const haut = id => mesuree(id) && notes[id] >= HI;
  const pe = profilGroupes(notes, ELEMENTS), pm = profilGroupes(notes, MODALITES);
  const out = [];
  let retraitFait = false;
  CROISEMENTS.forEach(c => {
    if(c.type === "paire"){
      if(haut(c.a) && haut(c.b)) out.push({ titre: c.titre, t: c.texte });
    }else if(c.type === "element_retrait"){
      if(retraitFait) return;
      const el = Object.keys(ELEMENTS).find(k => ELEMENTS[k].ids.every(id => mesuree(id)) && pe[k] != null && pe[k] <= LO);
      if(el){
        retraitFait = true;
        out.push({ titre: c.titre, t: remplir(c.texte, { el: ELEMENTS[el].nom, el_ids: listeVerbes(ELEMENTS[el].ids), piste: c.pistes[el] }) });
      }
    }else if(c.type === "element_domine"){
      const els = Object.keys(pe).filter(k => pe[k] != null && ELEMENTS[k].ids.filter(id => mesuree(id)).length >= 2).sort((a, b) => pe[b] - pe[a]);
      if(els.length >= 2 && ELEMENTS[els[0]].ids.every(id => mesuree(id)) && pe[els[0]] >= 5.5 && pe[els[0]] - pe[els[1]] >= 2){
        const h = ELEMENTS[els[0]], b = ELEMENTS[els[els.length - 1]];
        out.push({ titre: c.titre, t: remplir(c.texte, { el: h.nom, El_art: maj(h.art), el_ids: listeVerbes(h.ids), el_mode: h.mode, bas: b.nom, bas_art: b.art }) });
      }
    }else if(c.type === "modalite"){
      /* Le texte nomme les quatre énergies de chaque modalité : toutes doivent être mesurées. */
      const toutes = MODALITES[c.haut].ids.concat(MODALITES[c.bas].ids).every(id => mesuree(id));
      const h = pm[c.haut], b = pm[c.bas];
      if(toutes && h >= 5 && h - b >= 2) out.push({ titre: c.titre, t: c.texte });
    }
  });
  return out;
}
const listeVerbes = ids => {
  const v = ids.map(id => EN[id].verbe);
  return v.length > 1 ? v.slice(0, -1).join(", ") + " et " + v[v.length - 1] : v[0];
};

/* ————— Ton ciel du moment —————
   Une saison, jamais une identité : il se lit sur le duo des deux énergies les plus
   présentes, mesurées, selon leurs éléments. */
function cielDuMoment(notes){
  const M = triMesurees().filter(e => notes[e.id] > 0);
  if(M.length < 2) return { titre: CIEL_VOILE.titre, phrase: CIEL_VOILE.phrase };
  const [t1, t2] = M;
  if(notes[t2.id] >= CIEL_PLANCHER){
    const r = CIELS.find(c => (c.elements[0] === t1.element && c.elements[1] === t2.element)
                           || (c.elements[1] === t1.element && c.elements[0] === t2.element));
    if(r) return { titre: r.titre, phrase: `${maj(t1.verbe)} et ${t2.verbe} prennent le plus de place en ce moment. ${r.phrase} ${CIEL_FIN}` };
  }
  const pe = profilGroupes(notes, ELEMENTS);
  const els = Object.keys(pe).filter(k => pe[k] != null).sort((a, b) => pe[b] - pe[a]);
  if(els.length >= 2 && ELEMENTS[els[0]].ids.every(id => mesuree(id)) && pe[els[0]] - pe[els[1]] >= 1.5){
    const g = ELEMENTS[els[0]];
    return { titre: CIEL_ELEMENT.titre[els[0]],
             phrase: remplir(CIEL_ELEMENT.phrase, { el: g.nom, el_art: g.art, el_ids: listeVerbes(g.ids), el_mode: g.mode }) + " " + CIEL_FIN };
  }
  return { titre: CIEL_PARTAGE.titre, phrase: CIEL_PARTAGE.phrase + " " + CIEL_FIN };
}

/* ————— Synthèse croisée ————— */
function buildSynthese(notes){
  const M = triMesurees();
  const ph = [];
  if(M.length >= 3) ph.push(`En ce moment, ce sont surtout ${M[0].verbe}, ${M[1].verbe} et ${M[2].verbe} qui prennent de la place dans tes réponses.`);
  const pe = profilGroupes(notes, ELEMENTS), pm = profilGroupes(notes, MODALITES);
  const els = Object.keys(pe).filter(k => pe[k] != null).sort((a, b) => pe[b] - pe[a]);
  if(els.length >= 2){
    const h = ELEMENTS[els[0]], b = ELEMENTS[els[els.length - 1]];
    ph.push(pe[els[0]] - pe[els[els.length - 1]] >= 1.5
      ? `Côté éléments, ${h.art}${h.nom} domine (${fmt(pe[els[0]])}), et ${b.art}${b.nom} est le plus discret (${fmt(pe[els[els.length - 1]])}).`
      : `Côté éléments, aucun ne domine vraiment : le Feu, la Terre, l’Air et l’Eau se partagent la place.`);
  }
  const mods = Object.keys(pm).filter(k => pm[k] != null).sort((a, b) => pm[b] - pm[a]);
  if(mods.length >= 2){
    ph.push(pm[mods[0]] - pm[mods[mods.length - 1]] >= 1.5
      ? `Pour avancer, tu passes surtout par le mode « ${MODALITES[mods[0]].mode} », plus que par « ${MODALITES[mods[mods.length - 1]].mode} ».`
      : `Tes façons d’avancer s’équilibrent : lancer, tenir et adapter se partagent la place.`);
  }
  const combos = listeCombos(notes).slice(0, 3);
  combos.forEach(c => ph.push(c.t));
  const discretes = M.filter(e => palierDe(notes[e.id]) === "discrete").reverse().slice(0, 3).map(e => deVerbe(e.verbe));
  if(discretes.length){
    const l = discretes.length > 1 ? discretes.slice(0, -1).join(", ") + " et " + discretes[discretes.length - 1] : discretes[0];
    ph.push(discretes.length > 1
      ? `À l’inverse, les énergies ${l} restent discrètes en ce moment. Ce n’est pas un manque : ta vie actuelle les sollicite moins.`
      : `À l’inverse, l’énergie ${l} reste discrète en ce moment. Ce n’est pas un manque : ta vie actuelle la sollicite moins.`);
  }
  ph.push("Ces notes décrivent une période, pas une personnalité : elles bougeront avec ce que tu traverses.");
  const coupe = Math.min(3, Math.max(1, ph.length - 2));
  return `<p class="lead-letter">${ph.slice(0, coupe).join(" ")}</p><p>${ph.slice(coupe).join(" ")}</p>`;
}

/* ————— Copier les résultats ————— */
function buildCopyText(notes){
  const M = triMesurees(), absentes = tri().filter(e => !mesuree(e.id));
  const date = new Date().toLocaleDateString("fr-FR");
  const ciel = cielDuMoment(notes);
  /* Le nombre de mesures accompagne la note : « 10/10 » partagé seul laisserait
     croire à une omniprésence qui peut venir d'une seule scène. */
  const lignes = M.map((e, k) => `${String(k+1).padStart(2, " ")}. ${maj(e.verbe)} (${e.signe}) — ${fmt(notes[e.id])}/10 · ${txtMesures(nbMesures(e.id))} · ${BANDES[palierDe(notes[e.id])].lbl.toLowerCase()}`);
  if(absentes.length) lignes.push("", `Non mesurées : ${absentes.map(e => e.verbe).join(", ")}.`);
  return [
    `✦ Boussole céleste — mes résultats (${date})`, "",
    `Mon ciel du moment : ${ciel.titre}.`, "",
    ...lignes, "",
    `Éléments : ${Object.keys(ELEMENTS).map(el => `${ELEMENTS[el].nom} ${lastPart[el]} %`).join(" · ")}.`, "",
    "Un test de réflexion sur soi, réalisé dans mon navigateur : mes réponses n’en sont jamais sorties.",
    "L’astrologie y sert de langage : elle ne prédit rien."
  ].join("\n");
}
async function copierTexte(texte){
  try{ await navigator.clipboard.writeText(texte); return true; }
  catch(_){
    try{
      const ta = document.createElement("textarea");
      ta.value = texte; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      const ok = document.execCommand("copy"); ta.remove(); return ok;
    }catch(e){ return false; }
  }
}
async function copierResultats(){
  const fb = $("#copyFeedback");
  fb.textContent = await copierTexte(buildCopyText(lastNotes))
    ? "Résultats copiés. Tu peux maintenant les coller où tu veux."
    : "La copie n’a pas fonctionné : tu peux faire une capture d’écran.";
  setTimeout(() => { fb.textContent = ""; }, 5000);
}

/* ————— Le signe de naissance —————
   Facultatif, après les résultats. Jour et mois seulement, jamais l'année, l'heure ni
   le lieu. Calculé ici, gardé dans ce navigateur, et il n'entre dans aucun calcul. */
const SIGNE_KEY = PREFIXE + ".signe.v1";
const MOIS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"];
const JOURS_MOIS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
/* Le ou les signes possibles pour un jour et un mois. Le jour où le Soleil change de
   signe, et la veille, varient d'une année à l'autre : on propose alors les deux. */
function candidatsSigne(j, m){
  if(!(m >= 1 && m <= 12 && j >= 1 && j <= JOURS_MOIS[m - 1])) return [];
  const debuts = [...DEBUTS].sort((a, b) => a[2] - b[2] || a[1] - b[1]);   /* par mois, puis jour */
  const cle = m * 100 + j;
  let k = debuts.length - 1;
  debuts.forEach(([, dj, dm], i) => { if(dm * 100 + dj <= cle) k = i; });
  const actuel = debuts[k][0];
  const suivant = debuts[(k + 1) % debuts.length], precedent = debuts[(k - 1 + debuts.length) % debuts.length];
  const lendemain = new Date(2024, m - 1, j + 1);   /* 2024 : année bissextile, le 29 février existe */
  const estDebut = debuts[k][1] === j && debuts[k][2] === m;
  const veilleDebut = suivant[1] === lendemain.getDate() && suivant[2] === lendemain.getMonth() + 1;
  if(estDebut) return [precedent[0], actuel];
  if(veilleDebut) return [actuel, suivant[0]];
  return [actuel];
}
function lireSigne(){
  try{ const s = JSON.parse(localStorage.getItem(SIGNE_KEY) || "null"); return s && EN[s.signe] ? s : null; }
  catch(_){ return null; }
}
function initSigne(){
  $("#signeJour").innerHTML = `<option value="">Jour</option>` + Array.from({length:31}, (_, k) => `<option value="${k+1}">${k+1}</option>`).join("");
  $("#signeMois").innerHTML = `<option value="">Mois</option>` + MOIS.map((m, k) => `<option value="${k+1}">${m}</option>`).join("");
}
function chercherSigne(){
  const j = +$("#signeJour").value, m = +$("#signeMois").value;
  const c = candidatsSigne(j, m);
  $("#signeInfo").textContent = "";
  if(!c.length){ $("#signeInfo").textContent = j && m ? "Cette date n’existe pas : vérifie le jour et le mois." : "Choisis un jour et un mois."; return; }
  if(c.length === 1){ choisirSigne(c[0], j, m); return; }
  $("#signeLimite").textContent = SIGNE.limite;
  $("#signeLimite").hidden = false;
  $("#signeChoix").hidden = false;
  $("#signeChoix").innerHTML = c.map(id => `<button class="j-chip" data-s="${id}">${glyphe(id)}${EN[id].signe}</button>`).join("");
  $("#signeChoix").querySelectorAll(".j-chip").forEach(b => b.addEventListener("click", () => choisirSigne(b.dataset.s, j, m)));
  $("#signeChoix .j-chip").focus();
}
function choisirSigne(id, j, m){
  try{ localStorage.setItem(SIGNE_KEY, JSON.stringify({ signe: id, j, m })); }catch(_){}
  $("#signeLimite").hidden = true;
  $("#signeChoix").hidden = true;
  majSigne(id);
}
function majSigne(forcer){
  const s = forcer ? { signe: forcer } : lireSigne();
  const box = $("#signeResultat");
  $("#signeForm").hidden = !!s;
  if(!s || !lastNotes){ box.hidden = true; return; }
  const M = triMesurees();
  if(!M.length){ box.hidden = true; return; }
  const e0 = EN[s.signe], e1 = M[0];
  const vars = { s0: e0.signe, v0: e0.verbe, v1: e1.verbe, s1: e1.signe };
  let texte;
  if(e0.id === e1.id) texte = remplir(SIGNE.meme, vars);
  else if(e0.element === e1.element) texte = remplir(SIGNE.element, { ...vars, el: ELEMENTS[e0.element].nom, el_art: ELEMENTS[e0.element].art });
  else if(e0.modalite === e1.modalite) texte = remplir(SIGNE.modalite, { ...vars, mod_mode: SIGNE.mod_mode[e0.modalite] });
  else texte = remplir(SIGNE.autre, vars);
  const position = M.findIndex(e => e.id === e0.id);
  $("#signeCases").innerHTML = `
    <div class="signe-case">${vignette(e0.id)}<span><small>Ton signe de naissance</small><b>${e0.signe}</b><br><span style="color:var(--muted)">l’énergie ${deVerbe(e0.verbe)}</span></span></div>
    <div class="signe-case">${vignette(e1.id)}<span><small>Ton énergie la plus présente</small><b>${maj(e1.verbe)}</b><br><span style="color:var(--muted)">${e1.signe} · ${fmt(lastNotes[e1.id])}/10</span></span></div>`;
  $("#signeTexte").textContent = texte;
  $("#signeRang").textContent = position >= 0
    ? remplir(SIGNE.rang, { ...vars, rang: ordinal(position + 1), note: fmt(lastNotes[e0.id]) })
    : `L’énergie de ton signe (${e0.verbe}) n’a pas été mesurée dans ce test.`;
  box.hidden = false;
}
function effacerSigne(){
  try{ localStorage.removeItem(SIGNE_KEY); }catch(_){}
  $("#signeResultat").hidden = true;
  $("#signeForm").hidden = false;
  $("#signeJour").value = ""; $("#signeMois").value = "";
  $("#signeInfo").textContent = "Ton signe est effacé de ce navigateur.";
}

/* ————— La carte à partager (image fabriquée dans le navigateur) ————— */
const PAL_CANVAS = { ...COULEURS, trait:"rgba(242,235,221,.22)", piste:"rgba(242,235,221,.08)", discret:"#A3A1B8", or:"#D4B06A", centre:"#1F2849" };
const chargeImage = src => new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = src; });
const svgImage = svg => chargeImage("data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg));
const vignetteCanvas = (id, taille) => VIGNETTES[id]
  .replace('<svg ', `<svg width="${taille}" height="${taille * 1.2}" `)
  .replace(/var\(--filet,currentColor\)/g, "#D4B06A").replace(/var\(--etoile,currentColor\)/g, "#F2EBDD")
  .replace(/var\(--glyphe,currentColor\)/g, "#D4B06A");
function fondCanvas(ctx, W, H){
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, "#0F1424"); g.addColorStop(.6, "#1A2140"); g.addColorStop(1, "#11172C");
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const h = ctx.createRadialGradient(W / 2, 0, 0, W / 2, 0, W * .8);
  h.addColorStop(0, "rgba(212,176,106,.16)"); h.addColorStop(1, "rgba(212,176,106,0)");
  ctx.fillStyle = h; ctx.fillRect(0, 0, W, H);
  let graine = 7;
  const alea = () => (graine = (graine * 16807) % 2147483647) / 2147483647;
  for(let k = 0; k < 220; k++){
    ctx.globalAlpha = .25 + alea() * .6;
    ctx.fillStyle = "#F2EBDD";
    ctx.beginPath(); ctx.arc(alea() * W, alea() * H, .6 + alea() * 1.6, 0, Math.PI * 2); ctx.fill();
  }
  ctx.globalAlpha = 1;
}
function texteCentre(ctx, t, x, y, police, couleur, espace){
  ctx.font = police; ctx.fillStyle = couleur; ctx.textAlign = "center";
  if(espace && "letterSpacing" in ctx){ ctx.letterSpacing = espace + "px"; ctx.fillText(t, x, y); ctx.letterSpacing = "0px"; }
  else ctx.fillText(t, x, y);
}
function lignesCoupees(ctx, t, largeur){
  const mots = t.split(" "), l = []; let c = "";
  mots.forEach(m => { const e = c ? c + " " + m : m; if(ctx.measureText(e).width > largeur && c){ l.push(c); c = m; } else c = e; });
  if(c) l.push(c);
  return l;
}
const SERIF_C = '"Cormorant Garamond", Georgia, serif', SANS_C = '"Jost", -apple-system, sans-serif';
async function polices(){
  try{ await Promise.all([document.fonts.load(`600 80px ${SERIF_C}`), document.fonts.load(`400 30px ${SANS_C}`), document.fonts.load(`500 30px ${SANS_C}`)]); }catch(_){}
}
async function genererCartePost(notes){
  await polices();
  const W = 1080, H = 1350, cv = document.createElement("canvas"); cv.width = W; cv.height = H;
  const ctx = cv.getContext("2d");
  fondCanvas(ctx, W, H);
  texteCentre(ctx, "BOUSSOLE CÉLESTE", W / 2, 96, `500 26px ${SANS_C}`, "#D4B06A", 6);
  texteCentre(ctx, "Mon ciel du moment", W / 2, 168, `400 30px ${SANS_C}`, "#B9B7C9");
  const ciel = cielDuMoment(notes);
  ctx.font = `600 84px ${SERIF_C}`;
  lignesCoupees(ctx, ciel.titre, 900).slice(0, 2).forEach((l, k) => texteCentre(ctx, l, W / 2, 262 + k * 84, `600 84px ${SERIF_C}`, "#E3C68B"));
  const roue = await svgImage(buildRoue(notes, PAL_CANVAS));
  ctx.drawImage(roue, W / 2 - 300, 330, 600, 600);
  const M = triMesurees().slice(0, 3);
  const y0 = 990;
  for(let k = 0; k < M.length; k++){
    const e = M[k], y = y0 + k * 92;
    ctx.fillStyle = "rgba(31,40,73,.82)";
    ctx.beginPath(); ctx.roundRect ? ctx.roundRect(150, y, 780, 78, 22) : ctx.rect(150, y, 780, 78); ctx.fill();
    ctx.strokeStyle = "rgba(242,235,221,.12)"; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.save(); ctx.translate(178, y + 17); ctx.scale(1.8, 1.8);
    ctx.strokeStyle = COULEURS[e.element]; ctx.lineWidth = 1.6; ctx.lineCap = "round"; ctx.lineJoin = "round";
    ctx.stroke(new Path2D(GLYPHES[e.id])); ctx.restore();
    /* Les chiffres en Jost : ceux de Cormorant descendent sous la ligne. */
    ctx.textAlign = "left"; ctx.fillStyle = "#D4B06A"; ctx.font = `500 34px ${SANS_C}`;
    ctx.fillText(`${k + 1}`, 250, y + 51);
    ctx.fillStyle = "#F2EBDD"; ctx.font = `600 46px ${SERIF_C}`;
    const titre = maj(e.verbe);
    ctx.fillText(titre, 284, y + 52);
    const lt = ctx.measureText(titre).width + 34;
    ctx.fillStyle = "#B9B7C9"; ctx.font = `400 26px ${SANS_C}`;
    ctx.fillText(e.signe, 250 + lt + 18, y + 50);
    ctx.textAlign = "right"; ctx.fillStyle = COULEURS[e.element]; ctx.font = `500 40px ${SANS_C}`;
    ctx.fillText(fmt(notes[e.id]), 900, y + 54);
  }
  const pe = profilGroupes(notes, ELEMENTS);
  const domEl = Object.keys(pe).filter(k => pe[k] != null).sort((a, b) => pe[b] - pe[a])[0];
  if(domEl) texteCentre(ctx, `Élément dominant : ${ELEMENTS[domEl].art}${ELEMENTS[domEl].nom}`, W / 2, 1290, `400 28px ${SANS_C}`, "#B9B7C9");
  texteCentre(ctx, URL_SITE, W / 2, 1326, `500 24px ${SANS_C}`, "#D4B06A", 3);
  return cv;
}
async function genererCarteStory(notes){
  await polices();
  const W = 1080, H = 1920, cv = document.createElement("canvas"); cv.width = W; cv.height = H;
  const ctx = cv.getContext("2d");
  fondCanvas(ctx, W, H);
  const e = triMesurees()[0];
  texteCentre(ctx, "BOUSSOLE CÉLESTE", W / 2, 150, `500 28px ${SANS_C}`, "#D4B06A", 7);
  texteCentre(ctx, "MON ÉNERGIE LA PLUS PRÉSENTE", W / 2, 300, `500 28px ${SANS_C}`, "#B9B7C9", 5);
  if(e){
    const vig = await svgImage(vignetteCanvas(e.id, 520));
    ctx.drawImage(vig, W / 2 - 260, 360, 520, 624);
    texteCentre(ctx, maj(e.verbe), W / 2, 1140, `600 170px ${SERIF_C}`, "#E3C68B");
    texteCentre(ctx, `${e.signe} · ${ELEMENTS[e.element].nom} · ${e.modalite}`, W / 2, 1210, `400 38px ${SANS_C}`, "#F2EBDD");
    texteCentre(ctx, `${fmt(notes[e.id])} / 10 · ${BANDES[palierDe(notes[e.id])].lbl.toLowerCase()}`, W / 2, 1280, `500 34px ${SANS_C}`, COULEURS[e.element]);
  }
  const roue = await svgImage(buildRoue(notes, PAL_CANVAS));
  ctx.drawImage(roue, W / 2 - 210, 1360, 420, 420);
  texteCentre(ctx, URL_SITE, W / 2, 1850, `500 30px ${SANS_C}`, "#D4B06A", 3);
  return cv;
}
let carteFormat = "post";
const genererCarte = notes => carteFormat === "story" ? genererCarteStory(notes) : genererCartePost(notes);
function lancerRoulette(duree){
  $("#roulette").hidden = false;
  $("#carteImg").style.display = "none";
  return new Promise(res => setTimeout(res, prefersReduced ? 0 : duree));
}
function arreterRoulette(){ $("#roulette").hidden = true; $("#carteImg").style.display = ""; }
async function telechargerFichier(nom, blob){
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = nom;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 4000);
}
let carteBlob = null;
async function fabriquerCarte(duree){
  const attente = lancerRoulette(duree);
  try{
    const cv = await genererCarte(lastNotes);
    if(!carteAutorisee()) return;   /* le droit a pu tomber pendant la fabrication */
    $("#carteImg").src = cv.toDataURL("image/png");
    $("#carteImg").dataset.fmt = carteFormat;
    carteBlob = await new Promise(res => cv.toBlob(res, "image/png"));
    let partageOK = false;
    try{
      const f = new File([carteBlob], "boussole-celeste.png", { type:"image/png" });
      partageOK = !!(navigator.canShare && navigator.canShare({ files:[f] }));
    }catch(_){}
    $("#btnCartePartage").hidden = !partageOK;
    await attente;
  }finally{ arreterRoulette(); }
}
async function ouvrirCarte(){
  if(!lastNotes || !carteAutorisee()) return;
  const btn = $("#btnCarte");
  btn.disabled = true;
  $("#carteOverlay").hidden = false;
  $("#btnCarteFermer").focus();
  try{ await fabriquerCarte(1400); } finally{ btn.disabled = false; }
}
async function telechargerCarte(){ if(carteBlob) await telechargerFichier("boussole-celeste.png", carteBlob); }
async function partagerCarte(){
  if(!carteBlob) return;
  try{
    const f = new File([carteBlob], "boussole-celeste.png", { type:"image/png" });
    await navigator.share({ files:[f], title:"Boussole céleste", text:`Mon ciel du moment. Fais le test : https://${URL_SITE}` });
  }catch(_){}
}

/* ————— Le dossier complet ————— */
/* Les leviers : la force du moment, ce qui manque peut-être, et l'excès à surveiller.
   Aucun ne se bâtit sur une énergie non mesurée (piège Boussole : « la gratitude est
   ton émotion la plus discrète (0,0/10) », un levier entier tiré d'aucune donnée). */
function leviers(notes){
  const M = triMesurees();
  const out = [];
  if(!M.length) return out;
  const pratique = (e, p) => e.dossier.pratiques[p === "apaiser" ? e.dossier.apaiser : p];
  const vars = e => ({ verbe: e.verbe, note: fmt(notes[e.id]), mesures: txtMesures(nbMesures(e.id)), ombre: e.ombre });
  const ajoute = (cle, e) => out.push({ cle, e, titre: LEVIERS[cle].titre, pourquoi: remplir(LEVIERS[cle].pourquoi, vars(e)), quoi: pratique(e, LEVIERS[cle].pratique) });
  const force = M[0];
  ajoute("force", force);
  const retrait = M[M.length - 1];
  if(M.length > 1 && notes[retrait.id] < LEVIERS.retrait.seulement_sous) ajoute("retrait", retrait);
  const ombre = M.find(e => notes[e.id] > SEUILS.ombre);
  if(ombre) ajoute("ombre", ombre);
  else if(M[1] && M[1] !== retrait && notes[M[1].id] >= LEVIERS.appui.seulement_dessus) ajoute("appui", M[1]);
  const quand = ["Cette semaine", "La semaine suivante", "Quand les deux premiers seront installés"];
  out.forEach((l, k) => { l.quand = quand[k]; });
  return out;
}
function planTrenteJours(notes){
  const M = triMesurees();
  if(!M.length) return "";
  const bloc = (titre, texte) => `<div class="rap-semaine"><b>${titre}.</b><p>${texte}</p></div>`;
  const haut = M[0], bas = M[M.length - 1];
  const v = e => ({ verbe: e.verbe, de_verbe: deVerbe(e.verbe), note: fmt(notes[e.id]), ombre: e.ombre,
                    p0: e.dossier.pratiques[0], p1: e.dossier.pratiques[1], p2: e.dossier.pratiques[2],
                    pa: e.dossier.pratiques[e.dossier.apaiser], signal: e.dossier.signal });
  let s = bloc(PLAN.s1.titre, PLAN.s1.texte);
  if(M.length > 1) s += bloc(remplir(PLAN.s2.titre, v(bas)), remplir(PLAN.s2.texte, v(bas)));
  s += notes[haut.id] > SEUILS.ombre
    ? bloc(remplir(PLAN.s3_ombre.titre, v(haut)), remplir(PLAN.s3_ombre.texte, v(haut)))
    : bloc(PLAN.s3_force.titre, remplir(PLAN.s3_force.texte, v(haut)));
  s += bloc(PLAN.s4.titre, PLAN.s4.texte);
  return s;
}
function renderRapport(notes){
  const T = tri(), M = triMesurees();
  const date = new Date().toLocaleDateString("fr-FR", { day:"numeric", month:"long", year:"numeric" });
  const ciel = cielDuMoment(notes);
  const combos = listeCombos(notes);
  const lev = leviers(notes);
  const pe = profilGroupes(notes, ELEMENTS), pm = profilGroupes(notes, MODALITES);
  const nbLev = ["", "Ton levier", "Tes deux leviers", "Tes trois leviers"][lev.length] || "Tes leviers";

  const recap = T.map(e => {
    const nm = mesuree(e.id), b = BANDES[palierDe(notes[e.id])];
    return `<div class="rap-ligne${nm ? "" : " rap-absente"}">
      ${glyphe(e.id)}<span class="nm">${maj(e.verbe)} · ${e.signe}</span>
      <span class="tr">${nm ? `<span class="fl" style="width:${notes[e.id] * 10}%; background:${VAR_ELEM(e.element)}"></span>` : ""}</span>
      <span class="bd" style="color:${nm ? b.c : "var(--faint)"}">${nm ? `${b.lbl} · ${txtMesures(nbMesures(e.id))}` : NON_MESUREE}</span>
      <span class="nt">${nm ? fmt(notes[e.id]) : "—"}</span></div>`;
  }).join("");

  const moments = (state.reelles || []).map((r, i) => {
    const nommees = Object.entries(r.emos || {}).filter(([id]) => EN[id]).sort((a, b) => b[1] - a[1]);
    if(!nommees.length) return "";
    return `<div class="rap-moment"><span class="num">Moment ${i + 1}</span>
      <div class="tags">${nommees.map(([id, v]) => `<span class="j-tag">${glyphe(id)}${maj(EN[id].verbe)} · ${esc(INTENSITES[v] ? INTENSITES[v][1].toLowerCase() : "")}</span>`).join("")}</div></div>`;
  }).filter(Boolean).join("");

  const fiches = T.map((e, i) => {
    const nm = mesuree(e.id), bd = palierDe(notes[e.id]), b = BANDES[bd], d = e.dossier;
    const exces = nm && notes[e.id] > SEUILS.ombre;
    const vigilance = `<h4>${exces ? "Quand elle prend toute la place" : "Le point de vigilance"}</h4><p>${d.vigilance} Le signal à surveiller&nbsp;: ${d.signal}.</p>`;
    return `<div class="rap-bloc rap-fiche${nm ? "" : " rap-absente"}">
      <div class="rap-entete">${vignette(e.id)}
        <div class="titres"><h3 style="margin:0">${maj(e.verbe)}</h3>
          <span class="emo-cat">${e.signe} · ${ELEMENTS[e.element].nom} · ${e.modalite} · ${e.maitre}</span></div>
        <span class="note">${nm ? fmt(notes[e.id]) : "—"}${nm ? `<span style="font-size:1rem; color:var(--faint)"> /10</span>` : ""}</span>
      </div>
      <p class="rap-rang">${nm ? `${ordinal(M.indexOf(e) + 1)} sur ${M.length} dans ton profil · ${b.lbl.toLowerCase()} · ${txtMesures(nbMesures(e.id))}` : NON_MESUREE}</p>
      <h4>Chez toi, en ce moment</h4><p>${nm ? e.paliers[bd] : "Aucune scène de ton parcours n’a mesuré cette énergie : le test n’a rien à en dire. Les pages qui suivent restent valables pour la découvrir."}</p>
      ${exces ? `<div class="rap-ombre">${vigilance}</div>` : ""}
      <h4>Ce qu’elle est</h4><p>${d.essence}</p>
      <h4>Dans le corps et dans la tête</h4><p>${d.corps_sent} ${d.corps_pense}</p>
      <h4>Trois pratiques, de la plus simple à la plus engageante</h4>
      <ol>${d.pratiques.map(x => `<li>${x}</li>`).join("")}</ol>
      ${exces ? "" : vigilance}
      <div class="rap-question"><b>À méditer</b>${e.question}</div>
    </div>`;
  }).join("");

  $("#rapportContenu").innerHTML = `
    <div class="rap-bloc rap-couv">
      <div class="logo-grand" aria-hidden="true">@@LOGO_JS@@</div>
      <h3>Ton dossier personnalisé</h3>
      <p class="date">Boussole céleste · établi le ${date}</p>
      <div class="rap-arch"><span class="etiq">Ton ciel du moment</span><p class="titre">${ciel.titre}</p><p class="phrase">${ciel.phrase}</p></div>
      <div class="roue-wrap" style="margin-top:1.4rem">${buildRoue(notes)}</div>
      <p style="max-width:30rem; margin:1.2rem auto 0">Tes énergies les plus présentes&nbsp;: <b>${M.slice(0, 3).map(e => e.verbe).join(", ")}</b>.</p>
    </div>

    <div class="rap-bloc">
      <h3>Ce que tu vas trouver ici</h3>
      <ol class="rap-somm">
        <li><b>Ton profil en un coup d’œil</b>&nbsp;: les douze énergies, classées, et tes éléments.</li>
        ${lev.length ? `<li><b>${nbLev}</b>&nbsp;: par quoi commencer, concrètement.</li>` : ""}
        ${moments ? "<li><b>Tes moments, relus</b>&nbsp;: ce que tu as noté avant le test.</li>" : ""}
        <li><b>Les douze fiches</b>&nbsp;: une par énergie, avec trois pratiques et une question de réflexion.</li>
        <li><b>Tes croisements</b>&nbsp;: ce que tes énergies racontent ensemble.</li>
        <li><b>Ton plan de trente jours</b>&nbsp;: quatre semaines, une intention chacune.</li>
        <li><b>Ta page de suivi</b>&nbsp;: à remplir dans un mois.</li>
      </ol>
      <p style="margin-top:1rem">Ton dossier comprend aussi <b>ta carte à partager</b>, au format post ou story&nbsp;: elle se fabrique sur la page de résultats.</p>
      <p style="margin-top:1rem">Prends ce dossier comme une promenade, pas comme un bulletin de notes. Chaque fiche décrit une énergie telle qu’elle vit chez toi <i>en ce moment</i>&nbsp;: tes notes bougeront avec ce que tu traverses. L’astrologie y sert de langage, pour mettre des mots sur ce que tu vis. Elle ne prédit rien.</p>
    </div>

    <div class="rap-bloc">
      <h3>Ton profil en un coup d’œil</h3>
      <div class="rap-recap">${recap}</div>
      <div class="rap-elements">${Object.entries(ELEMENTS).map(([k, g]) => `<div><b style="color:${VAR_ELEM(k)}">${pe[k] == null ? "—" : fmt(pe[k])}</b><span>${g.nom} · ${g.mode} · ${lastPart[k]}&nbsp;%</span></div>`).join("")}</div>
      <div class="rap-elements">${Object.entries(MODALITES).map(([k, g]) => `<div><b>${pm[k] == null ? "—" : fmt(pm[k])}</b><span>${maj(g.mode)}</span></div>`).join("")}</div>
    </div>

    ${lev.length ? `<div class="rap-bloc">
      <h3>${nbLev}</h3>
      <p>Trente-six pratiques t’attendent dans les fiches, mais on ne change pas tout à la fois. Voici par quoi commencer, dans cet ordre.</p>
      ${lev.map((l, i) => `<div class="rap-levier"><span class="rang">${i + 1}</span>
        <div><span class="quand">${l.quand}</span><p class="titre">${l.titre}</p><p class="quoi">${l.quoi}</p><p class="pourquoi">${l.pourquoi}</p></div></div>`).join("")}
    </div>` : ""}

    ${moments ? `<div class="rap-bloc"><h3>Tes moments, relus</h3>
      <p>Avant le test, tu as noté ${state.reelles.length} moment${state.reelles.length > 1 ? "s" : ""} vécu${state.reelles.length > 1 ? "s" : ""}. Ils ont compté dans le calcul, au même titre que les situations, et ils disent quelque chose de plus juste qu’une scène imaginée.</p>
      ${moments}
      <p style="margin-top:1rem">Relis-les dans un mois&nbsp;: ce que tu vivais ces jours-là aura peut-être déjà changé de forme.</p></div>` : ""}

    ${fiches}

    <div class="rap-bloc">
      <h3>Tes croisements décodés</h3>
      <p>Une énergie seule dit peu de chose. Ce sont leurs alliances qui dessinent une façon d’avancer.</p>
      ${combos.length ? combos.map(c => `<h4>${c.titre}</h4><p>${c.t}</p>`).join("")
        : `<p>Aucun croisement marquant&nbsp;: aucune alliance d’énergies ne domine ton profil. Tes réactions s’ajustent selon les situations, et c’est une souplesse.</p>`}
    </div>

    <div class="rap-bloc">
      <h3>Ton plan de trente jours</h3>
      <p>Quatre semaines, une intention par semaine&nbsp;: dix minutes par jour suffisent.</p>
      ${planTrenteJours(notes)}
    </div>

    <div class="rap-bloc rap-suivi">
      <h3>${SUIVI.titre}</h3>
      <p>${SUIVI.intro}</p>
      <div class="rap-champ"><b>Date du premier test</b><span>${date}</span></div>
      <div class="rap-champ"><b>Date du nouveau test</b><span class="vide"></span></div>
      <table><thead><tr><th>Énergie</th><th>Aujourd’hui</th><th>À J30</th></tr></thead><tbody>
        ${T.map(e => `<tr><td>${maj(e.verbe)} · ${e.signe}</td><td>${mesuree(e.id) ? fmt(notes[e.id]) : "—"}</td><td></td></tr>`).join("")}
      </tbody></table>
      ${SUIVI.questions.map(q => `<div class="rap-champ"><b>${q}</b><span class="vide grand"></span></div>`).join("")}
    </div>

    <div class="rap-bloc">
      <h3>Pour finir</h3>
      <p>Ce dossier a été préparé dans ton navigateur, à partir de tes seules réponses&nbsp;: rien n’a été enregistré ni transmis. Il ne prédit rien, ne pose aucun diagnostic et ne remplace aucun professionnel. ${DOUCE}</p>
    </div>`;
}
function ouvrirRapport(){
  if(!lastNotes) return;
  if(paywallActif() && niveauAcces !== "dossier") return;
  renderRapport(lastNotes);
  showView("v-rapport");
}

/* ————— Le paiement ————— */
/* Un <a> privé de son href n'est plus focusable : il devient un bouton à part entière. */
function enBouton(a){
  a.removeAttribute("href");
  a.setAttribute("role", "button");
  a.setAttribute("tabindex", "0");
  a.onkeydown = e => { if(e.key !== "Enter" && e.key !== " ") return; e.preventDefault(); a.click(); };
}
function enLien(a, href){ a.href = href; a.removeAttribute("role"); a.removeAttribute("tabindex"); a.onkeydown = null; }
/* Une seule case accepte les conditions de vente ET vaut renonciation au droit de
   rétractation. Tant qu'elle n'est pas cochée, aucun bouton ne mène au paiement — sur
   les deux parcours : la fenêtre de fin et l'encart du dossier. */
function armerPaiement(a, href, caseCgv, sansLien){
  const coche = !!(caseCgv && caseCgv.checked);
  a.classList.toggle("paiement-inactif", !coche);
  a.setAttribute("aria-disabled", coche ? "false" : "true");
  if(coche && href){ enLien(a, href); a.onclick = null; return; }
  enBouton(a);
  a.onclick = e => {
    e.preventDefault();
    if(!caseCgv || !caseCgv.checked){ signalerCgv(caseCgv); return; }
    if(sansLien) sansLien();
  };
}
function signalerCgv(caseCgv){
  if(!caseCgv) return;
  const boite = caseCgv.closest(".cgv-case");
  boite.classList.remove("a-cocher"); void boite.offsetWidth;
  boite.classList.add("a-cocher");
  boite.scrollIntoView({ block:"nearest", behavior:"smooth" });
  caseCgv.focus({ preventScroll:true });
}

/* Groupes de boutons radio : un seul arrêt de tabulation par groupe, les flèches pour
   circuler. */
function normaliserRadios(racine){
  (racine.matches && racine.matches('[role="radiogroup"]') ? [racine] : [...racine.querySelectorAll('[role="radiogroup"]')]).forEach(g => {
    const radios = [...g.querySelectorAll('[role="radio"]')];
    if(!radios.length) return;
    const actif = radios.find(r => r.getAttribute("aria-checked") === "true") || radios[0];
    radios.forEach(r => r.tabIndex = r === actif ? 0 : -1);
  });
}
document.addEventListener("keydown", e => {
  const r = e.target.closest && e.target.closest('[role="radio"]');
  if(!r) return;
  const g = r.closest('[role="radiogroup"]');
  if(!g) return;
  const radios = [...g.querySelectorAll('[role="radio"]')];
  const i = radios.indexOf(r);
  let j = null;
  if(e.key === "ArrowRight" || e.key === "ArrowDown") j = (i + 1) % radios.length;
  else if(e.key === "ArrowLeft" || e.key === "ArrowUp") j = (i - 1 + radios.length) % radios.length;
  else if(e.key === "Home") j = 0;
  else if(e.key === "End") j = radios.length - 1;
  if(j === null) return;
  e.preventDefault();
  const ident = g.getAttribute("aria-labelledby") || g.getAttribute("aria-label");
  radios[j].focus();
  radios[j].click();
  requestAnimationFrame(() => {
    if(document.activeElement && document.activeElement.closest('[role="radio"]')) return;
    const gg = document.querySelector(`[role="radiogroup"][aria-labelledby="${CSS.escape(ident || "")}"], [role="radiogroup"][aria-label="${CSS.escape(ident || "")}"]`);
    const rr = gg && gg.querySelectorAll('[role="radio"]')[j];
    if(rr){ rr.tabIndex = 0; rr.focus(); }
  });
});
new MutationObserver(m => m.forEach(x => x.addedNodes.forEach(n => { if(n.nodeType === 1) normaliserRadios(n); })))
  .observe(document.body, { childList: true, subtree: true });

const prixDossierAffiche = () => VENTE.prixDossierRef ? `${VENTE.prixDossier} <s>${VENTE.prixDossierRef}</s>` : VENTE.prixDossier;
const badgeDossier = () => VENTE.remiseDossier ? `Offre de lancement · ${VENTE.remiseDossier}` : "Tarif de lancement";

function ouvrirPaywall(){
  mesurer("paywall");
  $("#paywallGlyphs").innerHTML = triMesurees().slice(0, 3).map(e => vignette(e.id)).join("");
  const aR = $("#btnPayerResultats"), aD = $("#btnPayerDossier");
  $("#pwPrixResultats").textContent = VENTE.prixResultats;
  $("#pwPrixDossier").innerHTML = prixDossierAffiche();
  $("#pwBadgeDossier").textContent = badgeDossier();
  const caseCgv = $("#pwCgv");
  caseCgv.checked = false;   /* jamais pré-cochée, même à la réouverture */
  $("#pwCgvBox").classList.remove("a-cocher");
  const liens = !!(VENTE.lienResultats && VENTE.lienDossier);
  const armer = () => {
    armerPaiement(aR, liens ? lienAvecSuivi(VENTE.lienResultats) : "", caseCgv, () => appliquerAcces("resultats"));
    armerPaiement(aD, liens ? lienAvecSuivi(VENTE.lienDossier) : "", caseCgv, () => appliquerAcces("dossier"));
  };
  caseCgv.onchange = armer;
  const caseAppli = $("#pwAppli");
  caseAppli.checked = false;   /* un consentement ne se pré-coche pas */
  noterAppli(false);
  caseAppli.onchange = () => { noterAppli(caseAppli.checked); armer(); majVenteBox(); };
  armer();
  $("#skipZone").hidden = !VENTE.modeTest;
  $("#btnPaywallCadeau").hidden = $("#pwCadeauSep").hidden = !cadeauActif();
  $("#paywallOverlay").hidden = false;
  $("#paywallTitre").focus();
}
function appliquerAcces(niveau){
  niveauAcces = niveau;
  paywallEnAttente = false;
  effacerBrouillon();   /* les résultats s'ouvrent : le brouillon a fait son office */
  $("#paywallOverlay").hidden = true;
  $("#rapportOverlay").hidden = true;
  majCarteBox();
  if(!lastNotes) return;
  renderResults(lastNotes);
  showView("v-resultats");
}
/* La carte appartient au dossier, et à lui seul — mais reste ouverte à tous le jour où
   la vente s'arrête. */
const carteOuverte = (sousPaywall, niveau) => !sousPaywall || niveau === "dossier";
const carteAutorisee = () => carteOuverte(paywallActif(), niveauAcces);
function majCarteBox(){
  const ouverte = carteAutorisee();
  $("#btnCarte").hidden = !ouverte;
  $("#cartePromo").hidden = ouverte || !paywallActif();
  if(!ouverte) fermerCarte();
}
function fermerCarte(){
  const etaitOuverte = !$("#carteOverlay").hidden;
  $("#carteOverlay").hidden = true;
  carteBlob = null;
  $("#carteImg").removeAttribute("src");
  const btn = $("#btnCarte");
  if(etaitOuverte && btn && !btn.hidden) btn.focus();
}
function majVenteBox(){
  majCadeauBox();
  majCarteBox();
  const box = $("#venteBox"), a = $("#btnAcheter");
  const badge = $("#venteBadge"), note = $("#venteComplement");
  const complement = niveauAcces === "resultats" && !!VENTE.lienComplement;
  note.hidden = !complement;
  badge.hidden = complement;
  if(complement) $("#ventePrix").innerHTML = VENTE.prixComplement;
  else{ $("#ventePrix").innerHTML = prixDossierAffiche(); badge.textContent = badgeDossier(); }
  a.onclick = null;
  $("#venteCgvBox").hidden = niveauAcces === "dossier" || !paywallActif();
  a.classList.remove("paiement-inactif"); a.removeAttribute("aria-disabled");
  if(niveauAcces === "dossier"){
    box.hidden = false;
    enBouton(a);
    a.innerHTML = 'Ouvrir mon dossier <span class="ico" aria-hidden="true">→</span>';
    a.onclick = e => { e.preventDefault(); ouvrirRapport(); };
  }else if(paywallActif()){
    box.hidden = false;
    a.innerHTML = complement ? 'Compléter mon accès <span class="ico" aria-hidden="true">→</span>' : 'Obtenir mon dossier <span class="ico" aria-hidden="true">→</span>';
    const lien = complement ? VENTE.lienComplement : VENTE.lienDossier;
    armerPaiement(a, lien ? lienAvecSuivi(lien, complement) : "", $("#venteCgv"), () => appliquerAcces("dossier"));
  }else box.hidden = true;
}

const REF_ACHAT = /^cs_(live|test)_[A-Za-z0-9]{10,}$/;
async function validerCle(){
  const saisi = $("#cleLicence").value.trim();
  const st = $("#cleStatut");
  if(!saisi){ st.textContent = "Colle d’abord ta référence d’achat, ou le code qu’on t’a offert."; return; }
  if(decoderNotes(saisi)){ st.textContent = "Ce code-là sert à comparer ton profil avec celui d’un proche : il se colle plus bas, dans « Comparer avec un proche »."; return; }
  const codeCadeau = normaliserCadeau(saisi);
  if(codeCadeau) return validerCadeau(codeCadeau, st);
  if(!REF_ACHAT.test(saisi)){
    st.textContent = "Cette référence n’est pas reconnue. Elle commence par « cs_ » et figure sur la page affichée après ton paiement"
      + (cadeauActif() ? " ; un code cadeau ressemble à BC-XXXX-XXXX." : ".");
    return;
  }
  st.textContent = "Vérification…";
  const niveau = await verifierAchat(saisi);
  if(niveau === "indisponible"){ st.textContent = `La vérification est momentanément indisponible : ta référence n’est pas en cause. Réessaie dans un moment, ou écris à contact@${URL_SITE}.`; return; }
  if(!niveau){ st.textContent = `Cette référence n’a pas été reconnue comme un paiement valide. Vérifie que tu as collé celle affichée après ton paiement, ou écris à contact@${URL_SITE}.`; return; }
  enregistrerAcces(niveau, saisi);
  if(!lastNotes){ niveauAcces = niveau; st.textContent = "Accès validé. Tes réponses ne sont plus là : refais le test, et tes résultats s’ouvriront directement à la fin."; return; }
  st.textContent = "";
  appliquerAcces(niveau);
  if(niveau === "dossier") ouvrirRapport();
}
/* Renvoie le niveau réellement acheté, ou null. Sans Worker, on échoue franchement
   (piège Boussole : n'importe quelle chaîne au bon format ouvrait le dossier). */
async function verifierAchat(ref){
  if(!VENTE.verification) return "indisponible";
  try{
    const r = await fetch(VENTE.verification + "?session_id=" + encodeURIComponent(ref));
    if(!r.ok) return r.status >= 500 ? "indisponible" : null;
    const d = await r.json();
    if(!d || !d.valide) return null;
    return d.niveau === "dossier" ? "dossier" : d.niveau === "resultats" ? "resultats" : null;
  }catch(_){ return "indisponible"; }
}
const ACCES_KEY = PREFIXE + ".acces.v1";
function enregistrerAcces(niveau, session, cadeau){
  try{ localStorage.setItem(ACCES_KEY, JSON.stringify({ niveau, session, cadeau: cadeau || "", d: new Date().toISOString() })); }catch(_){}
}
function lireAccesComplet(){
  try{ const a = JSON.parse(localStorage.getItem(ACCES_KEY) || "null"); return a && (a.niveau === "dossier" || a.niveau === "resultats") ? a : null; }
  catch(_){ return null; }
}
const lireAcces = () => { const a = lireAccesComplet(); return a ? a.niveau : null; };
const sessionAchat = () => { const a = lireAccesComplet(); return a && a.niveau === "dossier" && REF_ACHAT.test(a.session || "") ? a.session : ""; };

/* ————— Le code à offrir —————
   Tout se décide sur le serveur : ce qui suit n'est qu'une fenêtre sur sa décision. */
const CADEAU_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";   /* ni O ni 0, ni I ni 1 */
function normaliserCadeau(brut){
  const brutMaj = String(brut || "").trim().toUpperCase();
  /* Le code de comparaison commence lui aussi par BC : sans cette garde, un BC1- dont
     les tirets s'effacent au nettoyage prendrait la forme d'un code cadeau. */
  if(/^BC\d-/.test(brutMaj)) return "";
  const s = brutMaj.replace(/[^A-Z0-9]/g, "");
  const c = s.startsWith("BC") ? s.slice(2) : s;
  if(!new RegExp(`^[${CADEAU_ALPHABET}]{8}$`).test(c)) return "";
  return `BC-${c.slice(0,4)}-${c.slice(4)}`;
}
function echeanceCadeau(iso){
  const t = Date.parse(iso);
  if(!isFinite(t)) return "";
  const minutes = Math.round((t - Date.now()) / 60000);
  if(minutes <= 0) return "Ce code a passé ses vingt-quatre heures.";
  const h = Math.floor(minutes / 60), m = minutes % 60;
  const reste = h >= 1 ? `${h} h` + (m ? ` ${m} min` : "") : `${m} min`;
  const d = new Date(t);
  const jour = new Intl.DateTimeFormat("fr-FR", { weekday:"long" }).format(d);
  const heure = d.getMinutes() ? `${d.getHours()} h ${String(d.getMinutes()).padStart(2, "0")}` : `${d.getHours()} h`;
  return `Valable encore ${reste}, jusqu’à ${jour} ${heure}.`;
}
/* Un achat n'ouvre qu'un code : le premier clic dit ce qui va se passer, le second le fait. */
let cadeauConfirme = false;
async function demanderCadeau(){
  const info = $("#cadeauInfo"), bouton = $("#btnCreerCadeau");
  const session = sessionAchat();
  if(!session){ info.textContent = `Ta référence d’achat n’est pas retrouvée sur cet appareil. Écris à contact@${URL_SITE} avec ta référence, et le code sera créé à la main.`; return; }
  if(!cadeauConfirme){
    cadeauConfirme = true;
    bouton.innerHTML = 'Oui, créer mon code <span class="ico" aria-hidden="true">✦</span>';
    info.textContent = "Un seul code par achat, et il n’est pas réédité : ses vingt-quatre heures partent à sa création.";
    return;
  }
  bouton.disabled = true;
  info.textContent = "Création…";
  let d;
  try{
    const r = await fetch(VENTE.cadeau, { method:"POST", body: JSON.stringify({ session_id: session }) });
    d = await r.json();
  }catch(_){ bouton.disabled = false; info.textContent = "La création est momentanément indisponible : réessaie dans un moment."; return; }
  bouton.disabled = false;
  if(!d || !d.code){
    info.textContent = d && d.erreur === "réservé au dossier complet" ? "Ce geste est réservé au dossier complet."
      : `La création est momentanément indisponible : réessaie dans un moment, ou écris à contact@${URL_SITE}.`;
    return;
  }
  afficherCadeau(d);
}
const CADEAU_KEY = PREFIXE + ".cadeau.v1";
function afficherCadeau(d){
  try{ localStorage.setItem(CADEAU_KEY, "1"); }catch(_){}
  $("#cadeauCode").textContent = d.code;
  $("#cadeauResultat").hidden = false;
  $("#btnCreerCadeau").hidden = true;
  if(d.utilise || d.expire){
    $("#cadeauDelai").textContent = d.utilise ? "Ce code a servi : quelqu’un a découvert ses résultats grâce à toi." : "Ce code a passé ses vingt-quatre heures sans servir.";
    $("#btnCopierCadeau").hidden = true;
    $("#cadeauInfo").textContent = "";
    return;
  }
  $("#cadeauDelai").textContent = echeanceCadeau(d.expire_le);
  $("#btnCopierCadeau").hidden = false;
  $("#cadeauInfo").textContent = "";
  $("#btnCopierCadeau").onclick = async () => {
    const message = `Je t’offre Boussole céleste : seize situations du quotidien, et les douze énergies qu’elles mettent en jeu chez toi.\n\n`
                  + `Ton code : ${d.code}\n\nLe test est ici : https://${URL_SITE}\n`
                  + `À la fin, clique sur « On m’a offert un code » et colle celui-ci : tes résultats s’ouvriront.\n`
                  + `Il sert une fois, et il est valable vingt-quatre heures.`;
    $("#cadeauInfo").textContent = await copierTexte(message) ? "Message copié : il n’y a plus qu’à l’envoyer." : "Copie impossible : sélectionne le code ci-dessus et copie-le.";
  };
}
function majCadeauBox(){
  const box = $("#cadeauBox");
  box.hidden = !(cadeauActif() && niveauAcces === "dossier" && sessionAchat());
  if(box.hidden) return;
  let dejaCree = false;
  try{ dejaCree = localStorage.getItem(CADEAU_KEY) === "1"; }catch(_){}
  if(dejaCree && !cadeauConfirme){
    cadeauConfirme = true;
    $("#btnCreerCadeau").innerHTML = 'Revoir mon code <span class="ico" aria-hidden="true">✦</span>';
  }
}
async function validerCadeau(code, st){
  /* Avant le serveur, jamais après : le code se consomme à la première présentation. */
  if(niveauAcces === "dossier" || lireAcces() === "dossier"){
    st.textContent = "Tu as déjà le dossier complet sur cet appareil, et il comprend tout ce que ce code ouvre. Garde-le pour quelqu’un d’autre : il n’a pas été utilisé.";
    return;
  }
  if(!cadeauActif()){ st.textContent = "Les codes cadeaux ne sont pas encore en service."; return; }
  st.textContent = "Vérification…";
  let d;
  try{
    const r = await fetch(VENTE.cadeau + "/utiliser", { method:"POST", body: JSON.stringify({ code }) });
    d = await r.json();
  }catch(_){ st.textContent = "La vérification est momentanément indisponible : ton code n’est pas en cause. Réessaie dans un moment."; return; }
  if(!d || !d.valide){
    const raison = d && d.raison;
    st.textContent = raison === "utilise" ? "Ce code a déjà servi : il ne s’ouvre qu’une fois."
      : raison === "expire" ? "Ce code a passé ses vingt-quatre heures."
      : raison === "inconnu" ? "Ce code n’est pas reconnu. Vérifie que tu l’as recopié en entier : il ressemble à BC-XXXX-XXXX."
      : `La vérification est momentanément indisponible : réessaie dans un moment, ou écris à contact@${URL_SITE}.`;
    return;
  }
  enregistrerAcces("resultats", "", code);
  if(!lastNotes){ niveauAcces = "resultats"; st.textContent = "Code accepté. Fais le test : tes résultats s’ouvriront directement à la fin."; return; }
  st.textContent = "";
  appliquerAcces("resultats");
}

/* ————— « Préviens-moi quand l'application sort » —————
   Le souhait voyage avec le paiement (client_reference_id=appli-oui), et rien d'autre. */
const APPLI_KEY = PREFIXE + ".appli.v1";
const REF_APPLI = "appli-oui";
const veutAppli = () => { try{ return localStorage.getItem(APPLI_KEY) === "1"; }catch(_){ return false; } };
const noterAppli = oui => { try{ oui ? localStorage.setItem(APPLI_KEY, "1") : localStorage.removeItem(APPLI_KEY); }catch(_){} };
function lienAvecSuivi(url, complement){
  const marques = [];
  if(veutAppli()) marques.push(REF_APPLI);
  if(complement){ const ref = (lireAccesComplet() || {}).session || ""; if(REF_ACHAT.test(ref)) marques.push("de:" + ref); }
  if(!url || !marques.length) return url;
  try{ const u = new URL(url); u.searchParams.set("client_reference_id", marques.join("+")); return u.toString(); }
  catch(_){ return url + (url.includes("?") ? "&" : "?") + "client_reference_id=" + encodeURIComponent(marques.join("+")); }
}

/* ————— Le brouillon du test (reprise après fermeture de l'onglet, sept jours) ————— */
const BROUILLON_KEY = PREFIXE + ".brouillon.v1";
const BROUILLON_VERSION = 1;   /* à incrémenter dès que SITUATIONS ou ROTATIONS bouge */
function sauverBrouillon(){
  try{
    localStorage.setItem(BROUILLON_KEY, JSON.stringify({ v: BROUILLON_VERSION, d: new Date().toISOString(),
      i: state.i, answers: state.answers, reelles: state.reelles, selection: state.selection }));
  }catch(_){}
}
function chargerBrouillon(){
  try{
    const b = JSON.parse(localStorage.getItem(BROUILLON_KEY) || "null");
    if(!b || b.v !== BROUILLON_VERSION || !Array.isArray(b.answers) || !Array.isArray(b.selection) || !b.selection.length) return null;
    if(b.answers.length !== N || !b.selection.every(k => SITUATIONS[k])) return null;
    if(Date.now() - new Date(b.d).getTime() > 7 * 864e5) return null;
    const faites = b.selection.filter(k => SITUATIONS[k].reac.every(([id]) => b.answers[k] && b.answers[k][id] != null)).length;
    if(faites === 0) return null;
    /* Un brouillon terminé est gardé : c'est celui de la personne partie payer. */
    return { ...b, faites, complet: faites >= b.selection.length };
  }catch(_){ return null; }
}
const effacerBrouillon = () => { try{ localStorage.removeItem(BROUILLON_KEY); }catch(_){} };
function reprendreBrouillon(b){
  state.answers = b.answers;
  state.reelles = (b.reelles || []).filter(r => r && r.emos && typeof r.emos === "object");
  state.selection = b.selection;
  state.i = Math.min(b.i || 0, b.selection.length - 1);
  renderQuestion();
  showView("v-test");
}
function majBandeauReprise(){
  const b = chargerBrouillon();
  const box = $("#repriseBox");
  if(!b){ box.hidden = true; return; }
  box.hidden = false;
  if(b.complet){
    $("#repriseTexte").innerHTML = `<strong>Ton test est terminé.</strong> Les ${b.selection.length} situations sont remplies : tes résultats t’attendent, sans avoir à recommencer.`;
    $("#btnReprendre").innerHTML = 'Voir mes résultats <span class="ico" aria-hidden="true">→</span>';
    $("#btnReprendre").onclick = () => { reprendreBrouillon(b); finish(); };
  }else{
    $("#repriseTexte").innerHTML = `<strong>Tu avais commencé un test.</strong> ${b.faites} situation${b.faites > 1 ? "s" : ""} sur ${b.selection.length} déjà remplie${b.faites > 1 ? "s" : ""} : tu peux reprendre là où tu t’étais arrêté·e.`;
    $("#btnReprendre").innerHTML = 'Reprendre mon test <span class="ico" aria-hidden="true">→</span>';
    $("#btnReprendre").onclick = () => reprendreBrouillon(b);
  }
  $("#btnAbandonner").onclick = () => { effacerBrouillon(); majBandeauReprise(); };
}

/* ————— Le journal (sur l'appareil, jamais envoyé) ————— */
function chargerJournal(){
  try{
    const brut = localStorage.getItem(JOURNAL_KEY);
    const j = brut ? JSON.parse(brut) : { entrees: [] };
    if(!Array.isArray(j.entrees)) j.entrees = [];
    return j;
  }catch(_){ return null; }   /* stockage indisponible : navigation privée, réglage… */
}
function sauverJournal(j){ try{ localStorage.setItem(JOURNAL_KEY, JSON.stringify(j)); return true; }catch(_){ return false; } }
function dateEntree(iso){
  const d = new Date(iso), auj = new Date();
  const hier = new Date(auj); hier.setDate(auj.getDate() - 1);
  const meme = (a, b) => a.toDateString() === b.toDateString();
  const h = d.toLocaleTimeString("fr-FR", { hour:"2-digit", minute:"2-digit" });
  if(meme(d, auj)) return `Aujourd’hui · ${h}`;
  if(meme(d, hier)) return `Hier · ${h}`;
  return d.toLocaleDateString("fr-FR", { weekday:"long", day:"numeric", month:"long" }) + " · " + h;
}
function serieJours(entrees){
  const jours = new Set(entrees.map(e => new Date(e.d).toDateString()));
  let n = 0; const c = new Date();
  if(!jours.has(c.toDateString())) c.setDate(c.getDate() - 1);
  while(jours.has(c.toDateString())){ n++; c.setDate(c.getDate() - 1); }
  return n;
}
/* Les motifs, à partir de dix entrées sur quatre-vingt-dix jours. */
function motifsJournal(entrees){
  const ph = [];
  const rec = entrees.filter(e => new Date(e.d).getTime() >= Date.now() - 90 * 864e5);
  if(rec.length < 10) return ph;
  const freq = {};
  rec.forEach(e => Object.keys(e.emos || {}).forEach(id => { if(EN[id]) freq[id] = (freq[id] || 0) + 1; }));
  const parFreq = Object.keys(freq).sort((a, b) => freq[b] - freq[a]);
  const top = (o) => Object.keys(o).sort((a, b) => o[b] - o[a])[0];
  const ctxDominant = id => {
    const avec = rec.filter(e => (e.emos || {})[id] != null);
    const n = {}; avec.forEach(e => (e.ctx || []).forEach(c => { n[c] = (n[c] || 0) + 1; }));
    const t = top(n);
    return t && n[t] >= 3 && n[t] / avec.length >= .5 ? { c: t, p: Math.round(n[t] / avec.length * 100) } : null;
  };
  const t1 = parFreq[0], t2 = parFreq[1];
  if(t1){
    const avec = rec.filter(e => (e.emos || {})[t1] != null);
    const c = ctxDominant(t1);
    if(c) ph.push(`${maj(nomEnergie(t1))} revient surtout en contexte « ${esc(c.c)} » (${c.p} % de ses apparitions).`);
    const jN = {}; avec.forEach(e => { const j = JOURS_FR[new Date(e.d).getDay()]; jN[j] = (jN[j] || 0) + 1; });
    const jt = top(jN);
    if(jt && jN[jt] >= 3 && jN[jt] / avec.length >= .4) ph.push(`${maj(nomEnergie(t1))} revient souvent le ${jt} : un motif à observer.`);
    const coupe = Date.now() - 14 * 864e5;
    const moy = l => l.length ? l.reduce((t, e) => t + ((e.emos || {})[t1] || 0), 0) / l.length : null;
    const m1 = moy(avec.filter(e => new Date(e.d).getTime() >= coupe));
    const m0 = moy(avec.filter(e => { const t = new Date(e.d).getTime(); return t < coupe && t >= Date.now() - 28 * 864e5; }));
    if(m1 != null && m0 != null && Math.abs(m1 - m0) >= .7) ph.push(`Sur les deux dernières semaines, la force de ${nomEnergie(t1)} est en ${m1 > m0 ? "hausse" : "baisse"} par rapport aux deux précédentes.`);
    const avecSens = avec.filter(e => (e.sens || []).length);
    const sN = {}; avecSens.forEach(e => e.sens.forEach(s => { sN[s] = (sN[s] || 0) + 1; }));
    const st = top(sN);
    if(st && sN[st] >= 3 && sN[st] / avecSens.length >= .5) ph.push(`Ton corps accompagne souvent ${nomEnergie(t1)} par « ${esc(st.toLowerCase())} » : présent dans ${Math.round(sN[st] / avecSens.length * 100)} % de ces moments.`);
    const eN = {}; avec.forEach(e => { if(e.elan) eN[e.elan] = (eN[e.elan] || 0) + 1; });
    const et = top(eN);
    if(et && eN[et] >= 3 && eN[et] / avec.length >= .5) ph.push(`Quand ${nomEnergie(t1)} est là, ton premier élan est le plus souvent « ${esc(et.toLowerCase())} ».`);
    const iN = {}; avec.forEach(e => (e.imp || []).forEach(c => { iN[c] = (iN[c] || 0) + 1; }));
    const it = top(iN);
    if(it && iN[it] >= 3 && iN[it] / avec.length >= .5) ph.push(`Derrière ${nomEnergie(t1)}, ce qui compte le plus souvent : « ${esc(it)} ».`);
  }
  if(t2){
    const c = ctxDominant(t2);
    if(c) ph.push(`${maj(nomEnergie(t2))}, elle, se montre surtout en contexte « ${esc(c.c)} ».`);
  }
  const avecConf = entrees.filter(e => e.conf);
  if(avecConf.length >= 10){
    const moitie = Math.floor(avecConf.length / 2);
    const taux = l => l.filter(e => e.conf === 1).length / l.length;
    if(taux(avecConf.slice(0, moitie)) - taux(avecConf.slice(moitie)) >= .2) ph.push("Tu hésites de moins en moins sur tes choix : ta lecture de toi-même s’affine, entrée après entrée.");
  }
  return ph.slice(0, 6);
}
function renderJournalBlocs(){
  const j = chargerJournal();
  $("#jMotifs").innerHTML = ""; $("#jHistorique").innerHTML = "";
  const dispo = j !== null;
  $("#jActions").hidden = !dispo || !j.entrees.length;
  if(!dispo || !j.entrees.length) return;
  const E = j.entrees;
  const serie = serieJours(E);
  const motifs = [...motifsJournal(E), ...motifsTestJournal(E)].slice(0, 7);
  const t = chargerTests();
  const infoTest = t && t.passages.length ? (() => {
    const d = t.passages[t.passages.length - 1];
    const doms = [...ENERGIES].filter(e => !d.mesures || d.mesures[e.id] > 0).sort((a, b) => (d.notes[b.id] || 0) - (d.notes[a.id] || 0)).slice(0, 3).map(e => e.verbe).join(", ");
    return `<p style="font-size:.82rem; color:var(--faint); margin:-.3rem 0 .9rem">Dernier test gardé : ${new Date(d.d).toLocaleDateString("fr-FR")} · les plus présentes : ${doms}.</p>`;
  })() : "";
  const rec = E.filter(e => new Date(e.d).getTime() >= Date.now() - 30 * 864e5);
  const freq = {};
  rec.forEach(e => Object.keys(e.emos || {}).forEach(id => { if(EN[id]) freq[id] = (freq[id] || 0) + 1; }));
  const top5 = Object.keys(freq).sort((a, b) => freq[b] - freq[a]).slice(0, 5);
  $("#jMotifs").innerHTML = `<div class="j-bloc">
    <h3>Tes motifs</h3>${infoTest}
    <div class="j-stats">
      <div class="j-stat"><b>${E.length}</b><span>entrée${E.length > 1 ? "s" : ""}</span></div>
      <div class="j-stat"><b>${serie}</b><span>jour${serie > 1 ? "s" : ""} d’affilée</span></div>
      <div class="j-stat"><b>${rec.length}</b><span>sur 30 jours</span></div>
    </div>
    ${motifs.length ? motifs.map(m => `<p class="j-motif">${m}</p>`).join("")
      : `<p style="font-size:.9rem; color:var(--muted)">${E.length >= 10 ? "Continue : tes motifs se dessinent à mesure que les entrées s’accumulent." : `Encore ${10 - E.length} entrée${10 - E.length > 1 ? "s" : ""}, et tes premiers motifs apparaîtront ici.`}</p>`}
    ${top5.length ? `<div class="j-freq">${top5.map(id => {
      const part = Math.round(freq[id] / rec.length * 100);
      return `<div class="j-freq-row"><span>${maj(EN[id].verbe)}</span><span class="tr"><span class="fl" style="width:${part}%; background:${VAR_ELEM(EN[id].element)}"></span></span><span class="ct">${part}&nbsp;%</span></div>`;
    }).join("")}<p style="font-size:.76rem; color:var(--faint); margin-top:.3rem">Présence dans tes entrées des 30 derniers jours.</p></div>` : ""}
  </div>`;
  const lignes = [...E].sort((a, b) => new Date(b.d) - new Date(a.d)).slice(0, 60).map(e => `
    <div class="j-entree">
      <div class="j-entete"><span class="j-date">${esc(dateEntree(e.d))}</span><button class="j-suppr" data-d="${esc(e.d)}">supprimer</button></div>
      <div class="j-tags">
        ${Object.entries(e.emos || {}).map(([id, v]) => EN[id] ? `<span class="j-tag">${glyphe(id)}${maj(EN[id].verbe)}${INTENSITES[v] ? " · " + esc(INTENSITES[v][1].toLowerCase()) : ""}</span>` : "").join("")}
        ${e.corps && CORPS_NIVEAUX[e.corps - 1] ? `<span class="j-tag ctx">${esc(CORPS_NIVEAUX[e.corps - 1])}</span>` : ""}
        ${(e.sens || []).slice(0, 3).map(s => `<span class="j-tag ctx">${esc(String(s).toLowerCase())}</span>`).join("")}
        ${(e.sens || []).length > 3 ? `<span class="j-tag ctx">+${e.sens.length - 3}</span>` : ""}
        ${e.elan ? `<span class="j-tag ctx">→ ${esc(String(e.elan).toLowerCase())}</span>` : ""}
        ${(e.imp || []).map(c => `<span class="j-tag ctx">${esc(c)}</span>`).join("")}
        ${(e.ctx || []).map(c => `<span class="j-tag ctx">${esc(c)}</span>`).join("")}
      </div>
      ${e.note ? `<p class="j-txt">${esc(e.note)}</p>` : ""}
    </div>`).join("");
  $("#jHistorique").innerHTML = `<div class="j-bloc"><h3>Ton historique</h3>${lignes}
    ${E.length > 60 ? `<p style="font-size:.8rem; color:var(--faint)">${E.length - 60} entrées plus anciennes ne sont pas affichées : elles restent dans ta sauvegarde.</p>` : ""}</div>`;
  $("#jHistorique").querySelectorAll(".j-suppr").forEach(b => b.addEventListener("click", () => {
    if(!confirm("Supprimer cette entrée ?")) return;
    const jj = chargerJournal();
    jj.entrees = jj.entrees.filter(x => x.d !== b.dataset.d);
    sauverJournal(jj); renderJournalBlocs();
  }));
}
async function exporterJournal(){
  const j = chargerJournal();
  if(!j || !j.entrees.length){ $("#jFeedback2").textContent = "Rien à exporter pour l’instant."; return; }
  await telechargerFichier(`boussole-celeste-journal-${new Date().toISOString().slice(0, 10)}.json`,
    new Blob([JSON.stringify(j, null, 2)], { type:"application/json" }));
}
/* Import : validation stricte. On ne recopie que des entrées bien formées, aux valeurs
   connues ; tout le reste est ignoré (piège Boussole : un fichier trafiqué glissait du
   contenu dans la page). */
function importerJournal(fichier){
  const lecteur = new FileReader();
  lecteur.onload = () => {
    try{
      const imp = JSON.parse(lecteur.result);
      if(!imp || !Array.isArray(imp.entrees)) throw 0;
      const j = chargerJournal() || { entrees: [] };
      const vues = new Set(j.entrees.map(e => e.d));
      const texte = (v, max) => typeof v === "string" ? v.slice(0, max) : null;
      const liste = (v, ref, max) => Array.isArray(v) ? v.filter(x => ref.includes(x)).slice(0, max) : [];
      const entier = (v, min, max) => Number.isInteger(v) && v >= min && v <= max ? v : null;
      imp.entrees.forEach(e => {
        if(!e || typeof e !== "object" || typeof e.d !== "string") return;
        if(isNaN(new Date(e.d).getTime()) || vues.has(e.d)) return;
        const emos = {};
        if(e.emos && typeof e.emos === "object"){
          for(const id in e.emos){ const v = entier(e.emos[id], 1, 4); if(EN[id] && v) emos[id] = v; }
        }
        if(!Object.keys(emos).length || Object.keys(emos).length > 3) return;
        const propre = { d: new Date(e.d).toISOString(), emos, ctx: liste(e.ctx, CONTEXTES, 8), note: texte(e.note, 500) || "" };
        const corps = entier(e.corps, 1, CORPS_NIVEAUX.length); if(corps) propre.corps = corps;
        const conf = entier(e.conf, 1, CONFIANCES.length); if(conf) propre.conf = conf;
        const sens = liste(e.sens, SENSATIONS, 10); if(sens.length) propre.sens = sens;
        const imp2 = liste(e.imp, IMPORTANTS, 2); if(imp2.length) propre.imp = imp2;
        if(ELANS.includes(e.elan)) propre.elan = e.elan;
        vues.add(propre.d);
        j.entrees.push(propre);
      });
      j.entrees.sort((a, b) => new Date(a.d) - new Date(b.d));
      $("#jFeedback2").textContent = sauverJournal(j) ? "Sauvegarde importée et fusionnée." : "Import lu, mais le stockage local est indisponible ici.";
      renderJournalBlocs();
    }catch(_){ $("#jFeedback2").textContent = "Ce fichier ne ressemble pas à une sauvegarde du journal."; }
    setTimeout(() => { $("#jFeedback2").textContent = ""; }, 5000);
  };
  lecteur.readAsText(fichier);
}

/* ————— Résultats gardés sur l'appareil (au choix de la personne) ————— */
const TESTS_KEY = PREFIXE + ".tests.v1";
const BAREME = 1;   /* à incrémenter à chaque changement de SITUATIONS ou du calcul */
function chargerTests(){
  try{ const t = JSON.parse(localStorage.getItem(TESTS_KEY) || "null") || { passages: [] }; if(!Array.isArray(t.passages)) t.passages = []; return t; }
  catch(_){ return null; }
}
const sauverTests = t => { try{ localStorage.setItem(TESTS_KEY, JSON.stringify(t)); return true; }catch(_){ return false; } };
function majGardeBox(){
  const box = $("#gardeBox"), t = chargerTests();
  if(t === null || !lastNotes){ box.hidden = true; return; }
  box.hidden = false;
  const ref = resultatsGardesCe ? t.passages[t.passages.length - 2] : t.passages[t.passages.length - 1];
  const evo = $("#gardeEvo");
  if(ref && ref.bareme !== BAREME){
    evo.innerHTML = `<span class="j-tag ctx">Ton passage du ${new Date(ref.d).toLocaleDateString("fr-FR")} a été fait avec une version précédente du test : les notes ne se comparent pas.</span>`;
  }else if(ref){
    const deltas = ENERGIES.filter(e => mesuree(e.id) && (!ref.mesures || ref.mesures[e.id] > 0))
      .map(e => ({ e, delta: Math.round((lastNotes[e.id] - ref.notes[e.id]) * 10) / 10 }))
      .filter(x => Math.abs(x.delta) >= 1).sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta)).slice(0, 4);
    evo.innerHTML = `<span class="j-tag ctx">Depuis ton passage du ${new Date(ref.d).toLocaleDateString("fr-FR")} :</span>` +
      (deltas.length ? deltas.map(x => `<span class="j-tag">${maj(x.e.verbe)} ${x.delta > 0 ? "▲" : "▼"} ${fmt(Math.abs(x.delta))}</span>`).join("")
        : `<span class="j-tag ctx">aucun mouvement d’un point ou plus</span>`);
  }else evo.innerHTML = "";
  $("#btnGarder").hidden = resultatsGardesCe;
  $("#gardeTexte").innerHTML = resultatsGardesCe
    ? "<strong>Résultats gardés sur cet appareil.</strong> Ton prochain passage montrera ce qui a bougé, et ton journal pourra croiser ton test avec ton vécu."
    : "<strong>Suivre ce qui bouge&nbsp;?</strong> Garde ces résultats sur cet appareil, et seulement ici&nbsp;: au prochain passage, tu verras ce qui a changé.";
}
function garderResultats(){
  const t = chargerTests();
  if(!t || !lastNotes) return;
  t.passages.push({ d: new Date().toISOString(), bareme: BAREME, notes: { ...lastNotes }, mesures: lastMesures ? { ...lastMesures } : null });
  if(sauverTests(t)){ resultatsGardesCe = true; majGardeBox(); }
}
function motifsTestJournal(entrees){
  const t = chargerTests();
  if(!t || !t.passages.length) return [];
  const dernier = t.passages[t.passages.length - 1];
  const rec = entrees.filter(e => new Date(e.d).getTime() >= Date.now() - 90 * 864e5);
  if(rec.length < 8) return [];
  const vu = id => !dernier.mesures || dernier.mesures[id] > 0;
  const freq = {};
  rec.forEach(e => Object.keys(e.emos || {}).forEach(id => { freq[id] = (freq[id] || 0) + 1; }));
  const part = id => (freq[id] || 0) / rec.length;
  const ph = [];
  const hautes = ENERGIES.filter(e => vu(e.id) && (dernier.notes[e.id] || 0) >= SEUILS.haut).sort((a, b) => dernier.notes[b.id] - dernier.notes[a.id]).slice(0, 3);
  const conf = hautes.find(e => part(e.id) >= .4);
  if(conf) ph.push(`Ton test plaçait ${nomEnergie(conf.id)} haut (${fmt(dernier.notes[conf.id])}/10), et ton vécu le confirme : elle est présente dans ${Math.round(part(conf.id) * 100)} % de tes entrées.`);
  const topJ = Object.keys(freq).filter(id => EN[id]).sort((a, b) => freq[b] - freq[a])[0];
  if(topJ && vu(topJ) && part(topJ) >= .5 && dernier.notes[topJ] <= SEUILS.bas)
    ph.push(`Écart intéressant : ${nomEnergie(topJ)} était discrète dans ton test (${fmt(dernier.notes[topJ])}/10), mais revient dans ${Math.round(part(topJ) * 100)} % de ton vécu.`);
  const sur = hautes.find(e => part(e.id) <= .15);
  if(sur) ph.push(`À l’inverse, ${nomEnergie(sur.id)}, haute dans ton test (${fmt(dernier.notes[sur.id])}/10), apparaît peu dans ton quotidien (${Math.round(part(sur.id) * 100)} %) : la scène imaginée touche peut-être plus fort que le réel.`);
  return ph.slice(0, 2);
}

/* ————— Comparer avec un proche (sans serveur) —————
   Les douze notes, au demi-point, tiennent dans douze caractères d'un alphabet de
   21 symboles ; « - » marque une énergie non mesurée, distincte d'une note de zéro.
   Le préfixe est versionné : changer l'ordre des énergies invaliderait les codes, on
   passerait alors à BC2-. */
const ALPHABET_CODE = "0123456789ABCDEFGHIJK";
const CODE_ABSENTE = "-";
const PREFIXE_CODE = "BC1-";
function encoderNotes(notes){
  return PREFIXE_CODE + IDS.map(id => {
    if(lastMesures && lastMesures[id] === 0) return CODE_ABSENTE;
    return ALPHABET_CODE[Math.max(0, Math.min(20, Math.round((notes[id] || 0) * 2)))];
  }).join("");
}
function decoderNotes(code){
  const c = String(code || "").trim().toUpperCase().replace(/\s+/g, "");
  if(!c.startsWith(PREFIXE_CODE)) return null;
  const corps = c.slice(PREFIXE_CODE.length);
  if(corps.length !== IDS.length) return null;
  const notes = {};
  for(let k = 0; k < IDS.length; k++){
    if(corps[k] === CODE_ABSENTE){ notes[IDS[k]] = null; continue; }
    const v = ALPHABET_CODE.indexOf(corps[k]);
    if(v < 0) return null;
    notes[IDS[k]] = v / 2;
  }
  return notes;
}
function comparerAvec(autres){
  /* On ne compare que ce que vous avez mesuré tous les deux : comparer une note à une
     absence inventerait un écart. */
  const toutes = ENERGIES.map(e => ({ e, moi: lastNotes[e.id], lui: autres[e.id], comparable: mesuree(e.id) && autres[e.id] != null }));
  const paires = toutes.filter(p => p.comparable).map(p => ({ ...p, ecart: Math.abs(p.moi - p.lui) }));
  const hors = toutes.filter(p => !p.comparable);
  if(!paires.length){
    $("#compResume").innerHTML = `<p>Aucune énergie n’a été mesurée chez vous deux : il n’y a rien à comparer.</p>`;
    $("#compTable").innerHTML = ""; $("#compResultat").hidden = false; return;
  }
  const proximite = Math.max(0, Math.round((1 - paires.reduce((t, p) => t + p.ecart, 0) / (paires.length * 10)) * 100));
  const ph = [`Sur les ${paires.length} énergie${paires.length > 1 ? "s" : ""} mesurée${paires.length > 1 ? "s" : ""} chez vous deux, vos profils se ressemblent à <b>${proximite}&nbsp;%</b>.`];
  if(hors.length) ph.push(`${hors.length} énergie${hors.length > 1 ? "s ne sont" : " n’est"} pas comparable${hors.length > 1 ? "s" : ""} : l’un de vous deux ne l’a pas mesurée.`);
  const communes = paires.filter(p => p.moi >= 5 && p.lui >= 5).sort((a, b) => (b.moi + b.lui) - (a.moi + a.lui));
  if(communes.length) ph.push(`Vous partagez ${communes.slice(0, 2).map(p => nomEnergie(p.e.id)).join(" et ")} : un terrain commun, sur lequel vous vous comprenez sans effort.`);
  const ecart = [...paires].sort((a, b) => b.ecart - a.ecart)[0];
  if(ecart && ecart.ecart >= 2) ph.push(`Votre plus grand écart porte sur ${nomEnergie(ecart.e.id)} (${fmt(ecart.moi)} contre ${fmt(ecart.lui)}) : ${ecart.moi > ecart.lui ? "elle prend plus de place chez toi" : "elle prend plus de place chez l’autre"}. C’est une différence utile à connaître entre vous.`);
  ph.push("Il n’y a pas de bon ou de mauvais profil : juste deux façons de traverser les mêmes situations.");
  $("#compResume").innerHTML = ph.map(p => `<p style="margin-bottom:.6rem">${p}</p>`).join("");
  $("#compTable").innerHTML = paires.sort((a, b) => (b.moi + b.lui) - (a.moi + a.lui)).map(p => `
    <div class="comp-row"><span class="comp-id">${glyphe(p.e.id)}<span>${maj(p.e.verbe)}</span></span>
      <span class="comp-barres"><span class="cb"><span class="cf" style="width:${p.moi * 10}%"></span></span><span class="cb"><span class="cf autre" style="width:${p.lui * 10}%"></span></span></span>
      <span class="comp-val">${fmt(p.moi)} · ${fmt(p.lui)}</span></div>`).join("")
    + hors.map(p => `<div class="comp-row rap-absente"><span class="comp-id">${glyphe(p.e.id)}<span>${maj(p.e.verbe)}</span></span><span class="comp-barres"><span class="cb"></span><span class="cb"></span></span><span class="comp-val">${NON_MESUREE.toLowerCase()}</span></div>`).join("");
  $("#compResultat").hidden = false;
}
async function copierCode(){
  const code = encoderNotes(lastNotes);
  $("#compInfo").textContent = await copierTexte(`Voici mon code Boussole céleste : ${code}\nColle-le sur https://${URL_SITE} après ton test, pour comparer nos profils.`)
    ? "Code copié. Envoie-le à la personne de ton choix." : `Ton code : ${code}`;
  setTimeout(() => { $("#compInfo").textContent = ""; }, 6000);
}
function validerCodeAmi(){
  const autres = decoderNotes($("#compCode").value);
  if(!autres){ $("#compInfo").textContent = `Ce code n’est pas reconnu : il commence par « ${PREFIXE_CODE} » et compte ${PREFIXE_CODE.length + IDS.length} caractères.`; return; }
  $("#compInfo").textContent = "";
  comparerAvec(autres);
}

/* ————— Application installable, rappel quotidien ————— */
let promptInstall = null;
window.addEventListener("beforeinstallprompt", e => { e.preventDefault(); promptInstall = e; $("#btnInstaller").hidden = false; });
async function installerApp(){
  if(!promptInstall) return;
  promptInstall.prompt();
  try{ await promptInstall.userChoice; }catch(_){}
  promptInstall = null;
  $("#btnInstaller").hidden = true;
}
function texteICS(){
  const d = new Date(), p = n => String(n).padStart(2, "0");
  const jour = `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}`;
  return ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Boussole celeste//FR", "CALSCALE:GREGORIAN",
    "BEGIN:VEVENT", `UID:celeste-${jour}@${URL_SITE}`, `DTSTAMP:${jour}T090000Z`,
    `DTSTART:${jour}T210000`, `DTEND:${jour}T210500`, "RRULE:FREQ=DAILY",
    "SUMMARY:Mon journal Boussole céleste (2 min)",
    `DESCRIPTION:Un moment de la journée à noter : https://${URL_SITE}`, `URL:https://${URL_SITE}`,
    "BEGIN:VALARM", "TRIGGER:-PT0M", "ACTION:DISPLAY", "DESCRIPTION:Ton journal Boussole céleste", "END:VALARM",
    "END:VEVENT", "END:VCALENDAR"].join("\r\n");
}
async function creerRappel(){
  await telechargerFichier("boussole-celeste-rappel.ics", new Blob([texteICS()], { type:"text/calendar" }));
  $("#rappelNote").textContent = "Fichier téléchargé : ouvre-le pour ajouter le rappel de 21 h à ton agenda. Tu pourras changer l’heure ensuite.";
  setTimeout(() => { $("#rappelNote").textContent = ""; }, 8000);
}

/* ————— Auto-vérification (console, à chaque chargement) ————— */
function runSelfTests(){
  const sauve = { lastNotes, lastMesures, lastPart };
  const repondre = v => SITUATIONS.map(s => Object.fromEntries(s.reac.map(([id]) => [id, v])));
  const res = {};

  /* 1. Tout à 4 → 10/10, sur la banque et sur chacun des trois jeux de 16. */
  res.max = [null, ...ROTATIONS].every(sel => { const n = computeScores(repondre(4), [], sel); return IDS.every(id => n[id] === 10); });
  /* 2. Tout à « un peu » → 2,5/10. */
  res.min = [null, ...ROTATIONS].every(sel => { const n = computeScores(repondre(1), [], sel); return IDS.every(id => n[id] === 2.5); });
  /* 3. Jamais présentée → 0 mesure, et aucune phrase ne se bâtit dessus. */
  const partiel = SITUATIONS.map(() => ({ belier: 4, capricorne: 4, cancer: 1 }));
  const mesP = compterMesures(partiel, [], null);
  res.absence = mesP.lion === 0 && mesP.belier === N && computeScores(partiel, [], null).lion === 0;
  /* 4. Une seule mesure ne vaut plus 10/10 (elle reste à 4 au plus). */
  const une = SITUATIONS.map((_, k) => k === 0 ? { lion: 4, belier: 2 } : { belier: 2 });
  const nL = computeScores(une, [], null).lion;
  res.uneMesure = nL > 0 && nL <= 4 && compterMesures(une, [], null).lion === 1;
  /* 5. Répartition des éléments : la somme fait 100, et chaque élément présent compte. */
  const r = repartition(repondre(2), [], null);
  res.repartition = Object.values(r).reduce((a, b) => a + b, 0) === 100 && Object.values(r).every(x => x > 0);
  /* 6. Journal + test court : cinq moments, huit scènes, tout à 4 → 10/10 partout,
        et chaque moment compte exactement pour les énergies qu'il nomme. */
  const sel8 = ROTATIONS[0].slice(0, PLANCHER_TEST);
  const reelles = Array.from({length:5}, () => ({ emos: Object.fromEntries(IDS.map(id => [id, 4])) }));
  const nM = computeScores(repondre(4), reelles, sel8);
  const presentes8 = id => sel8.filter(k => SITUATIONS[k].reac.some(([e]) => e === id)).length;
  const mM = compterMesures(repondre(4), reelles, sel8);
  res.journal = IDS.every(id => nM[id] === 10 && mM[id] === presentes8(id) + 5);
  /* 7. Couverture des rotations : chaque énergie au moins 5 fois par jeu, et 2 fois
        dans les 8 premières ; chaque scène dans deux jeux ; 8 nouvelles d'un jeu au suivant. */
  const couv = sel => { const c = Object.fromEntries(IDS.map(id => [id, 0])); sel.forEach(k => SITUATIONS[k].reac.forEach(([id]) => c[id]++)); return c; };
  const pres = {}; ROTATIONS.forEach(rr => rr.forEach(k => { pres[k] = (pres[k] || 0) + 1; }));
  res.rotations = ROTATIONS.every((rr, k) => new Set(rr).size === TAILLE_TEST
      && Object.values(couv(rr)).every(x => x >= COUVERTURE) && Object.values(couv(rr.slice(0, PLANCHER_TEST))).every(x => x >= 2)
      && ROTATIONS[(k + 1) % 3].filter(x => !rr.includes(x)).length === 8)
    && TOUTES.every(k => pres[k] === 2);
  /* 8. Le code cadeau, tel qu'il voyage ; et rien ne passe pour lui qui n'en est pas un. */
  res.cadeau = ["BC-K4T9-M2PX", "bc-k4t9-m2px", "BCK4T9M2PX", "k4t9 m2px", " BC K4T9-M2PX "].every(s => normaliserCadeau(s) === "BC-K4T9-M2PX")
    && ["", "BC-K4T9-M2P", "cs_test_9B68wI5BQ11M8Mg00oc7u00", "BC1-5A3B7C9D2E4F", "BC1-5-A-3-B-7-C-", "BC-IOIO-0101"].every(s => normaliserCadeau(s) === "");
  /* 9. La carte à partager : réservée au dossier, ouverte à tous si la vente s'arrête. */
  res.carte = [[true,"aucun",false],[true,"resultats",false],[true,"dossier",true],[false,"aucun",true],[false,"resultats",true],[false,"dossier",true]]
    .every(([p, n, att]) => carteOuverte(p, n) === att);
  /* 10. Le signe de naissance, jours limites compris. */
  const eq = (a, b) => a.length === b.length && a.every((x, k) => x === b[k]);
  res.signe = eq(candidatsSigne(15, 4), ["belier"]) && eq(candidatsSigne(21, 3), ["poissons", "belier"])
    && eq(candidatsSigne(20, 3), ["poissons", "belier"]) && eq(candidatsSigne(1, 1), ["capricorne"])
    && eq(candidatsSigne(31, 12), ["capricorne"]) && eq(candidatsSigne(22, 12), ["sagittaire", "capricorne"])
    && eq(candidatsSigne(29, 2), ["poissons"]) && candidatsSigne(30, 2).length === 0 && candidatsSigne(0, 5).length === 0
    && [[1,1],[15,2],[10,5],[15,8],[30,11]].every(([j, m]) => candidatsSigne(j, m).length === 1);
  /* 11. Le code de comparaison fait l'aller-retour, absences comprises. */
  lastMesures = Object.fromEntries(IDS.map((id, k) => [id, k === 3 ? 0 : 5]));
  const notesT = Object.fromEntries(IDS.map((id, k) => [id, k * .5 + 1]));
  const dec = decoderNotes(encoderNotes(notesT));
  res.code = !!dec && IDS.every((id, k) => k === 3 ? dec[id] === null : dec[id] === notesT[id]) && encoderNotes(notesT).length === PREFIXE_CODE.length + 12;
  /* 12. Aucune phrase sur une énergie non mesurée : une paire haute dont l'une n'est pas
         mesurée ne déclenche rien, et ni le ciel, ni les leviers ne la citent. */
  lastMesures = Object.fromEntries(IDS.map(id => [id, id === "capricorne" ? 0 : 6]));
  const notesU = Object.fromEntries(IDS.map(id => [id, id === "belier" || id === "capricorne" ? 9 : 3]));
  lastNotes = notesU;
  const combosU = listeCombos(notesU);
  const levU = leviers(notesU);
  const cielU = cielDuMoment(notesU);
  res.nonMesuree = !combosU.some(c => /bâtir/.test(c.t)) && !levU.some(l => l.e.id === "capricorne")
    && !/bâtir/.test(cielU.phrase) && levU[0].e.id === "belier";
  /* 13. Les paliers. */
  res.paliers = palierDe(3.4) === "discrete" && palierDe(3.5) === "presente" && palierDe(7) === "presente" && palierDe(7.1) === "dominante";
  /* 14. Le ciel du moment répond à toutes les paires d'éléments. */
  const els = Object.keys(ELEMENTS);
  res.ciels = els.every(a => els.every(b => CIELS.some(c => (c.elements[0] === a && c.elements[1] === b) || (c.elements[0] === b && c.elements[1] === a))));
  /* 15. Le mot interdit n'apparaît nulle part sur la page : le test, les résultats et le
         dossier ne sont jamais présentés comme offerts. */
  const page = document.body.cloneNode(true);
  page.querySelectorAll("script, style").forEach(n => n.remove());
  res.motInterdit = !new RegExp("gra" + "tuit", "i").test(page.textContent);

  ({ lastNotes, lastMesures, lastPart } = sauve);
  const ok = Object.values(res).every(Boolean);
  const lib = { max:"tout à 4 → 10/10", min:"tout à 1 → 2,5/10", absence:"jamais présentée → 0 mesure", uneMesure:"une seule mesure ne vaut plus 10/10",
    repartition:"répartition = 100 %", journal:"journal + test court", rotations:"couverture des rotations", cadeau:"code cadeau lu et refusé comme il faut",
    carte:"carte réservée au dossier", signe:"signe de naissance et jours limites", code:"code de comparaison", nonMesuree:"aucune phrase sur une énergie non mesurée",
    paliers:"paliers", ciels:"un ciel pour chaque paire d’éléments", motInterdit:"aucun mot interdit" };
  console.info("[Boussole céleste] Auto-vérification — " + Object.entries(res).map(([k, v]) => `${lib[k]} : ${v ? "✓" : "✗"}`).join(" · "));
  return { ok, ...res };
}

/* ————— Fin du test ————— */
function finish(){
  lastNotes   = computeScores(state.answers, state.reelles, state.selection);
  lastMesures = compterMesures(state.answers, state.reelles, state.selection);
  lastPart    = repartition(state.answers, state.reelles, state.selection);
  resultatsGardesCe = false;
  mesurer("test-fin");
  /* Le brouillon n'est effacé qu'une fois les résultats ouverts : effacé ici, il
     laissait celui qui part payer sans rien à retrouver au retour. */
  if(paywallActif() && niveauAcces === "aucun"){ ouvrirPaywall(); return; }
  effacerBrouillon();
  renderResults(lastNotes);
  showView("v-resultats");
}

/* ————— Câblage ————— */
$("#navHome").addEventListener("click", () => { majBandeauReprise(); showView("v-accueil"); });
$("#btnVersJournal").addEventListener("click", () => { renderPerso(); showView("v-perso"); });
$("#btnGarder").addEventListener("click", garderResultats);
$("#btnJournalExport").addEventListener("click", exporterJournal);
$("#jImport").addEventListener("change", e => { if(e.target.files[0]) importerJournal(e.target.files[0]); e.target.value = ""; });
$("#btnJournalVider").addEventListener("click", () => {
  const j = chargerJournal();
  if(!j || !j.entrees.length){ $("#jFeedback2").textContent = "Le journal est déjà vide."; return; }
  if(!confirm(`Effacer définitivement les ${j.entrees.length} entrées de ton journal ? Pense à exporter d’abord.`)) return;
  sauverJournal({ entrees: [] });
  renderJournalBlocs();
});
const commencer = () => { mesurer("test-debut"); showView("v-emotions"); };
$("#btnStart").addEventListener("click", commencer);
$("#btnStart2").addEventListener("click", commencer);
/* Départ vers le paiement, écouté sur le document : deux chemins mènent à Stripe. */
document.addEventListener("click", e => { if(e.target.closest && e.target.closest('a[href*="buy.stripe.com"]')) mesurer("stripe"); }, true);
$("#btnToTest").addEventListener("click", () => { renderPerso(); showView("v-perso"); });
$("#btnMomentAjout").addEventListener("click", ajouterMoment);
$("#btnPersoRetour").addEventListener("click", () => showView("v-emotions"));
$("#btnPersoContinuer").addEventListener("click", () => { construireSelection(); state.i = 0; renderQuestion(); showView("v-test"); sauverBrouillon(); });
$("#btnPrev").addEventListener("click", () => { if(state.i === 0){ renderPerso(); showView("v-perso"); } else gotoQuestion(state.i - 1); });
$("#btnNext").addEventListener("click", () => {
  if($("#btnNext").disabled) return;
  if(state.i === state.selection.length - 1) finish(); else gotoQuestion(state.i + 1);
});
$("#btnRien").addEventListener("click", toutRien);
$("#btnCopy").addEventListener("click", copierResultats);
$("#btnCarte").addEventListener("click", ouvrirCarte);
$("#btnCartePromo").addEventListener("click", () => {
  const box = $("#venteBox");
  if(!box || box.hidden) return;
  mesurer("promo-carte");
  box.scrollIntoView({ behavior: prefersReduced ? "auto" : "smooth", block:"center" });
  $("#btnAcheter").focus({ preventScroll:true });
});
let paywallEnAttente = false;
const ouvrirModaleCle = mode => {
  const cadeau = mode === "cadeau";
  $("#cleStatut").textContent = "";
  $("#rapportTitre").textContent = cadeau ? "Utiliser mon code cadeau" : "Débloquer mon accès";
  $("#cleHint").innerHTML = cadeau
    ? "Colle ici le code qu’on t’a envoyé&nbsp;: il ressemble à «&nbsp;BC-XXXX-XXXX&nbsp;». Il ouvre tes résultats, une fois, pendant vingt-quatre heures."
    : "Colle ici la référence d’achat affichée après ton paiement&nbsp;: elle commence par «&nbsp;cs_&nbsp;». Normalement, l’onglet se débloque tout seul&nbsp;; ceci ne sert qu’en dépannage."
      + (cadeauActif() ? " Un code cadeau a sa place ici aussi." : "");
  $("#cleLicence").placeholder = cadeau ? "BC-XXXX-XXXX" : (cadeauActif() ? "cs_live_… ou BC-XXXX-XXXX" : "cs_live_…");
  paywallEnAttente = !$("#paywallOverlay").hidden;   /* la fenêtre de clé passe devant */
  $("#paywallOverlay").hidden = true;
  $("#rapportOverlay").hidden = false;
  $("#cleLicence").focus();
};
const fermerModaleCle = () => {
  $("#rapportOverlay").hidden = true;
  if(paywallEnAttente){ $("#paywallOverlay").hidden = false; paywallEnAttente = false; }
};
$("#btnDejaCle").addEventListener("click", () => { if(niveauAcces === "dossier"){ ouvrirRapport(); return; } ouvrirModaleCle(); });
$("#btnPaywallCle").addEventListener("click", () => ouvrirModaleCle());
$("#btnPaywallCadeau").addEventListener("click", () => ouvrirModaleCle("cadeau"));
$("#btnCreerCadeau").addEventListener("click", demanderCadeau);
$("#btnSkipPaiement").addEventListener("click", () => appliquerAcces("dossier"));
$("#btnPaywallRetour").addEventListener("click", () => { $("#paywallOverlay").hidden = true; });
$("#paywallOverlay").addEventListener("click", e => { if(e.target === e.currentTarget) e.currentTarget.hidden = true; });
$("#btnValiderCle").addEventListener("click", validerCle);
$("#cleLicence").addEventListener("keydown", e => { if(e.key === "Enter") validerCle(); });
$("#btnFermerCle").addEventListener("click", fermerModaleCle);
$("#rapportOverlay").addEventListener("click", e => { if(e.target === e.currentTarget) fermerModaleCle(); });
$("#btnRapportPdf").addEventListener("click", () => window.print());
$("#btnRapportRetour").addEventListener("click", () => showView("v-resultats"));
$("#venteCgv").addEventListener("change", majVenteBox);
$("#btnRapportCarte").addEventListener("click", () => { showView("v-resultats"); ouvrirCarte(); });
$("#btnCarteDl").addEventListener("click", telechargerCarte);
$("#btnCartePartage").addEventListener("click", partagerCarte);
$("#btnCarteFermer").addEventListener("click", fermerCarte);
document.querySelectorAll(".carte-formats .fmt").forEach(b => b.addEventListener("click", async () => {
  if(b.dataset.fmt === carteFormat) return;
  carteFormat = b.dataset.fmt;
  document.querySelectorAll(".carte-formats .fmt").forEach(x => { const s = x.dataset.fmt === carteFormat; x.classList.toggle("sel", s); x.setAttribute("aria-checked", s); });
  await fabriquerCarte(500);
}));
$("#carteOverlay").addEventListener("click", e => { if(e.target === e.currentTarget) fermerCarte(); });
$("#btnRestart").addEventListener("click", () => {
  effacerBrouillon();
  state.i = 0;
  state.answers = Array.from({length:N}, () => null);
  state.reelles = [];
  construireSelection();
  saisie = saisieVierge();
  $("#jNote").value = "";
  lastNotes = lastMesures = lastPart = null;
  fermerCarte();
  $("#copyFeedback").textContent = "";
  majBandeauReprise();
  showView("v-accueil");
});
/* La tabulation reste dans la fenêtre ouverte. */
document.addEventListener("keydown", e => {
  if(e.key !== "Tab") return;
  const modale = [$("#paywallOverlay"), $("#rapportOverlay"), $("#carteOverlay")].find(m => m && !m.hidden);
  if(!modale) return;
  const cibles = [...modale.querySelectorAll('a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])')].filter(el => el.offsetParent !== null);
  if(!cibles.length) return;
  const premier = cibles[0], dernier = cibles[cibles.length - 1];
  if(e.shiftKey && document.activeElement === premier){ dernier.focus(); e.preventDefault(); }
  else if(!e.shiftKey && document.activeElement === dernier){ premier.focus(); e.preventDefault(); }
});
/* Échap ferme la fenêtre ouverte, sauf la fenêtre de fin de test, qu'on ne contourne pas. */
document.addEventListener("keydown", e => {
  if(e.key !== "Escape") return;
  if(!$("#carteOverlay").hidden){ fermerCarte(); e.preventDefault(); return; }
  if(!$("#rapportOverlay").hidden){ fermerModaleCle(); e.preventDefault(); }
});
$("#btnVersMethode").addEventListener("click", () => showView("v-methode"));
$("#btnFooterMethode").addEventListener("click", () => showView("v-methode"));
$("#btnFooterEnergies").addEventListener("click", () => showView("v-emotions"));
$("#btnMethodeRetour").addEventListener("click", () => showView("v-emotions"));
$("#btnCopierCode").addEventListener("click", copierCode);
$("#btnComparer").addEventListener("click", validerCodeAmi);
$("#compCode").addEventListener("keydown", e => { if(e.key === "Enter") validerCodeAmi(); });
$("#btnRappel").addEventListener("click", creerRappel);
$("#btnInstaller").addEventListener("click", installerApp);
$("#btnSigne").addEventListener("click", chercherSigne);
$("#btnSigneEffacer").addEventListener("click", effacerSigne);

/* Un achat déjà fait sur cet appareil rouvre l'accès sans rien redemander. */
const accesEnregistre = lireAcces();
if(accesEnregistre) niveauAcces = accesEnregistre;
/* Le paiement se fait dans un autre onglet : celui-ci l'apprend aussitôt. */
window.addEventListener("storage", e => {
  if(e.key !== ACCES_KEY) return;
  const n = lireAcces();
  if(!n || niveauAcces === n) return;
  niveauAcces = n;
  if(lastNotes) appliquerAcces(n);
});

normaliserRadios(document.body);
renderEnergyCards();
initSigne();
majBandeauReprise();
/* ?apercu=1 (mode test seulement) : la fenêtre de fin, sur un profil d'exemple. */
if(APERCU){
  const exemple = SITUATIONS.map(s => Object.fromEntries(s.reac.map(([id], k) => [id, (k * 3) % 5])));
  lastNotes = computeScores(exemple, [], null);
  lastMesures = compterMesures(exemple, [], null);
  lastPart = repartition(exemple, [], null);
  ouvrirPaywall();
}
runSelfTests();
mesurer("accueil");
if("serviceWorker" in navigator && location.protocol === "https:"){
  window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
}
window.__celeste = { ENERGIES, SITUATIONS, ROTATIONS, computeScores, compterMesures, repartition, state, runSelfTests, buildCopyText, candidatsSigne };
