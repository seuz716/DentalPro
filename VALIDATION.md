"""
INSTRUCCIONES DE VALIDACIÓN - DentalPro
========================================

Este archivo contiene los comandos que debes ejecutar para validar
que todas las fases se completaron correctamente.

Ejecuta cada comando en orden y verifica que no hay errores.
"""

# ============================================================================
# FASE 0: Validar estructura y settings
# ============================================================================

# Verificar que Django se configura correctamente (desarrollo)
python manage.py check --settings=config.settings.dev
# Esperado: "System check identified no issues (0 silenced)."

# Verificar que Django se configura correctamente (producción)
python manage.py check --settings=config.settings.prod
# Esperado: "System check identified no issues (0 silenced)."

# Verificar base de datos existe
ls -lh db.sqlite3
# Esperado: -rw-r--r-- ... db.sqlite3 (archivo ~150KB)


# ============================================================================
# FASE 1-2: Validar modelo Patient y migraciones
# ============================================================================

# Mostrar migraciones aplicadas
python manage.py showmigrations --settings=config.settings.dev
# Esperado: [X] pacientes.0001_initial

# Verificar estructura de tabla Patient
python manage.py sqlmigrate pacientes 0001 --settings=config.settings.dev | head -50
# Esperado: CREATE TABLE pacientes_patient con campos: document_type, document_number, etc.

# Crear superusuario para acceder al admin
python manage.py createsuperuser --settings=config.settings.dev
# Sigue las instrucciones interactivas


# ============================================================================
# FASE 3: Validar vistas CBV
# ============================================================================

# Probar que las vistas existen y están configuradas
python -c "
from pacientes.views import PatientListView, PatientSearchView, PatientDetailView
print('✓ PatientListView:', PatientListView)
print('✓ PatientSearchView:', PatientSearchView)
print('✓ PatientDetailView:', PatientDetailView)
" --settings=config.settings.dev


# ============================================================================
# FASE 4-5: Validar templates
# ============================================================================

# Verificar que los templates existen
ls -la core/templates/core/*.html
ls -la pacientes/templates/pacientes/*.html
ls -la pacientes/templates/pacientes/partials/*.html
ls -la core/templates/core/components/*.html
# Esperado: Todos los archivos .html listados


# ============================================================================
# FASE 10: Validar launcher y configuración de producción
# ============================================================================

# Verificar que launcher.py es ejecutable
python -m py_compile desktop/launcher.py
# Esperado: Sin errores

# Verificar sintaxis y que se importa
python -c "
import sys
sys.path.insert(0, '.')
from desktop import launcher
print('✓ Launcher importado correctamente')
"

# Verificar que requirements/prod.txt tiene waitress
grep waitress requirements/prod.txt
# Esperado: waitress==2.1.2

# Verificar que prod.py tiene DEBUG=False
grep "DEBUG = False" config/settings/prod.py
# Esperado: DEBUG = False

# Verificar que dentalpro.spec existe
ls -la dentalpro.spec
# Esperado: -rw-r--r-- ... dentalpro.spec


# ============================================================================
# VALIDACIÓN FUNCIONAL: Iniciar aplicación en desarrollo
# ============================================================================

# Terminal 1: Iniciar servidor Django
python manage.py runserver --settings=config.settings.dev

# Terminal 2: En otra ventana, probar endpoints
curl http://127.0.0.1:8000/                    # Página de inicio
curl http://127.0.0.1:8000/pacientes/          # Lista de pacientes
curl http://127.0.0.1:8000/admin/              # Admin panel

# Navegador: Abre http://127.0.0.1:8000
# Esperado:
#   - Página de inicio funciona
#   - Link a "Gestión de Pacientes" visible
#   - Admin en http://127.0.0.1:8000/admin accesible


# ============================================================================
# VALIDACIÓN FUNCIONAL: Probar modelo Patient
# ============================================================================

# Shell de Django para pruebas
python manage.py shell --settings=config.settings.dev

# En el shell de Python, ejecuta:
from pacientes.models import Patient
from datetime import date

# Crear paciente de prueba
p = Patient.objects.create(
    document_type='CC',
    document_number='1234567890',
    first_name='Juan',
    last_name='Pérez',
    birth_date=date(1990, 1, 15),
    gender='M',
    phone='3001234567',
    email='juan@example.com',
    blood_type='O+',
)

# Verificar que se guardó
print(p)              # Esperado: "Juan Pérez (1234567890)"
print(p.full_name)    # Esperado: "Juan Pérez"
print(p.age)          # Esperado: 36 (aproximadamente)

# Verificar validación de cédula
p2 = Patient(
    document_type='CC',
    document_number='invalid',
    first_name='Test',
    last_name='User',
    birth_date=date(2000, 1, 1),
    gender='M',
)
try:
    p2.full_clean()
    print("✗ Validación falló: debería haber rechazado cédula inválida")
except Exception as e:
    print("✓ Validación correcta:", e)

# Salir del shell
exit()


# ============================================================================
# VALIDACIÓN FINAL: Probar launcher en producción
# ============================================================================

# IMPORTANTE: Esto inicia el servidor en puerto 8000
# Presiona Ctrl+C para detener

python desktop/launcher.py

# Esperado:
#   - Pantalla de inicio del launcher
#   - "Iniciando DentalPro en 127.0.0.1:8000"
#   - Navegador se abre automáticamente
#   - Aplicación es accesible en http://localhost:8000


# ============================================================================
# RESUMEN DE VALIDACIÓN
# ============================================================================

Pasos completados:
[_] Django check (dev y prod)
[_] Migraciones aplicadas
[_] Superusuario creado
[_] Vistas importadas correctamente
[_] Templates existen
[_] Launcher validado
[_] Servidor desarrollo funciona
[_] Modelo Patient funciona
[_] Validación de cédula funciona
[_] Launcher de escritorio funciona

Si todos los pasos pasaron ✓ el proyecto está listo para usar.

Para continuar con las siguientes fases, ve al README.md.
