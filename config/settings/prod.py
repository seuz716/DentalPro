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

# Rutas relativas (relativas a BASE_DIR)
# Ya configuradas en base.py usando Path de pathlib

# Middleware para capturar excepciones no controladas en producción
MIDDLEWARE += [
    'core.middleware.FriendlyErrorMiddleware',
]

