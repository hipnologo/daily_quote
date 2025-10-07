// Service Worker for Daily Quote PWA
// Provides offline functionality and caching for better performance

const CACHE_NAME = 'daily-quote-v1';
const OFFLINE_URL = '/offline.html';

// Resources to cache for offline functionality
const CACHE_RESOURCES = [
  '/',
  '/index.html',
  '/daily_quote.png',
  'https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.3.2/html2canvas.min.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@400;500;600;700&display=swap',
  'https://flagicons.lipis.dev/flags/4x3/us.svg',
  'https://flagicons.lipis.dev/flags/4x3/es.svg',
  'https://flagicons.lipis.dev/flags/4x3/br.svg',
  'https://flagicons.lipis.dev/flags/4x3/it.svg'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  console.log('Service Worker installing');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker caching resources');
        return cache.addAll(CACHE_RESOURCES);
      })
      .catch((error) => {
        console.log('Service Worker cache failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip external URLs for caching strategy
  if (!event.request.url.startsWith(self.location.origin) &&
      !event.request.url.includes('cdnjs.cloudflare.com') &&
      !event.request.url.includes('fonts.googleapis.com') &&
      !event.request.url.includes('flagicons.lipis.dev')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        // Return cached version if available
        if (cachedResponse) {
          return cachedResponse;
        }

        // Otherwise, fetch from network
        return fetch(event.request)
          .then((response) => {
            // Don't cache non-successful responses
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone the response (can only be consumed once)
            const responseToCache = response.clone();

            // Cache successful responses for future use
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });

            return response;
          })
          .catch(() => {
            // Network failed, return offline page for navigation requests
            if (event.request.destination === 'document') {
              return caches.match(OFFLINE_URL);
            }
          });
      })
  );
});

// Background sync for quote updates (if supported)
self.addEventListener('sync', (event) => {
  if (event.tag === 'quote-sync') {
    console.log('Service Worker background sync for quotes');
    event.waitUntil(syncQuotes());
  }
});

async function syncQuotes() {
  try {
    // This would sync quotes when online
    // Implementation depends on your specific requirements
    console.log('Syncing quotes in background');
  } catch (error) {
    console.log('Quote sync failed:', error);
  }
}

// Push notification handling (if needed)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/daily_quote.png',
      badge: '/daily_quote.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: 1
      }
    };

    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  event.waitUntil(
    clients.openWindow('/')
  );
});
