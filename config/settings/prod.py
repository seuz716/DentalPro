"""
Configuración de Django para producción.
Hereda de base.py con ajustes de seguridad.
"""

from .base import *

# Desactivar DEBUG en producción
DEBUG = False

# Hosts permitidos en producción (restringidos)
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Configuración de seguridad CSRF
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Deshabilitar si tu sitio no es embebido por otros
X_FRAME_OPTIONS = 'DENY'

# Content Security Policy (CSP) para mitigar ataques XSS
# Cuidado: ajusta esto a *tus* fuentes reales para evitar bloquear recursos
SECURE_CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "  # Permite recursos desde el propio dominio
    "script-src 'self' 'unsafe-inline' https://unpkg.com; " # Scripts (ajustar si usas CDNs)
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " # Estilos
    "img-src 'self' data:; " # Imágenes
    "font-src 'self' https://fonts.gstatic.com; " # Fuentes
    "connect-src 'self'; " # Conexiones (AJAX, WebSockets)
    "object-src 'none'; " # Prohíbe plugins como Flash
    "frame-ancestors 'none'; " # Equivale a X-Frame-Options DENY
)

# Rutas relativas (relativas a BASE_DIR)
# Ya configuradas en base.py usando Path de pathlib

# Middleware para capturar excepciones no controladas en producción
MIDDLEWARE += [
    'core.middleware.FriendlyErrorMiddleware',
]

