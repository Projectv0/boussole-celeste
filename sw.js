/* Service worker — met le site en cache pour un usage hors connexion.
   Stratégie : réseau d'abord (pour recevoir les mises à jour), cache en secours.
   Le nom du cache change à chaque déploiement (outils/construire.py, site/VERSION). */
const CACHE = "celeste-v1";
const ESSENTIELS = ["./", "./index.html", "./merci.html", "./manifest.webmanifest",
                    "./icone-192.png", "./icone-512.png", "./favicon.svg",
                    /* les polices sont hébergées ici : sans elles en cache, la page hors
                       connexion retomberait sur les polices système */
                    "./polices/polices.css",
                    "./polices/jost-400-latin.woff2",
                    "./polices/cormorant-garamond-600-latin.woff2"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ESSENTIELS)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(noms => Promise.all(noms.filter(n => n !== CACHE).map(n => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", e => {
  if(e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  /* Rien qui vienne d'ailleurs (le Worker, Stripe), et rien qui porte une chaîne de
     requête : merci.html?session_id=… ne doit jamais être servi depuis le cache. */
  if(url.origin !== location.origin || url.search) return;
  e.respondWith(
    fetch(e.request)
      .then(rep => {
        if(rep && rep.status === 200 && rep.type === "basic"){
          const copie = rep.clone();
          caches.open(CACHE).then(c => c.put(e.request, copie));
        }
        return rep;
      })
      /* Le repli sur index.html ne vaut que pour une navigation (piège Boussole : il
         servait la page du test à la place de merci.html). */
      .catch(() => caches.match(e.request).then(r =>
        r || (e.request.mode === "navigate" ? caches.match("./index.html") : Response.error())))
  );
});
