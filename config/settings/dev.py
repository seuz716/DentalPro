"""
Configuración de Django para desarrollo.
Hereda de base.py con ajustes para DEBUG y acceso local.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']
