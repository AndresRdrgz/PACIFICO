const CACHE_NAME = 'pacifico-workflow-v1.0.1';
const STATIC_CACHE = 'pacifico-static-v1.0.1';
const DYNAMIC_CACHE = 'pacifico-dynamic-v1.0.1';

const urlsToCache = [
  '/workflow/',
  '/workflow/dashboard/',
  '/workflow/bandeja/',
  '/workflow/nueva-solicitud/',
  '/workflow/negocios/',
  '/workflow/offline/',
  '/static/workflow/manifest.json',
  '/static/images/logoBlanco.png',
  '/static/workflow/icons/icon-192x192.png',
  '/static/workflow/icons/icon-512x512.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

const STATIC_FILES = [
  '/static/workflow/icons/icon-16x16.png',
  '/static/workflow/icons/icon-32x32.png',
  '/static/workflow/icons/icon-72x72.png',
  '/static/workflow/icons/icon-96x96.png',
  '/static/workflow/icons/icon-128x128.png',
  '/static/workflow/icons/icon-144x144.png',
  '/static/workflow/icons/icon-152x152.png',
  '/static/workflow/icons/icon-192x192.png',
  '/static/workflow/icons/icon-384x384.png',
  '/static/workflow/icons/icon-512x512.png',
  '/static/workflow/icons/apple-touch-icon.png',
  '/static/workflow/icons/favicon.ico'
];

// Install event
self.addEventListener('install', event => {
  console.log('Service Worker installing...');
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then(cache => {
        console.log('Caching static files');
        return cache.addAll(STATIC_FILES);
      }),
      caches.open(CACHE_NAME).then(cache => {
        console.log('Caching core files');
        return cache.addAll(urlsToCache);
      })
    ]).catch(error => {
      console.error('Cache addAll failed:', error);
    })
  );
  // Force the waiting service worker to become the active service worker
  self.skipWaiting();
});

// Activate event
self.addEventListener('activate', event => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME && cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Take control of all clients immediately
      return self.clients.claim();
    })
  );
});

// Fetch event - Cache first for static assets, network first for dynamic content
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip cross-origin requests
  if (!request.url.startsWith(self.location.origin) && !request.url.startsWith('https://cdn.')) {
    return;
  }

  // Handle different types of requests
  if (request.destination === 'image' || request.url.includes('/static/') || request.url.includes('cdn.')) {
    // Cache first strategy for static assets
    event.respondWith(cacheFirst(request));
  } else if (request.url.includes('/workflow/api/') || request.method === 'POST') {
    // Network only for API calls and POST requests
    event.respondWith(networkOnly(request));
  } else {
    // Network first strategy for pages
    event.respondWith(networkFirst(request));
  }
});

// Cache first strategy
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Network failed for cache first:', error);
    return new Response('Contenido no disponible sin conexión', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// Network first strategy
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', error);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      const offlinePage = await caches.match('/workflow/offline/');
      if (offlinePage) {
        return offlinePage;
      }
    }
    
    return new Response('Contenido no disponible sin conexión', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: new Headers({
        'Content-Type': 'text/html'
      })
    });
  }
}

// Network only strategy
async function networkOnly(request) {
  try {
    return await fetch(request);
  } catch (error) {
    return new Response(JSON.stringify({
      error: 'No hay conexión a internet',
      message: 'Esta funcionalidad requiere conexión'
    }), {
      status: 503,
      statusText: 'Service Unavailable',
      headers: new Headers({
        'Content-Type': 'application/json'
      })
    });
  }
}

// Cache management functions
async function cleanupOldCaches() {
  const cacheWhitelist = [CACHE_NAME, STATIC_CACHE, DYNAMIC_CACHE];
  const cacheNames = await caches.keys();
  
  return Promise.all(
    cacheNames.map(cacheName => {
      if (!cacheWhitelist.includes(cacheName)) {
        console.log('Deleting old cache:', cacheName);
        return caches.delete(cacheName);
      }
    })
  );
}

// Periodic cache cleanup
self.addEventListener('periodicsync', event => {
  if (event.tag === 'cache-cleanup') {
    event.waitUntil(cleanupOldCaches());
  }
});

// Handle skip waiting
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Background sync for offline actions
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    console.log('Background sync triggered');
    // Handle any background sync operations here
  }
});

// Push notifications (if needed in the future)
self.addEventListener('push', event => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/static/workflow/icons/icon-192x192.png',
      badge: '/static/workflow/icons/icon-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: data.primaryKey
      },
      actions: [
        {
          action: 'explore',
          title: 'Ver detalles',
          icon: '/static/workflow/icons/icon-192x192.png'
        },
        {
          action: 'close',
          title: 'Cerrar',
          icon: '/static/workflow/icons/icon-192x192.png'
        }
      ]
    };

    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/workflow/dashboard/')
    );
  }
});

console.log('Service Worker loaded successfully - Version 1.0.1');
