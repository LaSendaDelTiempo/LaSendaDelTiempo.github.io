/* =====================================================
   Service Worker — QuienBuscaEncuentra
   Estrategia: Network First con fallback a caché
   Cada apertura comprueba si hay versión nueva en el servidor.
   Si hay conexión → carga la nueva y actualiza la caché.
   Si no hay conexión → sirve la caché guardada.
===================================================== */

const CACHE_NAME = 'qbe-v1';

// Archivos a cachear en la instalación inicial
const PRECACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.png',
  '/apple-touch-icon.png'
];

// ── Instalación: guarda los archivos básicos ──────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE))
  );
  // Activa el SW nuevo inmediatamente, sin esperar a que se cierren las pestañas
  self.skipWaiting();
});

// ── Activación: borra cachés antiguas ─────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      )
    )
  );
  // Toma control de todas las pestañas abiertas de inmediato
  self.clients.claim();
});

// ── Fetch: Network First ───────────────────────────────
self.addEventListener('fetch', event => {
  // Solo interceptamos peticiones GET a nuestro propio origen
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  if (url.origin !== location.origin) return;

  event.respondWith(
    fetch(event.request)
      .then(networkResponse => {
        // Si la red responde bien, actualizamos la caché y devolvemos la respuesta
        if (networkResponse && networkResponse.status === 200) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return networkResponse;
      })
      .catch(() => {
        // Sin conexión: servimos desde caché
        return caches.match(event.request);
      })
  );
});
