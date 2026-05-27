# -*- mode: python ; coding: utf-8 -*-
"""
Especificación para PyInstaller - DentalPro.

Crea un ejecutable único (one-file) para Windows, macOS y Linux.
Incluye:
- Aplicación Django completa
- Base de datos SQLite pre-inicializada
- Archivos estáticos y media
- Todos los templates y configuración

Uso:
    pyinstaller dentalpro.spec

Esto creará:
    - dist/DentalPro (ejecutable)
    - build/ (archivos temporales)

Nota: El icono puede configurarse con icon='desktop/dentalpro.ico'
"""

from PyInstaller.utils.hooks import collect_submodules
import os

# Directorio del proyecto
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

block_cipher = None

# Archivos y directorios a incluir en el ejecutable
datas = [
    # Base de datos SQLite pre-inicializada
    (os.path.join(PROJECT_DIR, 'db.sqlite3'), '.'),
    
    # Archivos estáticos (CSS, JS, imágenes)
    (os.path.join(PROJECT_DIR, 'static'), 'static'),
    
    # Archivos de media (imágenes clínicas, radiografías)
    (os.path.join(PROJECT_DIR, 'media'), 'media'),
    
    # Templates de core (base.html, index.html)
    (os.path.join(PROJECT_DIR, 'core', 'templates'), 'core/templates'),
    
    # Templates de pacientes (listado, detalles, búsqueda)
    (os.path.join(PROJECT_DIR, 'pacientes', 'templates'), 'pacientes/templates'),
    
    # Configuración de Django (settings, urls)
    (os.path.join(PROJECT_DIR, 'config'), 'config'),
]

# Módulos Python a incluir (evita errores de importación)
hiddenimports = [
    'django',
    'django.conf',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.core.wsgi',
    'django.core.management',
    'django.db.models',
    'django.template.loaders.filesystem',
    'django.template.loaders.app_directories',
    'waitress',
]

# Análisis de dependencias
a = Analysis(
    [os.path.join(PROJECT_DIR, 'desktop', 'launcher.py')],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Archivar módulos compilados
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Crear ejecutable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DentalPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Cambiar a True durante la depuración para ver logs en consola

    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Descomentar y asignar: icon='desktop/dentalpro.ico'
)
