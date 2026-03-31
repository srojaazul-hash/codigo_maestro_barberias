self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('fetch', (e) => {
  e.respondWith(fetch(e.request).catch(() => console.log("Sin conexión")));
});

self.addEventListener('push', function(event) {
    const options = {
        body: event.data.text(),
        icon: '/static/icon.png',
        badge: '/static/icon.png'
    };
    event.waitUntil(
        self.registration.showNotification('Nueva Cita', options)
    );
});