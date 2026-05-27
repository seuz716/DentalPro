#!/usr/bin/env python
"""
Utilidad de línea de comando para tareas administrativas.
"""

import os
import sys


def main():
    """Ejecutar tareas administrativas."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se puede importar Django. ¿Está instalado y disponible en PYTHONPATH?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
