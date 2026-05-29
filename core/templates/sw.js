const CACHE_NAME = 'dentalpro-cache-v1';
const STATIC_ASSETS = [
    '/',
    'https://cdn.tailwindcss.com',
    'https://unpkg.com/htmx.org@1.9.10',
    'https://unpkg.com/lucide@latest',
    'https://unpkg.com/three@0.152.2/build/three.min.js',
    'https://unpkg.com/three@0.152.2/examples/js/controls/OrbitControls.js'
];

// Instalar y almacenar en caché los activos estáticos principales
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// Activar y purgar cachés obsoletos
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.map(key => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Interceptar y despachar peticiones (Fetch)
self.addEventListener('fetch', event => {
    // Excluir WebSockets y peticiones que no sean GET
    if (
        event.request.url.startsWith('ws') || 
        event.request.url.includes('/ws/') || 
        event.request.method !== 'GET'
    ) {
        return;
    }

    const requestUrl = new URL(event.request.url);

    // Evitar interceptar el panel de administración
    if (requestUrl.pathname.startsWith('/admin/')) {
        return;
    }

    // Determinar si es un asset estático o librería CDN
    const isStaticAsset = (
        requestUrl.pathname.includes('/static/') ||
        event.request.url.includes('unpkg.com') ||
        event.request.url.includes('tailwindcss.com') ||
        event.request.url.includes('cdnjs.cloudflare.com')
    );

    if (isStaticAsset) {
        // Estrategia: Cache First (Optimiza velocidad y uso offline)
        event.respondWith(
            caches.match(event.request).then(cachedResponse => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(event.request).then(networkResponse => {
                    if (!networkResponse || networkResponse.status !== 200) {
                        return networkResponse;
                    }
                    return caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, networkResponse.clone());
                        return networkResponse;
                    });
                });
            })
        );
    } else {
        // Estrategia: Network First (Asegura datos frescos, fallback offline)
        event.respondWith(
            fetch(event.request)
                .then(networkResponse => {
                    if (networkResponse && networkResponse.status === 200) {
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, networkResponse.clone());
                        });
                    }
                    return networkResponse;
                })
                .catch(() => {
                    return caches.match(event.request).then(cachedResponse => {
                        if (cachedResponse) {
                            return cachedResponse;
                        }
                        // Fallback: Si no hay red ni caché para esta url, retornar home o página offline
                        return caches.match('/');
                    });
                })
        );
    }
});
