/* ============================================================
   Service worker di Cyber Hub.
   Obiettivo: rendere l'INTERFACCIA disponibile offline (app shell).
   I siti esterni linkati nelle card NON vengono messi in cache:
   restano risorse online di terze parti.

   Quando modifichi i file dell'app, alza il numero di versione qui
   sotto (es. v2): così il browser scarica la nuova cache e butta
   quella vecchia.
   ============================================================ */
const CACHE = "cyberhub-v2";

/* L'app shell: i file minimi che servono per mostrare l'interfaccia.
   Percorsi RELATIVI così funziona anche sotto /pezzaliapp-cyberhub/ su GitHub Pages. */
const APP_SHELL = [
  "./",
  "./index.html",
  "./data.json",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
  "./icons/apple-touch-icon.png"
];

/* INSTALL: pre-carico l'app shell in cache. */
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting(); // attiva subito la nuova versione
});

/* ACTIVATE: cancello le cache vecchie con nome diverso. */
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

/* FETCH: strategia "stale-while-revalidate" SOLO per i nostri file
   (stessa origine). Mostro subito la copia in cache (veloce/offline) e
   nel frattempo aggiorno la cache dalla rete per la volta successiva.
   Le richieste verso altri domini (le mappe, i giochi...) le lascio
   passare normalmente: non ha senso metterle in cache. */
self.addEventListener("fetch", (event) => {
  const req = event.request;

  // gestisco solo GET di pagina/risorse della mia origine
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) {
    return; // lascio fare al browser (rete normale)
  }

  event.respondWith(
    caches.open(CACHE).then(async (cache) => {
      const cached = await cache.match(req);
      const network = fetch(req)
        .then((res) => {
          if (res && res.status === 200) cache.put(req, res.clone());
          return res;
        })
        .catch(() => null);

      // se ho una copia in cache la uso subito, altrimenti aspetto la rete
      return cached || (await network) ||
        // fallback finale per le navigazioni offline senza copia: l'index
        (req.mode === "navigate" ? cache.match("./index.html") : Response.error());
    })
  );
});
