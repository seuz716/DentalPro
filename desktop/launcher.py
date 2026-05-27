#!/usr/bin/env python
"""
Launcher de escritorio para DentalPro.

Inicia automáticamente:
1. Servidor Waitress en puerto 8000
2. Abre el navegador web a http://localhost:8000
3. Maneja cierre limpio y liberación de recursos

Uso:
    python desktop/launcher.py

Requisitos:
    - waitress (instalado en requirements/prod.txt)
    - config/settings/prod.py configurado correctamente
"""

import os
import sys
import webbrowser
import threading
import time
import signal
import socket
from pathlib import Path
from subprocess import Popen, PIPE
from wsgiref.simple_server import WSGIServer

# Manejo de PyInstaller (directorio temporal de extracción)
if getattr(sys, 'frozen', False):
    try:
        os.chdir(sys._MEIPASS)
        PROJECT_DIR = Path(sys._MEIPASS)
    except Exception as e:
        PROJECT_DIR = Path(__file__).resolve().parent.parent
else:
    PROJECT_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_DIR))

# Configurar variables de entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')


def setup_django():
    """
    Configura Django antes de iniciar el servidor.
    """
    import django
    django.setup()


def open_browser(url='http://localhost:8000', delay=2):
    """
    Abre el navegador web después de un retraso.
    
    Args:
        url: URL a abrir en el navegador
        delay: Tiempo de espera en segundos antes de abrir
    """
    time.sleep(delay)
    try:
        webbrowser.open(url)
        print(f"✓ Navegador abierto en {url}")
    except Exception as e:
        print(f"⚠ No se pudo abrir el navegador automáticamente: {e}")
        print(f"✓ Abre manualmente: {url}")


def run_waitress_server(host='127.0.0.1', port=8000, threads=4):
    """
    Inicia el servidor Waitress.
    
    Args:
        host: Host donde escuchar
        port: Puerto donde escuchar
        threads: Número de threads de trabajo
    """
    try:
        # Importar después de setup_django
        from waitress import serve
        from config.wsgi import application
        
        print(f"▶ Iniciando DentalPro en {host}:{port}")
        print(f"▶ Abre http://localhost:{port} en tu navegador")
        print("✓ Presiona Ctrl+C para detener el servidor\n")
        
        # Iniciar servidor
        serve(
            application,
            host=host,
            port=port,
            threads=threads,
            _quiet=False,
        )
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"✗ Error al iniciar servidor: {e}")
        sys.exit(1)


def signal_handler(signum, frame):
    """
    Maneja señales de terminación (SIGINT, SIGTERM).
    """
    print("\n\n✓ Cerrando DentalPro...")
    print("✓ Servidor detenido")
    sys.exit(0)


def find_free_port(host='127.0.0.1', start_port=8000, max_attempts=3):
    """
    Busca un puerto libre a partir de start_port.
    """
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                print(f"⚠ Puerto {port} ocupado. Intentando con el siguiente...")
    return None


def main():
    """
    Función principal del launcher.
    """
    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("  DentalPro - Sistema de Gestión Dental")
    print("=" * 60 + "\n")
    
    # Configurar Django
    print("▶ Configurando Django...")
    try:
        setup_django()
        print("✓ Django configurado\n")
    except Exception as e:
        print(f"✗ Error configurando Django: {e}")
        sys.exit(1)
    
    # Verificar configuración de seguridad
    print("▶ Verificando configuración...")
    try:
        from django.conf import settings
        from django.core.management import call_command
        
        # Ejecutar checks de Django
        call_command('check', '--settings=config.settings.prod')
        print("✓ Configuración validada\n")
    except Exception as e:
        print(f"✗ Error en validación: {e}")
        print("⚠ Continúa de todas formas...\n")
    
    # Buscar puerto disponible
    host = '127.0.0.1'
    port = find_free_port(host, 8000, 3)
    if not port:
        print("✗ Error crítico: Los puertos 8000, 8001 y 8002 están ocupados.")
        print("⚠ Libera alguno de estos puertos e intenta de nuevo.")
        sys.exit(1)
        
    url = f"http://localhost:{port}"
    
    # Iniciar hilo para abrir navegador
    browser_thread = threading.Thread(
        target=open_browser,
        kwargs={'url': url, 'delay': 2},
        daemon=True
    )
    browser_thread.start()
    
    # Iniciar servidor Waitress (bloqueante)
    run_waitress_server(host=host, port=port)


if __name__ == '__main__':
    main()

