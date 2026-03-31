self.addEventListener('install', (e) => {
  console.log('Service Worker instalado');
});

self.addEventListener('fetch', (e) => {
  // Aquí podríamos añadir lógica para que funcione sin internet
});

// Lógica para recibir notificaciones
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