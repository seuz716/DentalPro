# -*- mode: python ; coding: utf-8 -*-
"""
Especificación para PyInstaller - DentalPro.

Crea un ejecutable único (one-file) para Windows, macOS y Linux.
Incluye:
- Aplicación Django completa
- Archivos estáticos y media
- Base de datos SQLite

Uso:
    pyinstaller dentalpro.spec --onefile

Esto creará:
    - dist/dentalpro (ejecutable)
    - build/ (archivos temporales)
"""

from PyInstaller.utils.hooks import get_module_collection_mode
import os

# Directorio del proyecto
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

block_cipher = None

# Archivos y directorios a incluir
datas = [
    # Archivos estáticos
    (os.path.join(PROJECT_DIR, 'static'), 'static'),
    
    # Archivos de media
    (os.path.join(PROJECT_DIR, 'media'), 'media'),
    
    # Templates de core
    (os.path.join(PROJECT_DIR, 'core', 'templates'), 'core/templates'),
    
    # Templates de pacientes
    (os.path.join(PROJECT_DIR, 'pacientes', 'templates'), 'pacientes/templates'),
    
    # Configuración de Django
    (os.path.join(PROJECT_DIR, 'config'), 'config'),
]

# Módulos Python a incluir
hiddenimports = [
    'django',
    'django.conf',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.core.wsgi',
    'django.core.management',
    'django.db.models',
    'django.template.loaders.filesystem',
    'django.template.loaders.app_directories',
    'waitress',
]

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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
