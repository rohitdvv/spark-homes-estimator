/* Spark Homes Repair Estimator — service worker
 * Offline-first: pre-cache the app shell + icons, runtime-cache CDN libraries.
 * Bump CACHE version to force clients to refresh cached assets. */
const CACHE = 'spark-estimator-v14';

// App shell — everything needed to boot fully offline.
const SHELL = [
  './',
  './index.html',
  './manifest.json',
  './spark-logo.png',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png',
  './apple-touch-icon.png',
  './favicon.png'
];

// CDN libraries + on-device AI assets cached at runtime so a second launch
// (and the offline semantic Copilot / OCR) work with no network.
const RUNTIME_HOSTS = [
  'cdn.tailwindcss.com', 'cdn.jsdelivr.net', 'unpkg.com',
  'huggingface.co', 'cdn-lfs.huggingface.co', 'cdn-lfs-us-1.hf.co', 'hf.co', // embedding model weights
  'tessdata.projectnaptha.com' // Tesseract OCR trained data
];

self.addEventListener('message', (e) => { if (e.data === 'skipWaiting') self.skipWaiting(); });

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const isRuntime = RUNTIME_HOSTS.some((h) => url.hostname.endsWith(h));
  const sameOrigin = url.origin === self.location.origin;

  // Network-first for the HTML document / navigations so updates show
  // immediately when online; fall back to cache when offline.
  const isDoc = req.mode === 'navigate' || (sameOrigin && /\.html(\?|$)/.test(url.pathname + url.search)) ||
                (sameOrigin && (url.pathname === '/' || url.pathname.endsWith('/')));
  if (isDoc) {
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put('./index.html', copy));
          return res;
        })
        .catch(() => caches.match(req).then((hit) => hit || caches.match('./index.html')))
    );
    return;
  }

  if (sameOrigin || isRuntime) {
    // Cache-first for static assets + CDN libs; populate cache on miss.
    e.respondWith(
      caches.match(req).then((hit) => {
        if (hit) return hit;
        return fetch(req)
          .then((res) => {
            if (res && res.status === 200 && (res.type === 'basic' || res.type === 'cors')) {
              const copy = res.clone();
              caches.open(CACHE).then((c) => c.put(req, copy));
            }
            return res;
          })
          .catch(() => caches.match('./index.html'));
      })
    );
  }
});
