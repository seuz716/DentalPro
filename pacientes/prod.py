"""
Configuración de Django para producción.
Hereda de base.py con ajustes de seguridad estrictos.

IMPORTANTE: Para desarrollo/pruebas locales (127.0.0.1:8000),
descomenta las líneas marcadas con "← LOCAL" si necesitas usar HTTP.
"""

from .base import *

# ============================================================================
# DEBUG Y SEGURIDAD BÁSICA
# ============================================================================

# NUNCA activar DEBUG en producción
DEBUG = False

# Hosts permitidos (estrictamente local para desktop)
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '[::1]']

# ============================================================================
# SEGURIDAD HTTPS Y COOKIES (DESCOMENTA PARA LOCAL SI ES NECESARIO)
# ============================================================================

# Redirigir HTTP a HTTPS automáticamente
SECURE_SSL_REDIRECT = False  # ← LOCAL: Mantén False si usas http://localhost:8000

# Cookies solo por HTTPS
SESSION_COOKIE_SECURE = False  # ← LOCAL: Mantén False para localhost
CSRF_COOKIE_SECURE = False  # ← LOCAL: Mantén False para localhost

# Activar HSTS (HTTP Strict Transport Security)
# Uncomment en producción con HTTPS real
SECURE_HSTS_SECONDS = 0  # ← LOCAL: Cambia a 31536000 (1 año) en producción con HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = False  # ← LOCAL: Cambia a True en producción
SECURE_HSTS_PRELOAD = False  # ← LOCAL: Cambia a True en producción

# ============================================================================
# CSRF Y SEGURIDAD
# ============================================================================

# Orígenes CSRF de confianza (localhost para desktop)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Configuración de protección CSRF
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# ============================================================================
# HEADERS DE SEGURIDAD
# ============================================================================

# Content Security Policy (CSP) - permite CDN de Tailwind, HTMX, Lucide
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    
    'script-src': (
        "'self'",
        "cdn.tailwindcss.com",  # Tailwind CSS CDN
        "unpkg.com",  # HTMX y Lucide Icons
        "'unsafe-inline'",  # Requerido para Tailwind JIT
    ),
    
    'style-src': (
        "'self'",
        "'unsafe-inline'",  # Requerido para Tailwind
        "cdn.tailwindcss.com",
        "fonts.googleapis.com",
    ),
    
    'img-src': (
        "'self'",
        "data:",  # Permite data URIs para imágenes inline
    ),
    
    'font-src': (
        "'self'",
        "fonts.googleapis.com",
        "fonts.gstatic.com",
    ),
    
    'connect-src': (
        "'self'",  # Permite fetch/AJAX solo a mismo origin (HTMX requests)
    ),
    
    'frame-ancestors': ("'none'",),  # No permite embedding en iframes
    
    'form-action': ("'self'",),  # Formularios solo a mismo origin
}

# Protección contra clickjacking (X-Frame-Options)
X_FRAME_OPTIONS = 'DENY'

# Prevención de MIME-sniffing (no adivines tipos MIME)
SECURE_CONTENT_TYPE_NOSNIFF = True

# Protección XSS en navegadores antiguos
SECURE_BROWSER_XSS_FILTER = True

# Política de referrer (no envía referrer a orígenes externos)
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# ============================================================================
# COOKIES Y SESIONES
# ============================================================================

# Configuración de cookie de sesión
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_COOKIE_HTTPONLY = True  # No accesible desde JavaScript
SESSION_COOKIE_SAMESITE = 'Strict'  # No envía cookies con requests cross-site

# Expirar sesión al cerrar navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# ============================================================================
# MIDDLEWARE CUSTOM
# ============================================================================

MIDDLEWARE += [
    'core.middleware.FriendlyErrorMiddleware',
]

# ============================================================================
# LOGGING EN PRODUCCIÓN
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/dentalpro.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django.security': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ============================================================================
# NOTA IMPORTANTE PARA DESKTOP
# ============================================================================

"""
El launcher de escritorio (desktop/launcher.py) inicia el servidor en:
    http://127.0.0.1:8000

Por eso desactivamos HTTPS localmente (SECURE_SSL_REDIRECT=False, etc).

Si despliegas DentalPro en un servidor REAL con dominio (ej: dentalpro.miempresa.com),
comenta estas líneas:

    SECURE_SSL_REDIRECT = False  ← COMENTA (activa HTTPS redirect)
    SESSION_COOKIE_SECURE = False  ← COMENTA (activa secure cookies)
    CSRF_COOKIE_SECURE = False  ← COMENTA
    SECURE_HSTS_SECONDS = 0  ← CAMBIA A 31536000

Y genera certificados SSL válidos (ej: Let's Encrypt).
"""
